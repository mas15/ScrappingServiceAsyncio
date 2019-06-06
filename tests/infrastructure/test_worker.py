import pytest
from asynctest import CoroutineMock

from scrapping_asyncio.data.serialization import task_to_json
from scrapping_asyncio.entities.task import Status
from scrapping_asyncio.infrastructure.worker import AsyncioScrappingWorker


@pytest.fixture
def worker(queue, scrapping_service, monkeypatch):
    monkeypatch.setattr('scrapping_asyncio.use_cases.service.scrape', CoroutineMock())
    yield AsyncioScrappingWorker(queue=queue, service=scrapping_service)


@pytest.fixture
def worker_failing_on_scrape(queue, scrapping_service, monkeypatch):
    monkeypatch.setattr('scrapping_asyncio.use_cases.service.scrape', lambda: Exception('Failed'))
    yield AsyncioScrappingWorker(queue=queue, service=scrapping_service)


@pytest.mark.asyncio
async def test_get_task(worker, expected_task, tasks_repo, queue):
    task = await tasks_repo.add('www.abc.pl')
    await queue.put(task_to_json(task))

    await worker.run()

    updated_task = await tasks_repo.get(task.id)
    assert updated_task.status == Status.DONE


@pytest.mark.asyncio
async def test_get_task_failing(worker_failing_on_scrape, expected_task, tasks_repo, queue):
    task = await tasks_repo.add('www.abc.pl')
    await queue.put(task_to_json(task))

    await worker_failing_on_scrape.run()

    updated_task = await tasks_repo.get(task.id)
    assert updated_task.status == Status.FAILED

# TODO how to test run?
