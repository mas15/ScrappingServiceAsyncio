import pytest

from scrapping_asyncio.data.serialization import task_from_json, task_to_json


@pytest.mark.asyncio
def test_serialization(task):
    as_json = task_to_json(task)
    assert task_from_json(as_json) == task


@pytest.mark.asyncio
def test_api_serialization(task):
    as_json = task_to_json(task)
    assert as_json == {
        'id': 'id123',
        'url': 'http://www.wp.pl',
        'status': 'IN_PROGRESS',
        'images_paths': ['img123.png'],
        'text_path': 'aaa.txt'
    }
