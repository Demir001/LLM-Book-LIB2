# backend/gpu/parallel_executor.py
"""
ParallelExecutor.py
GPU/CPU cihazlarına görevleri dağıtmak için yüksek performanslı, async destekli executor.
Her cihaz için eşzamanlı görev sayısı ayarlanabilir, round-robin veya manuel device ataması yapılabilir.
ThreadPool ile bloklayan fonksiyonlar async ortamda güvenle çalıştırılır.
"""

import asyncio
import inspect
import functools
import concurrent.futures
from typing import Callable, Any, List, Optional, Dict


class ParallelExecutor:
    """
    Basit ama güçlü bir paralel görev dağıtıcı.
    - devices: ["cuda:0", "cuda:1", "cpu"]
    - per_device_concurrency: her cihaz için eşzamanlı görev limiti
    - submit(coro_fn, *args, device=None, **kwargs) -> asyncio.Task
      Cihaz belirtilmezse round-robin ile atanır.
    """

    def __init__(
        self,
        devices: Optional[List[str]] = None,
        per_device_concurrency: int = 2,
        thread_pool_workers: int = 8,
    ):
        self.devices = devices or ["cpu"]
        self.per_device_concurrency = per_device_concurrency
        self.device_locks: Dict[str, asyncio.Semaphore] = {
            d: asyncio.Semaphore(per_device_concurrency) for d in self.devices
        }
        self._rr_index = 0
        self._loop = asyncio.get_event_loop()
        self._thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=thread_pool_workers
        )
        self._active_tasks: List[asyncio.Task] = []
        self._shutdown = False

    def _pick_device(self) -> str:
        """Round-robin cihaz seçimi."""
        if not self.devices:
            return "cpu"
        device = self.devices[self._rr_index % len(self.devices)]
        self._rr_index += 1
        return device

    async def _run_on_device(self, device: str, fn: Callable, *args, **kwargs):
        """
        Cihaz bazlı semaphore ile görev çalıştırır.
        Async veya bloklayan fonksiyonlar desteklenir.
        """
        sem = self.device_locks.get(device, asyncio.Semaphore(self.per_device_concurrency))
        async with sem:
            # async fonksiyon ise doğrudan çalıştır
            if inspect.iscoroutinefunction(fn):
                return await fn(*args, device=device, **kwargs)
            else:
                # bloklayan fonksiyon -> thread pool
                func = functools.partial(fn, *args, device=device, **kwargs)
                return await self._loop.run_in_executor(self._thread_pool, func)

    def submit(self, fn: Callable, *args, device: Optional[str] = None, **kwargs) -> asyncio.Task:
        """
        Görev ekler ve asyncio.Task döner.
        Device belirtilmezse round-robin ile seçilir.
        """
        if self._shutdown:
            raise RuntimeError("Executor shutdown edilmiş durumda, yeni görev kabul edilmiyor.")
        chosen = device or self._pick_device()
        task = self._loop.create_task(self._run_on_device(chosen, fn, *args, **kwargs))
        self._active_tasks.append(task)

        # biten görevleri temizle
        def _on_done(t):
            try:
                self._active_tasks.remove(t)
            except ValueError:
                pass

        task.add_done_callback(_on_done)
        return task

    async def map(self, fn: Callable, iterable, device: Optional[str] = None):
        """
        Basit map: iterable öğeleri üzerinde paralel çalıştırır.
        """
        tasks = [self.submit(fn, item, device=device) for item in iterable]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def shutdown(self, wait: bool = True):
        """
        Executor'u kapatır; bekleyen görevler sonlanır.
        ThreadPool kapanır.
        """
        self._shutdown = True
        if wait and self._active_tasks:
            try:
                await asyncio.gather(*self._active_tasks, return_exceptions=True)
            except Exception:
                pass
        self._thread_pool.shutdown(wait=wait)

    # -----------------------------
    # Yardımcı Fonksiyonlar
    # -----------------------------
    def active_task_count(self) -> int:
        """Şu anda aktif görev sayısı."""
        return len(self._active_tasks)

    def list_devices(self) -> List[str]:
        """Tüm kullanılabilir cihazları döndürür."""
        return self.devices

    def set_per_device_concurrency(self, count: int):
        """Cihaz başına eşzamanlı görev sayısını değiştirir."""
        self.per_device_concurrency = count
        for device, sem in self.device_locks.items():
            sem._value = count

    async def wait_all(self):
        """Tüm aktif görevlerin bitmesini bekler."""
        if self._active_tasks:
            await asyncio.gather(*self._active_tasks, return_exceptions=True)


# ==========================
# TEST / DEMO
# ==========================
if __name__ == "__main__":
    import random

    async def demo_task(name, duration=None, device=None):
        duration = duration or random.uniform(0.5, 2.0)
        print(f"[{device}] Başlıyor -> {name} ({duration:.2f}s)")
        await asyncio.sleep(duration)
        print(f"[{device}] Bitti -> {name}")
        return name

    async def main():
        devices = ["cuda:0", "cuda:1", "cpu"]
        executor = ParallelExecutor(devices=devices, per_device_concurrency=2)
        tasks = [executor.submit(demo_task, f"Job-{i}") for i in range(6)]
        results = await asyncio.gather(*tasks)
        print("Sonuçlar:", results)
        await executor.shutdown()

    asyncio.run(main())
