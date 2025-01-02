import nltk
from textblob.download_corpora import download_all

def setup_dependencies():
    """Download all required dependencies"""
    print("Downloading NLTK data...")
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('brown')
    nltk.download('punkt_tab')
    nltk.download('wordnet')
    
    print("\nDownloading TextBlob corpora...")
    download_all()
    
    print("\nSetup complete!")

if __name__ == "__main__":
    setup_dependencies()
