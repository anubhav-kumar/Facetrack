#!/opt/homebrew/bin/fish

set -l INSTANCE_NAME "facetrack_redis"
set -l IMAGE_NAME "docker.io/library/redis"
set -l PORT_MAPPING "6379:6379"
set -l VOLUME_MOUNT "./redis-data:/data"

podman run -d --name $INSTANCE_NAME -p $PORT_MAPPING -v $VOLUME_MOUNT $IMAGE_NAME
