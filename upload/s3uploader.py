import boto3
import logging
import hashlib
import base64

from models.task import Task
from upload.iuploader import IUploader


#
# implementation of the upload action - for AWS S3
#

class S3Uploader(IUploader):
    def __init__(self):
        # assuming the region, access key and secret are configured in the environment
        self._client = boto3.client('s3') 

    def run(self, task: Task) -> bool:
        try:
            with open(task.source) as f:
                data = f.read()
                md = hashlib.md5(data.encode('utf-8')).digest()
                contents_md5 = base64.b64encode(md).decode('utf-8')
            self._client.put_object(
                Bucket=task.target_bucket,
                Key=task.target_name,
                Body=data,
                ContentMD5=contents_md5
            )
        except Exception as e:
            logging.error(e)
            return False
        return True
        
    