# Abstract
This is Trend Search Site for VRChat.

# Build
docker build -t gcr.io/vrchat-analyzer/crawler .

## Develop
docker run -it --rm -p 8080:8080  -p 13306:3306 -v C:\obara\VrcSearch:/app gcr.io/vrchat-analyzer/crawler /bin/bash

## Test
python3 -m unittest tests/test_*

## remove docker caches
docker images -aq | xargs docker rmi

# Deploy
## gcloud docker -- push gcr.io/vrchat-analyzer/crawler # deprecated
docker image push gcr.io/vrchat-analyzer/crawler:latest

# Operation
## batch.py
Daily, Hourly batch

## app.py
Web page.

# Reference
https://cloud.google.com/cloud-build/docs/building/build-containers?hl=ja
