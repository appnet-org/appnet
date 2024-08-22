#!/bin/bash
set -ex

sudo docker build --tag load-manager:latest -f Dockerfile .

# Tag the images
sudo docker tag load-manager xzhu0027/load-manager:latest

# Push the images to the registry
sudo docker push  xzhu0027/load-manager:latest

set +ex
