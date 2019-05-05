from typing import Dict

from scrapping_asyncio.entities.task import Task, Status


def task_from_json(as_json: Dict) -> Task:
    return Task(id=as_json['id'], url=as_json['url'], status=Status(as_json['status']))


def task_to_json(task: Task) -> Dict:
    return {'id': task.id, 'url': task.url, 'status': task.status.value}
