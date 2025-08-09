from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import os
import psutil
import time
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def api_health():
    """API health check endpoint"""
    try:
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "uptime": time.time() - psutil.boot_time(),
            },
            "environment": {
                "python_version": os.sys.version,
                "platform": os.sys.platform,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Student Tracker API",
        "version": "1.1.0",
        "description": "A comprehensive student tracking application",
        "endpoints": {
            "students": "/students/api",
            "health": "/api/v1/health",
            "docs": "/docs",
            "metrics": "/metrics",
        },
        "production_url": "http://54.166.101.159:30011",
    }


@router.get("/stats")
async def api_stats():
    """API statistics endpoint"""
    try:
        # Get process information
        process = psutil.Process()

        return {
            "process": {
                "pid": process.pid,
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "memory_info": {
                    "rss": process.memory_info().rss,
                    "vms": process.memory_info().vms,
                },
                "num_threads": process.num_threads(),
                "create_time": datetime.fromtimestamp(
                    process.create_time()
                ).isoformat(),
            },
            "system": {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_total": psutil.disk_usage("/").total,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Stats collection failed: {str(e)}"
        )


@router.get("/config")
async def api_config():
    """API configuration endpoint"""
    return {
        "environment": os.getenv("ENVIRONMENT", "production"),
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "database": {
            "type": "mongodb" if os.getenv("MONGO_URI") else "in-memory",
            "configured": bool(os.getenv("MONGO_URI")),
        },
        "vault": {
            "configured": bool(os.getenv("VAULT_ADDR")),
            "enabled": bool(
                os.getenv("VAULT_ROLE_ID") and os.getenv("VAULT_SECRET_ID")
            ),
        },
    }
