import requests
from typing import List
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv(dotenv_path='../.env')


def test_jina_ai():
    # Replace with your API key
    JINA_API_KEY = os.getenv('JINA_API_KEY')
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {JINA_API_KEY}'
    }
    
    try:
        # 1. Test Embeddings
        print("Testing embeddings generation...")
        url = 'https://api.jina.ai/v1/embeddings'
        test_chunks = ["This is a test sentence.", "Another test sentence."]
        
        data = {
            'input': test_chunks,
            'model': 'jina-embeddings-v2-base-en'
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            embeddings = response.json()['data']
            print(f"✅ Embeddings generated successfully!")
            print(f"   Embedding dimension: {len(embeddings[0]['embedding'])}")
        else:
            print(f"❌ Embeddings generation failed: {response.text}")
            
        # 2. Test Reranking
        print("\nTesting reranking...")
        url = "https://api.jina.ai/v1/rerank"
        test_query = "test query"
        test_documents = ["First test document.", "Second test document."]
        
        data = {
            "model": "jina-reranker-v1-base-en",
            "query": test_query,
            "documents": test_documents,
            "top_n": 2
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            results = response.json()['results']
            print("✅ Reranking successful!")
            print("   Reranked results:")
            for result in results:
                print(f"   - Index: {result['index']}, Score: {result['relevance_score']:.4f}")
        else:
            print(f"❌ Reranking failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_jina_ai()