# Southampton University Formula Student Team Intermediate Server
# Copyright (C) 2021 Nathan Rowley-Smith

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

FROM python:latest

SHELL ["/bin/bash", "-c"]

RUN mkdir -p /var/backend-server

COPY ./ /var/backend-server

RUN apt-get update

RUN apt-get install tree

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir -r /var/backend-server/requirements.txt

RUN ls -a /var/backend-server

EXPOSE 5000

ENTRYPOINT python /var/backend-server/server.py