import re
import string
import nltk
import os
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Download all required NLTK data
try:
    # Create NLTK data directory if it doesn't exist
    nltk_data_dir = os.path.expanduser('~/nltk_data')
    if not os.path.exists(nltk_data_dir):
        os.makedirs(nltk_data_dir)
    
    # Download required data
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except Exception as e:
    print(f"Error downloading NLTK data: {e}")
    print("Please run this command in your terminal:")
    print("python -m nltk.downloader punkt stopwords wordnet punkt_tab averaged_perceptron_tagger")

class TextProcessor:
    def __init__(self):
        self.stemmer = PorterStemmer() # Cuts words down to their root form: "running" -> "run"
        self.lemmatizer = WordNetLemmatizer() # Convert words to their dictionary form: "better" -> "good"
        self.stop_words = set(stopwords.words('english')) # Common words to ignore: "the", "is", "and"
        
        # # Add domain-specific stopwords
        # with open('data/stopwords.txt', 'r') as f:
        #     custom_stopwords = [line.strip() for line in f]
        #     self.stop_words.update(custom_stopwords)
    
    def preprocess(self, text, lemmatize=True, stem=False):
        """Preprocess text: lowercase, remove punctuation, tokenize, remove stopwords, stem/lemmatize"""
        if not text:
            return []
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        tokens = [word for word in tokens if word not in self.stop_words]
        
        # Lemmatize or stem
        if lemmatize:
            tokens = [self.lemmatizer.lemmatize(word) for word in tokens]
        elif stem:
            tokens = [self.stemmer.stem(word) for word in tokens]
            
        return tokens
    
    def extract_sentences(self, text):
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def normalize_text(self, text):
        """Basic text normalization without tokenization"""
        if not text:
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        
        # Replace punctuation with space
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

# Example usage
if __name__ == "__main__":
    processor = TextProcessor()
    text = "Senior Software Engineer needed at TechCorp. Must have 5+ years of experience with Python programming. Knowledge of Django and REST APIs required. Experience with AWS cloud services is a plus. Bachelor's degree in Computer Science or related field required."
    print(processor.preprocess(text))
    print(processor.extract_sentences(text))
    print(processor.normalize_text(text))