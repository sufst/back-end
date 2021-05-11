#!/bin/bash

sudo git pull
sudo systemctl restart back-end.service
sudo systemctl status back-end.service