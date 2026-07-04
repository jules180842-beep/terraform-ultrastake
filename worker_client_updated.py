#!/usr/bin/env python3
"""
UltraStake Worker Client - Registers and monitors worker nodes
Sends periodic heartbeats and telemetry to Master Node
"""

import os
import time
import uuid
import requests
import random
import logging
import signal
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment
NODE_ID = os.getenv("NODE_ID", str(uuid.uuid4()))
MASTER_IP = os.getenv("MASTER_IP", "localhost")
WORKER_IP = os.getenv("WORKER_IP", "ec2-worker")
API_KEY = os.getenv("API_KEY", "")
HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "2"))
USERID = os.getenv("USER_ID", "default-user")

BASE_URL = f"http://{MASTER_IP}:8000"

class WorkerClient:
    """Client for worker node communication with master"""
    
    def __init__(self):
        self.node_id = NODE_ID
        self.worker_ip = WORKER_IP
        self.api_key = API_KEY
        self.user_id = USERID
        self.running = True
        self.metrics = {}
        
        # Graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        logger.info(f"Shutdown signal received. Unregistering node {self.node_id}...")
        self.running = False
        sys.exit(0)
    
    def register(self):
        """Register worker node with master"""
        try:
            response = requests.post(
                f"{BASE_URL}/register",
                headers={"X-API-Key": self.api_key} if self.api_key else {},
                json={
                    "node_id": self.node_id,
                    "ip": self.worker_ip,
                    "stake": 10,
                    "user_id": self.user_id,
                    "status": "active"
                },
                timeout=5
            )
            logger.info(f"✓ Worker registered: {response.json()}")
            return True
        except Exception as e:
            logger.error(f"✗ Registration failed: {e}")
            return False
    
    def collect_metrics(self):
        """Collect system and application metrics"""
        metrics = {
            "cpu": random.uniform(10, 95),
            "memory": random.uniform(20, 80),
            "memory_mb": random.randint(500, 3000),
            "load": random.uniform(0.5, 4),
            "disk_usage_percent": random.uniform(30, 70),
            "network_in_mbps": random.uniform(0, 100),
            "network_out_mbps": random.uniform(0, 100),
            "reward": random.uniform(0, 0.001),
            "active_connections": random.randint(5, 50),
            "uptime_hours": random.randint(1, 168)
        }
        self.metrics = metrics
        return metrics
    
    def send_heartbeat(self):
        """Send heartbeat with metrics to master"""
        try:
            metrics = self.collect_metrics()
            
            response = requests.post(
                f"{BASE_URL}/heartbeat",
                headers={"X-API-Key": self.api_key} if self.api_key else {},
                json={
                    "node_id": self.node_id,
                    "user_id": self.user_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "active",
                    **metrics
                },
                timeout=5
            )
            
            if response.status_code == 200:
                logger.debug(
                    f"♥ Heartbeat sent - CPU: {metrics['cpu']:.1f}%, "
                    f"Memory: {metrics['memory']:.1f}%, Load: {metrics['load']:.2f}"
                )
            else:
                logger.warning(f"Heartbeat returned status {response.status_code}")
        
        except Exception as e:
            logger.error(f"✗ Heartbeat failed: {e}")
    
    def run(self):
        """Main worker client loop"""
        logger.info(f"Starting UltraStake Worker Client")
        logger.info(f"Node ID: {self.node_id}")
        logger.info(f"Master: {MASTER_IP}")
        logger.info(f"Worker IP: {self.worker_ip}")
        
        # Register with master
        if not self.register():
            logger.warning("Registration failed, but continuing...")
        
        # Main heartbeat loop
        try:
            while self.running:
                self.send_heartbeat()
                time.sleep(HEARTBEAT_INTERVAL)
        
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    client = WorkerClient()
    client.run()
