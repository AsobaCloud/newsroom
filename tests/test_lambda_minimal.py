#!/usr/bin/env python3
"""
Minimal test to isolate the segfault issue in Lambda
"""
import sys
import os

print("Python version:", sys.version)
print("Current directory:", os.getcwd())
print("Files in current directory:", os.listdir('.'))

# Test imports one by one
print("\nTesting imports...")

try:
    import boto3
    print("✓ boto3 imported")
except Exception as e:
    print(f"✗ boto3 import failed: {e}")
    sys.exit(1)

try:
    import requests
    print("✓ requests imported")
except Exception as e:
    print(f"✗ requests import failed: {e}")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
    print("✓ BeautifulSoup imported")
except Exception as e:
    print(f"✗ BeautifulSoup import failed: {e}")
    sys.exit(1)

try:
    from article_tagger import tag_article
    print("✓ article_tagger imported")
except Exception as e:
    print(f"✗ article_tagger import failed: {e}")
    sys.exit(1)

print("\nAll imports successful!")

# Test basic functionality
print("\nTesting basic functionality...")

try:
    # Test BeautifulSoup
    html = "<html><body><p>Test</p></body></html>"
    soup = BeautifulSoup(html, 'html.parser')
    print("✓ BeautifulSoup parsing works")
except Exception as e:
    print(f"✗ BeautifulSoup parsing failed: {e}")
    sys.exit(1)

try:
    # Test article_tagger
    result = tag_article("This is a test article about energy in the United States", ["energy", "test"])
    print("✓ article_tagger works:", result)
except Exception as e:
    print(f"✗ article_tagger failed: {e}")
    sys.exit(1)

print("\nAll tests passed!")