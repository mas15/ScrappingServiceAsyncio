import uuid
from typing import List

from scrapping_asyncio.entities.task import Task, Status
from scrapping_asyncio.entities.tasks_data_storage import TaskDataStorage
from scrapping_asyncio.entities.tasks_repository import TasksRepository
from scrapping_asyncio.use_cases.scrapping import scrape
import logging

logger = logging.getLogger(__name__)


class ScrappingServiceUsecase:
    def __init__(self, tasks_repo: TasksRepository, task_data_storage: TaskDataStorage):
        self.tasks_repo = tasks_repo
        self.task_data_storage = task_data_storage

    async def get_tasks(self) -> List[Task]:  # TODO iterable
        return await self.tasks_repo.all()

    async def get_task_text(self, task_id: str) -> str:
        task = await self._get_task(task_id)
        return await self.task_data_storage.get_text(task)

    async def get_task_image(self, task_id: str, image_path: str) -> bytes:
        task = await self._get_task(task_id)
        return await self.task_data_storage.get_image(task, image_path)

    async def add_task(self, url: str) -> Task:
        task = Task(id=str(uuid.uuid4()), url=url, status=Status.WAITING)  # Todo id
        await self.tasks_repo.add(task)
        return task

    async def _get_task(self, _id: str) -> Task:
        return await self.tasks_repo.get(_id)

    async def process(self, task):
        logger.debug(f'Started processing {task.id} task (url: {task.url})')
        task.status = Status.IN_PROGRESS
        await self.tasks_repo.update(task)
        try:
            text_filename, images_filenames = await scrape(task=task, storage=self.task_data_storage)
            task.text_path = text_filename
            task.images_paths = images_filenames
            task.status = Status.DONE
            logger.debug(f'Task {task.id} (url: {task.url}) done')
        except Exception:
            logger.exception(f'Task {task.id} (url: {task.url}) failed')
            task.status = Status.FAILED
        await self.tasks_repo.update(task)
