import psutil
import time
import threading

class Profiler:
    """Tracks memory and CPU usage of a specific process."""

    def __init__(self, pid: int, interval: float = 0.1):
        self.pid = pid
        self.interval = interval
        self.is_running = False
        self.thread = None
        self.max_rss = 0
        self.cpu_samples = []

    def _monitor(self):
        try:
            process = psutil.Process(self.pid)
            while self.is_running:
                # Memory (RSS)
                try:
                    mem_info = process.memory_info()
                    rss = mem_info.rss
                    if rss > self.max_rss:
                        self.max_rss = rss
                    
                    # CPU
                    cpu_percent = process.cpu_percent(interval=None)
                    self.cpu_samples.append(cpu_percent)
                except psutil.NoSuchProcess:
                    break
                
                time.sleep(self.interval)
        except psutil.NoSuchProcess:
            pass

    def start(self):
        self.is_running = True
        self.thread = threading.Thread(target=self._monitor)
        self.thread.start()

    def stop(self) -> dict:
        self.is_running = False
        if self.thread:
            self.thread.join()
            
        avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0.0
        
        return {
            "peak_ram_mb": self.max_rss / (1024 * 1024),
            "avg_cpu_percent": avg_cpu
        }
