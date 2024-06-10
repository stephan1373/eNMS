#!/bin/bash

start_cluster() {
    echo "Starting a new Galera cluster..."
    sudo systemctl stop mariadb
    sudo galera_new_cluster
    sudo systemctl start mariadb
    sudo systemctl enable mariadb
    check_status
}

check_status() {
    echo "Checking MariaDB status..."
    sudo systemctl status mariadb

    echo "Verifying cluster size..."
    mysql -e "SHOW STATUS LIKE 'wsrep_cluster_size';"

    echo "Checking local state comment..."
    mysql -e "SHOW STATUS LIKE 'wsrep_local_state_comment';"

    echo "Checking cluster status..."
    mysql -e "SHOW STATUS LIKE 'wsrep_cluster_status';"

    echo "Checking if the node is connected to the cluster..."
    mysql -e "SHOW STATUS LIKE 'wsrep_connected';"

    echo "Checking if the node is ready to accept queries..."
    mysql -e "SHOW STATUS LIKE 'wsrep_ready';"

    echo "Checking the local state of the node..."
    echo "(0: INITIALIZING, 1: JOINING, 2: DONOR/DESYNCED, 3: JOINED, 4: SYNCED)"
    mysql -e "SHOW STATUS LIKE 'wsrep_local_state';"

    echo "Checking the local index of the node within the cluster..."
    mysql -e "SHOW STATUS LIKE 'wsrep_local_index';"

    echo "Checking the wsrep provider name..."
    mysql -e "SHOW STATUS LIKE 'wsrep_provider_name';"

    echo "Checking the wsrep provider version..."
    mysql -e "SHOW STATUS LIKE 'wsrep_provider_version';"

    echo "Checking the cluster configuration ID..."
    mysql -e "SHOW STATUS LIKE 'wsrep_cluster_conf_id';"

    echo "Checking the IP addresses of nodes in the cluster..."
    mysql -e "SHOW STATUS LIKE 'wsrep_incoming_addresses';"
}

delete_mariadb() {
    echo "Stopping MariaDB service..."
    sudo systemctl stop mariadb

    echo "Removing MariaDB packages..."
    sudo dnf remove -y mariadb mariadb-server

    echo "Removing MariaDB data and configuration files..."
    sudo rm -rf /var/lib/mysql
    sudo rm -rf /etc/my.cnf
    sudo rm -rf /etc/my.cnf.d
}

install_mariadb() {
    echo "Installing MariaDB packages..."
    sudo dnf install -y mariadb-server mariadb-server-galera

    echo "Starting and enabling MariaDB service..."
    sudo systemctl start mariadb
    sudo systemctl enable mariadb

    echo "Running MariaDB secure installation..."
    sudo mysql_secure_installation
}

restart_mariadb() {
    echo "Stopping MariaDB service..."
    sudo systemctl stop mariadb
    echo "Starting MariaDB service..."
    sudo systemctl start mariadb
}

case "$1" in
    -s|--start)
        start_cluster
        ;;
    -c|--check)
        check_status
        ;;
    -d|--delete)
        delete_mariadb
        ;;
    -i|--install)
        install_mariadb
        ;;
    -r|--restart)
        restart_mariadb
        ;;
    *)
        echo "Usage: $0 {-s|--start|-c|--check|-d|--delete|-i|--install}"
        exit 1
        ;;
esac
