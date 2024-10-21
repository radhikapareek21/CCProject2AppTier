import boto3
import os
import json
import torch
from model.face_recognition import face_match  # Assuming this function handles your model inference

# AWS region and ASU ID
REGION = 'us-east-1'
ASU_ID = '1231545642'  # Replace with your actual ASU ID

# SQS Queue URLs based on the ASU ID
REQUEST_QUEUE_URL = f'https://sqs.{REGION}.amazonaws.com/147997137167/{ASU_ID}-req-queue'
RESPONSE_QUEUE_URL = f'https://sqs.{REGION}.amazonaws.com/147997137167/{ASU_ID}-resp-queue'

# AWS S3 bucket names based on ASU ID
INPUT_BUCKET = f'{ASU_ID}-in-bucket'
OUTPUT_BUCKET = f'{ASU_ID}-out-bucket'

# Initialize AWS clients
sqs = boto3.client('sqs', region_name=REGION)
s3 = boto3.client('s3', region_name=REGION)

# Function to download an image from S3
def download_image_from_s3(bucket_name, key, download_path):
    try:
        s3.download_file(Bucket=bucket_name, Key=key, Filename=download_path)
        print(f"Downloaded {key} from {bucket_name} to {download_path}")
    except Exception as e:
        print(f"Error downloading file {key} from S3: {e}")

# Function to upload the result to S3

def upload_result_to_s3(bucket_name, key, result):
    try:
        # Strip the file extension from the key to get only the base filename
        base_key = os.path.splitext(key)[0]
        
        # Store the result in the output bucket using the base filename as the key
        s3.put_object(Bucket=bucket_name, Key=base_key, Body=result)
        print(f"Uploaded result for {base_key} to {bucket_name}")
    except Exception as e:
        print(f"Error uploading result {base_key} to S3: {e}")


    

# Function to process image using the face recognition model
def process_image(filename):
    local_image_path = f'/tmp/{filename}'
    download_image_from_s3(INPUT_BUCKET, filename, local_image_path)

    # Run inference using the face recognition model
    try:
        # Inject the local_image_path into sys.argv[1] as a workaround
        model_path = './model/data.pt'  # Adjust the path based on where 'data.pt' is located
        result_name, match_score = face_match(local_image_path, model_path)
        print(result_name)
        return f"{result_name}:{match_score}"
    except Exception as e:
        print(f"Error during face recognition inference: {e}")
        return "Error during inference"


# Main loop to poll the SQS request queue for messages
def process_queue_messages():
    while True:
        # Receive message from the SQS request queue
        try:
            response = sqs.receive_message(
                QueueUrl=REQUEST_QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20  # Long polling for better efficiency
            )
        except Exception as e:
            print(f"Error receiving messages from SQS: {e}")
            continue

        if 'Messages' in response:
            for message in response['Messages']:
                try:
                    body = json.loads(message['Body'])
                    filename = body.get('filename', '')

                    if filename:
                        print(f"Processing image: {filename}")
                        
                        # Process the image using the model
                        result = process_image(filename)

                        # Upload the result to the S3 output bucket
                        upload_result_to_s3(OUTPUT_BUCKET, filename, result)

                        # Send the result back to the response queue
                        result_message = {
                            'filename': filename,
                            'result': result
                        }
                        sqs.send_message(
                            QueueUrl=RESPONSE_QUEUE_URL,
                            MessageBody=json.dumps(result_message)
                        )

                        # Delete the processed message from the queue
                        sqs.delete_message(
                            QueueUrl=REQUEST_QUEUE_URL,
                            ReceiptHandle=message['ReceiptHandle']
                        )
##
                        print(f"Processed and sent result for {filename}")
                    else:
                        print("No valid filename found in the message.")
                except Exception as e:
                    print(f"Error processing message: {e}")
        else:
            print("No messages to process")

if __name__ == "__main__":
    print("Starting the App Tier worker to process images.")
    process_queue_messages()