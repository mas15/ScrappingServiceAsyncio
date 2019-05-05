import mimetypes
import os
from typing import Iterable, Tuple
from urllib.parse import urljoin

import aiofiles
import aiohttp
from bs4 import BeautifulSoup
from bs4.element import Comment


async def scrape(url: str, text_file_path: str, images_dir_path: str):
    content, _ = await download_content(url)
    soup = BeautifulSoup(content, 'html.parser')

    text = scrape_text(soup)
    await save_text(text, text_file_path)

    imgs_urls = get_images_urls(soup, url)
    for img_url in imgs_urls:
        image, image_name = await download_content(img_url)
        await save_image(image, image_name, images_dir_path)


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


async def save_text(text, text_file_path):
    async with aiofiles.open(text_file_path, 'w') as f:
        await f.write(text)


async def save_image(content: bytes, filename: str, dir_path: str):
    os.makedirs(dir_path, exist_ok=True)
    async with aiofiles.open(os.path.join(dir_path, filename), 'wb') as f:
        await f.write(content)


def get_images_urls(soup, base_url) -> Iterable[str]:
    def _fix_relative_url(img_url):
        return urljoin(base_url, img_url) if 'http' not in img_url else img_url

    img_tags = soup.find_all('img')
    img_urls = (img['src'] for img in img_tags)
    img_urls = (_fix_relative_url(url) for url in img_urls)
    yield from img_urls
