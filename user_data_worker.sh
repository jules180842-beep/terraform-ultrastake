#!/bin/bash

apt update -y
apt install -y python3 python3-pip git

cd /home/ubuntu
git clone https://github.com/YOUR_ORG/ultrastake-core.git
cd ultrastake-core

pip3 install -r requirements.txt

export MASTER_IP=${master_ip}
export NODE_ROLE=worker
export PORT=8000

# register + run validator + telemetry
nohup python3 -m simulator.validator_sim > validator.log 2>&1 &
nohup python3 -m core.telemetry > telemetry.log 2>&1 &