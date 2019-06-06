import asyncio
import logging

from scrapping_asyncio.data.ondisk_tasks_storage import OnDiskTaskDataStorage
from scrapping_asyncio.infrastructure.queuee import Queue
from scrapping_asyncio.data.mongo_tasks_repository import TaskRepository
from scrapping_asyncio.data.serialization import task_from_json
from scrapping_asyncio.use_cases.service import ScrappingServiceUsecase

logger = logging.getLogger(__name__)


class AsyncioScrappingWorker:
    def __init__(self, queue, service: ScrappingServiceUsecase):
        self.service = service
        self.queue = queue

    async def run(self):
        async for task_as_json in self.queue.get():
            task = task_from_json(task_as_json)
            await self.service.process(task)


async def run():
    tasks_repo = TaskRepository()
    queue = await Queue.create()
    task_data_storage = OnDiskTaskDataStorage()
    service = ScrappingServiceUsecase(tasks_repo, task_data_storage)
    worker = AsyncioScrappingWorker(queue, service)
    await worker.run()


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()


if __name__ == "__main__":
    main()
