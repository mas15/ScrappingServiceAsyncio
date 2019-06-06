from abc import ABC, abstractmethod

from scrapping_asyncio.entities.task import Task


class TaskDataStorage(ABC):
    @abstractmethod
    async def save_text(self, task: Task, text: str) -> str:
        pass

    @abstractmethod
    async def save_image(self, task: Task, content: bytes, filename: str) -> str:
        pass

    @abstractmethod
    async def get_image(self, task: Task, filename: str) -> bytes:
        pass

    @abstractmethod
    async def get_text(self, task: Task) -> str:
        pass
