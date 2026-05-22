import numpy as np


class SemanticClusterer:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.model = None
        self._model = None

    def _lazy_load(self):
        if self._model is not None:
            return self._model
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            return self._model
        except ImportError:
            return None

    def cluster(self, conversations, n_clusters=10):
        model = self._lazy_load()
        if not model:
            return conversations, np.zeros(len(conversations))

        texts = [conv.get('title', '') + ' ' + conv.get('content', '') for conv in conversations]
        if not texts:
            return conversations, np.array([])

        embeddings = model.encode(texts)
        n_clusters = min(n_clusters, len(set(texts)))
        if n_clusters < 2:
            return conversations, np.zeros(len(conversations))

        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)

        for i, conv in enumerate(conversations):
            conv['cluster'] = int(labels[i])

        return conversations, labels
