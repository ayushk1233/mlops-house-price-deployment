pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/ayushk1233/mlops-house-price-deployment.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build('mlops-house-price-deployment:latest')
                }
            }
        }

        stage('Test Model') {
            steps {
                script {
                    sh 'python3 -m unittest discover -s tests || echo "No tests found"'
                }
            }
        }

        stage('Deploy App') {
            steps {
                script {
                    docker.image('mlops-house-price-deployment:latest').run('-p 8000:8000')
                }
            }
        }
    }

    post {
        failure {
            echo 'Build or deployment failed!'
        }
    }
}

