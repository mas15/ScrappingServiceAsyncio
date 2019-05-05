from setuptools import setup, find_packages

setup(
    name="scrapping_asyncio",
    entry_points={
        'console_scripts': [
            'api=scrapping_asyncio.infrastructure.service:main',
            'worker=scrapping_asyncio.infrastructure.worker:main'
        ],
    },
    install_requires=[
        'aiofiles==0.4.0',
        'aio-pika>=5.5.1,<6.0',
        'attrs>=19.1.0,<20.0.0',
        'aiohttp>=3.5.4,<3.6.0',
        'asynctest==0.12.3',
        'beautifulsoup4>=4.6.3,<5.0',
        'motor>=2.0.0,<4.0',
        'pymongo>=3.7.2,<4.0',
        'requests>=2.21.0,<2.22.0'
    ],
    version="0.1",
    packages=find_packages(),  # TODO remove?
)
