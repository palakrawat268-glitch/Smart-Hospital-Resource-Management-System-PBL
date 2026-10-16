# modules/module5_kanishk_bankers/os_core/synchronization.py
# Author: Kanishk Ramola
# OS Concept: Mutex Locks & Concurrency Control

import threading
from contextlib import contextmanager

class ResourceSynchronization:
    def __init__(self, initial_slots: int = 1):
        self.mutexLock = threading.Lock()
        self.resourceSemaphore = threading.Semaphore(initial_slots)
        self.accessFlag = False

    @contextmanager
    def criticalSection(self):
        self.mutexLock.acquire()
        self.accessFlag = True
        try:
            yield
        finally:
            self.accessFlag = False
            self.mutexLock.release()

equipment_sync = ResourceSynchronization()
