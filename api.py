from typing import Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic import BaseSettings

from app import AppConfig, UploaderApp
from models.job import Job


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

@uploader.post("/job")
async def startJob(job: JobRequest):
    result = app.startJob(Job(
        job_id=job.Upload_id,
        source_basedir=job.Source_folder,
        target_bucket=job.Destination_bucket,
        regex=job.Regex
    ))
    return result

@uploader.get("/job/{job_id}")
async def getJob(job_id: str):
    job = app.getJob(job_id)
    if job == None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@uploader.on_event("startup")
async def startup_event():
    # pick up jobs ...
    pass

