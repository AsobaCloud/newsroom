import json
import os
import subprocess
import sys
from datetime import datetime

def lambda_handler(event, context):
    """
    Minimal Lambda handler to test news_scraper import
    """
    try:
        print("Lambda handler started")
        print(f"Python version: {sys.version}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Files in current directory: {os.listdir('.')}")
        
        # Test direct import
        print("Attempting to import news_scraper...")
        import news_scraper
        print("✓ news_scraper imported successfully")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'news_scraper import successful',
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        print(f"Error: {e}")
        print(f"Exception type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Import failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })
        }