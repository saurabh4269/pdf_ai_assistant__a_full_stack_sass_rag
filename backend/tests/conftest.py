import os
import sys
import pytest
import nltk
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from pymongo import MongoClient

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.config import config

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )

@pytest.fixture(scope="session", autouse=True)
def setup_nltk():
    """Download required NLTK data"""
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('brown')
    nltk.download('wordnet')

@pytest.fixture(autouse=True)
def env_setup():
    """Load test environment variables"""
    load_dotenv("tests/.env.test")

@pytest.fixture(scope="session")
def test_pdf():
    """Create a test PDF file"""
    if not os.path.exists("tests/test_data"):
        os.makedirs("tests/test_data")
        
    pdf_path = "tests/test_data/test.pdf"
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, "This is a test PDF document.")
    c.save()
    
    yield pdf_path
    
    # Cleanup
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

@pytest.fixture(scope="session")
def mongodb():
    """Setup MongoDB connection"""
    client = MongoClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('MONGODB_NAME', 'test_db')]
    yield db
    # Cleanup after all tests
    db.files.delete_many({"file_key": {"$regex": "^test/"}})
    db.chunks.delete_many({"chat_id": {"$regex": "^test_"}})
    client.close()