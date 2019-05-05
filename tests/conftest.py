from itertools import count
from typing import Iterable

import pytest
from aiohttp import web
from asynctest import create_autospec

from scrapping_asyncio.infrastructure.queuee import Queue
from scrapping_asyncio.infrastructure.service import AsyncioScrappingApi
from scrapping_asyncio.entities.task import Task, Status
from scrapping_asyncio.data.mongo_tasks_repository import TaskNotFound


@pytest.fixture(autouse=True)
def mocked_uuid(mocker):
    mocker.patch('uuid.uuid4', side_effect=count(start=1))


@pytest.fixture()
def tasks_repo():
    class TaskRepository:
        id_counter = 0

        def __init__(self):
            self.tasks = dict()

        async def add(self, url: str) -> Task:
            self.id_counter += 1
            task = Task(id=str(self.id_counter), url=url, status=Status.WAITING)
            self.tasks[task.id] = task
            return task

        async def get(self, id: str) -> Task:
            task = self.tasks.get(id, None)
            if task:
                return task
            raise TaskNotFound()

        async def all(self) -> Iterable[Task]:
            return self.tasks.values()

        async def update(self, task: Task):
            self.tasks[task.id] = task

    return TaskRepository()


@pytest.fixture
def queue(loop):
    return create_autospec(Queue)


@pytest.fixture()
def scrapping_service(queue, tasks_repo):
    return AsyncioScrappingApi(queue=queue, tasks_repo=tasks_repo)


@pytest.fixture
def task():
    return Task('id123', 'http://www.wp.pl', Status.IN_PROGRESS)


@pytest.fixture
def api_service(loop, aiohttp_client, scrapping_service):
    app = web.Application()
    app.add_routes([
        web.post('/tasks', scrapping_service.add_task),
        web.get('/tasks', scrapping_service.get_tasks),
        web.get('/tasks/{task_id}', scrapping_service.get_task)
    ])
    return loop.run_until_complete(aiohttp_client(app))


@pytest.fixture
def expected_task():
    return Task(id='1', url='www.abc.pl', status=Status.WAITING)
