#!/bin/bash

set -e
#set -x

# color flag
RED='\e[0;31m'
YEL='\e[1;33m'
GRN='\e[1;32m'
NC='\e[0m'

clear
echo -e "${RED}-= RUNNING Mazu =-${NC}"
echo "==> Here we go..."

# celery db migration
echo "  > Migrating celery database..."
./manage.py migrate &> /dev/null

# Initialize database
echo "  > Initializing database..."
./manage.py syncdb &> /dev/null

# start web server
echo "  > Starting web service..."
read -p "  > Type in IP address that binds mazu to : " ip
read -p "  > Type in port number that runs mazu : " port
sed -i s/iptochange/$ip/g settings/production.py

./manage.py runserver $ip:$port &
sleep 5

# start celery worker
echo "  > Starting celery worker..."
./manage.py celery worker --app mazu --beat

