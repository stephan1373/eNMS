#!/bin/bash

start_cluster() {
    echo "Starting a new Galera cluster..."
    sudo galera_new_cluster
    check_status
}

check_status() {
    echo "Checking MariaDB status..."
    sudo systemctl status mariadb
    echo "Verifying cluster size..."
    sudo mysql -u root -p -e "SHOW STATUS LIKE 'wsrep_cluster_size';"
}

case "$1" in
    -s|--start)
        start_cluster
        ;;
    -c|--check)
        check_status
        ;;
    *)
        echo "Usage: $0 {-s|--start|-c|--check}"
        exit 1
        ;;
esac
