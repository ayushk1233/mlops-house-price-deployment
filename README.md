# 🏠 End-to-End MLOps: House Price Prediction

**FastAPI | Terraform | Ansible | Docker | Nagios**

This project demonstrates a complete, automated DevOps and MLOps pipeline.

- **The Application:** A simple machine learning model is trained with scikit-learn to predict house prices. This model is served via a Python FastAPI application.
- **The Pipeline:** We treat this app as a professional production service. The entire infrastructure (servers, firewalls), configuration (installing Docker, Nagios), and application deployment is automated using Terraform and Ansible.
- **The Result:** A live, running application on an AWS EC2 server, which is being actively monitored by a second, automatically-configured Nagios server.

---

## 📋 Project Architecture

This project is built on a **3-node architecture:**

1. **Control Node (Your Laptop):** Your local machine. This is where you write code and run all terraform and ansible-playbook commands.
2. **App Server (AWS EC2):** An Ubuntu server that runs the FastAPI application inside a Docker container.
3. **Nagios Server (AWS EC2):** A second Ubuntu server that runs Nagios Core. Its job is to continuously monitor the App Server's health.

---

## 🛠️ Technologies Used

| Category       | Technologies                                                  |
| -------------- | ------------------------------------------------------------- |
| Application    | Python, FastAPI, Scikit-learn, Pandas, Docker, Docker Compose |
| Infrastructure | Terraform, AWS (EC2, VPC Security Groups)                     |
| Configuration  | Ansible                                                       |
| Monitoring     | Nagios Core                                                   |

---

## 📂 Project Structure

```
mlops-house-price-deployment/
├── .github/
│   └── workflows/
│       └── docker-build.yml          # CI/CD pipeline
├── app/
│   └── app.py                        # FastAPI application
├── data/
│   └── house_data.csv                # Training dataset
├── model/
│   ├── train_model.py                # Initial model training script
│   ├── retrain_model.py              # Model retraining script
│   └── house_price_model.pkl         # Trained model (artifact)
├── terraform/
│   └── main.tf                       # Infrastructure as Code (to be created)
├── ansible/
│   ├── inventory.ini                 # Server inventory (to be created)
│   ├── deploy_app.yml                # App deployment playbook (to be created)
│   ├── install_nagios.yml            # Nagios installation playbook (to be created)
│   └── test-connection.yml           # Connection test playbook (to be created)
├── Dockerfile                        # Docker container configuration
├── requirements.txt                  # Python dependencies
├── ansible.cfg                       # Ansible configuration (to be created)
└── README.md                         # Project documentation
```

---

# Part 1: The Local Application

Before automating, you can run the application locally.

## 1.1. Setup Local Environment

```bash
# 1. Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
```

## 1.2. Train the Model

This script creates the `model/house_price_model.pkl` file.

```bash
python model/train_model.py
```

## 1.3. Run the App Locally

This command starts the FastAPI server on `http://127.0.0.1:8000`.

```bash
uvicorn app.app:app --reload
```

You can now access these URLs:

- **API Docs:** `http://127.0.0.1:8000/docs`
- **Health Check:** `http://127.0.0.1:8000/health`

---

# Part 2: Full DevOps Deployment

This is the main workflow to build, deploy, and monitor the application in the cloud.

## Phase 1: Provision Infrastructure (Terraform)

We will use Terraform to build our two servers and their shared firewall.

### Prerequisites

- An AWS Account
- AWS CLI installed (`brew install awscli`)
- An IAM User with `AmazonEC2FullAccess` permissions
- Your local AWS CLI configured with this user's credentials (`aws configure`)

### Step 1.1: Create AWS Key Pair

We will create a key pair in the AWS Console to avoid CLI permission errors.

1. Navigate to the EC2 Dashboard in your AWS Console
2. Go to **Key Pairs** and click **"Create key pair"**
3. Name it exactly: `my-app-key`
4. Choose file format: `.pem`
5. Click **"Create"** - Your browser will download `my-app-key.pem`
6. Move this `my-app-key.pem` file into the `terraform/` directory

### Step 1.2: Define Infrastructure (main.tf)

This file (`terraform/main.tf`) is our blueprint. It defines our firewall and two t3.micro Ubuntu servers.

```hcl
provider "aws" {
  region = "ap-south-1"
}

# 1. Define the Security Group (Firewall)
resource "aws_security_group" "app-sg" {
  name        = "app-server-sg"
  description = "Allow SSH, HTTP, App, and Ping"

  # Allow SSH (Port 22 for Ansible)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow HTTP (Port 80 for Nagios UI)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow App Port (Port 8000 for FastAPI)
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow ICMP (Ping for Nagios)
  ingress {
    from_port   = -1
    to_port     = -1
    protocol    = "icmp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "app-sg"
  }
}

# 2. Create the Application Server
resource "aws_instance" "app_server" {
  ami           = "ami-0f5ee92e2d63afc18" # Ubuntu 22.04 LTS (ap-south-1)
  instance_type = "t3.micro"             # Note: Not Free Tier
  key_name      = "my-app-key"
  vpc_security_group_ids = [aws_security_group.app-sg.id]

  tags = {
    Name = "FastAPI-App-Server"
  }
}

# 3. Create the Nagios Monitoring Server
resource "aws_instance" "nagios_server" {
  ami           = "ami-0f5ee92e2d63afc18"
  instance_type = "t3.micro"
  key_name      = "my-app-key"
  vpc_security_group_ids = [aws_security_group.app-sg.id]

  tags = {
    Name = "Nagios-Server"
  }
}

# 4. Output the IPs
output "app_server_public_ip" {
  value = aws_instance.app_server.public_ip
}

output "nagios_server_public_ip" {
  value = aws_instance.nagios_server.public_ip
}
```

### Step 1.3: Build the Servers

Run these commands from your local terminal, inside the `terraform/` directory.

```bash
# 1. Initialize Terraform (downloads AWS provider)
terraform init

# 2. See what will be built
terraform plan

# 3. Build the servers!
terraform apply
```

Terraform will ask you to confirm by typing `yes`. After 1-2 minutes, it will output the Public IPs for your two servers.

**Outcome:** Two running EC2 instances with public IPs.

---

## Phase 2: Configure Servers (Ansible)

Now that our servers are running, we'll use Ansible to install software on them.

### Prerequisites

- Install Ansible on your local machine (Mac): `brew install ansible`

### Step 2.1: Create Ansible Config (ansible.cfg)

Create `ansible.cfg` in the project root. This file tells Ansible to skip the Host key verification error for our new servers.

```ini
[defaults]
host_key_checking = False
```

### Step 2.2: Create Ansible Inventory (ansible/inventory.ini)

This is our "phone book." It tells Ansible the IP addresses of our servers and how to connect.

**File:** `ansible/inventory.ini`

```ini
[app_server]
<!-- PASTE YOUR APP SERVER IP HERE -->
3.110.217.217

[nagios_server]
<!-- PASTE YOUR NAGIOS SERVER IP HERE -->
3.110.183.24

[all:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=terraform/my-app-key.pem
ansible_python_interpreter=/usr/bin/python3
```

### Step 2.3: Test Connection

Run this from your project root to confirm Ansible can talk to your servers.

```bash
ansible-playbook -i ansible/inventory.ini ansible/test-connection.yml
```

You should see a green "ok" from both servers.

### Step 2.4: Deploy the App (deploy_app.yml)

This playbook installs Docker, clones the Git repo, installs Python libraries, trains the model, and runs the app.

**File:** `ansible/deploy_app.yml`

```yaml
---
- name: Deploy FastAPI App to App Server
  hosts: app_server
  become: yes
  tasks:
    - name: Update the package list
      apt:
        update_cache: yes

    - name: Install dependencies (git, python3-pip, docker, docker-compose)
      apt:
        name:
          - git
          - python3-pip
          - docker.io
          - docker-compose
        state: present

    - name: Start and enable Docker service
      service:
        name: docker
        state: started
        enabled: yes

    - name: Add 'ubuntu' user to the 'docker' group
      user:
        name: ubuntu
        groups: docker
        append: yes

    - name: Clone the application repository
      git:
        # !!! CHANGE THIS to your GitHub repo URL !!!
        repo: https://github.com/your-username/mlops-house-price-deployment.git
        dest: /home/ubuntu/app
        force: yes

    - name: Install Python libraries on host
      # This is the fix for the "ModuleNotFoundError: pandas" error
      pip:
        requirements: /home/ubuntu/app/requirements.txt
        executable: pip3

    - name: Train the model
      shell: |
        python3 /home/ubuntu/app/model/train_model.py
      args:
        chdir: /home/ubuntu/app

    - name: Build and run the app with docker-compose
      shell: |
        cd /home/ubuntu/app
        docker-compose up -d --build
      args:
        chdir: /home/ubuntu/app
```

### Step 2.5: Install Nagios (install_nagios.yml)

This playbook automates the entire Nagios + Apache installation. It includes our fixes for the passlib and make install-webconf errors.

**File:** `ansible/install_nagios.yml`

```yaml
---
- name: Install Nagios Core on Nagios Server
  hosts: nagios_server
  become: yes
  vars:
    nagios_version: "4.4.12"
    plugins_version: "2.3.3"

  tasks:
    - name: Update the package list
      apt:
        update_cache: yes

    - name: Install Nagios dependencies
      apt:
        name:
          - apache2
          - php
          - libapache2-mod-php
          - build-essential
          - libgd-dev
          - unzip
          - wget
          - autoconf
          - gcc
          - libc6
          - make
          - libssl-dev
          - bc
          - gawk
          - dc
          - snmp
          - libnet-snmp-perl
          - gettext
          - libpq5
          - python3-pip # Fix for passlib
        state: present

    - name: Create Nagios user and group
      user: { name: nagios, state: present }

    - name: Create Nagios command group
      group: { name: nagcmd, state: present }

    - name: Add users to the command group
      user:
        name: "{{ item }}"
        groups: nagcmd
        append: yes
      loop: ["nagios", "www-data"]

    - name: Download and Unarchive Nagios
      unarchive:
        src: "https://assets.nagios.com/downloads/nagioscore/releases/nagios-{{ nagios_version }}.tar.gz"
        dest: /tmp
        remote_src: yes

    - name: Download and Unarchive Nagios Plugins
      unarchive:
        src: "https://nagios-plugins.org/download/nagios-plugins-{{ plugins_version }}.tar.gz"
        dest: /tmp
        remote_src: yes

    - name: Configure Nagios Core
      command: ./configure --with-nagios-user=nagios --with-nagios-group=nagios --with-command-group=nagcmd
      args:
        chdir: "/tmp/nagios-{{ nagios_version }}"
        creates: /usr/local/nagios/bin/nagios

    - name: Run 'make all' for Nagios Core
      make: { chdir: "/tmp/nagios-{{ nagios_version }}", target: all }

    # Start: Fix for 'File exists' error
    - name: Run 'make install' (core, cmd, init, config)
      make:
        chdir: "/tmp/nagios-{{ nagios_version }}"
        target: "{{ item }}"
      loop:
        - install
        - install-commandmode
        - install-init
        - install-config

    - name: Remove existing Apache symlink
      file:
        path: /etc/apache2/sites-enabled/nagios.conf
        state: absent

    - name: Run 'make install-webconf'
      make:
        chdir: "/tmp/nagios-{{ nagios_version }}"
        target: install-webconf
    # End: Fix for 'File exists' error

    - name: Install passlib (dependency for htpasswd module)
      pip: { name: passlib, executable: pip3 }

    - name: Set Nagios web interface password (nagiosadmin:nagiosadmin)
      community.general.htpasswd:
        path: /usr/local/nagios/etc/htpasswd.users
        name: nagiosadmin
        password: nagiosadmin
        create: yes
        owner: nagios
        group: nagcmd

    - name: Configure Nagios Plugins
      command: ./configure --with-nagios-user=nagios --with-nagios-group=nagios
      args:
        chdir: "/tmp/nagios-plugins-{{ plugins_version }}"
        creates: /usr/local/nagios/libexec/check_ping

    - name: Run 'make' and 'make install' for Plugins
      make:
        chdir: "/tmp/nagios-plugins-{{ plugins_version }}"
        target: "{{ item }}"
      loop: ["all", "install"]

    - name: Enable Apache modules
      command: a2enmod cgi

    - name: Start and enable services
      service:
        name: "{{ item }}"
        state: started
        enabled: yes
      loop: ["apache2", "nagios"]
```

### Step 2.6: Run the Playbooks

Run these commands from your project root.

```bash
# 1. Deploy the app
ansible-playbook -i ansible/inventory.ini ansible/deploy_app.yml

# 2. Install Nagios
ansible-playbook -i ansible/inventory.ini ansible/install_nagios.yml
```

### Step 2.7: Verification

- **Check the App:** Go to `http://<YOUR_APP_SERVER_IP>:8000/health`. You should see `{"status": "ok"}`.
- **Check Nagios:** Go to `http://<YOUR_NAGIOS_SERVER_IP>/nagios`. Log in with `nagiosadmin / nagiosadmin`. The dashboard should be running.

---

## Phase 3: Configure Nagios Monitoring

The final step is to log into our Nagios server and tell it to monitor our app server.

### Step 3.1: SSH into the Nagios Server

From your local terminal:

```bash
# ssh -i [your key file] [user]@[server_ip]
ssh -i terraform/my-app-key.pem ubuntu@<YOUR_NAGIOS_SERVER_IP>
```

### Step 3.2: Define New Check Command

We need to teach Nagios how to check our app's `/health` endpoint.

```bash
# Open the commands file
sudo nano /usr/local/nagios/etc/objects/commands.cfg
```

Scroll to the bottom and add this:

```
define command {
    command_name    check_http_fastapi
    command_line    $USER1$/check_http -H $HOSTADDRESS$ -p 8000 -u /health -s "ok"
}
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

### Step 3.3: Create App Server Config File

This file defines our app server and its services.

```bash
# Create the new config file
sudo nano /usr/local/nagios/etc/objects/app-server.cfg
```

Paste in the following, making sure to add your App Server's IP:

```
# 1. Define the Host (Your App Server)
define host {
    use                     linux-server
    host_name               fastapi-app-server
    alias                   FastAPI App Server
    address                 <YOUR_APP_SERVER_IP>
}

# 2. Define the PING Service
define service {
    use                             generic-service
    host_name                       fastapi-app-server
    service_description             PING
    check_command                   check_ping!100.0,20%!500.0,60%
}

# 3. Define the App Health Service
define service {
    use                             generic-service
    host_name                       fastapi-app-server
    service_description             FastAPI_App_Health
    check_command                   check_http_fastapi
}
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

### Step 3.4: Tell Nagios to Load the New File

```bash
# Open the main config file
sudo nano /usr/local/nagios/etc/nagios.cfg
```

Find the line `cfg_file=/usr/local/nagios/etc/objects/localhost.cfg` (around line 52) and add this new line right below it:

```
cfg_file=/usr/local/nagios/etc/objects/app-server.cfg
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

### Step 3.5: Verify and Restart

This is the final command to apply all our changes.

```bash
# 1. Verify the configuration for any errors
sudo /usr/local/nagios/bin/nagios -v /usr/local/nagios/etc/nagios.cfg
# (This should end with "Total Errors: 0")

# 2. Restart the Nagios service
sudo systemctl restart nagios.service
```

---

## Final Result

Go back to your Nagios web dashboard (`http://<YOUR_NAGIOS_SERVER_IP>/nagios`) and click on the **"Services"** tab. After a few moments, you will see your `fastapi-app-server` with both **PING** and **FastAPI_App_Health** showing a green **"OK"** status.

---

## How to Clean Up

When you are finished with the project, you can destroy all the cloud infrastructure with a single command. This will delete everything.

```bash
# 1. Go to your terraform directory
cd terraform

# 2. Run the destroy command
terraform destroy
```

Confirm with `yes`, and Terraform will delete both EC2 instances and the security group.
