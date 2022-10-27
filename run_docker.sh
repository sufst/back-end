#!/bin/bash

#
# Bash script to generate requirements.txt file, build docker image and launch container.
# author: AndreasDemenagas (@AndreasDemenagas)
# date: October 27th 2022
#
# Copyright (C) 2022 SUFST
#

env -i

# Activates the Virtual Environment
source venv/bin/activate

# Freezes pip and generates a requirements.txt file with dependencies.
# This file will be used later on to install everything in the Docker container
pip freeze > requirements.txt

deactivate

# Builds the Docker image, giving it the name `sufst-back-end`
docker build -t sufst-back-end .

# Stops existing containers with the same name and removes them from Docker.
docker stop sufst-back-end
docker rm sufst-back-end

# Runs the container from the built image and exposes port 5000 to the local machine's port 5000
# Assigns localhost to host.docker.internal (host.docker.internal = the localhost of the host machine)
# host-gateway = alias to my localhost
docker run --add-host host.docker.internal:host-gateway -p 5000:5000 -it --rm --name sufst-back-end sufst-back-end
