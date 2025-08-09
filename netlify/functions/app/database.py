import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Simplified database configuration for immediate deployment
# This will be replaced with proper MongoDB/Vault setup later


class DatabaseConfig:
    """Database configuration with fallback to environment variables"""

    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.database_name = os.getenv("DATABASE_NAME", "student_project_tracker")
        self.collection_name = os.getenv("COLLECTION_NAME", "students")

        # Vault configuration (optional)
        self.vault_addr = os.getenv("VAULT_ADDR")
        self.vault_role_id = os.getenv("VAULT_ROLE_ID")
        self.vault_secret_id = os.getenv("VAULT_SECRET_ID")

        logger.info(f"Database config initialized: {self.database_name}")

    def get_mongo_uri(self) -> str:
        """Get MongoDB URI with fallback"""
        return self.mongo_uri

    def is_vault_configured(self) -> bool:
        """Check if Vault is properly configured"""
        return all([self.vault_addr, self.vault_role_id, self.vault_secret_id])


# Global database configuration
db_config = DatabaseConfig()

# Initialize database connection (will be lazy-loaded)
client = None
database = None
student_collection = None


async def init_database():
    """Initialize database connection"""
    global client, database, student_collection

    try:
        # Try to import motor for MongoDB
        import motor.motor_asyncio

        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient(db_config.get_mongo_uri())
        database = client[db_config.database_name]
        student_collection = database.get_collection(db_config.collection_name)

        # Test connection
        await client.admin.command("ping")
        logger.info("✅ MongoDB connection established successfully")

    except ImportError:
        logger.warning("⚠️ Motor not available, using in-memory storage")
        # Fallback to in-memory storage
        client = None
        database = None
        student_collection = None

    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.info("🔄 Using in-memory storage as fallback")
        client = None
        database = None
        student_collection = None


async def close_database():
    """Close database connection"""
    if client:
        client.close()
        logger.info("Database connection closed")


# In-memory storage fallback
_in_memory_students = {}


def get_student_collection():
    """Get student collection with fallback to in-memory storage"""
    if student_collection:
        return student_collection
    else:
        # Return a mock collection that works with in-memory storage
        return MockCollection()


class MockCollection:
    """Mock collection for in-memory storage"""

    async def insert_one(self, document):
        student_id = document.get("id", str(len(_in_memory_students) + 1))
        _in_memory_students[student_id] = document
        return type("MockResult", (), {"inserted_id": student_id})()

    async def find_one(self, filter_dict):
        student_id = filter_dict.get("id")
        return _in_memory_students.get(student_id)

    async def find(self, filter_dict=None):
        # Return all students as a list
        return list(_in_memory_students.values())

    async def update_one(self, filter_dict, update_dict):
        student_id = filter_dict.get("id")
        if student_id in _in_memory_students:
            _in_memory_students[student_id].update(update_dict.get("$set", {}))
        return type("MockResult", (), {"modified_count": 1})()

    async def count_documents(self, filter_dict=None):
        return len(_in_memory_students)
