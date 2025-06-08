from flask import Flask, send_file, request, jsonify, redirect, Response
from google.cloud import storage
import os
import requests

app = Flask(__name__)

# 🔁 Backend API behind internal load balancer
BACKEND_URL = "http://192.168.20.12:8080"

@app.route('/')
def index():
    return send_file('index.html')

# Submit proxy
@app.route('/submit', methods=['POST'])
def proxy_submit():
    form_data = request.form.to_dict(flat=True)
    form_data['addons'] = request.form.getlist("addons")

    try:
        response = requests.post(f"{BACKEND_URL}/submit", json=form_data)
        response.raise_for_status()
        return redirect('/')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/image/<filename>')
def serve_private_image(filename):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket("capstone-food-order")
        blob = bucket.blob(filename)

        stream = blob.open("rb")
        content_type = blob.content_type or "application/octet-stream"
        return Response(stream, content_type=content_type)
    except Exception as e:
        return jsonify({"error": f"Could not serve image: {str(e)}"}), 500


# Catch all other routes to serve SPA
@app.route('/<path:path>')
def catch_all(path):
    return send_file('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
