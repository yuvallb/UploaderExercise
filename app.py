from dataclasses import dataclass
from database.idatabase import IDatabase
from database.inmemorydatabase import InMemoryDatabase
from models.job import Job, JobCreation
from scanner import Scanner
from upload.filesystemuploader import FileSystemUploader
import logging

from upload.iuploader import IUploader
from upload.s3uploader import S3Uploader

@dataclass
class AppConfig:
    dbWorkdir: str = ""
    targetSetting: str = "" # "s3" for using the s3 uploader or a local folder for using the filesystem uploader


class UploaderApp:

    def __init__(self, config: AppConfig):
        self._db: IDatabase = InMemoryDatabase()
        self._config = config

    def startJob(self, job: Job):
        logging.debug("called startJob with {}".format(job))
        creation = self._db.startJob(job)
        if creation == JobCreation.EXISTED:
            raise Exception("job already exists")

        scanner = Scanner(self._db)
        scanner.run(job)
        uploader = self._uploaderFactory()
        for task in self._db.yieldPendingTasks(job.job_id):
            if uploader.run(task):
                self._db.setTaskDone(job.job_id, task.source)
        self._db.finishJob(job.job_id)

    def resumeJobUploads(self, job_id: str):
        job = self._db.getJob(job_id)
        if job == None:
            raise Exception("job does not exist")

        uploader = self._uploaderFactory()
        for task in self._db.yieldPendingTasks(job.job_id):
            uploader.run(task)
        self._db.finishJob(job.job_id)

    def getJob(self, job_id: str) -> Job:
        return self._db.getJob(job_id)

    def recoverJobs(self):
        for job in self._db.getActiveJobs():
            self.startJob(job)


    def _uploaderFactory(self) -> IUploader:
        if self._config.targetSetting.lower() == "s3":
            return S3Uploader()
        if len(self._config.targetSetting)>0:
            return FileSystemUploader(self._config.targetSetting)
        raise Exception("No target configured")