# backend/utils/async_utils.py
"""
async_utils.py
Asenkron görev yönetimi ve yardımcı coroutine fonksiyonları.
Paralel çalışmayı kolaylaştırır, timeout ve retry mekanizmaları içerir.
"""

import asyncio
import functools
from typing import Callable, Any, Optional, Coroutine, List, Dict, Union
import random
import logging

logger = logging.getLogger(__name__)


class AsyncHelper:
    """
    Asenkron görevler için yardımcı sınıf.
    - timeout desteği
    - retry desteği
    - paralel gather yönetimi
    """

    @staticmethod
    async def run_with_timeout(coro: Coroutine, timeout: float, default: Any = None) -> Any:
        """
        Coroutine'i belirli bir süre çalıştırır, timeout olursa default döner.
        """
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Timeout ({timeout}s) aşıldı. Varsayılan değer döndürülüyor.")
            return default

    @staticmethod
    async def run_with_retries(coro_fn: Callable, retries: int = 3, delay: float = 0.5, *args, **kwargs):
        """
        Asenkron fonksiyonu belirli sayıda tekrar çalıştırır, başarısız olursa exception fırlatır.
        """
        last_exc = None
        for attempt in range(1, retries + 1):
            try:
                return await coro_fn(*args, **kwargs)
            except Exception as e:
                last_exc = e
                logger.warning(f"Retry {attempt}/{retries} failed: {e}")
                await asyncio.sleep(delay)
        raise last_exc

    @staticmethod
    async def gather_with_limit(coros: List[Coroutine], limit: int = 5) -> List[Any]:
        """
        Çok sayıda coroutine'i eşzamanlı sınırlama ile çalıştırır.
        """
        semaphore = asyncio.Semaphore(limit)
        results = []

        async def sem_task(coro):
            async with semaphore:
                return await coro

        tasks = [asyncio.create_task(sem_task(c)) for c in coros]
        for t in asyncio.as_completed(tasks):
            try:
                res = await t
                results.append(res)
            except Exception as e:
                logger.error(f"Task failed: {e}")
                results.append(e)
        return results

    @staticmethod
    async def async_map(fn: Callable[..., Coroutine], iterable, concurrency: int = 5):
        """
        Coroutine fonksiyonunu iterable üzerinde paralel çalıştırır, concurrency limiti vardır.
        """
        semaphore = asyncio.Semaphore(concurrency)
        results = []

        async def worker(item):
            async with semaphore:
                return await fn(item)

        tasks = [asyncio.create_task(worker(i)) for i in iterable]
        for t in asyncio.as_completed(tasks):
            try:
                res = await t
                results.append(res)
            except Exception as e:
                logger.error(f"async_map task error: {e}")
                results.append(e)
        return results

    @staticmethod
    async def sleep_random(min_sec: float = 0.1, max_sec: float = 1.0):
        """
        Rastgele gecikme ekler. Test ve simülasyon için kullanılır.
        """
        delay = random.uniform(min_sec, max_sec)
        await asyncio.sleep(delay)
        return delay


# ==========================
# ÖRNEK KULLANIM
# ==========================
if __name__ == "__main__":
    import time

    async def test_coro(x):
        await AsyncHelper.sleep_random(0.1, 0.5)
        return x * 2

    async def main():
        results = await AsyncHelper.async_map(test_coro, range(10), concurrency=3)
        print("Sonuçlar:", results)

    start = time.time()
    import asyncio
    asyncio.run(main())
    print("Toplam süre:", round(time.time() - start, 2), "saniye")
