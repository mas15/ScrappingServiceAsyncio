import json
from typing import Dict

import aio_pika

MAX_TASKS_AT_ONCE = 10


class Queue:
    def __init__(self, queue, channel):
        self.queue = queue
        self.channel = channel

    @classmethod
    async def create(cls):
        connection = await aio_pika.connect_robust(
            'amqp://guest:guest@rabbitmq/'  # TODO loop=loop
        )
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=MAX_TASKS_AT_ONCE)
        queue = await channel.declare_queue('queue_name_here', auto_delete=True)
        return cls(queue, channel)

    async def get(self) -> Dict:
        # async with self.queue.iterator() as queue_iter:
        #     async for message in queue_iter:
        #         async with message.process():
        #             body_as_str = await message.body.decode()
        #             yield json.loads(body_as_str)

        async with self.queue.iterator() as q:  # todo iterator mozna usunac
            async for message in q:
                body_as_str = message.body.decode()
                yield json.loads(body_as_str)
                # task done?
        self.queue.consume()

    async def put(self, body_as_json: Dict):
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(body_as_json).encode(),
                content_type='text/json'
            ),
            routing_key='queue_name_here'
        )
