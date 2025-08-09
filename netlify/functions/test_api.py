#!/usr/bin/env python3
"""
Test script for Netlify Functions API
This script tests the basic functionality of the NativeSeries API
"""

import json
import sys
import os
import asyncio
from datetime import datetime, timezone

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

def test_health_function():
    """Test the health check function"""
    print("🏥 Testing health function...")
    
    try:
        from health import handler
        
        # Simulate Netlify event
        event = {
            'path': '/health',
            'httpMethod': 'GET',
            'headers': {},
            'queryStringParameters': {},
            'body': ''
        }
        
        context = {}
        
        # Call the handler
        result = handler(event, context)
        
        # Check response
        assert result['statusCode'] == 200
        assert 'body' in result
        assert 'headers' in result
        
        # Parse response body
        body = json.loads(result['body'])
        assert body['status'] == 'healthy'
        assert 'timestamp' in body
        
        print("✅ Health function test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Health function test failed: {e}")
        return False

def test_api_function():
    """Test the main API function"""
    print("🔧 Testing API function...")
    
    try:
        from api import handler
        
        # Test students endpoint
        event = {
            'path': '/api/students',
            'httpMethod': 'GET',
            'headers': {},
            'queryStringParameters': {},
            'body': ''
        }
        
        context = {}
        
        # Call the handler
        result = handler(event, context)
        
        # Check response
        assert result['statusCode'] == 200
        assert 'body' in result
        
        # Parse response body
        body = json.loads(result['body'])
        assert 'students' in body
        assert 'count' in body
        assert 'environment' in body
        
        print("✅ API function test passed!")
        return True
        
    except Exception as e:
        print(f"❌ API function test failed: {e}")
        return False

async def test_database_async():
    """Test the database functionality asynchronously"""
    try:
        from database_netlify import get_student_collection, get_database_stats, init_database
        
        # Initialize database
        await init_database()
        
        # Get collection
        collection = get_student_collection()
        
        # Test insert
        test_student = {
            "name": "Test Student",
            "email": "test@example.com",
            "course": "Test Course"
        }
        
        result = await collection.insert_one(test_student)
        assert result['acknowledged'] == True
        
        # Test find
        students = await collection.find()
        assert len(students) > 0
        
        # Get stats
        stats = get_database_stats()
        assert 'students_count' in stats
        assert 'courses_count' in stats
        assert 'progress_count' in stats
        
        return True
        
    except Exception as e:
        print(f"❌ Database async test failed: {e}")
        return False

def test_database_function():
    """Test the database functionality"""
    print("🗄️ Testing database function...")
    
    try:
        # Run async test in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(test_database_async())
        finally:
            loop.close()
        
        if result:
            print("✅ Database function test passed!")
            return True
        else:
            print("❌ Database function test failed")
            return False
        
    except Exception as e:
        print(f"❌ Database function test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting Netlify Functions Tests...")
    print("=" * 50)
    
    tests = [
        test_health_function,
        test_api_function,
        test_database_function
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Netlify functions are ready.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())