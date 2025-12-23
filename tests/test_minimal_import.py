#!/usr/bin/env python3
"""
Minimal test to isolate the exact cause of segmentation fault
"""

import sys
import os

print("Starting minimal import test...")
print(f"Python version: {sys.version}")

# Test 1: Basic imports
try:
    print("Testing basic imports...")
    import json
    print("✓ json imported")
    
    import os
    print("✓ os imported")
    
    import sys
    print("✓ sys imported")
    
    from datetime import datetime
    print("✓ datetime imported")
    
except Exception as e:
    print(f"✗ Basic import failed: {e}")
    sys.exit(1)

# Test 2: Third-party imports
try:
    print("Testing third-party imports...")
    import boto3
    print("✓ boto3 imported")
    
    import requests
    print("✓ requests imported")
    
    from bs4 import BeautifulSoup
    print("✓ BeautifulSoup imported")
    
    from article_tagger import tag_article
    print("✓ article_tagger imported")
    
except Exception as e:
    print(f"✗ Third-party import failed: {e}")
    sys.exit(1)

# Test 3: Import news_scraper module-level code step by step
try:
    print("Testing news_scraper imports step by step...")
    
    # Import just the module, don't execute main
    import news_scraper
    print("✓ news_scraper module imported")
    
    # Check if main function exists
    if hasattr(news_scraper, 'main'):
        print("✓ main function found")
    else:
        print("✗ main function not found")
        
except Exception as e:
    print(f"✗ news_scraper import failed: {e}")
    import traceback
    print(f"Traceback: {traceback.format_exc()}")
    sys.exit(1)

print("All imports successful!")