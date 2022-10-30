#!/bin/bash

docker build --tag=items-store-api .
docker image prune -f