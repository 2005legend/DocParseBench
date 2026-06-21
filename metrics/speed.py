import time

class SpeedMonitor:
    def __init__(self):
        self.start_time = 0
        self.end_time = 0
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time.time()
        
    def duration(self):
        return self.end_time - self.start_time
