#!/bin/bash

if [ $1 == "build" ]; then
    echo "Building container...";
    docker build -t bot-api/v1 .;
fi

if [ $1 == "build-interactive" ]; then
    echo "Building container...";
    docker build -t bot-api-interactive/v1:latest -f Dockerfile-Interactive .;
fi