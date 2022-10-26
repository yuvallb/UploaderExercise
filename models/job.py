from enum import IntEnum
from dataclasses import dataclass

#
# Model for the upload job
#


class JobStatus(IntEnum):
    ACTIVE = 1
    INACTIVE = 2

class JobCreation(IntEnum):
    CREATED = 1
    EXISTED = 2

@dataclass
class Job:
    job_id: str
    source_basedir: str
    target_bucket: str
    regex: str = None
    status: JobStatus = JobStatus.ACTIVE

