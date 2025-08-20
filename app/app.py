from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "DevOps CI/CD Pipeline"

@app.get("/healthz")
def healthz():
    return "", 204

@app.get("/readyz")
def readyz():
    return "", 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)