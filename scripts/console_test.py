# scripts/console_test.py
"""
console_test.py
-----------------
Sistem test aracı: paralel executor ve console runner'ı test eder.
Amaç: PDF tarama, sorgu ve stub iş akışını hızlıca doğrulamak.
Her şey stub modda çalışır; gerçek ingestion/RAG bağlanmamıştır.
"""

import asyncio
import os
import random
import time
from backend.config import Config
from backend.gpu.parallel_executor import ParallelExecutor

# -------------------------
# TEST AYARLARI
# -------------------------
TEST_PDF_DIR = Config.PDF_SOURCE_DIR
SIMULATED_PDF_COUNT = 5
SIMULATED_LATENCY = (0.5, 1.2)

# -------------------------
# HELPER / STUB FUNCTIONS
# -------------------------
async def stub_pdf_ingest(file_path: str, device: str):
    """PDF işleme stub fonksiyonu."""
    print(f"[{device}] Başlıyor -> {os.path.basename(file_path)}")
    await asyncio.sleep(random.uniform(*SIMULATED_LATENCY))
    print(f"[{device}] Bitti -> {os.path.basename(file_path)}")
    return {"file": file_path, "status": "ok"}


async def stub_question_answer(question: str, device: str):
    """Soru-cevap stub fonksiyonu."""
    print(f"[{device}] Sorgu alındı: {question[:50]}...")
    await asyncio.sleep(random.uniform(*SIMULATED_LATENCY))
    answer = f"Simulated answer for '{question[:30]}...'"
    print(f"[{device}] Cevap hazır -> {answer}")
    return answer


# -------------------------
# TEST AKIŞI
# -------------------------
async def run_console_test():
    print("\n=== Başlatılıyor: Console Test ===\n")

    # ParallelExecutor
    devices = ["cpu"]
    if Config.NUM_GPUS > 0:
        devices = [f"cuda:{i}" for i in range(Config.NUM_GPUS)]
    executor = ParallelExecutor(devices=devices, per_device_concurrency=2)

    # Test PDF dizini oluştur
    os.makedirs(TEST_PDF_DIR, exist_ok=True)
    pdf_files = []
    for i in range(SIMULATED_PDF_COUNT):
        file_path = os.path.join(TEST_PDF_DIR, f"test_doc_{i+1}.pdf")
        with open(file_path, "w") as f:
            f.write("Dummy PDF content\n")
        pdf_files.append(file_path)

    print(f"{len(pdf_files)} test PDF dosyası oluşturuldu.\n")

    # 1) PDFleri paralel işleme
    print(">>> PDF İşleme Testi Başlıyor...\n")
    tasks = [executor.submit(stub_pdf_ingest, f) for f in pdf_files]
    await asyncio.gather(*tasks)
    print("\n>>> PDF İşleme Testi Tamamlandı.\n")

    # 2) Soru-Cevap Testi
    print(">>> Soru-Cevap Testi Başlıyor...\n")
    questions = [
        "Örnek soru 1: PDF içerik hakkında?",
        "Örnek soru 2: Sistemin kapasitesi nedir?",
        "Örnek soru 3: Paralel işlem çalışıyor mu?"
    ]
    qa_tasks = [executor.submit(stub_question_answer, q) for q in questions]
    await asyncio.gather(*qa_tasks)
    print("\n>>> Soru-Cevap Testi Tamamlandı.\n")

    # 3) Cleanup
    print(">>> Test tamamlandı. Oluşturulan PDF dosyaları temizleniyor...")
    for f in pdf_files:
        os.remove(f)
    print(">>> Temizlik tamamlandı.\n")

    # Shutdown executor
    await executor.shutdown()
    print("=== Console Test Sonlandı ===\n")


# -------------------------
# ENTRY POINT
# -------------------------
if __name__ == "__main__":
    asyncio.run(run_console_test())
