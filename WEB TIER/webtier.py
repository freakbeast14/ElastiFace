from flask import Flask, request, jsonify
import boto3
import json
import uuid
import base64
from werkzeug.utils import secure_filename
import time
import os

app = Flask(__name__)

sqs = boto3.client('sqs', region_name='us-east-1')

REQUEST_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/<AWS-ACCOUNT-ID>/<QUEUE_ID>-req-queue'
RESPONSE_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/<AWS-ACCOUNT-ID>/<QUEUE_ID>-resp-queue'

cache = []

@app.route("/", methods=['POST'])
def handle_image_upload():
    if 'inputFile' not in request.files:
        return jsonify({'error': 'No inputFile part'}), 400
    file = request.files['inputFile']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    file_extension = os.path.splitext(filename)[1]
    if file_extension.lower() != '.jpg':
        return jsonify({'error': 'File format not supported. Only .jpg files are allowed'}), 400

    file_content = file.read()
    base64_encoded_content = base64.b64encode(file_content).decode('utf-8')
    unique_id = str(uuid.uuid4())

    message_body = json.dumps({
        'id': unique_id,
        'filename': filename,
        'image': base64_encoded_content
    })

    sqs.send_message(QueueUrl=REQUEST_QUEUE_URL, MessageBody=message_body)

    while True:
        # First, check if the message is already in the cache
        for cached_message in cache[:]:
            body = json.loads(cached_message['Body'])
            if body['id'] == unique_id:
                cache.remove(cached_message)  # Remove the processed message from the cache
                classification_result = body['classification_result']
                name_of_file = filename.split('.')[0]
                return f'{name_of_file}:{classification_result}', 200

        # If not found in the cache, check the SQS queue
        response = sqs.receive_message(QueueUrl=RESPONSE_QUEUE_URL, MaxNumberOfMessages=10, WaitTimeSeconds=20)
        if 'Messages' in response:
            for message in response['Messages']:
                body = json.loads(message['Body'])
                if body['id'] == unique_id:
                    classification_result = body['classification_result']
                    sqs.delete_message(QueueUrl=RESPONSE_QUEUE_URL, ReceiptHandle=message['ReceiptHandle'])
                    name_of_file = filename.split('.')[0]
                    return f'{name_of_file}:{classification_result}', 200
                else:
                    # If the message does not match the unique_id, add it to the cache
                    cache.append(message)

    # If the result is not found within the timeout, you might want to send an appropriate response
    # Note: The infinite loop (while True:) might need a break condition based on a timeout
    # return 'error: Processing timeout or no result found', 504

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
