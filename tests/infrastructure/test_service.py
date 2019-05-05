import json

import pytest

from scrapping_asyncio.data.serialization import task_to_json


@pytest.mark.asyncio
async def test_get_task(api_service, loop, expected_task, tasks_repo):
    await tasks_repo.add('www.abc.pl')
    resp = await api_service.get('/tasks/1')
    assert resp.status == 200
    text = json.loads(await resp.text())
    assert text == task_to_json(expected_task)


@pytest.mark.asyncio
async def test_get_tasks(api_service, loop):
    resp = await api_service.get('/tasks')
    assert resp.status == 200
    text = json.loads(await resp.text())
    assert text == []


@pytest.mark.asyncio
async def test_add_task(api_service, expected_task):
    resp = await api_service.post('/tasks', data=json.dumps({'url': 'www.abc.pl'}))
    assert resp.status == 200
    text = json.loads(await resp.text())
    assert text == task_to_json(expected_task)


@pytest.mark.asyncio
async def test_get_task_raises_when_not_found(api_service):
    resp = await api_service.get('/tasks/1234')
    assert resp.status == 404
    text = await resp.text()
    assert '404' in text


@pytest.mark.asyncio
async def test_integration(api_service, expected_task):
    resp = await api_service.post('/tasks', data=json.dumps({'url': 'www.abc.pl'}))
    assert resp.status == 200

    resp = await api_service.get('/tasks')
    assert resp.status == 200
    text = json.loads(await resp.text())
    assert text == [task_to_json(expected_task)]

    resp = await api_service.get('/tasks/1')
    assert resp.status == 200
    text = json.loads(await resp.text())
    assert text == task_to_json(expected_task)


@pytest.mark.asyncio
async def test_two_tasks(api_service):
    await api_service.post('/tasks', data=json.dumps({'url': 'www.abc.pl'}))
    resp = await api_service.post('/tasks', data=json.dumps({'url': 'www.xd.pl'}))
    assert resp.status == 200

    resp = await api_service.get('/tasks')
    assert resp.status == 200
    text = json.loads(await resp.text())
    assert len(text) == 2

    resp = await api_service.get('/tasks/2')
    assert resp.status == 200
    text = json.loads(await resp.text())
    assert text == {'id': '2', 'url': 'www.xd.pl', 'status': 'WAITING'}
