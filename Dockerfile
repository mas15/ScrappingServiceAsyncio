FROM python:3.7-alpine
RUN pip3 install --upgrade pip
COPY scrapping_asyncio /app/scrapping_asyncio
COPY setup.py /app
WORKDIR app
RUN mkdir downloads
RUN pip3 install .
# todo dockerignore