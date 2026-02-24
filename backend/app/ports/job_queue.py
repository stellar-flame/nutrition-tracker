# app/queue/base.py
from typing import Protocol

class JobQueue(Protocol):
    async def enqueue(self, prompt: dict) -> None: ...
