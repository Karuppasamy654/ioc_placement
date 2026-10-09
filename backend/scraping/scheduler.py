import time
import threading
from typing import Dict, Any, Optional, List
from backend.scraping.source_registry import SourceRegistry
from backend.scraping.ingestion_service import IngestionService

class ScrapingScheduler:
    """
    Background scheduler for scheduled data ingestion jobs with
    overlapping run locks per source and graceful shutdown.
    """
    _instance = None
    _active_locks: Dict[int, threading.Lock] = {}
    _running_sources: Dict[int, bool] = {}
    _thread: Optional[threading.Thread] = None
    _stop_event = threading.Event()

    def __init__(self, check_interval_seconds: int = 30):
        self.check_interval_seconds = check_interval_seconds

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ScrapingScheduler()
        return cls._instance

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="ScrapingSchedulerThread")
        self._thread.start()
        print("[SCRAPING SCHEDULER] Background ingestion scheduler thread started.")

    def stop(self):
        self._stop_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=5.0)
            print("[SCRAPING SCHEDULER] Scheduler thread stopped gracefully.")

    def _run_loop(self):
        while not self._stop_event.is_set():
            try:
                enabled_sources = SourceRegistry.list_sources(enabled_only=True)
                now = time.time()

                for source in enabled_sources:
                    if self._stop_event.is_set():
                        break

                    source_id = source["id"]
                    crawl_interval_sec = source["crawl_interval_minutes"] * 60

                    # Check last run timestamp
                    last_run_str = source.get("last_successful_run")
                    should_run = False

                    if not last_run_str:
                        should_run = True
                    else:
                        try:
                            from datetime import datetime, timezone
                            dt = datetime.strptime(last_run_str, "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=timezone.utc)
                            if (now - dt.timestamp()) >= crawl_interval_sec:
                                should_run = True
                        except Exception:
                            should_run = True

                    if should_run:
                        self.trigger_source_run_async(source_id)

            except Exception as e:
                print(f"[SCRAPING SCHEDULER ERROR] Loop error: {e}")

            self._stop_event.wait(self.check_interval_seconds)

    def trigger_source_run_async(self, source_id: int):
        if source_id not in self._active_locks:
            self._active_locks[source_id] = threading.Lock()

        lock = self._active_locks[source_id]
        if not lock.acquire(blocking=False):
            # Already running, prevent overlapping execution
            print(f"[SCRAPING SCHEDULER] Skip source ID {source_id}: run already in progress.")
            return False

        def worker():
            try:
                self._running_sources[source_id] = True
                print(f"[SCRAPING SCHEDULER] Executing ingestion run for source ID {source_id}...")
                result = IngestionService.run_source_ingestion(source_id)
                print(f"[SCRAPING SCHEDULER] Completed run for source ID {source_id}: {result['inserted']} inserted, {result['updated']} updated, {result['failures']} failures.")
            except Exception as e:
                print(f"[SCRAPING SCHEDULER ERROR] Ingestion error for source ID {source_id}: {e}")
            finally:
                self._running_sources[source_id] = False
                lock.release()

        t = threading.Thread(target=worker, daemon=True, name=f"ScraperWorker-{source_id}")
        t.start()
        return True
