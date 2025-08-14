"""
Models for Epic 5: Monetization & Subscriptions
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
import uuid


class SubscriptionTier(str, Enum):
    """Subscription tier types"""
    FREE = "free"
    PREMIUM_MONTHLY = "premium_monthly"
    PREMIUM_ANNUAL = "premium_annual"


class PaymentStatus(str, Enum):
    """Payment status types"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class TestPackType(str, Enum):
    """Test pack types for one-time purchases"""
    PACK_5 = "pack_5"
    PACK_10 = "pack_10"
    PACK_20 = "pack_20"


class UserSubscription(BaseModel):
    """US-5.3: Premium Subscription model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # Subscription details
    tier: SubscriptionTier = SubscriptionTier.FREE
    status: str = "active"  # active, cancelled, expired, trial
    
    # Billing cycle
    start_date: datetime
    end_date: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None
    
    # Trial information
    is_trial: bool = False
    trial_end_date: Optional[datetime] = None
    
    # Features and limits
    monthly_test_limit: Optional[int] = 3  # Free tier default, None = unlimited
    current_month_tests_used: int = 0
    month_reset_date: datetime
    
    # Payment info
    payment_method_id: Optional[str] = None
    last_payment_date: Optional[datetime] = None
    
    # Cancellation
    cancel_at_period_end: bool = False
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TestPackPurchase(BaseModel):
    """US-5.2: Purchase Additional Tests model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # Purchase details
    pack_type: TestPackType
    test_count: int  # Number of tests in pack
    price_usd: float
    
    # Usage tracking
    tests_remaining: int
    tests_used: int = 0
    
    # Purchase info
    purchase_date: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # None = never expires
    
    # Payment
    payment_id: str
    payment_status: PaymentStatus = PaymentStatus.PENDING
    
    # Receipt
    receipt_email: Optional[str] = None
    receipt_sent: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PaymentRecord(BaseModel):
    """Payment transaction record"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # Payment details
    amount_usd: float
    currency: str = "USD"
    payment_method: str  # "apple_pay", "google_pay", "stripe", etc.
    
    # Transaction info
    external_transaction_id: Optional[str] = None  # From payment provider
    status: PaymentStatus = PaymentStatus.PENDING
    
    # What was purchased
    item_type: str  # "subscription", "test_pack"
    item_id: str  # subscription_id or test_pack_id
    item_description: str
    
    # Timestamps
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    
    # Receipt and billing
    receipt_url: Optional[str] = None
    invoice_id: Optional[str] = None
    
    # Failure info
    failure_reason: Optional[str] = None
    failure_code: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UsageQuota(BaseModel):
    """US-5.1: Free Trial Experience - Usage tracking"""
    user_id: str
    
    # Current period
    period_start: date
    period_end: date
    
    # Test usage
    tests_used_this_period: int = 0
    tests_remaining_this_period: int = 3  # Free tier default
    
    # Additional purchased tests
    bonus_tests_available: int = 0  # From test packs
    
    # Subscription status
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    is_unlimited: bool = False  # Premium users
    
    # Warnings and notifications
    quota_warning_sent: bool = False
    quota_exceeded: bool = False
    upgrade_prompt_shown: int = 0
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class SubscriptionPlan(BaseModel):
    """Available subscription plans"""
    id: str
    name: str
    tier: SubscriptionTier
    
    # Pricing
    price_usd: float
    billing_period_months: int  # 1 for monthly, 12 for annual
    
    # Features
    monthly_test_limit: Optional[int] = None  # None = unlimited
    priority_processing: bool = False
    advanced_analytics: bool = False
    
    # Discounts
    discount_percentage: float = 0.0
    promotional_price: Optional[float] = None
    
    # Display
    description: str
    features: List[str] = []
    is_popular: bool = False
    is_available: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Request/Response models for API endpoints

class SubscriptionStatusResponse(BaseModel):
    """Response for subscription status"""
    subscription: UserSubscription
    quota: UsageQuota
    current_plan: SubscriptionPlan
    can_take_test: bool
    upgrade_recommended: bool


class AvailablePlansResponse(BaseModel):
    """Response for available subscription plans"""
    plans: List[SubscriptionPlan]
    current_tier: SubscriptionTier
    test_packs: List[Dict[str, Any]]


class PurchaseTestPackRequest(BaseModel):
    """Request to purchase test pack"""
    pack_type: TestPackType
    payment_method: str  # "apple_pay", "google_pay"
    payment_token: Optional[str] = None


class SubscribeRequest(BaseModel):
    """Request to start subscription"""
    plan_id: str
    payment_method: str
    payment_token: Optional[str] = None
    trial_period_days: Optional[int] = None


class UpdateSubscriptionRequest(BaseModel):
    """Request to update subscription"""
    cancel_at_period_end: Optional[bool] = None
    new_plan_id: Optional[str] = None


class PaymentHistoryResponse(BaseModel):
    """Response for payment history"""
    payments: List[PaymentRecord]
    total_spent: float
    next_billing_date: Optional[datetime]


class CancelSubscriptionRequest(BaseModel):
    """Request to cancel subscription"""
    reason: Optional[str] = None
    feedback: Optional[str] = None
    immediate: bool = False  # True = cancel now, False = cancel at period end


class UsageAnalyticsResponse(BaseModel):
    """Response for usage analytics"""
    current_period: Dict[str, Any]
    historical_usage: List[Dict[str, Any]]
    cost_savings: Dict[str, float]
    recommendations: List[str]


# Webhook models for payment providers

class PaymentWebhookEvent(BaseModel):
    """Payment webhook event from external providers"""
    provider: str  # "stripe", "apple", "google"
    event_type: str  # "payment.succeeded", "subscription.cancelled", etc.
    external_id: str
    data: Dict[str, Any]
    processed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Mock pricing configuration

SUBSCRIPTION_PLANS = [
    {
        "id": "premium_monthly",
        "name": "Premium Monthly",
        "tier": SubscriptionTier.PREMIUM_MONTHLY,
        "price_usd": 9.99,
        "billing_period_months": 1,
        "monthly_test_limit": None,  # Unlimited
        "priority_processing": True,
        "advanced_analytics": True,
        "description": "Unlimited tests with premium features",
        "features": [
            "Unlimited IELTS speaking tests",
            "Priority AI processing",
            "Advanced performance analytics",
            "Detailed improvement insights",
            "Email support"
        ],
        "is_popular": False
    },
    {
        "id": "premium_annual",
        "name": "Premium Annual",
        "tier": SubscriptionTier.PREMIUM_ANNUAL,
        "price_usd": 79.99,
        "billing_period_months": 12,
        "monthly_test_limit": None,  # Unlimited
        "priority_processing": True,
        "advanced_analytics": True,
        "discount_percentage": 33.0,  # 33% off monthly price
        "description": "Best value - Save 33% with annual billing",
        "features": [
            "Everything in Premium Monthly",
            "Save $40+ per year",
            "Priority customer support",
            "Early access to new features"
        ],
        "is_popular": True
    }
]

TEST_PACKS = [
    {
        "type": TestPackType.PACK_5,
        "test_count": 5,
        "price_usd": 4.99,
        "description": "5 additional tests",
        "best_for": "Quick practice boost"
    },
    {
        "type": TestPackType.PACK_10,
        "test_count": 10,
        "price_usd": 8.99,
        "description": "10 additional tests",
        "best_for": "Extended practice",
        "discount": "Save 10%"
    },
    {
        "type": TestPackType.PACK_20,
        "test_count": 20,
        "price_usd": 15.99,
        "description": "20 additional tests",
        "best_for": "Intensive preparation",
        "discount": "Save 20%",
        "popular": True
    }
]