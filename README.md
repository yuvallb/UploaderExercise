# Uploader service 

## Home Assignment for Ultima Genomics

## Requirements

python >= 3.7

`pip install -r requirements.txt`

AWS region and user with permissions to upload to the configured bucket defined using `aws configure`

## Configuration

## Local run 

`DB_WORKDIR="/tmp/db" TARGET_SETTING="s3" uvicorn api:uploader --reload`

Browse to http://127.0.0.1:8000/docs

## Architecture

FastAPI...
Business logic ...
Database layer...

