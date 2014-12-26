#!/bin/bash

set -e
#set -x

# color flag
RED='\e[0;31m'
YEL='\e[1;33m'
GRN='\e[1;32m'
NC='\e[0m'


#
ROOT_UID=0
E_ROOT=1


clear
echo -e "${RED}-= Mazu installation =-${NC}"
echo "==> Here we go..."


# check if whoami = root
if [ "$UID" == "$ROOT_UID" ]; then
    echo "Must NOT be root ro run this script"
    exit $E_ROOT
fi


# install PREREQUISITES
echo "  > Installing PREREQUISITES..."
echo "  > Updating package soruce..."
sudo apt-get update &> /dev/null
echo "  > Installing python-dev libxml2-dev libxslt-dev..."
sudo apt-get -y install python-dev libxml2-dev libxslt-dev mongodb&> /dev/null
echo "  > Installing packages in requirements..."
sudo pip install -r requirements.txt &> /dev/null


# rename to production.py
cp settings/production.example.py settings/production.py


echo "  > Generating production key..."
PRO_GEN=$(/usr/bin/python -c 'import random; print "".join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZbcdefghijklmnopqrstuvwxyz0123456789\\#/$%@!&^*()<>?[]{}") for i in range(50)])')

# replace key in settings/production.py
sed -i "s|yoursecretkey|$PRO_GEN|g" settings/production.py

echo "  > Creating superuser for django..."
./manage.py createsuperuser

echo -e "  > Your key is ${YEL}$PRO_GEN${NC}. And is now using in settings/production.py"
echo -e "${GRN}-= Great, now you're all set to go! =-${NC}"
