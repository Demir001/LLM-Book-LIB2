# scripts/benchmark_parallel.py
"""
Benchmark Parallel
------------------
Bu script, Advanced RAG System’in paralel görev yürütme altyapısını test eder.
Hem CPU hem GPU ortamlarında görevlerin eş zamanlı çalışmasını ve performansını ölçer.
Küçük, sahte PDF ve sorgu görevleri ile stub tabanlı testler yapılır.
"""

import asyncio
import random
import time
from backend.gpu.parallel_executor import ParallelExecutor
from backend.gpu.gpu_manager import GPUManager

NUM_TEST_TASKS = 20
SIMULATED_TASK_DURATION = (0.5, 2.0)  # saniye


async def simulated_task(task_id: int, device: str):
    """Stub görevi, rasgele süre bekleyip tamamlanır."""
    duration = random.uniform(*SIMULATED_TASK_DURATION)
    print(f"[{device}] Task {task_id} başlıyor ({duration:.2f}s)")
    await asyncio.sleep(duration)
    print(f"[{device}] Task {task_id} tamamlandı")
    return task_id, duration


async def run_benchmark():
    # GPU durumu
    gpu = GPUManager()
    devices = gpu.get_all_devices()
    print("Kullanılacak cihazlar:", devices)

    # Executor oluştur
    executor = ParallelExecutor(devices=devices, per_device_concurrency=2)

    # Görevleri submit et
    tasks = [executor.submit(simulated_task, i) for i in range(NUM_TEST_TASKS)]

    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.time()

    # Sonuçları raporla
    completed = sum(1 for r in results if not isinstance(r, Exception))
    failed = sum(1 for r in results if isinstance(r, Exception))
    print("\n=== Benchmark Sonuçları ===")
    print(f"Toplam Görev      : {NUM_TEST_TASKS}")
    print(f"Başarılı Görevler : {completed}")
    print(f"Hatalı Görevler   : {failed}")
    print(f"Toplam Süre       : {end_time - start_time:.2f} saniye")
    print("===========================\n")

    await executor.shutdown()


if __name__ == "__main__":
    asyncio.run(run_benchmark())
