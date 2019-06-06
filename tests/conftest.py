from itertools import count
from typing import Iterable, List

import pytest
from aiohttp import web
from asynctest import create_autospec

from scrapping_asyncio.entities.tasks_data_storage import TaskDataStorage
from scrapping_asyncio.entities.tasks_repository import TasksRepository
from scrapping_asyncio.infrastructure.queuee import Queue
from scrapping_asyncio.infrastructure.service import AsyncioScrappingApi
from scrapping_asyncio.entities.task import Task, Status
from scrapping_asyncio.data.mongo_tasks_repository import TaskNotFound
from scrapping_asyncio.use_cases.service import ScrappingServiceUsecase


@pytest.fixture(autouse=True)
def mocked_uuid(mocker):
    mocker.patch('uuid.uuid4', side_effect=count(start=1))


@pytest.fixture()
def tasks_data_storage():
    class Storage(TaskDataStorage):
        def __init__(self):
            self.images = dict()
            self.texts = dict()

        async def save_text(self, task: Task, text: str) -> str:
            self.texts[task.id] = text
            return 'aaa.txt'

        async def save_image(self, task: Task, content: bytes, filename: str) -> str:
            self.images[(task.id, filename)] = content
            return filename

        async def get_image(self, task: Task, filename: str) -> bytes:
            return self.images[(task.id, filename)]

        async def get_text(self, task: Task) -> str:
            return self.texts[task.id]  # TODO raise if not exists

    return Storage()


@pytest.fixture()
def tasks_repo():
    class TaskRepository(TasksRepository):
        id_counter = 0

        def __init__(self):
            self.tasks = dict()

        async def add(self, url: str) -> Task:
            self.id_counter += 1
            task = Task(id=str(self.id_counter), url=url, status=Status.WAITING)
            self.tasks[task.id] = task
            return task

        async def get(self, _id: str) -> Task:
            task = self.tasks.get(id, None)
            if task:
                return task
            raise TaskNotFound(f'There is no task with id {_id}')

        async def all(self) -> List[Task]:
            return list(self.tasks.values())

        async def update(self, task: Task):
            self.tasks[task.id] = task

    return TaskRepository()


@pytest.fixture
def queue(loop):
    return create_autospec(Queue)


@pytest.fixture()
def scrapping_service(queue, tasks_repo, tasks_data_storage):
    return ScrappingServiceUsecase(tasks_repo=tasks_repo, task_data_storage=tasks_data_storage)


@pytest.fixture()
def scrapping_api_service(queue, scrapping_service):
    return AsyncioScrappingApi(queue=queue, scrapping_service=scrapping_service)


@pytest.fixture()
async def task(loop, tasks_data_storage):
    task = Task('id123', 'http://www.wp.pl', Status.IN_PROGRESS)
    task.images_paths = [await tasks_data_storage.save_image(task, b'img_content', 'img123.png')]
    task.text_path = await tasks_data_storage.save_text(task, 'some_text')
    return task


@pytest.fixture
def api_service(loop, aiohttp_client, scrapping_api_service):
    app = web.Application()
    app.add_routes([
        web.post('/tasks', scrapping_api_service.add_task),
        web.get('/tasks', scrapping_api_service.get_tasks),
        web.get('/tasks/{task_id}', scrapping_api_service.get_task)
    ])
    return loop.run_until_complete(aiohttp_client(app))


@pytest.fixture
def expected_task():
    return Task(id='1', url='www.abc.pl', status=Status.WAITING)
