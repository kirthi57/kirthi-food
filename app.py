from flask import Flask, send_file, request, jsonify, redirect
import requests
from google.cloud import storage
from flask import Response

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


# Catch all other routes to serve SPA
@app.route('/<path:path>')
def catch_all(path):
    return send_file('index.html')
    
@app.route('/image/<filename>')
def serve_private_image(filename):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket("capstone-food-order")
        blob = bucket.blob(filename)

        # Stream file contents securely
        stream = blob.open("rb")
        return Response(stream, content_type="image/jpeg")  # change MIME type if needed
    except Exception as e:
        return jsonify({"error": f"Could not serve image: {str(e)}"}), 500    
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
