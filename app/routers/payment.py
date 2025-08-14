"""
Payment router for Payme integration
"""
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from typing import Dict, Any, Optional
import logging
import os
from datetime import datetime
import uuid
from ..services.payme_service import PaymeService, SUBSCRIPTION_PRICES, convert_to_tiyin
from ..services.supabase_service import supabase_service
from ..core.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payment", tags=["payment"])

# Initialize Payme service
payme_service = PaymeService(
    merchant_id=os.getenv("PAYME_MERCHANT_ID", "test_merchant"),
    secret_key=os.getenv("PAYME_SECRET_KEY", "test_secret"),
    test_mode=os.getenv("PAYME_TEST_MODE", "true").lower() == "true"
)


@router.post("/create-payment")
async def create_payment(
    subscription_plan: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create a Payme payment link for subscription
    
    Args:
        subscription_plan: Plan type (basic, standard, premium, lifetime)
        current_user: Current authenticated user
        
    Returns:
        Payment link and order details
    """
    try:
        # Validate subscription plan
        if subscription_plan not in SUBSCRIPTION_PRICES:
            raise HTTPException(status_code=400, detail="Invalid subscription plan")
        
        # Get price in UZS
        price_uzs = SUBSCRIPTION_PRICES[subscription_plan]
        price_tiyin = convert_to_tiyin(price_uzs)
        
        # Create order ID
        order_id = f"order_{current_user['id']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Save payment record to database
        payment_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "order_id": order_id,
            "subscription_plan": subscription_plan,
            "amount_uzs": price_uzs,
            "amount_tiyin": price_tiyin,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Save to Supabase payments table
        await supabase_service.create_payment(payment_data)
        
        # Generate Payme payment link
        payment_url = payme_service.generate_pay_link(
            amount=price_tiyin,
            order_id=order_id,
            user_id=current_user["id"],
            return_url="qanotai://payment-success"  # Deep link back to app
        )
        
        return {
            "payment_url": payment_url,
            "order_id": order_id,
            "amount_uzs": price_uzs,
            "subscription_plan": subscription_plan,
            "message": "Payment link created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payme-webhook")
async def payme_webhook(
    request: Request,
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Handle Payme webhook callbacks
    
    This endpoint processes payment notifications from Payme
    """
    try:
        # Get request body
        body = await request.json()
        
        # Verify signature
        if authorization:
            if not payme_service.verify_signature(
                request_body=await request.body(),
                signature=authorization
            ):
                logger.warning("Invalid Payme signature")
                return {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {
                        "code": -32504,
                        "message": "Unauthorized"
                    }
                }
        
        # Process webhook
        response = payme_service.process_webhook(body)
        
        # Update database based on method
        method = body.get("method")
        params = body.get("params", {})
        
        if method == "PerformTransaction":
            # Transaction completed - activate subscription
            transaction_id = params.get("id")
            account = params.get("account", {})
            order_id = account.get("order_id")
            user_id = account.get("user_id")
            
            # Update payment status
            await supabase_service.update_payment_status(
                order_id=order_id,
                status="completed",
                transaction_id=transaction_id
            )
            
            # Activate subscription
            payment = await supabase_service.get_payment_by_order_id(order_id)
            if payment:
                await supabase_service.activate_subscription(
                    user_id=user_id,
                    plan_name=payment["subscription_plan"]
                )
                
                logger.info(f"Subscription activated for user {user_id}")
        
        elif method == "CancelTransaction":
            # Transaction cancelled
            transaction_id = params.get("id")
            await supabase_service.update_payment_status_by_transaction(
                transaction_id=transaction_id,
                status="cancelled"
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": "Internal server error"
            }
        }


@router.get("/check-payment/{order_id}")
async def check_payment_status(
    order_id: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Check payment status by order ID
    
    Args:
        order_id: Order ID to check
        current_user: Current authenticated user
        
    Returns:
        Payment status and details
    """
    try:
        # Get payment from database
        payment = await supabase_service.get_payment_by_order_id(order_id)
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Verify payment belongs to user
        if payment["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "order_id": order_id,
            "status": payment["status"],
            "amount_uzs": payment["amount_uzs"],
            "subscription_plan": payment["subscription_plan"],
            "created_at": payment["created_at"],
            "completed_at": payment.get("completed_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payment-history")
async def get_payment_history(
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get user's payment history
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of user's payments
    """
    try:
        payments = await supabase_service.get_user_payments(current_user["id"])
        
        return {
            "payments": payments,
            "total": len(payments)
        }
        
    except Exception as e:
        logger.error(f"Error getting payment history: {e}")
        raise HTTPException(status_code=500, detail=str(e))