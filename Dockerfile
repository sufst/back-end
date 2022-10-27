#
# Dockerfile to build Docker image for back-end server
# author: AndreasDemenagas (@AndreasDemenagas)
# date: October 27th 2022
#
# Copyright (C) 2022 SUFST
#

FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python", "server.py" ]
