import uuid
from typing import List

from scrapping_asyncio.entities.task import Task, Status
from scrapping_asyncio.use_cases.scrapping import scrape
import logging

logger = logging.getLogger(__name__)


class ScrappingServiceUSECASE:
    def __init__(self, tasks_repo):
        self.tasks_repo = tasks_repo

    async def get_tasks(self) -> List[Task]:
        return await self.tasks_repo.all()

    async def add_task(self, url: str) -> Task:
        task = Task(id=str(uuid.uuid4()), url=url, status=Status.WAITING)  # Todo id
        await self.tasks_repo.add(task)
        return task

    async def get_task(self, _id: str) -> Task:
        return await self.tasks_repo.get(_id)

    async def process(self, task):
        logger.debug(f'Started processing {task.id} task (url: {task.url})')
        task.status = Status.IN_PROGRESS
        await self.tasks_repo.update(task)
        try:
            await scrape(
                url=task.url,
                text_file_path=task.text_location,
                images_dir_path=task.images_location
            )
            task.status = Status.DONE
            logger.debug(f'Task {task.id} (url: {task.url}) done')
        except Exception:
            logger.exception(f'Task {task.id} (url: {task.url}) failed')
            task.status = Status.FAILED
        await self.tasks_repo.update(task)
