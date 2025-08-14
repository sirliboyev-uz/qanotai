"""
Supabase service for database operations
"""
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from uuid import uuid4
import logging
from supabase import Client
from ..core.supabase_config import supabase, supabase_admin

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service class for Supabase database operations"""
    
    def __init__(self, client: Optional[Client] = None):
        self.client = client or supabase
        
    # =====================================================
    # USER OPERATIONS
    # =====================================================
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new user in the database"""
        try:
            # Insert into users table
            result = self.client.table("users").insert({
                "id": user_data.get("id", str(uuid4())),
                "phone_number": user_data.get("phone_number"),
                "email": user_data.get("email"),
                "display_name": user_data.get("display_name"),
                "photo_url": user_data.get("photo_url"),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).execute()
            
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    async def get_user_by_phone(self, phone_number: str) -> Optional[Dict]:
        """Get user by phone number"""
        try:
            result = self.client.table("users").select("*").eq("phone_number", phone_number).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting user by phone: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            result = self.client.table("users").select("*").eq("email", email).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            result = self.client.table("users").select("*").eq("id", user_id).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict]:
        """Update user information"""
        try:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            result = self.client.table("users").update(update_data).eq("id", user_id).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None
    
    # =====================================================
    # SUBSCRIPTION OPERATIONS
    # =====================================================
    
    async def get_user_subscription(self, user_id: str) -> Optional[Dict]:
        """Get user's current subscription"""
        try:
            result = self.client.table("user_subscriptions").select(
                "*, subscription_plans(*)"
            ).eq("user_id", user_id).eq("status", "active").execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting subscription: {e}")
            return None
    
    async def create_subscription(self, subscription_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new subscription"""
        try:
            result = self.client.table("user_subscriptions").insert(subscription_data).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return None
    
    async def get_subscription_plans(self) -> List[Dict]:
        """Get all available subscription plans"""
        try:
            result = self.client.table("subscription_plans").select("*").eq("is_active", True).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting subscription plans: {e}")
            return []
    
    # =====================================================
    # USAGE QUOTA OPERATIONS
    # =====================================================
    
    async def get_usage_quota(self, user_id: str) -> Optional[Dict]:
        """Get user's current usage quota"""
        try:
            today = datetime.utcnow().date()
            result = self.client.table("usage_quotas").select("*").eq(
                "user_id", user_id
            ).gte("period_end", today.isoformat()).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            # Create new quota if none exists
            return await self.create_usage_quota(user_id)
        except Exception as e:
            logger.error(f"Error getting usage quota: {e}")
            return None
    
    async def create_usage_quota(self, user_id: str) -> Optional[Dict]:
        """Create usage quota for user"""
        try:
            today = datetime.utcnow().date()
            period_end = today + timedelta(days=30)
            
            quota_data = {
                "user_id": user_id,
                "period_start": today.isoformat(),
                "period_end": period_end.isoformat(),
                "tests_used": 0,
                "tests_limit": 3,  # Free tier default
                "bonus_tests": 0
            }
            
            result = self.client.table("usage_quotas").insert(quota_data).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error creating usage quota: {e}")
            return None
    
    async def increment_test_usage(self, user_id: str) -> bool:
        """Increment test usage count"""
        try:
            quota = await self.get_usage_quota(user_id)
            if not quota:
                return False
            
            # Check if user can take test
            total_available = quota["tests_limit"] - quota["tests_used"] + quota["bonus_tests"]
            if total_available <= 0:
                return False
            
            # Use bonus test first
            if quota["bonus_tests"] > 0:
                result = self.client.table("usage_quotas").update({
                    "bonus_tests": quota["bonus_tests"] - 1,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", quota["id"]).execute()
            else:
                result = self.client.table("usage_quotas").update({
                    "tests_used": quota["tests_used"] + 1,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", quota["id"]).execute()
            
            return result.data is not None
        except Exception as e:
            logger.error(f"Error incrementing test usage: {e}")
            return False
    
    # =====================================================
    # TEST ATTEMPT OPERATIONS
    # =====================================================
    
    async def create_test_attempt(self, attempt_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new test attempt"""
        try:
            result = self.client.table("test_attempts").insert(attempt_data).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error creating test attempt: {e}")
            return None
    
    async def update_test_attempt(self, attempt_id: str, update_data: Dict[str, Any]) -> Optional[Dict]:
        """Update test attempt"""
        try:
            result = self.client.table("test_attempts").update(update_data).eq("id", attempt_id).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error updating test attempt: {e}")
            return None
    
    async def get_user_test_attempts(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get user's test attempts"""
        try:
            result = self.client.table("test_attempts").select("*").eq(
                "user_id", user_id
            ).order("test_date", desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting test attempts: {e}")
            return []
    
    # =====================================================
    # PROGRESS OPERATIONS
    # =====================================================
    
    async def get_user_progress(self, user_id: str, days: int = 30) -> List[Dict]:
        """Get user's progress data"""
        try:
            start_date = (datetime.utcnow() - timedelta(days=days)).date()
            result = self.client.table("user_progress").select("*").eq(
                "user_id", user_id
            ).gte("date", start_date.isoformat()).order("date", desc=False).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting user progress: {e}")
            return []
    
    async def update_daily_progress(self, user_id: str, progress_data: Dict[str, Any]) -> Optional[Dict]:
        """Update or create daily progress"""
        try:
            today = datetime.utcnow().date()
            
            # Check if progress exists for today
            existing = self.client.table("user_progress").select("*").eq(
                "user_id", user_id
            ).eq("date", today.isoformat()).execute()
            
            if existing.data and len(existing.data) > 0:
                # Update existing
                result = self.client.table("user_progress").update(progress_data).eq(
                    "id", existing.data[0]["id"]
                ).execute()
            else:
                # Create new
                progress_data["user_id"] = user_id
                progress_data["date"] = today.isoformat()
                result = self.client.table("user_progress").insert(progress_data).execute()
            
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error updating daily progress: {e}")
            return None
    
    # =====================================================
    # CONTENT OPERATIONS
    # =====================================================
    
    async def get_questions(self, filters: Dict[str, Any] = None, limit: int = 20) -> List[Dict]:
        """Get questions with optional filters"""
        try:
            query = self.client.table("questions").select("*, question_topics(*)")
            
            if filters:
                if "part" in filters:
                    query = query.eq("part", filters["part"])
                if "difficulty" in filters:
                    query = query.eq("difficulty", filters["difficulty"])
                if "topic_id" in filters:
                    query = query.eq("topic_id", filters["topic_id"])
            
            query = query.eq("is_active", True).limit(limit)
            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting questions: {e}")
            return []
    
    async def get_topics(self, category: Optional[str] = None) -> List[Dict]:
        """Get question topics"""
        try:
            query = self.client.table("question_topics").select("*").eq("is_active", True)
            
            if category:
                query = query.eq("category", category)
            
            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting topics: {e}")
            return []
    
    async def get_daily_challenge(self, date: Optional[datetime] = None) -> Optional[Dict]:
        """Get daily challenge"""
        try:
            challenge_date = date or datetime.utcnow().date()
            result = self.client.table("daily_challenges").select("*").eq(
                "challenge_date", challenge_date.isoformat()
            ).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting daily challenge: {e}")
            return None
    
    # =====================================================
    # PAYMENT OPERATIONS
    # =====================================================
    
    async def create_payment(self, payment_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new payment record"""
        try:
            result = self.client.table("payments").insert(payment_data).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error creating payment: {e}")
            return None
    
    async def get_payment_by_order_id(self, order_id: str) -> Optional[Dict]:
        """Get payment by order ID"""
        try:
            result = self.client.table("payments").select("*").eq("order_id", order_id).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting payment: {e}")
            return None
    
    async def update_payment_status(self, order_id: str, status: str, transaction_id: Optional[str] = None) -> bool:
        """Update payment status"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            if transaction_id:
                update_data["transaction_id"] = transaction_id
            if status == "completed":
                update_data["completed_at"] = datetime.utcnow().isoformat()
            
            result = self.client.table("payments").update(update_data).eq("order_id", order_id).execute()
            return result.data is not None
        except Exception as e:
            logger.error(f"Error updating payment status: {e}")
            return False
    
    async def update_payment_status_by_transaction(self, transaction_id: str, status: str) -> bool:
        """Update payment status by transaction ID"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("payments").update(update_data).eq("transaction_id", transaction_id).execute()
            return result.data is not None
        except Exception as e:
            logger.error(f"Error updating payment status: {e}")
            return False
    
    async def get_user_payments(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user's payment history"""
        try:
            result = self.client.table("payments").select("*").eq(
                "user_id", user_id
            ).order("created_at", desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting user payments: {e}")
            return []
    
    async def activate_subscription(self, user_id: str, plan_name: str) -> bool:
        """Activate user subscription after successful payment"""
        try:
            # Get subscription plan details
            plan = self.client.table("subscription_plans").select("*").eq("name", plan_name).execute()
            if not plan.data:
                logger.error(f"Subscription plan {plan_name} not found")
                return False
            
            plan_data = plan.data[0]
            
            # Calculate subscription dates
            start_date = datetime.utcnow()
            if plan_name == "lifetime":
                # Lifetime subscription - 100 years
                end_date = start_date + timedelta(days=36500)
            else:
                # Monthly subscription
                end_date = start_date + timedelta(days=30)
            
            # Create or update subscription
            subscription_data = {
                "user_id": user_id,
                "plan_id": plan_data["id"],
                "status": "active",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "auto_renew": False,  # Manual renewal for Payme
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Check if user has existing subscription
            existing = self.client.table("user_subscriptions").select("*").eq(
                "user_id", user_id
            ).eq("status", "active").execute()
            
            if existing.data:
                # Update existing subscription
                result = self.client.table("user_subscriptions").update({
                    "plan_id": plan_data["id"],
                    "end_date": end_date.isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", existing.data[0]["id"]).execute()
            else:
                # Create new subscription
                subscription_data["id"] = str(uuid4())
                result = self.client.table("user_subscriptions").insert(subscription_data).execute()
            
            # Update usage quota based on plan
            await self.update_usage_quota_for_plan(user_id, plan_name)
            
            return result.data is not None
        except Exception as e:
            logger.error(f"Error activating subscription: {e}")
            return False
    
    async def update_usage_quota_for_plan(self, user_id: str, plan_name: str) -> bool:
        """Update usage quota based on subscription plan"""
        try:
            # Define test limits per plan
            plan_limits = {
                "basic": 50,
                "standard": 200,
                "premium": -1,  # Unlimited
                "lifetime": -1  # Unlimited
            }
            
            test_limit = plan_limits.get(plan_name, 3)  # Default to free tier
            
            # Get or create current quota
            quota = await self.get_usage_quota(user_id)
            if quota:
                # Update existing quota
                result = self.client.table("usage_quotas").update({
                    "tests_limit": test_limit,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", quota["id"]).execute()
                return result.data is not None
            
            return False
        except Exception as e:
            logger.error(f"Error updating usage quota: {e}")
            return False
    
    # =====================================================
    # LEADERBOARD OPERATIONS
    # =====================================================
    
    async def get_leaderboard(self, period: str = "weekly", limit: int = 50) -> List[Dict]:
        """Get leaderboard data"""
        try:
            result = self.client.table("leaderboard").select(
                "*, users(display_name, photo_url)"
            ).eq("period", period).order("score", desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    async def update_leaderboard_score(self, user_id: str, score: float, period: str = "weekly") -> bool:
        """Update user's leaderboard score"""
        try:
            # Check if entry exists
            existing = self.client.table("leaderboard").select("*").eq(
                "user_id", user_id
            ).eq("period", period).execute()
            
            if existing.data and len(existing.data) > 0:
                # Update existing
                result = self.client.table("leaderboard").update({
                    "score": score,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", existing.data[0]["id"]).execute()
            else:
                # Create new
                result = self.client.table("leaderboard").insert({
                    "user_id": user_id,
                    "period": period,
                    "score": score
                }).execute()
            
            return result.data is not None
        except Exception as e:
            logger.error(f"Error updating leaderboard: {e}")
            return False


# Create a singleton instance
supabase_service = SupabaseService()