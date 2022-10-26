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

class UploadJobRequest(BaseModel):
    Upload_id: str
    Source_folder: str
    Destination_bucket: str
    Regex: Union[str, None] = None

# upload files in the foreground, the request will stay open until upload is finished
@uploader.post("/upload")
async def upload_folder(job: UploadJobRequest):
    result = app.startJob(Job(
        job_id=job.Upload_id,
        source_basedir=job.Source_folder,
        target_bucket=job.Destination_bucket,
        regex=job.Regex
    ))
    return result

# upload files in the background, the request will return with 202 response
@uploader.post("/background-upload", status_code=202)
async def upload_folder_in_background(job: UploadJobRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(app.startJob, Job(
        job_id=job.Upload_id,
        source_basedir=job.Source_folder,
        target_bucket=job.Destination_bucket,   
        regex=job.Regex
    ))
    return {"message": "started background upload id {}".format(job.Upload_id)}


# upload files in the background, and continue to monitor for changes, the request will return with 202 response
@uploader.post("/ongoing-background-upload", status_code=202)
async def ongoing_upload_folder_in_background(job: UploadJobRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(app.startOngoingJob, Job(
        job_id=job.Upload_id,
        source_basedir=job.Source_folder,
        target_bucket=job.Destination_bucket,   
        regex=job.Regex
    ))
    return {"message": "started ongoing background upload id {}".format(job.Upload_id)}


# get upload status
@uploader.get("/upload/{Upload_id}")
async def get_upload_information(Upload_id: str):
    job = app.getJob(Upload_id)
    if job == None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

# event to allow resuming stopped uploads
@uploader.on_event("startup")
async def startup_event():
    SingleBackgroundTask(app.recoverJobs)
