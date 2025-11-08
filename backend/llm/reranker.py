# backend/llm/reranker.py
"""
Reranker.py
Bu modül, embedding ve retrieval sonuçlarını sıralamak için kullanılan Cross-Encoder veya benzeri
reranker modellerini yönetir. Hem tekli hem çoklu GPU kullanımını destekler.
Paralel görevler için device parametrelerini dikkate alır.
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from backend.config import Config
from backend.gpu.gpu_manager import GPUManager
import asyncio
from typing import List, Tuple, Optional


class Reranker:
    """
    Cross-encoder tabanlı reranker sınıfı.
    Önemli fonksiyonlar:
      - load_model: modeli yükler ve GPU/CPU'ya yerleştirir.
      - rank: query + candidate listesi alır ve skor sıralaması döndürür.
      - async_rank: async kullanım için coroutine versiyonu.
    """

    def __init__(self, model_repo: str = Config.RERANKER_MODEL_REPO, device: Optional[str] = None):
        self.model_repo = model_repo
        self.device = device or self._get_device()
        self.tokenizer = None
        self.model = None
        self.gpu_manager = GPUManager()

    def _get_device(self) -> str:
        """Varsayılan olarak en iyi GPU'yu seçer veya CPU fallback."""
        return self.gpu_manager.get_best_gpu()

    def load_model(self):
        """Tokenizer ve model yükleme."""
        print(f"[{self.device}] Reranker modeli yükleniyor: {self.model_repo}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_repo, use_fast=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_repo)
        self.model.to(self.device)
        self.model.eval()
        print(f"[{self.device}] Model başarıyla yüklendi.")

    @torch.no_grad()
    def rank(self, query: str, candidates: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Query ve candidate listesi alır, skorları hesaplar ve en iyi top_k döndürür.
        """
        if not self.model or not self.tokenizer:
            self.load_model()

        scores = []
        for candidate in candidates:
            inputs = self.tokenizer(query, candidate, return_tensors="pt", truncation=True, padding=True).to(self.device)
            outputs = self.model(**inputs)
            score = torch.softmax(outputs.logits, dim=-1)[0][1].item()
            scores.append((candidate, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    async def async_rank(self, query: str, candidates: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Async versiyonu, ParallelExecutor veya asyncio loop içinde kullanılabilir.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.rank, query, candidates, top_k)

    def batch_rank(self, queries: List[str], candidate_lists: List[List[str]], top_k: int = 5) -> List[List[Tuple[str, float]]]:
        """
        Birden fazla query için batch ranking.
        """
        assert len(queries) == len(candidate_lists), "Queries ve candidate listeleri uzunluğu eşit olmalı."
        results = []
        for q, cands in zip(queries, candidate_lists):
            result = self.rank(q, cands, top_k=top_k)
            results.append(result)
        return results

    async def async_batch_rank(self, queries: List[str], candidate_lists: List[List[str]], top_k: int = 5) -> List[List[Tuple[str, float]]]:
        """
        Async batch rank, paralel sorgular için uygundur.
        """
        tasks = []
        for q, cands in zip(queries, candidate_lists):
            tasks.append(self.async_rank(q, cands, top_k))
        return await asyncio.gather(*tasks, return_exceptions=False)

    def rerank_with_scores(self, query: str, candidates: List[str], scores: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Harici skorlar ile reranking yapılabilir.
        scores: candidates ile eşleşen float listesi
        """
        assert len(candidates) == len(scores), "Candidates ve skor listesi uzunluğu eşit olmalı."
        combined = list(zip(candidates, scores))
        # Öncelikle skorları güncelle, sonra model skorları ile birleştir
        ranked = self.rank(query, candidates, top_k=len(candidates))
        reranked_dict = {c: s for c, s in ranked}
        for i, (c, s) in enumerate(combined):
            combined[i] = (c, s + reranked_dict.get(c, 0))
        combined.sort(key=lambda x: x[1], reverse=True)
        return combined[:top_k]


# ==========================
# TEST / STUB
# ==========================
if __name__ == "__main__":
    r = Reranker()
    r.load_model()
    queries = ["Yapay zeka ve eğitim hakkında"]
    candidates = ["Makale 1: Eğitimde yapay zeka", "Makale 2: Spor ve sağlık", "Makale 3: AI uygulamaları"]
    results = r.rank(queries[0], candidates, top_k=3)
    print("Rerank Sonuçları:")
    for cand, score in results:
        print(f"  {cand} -> {score:.4f}")
