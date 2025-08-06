# 🏠 House Price Prediction with MLOps

This project implements a complete MLOps pipeline to train, package, and deploy a machine learning model that predicts house prices based on input features. It leverages FastAPI, Docker, GitHub Actions, and Scikit-Learn to deliver a production-ready solution.

---

## 📌 Features

- ✅ End-to-end ML pipeline from training to deployment  
- 🚀 FastAPI-based REST API to serve real-time predictions  
- 🐳 Dockerized application for platform-independent deployment  
- 🔁 CI/CD pipeline using GitHub Actions for automated testing and deployment  
- 📈 Trained and evaluated model using Scikit-Learn on cleaned house pricing data  

---

## 🛠️ Tech Stack

| Category        | Tools & Technologies                     |
|----------------|-------------------------------------------|
| Language        | Python                                    |
| ML Library      | Scikit-Learn                              |
| Web Framework   | FastAPI                                   |
| Containerization| Docker                                    |
| CI/CD           | GitHub Actions                            |
| Version Control | Git & GitHub                              |

---

## 📂 Project Structure

mlops-house-price-deployment/
│
├── app/
│ └── app.py # FastAPI application for predictions
│
├── model/
│ └── train_model.py # Model training script
│
├── data/
│ └── housing.csv # Dataset for training
│
├── Dockerfile # Docker configuration file
├── requirements.txt # Python dependencies
├── .github/
│ └── workflows/
│ └── main.yml # GitHub Actions CI/CD pipeline
└── README.md # Project documentation

YAML FILE

---

## 🚀 How to Run Locally

### 🔧 Prerequisites
- Python 3.8+
- Docker (for containerized deployment)

### ✅ Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/mlops-house-price-deployment.git
cd mlops-house-price-deployment



