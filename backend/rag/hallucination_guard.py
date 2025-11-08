# backend/rag/hallucination_guard.py
"""
hallucination_guard.py
----------------------
Bu modül, RAG (Retrieval-Augmented Generation) pipeline'ında
LLM’in halüsinasyonlarını en aza indirmek için kontroller ve
denetimler sağlar. Hem retrieval hem generation aşamasında
güvenlik ve doğruluk filtreleri uygular.
"""

import re
import asyncio
from typing import List, Dict, Any, Optional


class HallucinationGuard:
    """
    LLM cevaplarını ve retrieval sonuçlarını denetler,
    alakasız veya mantıksal olarak tutarsız içerikleri filtreler.
    """

    def __init__(self, similarity_threshold: float = 0.75, banned_patterns: Optional[List[str]] = None):
        """
        Args:
            similarity_threshold (float): Retrieval sonuçlarının kabul eşiği.
            banned_patterns (List[str]): Regex listesi, LLM cevaplarında
                                         bulunması istenmeyen ifadeler.
        """
        self.similarity_threshold = similarity_threshold
        self.banned_patterns = banned_patterns or [
            r"lütfen benim yanıtımı takip etmeyin",
            r"benimle ilgili bilinmeyen bilgiler",
            r"inanılmaz derecede yanlış",
        ]

    def _check_patterns(self, text: str) -> bool:
        """Text, banned_patterns ile eşleşiyorsa False döner."""
        for pattern in self.banned_patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                return False
        return True

    def filter_retrieval_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Retrieval sonuçlarını halüsinasyon riskine göre filtreler.
        Args:
            results: List[Dict], her dict {'content': str, 'score': float}
        Returns:
            Filtrelenmiş list
        """
        filtered = [
            r for r in results
            if r.get("score", 0.0) >= self.similarity_threshold
            and self._check_patterns(r.get("content", ""))
        ]
        return filtered

    async def async_filter_generation(self, generations: List[str]) -> List[str]:
        """
        Generation çıktılarında eşleşmeleri kontrol eder.
        Async versiyon, streaming veya paralel generation için uygundur.
        """
        filtered = []
        for gen in generations:
            if self._check_patterns(gen):
                filtered.append(gen)
        await asyncio.sleep(0)  # event loop yield
        return filtered

    def validate_answer(self, answer: str, retrieval_contexts: Optional[List[str]] = None) -> bool:
        """
        Tek bir cevabın doğruluğunu ve güvenilirliğini kontrol eder.
        Args:
            answer: LLM tarafından üretilmiş string
            retrieval_contexts: opsiyonel, reference context listesi
        Returns:
            True/False
        """
        if not self._check_patterns(answer):
            return False
        if retrieval_contexts:
            # basit check: cevabın en azından bir context ile eşleşmesi
            if not any(ctx.lower() in answer.lower() for ctx in retrieval_contexts):
                return False
        return True

    async def async_validate_batch(self, answers: List[str], contexts_batch: Optional[List[List[str]]] = None) -> List[bool]:
        """
        Çoklu cevapların batch doğrulaması (async)
        Args:
            answers: List[str]
            contexts_batch: List[List[str]] her cevabın context listesi
        Returns:
            List[bool] doğruluk durumları
        """
        results = []
        for i, ans in enumerate(answers):
            contexts = None
            if contexts_batch and i < len(contexts_batch):
                contexts = contexts_batch[i]
            results.append(self.validate_answer(ans, contexts))
            await asyncio.sleep(0)  # event loop yield
        return results

    def add_banned_pattern(self, pattern: str):
        """Banned patterns listesine yeni regex ekler."""
        if pattern not in self.banned_patterns:
            self.banned_patterns.append(pattern)

    def remove_banned_pattern(self, pattern: str):
        """Banned patterns listesinden regex çıkarır."""
        if pattern in self.banned_patterns:
            self.banned_patterns.remove(pattern)


# ==========================
# ÖRNEK KULLANIM
# ==========================
if __name__ == "__main__":
    hg = HallucinationGuard(similarity_threshold=0.8)
    retrieval_results = [
        {"content": "Bu doğru bir bilgi.", "score": 0.9},
        {"content": "Bilinmeyen ve hatalı içerik.", "score": 0.95},
        {"content": "lütfen benim yanıtımı takip etmeyin", "score": 0.99},
    ]
    filtered = hg.filter_retrieval_results(retrieval_results)
    print("Filtrelenmiş retrieval:", filtered)

    generations = ["Bu doğru.", "lütfen benim yanıtımı takip etmeyin", "Bilgi hatalı"]
    import asyncio
    filtered_gen = asyncio.run(hg.async_filter_generation(generations))
    print("Filtrelenmiş generation:", filtered_gen)

    ans_valid = hg.validate_answer("Bu doğru bilgi.", ["Bu doğru bilgi."])
    print("Cevap geçerli mi?", ans_valid)
