import os
import sys
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
import boto3
from pymongo import MongoClient
from app.config import config
from dotenv import load_dotenv

# Load test environment variables
load_dotenv("../.env.test")

# Initialize real S3 client
s3 = boto3.client('s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

# Initialize MongoDB client
mongo_client = MongoClient(os.getenv('MONGODB_URL'))
db = mongo_client[config.mongodb_name]

# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Test constants
TEST_CHAT_ID = "test_chat_123"
TEST_FILE_KEY = "test/test.pdf"

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup test data after each test"""
    yield
    # Clean up MongoDB collections
    db.files.delete_many({"file_key": TEST_FILE_KEY})
    db.chunks.delete_many({"chat_id": TEST_CHAT_ID})
    # Clean up S3
    try:
        s3.delete_object(Bucket=config.s3_bucket, Key=TEST_FILE_KEY)
    except:
        pass

def test_ingest_file(test_pdf):
    """Test file ingestion endpoint with real S3 and MongoDB"""
    print("\nTesting file ingestion...")
    with open(test_pdf, "rb") as f:
        files = {
            "file": ("test.pdf", f, "application/pdf")
        }
        data = {
            "file_key": TEST_FILE_KEY,
            "chat_id": TEST_CHAT_ID
        }
        print(f"Uploading file with chat_id: {TEST_CHAT_ID}")
        response = client.post("/v1/ingest_file", files=files, data=data)
        
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json() == {"messages": "Ingested file successfully"}
    
    # Verify file was uploaded to S3
    try:
        s3.head_object(Bucket=config.s3_bucket, Key=TEST_FILE_KEY)
        print("File verified in S3")
    except Exception as e:
        pytest.fail(f"File not found in S3: {str(e)}")

    # Verify MongoDB entries
    file_doc = db.files.find_one({"file_key": TEST_FILE_KEY})
    assert file_doc is not None, "File document not found in MongoDB"
    
    chunks = list(db.chunks.find({"chat_id": TEST_CHAT_ID}))
    assert len(chunks) > 0, "No chunks found in MongoDB"
    print("File ingestion test passed!")

def test_vector_search():
    """Test vector search endpoint with MongoDB"""
    print("\nTesting vector search...")
    query = "test query"
    print(f"Search query: {query}")
    response = client.get(f"/v1/vector_search?query={query}&chat_id={TEST_CHAT_ID}")
    
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    if len(results) > 0:
        assert "text" in results[0]
        # Verify results match MongoDB data
        chunk_texts = [chunk["text"] for chunk in db.chunks.find({"chat_id": TEST_CHAT_ID})]
        assert all(result["text"] in chunk_texts for result in results)
    print("Vector search test passed!")

def test_keyword_search():
    """Test keyword search endpoint with MongoDB"""
    print("\nTesting keyword search...")
    query = "test query"
    print(f"Search query: {query}")
    response = client.get(f"/v1/keyword_search?query={query}&chat_id={TEST_CHAT_ID}")
    
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    if len(results) > 0:
        assert "text" in results[0]
        # Verify results match MongoDB data
        chunk_texts = [chunk["text"] for chunk in db.chunks.find({"chat_id": TEST_CHAT_ID})]
        assert all(result["text"] in chunk_texts for result in results)
    print("Keyword search test passed!")

def test_delete_file():
    """Test file deletion endpoint with real S3 and MongoDB"""
    print("\nTesting file deletion...")
    
    # Upload a test file to S3 first
    try:
        s3.put_object(
            Bucket=config.s3_bucket,
            Key=TEST_FILE_KEY,
            Body=b"test content"
        )
    except Exception as e:
        pytest.fail(f"Failed to upload test file to S3: {str(e)}")
    
    # Insert test data into MongoDB
    db.files.insert_one({
        "file_key": TEST_FILE_KEY,
        "file_name": "test.pdf",
        "full_text": "test content"
    })
    db.chunks.insert_one({
        "chat_id": TEST_CHAT_ID,
        "file_key": TEST_FILE_KEY,
        "text": "test content",
        "chunk_id": 0
    })
    
    payload = {
        "file_key": TEST_FILE_KEY
    }
    print(f"Deleting file: {TEST_FILE_KEY}")
    response = client.request(
        "DELETE",
        "/v1/delete_file",
        json=payload
    )
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json() == {"message": "File deleted successfully"}
    
    # Verify file was deleted from S3
    try:
        s3.head_object(Bucket=config.s3_bucket, Key=TEST_FILE_KEY)
        pytest.fail("File still exists in S3")
    except s3.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code != '404':
            pytest.fail(f"Unexpected error: {str(e)}")
    
    # Verify MongoDB entries were deleted
    assert db.files.find_one({"file_key": TEST_FILE_KEY}) is None, "File document still exists in MongoDB"
    assert db.chunks.find_one({"chat_id": TEST_CHAT_ID}) is None, "Chunks still exist in MongoDB"
    print("File deletion test passed!")

@pytest.mark.integration
def test_complete_flow(test_pdf):
    """Test the complete flow with real S3 and MongoDB"""
    print("\nTesting complete flow...")
    
    # 1. Upload file
    print("Step 1: Uploading file...")
    with open(test_pdf, "rb") as f:
        files = {
            "file": ("test.pdf", f, "application/pdf")
        }
        data = {
            "file_key": TEST_FILE_KEY,
            "chat_id": TEST_CHAT_ID
        }
        response = client.post("/v1/ingest_file", files=files, data=data)
    assert response.status_code == 200
    
    # Verify S3 and MongoDB
    try:
        s3.head_object(Bucket=config.s3_bucket, Key=TEST_FILE_KEY)
        print("File upload verified in S3")
    except Exception as e:
        pytest.fail(f"File not found in S3: {str(e)}")
    
    assert db.files.find_one({"file_key": TEST_FILE_KEY}) is not None
    assert db.chunks.find_one({"chat_id": TEST_CHAT_ID}) is not None
    print("File upload successful!")
    
    # 2. Perform searches
    query = "test query"
    print(f"\nStep 2: Testing searches with query: {query}")
    
    # Vector search
    print("Testing vector search...")
    response = client.get(f"/v1/vector_search?query={query}&chat_id={TEST_CHAT_ID}")
    assert response.status_code == 200
    print("Vector search successful!")
    
    # Keyword search
    print("Testing keyword search...")
    response = client.get(f"/v1/keyword_search?query={query}&chat_id={TEST_CHAT_ID}")
    assert response.status_code == 200
    print("Keyword search successful!")
    
    # Hybrid search
    print("Testing hybrid search...")
    response = client.get(f"/v1/hybrid_search?query={query}&chat_id={TEST_CHAT_ID}")
    assert response.status_code == 200
    print("Hybrid search successful!")
    
    # 3. Delete file
    print("\nStep 3: Deleting file...")
    payload = {
        "file_key": TEST_FILE_KEY
    }
    response = client.request(
        "DELETE",
        "/v1/delete_file",
        json=payload
    )
    assert response.status_code == 200
    
    # Verify deletion
    try:
        s3.head_object(Bucket=config.s3_bucket, Key=TEST_FILE_KEY)
        pytest.fail("File still exists in S3")
    except s3.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code != '404':
            pytest.fail(f"Unexpected error: {str(e)}")
    print("File deletion successful!")
    
    print("\nComplete flow test passed!")