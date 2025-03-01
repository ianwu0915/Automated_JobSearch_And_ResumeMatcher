import numpy as np
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    # Handle zero vectors
    if np.sum(vec1) == 0 or np.sum(vec2) == 0:
        return 0.0
        
    # Convert to numpy arrays if needed
    if not isinstance(vec1, np.ndarray):
        vec1 = np.array(vec1)
    if not isinstance(vec2, np.ndarray):
        vec2 = np.array(vec2)
        
    # Reshape for sklearn if needed
    if len(vec1.shape) == 1:
        vec1 = vec1.reshape(1, -1)
    if len(vec2.shape) == 1:
        vec2 = vec2.reshape(1, -1)
        
    return float(sklearn_cosine(vec1, vec2)[0][0])

def jaccard_similarity(set1, set2):
    """Calculate Jaccard similarity between two sets"""
    if not set1 or not set2:
        return 0.0
        
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0

def normalize_score(score, min_val=0, max_val=1):
    """Normalize score to 0-100 range"""
    return max(0, min(100, (score - min_val) / (max_val - min_val) * 100))