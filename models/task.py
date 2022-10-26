from datetime import datetime
from enum import IntEnum
from dataclasses import dataclass

#
# Model for a single file upload task
#


class TaskStatus(IntEnum):
    PENDING = 1
    IN_PROGRESS = 2
    DONE = 3

@dataclass
class Task:
    source: str
    source_size: int
    source_last_modified: float
    target_name: str
    target_bucket: str
    status: TaskStatus = TaskStatus.PENDING
    last_activity: datetime = datetime.now()
