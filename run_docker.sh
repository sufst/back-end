#!/bin/bash

env -i

source venv/bin/activate

pip freeze > requirements.txt

deactivate

docker build -t sufst-back-end .
docker stop sufst-back-end
docker rm sufst-back-end

# Assigns localhost to host.docker.internal (host.docker.internal = the localhost of the host machine)
# host-gateway = alias to my localhost
docker run --add-host host.docker.internal:host-gateway -p 5000:5000 -it --rm --name sufst-back-end sufst-back-end
