import pytest

from scrapping_asyncio.entities.task import TaskNotDoneException
from scrapping_asyncio.data.serialization import task_from_json, task_to_json


def test_serialization(task):
    as_json = task_to_json(task)
    assert task_from_json(as_json) == task


def test_cant_get_data_when_not_done(task):
    with pytest.raises(TaskNotDoneException):
        task.images()
    with pytest.raises(TaskNotDoneException):
        task.text()


def test_images_locations(task):
    assert task.images_location == 'downloads/id123'


def test_text_locations(task):
    assert task.text_location == 'downloads/id123.txt'
