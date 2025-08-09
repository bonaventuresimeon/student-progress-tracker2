import os
import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class NetlifyDatabaseConfig:
    """Netlify-specific database configuration using environment variables and in-memory storage"""

    def __init__(self):
        # Environment variables for Netlify
        self.app_env = os.getenv("APP_ENV", "production")
        self.app_name = os.getenv("APP_NAME", "NativeSeries")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        
        # Database configuration (using environment variables)
        self.database_url = os.getenv("DATABASE_URL", "memory://")
        self.database_name = os.getenv("DATABASE_NAME", "nativeseries")
        self.collection_name = os.getenv("COLLECTION_NAME", "students")
        
        # Security configuration
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Logging configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        logger.info(f"Netlify Database config initialized: {self.database_name}")
        logger.info(f"Environment: {self.app_env}")
        logger.info(f"Debug mode: {self.debug}")

    def get_database_url(self) -> str:
        """Get database URL with fallback"""
        return self.database_url

    def is_memory_storage(self) -> bool:
        """Check if using in-memory storage"""
        return self.database_url.startswith("memory://")

    def get_secret_key(self) -> str:
        """Get secret key for security"""
        return self.secret_key


# Global database configuration
db_config = NetlifyDatabaseConfig()

# In-memory storage for Netlify Functions
_in_memory_students = {
    "1": {
        "id": "1",
        "name": "John Doe",
        "email": "john@example.com",
        "course": "Computer Science",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    "2": {
        "id": "2",
        "name": "Jane Smith",
        "email": "jane@example.com",
        "course": "Mathematics",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    "3": {
        "id": "3",
        "name": "Bob Johnson",
        "email": "bob@example.com",
        "course": "Physics",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
}

_in_memory_courses = {
    "1": {
        "id": "1",
        "name": "Computer Science",
        "description": "Introduction to Computer Science",
        "students_count": 1
    },
    "2": {
        "id": "2",
        "name": "Mathematics",
        "description": "Advanced Mathematics",
        "students_count": 1
    },
    "3": {
        "id": "3",
        "name": "Physics",
        "description": "Classical Physics",
        "students_count": 1
    }
}

_in_memory_progress = {
    "1": {
        "student_id": "1",
        "week": "1",
        "status": "completed",
        "notes": "Good progress",
        "updated_at": "2024-01-01T00:00:00Z"
    }
}


async def init_database():
    """Initialize database connection for Netlify"""
    try:
        logger.info("✅ Netlify database initialized successfully")
        logger.info(f"📊 Using in-memory storage with {len(_in_memory_students)} students")
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False


async def close_database():
    """Close database connection (no-op for in-memory)"""
    logger.info("Database connection closed (in-memory storage)")


class NetlifyStudentCollection:
    """Netlify-specific student collection using in-memory storage"""

    async def insert_one(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new student"""
        student_id = str(len(_in_memory_students) + 1)
        document["id"] = student_id
        document["created_at"] = datetime.now(timezone.utc).isoformat()
        document["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        _in_memory_students[student_id] = document
        logger.info(f"✅ Student created: {student_id}")
        
        return {"inserted_id": student_id, "acknowledged": True}

    async def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single student"""
        student_id = filter_dict.get("id")
        if student_id:
            return _in_memory_students.get(student_id)
        
        # Search by other fields
        for student in _in_memory_students.values():
            if all(student.get(k) == v for k, v in filter_dict.items()):
                return student
        return None

    async def find(self, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Find multiple students"""
        if not filter_dict:
            return list(_in_memory_students.values())
        
        results = []
        for student in _in_memory_students.values():
            if all(student.get(k) == v for k, v in filter_dict.items()):
                results.append(student)
        return results

    async def update_one(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Update a single student"""
        student_id = filter_dict.get("id")
        if student_id and student_id in _in_memory_students:
            _in_memory_students[student_id].update(update_dict.get("$set", {}))
            _in_memory_students[student_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
            logger.info(f"✅ Student updated: {student_id}")
            return {"modified_count": 1, "acknowledged": True}
        return {"modified_count": 0, "acknowledged": True}

    async def count_documents(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """Count documents"""
        if not filter_dict:
            return len(_in_memory_students)
        
        count = 0
        for student in _in_memory_students.values():
            if all(student.get(k) == v for k, v in filter_dict.items()):
                count += 1
        return count

    async def delete_one(self, filter_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a single student"""
        student_id = filter_dict.get("id")
        if student_id and student_id in _in_memory_students:
            del _in_memory_students[student_id]
            logger.info(f"✅ Student deleted: {student_id}")
            return {"deleted_count": 1, "acknowledged": True}
        return {"deleted_count": 0, "acknowledged": True}


def get_student_collection():
    """Get student collection for Netlify"""
    return NetlifyStudentCollection()


def get_database_stats() -> Dict[str, Any]:
    """Get database statistics"""
    return {
        "total_students": len(_in_memory_students),
        "total_courses": len(_in_memory_courses),
        "total_progress_records": len(_in_memory_progress),
        "storage_type": "in-memory",
        "environment": db_config.app_env,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def export_data() -> Dict[str, Any]:
    """Export all data for backup"""
    return {
        "students": _in_memory_students,
        "courses": _in_memory_courses,
        "progress": _in_memory_progress,
        "exported_at": datetime.now(timezone.utc).isoformat()
    }


def import_data(data: Dict[str, Any]) -> bool:
    """Import data from backup"""
    try:
        global _in_memory_students, _in_memory_courses, _in_memory_progress
        
        if "students" in data:
            _in_memory_students.update(data["students"])
        if "courses" in data:
            _in_memory_courses.update(data["courses"])
        if "progress" in data:
            _in_memory_progress.update(data["progress"])
        
        logger.info("✅ Data imported successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Data import failed: {e}")
        return False