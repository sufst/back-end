#!/bin/bash

#
# Bash script to create venv and install dependencies from requirements.txt file
# author: AndreasDemenagas (@AndreasDemenagas)
# date: October 29th 2022
#
# Copyright (C) 2022 SUFST
#

# Checks if python is installed.
if !command -v python3.9 &> /dev/null
then
    echo "Python3.9 is not installed in your system."
    exit
else
    echo "Python3.9 detected ok."
fi

python3.9 -m venv venv

source venv/bin/activate
pip install --no-cache-dir wheel
pip install --no-cache-dir -r requirements.txt
deactivate

