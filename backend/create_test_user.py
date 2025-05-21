from database import create_tables, get_db
from auth import UserCreate, create_user

def create_test_user():
    # Create database tables if they don't exist
    create_tables()
    
    # Get DB session
    db = next(get_db())
    
    try:
        # Create a user
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpass"
        )
        
        # Add the user
        user = create_user(db, user_data)
        print(f"Created test user: {user.username}")
    except Exception as e:
        print(f"User may already exist: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
