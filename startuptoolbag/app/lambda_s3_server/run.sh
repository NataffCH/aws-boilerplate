#!/bin/bash

docker build -t myfunction:latest .
docker run -p 9000:8080 -e BUCKET=startuptoolbag-prod-lamb-datapipelinerawbucket2b3-siwnrvxuuum1 myfunction:latest
