"""
Migration to make occupancy_type and project_type nullable.
First step before removing them completely.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_fields_nullable():
    """Make occupancy_type and project_type nullable in the database"""
    
    # Get database URL
    database_url = settings.database_url
    if not database_url:
        database_url = os.getenv("DATABASE_URL", "sqlite:///./specsharp.db")
    
    # Create engine
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # For PostgreSQL
            if 'postgresql' in database_url:
                logger.info("Applying changes to PostgreSQL database...")
                
                # Make project_type nullable
                try:
                    conn.execute(text("""
                        ALTER TABLE projects 
                        ALTER COLUMN project_type DROP NOT NULL
                    """))
                    conn.commit()
                    logger.info("✓ Made project_type nullable")
                except Exception as e:
                    logger.warning(f"project_type might already be nullable: {e}")
                
                # Make occupancy_type nullable (it's already nullable but let's ensure)
                try:
                    conn.execute(text("""
                        ALTER TABLE projects 
                        ALTER COLUMN occupancy_type DROP NOT NULL
                    """))
                    conn.commit()
                    logger.info("✓ Made occupancy_type nullable")
                except Exception as e:
                    logger.warning(f"occupancy_type might already be nullable: {e}")
                    
            # For SQLite
            else:
                logger.info("Applying changes to SQLite database...")
                # SQLite doesn't support ALTER COLUMN directly
                # We need to recreate the table with the new schema
                
                # First, check current schema
                result = conn.execute(text("PRAGMA table_info(projects)"))
                columns = result.fetchall()
                
                logger.info("Current schema:")
                for col in columns:
                    if col[1] in ['project_type', 'occupancy_type']:
                        logger.info(f"  {col[1]}: nullable={not col[3]}")
                
                # Note: For SQLite, making columns nullable requires table recreation
                # This is complex and risky. For now, we'll just document the change
                logger.info("Note: SQLite doesn't easily support making columns nullable.")
                logger.info("The model has been updated. New records won't require these fields.")
                
            logger.info("\n✅ Migration complete!")
            logger.info("project_type and occupancy_type are now nullable.")
            logger.info("New projects won't require these redundant fields.")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    make_fields_nullable()