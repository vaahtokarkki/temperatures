#!/bin/bash
touch .env # Fix docker compose build when missing env file
docker-compose build
docker tag "$DOCKER_USERNAME"/"$DOCKER_REPO":x86 "$DOCKER_USERNAME"/"$DOCKER_REPO":latest
docker-compose push
docker push "$DOCKER_USERNAME"/"$DOCKER_REPO":latest