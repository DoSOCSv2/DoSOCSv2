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
mysql --user=$u --password=$p < Database/SQL/SPDX.sql
#Exit mySql

#Create Upload Directory
echo "Creating Upload Directory..."
sudo mkdir SPDXDash/uploads
sudo chmod 777 SPDXDash/uploads


#Move source to base directorie
echo "Reconfigure Repo Folder Structure"
sudo mv DoSPDX/src/* DoSPDX/
sudo mv SPDXDash/src/* SPDXDash/
sudo chmod 777 DoSPDX/ -R

#Remove src directories
echo "Removing old Repo Directories"
sudo rm DoSPDX/src -R
sudo rm SPDXDash/src -R

#Delete Database Repo
echo "Remove Database Repo"
sudo rm Database -R

echo "Install Complete"
echo "Don't forget to update the setting files ('DoSPDX/settings.py' AND 'SPDXDash/function/Data_Source.php') with the database"
echo "connection information, and with the paths to Ninka and FOSSology."



