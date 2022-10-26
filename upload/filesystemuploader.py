from shutil import copyfile
from os import path, makedirs
import logging
import hashlib
import base64

from models.task import Task
from upload.iuploader import IUploader

#
# implementation of the upload action - for a local filesystem
#   useful for testing and for mounted targets
#


class FileSystemUploader(IUploader):
    
    def __init__(self, workdir: str):
        self._workdir = workdir

    def run(self, task: Task) -> bool:
        target = path.join(self._workdir, task.target_bucket, task.target_name)
        logging.debug("copying from %s to %s",task.source, target)
        try:
            copyfile(task.source, target)
            if self._fileMd5(task.source) != self._fileMd5(target):
                logging.error("integrity error between %s and %s",task.source, target)
        except FileNotFoundError as e:
            # try creating parent directories
            makedirs(path.dirname(target))
            copyfile(task.source, target)
        return True
        

    def _fileMd5(self, filename:str ) -> str:
        with open(filename) as f:
            data = f.read()
            md = hashlib.md5(data.encode('utf-8')).digest()
            return base64.b64encode(md).decode('utf-8')