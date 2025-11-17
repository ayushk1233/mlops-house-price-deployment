provider "aws" {
  region = "ap-south-1"
}

# 1. Define the Security Group (Firewall)
# This controls what traffic is allowed IN to your servers
resource "aws_security_group" "app-sg" {
  name        = "app-server-sg"
  description = "Allow SSH, HTTP, App, and Ping"

  # Allow SSH (Port 22) from ANY IP address
  # This is so you and Ansible can connect
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow HTTP (Port 80) from ANY IP address
  # This is for the Nagios web dashboard
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow App Port (Port 8000) from ANY IP address
  # This is for your FastAPI application
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow ICMP (Ping) from ANY IP address
  # This is for Nagios to check if the server is alive
  ingress {
    from_port   = -1 # -1 means all ICMP types
    to_port     = -1
    protocol    = "icmp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic (so your servers can download updates)
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
# This is where your FastAPI app will run
resource "aws_instance" "app_server" {
  # This is the Amazon Machine Image (AMI) for Ubuntu 22.04
  # in the ap-south-1 (Mumbai) region.
  ami           = "ami-0f5ee92e2d63afc18" 
  instance_type = "t3.micro"             # Free-tier eligible
  key_name      = "my-app-key"           # The key we just created

  # Attach the firewall rules we defined above
  vpc_security_group_ids = [aws_security_group.app-sg.id]

  tags = {
    Name = "FastAPI-App-Server"
  }
}

# 3. Create the Nagios Monitoring Server
# This is where Nagios will run
resource "aws_instance" "nagios_server" {
  ami           = "ami-0f5ee92e2d63afc18" # Same Ubuntu 22.04 AMI
  instance_type = "t3.micro"             # Free-tier eligible
  key_name      = "my-app-key"           # Same key

  # Attach the same firewall rules
  vpc_security_group_ids = [aws_security_group.app-sg.id]

  tags = {
    Name = "Nagios-Server"
  }
}

# 4. Output the IP addresses
# This tells Terraform to print the public IPs after it's done
output "app_server_public_ip" {
  description = "Public IP address of the FastAPI App Server"
  value       = aws_instance.app_server.public_ip
}

output "nagios_server_public_ip" {
  description = "Public IP address of the Nagios Monitoring Server"
  value       = aws_instance.nagios_server.public_ip
}