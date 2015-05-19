#!/bin/bash
#Copyright 2014 University of Nebraska at Omaha (UNO)
#Setup User Name and Password for MySql
u=$USER
p=$PWD

#Clone Repos
git clone https://github.com/socs-dev-env/SOCSDatabase
git clone https://github.com/socs-dev-env/DoSOCS
git clone https://github.com/socs-dev-env/SOCSDashboard

#Install Database
echo "Install SPDX Database..."
mysql --user=$u --password=$p < SOCSDatabase/SQL/SPDX.sql
#Exit mySql

#Create Upload Directory
echo "Creating Upload Directory..."
sudo mkdir SOCSDashboard/uploads
sudo chmod 777 SOCSDashboard/uploads


#Move source to base directorie
echo "Reconfigure Repo Folder Structure"
sudo mv DoSOCS/src/* DoSOCS/
sudo mv SOCSDashboard/src/* SOCSDashboard/
sudo chmod 777 DoSOCS/ -R

#Remove src directories
echo "Removing old Repo Directories"
sudo rm DoSOCS/src -R
sudo rm SOCSDashboard/src -R

#Delete Database Repo
echo "Remove Database Repo"
sudo rm SOCSDatabase -R

echo "Install Complete"
echo "Don't forget to update the setting files ('DoSOCS/settings.py' AND 'SOCSDashboard/function/Data_Source.php') with the database"
echo "connection information, and with the paths to Ninka and FOSSology."



