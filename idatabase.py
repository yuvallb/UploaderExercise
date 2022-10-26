from typing import Iterator
from models.job import Job, JobCreation
from models.task import Task

# interface for the data persistance requirements
class IDatabase:
    
    # job: store the job_id, source folder, destination bucket and regex
    # job_id is the primary key
    def getActiveJobs(self) -> list[Job]:
        pass

    def startJob(self, job: Job) -> JobCreation:
        pass

    def finishJob(self, job_id: str) -> None:
        pass

    def getJob(self, job_id: str) -> Job:
        pass



    # task: store data for each transferred file: source and destination
    # source is the primary key
    def addTask(self, job_id: str, task: Task) -> None:
        pass

    def yieldPendingTasks(self, job_id: str) -> Iterator[Task]:
        pass
    
    def yieldInProgressTasks(self, job_id: str) -> Iterator[Task]:
        pass

    
    def setInProgressTask(self, job_id: str, source: str) -> None:
        # throw an exception if already in progress
        pass

    def touchInProgressTask(self, job_id: str, source: str) -> None:
        # update last_activity
        # throw an exception if not in progress
        pass

    def setTaskDone(self, job_id: str, source: str) -> None:
        pass

    def setTaskPending(self, job_id: str, source: str) -> None:
        pass