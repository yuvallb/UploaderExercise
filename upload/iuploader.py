from models.task import Task

#
# interface for the upload action
#


class IUploader:

    def run(self, task: Task) -> bool:
        pass
