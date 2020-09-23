# Abstract
This is VRChat Search Site.

# Build
docker build -t gcr.io/vrchat-analyzer/crawler .

# run
docker run -it --rm -p 8080:8080 -v C:\obara\VrcSearch:/app gcr.io/vrchat-analyzer/crawler /bin/bash

# push
### memory_size = 2G
gcloud builds submit --tag gcr.io/art-of-art/test --project art-of-art .

### PROJECT_ID=vrchat-analyzer
### IMAGE=crawler

# deploy
docker build -t gcr.io/vrchat-analyzer/crawler .
gcloud docker -- push gcr.io/vrchat-analyzer/crawler

# remove docker caches
docker images -aq | xargs docker rmi
