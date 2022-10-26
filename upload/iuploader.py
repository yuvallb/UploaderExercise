from models.task import Task

class IUploader:

    def run(self, task: Task) -> bool:
        pass
