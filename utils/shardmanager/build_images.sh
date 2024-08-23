#!/bin/bash
set -ex

sudo docker build --tag shard-manager:latest -f Dockerfile .

# Tag the images
sudo docker tag shard-manager xzhu0027/shard-manager:latest

# Push the images to the registry
sudo docker push  xzhu0027/shard-manager:latest

set +ex
