from dataclasses import dataclass
from database.idatabase import IDatabase
from database.inmemorydatabase import InMemoryDatabase
import logging

from models.job import Job, JobCreation
from scanner import Scanner
from upload.iuploader import IUploader
from upload.s3uploader import S3Uploader
from upload.filesystemuploader import FileSystemUploader


# 
# Main application logic
#   uses the scanner, database and uploader classes
#


@dataclass
class AppConfig:
    dbWorkdir: str = ""
    targetSetting: str = "" # set "s3" for using the s3 uploader or a local folder for using the filesystem uploader

@dataclass
class RunJobResult:
    found: int = 0
    uploaded: int = 0
    


class UploaderApp:

    def __init__(self, config: AppConfig):
        self._db: IDatabase = InMemoryDatabase()
        self._config = config
        self._stop = False

    def startJob(self, job: Job) -> RunJobResult:
        logging.debug("called startJob with %s",job)
        creation = self._db.startJob(job)
        if creation == JobCreation.EXISTED:
            raise Exception("job already exists")

        result = RunJobResult()
        scanner = Scanner(self._db)
        uploader = self._uploaderFactory()
        
        scanner.run(job)
        for task in self._db.yieldPendingTasks(job.job_id):
            result.found += 1
            if uploader.run(task):
                result.uploaded += 1
                self._db.setTaskDone(job.job_id, task.source)
        self._db.finishJob(job.job_id)
        return result

    def startOngoingJob(self, job: Job):
        logging.debug("called startOngoingJob with %s",job)
        creation = self._db.startJob(job)
        if creation == JobCreation.EXISTED:
            raise Exception("job already exists")

        scanner = Scanner(self._db)
        uploader = self._uploaderFactory()
        
        while not self._stop:
            scanner.run(job)
            for task in self._db.yieldPendingTasks(job.job_id):
                if uploader.run(task):
                    self._db.setTaskDone(job.job_id, task.source)


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

    def stopTasks(self):
        self._stop = True

    def _uploaderFactory(self) -> IUploader:
        if self._config.targetSetting.lower() == "s3":
            return S3Uploader()
        if len(self._config.targetSetting)>0:
            return FileSystemUploader(self._config.targetSetting)
        raise Exception("No target configured")