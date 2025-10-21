import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
import torch


class Embedder:
    def __init__(self, model: SentenceTransformer):
        self.model = model

    def get_chunks(self, text: str, splitter: str='\n\n') -> List:
        return text.split(splitter)        

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        embeddings = self.model.encode(texts)
        return np.array(embeddings)

    @staticmethod
    def cos_compare(emb1: list, emb2: list) -> float:
        dot = np.dot(emb1, emb2)
        norm = np.linalg.norm(emb1) * np.linalg.norm(emb2)
        return 0.0 if norm == 0 else dot / norm
    

if __name__ == '__main__':
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2').to(DEVICE)
    embedder = Embedder(model)

    text1 = 'Сегодня хорошая погода и светит солнце.'
    text2 = 'На улице солнечно и погода отличная.'

    emb1, emb2 = embedder.get_embeddings([text1, text2])
    similarity = embedder.cos_compare(emb1, emb2)
    print(f"Косинусное сходство: {similarity}")
