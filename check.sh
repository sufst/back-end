#!/bin/bash

RED='\033[0;31m'     #RED
GREEN='\033[0;32m'   #GREEN
NC='\033[0m'         #No Color - Reset

echo "Checking System Status"

# Backend Check
systemctl is-active --quiet back-end && echo -e "BACK-END ${GREEN}RUNNING${NC}" || echo -e "BACK-END ${RED}NOT RUNNING${NC}"

# Intermediate Check
systemctl is-active --quiet intermediate-server && echo -e "INTERMEDIATE SERVER ${GREEN}RUNNING${NC}" || echo -e "INTERMEDIATE SERVER ${RED}NOT RUNNING${NC}"


