# Intervall mit Drift-Korrektur
# Quelle: https://stackoverflow.com/a/48709380

from time import time
import threading

class SetInterval:
    def __init__(self, interval, callback):
        self.interval = interval
        self.callback = callback
        self.event = threading.Event()
        
        thread = threading.Thread(target = self.run)
        thread.start()
    
    def run(self):
        nextTime = time() + self.interval
        while not self.event.wait(nextTime - time()):
            nextTime += self.interval
            self.callback()
    
    def cancel(self):
        self.event.set()
