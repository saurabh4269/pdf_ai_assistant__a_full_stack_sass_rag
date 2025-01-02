from pymongo import MongoClient
from pprint import pprint
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv(dotenv_path='../.env')

def test_mongodb_connection():
    # Replace with your MongoDB connection string
    MONGODB_URL = os.getenv('MONGODB_URL')
    
    try:
        # 1. Test Connection
        print("Testing MongoDB connection...")
        client = MongoClient(MONGODB_URL)
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # 2. Access Database
        db = client['RAG']
        
        # 3. Test File Collection
        print("\nTesting UploadedFile collection...")
        file_collection = db['UploadedFile']
        test_file = {
            'file_name': 'test.pdf',
            'file_key': 'test/test.pdf',
            'file_url': 'https://d3ise5tbc77djz.cloudfront.net/test/test.pdf',
            'full_text': 'This is a test document.'
        }
        
        # Insert test document
        file_result = file_collection.insert_one(test_file)
        print("✅ File document inserted with ID:", file_result.inserted_id)
        
        # Verify insertion
        found_file = file_collection.find_one({'file_name': 'test.pdf'})
        print("✅ File document retrieved successfully")
        
        # 4. Test Embedding Collection
        print("\nTesting Embedding collection...")
        embedding_collection = db['Embedding']
        test_embedding = {
            'text': 'This is a test embedding',
            'embedding': [0.1] * 768,  # Dummy embedding vector
            'chat_id': 'test_chat',
            'file_key': 'test/test.pdf',
            'file_name': 'test.pdf',
            'word_size': 5
        }
        
        # Insert test embedding
        embedding_result = embedding_collection.insert_one(test_embedding)
        print("✅ Embedding document inserted with ID:", embedding_result.inserted_id)
        
        # 5. Test Vector Search (if index exists)
        print("\nTesting vector search...")
        try:
            vector_results = db['Embedding'].aggregate([
                {
                    "$vectorSearch": {
                        "index": "vector_index",
                        "path": "embedding",
                        "queryVector": [0.1] * 768,
                        "numCandidates": 1,
                        "limit": 1
                    }
                }
            ])
            list(vector_results)  # Execute the aggregation
            print("✅ Vector search working")
        except Exception as e:
            print("⚠️ Vector search failed (might need index setup):", str(e))
        
        # 6. Test Keyword Search
        print("\nTesting keyword search...")
        try:
            keyword_results = db['Embedding'].aggregate([
                {
                    '$search': {
                        'index': 'default',
                        'text': {
                            'query': 'test',
                            'path': 'text'
                        }
                    }
                }
            ])
            list(keyword_results)  # Execute the aggregation
            print("✅ Keyword search working")
        except Exception as e:
            print("⚠️ Keyword search failed (might need index setup):", str(e))
        
        # 7. Clean up test data
        print("\nCleaning up test data...")
        file_collection.delete_one({'file_name': 'test.pdf'})
        embedding_collection.delete_one({'chat_id': 'test_chat'})
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print("❌ Error:", str(e))
    finally:
        client.close()
        print("\nMongoDB connection closed")

if __name__ == "__main__":
    test_mongodb_connection()