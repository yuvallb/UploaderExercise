from models.task import Task

class IUploader:

    def run(self, job_id:str, task: Task):
        pass
