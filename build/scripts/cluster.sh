#!/bin/bash

# Function to start the Galera cluster
start_cluster() {
    echo "Starting a new Galera cluster..."
    sudo galera_new_cluster

    # Check the status of MariaDB to ensure it started correctly
    check_status
}

# Function to check the status of MariaDB and the cluster
check_status() {
    echo "Checking MariaDB status..."
    sudo systemctl status mariadb

    # Verify cluster size
    echo "Verifying cluster size..."
    mysql -u root -p -e "SHOW STATUS LIKE 'wsrep_cluster_size';"
}

# Parse the argument
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