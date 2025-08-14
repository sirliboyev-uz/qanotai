"""
Epic 5: Monetization & Subscriptions API Endpoints
US-5.1: Free Trial Experience
US-5.2: Purchase Additional Tests
US-5.3: Premium Subscription
US-5.4: Payment Management
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
from ..models.subscription_models import (
    UserSubscription,
    TestPackPurchase,
    PaymentRecord,
    UsageQuota,
    SubscriptionPlan,
    SubscriptionTier,
    PaymentStatus,
    TestPackType,
    SubscriptionStatusResponse,
    AvailablePlansResponse,
    PurchaseTestPackRequest,
    SubscribeRequest,
    UpdateSubscriptionRequest,
    PaymentHistoryResponse,
    CancelSubscriptionRequest,
    UsageAnalyticsResponse,
    SUBSCRIPTION_PLANS,
    TEST_PACKS
)
from ..core.auth import get_current_user

router = APIRouter(prefix="/api/subscription", tags=["Monetization & Subscriptions"])

# Mock data stores (replace with actual database in production)
subscriptions_db: Dict[str, UserSubscription] = {}
test_packs_db: List[TestPackPurchase] = []
payments_db: List[PaymentRecord] = []
usage_quotas_db: Dict[str, UsageQuota] = {}

@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(current_user: Dict = Depends(get_current_user)):
    """
    US-5.1: Free Trial Experience
    Get current subscription status and usage quota
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Get or create user subscription
    if user_id not in subscriptions_db:
        subscriptions_db[user_id] = _create_default_subscription(user_id)
    
    subscription = subscriptions_db[user_id]
    
    # Get or create usage quota
    if user_id not in usage_quotas_db:
        usage_quotas_db[user_id] = _create_usage_quota(user_id, subscription.tier)
    
    quota = usage_quotas_db[user_id]
    
    # Update quota if new month
    quota = _update_quota_if_new_period(quota)
    usage_quotas_db[user_id] = quota
    
    # Get current plan details
    current_plan = _get_plan_by_tier(subscription.tier)
    
    # Check if user can take test
    can_take_test = _can_user_take_test(subscription, quota)
    
    # Check if upgrade recommended
    upgrade_recommended = (
        subscription.tier == SubscriptionTier.FREE and 
        quota.tests_remaining_this_period <= 1
    )
    
    return SubscriptionStatusResponse(
        subscription=subscription,
        quota=quota,
        current_plan=current_plan,
        can_take_test=can_take_test,
        upgrade_recommended=upgrade_recommended
    )

@router.get("/plans", response_model=AvailablePlansResponse)
async def get_available_plans(current_user: Dict = Depends(get_current_user)):
    """
    US-5.3: Premium Subscription
    Get available subscription plans and test packs
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Get current subscription tier
    current_tier = SubscriptionTier.FREE
    if user_id in subscriptions_db:
        current_tier = subscriptions_db[user_id].tier
    
    # Convert subscription plans to SubscriptionPlan objects
    plans = [
        SubscriptionPlan(
            id=plan["id"],
            name=plan["name"],
            tier=plan["tier"],
            price_usd=plan["price_usd"],
            billing_period_months=plan["billing_period_months"],
            monthly_test_limit=plan.get("monthly_test_limit"),
            priority_processing=plan.get("priority_processing", False),
            advanced_analytics=plan.get("advanced_analytics", False),
            discount_percentage=plan.get("discount_percentage", 0.0),
            description=plan["description"],
            features=plan.get("features", []),
            is_popular=plan.get("is_popular", False)
        )
        for plan in SUBSCRIPTION_PLANS
    ]
    
    return AvailablePlansResponse(
        plans=plans,
        current_tier=current_tier,
        test_packs=TEST_PACKS
    )

@router.post("/subscribe")
async def subscribe_to_plan(
    request: SubscribeRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    US-5.3: Premium Subscription
    Subscribe to a premium plan
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Find the plan
    plan_data = None
    for plan in SUBSCRIPTION_PLANS:
        if plan["id"] == request.plan_id:
            plan_data = plan
            break
    
    if not plan_data:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Create payment record
    payment = PaymentRecord(
        user_id=user_id,
        amount_usd=plan_data["price_usd"],
        payment_method=request.payment_method,
        item_type="subscription",
        item_id=request.plan_id,
        item_description=f"{plan_data['name']} subscription",
        status=PaymentStatus.COMPLETED  # Mock success
    )
    payments_db.append(payment)
    
    # Create or update subscription
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=30 * plan_data["billing_period_months"])
    
    subscription = UserSubscription(
        user_id=user_id,
        tier=plan_data["tier"],
        start_date=start_date,
        end_date=end_date,
        next_billing_date=end_date,
        monthly_test_limit=plan_data.get("monthly_test_limit"),
        month_reset_date=start_date.replace(day=1) + timedelta(days=32),
        payment_method_id=f"pm_{uuid.uuid4().hex[:10]}",
        last_payment_date=start_date
    )
    
    # Trial handling
    if request.trial_period_days:
        subscription.is_trial = True
        subscription.trial_end_date = start_date + timedelta(days=request.trial_period_days)
    
    subscriptions_db[user_id] = subscription
    
    # Update usage quota
    quota = UsageQuota(
        user_id=user_id,
        period_start=date.today(),
        period_end=(date.today() + timedelta(days=30)),
        subscription_tier=plan_data["tier"],
        is_unlimited=(plan_data.get("monthly_test_limit") is None)
    )
    usage_quotas_db[user_id] = quota
    
    return {
        "message": "Subscription activated successfully",
        "subscription_id": subscription.id,
        "payment_id": payment.id,
        "trial_period": request.trial_period_days
    }

@router.post("/purchase-tests")
async def purchase_test_pack(
    request: PurchaseTestPackRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    US-5.2: Purchase Additional Tests
    Buy a one-time test pack
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Find test pack details
    pack_data = None
    for pack in TEST_PACKS:
        if pack["type"] == request.pack_type:
            pack_data = pack
            break
    
    if not pack_data:
        raise HTTPException(status_code=404, detail="Test pack not found")
    
    # Create payment record
    payment = PaymentRecord(
        user_id=user_id,
        amount_usd=pack_data["price_usd"],
        payment_method=request.payment_method,
        item_type="test_pack",
        item_id=str(request.pack_type),
        item_description=pack_data["description"],
        status=PaymentStatus.COMPLETED  # Mock success
    )
    payments_db.append(payment)
    
    # Create test pack purchase
    test_pack = TestPackPurchase(
        user_id=user_id,
        pack_type=request.pack_type,
        test_count=pack_data["test_count"],
        price_usd=pack_data["price_usd"],
        tests_remaining=pack_data["test_count"],
        payment_id=payment.id,
        payment_status=PaymentStatus.COMPLETED,
        receipt_email=current_user.get("email")
    )
    test_packs_db.append(test_pack)
    
    # Update user's bonus tests
    if user_id in usage_quotas_db:
        usage_quotas_db[user_id].bonus_tests_available += pack_data["test_count"]
    
    return {
        "message": "Test pack purchased successfully",
        "pack_id": test_pack.id,
        "tests_added": pack_data["test_count"],
        "payment_id": payment.id
    }

@router.put("/update")
async def update_subscription(
    request: UpdateSubscriptionRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    US-5.4: Payment Management
    Update subscription settings
    """
    user_id = current_user.get("uid", "unknown_user")
    
    if user_id not in subscriptions_db:
        raise HTTPException(status_code=404, detail="No subscription found")
    
    subscription = subscriptions_db[user_id]
    
    # Handle cancellation
    if request.cancel_at_period_end is not None:
        subscription.cancel_at_period_end = request.cancel_at_period_end
        if request.cancel_at_period_end:
            subscription.cancelled_at = datetime.utcnow()
    
    # Handle plan change
    if request.new_plan_id:
        plan_data = None
        for plan in SUBSCRIPTION_PLANS:
            if plan["id"] == request.new_plan_id:
                plan_data = plan
                break
        
        if plan_data:
            subscription.tier = plan_data["tier"]
            subscription.monthly_test_limit = plan_data.get("monthly_test_limit")
    
    subscription.updated_at = datetime.utcnow()
    subscriptions_db[user_id] = subscription
    
    return {
        "message": "Subscription updated successfully",
        "subscription": subscription
    }

@router.post("/cancel")
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    US-5.4: Payment Management
    Cancel subscription
    """
    user_id = current_user.get("uid", "unknown_user")
    
    if user_id not in subscriptions_db:
        raise HTTPException(status_code=404, detail="No subscription found")
    
    subscription = subscriptions_db[user_id]
    
    if request.immediate:
        # Cancel immediately
        subscription.status = "cancelled"
        subscription.end_date = datetime.utcnow()
    else:
        # Cancel at period end
        subscription.cancel_at_period_end = True
    
    subscription.cancelled_at = datetime.utcnow()
    subscription.cancellation_reason = request.reason
    subscription.updated_at = datetime.utcnow()
    
    subscriptions_db[user_id] = subscription
    
    return {
        "message": "Subscription cancelled successfully",
        "cancelled_immediately": request.immediate,
        "access_until": subscription.end_date
    }

@router.get("/payment-history", response_model=PaymentHistoryResponse)
async def get_payment_history(current_user: Dict = Depends(get_current_user)):
    """
    US-5.4: Payment Management
    Get payment history
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Get user payments
    user_payments = [p for p in payments_db if p.user_id == user_id]
    user_payments.sort(key=lambda x: x.payment_date, reverse=True)
    
    # Calculate total spent
    total_spent = sum(p.amount_usd for p in user_payments if p.status == PaymentStatus.COMPLETED)
    
    # Get next billing date
    next_billing_date = None
    if user_id in subscriptions_db:
        subscription = subscriptions_db[user_id]
        if not subscription.cancel_at_period_end and subscription.status == "active":
            next_billing_date = subscription.next_billing_date
    
    return PaymentHistoryResponse(
        payments=user_payments,
        total_spent=total_spent,
        next_billing_date=next_billing_date
    )

@router.post("/use-test")
async def use_test_attempt(current_user: Dict = Depends(get_current_user)):
    """
    US-5.1: Free Trial Experience
    Deduct a test from user's quota when they start a test
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Get subscription and quota
    subscription = subscriptions_db.get(user_id)
    quota = usage_quotas_db.get(user_id)
    
    if not subscription or not quota:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Check if user can take test
    if not _can_user_take_test(subscription, quota):
        raise HTTPException(
            status_code=403, 
            detail="Test limit reached. Please upgrade or purchase more tests."
        )
    
    # Deduct test
    if subscription.tier == SubscriptionTier.FREE:
        if quota.bonus_tests_available > 0:
            # Use bonus test first
            quota.bonus_tests_available -= 1
        else:
            # Use regular quota
            quota.tests_used_this_period += 1
            quota.tests_remaining_this_period -= 1
    elif subscription.monthly_test_limit is not None:
        # Premium with limit
        subscription.current_month_tests_used += 1
    
    # Check for quota warnings
    if quota.tests_remaining_this_period <= 1 and not quota.quota_warning_sent:
        quota.quota_warning_sent = True
        quota.upgrade_prompt_shown += 1
    
    quota.last_updated = datetime.utcnow()
    
    # Update databases
    subscriptions_db[user_id] = subscription
    usage_quotas_db[user_id] = quota
    
    return {
        "message": "Test started successfully",
        "tests_remaining": quota.tests_remaining_this_period + quota.bonus_tests_available,
        "quota_warning": quota.quota_warning_sent,
        "is_unlimited": subscription.monthly_test_limit is None
    }

@router.get("/usage-analytics", response_model=UsageAnalyticsResponse)
async def get_usage_analytics(current_user: Dict = Depends(get_current_user)):
    """
    Usage analytics and cost savings information
    """
    user_id = current_user.get("uid", "unknown_user")
    
    # Get user data
    subscription = subscriptions_db.get(user_id)
    quota = usage_quotas_db.get(user_id)
    
    if not subscription or not quota:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Calculate current period usage
    current_period = {
        "tests_used": quota.tests_used_this_period,
        "tests_limit": subscription.monthly_test_limit or "Unlimited",
        "bonus_tests": quota.bonus_tests_available,
        "period_start": quota.period_start.isoformat(),
        "period_end": quota.period_end.isoformat()
    }
    
    # Mock historical usage (would come from database)
    historical_usage = [
        {"month": "2024-01", "tests_used": 8},
        {"month": "2024-02", "tests_used": 12},
        {"month": "2024-03", "tests_used": 15}
    ]
    
    # Calculate cost savings for premium users
    cost_savings = {}
    if subscription.tier != SubscriptionTier.FREE:
        total_tests_used = sum(month["tests_used"] for month in historical_usage)
        cost_per_test_pack = 4.99 / 5  # $0.998 per test
        cost_if_paying_per_test = total_tests_used * cost_per_test_pack
        actual_cost = 9.99 * len(historical_usage)  # Monthly subscription cost
        
        cost_savings = {
            "total_tests_used": total_tests_used,
            "cost_if_paying_per_test": round(cost_if_paying_per_test, 2),
            "actual_subscription_cost": round(actual_cost, 2),
            "savings": round(cost_if_paying_per_test - actual_cost, 2)
        }
    
    # Generate recommendations
    recommendations = []
    if subscription.tier == SubscriptionTier.FREE:
        avg_monthly_tests = sum(month["tests_used"] for month in historical_usage) / len(historical_usage)
        if avg_monthly_tests > 5:
            recommendations.append("Consider Premium subscription for unlimited tests")
        elif avg_monthly_tests > 3:
            recommendations.append("Test packs might be more cost-effective than individual purchases")
    else:
        recommendations.append("You're on the best plan for your usage!")
    
    return UsageAnalyticsResponse(
        current_period=current_period,
        historical_usage=historical_usage,
        cost_savings=cost_savings,
        recommendations=recommendations
    )

# Helper functions

def _create_default_subscription(user_id: str) -> UserSubscription:
    """Create default free subscription for new user"""
    start_date = datetime.utcnow()
    return UserSubscription(
        user_id=user_id,
        tier=SubscriptionTier.FREE,
        start_date=start_date,
        month_reset_date=start_date.replace(day=1) + timedelta(days=32)
    )

def _create_usage_quota(user_id: str, tier: SubscriptionTier) -> UsageQuota:
    """Create usage quota for user"""
    today = date.today()
    return UsageQuota(
        user_id=user_id,
        period_start=today,
        period_end=today + timedelta(days=30),
        subscription_tier=tier,
        is_unlimited=(tier != SubscriptionTier.FREE)
    )

def _update_quota_if_new_period(quota: UsageQuota) -> UsageQuota:
    """Reset quota if new period started"""
    today = date.today()
    if today > quota.period_end:
        quota.period_start = today
        quota.period_end = today + timedelta(days=30)
        quota.tests_used_this_period = 0
        quota.tests_remaining_this_period = 3  # Reset to free tier default
        quota.quota_warning_sent = False
        quota.last_updated = datetime.utcnow()
    return quota

def _get_plan_by_tier(tier: SubscriptionTier) -> SubscriptionPlan:
    """Get plan details by tier"""
    for plan in SUBSCRIPTION_PLANS:
        if plan["tier"] == tier:
            return SubscriptionPlan(
                id=plan["id"],
                name=plan["name"],
                tier=plan["tier"],
                price_usd=plan["price_usd"],
                billing_period_months=plan["billing_period_months"],
                description=plan["description"],
                features=plan.get("features", [])
            )
    
    # Default free plan
    return SubscriptionPlan(
        id="free",
        name="Free",
        tier=SubscriptionTier.FREE,
        price_usd=0.0,
        billing_period_months=1,
        description="3 tests per month",
        features=["3 tests per month", "Basic scoring", "Simple feedback"]
    )

def _can_user_take_test(subscription: UserSubscription, quota: UsageQuota) -> bool:
    """Check if user can take a test"""
    # Premium unlimited
    if subscription.tier != SubscriptionTier.FREE and subscription.monthly_test_limit is None:
        return True
    
    # Check regular quota
    if quota.tests_remaining_this_period > 0:
        return True
    
    # Check bonus tests
    if quota.bonus_tests_available > 0:
        return True
    
    # Check premium with limit
    if (subscription.tier != SubscriptionTier.FREE and 
        subscription.monthly_test_limit is not None and
        subscription.current_month_tests_used < subscription.monthly_test_limit):
        return True
    
    return False