from pathlib import Path
import re

from database.idatabase import IDatabase
from models.job import Job
from models.task import Task

class Scanner:
    def __init__(self, db: IDatabase):
        self._db = db

    def run(self, job: Job):
        fileNameFilter = None if job.regex == None else re.compile(job.regex)
        for tocopy in Path(job.source_basedir).rglob('*.*'):
            if fileNameFilter == None or fileNameFilter.search(tocopy.name):
                self._db.addTask(job.job_id, Task(
                    source=str(tocopy),
                    target_name=str(tocopy.relative_to(job.source_basedir)),
                    target_bucket=job.target_bucket
                ))
