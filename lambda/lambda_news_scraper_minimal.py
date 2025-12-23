import json
import os
import sys
import boto3
import logging
from datetime import datetime, date
import time

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Mock argparse to avoid import-time argument parsing issues
class MockArgs:
    def __init__(self):
        self.fresh = False  # Run in idempotent mode in Lambda

# Mock the argparse module
class MockArgparse:
    class ArgumentParser:
        def __init__(self, *args, **kwargs):
            pass
        def add_argument(self, *args, **kwargs):
            pass
        def parse_args(self):
            return MockArgs()

# Replace argparse with our mock BEFORE importing news_scraper
sys.modules['argparse'] = MockArgparse()

# Set environment variables before importing
os.environ['FRESH_MODE'] = 'false'

def lambda_handler(event, context):
    """
    AWS Lambda handler for news scraper
    Runs the news scraper with minimal dependencies
    """
    
    try:
        # Import the news scraper after mocking argparse
        from news_scraper import main
        
        # Run the main scraper function
        main()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'News scraper completed successfully',
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error in Lambda: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error running news scraper: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })
        }