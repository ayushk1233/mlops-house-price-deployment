pipeline {
    agent any

    environment {
        IMAGE_NAME = 'house-price-app'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git 'https://github.com/<your-username>/mlops-house-price-deployment.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t $IMAGE_NAME .'
                }
            }
        }

        stage('Run Container') {
            steps {
                script {
                    sh 'docker stop house-price-app || true'
                    sh 'docker rm house-price-app || true'
                    sh 'docker run -d -p 8000:8000 --name house-price-app $IMAGE_NAME'
                }
            }
        }
    }

    post {
        failure {
            echo 'Build failed!'
        }
        success {
            echo 'Build and deploy successful!'
        }
    }
}

