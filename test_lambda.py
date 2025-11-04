import json
import os
import sys
from datetime import datetime

# Mock argparse to avoid import-time argument parsing issues
class MockArgs:
    def __init__(self):
        self.fresh = True  # Always run in fresh mode in Lambda

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
os.environ['FRESH_MODE'] = 'true'

def lambda_handler(event, context):
    """
    Test Lambda handler - just try to import news_scraper
    """
    
    try:
        # Just try to import the module first
        import news_scraper
        logger = news_scraper.logger
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully imported news_scraper module',
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error importing news_scraper: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })
        }