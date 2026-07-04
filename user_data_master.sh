#!/bin/bash

apt update -y
apt install -y python3 python3-pip git

cd /home/ubuntu
git clone https://github.com/YOUR_ORG/ultrastake-core.git
cd ultrastake-core

pip3 install -r requirements.txt

export NODE_ROLE=master
export PORT=8000

nohup python3 -m api.server > master.log 2>&1 &