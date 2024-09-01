#!/bin/bash
set -ex

sudo docker build --tag load-manager:latest -f Dockerfile .

# Tag the images
sudo docker tag load-manager appnetorg/load-manager:latest

# Push the images to the registry
sudo docker push  appnetorg/load-manager:latest

set +ex
