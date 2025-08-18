pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/adrian-wisniewski-it/hello-devops-ci-cd.git'
            }
        }

        stage('Build Image') {
            steps {
                sh 'docker build -t adrianwisniewskiit/hello-devops:$BUILD_NUMBER .'
                sh 'docker tag adrianwisniewskiit/hello-devops:$BUILD_NUMBER adrianwisniewskiit/hello-devops:latest'
            }
        }

        stage('Test Image') {
            steps {
                sh 'docker run --rm adrianwisniewskiit/hello-devops:$BUILD_NUMBER python -m unittest || true'
            }
        }

        stage('Login to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    sh 'echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin'
                }
            }
        }

        stage('Push Image') {
            steps {
                sh 'docker push adrianwisniewskiit/hello-devops:$BUILD_NUMBER'
                sh 'docker push adrianwisniewskiit/hello-devops:latest'
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh """
                microk8s.kubectl set image deployment/hello-devops-deployment hello-devops=adrianwisniewskiit/hello-devops:${BUILD_NUMBER}
                microk8s.kubectl apply -f k8s/service.yaml
                """
            }
        }
    }

    post {
        always {
            sh 'docker system prune -af || true'
        }
    }
}