#!/usr/bin/env python3
"""
Test script to identify which import causes the segmentation fault
"""

import sys
import os

# Mock argparse first
class MockArgs:
    def __init__(self):
        self.fresh = False

class MockArgparse:
    class ArgumentParser:
        def __init__(self, *args, **kwargs):
            pass
        def add_argument(self, *args, **kwargs):
            pass
        def parse_args(self):
            return MockArgs()

sys.modules['argparse'] = MockArgparse()
os.environ['FRESH_MODE'] = 'false'

print("Testing imports step by step...")

try:
    print("1. Testing basic imports...")
    import os
    import re
    import json
    import time
    import boto3
    import logging
    import requests
    import hashlib
    from datetime import datetime, date
    from typing import Dict, List, Optional
    from urllib.parse import urljoin, urlparse, quote
    print("✓ Basic imports successful")
except Exception as e:
    print(f"✗ Basic imports failed: {e}")
    sys.exit(1)

try:
    print("2. Testing BeautifulSoup...")
    from bs4 import BeautifulSoup
    print("✓ BeautifulSoup import successful")
except Exception as e:
    print(f"✗ BeautifulSoup import failed: {e}")
    sys.exit(1)

try:
    print("3. Testing ThreadPoolExecutor...")
    from concurrent.futures import ThreadPoolExecutor
    print("✓ ThreadPoolExecutor import successful")
except Exception as e:
    print(f"✗ ThreadPoolExecutor import failed: {e}")
    sys.exit(1)

try:
    print("4. Testing article_tagger...")
    from article_tagger import tag_article
    print("✓ article_tagger import successful")
except Exception as e:
    print(f"✗ article_tagger import failed: {e}")
    sys.exit(1)

try:
    print("5. Testing dateutil...")
    from dateutil import parser
    print("✓ dateutil import successful")
except Exception as e:
    print(f"✗ dateutil import failed: {e}")
    sys.exit(1)

print("All imports successful!")