import json
import sys
import os
import asyncio
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

try:
    # Import Netlify-specific database
    from database_netlify import get_student_collection, get_database_stats, init_database
    # Initialize database for Netlify
    asyncio.run(init_database())
    
except ImportError as e:
    print(f"Import error: {e}")

def handler(event, context):
    """Netlify function handler for NativeSeries API"""
    
    try:
        # Get request details
        path = event.get('path', '/')
        http_method = event.get('httpMethod', 'GET')
        headers = event.get('headers', {})
        query_string = event.get('queryStringParameters', {})
        body = event.get('body', '')
        
        # Handle CORS preflight
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                },
                'body': ''
            }
        
        # Handle common endpoints
        if path == '/health':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'status': 'healthy',
                    'message': 'NativeSeries API is running on Netlify',
                    'environment': 'netlify',
                    'timestamp': str(datetime.now(timezone.utc))
                })
            }
        
        elif path == '/api/students':
            try:
                # Use the Netlify database
                collection = get_student_collection()
                # Run async operation in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    students = loop.run_until_complete(collection.find())
                finally:
                    loop.close()
                
                stats = get_database_stats()
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'students': students,
                        'count': len(students),
                        'environment': 'netlify',
                        'database_stats': stats
                    })
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Database error',
                        'message': str(e),
                        'environment': 'netlify'
                    })
                }
        
        elif path == '/api/courses':
            try:
                from database_netlify import get_course_collection
                collection = get_course_collection()
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    courses = loop.run_until_complete(collection.find())
                finally:
                    loop.close()
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'courses': courses,
                        'count': len(courses),
                        'environment': 'netlify'
                    })
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Courses error',
                        'message': str(e),
                        'environment': 'netlify'
                    })
                }
        
        elif path == '/api/progress':
            try:
                from database_netlify import get_progress_collection
                collection = get_progress_collection()
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    progress = loop.run_until_complete(collection.find())
                finally:
                    loop.close()
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'progress': progress,
                        'count': len(progress),
                        'environment': 'netlify'
                    })
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Progress error',
                        'message': str(e),
                        'environment': 'netlify'
                    })
                }
        
        elif path == '/api/stats':
            try:
                stats = get_database_stats()
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'database_stats': stats,
                        'environment': 'netlify',
                        'timestamp': str(datetime.now(timezone.utc))
                    })
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Stats error',
                        'message': str(e),
                        'environment': 'netlify'
                    })
                }
        
        # Default response for unknown paths
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Not found',
                'message': f'Path {path} not found',
                'environment': 'netlify'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'environment': 'netlify'
            })
        }