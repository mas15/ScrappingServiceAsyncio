from abc import ABC, abstractmethod
from typing import List

from scrapping_asyncio.entities.task import Task


class TasksRepository(ABC):

    @abstractmethod
    async def add(self, task: Task):
        pass

    @abstractmethod
    async def get(self, _id: str) -> Task:
        pass

    @abstractmethod
    async def all(self) -> List[Task]:
        pass

    @abstractmethod
    async def update(self, task: Task):
        pass
