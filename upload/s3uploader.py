from database.idatabase import IDatabase
from models.task import Task
from upload.iuploader import IUploader

class S3Uploader(IUploader):
    def __init__(self, db: IDatabase):
        self._db = db

    def run(self, job_id:str, task: Task):
        
        pass
