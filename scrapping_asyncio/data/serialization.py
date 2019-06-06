import attr
from typing import Dict

from scrapping_asyncio.entities.task import Task


def task_from_json(as_json: Dict) -> Task:
    return Task(**as_json)


def task_to_json(task: Task) -> Dict:
    result = attr.asdict(task)
    result['status'] = task.status.value
    return result


def task_to_api_json(task: Task) -> Dict:
    # TODO
    text = 'http://localhost:8080/tasks/' + task.id + '/text/' + task.text_path if task.text_path else None
    images = []
    if task.images_paths:
        images = ['http://localhost:8080/tasks/' + task.id + '/images/' + img_name for img_name in task.images_paths]
    return {
        'id': task.id,
        'url': task.url,
        'status': task.status.value,
        'text': text,
        'images': images,
    }
