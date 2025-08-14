"""
Payme payment integration service for Uzbekistan
"""
import hashlib
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import requests
from decimal import Decimal

logger = logging.getLogger(__name__)


class PaymeService:
    """Service for handling Payme payment integration"""
    
    def __init__(self, merchant_id: str, secret_key: str, test_mode: bool = True):
        """
        Initialize Payme service
        
        Args:
            merchant_id: Payme merchant ID
            secret_key: Payme secret key for signature verification
            test_mode: Use test endpoint if True
        """
        self.merchant_id = merchant_id
        self.secret_key = secret_key
        self.test_mode = test_mode
        
        # Payme endpoints
        if test_mode:
            self.api_url = "https://checkout.test.paycom.uz/api"
            self.checkout_url = "https://checkout.test.paycom.uz"
        else:
            self.api_url = "https://checkout.paycom.uz/api"
            self.checkout_url = "https://checkout.paycom.uz"
    
    def generate_pay_link(
        self,
        amount: int,
        order_id: str,
        user_id: str,
        return_url: Optional[str] = None
    ) -> str:
        """
        Generate Payme payment link
        
        Args:
            amount: Amount in tiyin (UZS cents)
            order_id: Unique order ID
            user_id: User ID
            return_url: URL to return after payment
            
        Returns:
            Payment URL
        """
        # Create payment parameters
        params = {
            "m": self.merchant_id,
            "ac.order_id": order_id,
            "ac.user_id": user_id,
            "a": amount,  # Amount in tiyin
            "l": "uz",  # Language (uz, ru, en)
        }
        
        if return_url:
            params["c"] = return_url
        
        # Encode parameters
        import base64
        params_str = ";".join([f"{k}={v}" for k, v in params.items()])
        encoded_params = base64.b64encode(params_str.encode()).decode()
        
        # Generate payment link
        payment_url = f"{self.checkout_url}/{encoded_params}"
        
        logger.info(f"Generated Payme payment link for order {order_id}")
        return payment_url
    
    def verify_signature(self, request_body: str, signature: str) -> bool:
        """
        Verify Payme webhook signature
        
        Args:
            request_body: Raw request body
            signature: Signature from Authorization header
            
        Returns:
            True if signature is valid
        """
        # Extract basic auth from signature
        if not signature.startswith("Basic "):
            return False
        
        import base64
        try:
            decoded = base64.b64decode(signature[6:]).decode()
            username, password = decoded.split(":")
            
            # Username should be "Paycom"
            if username != "Paycom":
                return False
            
            # Password should match secret key
            return password == self.secret_key
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def handle_check_perform_transaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle CheckPerformTransaction method
        Check if transaction can be performed
        
        Args:
            params: Request parameters
            
        Returns:
            Response dictionary
        """
        try:
            amount = params.get("amount")
            account = params.get("account", {})
            order_id = account.get("order_id")
            user_id = account.get("user_id")
            
            # Validate order exists and amount is correct
            # TODO: Check with database
            
            # For now, return success
            return {
                "result": {
                    "allow": True
                }
            }
        except Exception as e:
            logger.error(f"CheckPerformTransaction error: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": "Internal server error"
                }
            }
    
    def handle_create_transaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle CreateTransaction method
        Create a new transaction
        
        Args:
            params: Request parameters
            
        Returns:
            Response dictionary
        """
        try:
            transaction_id = params.get("id")
            time_ms = params.get("time")
            amount = params.get("amount")
            account = params.get("account", {})
            order_id = account.get("order_id")
            user_id = account.get("user_id")
            
            # Save transaction to database
            # TODO: Save to database
            
            # Return success response
            return {
                "result": {
                    "create_time": time_ms,
                    "transaction": str(transaction_id),
                    "state": 1  # Created
                }
            }
        except Exception as e:
            logger.error(f"CreateTransaction error: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": "Internal server error"
                }
            }
    
    def handle_perform_transaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle PerformTransaction method
        Confirm and complete transaction
        
        Args:
            params: Request parameters
            
        Returns:
            Response dictionary
        """
        try:
            transaction_id = params.get("id")
            
            # Mark transaction as completed
            # TODO: Update database
            
            perform_time = int(time.time() * 1000)
            
            return {
                "result": {
                    "transaction": str(transaction_id),
                    "perform_time": perform_time,
                    "state": 2  # Completed
                }
            }
        except Exception as e:
            logger.error(f"PerformTransaction error: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": "Internal server error"
                }
            }
    
    def handle_cancel_transaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle CancelTransaction method
        Cancel a transaction
        
        Args:
            params: Request parameters
            
        Returns:
            Response dictionary
        """
        try:
            transaction_id = params.get("id")
            reason = params.get("reason")
            
            # Cancel transaction in database
            # TODO: Update database
            
            cancel_time = int(time.time() * 1000)
            
            return {
                "result": {
                    "transaction": str(transaction_id),
                    "cancel_time": cancel_time,
                    "state": -1  # Cancelled
                }
            }
        except Exception as e:
            logger.error(f"CancelTransaction error: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": "Internal server error"
                }
            }
    
    def handle_check_transaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle CheckTransaction method
        Check transaction status
        
        Args:
            params: Request parameters
            
        Returns:
            Response dictionary
        """
        try:
            transaction_id = params.get("id")
            
            # Get transaction from database
            # TODO: Query database
            
            # For now, return mock data
            return {
                "result": {
                    "create_time": int(time.time() * 1000),
                    "perform_time": 0,
                    "cancel_time": 0,
                    "transaction": str(transaction_id),
                    "state": 1,
                    "reason": None
                }
            }
        except Exception as e:
            logger.error(f"CheckTransaction error: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": "Internal server error"
                }
            }
    
    def handle_get_statement(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle GetStatement method
        Get transactions list for period
        
        Args:
            params: Request parameters
            
        Returns:
            Response dictionary
        """
        try:
            from_time = params.get("from")
            to_time = params.get("to")
            
            # Get transactions from database
            # TODO: Query database
            
            return {
                "result": {
                    "transactions": []
                }
            }
        except Exception as e:
            logger.error(f"GetStatement error: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": "Internal server error"
                }
            }
    
    def process_webhook(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Payme webhook request
        
        Args:
            request_body: JSON-RPC request body
            
        Returns:
            JSON-RPC response
        """
        method = request_body.get("method")
        params = request_body.get("params", {})
        request_id = request_body.get("id")
        
        # Method handlers
        handlers = {
            "CheckPerformTransaction": self.handle_check_perform_transaction,
            "CreateTransaction": self.handle_create_transaction,
            "PerformTransaction": self.handle_perform_transaction,
            "CancelTransaction": self.handle_cancel_transaction,
            "CheckTransaction": self.handle_check_transaction,
            "GetStatement": self.handle_get_statement,
        }
        
        if method not in handlers:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": "Method not found"
                }
            }
        
        # Handle the method
        result = handlers[method](params)
        
        # Format response
        response = {
            "jsonrpc": "2.0",
            "id": request_id
        }
        
        if "error" in result:
            response["error"] = result["error"]
        else:
            response["result"] = result["result"]
        
        return response


# Subscription prices in UZS
SUBSCRIPTION_PRICES = {
    "basic": 29000,      # 29,000 UZS/month
    "standard": 49000,   # 49,000 UZS/month
    "premium": 79000,    # 79,000 UZS/month
    "lifetime": 990000   # 990,000 UZS one-time
}

def convert_to_tiyin(amount_uzs: int) -> int:
    """Convert UZS to tiyin (1 UZS = 100 tiyin)"""
    return amount_uzs * 100