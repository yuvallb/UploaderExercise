from database.idatabase import IDatabase
from models.task import Task
from upload.iuploader import IUploader
from shutil import copyfile
from os import path, makedirs
import logging

class FileSystemUploader(IUploader):
    
    def __init__(self, workdir: str):
        self._workdir = workdir

    def run(self, task: Task) -> bool:
        target = path.join(self._workdir, task.target_bucket, task.target_name)
        logging.debug("copying from {} to {}".format(task.source, target))
        try:
            copyfile(task.source, target)
        except FileNotFoundError as e:
            # try creating parent directories
            makedirs(path.dirname(target))
            copyfile(task.source, target)
        return True
        
