#!/bin/bash


echo 'Updating Back-End From Remote'

sudo git pull
sudo systemctl restart back-end.service
sudo systemctl status back-end.service

RED='\033[0;31m'     #RED
GREEN='\033[0;32m'   #GREEN
NC='\033[0m'         #No Color - Reset

echo "Checking System Status"

# Backend Check
systemctl is-active --quiet back-end.service && echo -e "BACK-END ${GREEN}RUNNING${NC}" || echo -e "BACK-END ${RED}NOT RUNNING${NC}"

# Intermediate Check
systemctl is-active --quiet intermediate-server.service && echo -e "INTERMEDIATE SERVER ${GREEN}RUNNING${NC}" || echo -e "INTERMEDIATE SERVER ${RED}NOT RUNNING${NC}"