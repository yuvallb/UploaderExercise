from database.idatabase import IDatabase
from models.task import Task
from upload.iuploader import IUploader
from botocore.exceptions import ClientError
import boto3
import logging

class S3Uploader(IUploader):
    def __init__(self):
        # assuming the region, access key and secret are configured in the environment
        self._client = boto3.client('s3') 

    def run(self, task: Task) -> bool:
        try:
            self._client.upload_file(task.source, task.target_bucket, task.target_name)
        except Exception as e:
            logging.error(e)
            return False
        return True
        
    
    