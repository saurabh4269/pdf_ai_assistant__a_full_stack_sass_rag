import boto3
import json
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv(dotenv_path='../.env')

def test_s3_permissions():
    try:
        # Fetch credentials from environment variables
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_DEFAULT_REGION')
        
        # Initialize the S3 client using credentials from .env
        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        # Test ListBucket
        print("Testing ListBucket...")
        s3.list_objects_v2(Bucket='pdf-chatbot-saurabh')
        
        # Test PutObject
        print("Testing PutObject...")
        s3.put_object(
            Bucket='pdf-chatbot-saurabh',
            Key='test.txt',
            Body='test content'
        )
        
        # Test GetObject
        print("Testing GetObject...")
        s3.get_object(
            Bucket='pdf-chatbot-saurabh',
            Key='test.txt'
        )
        
        # Test DeleteObject
        print("Testing DeleteObject...")
        s3.delete_object(
            Bucket='pdf-chatbot-saurabh',
            Key='test.txt'
        )
        
        print("All permissions working correctly!")
        
    except Exception as e:
        print(f"Error testing permissions: {str(e)}")

# Run the test function
test_s3_permissions()
