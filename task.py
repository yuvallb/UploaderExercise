from datetime import datetime
from enum import IntEnum
from dataclasses import dataclass

class TaskStatus(IntEnum):
    PENDING = 1
    IN_PROGRESS = 2
    DONE = 3

@dataclass
class Task:
    source: str
    target_name: str
    target_bucket: str
    status: TaskStatus = TaskStatus.PENDING
    last_activity: datetime = datetime.now()


#task = Task(source="/abc/dfe",target="s3://somebucket/def")
#print(task)
#Task(source='/abc/dfe', target='s3://somebucket/def', status=<TaskStatus.PENDING: 1>, last_activity=datetime.datetime(2022, 10, 25, 12, 18, 10, 13859))
