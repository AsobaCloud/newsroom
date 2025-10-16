#!/usr/bin/env python3
"""
Lambda wrapper for news scraper that handles argument parsing
"""
import sys
import os

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

# Replace argparse with our mock
sys.modules['argparse'] = MockArgparse()

# Now import and run the actual scraper
if __name__ == "__main__":
    # Set fresh mode environment variable
    os.environ['FRESH_MODE'] = 'true'
    
    # Import and run the main scraper
    from news_scraper import main
    main()