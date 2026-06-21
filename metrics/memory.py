import os
import psutil
import threading
import time

class PeakMemoryMonitor:
    def __init__(self):
        self.keep_measuring = True
        self.peak_memory = 0
        self.thread = None
        
    def _measure(self):
        process = psutil.Process(os.getpid())
        while self.keep_measuring:
            mem = process.memory_info().rss / (1024 * 1024) # MB
            if mem > self.peak_memory:
                self.peak_memory = mem
            time.sleep(0.05)
            
    def __enter__(self):
        self.keep_measuring = True
        self.peak_memory = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
        self.thread = threading.Thread(target=self._measure)
        self.thread.start()
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.keep_measuring = False
        if self.thread:
            self.thread.join()
            
    def get_peak_mb(self):
        return self.peak_memory
