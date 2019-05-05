import logging

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from scrapping_asyncio.infrastructure.queuee import Queue
from scrapping_asyncio.data.mongo_tasks_repository import TaskRepository, TaskNotFound
from scrapping_asyncio.data.serialization import task_to_json
from scrapping_asyncio.use_cases.service import ScrappingServiceUSECASE

logger = logging.getLogger(__name__)


class AsyncioScrappingApi:
    def __init__(self, queue, tasks_repo):
        self.service = ScrappingServiceUSECASE(tasks_repo=tasks_repo)
        self.queue = queue

    async def get_tasks(self, _: Request) -> Response:
        return web.json_response([task_to_json(t) for t in await self.service.get_tasks()])

    async def add_task(self, request: Request) -> Response:
        data = await request.json()
        task = await self.service.add_task(url=data['url'])
        await self.queue.put(task_to_json(task))
        return web.json_response(headers={'location': 'http://localhost:8080/tasks/' + task.id}, status=201)  #Todo url for

    async def get_task(self, request: Request) -> Response:
        task_id = request.match_info.get('task_id')
        try:
            task = await self.service.get_task(task_id)
            return web.json_response(task_to_json(task))
        except TaskNotFound:
            raise web.HTTPNotFound()


async def create_app():
    tasks_repo = TaskRepository()
    queue = await Queue.create()
    service = AsyncioScrappingApi(queue, tasks_repo)

    app = web.Application()
    app.add_routes([
        web.post('/tasks', service.add_task),
        web.get('/tasks', service.get_tasks),
        web.get('/tasks/{task_id}', service.get_task)
    ])
    return app


def main():
    web.run_app(create_app())


if __name__ == '__main__':
    main()
