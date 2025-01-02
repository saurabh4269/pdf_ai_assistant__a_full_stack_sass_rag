import requests
from typing import List, Tuple

class JinaAI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
    def get_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks"""
        url = 'https://api.jina.ai/v1/embeddings'
        
        data = {
            'input': chunks,
            'model': 'jina-embeddings-v2-base-en'
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()  # Raise exception for bad status codes
            
            return [item['embedding'] for item in response.json()['data']]
            
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            raise
            
    def rerank(self, query: str, chunks: List[str], top_n: int = 5) -> Tuple[List[int], List[float]]:
        """Rerank chunks based on relevance to query"""
        url = "https://api.jina.ai/v1/rerank"
        
        data = {
            "model": "jina-reranker-v1-base-en",
            "query": query,
            "documents": chunks,
            "top_n": top_n
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            results = response.json()['results']
            indices = [r['index'] for r in results]
            scores = [r['relevance_score'] for r in results]
            
            return indices, scores
            
        except Exception as e:
            print(f"Error reranking documents: {str(e)}")
            raise

    def test_connection(self) -> bool:
        """Test if the Jina AI connection is working"""
        try:
            # Test embeddings
            test_chunks = ["Test sentence."]
            embeddings = self.get_embeddings(test_chunks)
            
            # Test reranking
            test_query = "test"
            indices, scores = self.rerank(test_query, test_chunks)
            
            return True
            
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False