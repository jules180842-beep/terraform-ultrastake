"""Simple usage metering for API calls and resources"""

from collections import defaultdict
from datetime import datetime
from typing import Dict

# In-memory usage tracking
USAGE = defaultdict(lambda: {
    "api_calls": 0,
    "nodes": 0,
    "storage_gb": 0,
    "bandwidth_gb": 0,
    "last_updated": None
})

def track_api_call(user_id: str) -> None:
    """Track an API call for a user"""
    USAGE[user_id]["api_calls"] += 1
    USAGE[user_id]["last_updated"] = datetime.utcnow().isoformat()

def track_node(user_id: str, count: int = 1) -> None:
    """Track active nodes for a user"""
    USAGE[user_id]["nodes"] = count
    USAGE[user_id]["last_updated"] = datetime.utcnow().isoformat()

def track_storage(user_id: str, amount: float) -> None:
    """Track storage usage in GB"""
    USAGE[user_id]["storage_gb"] += amount
    USAGE[user_id]["last_updated"] = datetime.utcnow().isoformat()

def track_bandwidth(user_id: str, amount: float) -> None:
    """Track bandwidth usage in GB"""
    USAGE[user_id]["bandwidth_gb"] += amount
    USAGE[user_id]["last_updated"] = datetime.utcnow().isoformat()

def get_usage(user_id: str) -> Dict:
    """Get usage metrics for a user"""
    return dict(USAGE[user_id])

def reset_usage(user_id: str) -> None:
    """Reset usage metrics for a user (for new billing cycle)"""
    USAGE[user_id] = {
        "api_calls": 0,
        "nodes": 0,
        "storage_gb": 0,
        "bandwidth_gb": 0,
        "last_updated": datetime.utcnow().isoformat()
    }
