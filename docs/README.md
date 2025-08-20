# DevOps CI/CD Pipeline Project

This project showcases a complete **CI/CD pipeline** for a Flask application:

- **Docker** – containerizes the application
  - **Docker Hub** – stores and distributes the built image
- **Jenkins** – runs the CI/CD pipeline:
  - Builds the Docker image
  - Runs tests
  - Pushes the image to Docker Hub
  - Deploys the application to Kubernetes
- **Kubernetes (MicroK8s)** – orchestrates deployment:
  - Performs rolling updates
  - Checks health with readiness and liveness probes
  - Scales pods with a Horizontal Pod Autoscaler (CPU + memory)
  - Enables rollback on failed deployment

## Prerequisites

- **Ubuntu 20.04+**
- **Git** (to clone the repository)

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/adrian-wisniewski-it/devops-cicd-pipeline.git
cd devops-cicd-pipeline
```

### 2. Install Docker

```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER  # Log out and back in to apply group changes
```

### 3. Install Kubernetes (MicroK8s)

```bash
sudo snap install microk8s --classic
sudo usermod -aG microk8s $USER  # Log out and back in to apply group changes
microk8s enable metrics-server
```

### 4. Install Java (required for Jenkins)

```bash
sudo apt update
sudo apt install -y openjdk-17-jdk
java -version
```

### 5. Install Jenkins

```bash
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | \
  sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null

echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | \
  sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null

sudo apt update
sudo apt install -y jenkins
sudo systemctl enable --now jenkins
sudo ufw allow 8080/tcp || true
sudo usermod -aG docker jenkins
sudo usermod -aG microk8s jenkins
echo "export KUBECONFIG=/var/snap/microk8s/current/credentials/client.config" | sudo tee -a /etc/default/jenkins
sudo systemctl restart jenkins

# Get initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

> Open Jenkins at [**http://localhost:8080/**](http://localhost:8080/) and complete the setup wizard (install suggested plugins).

### 6. Configure the Jenkins Pipeline

#### 6.1 Create Docker Hub credentials

In Jenkins go to **Manage Jenkins → Credentials → (global) → Add Credentials** and create:

- **Kind:** Username with password
- **ID:** `dockerhub` (must match Jenkinsfile)
- **Username:** your Docker Hub username 
- **Password:** a **Docker Hub Personal Access Token** (recommended)

To generate a token: **Docker Hub → Account Settings → Personal Access Tokens → Generate New Token**.

#### 6.2 Create a Pipeline job

- **Jenkins → New Item → Pipeline**
- **Name:** choose any (e.g., `devops-cicd-pipeline`)
- **Pipeline** → *Pipeline script from SCM*
- **SCM:** Git
  - **Repository URL:** your fork URL, e.g. `https://github.com/<your-username>/devops-cicd-pipeline.git`
  - **Branches to build:** `*/main`
  - **Script Path:** `Jenkinsfile`
- **Build Triggers:** enable **Poll SCM**: `H/5 * * * *`

> Note: In the **Jenkinsfile**, update the variables `IMAGE_REPO` (Docker Hub repo) and `GIT_REPO` (repository URL) to point to **your own values**.

#### 6.3 Verify the pipeline job

Trigger the job manually in Jenkins  and verify that all stages run successfully:

- `Checkout`
- `Build Image`
- `Test Image`
- `Push Image`
- `Deploy to Kubernetes`

If all steps succeed, Jenkins will build and push your Docker image, then update your Kubernetes deployment automatically.

### 7. Verify the Deployment

After the pipeline completes:

```bash
microk8s.kubectl get pods
microk8s.kubectl get svc
microk8s.kubectl get hpa
```

Test the application endpoints:

```bash
curl http://localhost:30080/
curl http://localhost:30080/healthz
curl http://localhost:30080/readyz
```

You should see:

- `DevOps CI/CD Pipeline` response at `/`
- `204 No Content` from `/healthz` and `/readyz`

Check autoscaling metrics:

```bash
microk8s.kubectl top pods
```

If CPU/memory load increases, HPA will scale the number of replicas automatically.

### 8. Cleanup

To remove all resources created by this project:

```bash
microk8s.kubectl delete -f k8s/deployment.yaml
microk8s.kubectl delete -f k8s/service.yaml
microk8s.kubectl delete -f k8s/hpa.yaml
```

Optionally, remove Jenkins and Docker images:

```bash
sudo apt remove --purge -y jenkins docker.io
sudo snap remove microk8s
```

