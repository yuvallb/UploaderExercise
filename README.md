# Uploader service 

## Home Assignment for Ultima Genomics

## Requirements

python >= 3.7

`pip install -r requirements.txt`

AWS region and user with permissions to upload to the configured bucket defined using `aws configure`

## Configuration

## Local run 

`uvicorn api:uploader --reload`

To test on a local folder target:
`TARGET_SETTING="/tmp/target" uvicorn api:uploader --reload`

Browse to http://127.0.0.1:8000/docs

## Architecture

FastAPI...
Business logic ...
Database layer...

