"""
Supabase configuration and client initialization
"""
import os
from supabase import create_client, Client
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Supabase credentials (replace with your actual credentials)
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "your-anon-key")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "your-service-key")

# Initialize Supabase client
def get_supabase_client(use_service_key: bool = False) -> Optional[Client]:
    """
    Get Supabase client instance
    Args:
        use_service_key: Use service key for admin operations
    """
    try:
        key = SUPABASE_SERVICE_KEY if use_service_key else SUPABASE_ANON_KEY
        client = create_client(SUPABASE_URL, key)
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return None

# Get default client instance
supabase: Optional[Client] = get_supabase_client()

# Get admin client instance
supabase_admin: Optional[Client] = get_supabase_client(use_service_key=True)