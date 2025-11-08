# backend/rag/query_intent.py
"""
query_intent.py
RAG sistemi için sorgu niyet analiz modülü.
Bu modül, kullanıcı sorgusunu anlayarak intent sınıflandırması, tür tayini ve ön işleme sağlar.
Sistem paralel çalışacak şekilde tasarlanmıştır, async desteklidir ve GPU/CPU cihazlarına göre optimize edilebilir.
"""

import asyncio
import re
from typing import Dict, Any, Optional

class QueryIntent:
    """
    Kullanıcı sorgusunun niyetini çıkaran sınıf.
    """
    def __init__(self, query: str, user_id: Optional[str] = None):
        self.query = query.strip()
        self.user_id = user_id
        self.intent: Optional[str] = None
        self.entities: Dict[str, Any] = {}
        self.intent_score: float = 0.0

    async def analyze(self, device: str = "cpu") -> Dict[str, Any]:
        """
        Sorguyu analiz eder ve intent + entity çıkarımı döndürür.
        Async, paralel çalışmaya uygun stub.
        """
        # TODO: buraya gerçek LLM veya intent model çağrısı eklenecek
        await asyncio.sleep(0.1)  # simulate latency

        # Basit örnek intent çıkarımı
        lowered = self.query.lower()
        if any(w in lowered for w in ["pdf", "document", "book"]):
            self.intent = "ingest"
            self.intent_score = 0.95
        elif any(w in lowered for w in ["find", "search", "query", "what"]):
            self.intent = "retrieve"
            self.intent_score = 0.9
        else:
            self.intent = "unknown"
            self.intent_score = 0.5

        # Entity çıkarımı (stub)
        self.entities = self._extract_entities(lowered)

        return self.to_dict()

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Basit regex ile entity çıkarımı. 
        Gerçek sistemde NER modeline bağlanacak.
        """
        urls = re.findall(r'https?://\S+', text)
        emails = re.findall(r'\S+@\S+', text)
        return {
            "urls": urls,
            "emails": emails,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "user_id": self.user_id,
            "intent": self.intent,
            "intent_score": self.intent_score,
            "entities": self.entities,
        }

# Standalone test
if __name__ == "__main__":
    import asyncio

    async def test():
        queries = [
            "Lütfen PDF dosyasını ekle",
            "Bu dokümanı ara ve bana özet ver",
            "Merhaba, nasılsın?"
        ]
        for q in queries:
            qi = QueryIntent(q, user_id="test_user")
            res = await qi.analyze()
            print(res)

    asyncio.run(test())
