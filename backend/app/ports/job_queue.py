# app/queue/base.py
from typing import Protocol

class JobQueue(Protocol):
    def enqueue(self, prompt: dict) -> None: ...
