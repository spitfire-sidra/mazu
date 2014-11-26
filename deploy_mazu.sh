#!/bin/bash

set -e
#set -x

# color flag
red='\e[0;31m'
yel='\e[1;33m'
grn='\e[1;32m'
NC='\e[0m'


#
ROOT_UID=0
E_ROOT=1


clear
echo -e "${red}-= Mazu installation =-${NC}"
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
sudo apt-get -y install python-dev libxml2-dev libxslt-dev &> /dev/null
echo "  > Installing packages in requirements..."
sudo pip install -r requirements.txt &> /dev/null


# rename to production.py
cp settings/production.example.py settings/production.py


echo "  > Generating production key..."
pro_gen=$(/usr/bin/python -c 'import random; print "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for i in range(50)])')

# replace key in settings/production.py
sed -i s/yoursecretkey/$pro_gen/g settings/production.py 


echo -e "  > Your key is ${yel}$pro_gen${NC}. And is now using in settings/production.py"
echo -e "${grn}-= Great, now you're all set to go! =-${NC}"
