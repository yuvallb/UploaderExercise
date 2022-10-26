from dataclasses import dataclass
from datetime import datetime
from typing import  Iterator

from models.job import Job, JobCreation, JobStatus
from models.task import Task, TaskStatus
from database.idatabase import IDatabase

#
# implementation of data persistance 
#   does not support out of process persistance (api restart)
#

@dataclass
class JobPersistance:
    job: Job
    tasks: dict[str, Task]

class InMemoryDatabase(IDatabase):



    def __init__(self):
        self.__db: dict[str, JobPersistance] = {}


    # job: store the job_id, source folder, destination bucket and regex
    # job_id is the primary key
    def getActiveJobs(self) -> list[Job]:
        return list(map(lambda tp: tp.job, self.__db.values()))

    def startJob(self, job: Job) -> JobCreation:
        if job.job_id in self.__db:
            return JobCreation.EXISTED
        self.__db[job.job_id] = JobPersistance(
            job=job,
            tasks = {}
        )
        return JobCreation.CREATED

    def finishJob(self, job_id: str) -> None:
        self.__db[job_id].job.status = JobStatus.INACTIVE

    def getJob(self, job_id: str) -> Job:
        if job_id in self.__db.keys():
            return self.__db[job_id].job
        return None

    # task: store data for each transferred file: source and destination
    # source is the primary key
    def addTask(self, job_id: str, task: Task) -> None:
        if task.source in self.__db[job_id].tasks:
            existing = self.__db[job_id].tasks[task.source]
            if existing.source_size == task.source_size and existing.source_last_modified == task.source_last_modified:
                # avoid resetting a file that was already transferred
                return
        self.__db[job_id].tasks[task.source] = task

    def yieldPendingTasks(self, job_id: str) -> Iterator[Task]:
        for source in self.__db[job_id].tasks:
            task = self.__db[job_id].tasks[source]
            if task.status == TaskStatus.PENDING:
                yield task
    
    def yieldInProgressTasks(self, job_id: str) -> Iterator[Task]:
        for source in self.__db[job_id].tasks:
            task = self.__db[job_id].tasks[source]
            if task.status == TaskStatus.IN_PROGRESS:
                yield task

    
    def setInProgressTask(self, job_id: str, source: str) -> None:
        # throw an exception if already in progress
        self.__assertTaskExists(job_id, source)
        task = self.__db[job_id].tasks[source]
        if task.status == TaskStatus.IN_PROGRESS:
            raise Exception('task already in progress')
        task.last_activity = datetime.now()
        task.status = TaskStatus.IN_PROGRESS
         

    def touchInProgressTask(self, job_id: str, source: str) -> None:
        # update last_activity
        # throw an exception if not in progress
        self.__assertTaskExists(job_id, source)
        task = self.__db[job_id].tasks[source]
        if task.status != TaskStatus.IN_PROGRESS:
            raise Exception('task not in progress')
        task.last_activity = datetime.now()

    def setTaskDone(self, job_id: str, source: str) -> None:
        self.__assertTaskExists(job_id, source)
        task = self.__db[job_id].tasks[source]
        task.last_activity = datetime.now()
        task.status = TaskStatus.DONE

    def setTaskPending(self, job_id: str, source: str) -> None:
        self.__assertTaskExists(job_id, source)
        task = self.__db[job_id].tasks[source]
        task.last_activity = datetime.now()
        task.status = TaskStatus.DONE

    def __assertTaskExists(self, job_id: str, source: str) -> None:
        if source not in self.__db[job_id].tasks.keys():
            raise Exception('task not found')
