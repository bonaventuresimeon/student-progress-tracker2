# CRUD operations for Student Tracker application
from app.database import get_student_collection
from app.models import Student
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


async def create_student(name: str):
    """Create a new student"""
    try:
        student_id = str(uuid4())
        student = Student(id=student_id, name=name)

        collection = get_student_collection()
        await collection.insert_one(student.dict())

        logger.info(f"✅ Student created: {name} (ID: {student_id})")
        return student
    except Exception as e:
        logger.error(f"❌ Error creating student: {e}")
        raise


async def get_student(student_id: str):
    """Get a student by ID"""
    try:
        collection = get_student_collection()
        result = await collection.find_one({"id": student_id})
        return result
    except Exception as e:
        logger.error(f"❌ Error getting student {student_id}: {e}")
        return None


async def update_progress(student_id: str, week: str):
    """Update student progress for a specific week"""
    try:
        collection = get_student_collection()
        await collection.update_one(
            {"id": student_id}, {"$set": {f"progress.{week}": True}}
        )
        return await get_student(student_id)
    except Exception as e:
        logger.error(f"❌ Error updating progress for student {student_id}: {e}")
        raise


async def get_all_students():
    """Get all students"""
    try:
        collection = get_student_collection()
        cursor = await collection.find({})

        # Handle both MongoDB cursor and list
        if hasattr(cursor, "__aiter__"):
            students = []
            async for student in cursor:
                students.append(Student(**student))
            return students
        else:
            # Handle list from mock collection
            return [Student(**student) for student in cursor]
    except Exception as e:
        logger.error(f"❌ Error getting all students: {e}")
        return []


async def count_students():
    """Count total number of students"""
    try:
        collection = get_student_collection()
        return await collection.count_documents({})
    except Exception as e:
        logger.error(f"❌ Error counting students: {e}")
        return 0


async def get_student_progress(student_id: str):
    """Get student progress information"""
    try:
        student = await get_student(student_id)
        if student:
            return {
                "student_name": student["name"],
                "progress": student.get("progress", {}),
            }
        return {}
    except Exception as e:
        logger.error(f"❌ Error getting progress for student {student_id}: {e}")
        return {}


async def update_student_progress(student_id: str, week: str, status: str):
    """Update student progress with specific status"""
    try:
        status_bool = status.lower() == "true"
        collection = get_student_collection()
        await collection.update_one(
            {"id": student_id}, {"$set": {f"progress.{week}": status_bool}}
        )
        return await get_student(student_id)
    except Exception as e:
        logger.error(f"❌ Error updating student progress: {e}")
        raise


async def delete_student(student_id: str):
    """Delete a student"""
    try:
        collection = get_student_collection()
        # Note: MockCollection doesn't support delete, but MongoDB would
        if hasattr(collection, "delete_one"):
            result = await collection.delete_one({"id": student_id})
            return result.deleted_count > 0
        else:
            logger.warning("⚠️ Delete operation not supported in mock collection")
            return False
    except Exception as e:
        logger.error(f"❌ Error deleting student {student_id}: {e}")
        return False


async def search_students(name_filter: str = None):
    """Search students by name"""
    try:
        all_students = await get_all_students()
        if name_filter:
            return [s for s in all_students if name_filter.lower() in s.name.lower()]
        return all_students
    except Exception as e:
        logger.error(f"❌ Error searching students: {e}")
        return []
