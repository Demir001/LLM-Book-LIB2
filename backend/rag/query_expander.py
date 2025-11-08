# backend/rag/query_expander.py
"""
query_expander.py
=================
Sorguları genişleterek bilgi çekme (retrieval) performansını artıran modül.
Query Expansion, LLM veya embedding tabanlı yöntemlerle ana soruya benzer ek sorgular üretir.
Paralel olarak çalışabilir ve GPU/CPU cihazına göre optimize edilebilir.
"""

import asyncio
import random
from typing import List, Optional, Union

from backend.config import Config


class QueryExpander:
    """
    Sorgu genişletme sınıfı.
    - LLM veya embedding tabanlı genişletme yöntemlerini destekler.
    - Paralel olarak birden çok sorgu için expand edebilir.
    - Hallucination'ı minimuma indirgemek için güvenlik kontrolleri içerir.
    """

    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        self.model_name = model_name or "llm-query-expander"
        self.device = device or Config.DEVICE
        self._simulation_mode = Config.SIMULATION_MODE

    async def expand_queries(
        self,
        queries: Union[str, List[str]],
        top_k: int = 3,
        max_length: int = 64
    ) -> List[str]:
        """
        Ana sorguyu alır ve ek ilgili sorgular üretir.
        Parametreler:
        - queries: tek bir string veya string listesi
        - top_k: her sorgudan kaç yeni varyasyon üretileceği
        - max_length: LLM tabanlı üretimde maksimum token uzunluğu
        Döndürür:
        - genişletilmiş sorgu listesi
        """
        if isinstance(queries, str):
            queries = [queries]

        expanded_queries = []
        tasks = [self._expand_single(q, top_k, max_length) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for res in results:
            if isinstance(res, Exception):
                continue
            expanded_queries.extend(res)

        # Hallucination kontrolü (stub)
        expanded_queries = [q for q in expanded_queries if self._validate_query(q)]

        return expanded_queries

    async def _expand_single(self, query: str, top_k: int, max_length: int) -> List[str]:
        """
        Tek bir sorguyu genişletir.
        Bu stub fonksiyon simülasyon için random varyasyon üretir.
        Gerçek kullanımda LLM veya embedding tabanlı model çağrılır.
        """
        await asyncio.sleep(random.uniform(*Config.SIMULATED_LATENCY_RANGE))  # simule delay
        expanded = [f"{query} alternatif {i+1}" for i in range(top_k)]
        return expanded

    def _validate_query(self, query: str) -> bool:
        """
        Basit doğrulama: kısa ve anlamlı sorgular bırakılır.
        Hallucination azaltma amacıyla uygulanır.
        """
        if not query or len(query.strip()) < 3:
            return False
        return True

    async def expand_and_rank(
        self,
        queries: Union[str, List[str]],
        top_k: int = 5,
        reranker=None
    ) -> List[str]:
        """
        Query Expansion + Reranking kombinasyonu.
        - reranker: opsiyonel fonksiyon veya coroutine, genişletilmiş sorguları puanlayıp sıralar.
        """
        expanded = await self.expand_queries(queries, top_k=top_k)
        if reranker:
            if asyncio.iscoroutinefunction(reranker):
                scores = await reranker(expanded)
            else:
                scores = reranker(expanded)
            # skorlamaya göre sırala
            expanded = [q for _, q in sorted(zip(scores, expanded), reverse=True)]
        return expanded

    async def expand_for_user(
        self,
        user_id: str,
        query: str,
        top_k: int = 3
    ) -> List[str]:
        """
        Kullanıcı bazlı sorgu genişletme (gizlilik / kişiselleştirme için stub)
        """
        # TODO: kişiselleştirme bağlanacak
        return await self.expand_queries(query, top_k=top_k)


# ==========================
# TEST / ÖRNEK
# ==========================
async def _test():
    qe = QueryExpander()
    expanded = await qe.expand_queries(["AI ile PDF analiz", "RAG sistemi performans"])
    print("Genişletilmiş sorgular:")
    for q in expanded:
        print("-", q)


if __name__ == "__main__":
    import asyncio
    asyncio.run(_test())
