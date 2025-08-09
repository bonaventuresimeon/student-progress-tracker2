from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from typing import List, Optional
import os

from app.crud import (
    create_student,
    get_student,
    get_all_students,
    update_student_progress,
    delete_student,
    search_students,
    count_students,
    get_student_progress,
)
from app.models import Student

router = APIRouter()

# Template setup
template_paths = ["templates", "../templates", "/app/templates"]
templates = None
for path in template_paths:
    if os.path.exists(path):
        templates = Jinja2Templates(directory=path)
        break


@router.get("/", response_class=HTMLResponse)
async def list_students_page(request: Request):
    """List all students with web interface"""
    try:
        students = await get_all_students()
        student_count = await count_students()

        if templates:
            return templates.TemplateResponse(
                "students.html",
                {
                    "request": request,
                    "students": students,
                    "student_count": student_count,
                },
            )

        # Fallback HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Students - Student Tracker</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .stats {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center; }}
                .student-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 30px; }}
                .student-card {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 20px; border-radius: 8px; }}
                .student-name {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
                .student-id {{ color: #6c757d; font-size: 14px; margin-bottom: 10px; }}
                .progress {{ margin-top: 10px; }}
                .progress-item {{ display: flex; justify-content: space-between; margin: 5px 0; }}
                .completed {{ color: #28a745; }}
                .pending {{ color: #dc3545; }}
                .nav-links {{ margin-top: 20px; text-align: center; }}
                .nav-links a {{ color: #007bff; text-decoration: none; margin: 0 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>👥 Students Management</h1>
                    <p>Total Students: {student_count}</p>
                </div>
                
                <div class="stats">
                    <h3>📊 Statistics</h3>
                    <p>Total Students: <strong>{student_count}</strong></p>
                </div>
                
                <div class="student-grid">
        """

        for student in students:
            progress_items = []
            for week, completed in student.progress.items():
                status_class = "completed" if completed else "pending"
                status_text = "✅" if completed else "⏳"
                progress_items.append(
                    f'<div class="progress-item"><span>{week}</span><span class="{status_class}">{status_text}</span></div>'
                )

            progress_html = (
                "".join(progress_items)
                if progress_items
                else "<p>No progress recorded yet</p>"
            )

            html_content += f"""
                    <div class="student-card">
                        <div class="student-name">{student.name}</div>
                        <div class="student-id">ID: {student.id}</div>
                        <div class="progress">
                            <h4>Progress:</h4>
                            {progress_html}
                        </div>
                    </div>
            """

        html_content += """
                </div>
                
                <div class="nav-links">
                    <a href="/">← Back to Home</a>
                    <a href="/docs">📖 API Documentation</a>
                    <a href="/health">🩺 Health Check</a>
                </div>
            </div>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading students: {str(e)}")


@router.get("/api", response_model=List[Student])
async def list_students_api():
    """Get all students via API"""
    try:
        return await get_all_students()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving students: {str(e)}"
        )


@router.post("/api", response_model=Student)
async def create_student_api(name: str):
    """Create a new student via API"""
    try:
        if not name or len(name.strip()) == 0:
            raise HTTPException(status_code=400, detail="Name is required")

        student = await create_student(name.strip())
        return student
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating student: {str(e)}")


@router.get("/api/{student_id}", response_model=Student)
async def get_student_api(student_id: str):
    """Get a specific student by ID"""
    try:
        student = await get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return Student(**student)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving student: {str(e)}"
        )


@router.put("/api/{student_id}/progress")
async def update_student_progress_api(student_id: str, week: str, status: str = "true"):
    """Update student progress for a specific week"""
    try:
        student = await update_student_progress(student_id, week, status)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return {
            "message": f"Progress updated for {student['name']}",
            "student": student,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating progress: {str(e)}"
        )


@router.get("/api/{student_id}/progress")
async def get_student_progress_api(student_id: str):
    """Get student progress information"""
    try:
        progress = await get_student_progress(student_id)
        if not progress:
            raise HTTPException(status_code=404, detail="Student not found")
        return progress
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving progress: {str(e)}"
        )


@router.delete("/api/{student_id}")
async def delete_student_api(student_id: str):
    """Delete a student"""
    try:
        success = await delete_student(student_id)
        if not success:
            raise HTTPException(status_code=404, detail="Student not found")
        return {"message": "Student deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting student: {str(e)}")


@router.get("/api/search")
async def search_students_api(
    name: Optional[str] = Query(None, description="Name filter")
):
    """Search students by name"""
    try:
        students = await search_students(name)
        return students
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error searching students: {str(e)}"
        )


@router.get("/count")
async def get_student_count():
    """Get total number of students"""
    try:
        count = await count_students()
        return {"total_students": count}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error counting students: {str(e)}"
        )
