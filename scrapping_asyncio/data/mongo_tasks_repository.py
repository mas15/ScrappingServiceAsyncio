from typing import List

from motor import motor_asyncio

from scrapping_asyncio.entities.task import Task
from scrapping_asyncio.data.serialization import task_from_json, task_to_json


class TaskNotFound(Exception):
    pass


class TaskRepository:
    def __init__(self):
        self._client = motor_asyncio.AsyncIOMotorClient('mongodb://mongodb', 27017)
        self._db = self._client['db']
        self.tasks = self._db.tasks

    async def add(self, task: Task):
        as_json = task_to_json(task)
        as_json['_id'] = as_json.pop('id')
        insert_result = await self.tasks.insert_one(as_json)
        assert insert_result.inserted_id == task.id

    async def get(self, _id: str) -> Task:
        as_json = await self.tasks.find_one({'_id': _id})
        if as_json:
            as_json['id'] = as_json.pop('_id')
            return task_from_json(as_json)
        raise TaskNotFound()

    async def all(self) -> List[Task]:
        cursor = self.tasks.find()
        return [task_from_json(t) for t in await cursor.to_list(length=None)]

    async def update(self, task: Task):
        as_json = task_to_json(task)
        _id = as_json.pop('id')
        await self.tasks.replace_one({'_id': _id}, as_json)
