from flask import Flask, request
import subprocess, hmac, hashlib

app = Flask(__name__)
SECRET = b'HRAEciCdSecret@2025'  # même que celui sur GitHub

@app.route("/hooks/deploy", methods=["POST"])
def deploy():
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        return "Forbidden", 403

    sha_name, signature = signature.split('=')
    mac = hmac.new(SECRET, msg=request.data, digestmod=hashlib.sha256)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        return "Invalid signature", 403

    subprocess.Popen(["/var/www/hrae-webSite/deploy.sh"])
    return "Deploy triggered", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
