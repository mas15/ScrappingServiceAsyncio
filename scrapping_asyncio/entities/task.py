import glob
import os
from contextlib import suppress
from enum import Enum

import attr

DOWNLOADS_DIR = 'downloads'


class Status(Enum):
    DONE = 'DONE'
    IN_PROGRESS = 'IN_PROGRESS'
    WAITING = 'WAITING'
    FAILED = 'FAILED'


class TaskNotDoneException(Exception):
    pass


@attr.s
class Task:
    id: str = attr.ib()
    url: str = attr.ib()
    status: Status = attr.ib()

    def asdict(self): # todo usunac stad
        as_dict = attr.asdict(self)
        with suppress(TaskNotDoneException):
            as_dict['images'] = self.images # [b64encode(img).decode('utf-8') for img in self.images]
            as_dict['text'] = self.text
        return as_dict

    @property
    def text(self):
        self._check_if_done()
        with open(self.text_location) as f:
            return f.read()

    @property
    def images(self):
        self._check_if_done()
        for img_file in glob.iglob(self.images_location):
            with open(img_file) as f:
                return f.read()

    @property
    def text_location(self):
        return texts_location_for_task(self.id)

    @property
    def images_location(self):
        return images_location_for_task(self.id)

    def _check_if_done(self):
        if self.status is not Status.DONE:
            raise TaskNotDoneException()


def images_location_for_task(id: str):
    return os.path.join(DOWNLOADS_DIR, id)


def texts_location_for_task(id: str):
    return os.path.join(DOWNLOADS_DIR, id + '.txt')
