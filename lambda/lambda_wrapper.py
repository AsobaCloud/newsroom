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

# Now import and run the actual scrapers
if __name__ == "__main__":
    # Set fresh mode environment variable
    os.environ['FRESH_MODE'] = 'true'
    
    # Import and run the main news scraper
    try:
        from news_scraper import main as news_main
        print("Starting news_scraper...")
        news_main()
        print("news_scraper completed")
    except Exception as e:
        print(f"Error in news_scraper: {e}")
        import traceback
        traceback.print_exc()
    
    # Import and run the legislation scraper
    try:
        from legislation_scraper import process_legislation_feeds
        print("Starting legislation_scraper...")
        os.environ['FRESH_MODE'] = 'true'
        import legislation_scraper
        legislation_scraper.FRESH_MODE = True
        process_legislation_feeds()
        print("legislation_scraper completed")
    except Exception as e:
        print(f"Error in legislation_scraper: {e}")
        import traceback
        traceback.print_exc()

    # Import and run the Polymarket scraper
    try:
        from polymarket_scraper import process_polymarket_feeds
        print("Starting polymarket_scraper...")
        process_polymarket_feeds()
        print("polymarket_scraper completed")
    except Exception as e:
        print(f"Error in polymarket_scraper: {e}")
        import traceback
        traceback.print_exc()