# backend/utils/text_tools.py
"""
text_tools.py
Metin işleme ve NLP yardımcı fonksiyonları modülü.
İçerik: tokenizasyon, temizleme, cümle bölme, embedding ön hazırlık ve basit metin normalizasyonları.
"""

import re
import unicodedata
from typing import List, Optional

class TextTools:
    @staticmethod
    def normalize_text(text: str, lowercase: bool = True, remove_punctuation: bool = True) -> str:
        """
        Metni normalize eder:
        - Unicode normalize (NFKC)
        - İsteğe bağlı lowercase
        - İsteğe bağlı noktalama kaldırma
        """
        if not text:
            return ""
        text = unicodedata.normalize("NFKC", text)
        if lowercase:
            text = text.lower()
        if remove_punctuation:
            text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def split_sentences(text: str) -> List[str]:
        """
        Basit cümle bölme:
        - Noktalama işaretlerine göre bölme
        - Boş cümleleri atla
        """
        if not text:
            return []
        sentences = re.split(r'(?<=[.!?]) +', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
        """
        Metni parçalara böler:
        - Her chunk chunk_size token civarı olacak
        - Chunklar overlap kadar kesişim içerir
        """
        sentences = TextTools.split_sentences(text)
        chunks = []
        current_chunk = []
        current_len = 0

        for sentence in sentences:
            sentence_len = len(sentence.split())
            if current_len + sentence_len > chunk_size:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = current_chunk[-overlap:] if overlap < len(current_chunk) else current_chunk
                    current_len = sum(len(s.split()) for s in current_chunk)
            current_chunk.append(sentence)
            current_len += sentence_len

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    @staticmethod
    def remove_stopwords(text: str, stopwords: Optional[List[str]] = None) -> str:
        """
        Basit stopword temizleme
        """
        if not text:
            return ""
        if stopwords is None:
            # örnek Türkçe + İngilizce stopwords (minimal)
            stopwords = ["ve", "ile", "bir", "bu", "da", "the", "and", "is", "in", "on"]
        words = text.split()
        words = [w for w in words if w not in stopwords]
        return " ".join(words)

    @staticmethod
    def summarize_text(text: str, max_sentences: int = 3) -> str:
        """
        Basit özetleme: ilk n cümleyi al
        Daha gelişmiş yöntemler hyde/LLM ile yapılacak.
        """
        sentences = TextTools.split_sentences(text)
        return " ".join(sentences[:max_sentences])

    @staticmethod
    def clean_whitespace(text: str) -> str:
        """
        Gereksiz boşluk ve tab karakterlerini temizler
        """
        if not text:
            return ""
        text = re.sub(r"\s+", " ", text)
        return text.strip()


# ==========================
# ÖRNEK KULLANIM
# ==========================
if __name__ == "__main__":
    sample_text = "Merhaba! Bu bir testtir. NLP araçlarıyla metin işleme çok faydalıdır."
    print("Orijinal:", sample_text)
    print("Normalize:", TextTools.normalize_text(sample_text))
    print("Sentences:", TextTools.split_sentences(sample_text))
    print("Chunks:", TextTools.chunk_text(sample_text, chunk_size=5, overlap=1))
    print("No Stopwords:", TextTools.remove_stopwords(sample_text))
    print("Summary:", TextTools.summarize_text(sample_text))
