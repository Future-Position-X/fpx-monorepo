#! /usr/bin/env bash

# Exit in case of error
set -e

docker login 
docker build -f base-backend.dockerfile -t fpxgia/geo-api-backend-base:latest .
docker build -f base-worker.dockerfile -t fpxgia/geo-api-worker-base:latest .
docker push fpxgia/geo-api-backend-base:latest
docker push fpxgia/geo-api-worker-base:latest
