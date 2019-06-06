from enum import Enum
from typing import List, Optional

import attr


class Status(Enum):
    DONE = 'DONE'
    IN_PROGRESS = 'IN_PROGRESS'
    WAITING = 'WAITING'
    FAILED = 'FAILED'


@attr.s
class Task:
    id: str = attr.ib()
    url: str = attr.ib()
    status: Status = attr.ib(converter=Status)

    images_paths: Optional[List[str]] = attr.ib(default=None)
    text_path: Optional[str] = attr.ib(default=None)
# [b64encode(img).decode('utf-8') for img in self.images]
