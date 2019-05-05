import pytest
from asynctest import CoroutineMock

from scrapping_asyncio.entities.task import Status
from scrapping_asyncio.infrastructure.worker import AsyncioScrappingWorker


@pytest.fixture
def worker(queue, tasks_repo, monkeypatch):
    monkeypatch.setattr('scrapping_asyncio.worker.scrape', CoroutineMock())
    yield AsyncioScrappingWorker(queue=queue, tasks_repo=tasks_repo)


@pytest.fixture
def worker_failing_on_scrape(queue, tasks_repo, monkeypatch):
    monkeypatch.setattr('scrapping_asyncio.worker.scrape', lambda: Exception('Failed'))
    yield AsyncioScrappingWorker(queue=queue, tasks_repo=tasks_repo)


@pytest.mark.asyncio
async def test_get_task(worker, expected_task, tasks_repo, queue):
    task = await tasks_repo.add('www.abc.pl')
    await queue.put(task.asdict())

    await worker.process(task)

    updated_task = await tasks_repo.get(task.id)
    assert updated_task.status == Status.DONE


@pytest.mark.asyncio
async def test_get_task_failing(worker_failing_on_scrape, expected_task, tasks_repo, queue):
    task = await tasks_repo.add('www.abc.pl')
    await queue.put(task.asdict())

    await worker_failing_on_scrape.process(task)

    updated_task = await tasks_repo.get(task.id)
    assert updated_task.status == Status.FAILED

# TODO how to test run?
