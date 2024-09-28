#!/bin/bash

if [ $1 == "build-local" ]; then
    echo "Building container...";
    docker build -t bot-api/v1 .;
fi

if [ $1 == "build-interactive" ]; then
    echo "Building container...";
    docker build -t bot-api-interactive/v1:latest -f Dockerfile-Interactive .;
fi

if [ $1 == "build-hub" ]; then
    echo "Building container...";
    docker build -t generaliroh/general-project-repo:trading-bot-api-v1 .;
fi