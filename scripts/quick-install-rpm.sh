#!/bin/bash

install_database () {
    sudo -u postgres psql --host="$1" --port="$2" << EOF
create role spdx with login password '$3';
create role spdx_select with login password '$4';
create database spdx with owner spdx;
grant connect on database spdx to spdx_select;
grant select on all tables in schema public to spdx_select;
EOF
}

drop_create () { 
    dosocs2 dbinit
}

install_psql_config () {
    TEMP_CONFIG=$(mktemp)
    cat << EOF > $TEMP_CONFIG
connection_uri = postgresql://spdx:$3@$1:$2/spdx 
default_scanners = nomos
namespace_prefix = postgresql://$1:$2/spdx 
scanner_nomos_path = /usr/local/share/fossology/nomos/agent/nomossa
EOF
    sudo cp $TEMP_CONFIG /etc/dosocs2.conf
    sudo chmod 644 /etc/dosocs2.conf
}

if [[ "$(id -u)" == "0" ]]; then
    echo "[$0] Dangerous to run as root!"
    echo "[$0] Run as a nonprivileged user and I will 'sudo' as needed."
    exit 1
fi


if [[ ! -f "./setup.py" ]]; then
    echo "[$0] Didn't find setup.py in the current directory"
    echo "[$0] Make sure you run me with the package root as your working dir"
    exit 1
fi

echo "[$0] sudo yum install gcc git glib2-devel make postgresql-devel python-devel sqlite"
sudo yum install gcc git make postgresql-devel glib2-devel sqlite unzip || exit 1

if [[ -d "$VIRTUAL_ENV" ]]; then
    echo "[$0] Running inside a virtualenv"
    echo "[$0] pip install ."
    pip install . || exit 1
else
    echo "[$0] sudo pip install ."
    sudo pip install . || exit 1
fi

read -p "Install nomos scanner (y/N)? " yn
case ${yn:0:1} in
    y|Y ) ./scripts/install-nomos.sh ;;
    * ) ;;
esac

read -p "Install dependency-check scanner (y/N)? " yn
case ${yn:0:1} in
    y|Y ) ./scripts/install-dependency-check.sh ;;
    * ) ;;
esac

echo -e "\nSelect initial configuration:"
select ANSWER in "PostgreSQL (global)" "SQLite (per-user)"; do
    case $ANSWER in
        "PostgreSQL (global)" ) CONFIG_TYPE="postgresql" ; break ;;
        "SQLite (per-user)" ) CONFIG_TYPE="sqlite" ; break ;;
        * ) continue ;;
    esac
done

if [[ "$CONFIG_TYPE" == "postgresql" ]]; then

    read -e -p "Address or hostname of PostgreSQL server (localhost): " PSQL_HOST
    if [[ "$PSQL_HOST" == "" ]]; then
        PSQL_HOST="localhost"
    fi
    
    read -e -p "PostgreSQL port (5432): " PSQL_PORT
    if [[ "$PSQL_PORT" == "" ]]; then
        PSQL_PORT="5432"
    fi

    while true; do
        read -s -p "Password for role 'spdx': " SPDX_PASS
        echo ""
        read -s -p "Repeat password: " SPDX_PASS2
        echo ""
        if [[ "$SPDX_PASS" != "$SPDX_PASS2" ]]; then
            echo Passwords do not match!
        elif [[ "$SPDX_PASS" == "" ]]; then
            echo Password must not be empty!
        else
            break
        fi
    done

    while true; do
        read -s -p "Password for role 'spdx_select': " SPDX_SELECT_PASS
        echo ""
        read -s -p "Repeat password: " SPDX_SELECT_PASS2
        echo ""
        if [[ "$SPDX_SELECT_PASS" != "$SPDX_SELECT_PASS2" ]]; then
            echo Passwords do not match!
        else
            break
        fi
    done
    
    read -p "Install PostgresSQL SPDX roles and database now (on $PSQL_HOST:$PSQL_PORT as user postgres) (y/N)? " yn
    case ${yn:0:1} in
        y|Y ) install_database $PSQL_HOST $PSQL_PORT $SPDX_PASS $SPDX_SELECT_PASS;;
        * ) ;;
    esac

    read -p "Install DoSOCS2 PostgreSQL configuration to /etc/dosocs2.conf (y/N)? " yn
    case ${yn:0:1} in
        y|Y ) install_psql_config $PSQL_HOST $PSQL_PORT $SPDX_PASS;;
        * ) ;;
    esac

fi

if [[ "$CONFIG_TYPE" == "sqlite" ]]; then
    echo "[$0] dosocs2 newconfig"
    dosocs2 newconfig
fi

read -p "Create all tables in SPDX database (y/N)? " yn
case ${yn:0:1} in
    y|Y ) drop_create ;;
    * ) ;;
esac

echo "[$0] dosocs2 configtest"
dosocs2 configtest > /dev/null
if [[ "$?" != "0" ]]; then
    echo "[$0] The config test failed."
    echo "[$0] Make sure your dosocs2.conf has the correct database connection information."
else
    echo "[$0] The config test passed."
fi

echo "[$0] Ready to roll."
