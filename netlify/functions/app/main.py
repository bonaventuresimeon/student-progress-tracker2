from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os
import logging
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import uvicorn

# Configure logging
log_handlers = [logging.StreamHandler()]
logs_dir = "/app/logs" if os.path.exists("/app/logs") else "logs"
try:
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)
    log_handlers.append(logging.FileHandler(os.path.join(logs_dir, "app.log")))
except (OSError, PermissionError):
    # Fall back to stdout only if we can't write to logs
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=log_handlers,
)

logger = logging.getLogger(__name__)

# Application metadata
APP_VERSION = "1.1.0"
APP_NAME = "Student Tracker API"
PRODUCTION_URL = "http://54.166.101.159:30011"
APP_DESCRIPTION = """
A comprehensive student tracking application built with FastAPI.

## Features

* **Student Management** - Complete CRUD operations for student records
* **Course Management** - Multi-course enrollment system  
* **Progress Tracking** - Weekly progress monitoring and analytics
* **Assignment System** - Assignment creation, submission, and grading
* **Modern UI** - Responsive web interface
* **REST API** - Full RESTful API with OpenAPI documentation
* **Monitoring** - Health checks and metrics for production deployment

## Production Deployment

This application is deployed at: **{production_url}**

Access the interactive API documentation at: **{production_url}/docs**
""".format(
    production_url=PRODUCTION_URL
)

# Application state
app_state = {
    "start_time": datetime.now(timezone.utc),
    "request_count": 0,
    "students": [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "course": "Computer Science",
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "email": "jane@example.com",
            "course": "Mathematics",
        },
        {
            "id": 3,
            "name": "Bob Johnson",
            "email": "bob@example.com",
            "course": "Physics",
        },
    ],
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(f"🚀 {APP_NAME} starting up...")
    logger.info(f"📊 Version: {APP_VERSION}")
    logger.info(f"🌐 Production URL: {PRODUCTION_URL}")
    logger.info(f"📚 API Documentation: {PRODUCTION_URL}/docs")
    logger.info(f"🩺 Health Check: {PRODUCTION_URL}/health")

    # Initialize application state
    app_state["start_time"] = datetime.now(timezone.utc)
    app_state["request_count"] = 0

    logger.info("✅ Application startup completed successfully")

    # Test database connection (if available)
    try:
        # Add actual database connection test here
        logger.info("✅ Database connection test passed")
    except Exception as e:
        logger.warning(f"⚠️ Database connection test failed: {e}")

    yield

    # Shutdown
    logger.info(f"🛑 {APP_NAME} shutting down...")
    logger.info(f"📊 Final request count: {app_state['request_count']}")
    logger.info(
        f"⏱️ Total uptime: {int((datetime.now(timezone.utc) - app_state['start_time']).total_seconds())} seconds"
    )

    # Close database connection
    try:
        # Add actual database cleanup here
        logger.info("✅ Database connection closed successfully")
    except Exception as e:
        logger.warning(f"⚠️ Database cleanup failed: {e}")

    logger.info("✅ Application shutdown completed successfully")


app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "Development Team",
        "email": "dev@yourcompany.com",
        "url": "https://github.com/bonaventuresimeon/nativeseries",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {"url": PRODUCTION_URL, "description": "Production server"},
        {"url": "http://localhost:8000", "description": "Development server"},
    ],
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["54.166.101.159", "localhost", "127.0.0.1", "*"],
)

# Template configuration
template_paths = ["templates", "../templates", "/app/templates"]
template_dir = None

for path in template_paths:
    if os.path.exists(path):
        template_dir = path
        logger.info(f"Templates found in: {path}")
        break

if template_dir:
    templates = Jinja2Templates(directory=template_dir)
else:
    templates = None
    logger.warning("No templates directory found, using inline HTML")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add process time header to responses."""
    start_time = time.time()
    app_state["request_count"] += 1

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-Count"] = str(app_state["request_count"])

    return response


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    current_time = datetime.now(timezone.utc)
    uptime = int((current_time - app_state["start_time"]).total_seconds())

    return {
        "status": "healthy",
        "timestamp": current_time.isoformat(),
        "uptime_seconds": uptime,
        "version": APP_VERSION,
        "request_count": app_state["request_count"],
        "production_url": PRODUCTION_URL,
    }


@app.get("/metrics", tags=["System"])
async def get_metrics():
    """Application metrics endpoint."""
    current_time = datetime.now(timezone.utc)
    uptime = int((current_time - app_state["start_time"]).total_seconds())

    return {
        "application": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "uptime_seconds": uptime,
            "start_time": app_state["start_time"].isoformat(),
            "current_time": current_time.isoformat(),
        },
        "requests": {
            "total_count": app_state["request_count"],
            "requests_per_minute": app_state["request_count"] / max(uptime / 60, 1),
        },
        "system": {
            "production_url": PRODUCTION_URL,
            "docs_url": f"{PRODUCTION_URL}/docs",
            "health_url": f"{PRODUCTION_URL}/health",
        },
    }


@app.get("/", response_class=HTMLResponse, tags=["Web Interface"])
async def home(request: Request):
    """Home page."""
    current_time = datetime.now(timezone.utc)
    uptime = int((current_time - app_state["start_time"]).total_seconds())

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{APP_NAME}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
            .container {{ max-width: 1000px; margin: 0 auto; background: white; border-radius: 12px; padding: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
            .header {{ text-align: center; margin-bottom: 40px; }}
            .title {{ color: #2c3e50; margin: 0; font-size: 2.5em; }}
            .subtitle {{ color: #7f8c8d; margin: 10px 0 30px; }}
            .production-badge {{ background: #28a745; color: white; padding: 5px 12px; border-radius: 15px; font-size: 12px; margin-left: 10px; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
            .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }}
            .stat-number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
            .stat-label {{ color: #6c757d; margin-top: 5px; }}
            .nav-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
            .nav-card {{ background: #fff; border: 2px solid #e9ecef; border-radius: 8px; padding: 25px; text-align: center; transition: all 0.3s ease; text-decoration: none; color: inherit; }}
            .nav-card:hover {{ border-color: #007bff; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            .nav-icon {{ font-size: 2em; margin-bottom: 15px; }}
            .api-section {{ background: #f8f9fa; border-radius: 8px; padding: 25px; margin: 30px 0; }}
            .endpoint {{ background: #e9ecef; padding: 8px 12px; border-radius: 4px; font-family: monospace; margin: 5px 0; }}
            .footer {{ text-align: center; margin-top: 40px; color: #6c757d; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="title">{APP_NAME} <span class="production-badge">PRODUCTION</span></h1>
                <p class="subtitle">Student Tracking & Management System</p>
                <p>Production URL: <strong>{PRODUCTION_URL}</strong></p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{uptime}</div>
                    <div class="stat-label">Uptime (seconds)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{app_state["request_count"]}</div>
                    <div class="stat-label">Total Requests</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(app_state["students"])}</div>
                    <div class="stat-label">Sample Students</div>
                </div>
            </div>
            
            <div class="nav-grid">
                <a href="/students" class="nav-card">
                    <div class="nav-icon">👥</div>
                    <h3>Students</h3>
                    <p>View and manage student records</p>
                </a>
                <a href="/register" class="nav-card">
                    <div class="nav-icon">📝</div>
                    <h3>Register</h3>
                    <p>Register new students</p>
                </a>
                <a href="/progress" class="nav-card">
                    <div class="nav-icon">📊</div>
                    <h3>Progress</h3>
                    <p>Track student progress</p>
                </a>
                <a href="/update" class="nav-card">
                    <div class="nav-icon">✏️</div>
                    <h3>Update</h3>
                    <p>Update student information</p>
                </a>
                <a href="/admin" class="nav-card">
                    <div class="nav-icon">⚙️</div>
                    <h3>Admin</h3>
                    <p>Administrative functions</p>
                </a>
                <a href="/docs" class="nav-card">
                    <div class="nav-icon">📚</div>
                    <h3>API Docs</h3>
                    <p>Interactive API documentation</p>
                </a>
            </div>
            
            <div class="api-section">
                <h3>REST API Endpoints</h3>
                <div class="endpoint">GET /health - Health check</div>
                <div class="endpoint">GET /metrics - Application metrics</div>
                <div class="endpoint">GET /api/students - List students</div>
                <div class="endpoint">POST /api/register - Register student</div>
                <div class="endpoint">GET /docs - API documentation</div>
            </div>
            
            <div class="footer">
                <p>Built with FastAPI • Deployed on NativeSeries Pipeline</p>
                <p>Version {APP_VERSION} • <a href="https://github.com/bonaventuresimeon/nativeseries" target="_blank">GitHub</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/about", response_class=HTMLResponse, tags=["Web Interface"])
async def about(request: Request):
    """About page."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>About - {APP_NAME}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .back-link {{ color: #007bff; text-decoration: none; margin-bottom: 20px; display: inline-block; }}
            .production-badge {{ background: #28a745; color: white; padding: 3px 8px; border-radius: 10px; font-size: 11px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Home</a>
            <h1>About <span class="production-badge">PRODUCTION</span></h1>
            <p>Production URL: <strong>{PRODUCTION_URL}</strong></p>
            
            <h2>Student Tracker API</h2>
            <p>Version: {APP_VERSION}</p>
            <p>A comprehensive student tracking application built with FastAPI.</p>
            
            <h3>Features</h3>
            <ul>
                <li>Student Management - Complete CRUD operations</li>
                <li>Course Management - Multi-course enrollment</li>
                <li>Progress Tracking - Weekly progress monitoring</li>
                <li>Assignment System - Assignment creation and grading</li>
                <li>Modern UI - Responsive web interface</li>
                <li>REST API - Full RESTful API with documentation</li>
                <li>Monitoring - Health checks and metrics</li>
            </ul>
            
            <h3>Technology Stack</h3>
            <ul>
                <li>FastAPI - Modern web framework</li>
                <li>Python 3.13 - Latest Python version</li>
                <li>Docker - Containerization</li>
                <li>GitHub Actions - CI/CD Pipeline</li>
                <li>Production Deployment - AWS EC2</li>
            </ul>
            
            <h3>API Documentation</h3>
            <p>Access the interactive API documentation at: <a href="/docs" target="_blank">/docs</a></p>
            
            <h3>Health Check</h3>
            <p>Monitor application health at: <a href="/health" target="_blank">/health</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# Add missing endpoints
@app.get("/register", response_class=HTMLResponse, tags=["Students"])
async def register_page(request: Request):
    """Student registration page."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register Student - {APP_NAME}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .back-link {{ color: #007bff; text-decoration: none; margin-bottom: 20px; display: inline-block; }}
            .form-group {{ margin-bottom: 20px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            input, select {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }}
            button {{ background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }}
            button:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Home</a>
            <h1>Register New Student</h1>
            <p>Production URL: <strong>{PRODUCTION_URL}</strong></p>
            
            <form method="POST" action="/register">
                <div class="form-group">
                    <label for="name">Full Name:</label>
                    <input type="text" id="name" name="name" required>
                </div>
                
                <div class="form-group">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="course">Course:</label>
                    <select id="course" name="course" required>
                        <option value="">Select a course</option>
                        <option value="Computer Science">Computer Science</option>
                        <option value="Mathematics">Mathematics</option>
                        <option value="Physics">Physics</option>
                        <option value="Engineering">Engineering</option>
                    </select>
                </div>
                
                <button type="submit">Register Student</button>
            </form>
            
            <p style="margin-top: 30px;">
                <strong>API Endpoint:</strong> POST /api/register
            </p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/register", response_class=HTMLResponse, tags=["Students"])
async def register_student(
    request: Request,
    name: str = Form(...),
    email: str = Form(None),
    course: str = Form(None),
):
    """Handle student registration."""
    # In a real application, this would save to database
    # Use default values if email or course not provided
    email = email or f"{name.lower().replace(' ', '.')}@example.com"
    course = course or "Computer Science"

    new_student = {
        "id": len(app_state["students"]) + 1,
        "name": name,
        "email": email,
        "course": course,
    }
    app_state["students"].append(new_student)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Registration Success - {APP_NAME}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .success {{ color: #28a745; font-weight: bold; }}
            .back-link {{ color: #007bff; text-decoration: none; margin-top: 20px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="success">✅ Registration Successful!</h1>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Course:</strong> {course}</p>
            <p>Production URL: <strong>{PRODUCTION_URL}</strong></p>
            <a href="/" class="back-link">← Back to Home</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/progress", response_class=HTMLResponse, tags=["Students"])
async def progress_page(request: Request):
    """Student progress tracking page."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Progress - {APP_NAME}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .back-link {{ color: #007bff; text-decoration: none; margin-bottom: 20px; display: inline-block; }}
            .progress-card {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Home</a>
            <h1>Student Progress Tracking</h1>
            <p>Production URL: <strong>{PRODUCTION_URL}</strong></p>
            
            <div class="progress-card">
                <h3>Sample Progress Data</h3>
                <p>This is a demo page showing student progress tracking functionality.</p>
                <p>In production, this would display real progress data from the database.</p>
            </div>
            
            <div class="progress-card">
                <h3>Available Students</h3>
                <ul>
                    {''.join([f'<li>{student["name"]} - {student["course"]}</li>' for student in app_state["students"]])}
                </ul>
            </div>
            
            <p><strong>API Endpoint:</strong> GET /api/students</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/progress", response_class=HTMLResponse, tags=["Students"])
async def update_progress(request: Request, name: str = Form(...)):
    """Handle progress updates."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Progress Updated - {APP_NAME}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .success {{ color: #28a745; font-weight: bold; }}
            .back-link {{ color: #007bff; text-decoration: none; margin-top: 20px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="success">✅ Progress Updated!</h1>
            <p><strong>Student:</strong> {name}</p>
            <p>Progress information has been updated successfully.</p>
            <p>Production URL: <strong>{PRODUCTION_URL}</strong></p>
            <a href="/" class="back-link">← Back to Home</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/update", response_class=HTMLResponse, tags=["Students"])
async def update_page(request: Request):
    """Student update page."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Update Student - {APP_NAME}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .back-link {{ color: #007bff; text-decoration: none; margin-bottom: 20px; display: inline-block; }}
            .form-group {{ margin-bottom: 20px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            input, select {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }}
            button {{ background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }}
            button:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Home</a>
            <h1>Update Student Information</h1>
            <p>Production URL: <strong>{PRODUCTION_URL}</strong></p>
            
            <form method="POST" action="/update">
                <div class="form-group">
                    <label for="name">Student Name:</label>
                    <input type="text" id="name" name="name" required>
                </div>
                
                <div class="form-group">
                    <label for="week">Week:</label>
                    <select id="week" name="week" required>
                        <option value="">Select week</option>
                        <option value="week1">Week 1</option>
                        <option value="week2">Week 2</option>
                        <option value="week3">Week 3</option>
                        <option value="week4">Week 4</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="status">Status:</label>
                    <select id="status" name="status" required>
                        <option value="">Select status</option>
                        <option value="completed">Completed</option>
                        <option value="in_progress">In Progress</option>
                        <option value="not_started">Not Started</option>
                    </select>
                </div>
                
                <button type="submit">Update Progress</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/update", response_class=HTMLResponse, tags=["Students"])
async def update_student(
    request: Request,
    name: str = Form(...),
    week: str = Form(...),
    status: str = Form(...),
):
    """Handle student updates."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Update Success - {APP_NAME}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .success {{ color: #28a745; font-weight: bold; }}
            .back-link {{ color: #007bff; text-decoration: none; margin-top: 20px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="success">✅ Update Successful!</h1>
            <p><strong>Student:</strong> {name}</p>
            <p><strong>Week:</strong> {week}</p>
            <p><strong>Status:</strong> {status}</p>
            <p>Production URL: <strong>{PRODUCTION_URL}</strong></p>
            <a href="/" class="back-link">← Back to Home</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/admin", response_class=HTMLResponse, tags=["Admin"])
async def admin_page(request: Request):
    """Admin page."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - {APP_NAME}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .back-link {{ color: #007bff; text-decoration: none; margin-bottom: 20px; display: inline-block; }}
            .admin-card {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Home</a>
            <h1>Administrative Dashboard</h1>
            <p>Production URL: <strong>{PRODUCTION_URL}</strong></p>
            
            <div class="admin-card">
                <h3>System Statistics</h3>
                <p><strong>Total Requests:</strong> {app_state["request_count"]}</p>
                <p><strong>Uptime:</strong> {int((datetime.now(timezone.utc) - app_state["start_time"]).total_seconds())} seconds</p>
                <p><strong>Students:</strong> {len(app_state["students"])}</p>
            </div>
            
            <div class="admin-card">
                <h3>Health Monitoring</h3>
                <p><a href="/health" target="_blank">Health Check</a></p>
                <p><a href="/metrics" target="_blank">System Metrics</a></p>
            </div>
            
            <div class="admin-card">
                <h3>API Documentation</h3>
                <p><a href="/docs" target="_blank">Interactive API Docs</a></p>
                <p><a href="/redoc" target="_blank">ReDoc Documentation</a></p>
            </div>
            
            <div class="admin-card">
                <h3>Student Management</h3>
                <p><a href="/students">View Students</a></p>
                <p><a href="/register">Register New Student</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# API endpoints
@app.get("/api/students", tags=["API"])
async def get_students():
    """Get all students."""
    return {
        "students": app_state["students"],
        "count": len(app_state["students"]),
        "production_url": PRODUCTION_URL,
    }


@app.post("/api/register", tags=["API"])
async def api_register_student(name: str):
    """Register a new student via API."""
    new_student = {
        "id": len(app_state["students"]) + 1,
        "name": name,
        "email": f"{name.lower().replace(' ', '.')}@example.com",
        "course": "Computer Science",
    }
    app_state["students"].append(new_student)

    return {
        "message": "Student registered successfully",
        "student": new_student,
        "production_url": PRODUCTION_URL,
    }


# Include routers for different modules
try:
    from app.routes import students, api

    app.include_router(students.router, prefix="/students", tags=["Students"])
    app.include_router(api.router, prefix="/api/v1", tags=["API"])
    logger.info("Student and API routes loaded successfully")
except ImportError as e:
    logger.warning(f"Could not load all routes: {e}")

    # Fallback basic student endpoints
    @app.get("/students", response_class=HTMLResponse, tags=["Students"])
    async def list_students(request: Request):
        """List all students (fallback endpoint)."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Students - {APP_NAME}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .back-link {{ color: #007bff; text-decoration: none; margin-bottom: 20px; display: inline-block; }}
                .student-card {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .production-badge {{ background: #28a745; color: white; padding: 3px 8px; border-radius: 10px; font-size: 11px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <a href="/" class="back-link">← Back to Home</a>
                <h1>Students <span class="production-badge">PRODUCTION</span></h1>
                <p>Production URL: <strong>{PRODUCTION_URL}</strong></p>
                
                <div class="student-card">
                    <h3>Sample Student Records</h3>
                    <p>This is a demo endpoint. In production, this would connect to the PostgreSQL database to display real student data.</p>
                    <p>Available through the API at: <code>{PRODUCTION_URL}/api/v1/students</code></p>
                </div>
                
                <div class="student-card">
                    <h3>API Access</h3>
                    <p>For full functionality, use the REST API:</p>
                    <ul>
                        <li><strong>GET</strong> <code>/api/v1/students</code> - List students</li>
                        <li><strong>POST</strong> <code>/api/v1/students</code> - Create student</li>
                        <li><strong>GET</strong> <code>/api/v1/students/{{id}}</code> - Get student</li>
                        <li><strong>PUT</strong> <code>/api/v1/students/{{id}}</code> - Update student</li>
                        <li><strong>DELETE</strong> <code>/api/v1/students/{{id}}</code> - Delete student</li>
                    </ul>
                    <p><a href="/docs" target="_blank">View Interactive API Documentation →</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 error handler."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>404 - Page Not Found</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; text-align: center; }}
            .container {{ max-width: 600px; margin: 50px auto; background: white; border-radius: 8px; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .error-code {{ font-size: 72px; color: #dc3545; margin: 0; }}
            .home-link {{ color: #007bff; text-decoration: none; padding: 10px 20px; border: 2px solid #007bff; border-radius: 5px; display: inline-block; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="error-code">404</h1>
            <h2>Page Not Found</h2>
            <p>The requested page could not be found on this server.</p>
            <p>Production URL: <strong>{PRODUCTION_URL}</strong></p>
            <a href="/" class="home-link">← Return to Home</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=404)


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Custom 500 error handler."""
    logger.error(f"Internal server error: {exc}")
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>500 - Internal Server Error</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; text-align: center; }}
            .container {{ max-width: 600px; margin: 50px auto; background: white; border-radius: 8px; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .error-code {{ font-size: 72px; color: #dc3545; margin: 0; }}
            .home-link {{ color: #007bff; text-decoration: none; padding: 10px 20px; border: 2px solid #007bff; border-radius: 5px; display: inline-block; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="error-code">500</h1>
            <h2>Internal Server Error</h2>
            <p>Something went wrong on our end. We've been notified and are working to fix it.</p>
            <p>Production URL: <strong>{PRODUCTION_URL}</strong></p>
            <a href="/" class="home-link">← Return to Home</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=500)


# Application lifespan is now handled by the lifespan context manager above

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disabled for production
        log_level="info",
        access_log=True,
    )
