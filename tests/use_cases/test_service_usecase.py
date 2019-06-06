import pytest

from scrapping_asyncio.entities.task import Status


@pytest.fixture
async def task_in_repo(task, tasks_repo):
    tasks_repo.tasks[task.id] = task
    return task


@pytest.mark.asyncio
async def test_get_tasks(scrapping_service, task_in_repo):
    tasks = await scrapping_service.get_tasks
    assert tasks == [task_in_repo]


@pytest.mark.asyncio
async def test_get_task(scrapping_service, task_in_repo):
    assert await scrapping_service._get_task(task_in_repo.id) == task_in_repo


@pytest.mark.asyncio
async def test_get_task_text(scrapping_service, task_in_repo):
    assert await scrapping_service.get_task_text(task_in_repo.id) == 'some_text'


@pytest.mark.asyncio
async def test_get_task_image(scrapping_service, task_in_repo):
    assert await scrapping_service.get_task_image(task_in_repo.id, 'img123.png') == b'img_content'


@pytest.mark.asyncio
async def test_add_task(scrapping_service):
    task = await scrapping_service.add_task('www.google.pl')
    assert task.status == Status.WAITING
    assert task.url == 'www.google.pl'
    tasks = await scrapping_service.get_tasks()
    assert len(tasks) == 1
    assert tasks[0] == task


@pytest.mark.asyncio
async def test_process(scrapping_service):
    # TODO mock scrape
    pass
