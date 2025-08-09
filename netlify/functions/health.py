import json
from datetime import datetime, timezone

def handler(event, context):
    """Simple health check function"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps({
            'status': 'healthy',
            'message': 'NativeSeries is running on Netlify',
            'environment': 'netlify',
            'timestamp': str(datetime.now(timezone.utc)),
            'version': '1.0.0'
        })
    }
