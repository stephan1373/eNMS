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
