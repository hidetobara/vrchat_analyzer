# Abstract
This is VRChat Search Site.

# Build
docker build -t vrc docker/

# run
docker run -it --rm -p 8080:8080 -v C:\obara\VrcSearch:/app vrc /bin/bash

# push
# memory_size = 2G
gcloud builds submit --tag gcr.io/art-of-art/test --project art-of-art .

# better ?
# PROJECT_ID=vrchat-analyzer
# IMAGE=crawler

docker build -t gcr.io/vrchat-analyzer/crawler .
gcloud docker -- push gcr.io/vrchat-analyzer/crawler

# 中間イメージ削除
docker images -aq | xargs docker rmi
