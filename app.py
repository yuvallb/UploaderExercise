from dataclasses import dataclass
from database.idatabase import IDatabase
from database.inmemorydatabase import InMemoryDatabase
from models.job import Job, JobCreation
from scanner import Scanner
from upload.filesystemuploader import FileSystemUploader
import logging

@dataclass
class AppConfig:
    dbWorkdir: str = ""
    targetWorkdir: str = ""
    # TBD for connection strings, settings etc.

class UploaderApp:

    def __init__(self, config: AppConfig):
        self._db: IDatabase = InMemoryDatabase()
        self._config = config

    def startJob(self, job: Job):
        logging.debug("called startJob with {}".format(job))
        creation = self._db.startJob(job)
        if creation == JobCreation.CREATED:
            scanner = Scanner(self._db)
            scanner.run(job)
        uploader = FileSystemUploader(self._config.targetWorkdir, self._db)
        for task in self._db.yieldPendingTasks(job.job_id):
            uploader.run(job.job_id, task)
        self._db.finishJob(job.job_id)

    def getJob(self, job_id: str) -> Job:
        return self._db.getJob(job_id)

    def recoverJobs(self):
        for job in self._db.getActiveJobs():
            self.startJob(job)