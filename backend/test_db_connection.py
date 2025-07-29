from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv('.env.production')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        from sqlalchemy import text
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connected successfully!")
        print(f"Result: {result.scalar()}")
except Exception as e:
    print(f"❌ Connection failed: {e}")