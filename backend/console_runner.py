# backend/console_runner.py
"""
Console Runner
Terminal tabanlı etkileşimli modül. Kullanıcı PDF ekleyebilir, sorular sorabilir ve paralel görevleri test edebilir.
Bu modül, paralel executor ile GPU/CPU cihazlarını yönetir ve stub RAG işlevlerini çağırır.
"""

import asyncio
import os
from backend.config import Config
from backend.gpu.parallel_executor import ParallelExecutor
from backend.gpu.gpu_manager import GPUManager

DEMO_USER_ID = "user_default"


def _print_header():
    print("\n" + "=" * 70)
    print(f"{Config.APP_NAME} - Console Mode".center(70))
    print("=" * 70 + "\n")


async def _index_pdfs_task(executor: ParallelExecutor, pdf_dir: str, user_id: str):
    """PDF'leri paralel olarak işleyen stub görev."""
    pdfs = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]
    if not pdfs:
        print("PDF dizininde işlenecek dosya bulunamadı:", pdf_dir)
        return

    print(f"{len(pdfs)} PDF bulundu. Paralel olarak işleniyor...")
    tasks = []

    for pdf in pdfs:
        filepath = os.path.join(pdf_dir, pdf)

        async def stub_ingest(path, user_id, device):
            print(f"[{device}] Başlıyor -> {os.path.basename(path)}")
            await asyncio.sleep(1 + (hash(path) % 3))
            print(f"[{device}] Bitti -> {os.path.basename(path)}")
            return {"file": path, "status": "ok"}

        tasks.append(executor.submit(stub_ingest, filepath, user_id))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    success = sum(1 for r in results if not isinstance(r, Exception))
    print(f"İşleme tamamlandı. Başarılı: {success}/{len(pdfs)}")


async def _ask_question_task(executor: ParallelExecutor, question: str, user_id: str):
    """Soru-cevap görevlerini stub ile paralel olarak çalıştırır."""

    async def stub_rag(query, user_id, device):
        print(f"[{device}] Sorgu alındı: {query[:80]}...")
        await asyncio.sleep(0.8)
        return {"answer": f"Simulated answer for '{query[:40]}...'", "device": device}

    res = await executor.submit(stub_rag, question, user_id)
    print("\n--- CEVAP ---")
    if isinstance(res, Exception):
        print("Sorgu işlenirken hata:", res)
    else:
        print(res["answer"])
    print("--------------\n")


async def _console_main():
    _print_header()

    gpu = GPUManager()
    gpu.show_status()
    Config.show_summary()

    executor = ParallelExecutor(devices=gpu.get_all_devices(), per_device_concurrency=2)

    while True:
        print("Seçimler:")
        print("  1) Yeni PDF'leri Tara ve Kütüphaneye Ekle (paralel)")
        print("  2) Kütüphaneye Soru Sor")
        print("  3) Kütüphanedeki Kitapları Listele")
        print("  q) Çıkış")
