from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np


class SemanticClusterer:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name) if self._model_available(model_name) else None
    
    def _model_available(self, name):
        try:
            import sentence_transformers
            return True
        except ImportError:
            return False

    def cluster(self, conversations, n_clusters=10):
        if not self.model:
            return conversations, np.zeros(len(conversations))
        
        texts = [conv.get('title', '') + ' ' + conv.get('content', '') for conv in conversations]
        if not texts:
            return conversations, np.array([])
        
        embeddings = self.model.encode(texts)
        n_clusters = min(n_clusters, len(set(texts)))
        if n_clusters < 2:
            return conversations, np.zeros(len(conversations))
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)
        
        for i, conv in enumerate(conversations):
            conv['cluster'] = int(labels[i])
        
        return conversations, labels
