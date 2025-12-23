import json
import os
import subprocess
import sys
from datetime import datetime

def lambda_handler(event, context):
    """
    AWS Lambda handler for news scraper
    Runs the news_scraper.py script and returns results
    """
    
    try:
        # The files are in the Lambda package root, not /tmp
        # List current directory to debug
        print(f"Current directory: {os.getcwd()}")
        print(f"Files in current directory: {os.listdir('.')}")
        
        # Run the news scraper using the wrapper script
        result = subprocess.run([
            sys.executable, 'lambda_wrapper.py'
        ], capture_output=True, text=True, timeout=900)  # 15 minute timeout
        
        # Log the results
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'News scraper completed successfully',
                'return_code': result.returncode,
                'timestamp': datetime.now().isoformat(),
                'stdout': result.stdout[-1000:],  # Last 1000 chars
                'stderr': result.stderr[-500:] if result.stderr else None
            })
        }
        
    except subprocess.TimeoutExpired:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'News scraper timed out after 15 minutes',
                'timestamp': datetime.now().isoformat()
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error running news scraper: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })
        }