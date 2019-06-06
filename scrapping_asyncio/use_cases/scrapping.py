import mimetypes
from typing import Iterable, Tuple, List
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup
from bs4.element import Comment

from scrapping_asyncio.entities.task import Task
from scrapping_asyncio.entities.tasks_data_storage import TaskDataStorage


async def scrape(task: Task, storage: TaskDataStorage) -> Tuple[str, List[str]]:
    content, _ = await download_content(task.url)
    soup = BeautifulSoup(content, 'html.parser')

    text = scrape_text(soup)
    text_filename = await storage.save_text(task, text)

    images_filenames = []
    imgs_urls = get_images_urls(soup, task.url)
    for img_url in imgs_urls:
        image_content, image_name = await download_content(img_url)
        image_filename = await storage.save_image(task, image_content, image_name)
        images_filenames.append(image_filename)

    return text_filename, images_filenames


async def download_content(url: str) -> Tuple[bytes, str]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                extension = mimetypes.guess_extension(response.content_type) or ''
                content = await response.read()
                return content, 'file_name' + extension


def _is_tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def scrape_text(soup) -> str:
    texts = soup.findAll(text=True)
    visible_texts = filter(_is_tag_visible, texts)
    result = "\n".join(t.strip() for t in visible_texts)
    return result


def get_images_urls(soup, base_url) -> Iterable[str]:
    def _fix_relative_url(img_url):
        return urljoin(base_url, img_url) if 'http' not in img_url else img_url

    img_tags = soup.find_all('img')
    img_urls = (img['src'] for img in img_tags)
    img_urls = (_fix_relative_url(url) for url in img_urls)
    yield from img_urls
