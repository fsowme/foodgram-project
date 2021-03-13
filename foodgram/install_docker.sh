#!/bin/bash
docker=`dpkg -l | grep docker-ce`
if [ -z "$docker" ]
then
    apt-get -y remove docker docker-engine docker.io containerd runc
    apt-get update
    apt-get -y install \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg-agent \
        software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
    add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) \
    stable"
    apt-get update
    apt-get -y install docker-ce docker-ce-cli containerd.io
fi

if [ ! -e /usr/local/bin/docker-compose ]
then
    sudo curl -L "https://github.com/docker/compose/releases/download/1.28.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi