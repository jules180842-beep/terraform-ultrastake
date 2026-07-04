"""
Usage tracking module for the Usage Service.
Tracks and reports resource consumption metrics.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum
import uuid

# In-memory usage database (in production, use a real database)
USAGE_EVENTS = {}
USAGE_AGGREGATES = {}

class EventType(str, Enum):
    """Types of trackable events"""
    API_CALL = "api_call"
    NODE_ONLINE = "node_online"
    NODE_OFFLINE = "node_offline"
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    BANDWIDTH = "bandwidth"

# Resource limits per plan
PLAN_LIMITS = {
    "free": {
        "max_nodes": 3,
        "max_api_calls": 1_000,
        "max_storage_gb": 10,
        "max_bandwidth_gb": 5,
        "monitoring_interval": "hourly"
    },
    "starter": {
        "max_nodes": 10,
        "max_api_calls": 10_000,
        "max_storage_gb": 100,
        "max_bandwidth_gb": 50,
        "monitoring_interval": "real-time"
    },
    "pro": {
        "max_nodes": 50,
        "max_api_calls": 50_000,
        "max_storage_gb": 500,
        "max_bandwidth_gb": 500,
        "monitoring_interval": "real-time"
    },
    "enterprise": {
        "max_nodes": -1,  # Unlimited
        "max_api_calls": -1,  # Unlimited
        "max_storage_gb": -1,  # Unlimited
        "max_bandwidth_gb": -1,  # Unlimited
        "monitoring_interval": "real-time"
    }
}

class UsageEvent:
    """Represents a single usage event"""
    
    def __init__(self, user_id: str, event_type: str, amount: float = 1, metadata: Dict = None):
        self.event_id = str(uuid.uuid4())
        self.user_id = user_id
        self.event_type = EventType(event_type) if isinstance(event_type, str) else event_type
        self.amount = amount
        self.timestamp = datetime.utcnow()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "user_id": self.user_id,
            "event_type": self.event_type.value,
            "amount": self.amount,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

class UsageAggregate:
    """Aggregated usage metrics for a user"""
    
    def __init__(self, user_id: str, plan: str, period_start: datetime = None):
        self.aggregate_id = str(uuid.uuid4())
        self.user_id = user_id
        self.plan = plan
        self.period_start = period_start or datetime.utcnow()
        self.period_end = self.period_start + timedelta(days=30)
        self.api_calls = 0
        self.nodes_active = 0
        self.compute_hours = 0
        self.storage_gb = 0
        self.bandwidth_gb = 0
        self.events_count = 0
        self.last_updated = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        limits = PLAN_LIMITS.get(self.plan, {})
        return {
            "aggregate_id": self.aggregate_id,
            "user_id": self.user_id,
            "plan": self.plan,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "api_calls": self.api_calls,
            "api_calls_limit": limits.get("max_api_calls"),
            "nodes_active": self.nodes_active,
            "nodes_limit": limits.get("max_nodes"),
            "compute_hours": self.compute_hours,
            "storage_gb": self.storage_gb,
            "storage_limit_gb": limits.get("max_storage_gb"),
            "bandwidth_gb": self.bandwidth_gb,
            "bandwidth_limit_gb": limits.get("max_bandwidth_gb"),
            "events_count": self.events_count,
            "last_updated": self.last_updated.isoformat()
        }

def log_usage_event(user_id: str, event_type: str, amount: float = 1, metadata: Dict = None) -> Dict:
    """
    Log a usage event for a user.
    
    Args:
        user_id: User unique identifier
        event_type: Type of event (api_call, node_online, compute, etc.)
        amount: Quantity of event
        metadata: Additional event metadata
        
    Returns:
        Logged event dictionary
    """
    event = UsageEvent(user_id, event_type, amount, metadata)
    
    # Store event
    if user_id not in USAGE_EVENTS:
        USAGE_EVENTS[user_id] = []
    USAGE_EVENTS[user_id].append(event)
    
    return event.to_dict()

def get_usage_summary(user_id: str, plan: str = "free") -> Dict:
    """
    Get aggregated usage summary for a user.
    
    Args:
        user_id: User unique identifier
        plan: User's subscription plan
        
    Returns:
        Usage summary dictionary
    """
    # Check if aggregate exists
    agg_key = f"{user_id}:{datetime.utcnow().strftime('%Y-%m')}"
    
    if agg_key not in USAGE_AGGREGATES:
        aggregate = UsageAggregate(user_id, plan)
        USAGE_AGGREGATES[agg_key] = aggregate
    else:
        aggregate = USAGE_AGGREGATES[agg_key]
    
    # Count events from this period
    if user_id in USAGE_EVENTS:
        events = USAGE_EVENTS[user_id]
        for event in events:
            if aggregate.period_start <= event.timestamp <= aggregate.period_end:
                aggregate.events_count += 1
                
                if event.event_type == EventType.API_CALL:
                    aggregate.api_calls += event.amount
                elif event.event_type == EventType.NODE_ONLINE:
                    aggregate.nodes_active = int(event.amount)
                elif event.event_type == EventType.COMPUTE:
                    aggregate.compute_hours += event.amount
                elif event.event_type == EventType.STORAGE:
                    aggregate.storage_gb += event.amount
                elif event.event_type == EventType.BANDWIDTH:
                    aggregate.bandwidth_gb += event.amount
    
    aggregate.last_updated = datetime.utcnow()
    return aggregate.to_dict()

def check_usage_limits(user_id: str, plan: str) -> Dict:
    """
    Check if user has exceeded any usage limits.
    
    Args:
        user_id: User unique identifier
        plan: User's subscription plan
        
    Returns:
        Dictionary with limit status and warnings
    """
    summary = get_usage_summary(user_id, plan)
    limits = PLAN_LIMITS.get(plan, {})
    
    warnings = []
    exceeded = []
    
    # Check API calls limit
    if limits.get("max_api_calls", -1) > 0:
        api_calls_pct = (summary["api_calls"] / limits["max_api_calls"]) * 100
        if api_calls_pct >= 100:
            exceeded.append("api_calls")
        elif api_calls_pct >= 80:
            warnings.append(f"API calls at {api_calls_pct:.1f}% of limit")
    
    # Check nodes limit
    if limits.get("max_nodes", -1) > 0:
        if summary["nodes_active"] > limits["max_nodes"]:
            exceeded.append("nodes")
        elif summary["nodes_active"] >= limits["max_nodes"] * 0.8:
            warnings.append(f"Active nodes at {(summary['nodes_active']/limits['max_nodes'])*100:.1f}% of limit")
    
    # Check storage limit
    if limits.get("max_storage_gb", -1) > 0:
        storage_pct = (summary["storage_gb"] / limits["max_storage_gb"]) * 100
        if storage_pct >= 100:
            exceeded.append("storage")
        elif storage_pct >= 80:
            warnings.append(f"Storage at {storage_pct:.1f}% of limit")
    
    # Check bandwidth limit
    if limits.get("max_bandwidth_gb", -1) > 0:
        bandwidth_pct = (summary["bandwidth_gb"] / limits["max_bandwidth_gb"]) * 100
        if bandwidth_pct >= 100:
            exceeded.append("bandwidth")
        elif bandwidth_pct >= 80:
            warnings.append(f"Bandwidth at {bandwidth_pct:.1f}% of limit")
    
    return {
        "user_id": user_id,
        "plan": plan,
        "within_limits": len(exceeded) == 0,
        "exceeded": exceeded,
        "warnings": warnings,
        "summary": summary
    }

def get_org_usage(org_id: str, user_ids: List[str] = None) -> Dict:
    """
    Get aggregated usage metrics for an organization.
    
    Args:
        org_id: Organization unique identifier
        user_ids: Optional list of user IDs in the org
        
    Returns:
        Organization usage dictionary
    """
    if not user_ids:
        user_ids = []
    
    total_api_calls = 0
    total_nodes = 0
    total_compute_hours = 0
    total_storage_gb = 0
    total_bandwidth_gb = 0
    
    for user_id in user_ids:
        if user_id in USAGE_EVENTS:
            events = USAGE_EVENTS[user_id]
            for event in events:
                if event.event_type == EventType.API_CALL:
                    total_api_calls += event.amount
                elif event.event_type == EventType.NODE_ONLINE:
                    total_nodes = max(total_nodes, int(event.amount))
                elif event.event_type == EventType.COMPUTE:
                    total_compute_hours += event.amount
                elif event.event_type == EventType.STORAGE:
                    total_storage_gb += event.amount
                elif event.event_type == EventType.BANDWIDTH:
                    total_bandwidth_gb += event.amount
    
    return {
        "org_id": org_id,
        "total_api_calls": total_api_calls,
        "total_nodes": total_nodes,
        "total_compute_hours": total_compute_hours,
        "total_storage_gb": total_storage_gb,
        "total_bandwidth_gb": total_bandwidth_gb,
        "member_count": len(user_ids),
        "timestamp": datetime.utcnow().isoformat()
    }

def get_usage_trend(user_id: str, days: int = 30) -> List[Dict]:
    """
    Get usage trend over time.
    
    Args:
        user_id: User unique identifier
        days: Number of days to retrieve
        
    Returns:
        List of daily usage dictionaries
    """
    trend = {}
    
    if user_id not in USAGE_EVENTS:
        return []
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    for event in USAGE_EVENTS[user_id]:
        if event.timestamp < cutoff_date:
            continue
        
        date_key = event.timestamp.strftime("%Y-%m-%d")
        if date_key not in trend:
            trend[date_key] = {
                "date": date_key,
                "api_calls": 0,
                "events": 0,
                "compute_hours": 0,
                "storage_gb": 0,
                "bandwidth_gb": 0
            }
        
        trend[date_key]["events"] += 1
        
        if event.event_type == EventType.API_CALL:
            trend[date_key]["api_calls"] += event.amount
        elif event.event_type == EventType.COMPUTE:
            trend[date_key]["compute_hours"] += event.amount
        elif event.event_type == EventType.STORAGE:
            trend[date_key]["storage_gb"] += event.amount
        elif event.event_type == EventType.BANDWIDTH:
            trend[date_key]["bandwidth_gb"] += event.amount
    
    return sorted(trend.values(), key=lambda x: x["date"])

def get_plan_limits(plan: str) -> Dict:
    """
    Get resource limits for a plan.
    
    Args:
        plan: Subscription plan name
        
    Returns:
        Plan limits dictionary
    """
    return PLAN_LIMITS.get(plan, {})

def reset_monthly_usage(user_id: str) -> bool:
    """
    Reset monthly usage counters (called on billing cycle renewal).
    
    Args:
        user_id: User unique identifier
        
    Returns:
        True if successful
    """
    # Archive current month's aggregate
    agg_key = f"{user_id}:{datetime.utcnow().strftime('%Y-%m')}"
    if agg_key in USAGE_AGGREGATES:
        # Keep for history but create new aggregate for next month
        old_aggregate = USAGE_AGGREGATES.pop(agg_key)
    
    return True
