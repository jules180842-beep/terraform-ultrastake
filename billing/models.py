"""
Billing and payments module for the Billing Service.
Handles subscriptions, invoices, charges, and Stripe integration.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum
import uuid

try:
    import stripe
except ImportError:
    stripe = None

# Stripe configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_your_key_here")
if stripe:
    stripe.api_key = STRIPE_SECRET_KEY

class BillingPlan(str, Enum):
    """Available billing plans"""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class PaymentStatus(str, Enum):
    """Payment status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"

# Plan pricing and configuration
PLAN_CONFIG = {
    BillingPlan.FREE: {
        "name": "Free",
        "price": 0,
        "billing_cycle": "monthly",
        "features": ["Basic access", "Community support"],
        "stripe_price_id": None
    },
    BillingPlan.STARTER: {
        "name": "Starter",
        "price": 29,
        "billing_cycle": "monthly",
        "features": ["Up to 5 nodes", "Email support", "Basic monitoring"],
        "stripe_price_id": os.getenv("STRIPE_STARTER_PRICE_ID", "price_starter_id")
    },
    BillingPlan.PRO: {
        "name": "Pro",
        "price": 99,
        "billing_cycle": "monthly",
        "features": ["Up to 50 nodes", "Priority support", "Advanced monitoring", "Custom integrations"],
        "stripe_price_id": os.getenv("STRIPE_PRO_PRICE_ID", "price_pro_id")
    },
    BillingPlan.ENTERPRISE: {
        "name": "Enterprise",
        "price": "custom",
        "billing_cycle": "annual",
        "features": ["Unlimited nodes", "24/7 support", "Custom SLA", "Dedicated account manager"],
        "stripe_price_id": os.getenv("STRIPE_ENTERPRISE_PRICE_ID", "price_enterprise_id")
    }
}

# In-memory databases (in production, use a real database)
SUBSCRIPTIONS = {}
INVOICES = {}
PAYMENTS = {}
CUSTOMERS = {}

class Subscription:
    """Represents a user subscription"""
    
    def __init__(self, user_id: str, plan: str, stripe_subscription_id: str = None):
        self.subscription_id = str(uuid.uuid4())
        self.user_id = user_id
        self.plan = BillingPlan(plan) if isinstance(plan, str) else plan
        self.status = SubscriptionStatus.ACTIVE
        self.stripe_subscription_id = stripe_subscription_id
        self.current_period_start = datetime.utcnow()
        self.current_period_end = datetime.utcnow() + timedelta(days=30)
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.auto_renew = True
        self.metadata = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "subscription_id": self.subscription_id,
            "user_id": self.user_id,
            "plan": self.plan.value,
            "status": self.status.value,
            "current_period_start": self.current_period_start.isoformat(),
            "current_period_end": self.current_period_end.isoformat(),
            "auto_renew": self.auto_renew,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class Invoice:
    """Represents a billing invoice"""
    
    def __init__(self, user_id: str, subscription_id: str, amount: float, plan: str):
        self.invoice_id = str(uuid.uuid4())
        self.user_id = user_id
        self.subscription_id = subscription_id
        self.amount = amount
        self.plan = plan
        self.status = PaymentStatus.PENDING
        self.due_date = datetime.utcnow() + timedelta(days=30)
        self.paid_date = None
        self.created_at = datetime.utcnow()
        self.stripe_invoice_id = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "invoice_id": self.invoice_id,
            "user_id": self.user_id,
            "subscription_id": self.subscription_id,
            "amount": self.amount,
            "plan": self.plan,
            "status": self.status.value,
            "due_date": self.due_date.isoformat(),
            "paid_date": self.paid_date.isoformat() if self.paid_date else None,
            "created_at": self.created_at.isoformat()
        }

class Payment:
    """Represents a payment transaction"""
    
    def __init__(self, user_id: str, amount: float, invoice_id: str = None):
        self.payment_id = str(uuid.uuid4())
        self.user_id = user_id
        self.amount = amount
        self.invoice_id = invoice_id
        self.status = PaymentStatus.PENDING
        self.stripe_payment_id = None
        self.created_at = datetime.utcnow()
        self.completed_at = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "payment_id": self.payment_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "invoice_id": self.invoice_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

def get_plan_info(plan: str) -> Optional[Dict]:
    """
    Get pricing and feature information for a plan.
    
    Args:
        plan: Plan name (free, starter, pro, enterprise)
        
    Returns:
        Plan configuration dictionary
    """
    plan_enum = BillingPlan(plan) if isinstance(plan, str) else plan
    return PLAN_CONFIG.get(plan_enum)

def create_subscription(user_id: str, plan: str) -> Dict:
    """
    Create a new subscription for a user.
    
    Args:
        user_id: User unique identifier
        plan: Plan type (free, starter, pro, enterprise)
        
    Returns:
        Created subscription dictionary
    """
    subscription = Subscription(user_id, plan)
    SUBSCRIPTIONS[subscription.subscription_id] = subscription
    
    return subscription.to_dict()

def get_subscription(subscription_id: str) -> Optional[Dict]:
    """
    Get subscription by ID.
    
    Args:
        subscription_id: Subscription unique identifier
        
    Returns:
        Subscription dictionary if found, None otherwise
    """
    sub = SUBSCRIPTIONS.get(subscription_id)
    return sub.to_dict() if sub else None

def get_user_subscription(user_id: str) -> Optional[Dict]:
    """
    Get active subscription for a user.
    
    Args:
        user_id: User unique identifier
        
    Returns:
        Subscription dictionary if found, None otherwise
    """
    for sub in SUBSCRIPTIONS.values():
        if sub.user_id == user_id and sub.status == SubscriptionStatus.ACTIVE:
            return sub.to_dict()
    return None

def upgrade_plan(subscription_id: str, new_plan: str) -> Optional[Dict]:
    """
    Upgrade a subscription to a higher plan.
    
    Args:
        subscription_id: Subscription unique identifier
        new_plan: New plan type
        
    Returns:
        Updated subscription dictionary if found, None otherwise
    """
    if subscription_id not in SUBSCRIPTIONS:
        return None
    
    sub = SUBSCRIPTIONS[subscription_id]
    sub.plan = BillingPlan(new_plan) if isinstance(new_plan, str) else new_plan
    sub.updated_at = datetime.utcnow()
    
    return sub.to_dict()

def cancel_subscription(subscription_id: str) -> Optional[Dict]:
    """
    Cancel a subscription.
    
    Args:
        subscription_id: Subscription unique identifier
        
    Returns:
        Updated subscription dictionary if found, None otherwise
    """
    if subscription_id not in SUBSCRIPTIONS:
        return None
    
    sub = SUBSCRIPTIONS[subscription_id]
    sub.status = SubscriptionStatus.CANCELLED
    sub.updated_at = datetime.utcnow()
    
    return sub.to_dict()

def create_invoice(user_id: str, subscription_id: str, plan: str) -> Dict:
    """
    Create an invoice for a subscription.
    
    Args:
        user_id: User unique identifier
        subscription_id: Subscription unique identifier
        plan: Plan type
        
    Returns:
        Created invoice dictionary
    """
    plan_info = get_plan_info(plan)
    amount = plan_info["price"] if isinstance(plan_info["price"], (int, float)) else 0
    
    invoice = Invoice(user_id, subscription_id, amount, plan)
    INVOICES[invoice.invoice_id] = invoice
    
    return invoice.to_dict()

def get_invoice(invoice_id: str) -> Optional[Dict]:
    """
    Get invoice by ID.
    
    Args:
        invoice_id: Invoice unique identifier
        
    Returns:
        Invoice dictionary if found, None otherwise
    """
    invoice = INVOICES.get(invoice_id)
    return invoice.to_dict() if invoice else None

def list_user_invoices(user_id: str) -> List[Dict]:
    """
    List all invoices for a user.
    
    Args:
        user_id: User unique identifier
        
    Returns:
        List of invoice dictionaries
    """
    return [inv.to_dict() for inv in INVOICES.values() if inv.user_id == user_id]

def create_checkout_session(user_id: str, email: str, plan: str) -> Optional[Dict]:
    """
    Create a Stripe checkout session for subscription.
    
    Args:
        user_id: User unique identifier
        email: User email for Stripe
        plan: Plan type (starter, pro, enterprise)
        
    Returns:
        Checkout session dictionary with URL
    """
    if not stripe:
        return {"error": "Stripe not configured"}
    
    plan_info = get_plan_info(plan)
    if not plan_info or not plan_info.get("stripe_price_id"):
        return {"error": f"Invalid plan: {plan}"}
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            customer_email=email,
            line_items=[{
                "price": plan_info["stripe_price_id"],
                "quantity": 1
            }],
            success_url=os.getenv("STRIPE_SUCCESS_URL", "https://yourapp.com/billing/success?session_id={CHECKOUT_SESSION_ID}"),
            cancel_url=os.getenv("STRIPE_CANCEL_URL", "https://yourapp.com/billing/cancel")
        )
        
        return {
            "session_id": session.id,
            "url": session.url,
            "user_id": user_id,
            "plan": plan
        }
    except Exception as e:
        return {"error": str(e)}

def process_payment(user_id: str, amount: float, invoice_id: str = None) -> Dict:
    """
    Record a payment.
    
    Args:
        user_id: User unique identifier
        amount: Payment amount
        invoice_id: Associated invoice ID
        
    Returns:
        Payment dictionary
    """
    payment = Payment(user_id, amount, invoice_id)
    payment.status = PaymentStatus.COMPLETED
    payment.completed_at = datetime.utcnow()
    
    PAYMENTS[payment.payment_id] = payment
    
    # Mark invoice as paid
    if invoice_id and invoice_id in INVOICES:
        INVOICES[invoice_id].status = PaymentStatus.COMPLETED
        INVOICES[invoice_id].paid_date = datetime.utcnow()
    
    return payment.to_dict()

def get_usage_metrics(user_id: str) -> Dict:
    """
    Get usage metrics for billing.
    
    Args:
        user_id: User unique identifier
        
    Returns:
        Usage metrics dictionary
    """
    sub = get_user_subscription(user_id)
    invoices = list_user_invoices(user_id)
    
    return {
        "user_id": user_id,
        "current_plan": sub["plan"] if sub else "free",
        "total_invoices": len(invoices),
        "total_paid": sum(inv["amount"] for inv in invoices if inv["status"] == "completed"),
        "pending_amount": sum(inv["amount"] for inv in invoices if inv["status"] == "pending")
    }
