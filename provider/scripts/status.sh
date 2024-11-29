#!/bin/bash

# Get the list of all running container IDs for yagna-provider
container_ids=$(docker ps --filter "ancestor=yagna-provider" --format "{{.ID}}")

# Iterate over each container ID and execute the golemsp status command
for container_id in $container_ids; 
do
  echo "Status for container $container_id:"
  docker exec $container_id golemsp status
  echo ""
done
