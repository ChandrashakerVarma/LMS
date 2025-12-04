from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.subscription_plans_m import SubscriptionPlan


def seed_subscription_plans():
    """
    ✅ Seed default subscription plans
    - Basic (Free trial)
    - Standard (Growing businesses)
    - Premium (Established companies)
    - Enterprise (Large organizations)
    """
    
    plans = [
        {
            "name": "Basic",
            "description": "Perfect for startups and small teams - Free 30-day trial",
            "price_monthly": 0,
            "price_yearly": 0,
            "branch_limit": 2,
            "user_limit": 10,
            "storage_limit_mb": 1000,  # 1GB
            "has_analytics": False,
            "has_api_access": False,
            "has_priority_support": False,
            "has_whatsapp_notifications": False,
            "has_custom_branding": False,
            "is_active": True,
            "display_order": 1,
            "created_by": "System",
            "modified_by": "System"
        },
        {
            "name": "Standard",
            "description": "For growing businesses with multiple branches",
            "price_monthly": 5000,
            "price_yearly": 50000,  # ₹50,000/year (Save ₹10,000 - 2 months free)
            "branch_limit": 5,
            "user_limit": 50,
            "storage_limit_mb": 5000,  # 5GB
            "has_analytics": True,
            "has_api_access": False,
            "has_priority_support": False,
            "has_whatsapp_notifications": True,
            "has_custom_branding": False,
            "is_active": True,
            "display_order": 2,
            "created_by": "System",
            "modified_by": "System"
        },
        {
            "name": "Premium",
            "description": "For established companies requiring advanced features",
            "price_monthly": 10000,
            "price_yearly": 100000,  # ₹1,00,000/year (Save ₹20,000 - 2 months free)
            "branch_limit": 10,
            "user_limit": 100,
            "storage_limit_mb": 10000,  # 10GB
            "has_analytics": True,
            "has_api_access": True,
            "has_priority_support": True,
            "has_whatsapp_notifications": True,
            "has_custom_branding": True,
            "is_active": True,
            "display_order": 3,
            "created_by": "System",
            "modified_by": "System"
        },
        {
            "name": "Enterprise",
            "description": "Custom solution for large enterprises - Contact for pricing",
            "price_monthly": 0,  # Custom pricing - contact sales
            "price_yearly": 0,
            "branch_limit": 999,  # Virtually unlimited
            "user_limit": 999,
            "storage_limit_mb": 50000,  # 50GB
            "has_analytics": True,
            "has_api_access": True,
            "has_priority_support": True,
            "has_whatsapp_notifications": True,
            "has_custom_branding": True,
            "is_active": True,
            "display_order": 4,
            "created_by": "System",
            "modified_by": "System"
        }
    ]
    
    db: Session = SessionLocal()
    
    try:
        for plan_data in plans:
            # Check if plan already exists
            existing = db.query(SubscriptionPlan).filter_by(
                name=plan_data["name"]
            ).first()
            
            if not existing:
                new_plan = SubscriptionPlan(**plan_data)
                db.add(new_plan)
                print(f"   ✅ Created plan: {plan_data['name']}")
            else:
                print(f"   ⏭️  Plan already exists: {plan_data['name']}")
        
        db.commit()
        print("\n✅ Subscription plans seeded successfully!")
        
        # Show summary
        total_plans = db.query(SubscriptionPlan).count()
        print(f"📊 Total plans in database: {total_plans}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding subscription plans: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🌱 Seeding Subscription Plans...")
    seed_subscription_plans()