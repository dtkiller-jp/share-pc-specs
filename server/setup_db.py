from database import engine, Base, SessionLocal, User, ResourceLimit
from config import settings

def setup_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create admin users
        for email in settings.admin_emails:
            existing = db.query(User).filter(User.email == email).first()
            if not existing:
                admin = User(
                    email=email,
                    oauth_provider="manual",
                    oauth_id="admin",
                    is_admin=True,
                    is_whitelisted=True
                )
                db.add(admin)
                
                # Add default resource limits
                limits = ResourceLimit(
                    user=admin,
                    cpu_percent=100,
                    memory_mb=settings.default_limits.memory_mb * 2,
                    gpu_memory_mb=settings.default_limits.gpu_memory_mb * 2,
                    storage_mb=settings.default_limits.storage_mb * 2
                )
                db.add(limits)
                print(f"Created admin user: {email}")
        
        db.commit()
        print("Database setup complete!")
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()
