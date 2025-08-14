"""
Update subscription prices for Uzbek market
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

def update_subscription_prices():
    """Update subscription prices to UZS for Uzbek market"""
    
    print("🔄 Updating subscription prices for Uzbek market...")
    
    # Update each plan with UZS prices
    plans = [
        {
            "name": "basic",
            "price_usd": 2.5,  # Approximate USD equivalent
            "price_uzs": 29000,
            "display_name": "Basic",
            "display_name_uz": "Oddiy",
            "description": "Perfect for beginners - 50 tests per month",
            "description_uz": "Boshlovchilar uchun - oyiga 50 ta test",
        },
        {
            "name": "standard",
            "price_usd": 4.0,
            "price_uzs": 49000,
            "display_name": "Standard",
            "display_name_uz": "Standart",
            "description": "Most popular - 200 tests per month",
            "description_uz": "Eng mashhur - oyiga 200 ta test",
        },
        {
            "name": "premium",
            "price_usd": 6.5,
            "price_uzs": 79000,
            "display_name": "Premium",
            "display_name_uz": "Premium",
            "description": "Unlimited tests with all features",
            "description_uz": "Cheksiz testlar va barcha imkoniyatlar",
        },
        {
            "name": "lifetime",
            "price_usd": 80.0,
            "price_uzs": 990000,
            "display_name": "Lifetime",
            "display_name_uz": "Umrbod",
            "description": "One-time payment, unlimited forever",
            "description_uz": "Bir martalik to'lov, abadiy cheksiz",
        }
    ]
    
    for plan in plans:
        try:
            # Update existing plan
            result = supabase.table("subscription_plans").update({
                "price_uzs": plan["price_uzs"],
                "display_name_uz": plan.get("display_name_uz"),
                "description_uz": plan.get("description_uz"),
                "metadata": {
                    "currency": "UZS",
                    "market": "uzbekistan",
                    "price_display": f"{plan['price_uzs']:,} so'm"
                }
            }).eq("name", plan["name"]).execute()
            
            if result.data:
                print(f"✅ Updated {plan['name']}: {plan['price_uzs']:,} UZS")
            else:
                print(f"⚠️  Plan {plan['name']} not found")
        except Exception as e:
            print(f"❌ Error updating {plan['name']}: {e}")
    
    print("\n💰 Subscription prices updated for Uzbek market!")
    print("\nCurrent pricing:")
    print("  Basic:    29,000 so'm/oy")
    print("  Standard: 49,000 so'm/oy")
    print("  Premium:  79,000 so'm/oy")
    print("  Lifetime: 990,000 so'm")

if __name__ == "__main__":
    update_subscription_prices()