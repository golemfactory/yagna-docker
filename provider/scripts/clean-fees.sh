#!/bin/bash

# Get the list of all running container IDs for yagna-provider
container_ids=$(docker ps --filter "ancestor=yagna-provider" --format "{{.ID}}")

# Iterate over each container ID and execute the golemsp status command
for container_id in $container_ids; 
do
  echo "Status for container $container_id:"
  docker exec $container_id golemsp settings set --starting-fee 0 --env-per-hour 0 --cpu-per-hour 0
  echo ""
done
