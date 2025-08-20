pipeline {
    agent any

    environment {
        IMAGE_REPO = 'adrianwisniewskiit/devops-cicd-pipeline'                                  // <- change to your Docker Hub repo
        GIT_REPO   = 'https://github.com/adrian-wisniewski-it/devops-cicd-pipeline.git'         // <- change to your GitHub repo URL
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: "${GIT_REPO}"
            }
        }

        stage('Build Image') {
            steps {
                sh 'docker build -t ${IMAGE_REPO}:$BUILD_NUMBER .'
                sh 'docker tag ${IMAGE_REPO}:$BUILD_NUMBER ${IMAGE_REPO}:latest'
            }
        }

        stage('Test Image') {
            steps {
                sh 'docker run --rm ${IMAGE_REPO}:$BUILD_NUMBER python -m unittest || true'
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
                sh 'docker push ${IMAGE_REPO}:$BUILD_NUMBER'
                sh 'docker push ${IMAGE_REPO}:latest'
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh """
                microk8s.kubectl set image deployment/devops-cicd-deployment devops-cicd=${IMAGE_REPO}:${BUILD_NUMBER}
                microk8s.kubectl apply -f k8s/service.yaml
                microk8s.kubectl apply -f k8s/hpa.yaml
                """
            }
        }
    }

    post {
        failure {
            sh 'microk8s.kubectl rollout undo deployment/devops-cicd-deployment || true'
        }
        always {
            sh 'docker system prune -af || true'
        }
    }
}