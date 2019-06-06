import glob
import os

import aiofiles

from scrapping_asyncio.entities.task import Status, Task
from scrapping_asyncio.entities.tasks_data_storage import TaskDataStorage

DOWNLOADS_DIR = 'downloads'


class TaskNotDoneException(Exception):  # TODO move out
    pass


class OnDiskTaskDataStorage(TaskDataStorage):

    async def save_text(self, task: Task, text: str) -> str:
        file_path = self.text_location(task)
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(text)
        return file_path

    async def save_image(self, task: Task, content: bytes, filename: str) -> str:
        dir_path = self.images_location(task)
        file_path = os.path.join(dir_path, filename)
        os.makedirs(dir_path, exist_ok=True)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        return file_path

    # TODO raise if none

    async def get_image(self, task: Task, filename: str) -> bytes:
        self._check_if_task_done(task)  # TODO czy to dekorator
        async with aiofiles.open(self.image_location(task, filename)) as f:
            yield await f.read()

    async def get_text(self, task: Task) -> str:
        self._check_if_task_done(task)
        async with aiofiles.open(self.text_location(task)) as f:
            return await f.read()

    @staticmethod
    def _check_if_task_done(task: Task):
        if task.status is not Status.DONE:
            raise TaskNotDoneException()

    @staticmethod
    def images_location(task: Task):
        return os.path.join(DOWNLOADS_DIR, task.id)

    @staticmethod
    def image_location(task: Task, filename: str):
        return os.path.join(OnDiskTaskDataStorage.images_location(task), filename)

    @staticmethod
    def text_location(task: Task):
        return os.path.join(DOWNLOADS_DIR, task.id + '.txt')
