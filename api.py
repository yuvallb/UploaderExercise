from typing import Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic import BaseSettings

from app import AppConfig, UploaderApp
from models.job import Job


class APISettings(BaseSettings):
    db_workdir: str
    target_workdir: str


settings = APISettings()
app = UploaderApp(AppConfig(dbWorkdir=settings.db_workdir, targetWorkdir= settings.target_workdir))
uploader = FastAPI()

class JobRequest(BaseModel):
    jobId: str
    sourceBasedir: str
    targetBucket: str
    regex: Union[str, None] = None

@uploader.post("/job")
async def startJob(job: JobRequest):
    app.startJob(Job(
        job_id=job.jobId,
        source_basedir=job.sourceBasedir,
        target_bucket=job.targetBucket,
        regex=job.regex
    ))
    return {"message": "creating job"}

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

