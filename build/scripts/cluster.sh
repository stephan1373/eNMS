#!/bin/bash

# Function to start the Galera cluster
start_cluster() {
    echo "Starting a new Galera cluster..."
    sudo galera_new_cluster

    # Check the status of MariaDB to ensure it started correctly
    echo "Checking MariaDB status..."
    sudo systemctl status mariadb

    # Optionally, verify cluster size
    echo "Verifying cluster size..."
    mysql -u root -p -e "SHOW STATUS LIKE 'wsrep_cluster_size';"
}

# Parse the argument
case "$1" in
    -s|--start)
        start_cluster
        ;;
    *)
        echo "Usage: $0 -s|--start"
        exit 1
        ;;
esac