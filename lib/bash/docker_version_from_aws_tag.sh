#!/bin/bash

# send all stdout & stderr to rancherci-bootstrap.log
exec > /tmp/rancher-ci-bootstrap.log
exec 2>&1
set -uxe


###############################################################################
# do whatever is requird to bootstrap redhat
###############################################################################
redhat_prep() {
    sudo yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
    sudo yum install -y wget at
    sudo systemctl start atd
}


###############################################################################
# figure out the OS family for our context
###############################################################################
get_osfamily() {
    local osfamily='unknown'

    # ugly way to figure out what OS family we are running.
    set +e
    if apt-get --version > /dev/null 2>&1; then
	osfamily='debian'
    elif yum --version > /dev/null 2>&1; then
	osfamily='redhat'
    fi
    set -e

    echo "${osfamily}"
}


###############################################################################
# detect OS and run appropriate prep stage
###############################################################################
system_prep() {
    local osfamily
    osfamily="$(get_osfamily)" || exit $?

    if [ 'redhat' == "${osfamily}" ]; then
	redhat_prep
    else
	echo "Did not detect an OS which needs prep. Not necessarily an error..."
    fi
}


###############################################################################
# the main() function
###############################################################################
main() {
    system_prep

    # some shared utilities here
    . /tmp/rancher_ci_bootstrap_common.sh

    fetch_rancherlabs_ssh_keys
    docker_install_tag_version

    local osfamily
    osfamily="$(get_osfamily)" || exit $?
    local nodename
    nodename="$(ec2_node_name)" || exit $?
    
    if [ 'redhat' == "${osfamily}" ]; then
	if echo "${nodename}" | grep 'agent'; then
	   schedule_docker_lvm_tweaks
	fi
    fi

    # add the current user to the docker group so we can later run docker containers
    sudo usermod -G docker "${USER}"
}


# the fun starts here
main

