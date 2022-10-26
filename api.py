from typing import Union

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from pydantic import BaseSettings
from starlette.background import BackgroundTask as SingleBackgroundTask

from app import AppConfig, UploaderApp
from models.job import Job

# 
# API server 
#  uses the pplication logic
#


# external settings recieved from environment variables
class APISettings(BaseSettings):
    db_workdir: str = ""
    target_setting: str = ""


settings = APISettings()
app = UploaderApp(AppConfig(dbWorkdir=settings.db_workdir, targetSetting=settings.target_setting))
uploader = FastAPI()

class JobRequest(BaseModel):
    Upload_id: str
    Source_folder: str
    Destination_bucket: str
    Regex: Union[str, None] = None

# upload files in the foreground, the request will stay open until upload is finished
@uploader.post("/job")
async def startJob(job: JobRequest):
    result = app.startJob(Job(
        job_id=job.Upload_id,
        source_basedir=job.Source_folder,
        target_bucket=job.Destination_bucket,
        regex=job.Regex
    ))
    return result

# upload files in the background, the request will return with 202 response
@uploader.post("/background-job", status_code=202)
async def startBackgroundJob(job: JobRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(app.startJob, Job(
        job_id=job.Upload_id,
        source_basedir=job.Source_folder,
        target_bucket=job.Destination_bucket,   
        regex=job.Regex
    ))
    return {"message": "started background upload id {}".format(job.Upload_id)}


# upload files in the background, and continue to monitor for changes, the request will return with 202 response
@uploader.post("/ongoing-background-job", status_code=202)
async def startOngoingBackgroundMonitorJob(job: JobRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(app.startOngoingJob, Job(
        job_id=job.Upload_id,
        source_basedir=job.Source_folder,
        target_bucket=job.Destination_bucket,   
        regex=job.Regex
    ))
    return {"message": "started ongoing background upload id {}".format(job.Upload_id)}


# get upload status
@uploader.get("/job/{job_id}")
async def getJob(job_id: str):
    job = app.getJob(job_id)
    if job == None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

# event to allow resuming stopped uploads
@uploader.on_event("startup")
async def startup_event():
    SingleBackgroundTask(app.recoverJobs)
