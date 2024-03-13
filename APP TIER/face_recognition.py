import os
import csv
import sys
import torch
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
from torchvision import datasets
from torch.utils.data import DataLoader
import boto3
import json
import base64
from io import BytesIO

mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) # initializing mtcnn for face detection
resnet = InceptionResnetV1(pretrained='vggface2').eval() # initializing resnet for face img to embeding conversion

s3 = boto3.client('s3')
sqs = boto3.client('sqs', region_name='us-east-1')

REQUEST_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/992382601963/1225369223-req-queue'
RESPONSE_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/992382601963/1225369223-resp-queue'
INPUT_BUCKET = '1225369223-in-bucket'
OUTPUT_BUCKET = '1225369223-out-bucket'

def process_messages_from_queue():
    while True:
        response = sqs.receive_message(
            QueueUrl=REQUEST_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20
        )

        messages = response.get('Messages', [])
        for message in messages:
            body = json.loads(message['Body'])
            image_data = base64.b64decode(body['image'])
            print(image_data)
            image_id = body['id']
            filename = body['filename']

            image = Image.open(BytesIO(image_data))
            img_temp = BytesIO()
            image.save(img_temp, format=image.format)
            img_temp.seek(0)

            image_key = filename
            s3.upload_fileobj(Fileobj=img_temp, Bucket=INPUT_BUCKET, Key=image_key)
            print(f"Image {filename} saved to {INPUT_BUCKET}/{image_key}")

            classification_result = face_match(image, 'data.pt')[0] 
            print(classification_result)

            result_key = filename.split('.')[0]
            s3.put_object(Bucket=OUTPUT_BUCKET, Key=result_key, Body=classification_result)
            print(f"Result for {filename} saved to {OUTPUT_BUCKET}/{result_key}")

            response_message = {
                'id': image_id,
                'filename': filename,
                'classification_result': classification_result
            }
            sqs.send_message(QueueUrl=RESPONSE_QUEUE_URL, MessageBody=json.dumps(response_message))

            sqs.delete_message(QueueUrl=REQUEST_QUEUE_URL, ReceiptHandle=message['ReceiptHandle'])

            print(f"Processed and responded for {filename}")

def face_match(img, data_path):
    # img = Image.open(img_path)
    face, prob = mtcnn(img, return_prob=True)
    emb = resnet(face.unsqueeze(0)).detach()

    saved_data = torch.load('data.pt')
    embedding_list = saved_data[0]
    name_list = saved_data[1]
    dist_list = []

    for idx, emb_db in enumerate(embedding_list):
        dist = torch.dist(emb, emb_db).item()
        dist_list.append(dist)

    idx_min = dist_list.index(min(dist_list))
    return (name_list[idx_min], min(dist_list))

if __name__ == "__main__":
    process_messages_from_queue()






