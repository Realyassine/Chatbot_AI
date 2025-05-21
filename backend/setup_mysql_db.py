import pymysql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Extract database info from connection string
db_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost/chatbot_db")
parts = db_url.replace("mysql+pymysql://", "").split("/")
connection_details = parts[0].split("@")
credentials = connection_details[0].split(":")
host = connection_details[1]
username = credentials[0]
password = credentials[1] if len(credentials) > 1 else ""
db_name = parts[1]

print(f"Connecting to MySQL with user '{username}' on host '{host}'")
print(f"Target database name: '{db_name}'")

try:
    # Connect to the MySQL server without specifying a database
    connection = pymysql.connect(
        host=host,
        user=username,
        password=password,
    )
    
    cursor = connection.cursor()
    
    # Create the database if it doesn't exist
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    print(f"Database '{db_name}' is ready.")
    
    # Switch to the created database
    connection.select_db(db_name)
    
    print("MySQL connection successful.")
    connection.close()
    
except Exception as e:
    print(f"Error connecting to MySQL: {e}")
    print("\nPossible causes:")
    print("1. MySQL is not running in XAMPP. Start it from the XAMPP control panel.")
    print("2. MySQL credentials in .env file are incorrect.")
    print("3. Network/firewall issues preventing connection.")
    
print("\nTo fix:")
print("1. Make sure MySQL is running in XAMPP Control Panel")
print("2. Check that the username and password in .env are correct")
print("3. If needed, adjust the .env DATABASE_URL with your actual credentials")
