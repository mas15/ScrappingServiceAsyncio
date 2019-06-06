import logging

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from scrapping_asyncio.data.ondisk_tasks_storage import OnDiskTaskDataStorage
from scrapping_asyncio.infrastructure.queuee import Queue
from scrapping_asyncio.data.mongo_tasks_repository import TaskRepository, TaskNotFound
from scrapping_asyncio.data.serialization import task_to_json, task_to_api_json
from scrapping_asyncio.use_cases.service import ScrappingServiceUsecase

logger = logging.getLogger(__name__)


class AsyncioScrappingApi:
    def __init__(self, queue, scrapping_service: ScrappingServiceUsecase):
        self.service = scrapping_service
        self.queue = queue

    async def get_tasks(self, _: Request) -> Response:
        return web.json_response([task_to_api_json(t) for t in await self.service.get_tasks()])

    async def add_task(self, request: Request) -> Response:
        data = await request.json()
        task = await self.service.add_task(url=data['url'])
        await self.queue.put(task_to_json(task))
        return web.json_response(headers={'location': 'http://localhost:8080/tasks/' + task.id}, status=201)  #Todo url for

    async def get_task(self, request: Request) -> Response:
        task_id = request.match_info.get('task_id')
        try:
            task = await self.service._get_task(task_id)  # TODO store images and data
            return web.json_response(task_to_api_json(task))
        except TaskNotFound:
            raise web.HTTPNotFound()

    async def get_task_text(self, request: Request) -> Response:
        task_id = request.match_info.get('task_id')
        try:
            data = self.service.get_task_text(task_id)
            return web.json_response(data) # TODO normalne a nie json?
        except TaskNotFound:
            raise web.HTTPNotFound()

    async def get_task_image(self, request: Request) -> Response:
        task_id = request.match_info.get('task_id')
        filename = request.match_info.get('image_name')
        try:
            data = self.service.get_task_image(task_id, filename)
            return web.json_response(data) # TODO serve image
        except TaskNotFound:
            raise web.HTTPNotFound()


async def create_app():
    tasks_repo = TaskRepository()
    queue = await Queue.create()
    task_data_storage = OnDiskTaskDataStorage()
    scrapping_service = ScrappingServiceUsecase(tasks_repo, task_data_storage)
    service = AsyncioScrappingApi(queue, scrapping_service)

    app = web.Application()
    app.add_routes([
        web.post('/tasks', service.add_task),
        web.get('/tasks', service.get_tasks),
        web.get('/tasks/{task_id}', service.get_task),
        web.get('/tasks/{task_id}/text', service.get_task_text),
        web.get('/tasks/{task_id}/images/{image_name}', service.get_task_image)
    ])
    return app


def main():
    web.run_app(create_app())


if __name__ == '__main__':
    main()
