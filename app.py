from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from google.cloud import storage
import os
import logging
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()


# Initialize Flask app
app = Flask(__name__)
PROJECT_ID = os.getenv("PROJECT_ID")
BUCKET_NAME = "teladoc_storage"
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Initialize the Google Cloud Storage client inside the route
        storage_client = storage.Client(project=PROJECT_ID)

        # Get the file from the request
        file = request.files['file']
        filename = file.filename

        # Upload file to GCS
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_file(file)

        return jsonify({"message": f"File {filename} uploaded successfully to {BUCKET_NAME}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        # Download file from GCS
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        file_content = blob.download_as_text()

        return jsonify({"content": file_content}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Configure logging
logging.basicConfig(level=logging.INFO)  # Log INFO and above levels
logger = logging.getLogger(__name__)

# Initialize OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to handle user requests
@app.route('/chat', methods=['POST'])

def chat():
    try:
        # Get the input from the request
        user_input = request.json.get("input", "")
        if not user_input:
            return jsonify({"error": "No input provided"}), 400

        # Query the OpenAI API using the client
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": 
                 "You are an appointment assistant. "
                 "- Always confirm the time zone for rescheduling requests. "
                 "- If the user specifies a date in DD/MM or MM/DD format, ask for clarification. "
                 "- Handle queries in English and Spanish. "
                 "Examples: "
                 "- 'Cancel my appointment on September 10th' → 'Please specify the time if you have multiple appointments that day.' "
                 "- 'Cancelar mi cita del 10 de septiembre' → 'Tu cita del 10 de septiembre a las 10:00 AM ha sido cancelada.'"},
                {"role": "user", "content": user_input}
            ],
            model="gpt-3.5-turbo"
        )

        # Extract and return the assistant's response
        assistant_response = response.choices[0].message.content

        # Save user input and assistant response to GCS
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)

        # Create a unique filename based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"conversation_{timestamp}.json"

        # Prepare the conversation data
        conversation_data = {
            "timestamp": timestamp,
            "user_input": user_input,
            "assistant_response": assistant_response
        }

        # Upload conversation data as JSON to GCS
        blob = bucket.blob(filename)
        blob.upload_from_string(json.dumps(conversation_data), content_type="application/json")

        return jsonify({"response": assistant_response, "saved_to": filename}), 200

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")  # Log the error
        return jsonify({"error": str(e)}), 500


# Run the Flask app
if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))  # Use PORT environment variable
    app.run(host='0.0.0.0', port=port)
