#!/bin/bash

# Usage: sudo bash build_images.sh -u <user> -t <tag>
#   Login to docker hub with `docker login` before running the script

set -ex

EXEC=docker
IMAGE="ping_pong_app"

while getopts "u:t:" opt; do
  case $opt in
    u) USER="$OPTARG";;
    t) TAG="$OPTARG";;
    \?) echo "Invalid option: -$OPTARG" >&2; exit 1;;
    :) echo "Option -$OPTARG requires an argument." >&2; exit 1;;
  esac
done

if [ -z "$USER" ] || [ -z "$TAG" ]; then
  echo "You must specify -u (USER) and -t (TAG) options."
  exit 1
fi

echo "Cleaning old images, builder, and containers..."
$EXEC system prune -af

# rebuild, tag, push new image(s)
echo Processing image ${IMAGE}
# build and tag image
$EXEC build -t "$USER"/"$IMAGE":"$TAG" -f Dockerfile .
$EXEC push "$USER"/"$IMAGE":"$TAG"
echo


set +ex
