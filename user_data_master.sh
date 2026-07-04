#!/bin/bash

# Update system packages
apt update -y
apt install -y python3 python3-pip git curl

# Install Python dependencies
pip3 install fastapi uvicorn

# Clone UltraStake core repository
cd /home/ubuntu
git clone https://github.com/YOUR_ORG/ultrastake-core.git
cd ultrastake-core

# Install project requirements
pip3 install -r requirements.txt

# Set environment variables
export NODE_ROLE=master
export PORT=8000

# Start the FastAPI server
nohup python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8000 > master.log 2>&1 &

echo "Master node started on port 8000"
