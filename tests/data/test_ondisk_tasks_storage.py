import pytest

from scrapping_asyncio.data.ondisk_tasks_storage import OnDiskTaskDataStorage


@pytest.fixture
def on_disk_task_storage():
    return OnDiskTaskDataStorage()


@pytest.mark.asyncio
async def test_images_locations(task, on_disk_task_storage):
    assert on_disk_task_storage.images_location(task) == 'downloads/id123'


@pytest.mark.asyncio
async def test_image_locations(task, on_disk_task_storage):
    assert on_disk_task_storage.image_location(task, 'img1') == 'downloads/id123/img1'


@pytest.mark.asyncio
async def test_text_locations(task, on_disk_task_storage):
    assert on_disk_task_storage.text_location(task) == 'downloads/id123.txt'
