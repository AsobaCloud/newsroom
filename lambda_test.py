import json
import os
import subprocess
import sys
from datetime import datetime

def lambda_handler(event, context):
    """
    Simple test to diagnose the segfault issue
    """
    
    try:
        print(f"Current directory: {os.getcwd()}")
        print(f"Files in current directory: {os.listdir('.')}")
        
        # Test 1: Can we import the modules?
        print("Testing imports...")
        try:
            import requests
            print("✓ requests imported")
        except Exception as e:
            print(f"✗ requests import failed: {e}")
            
        try:
            import boto3
            print("✓ boto3 imported")
        except Exception as e:
            print(f"✗ boto3 import failed: {e}")
            
        try:
            from bs4 import BeautifulSoup
            print("✓ BeautifulSoup imported")
        except Exception as e:
            print(f"✗ BeautifulSoup import failed: {e}")
            
        try:
            from article_tagger import tag_article
            print("✓ article_tagger imported")
        except Exception as e:
            print(f"✗ article_tagger import failed: {e}")
        
        # Test 2: Can we run a simple Python script?
        print("Testing simple Python execution...")
        result = subprocess.run([
            sys.executable, '-c', 'print("Hello from subprocess")'
        ], capture_output=True, text=True, timeout=30)
        
        print(f"Simple test return code: {result.returncode}")
        print(f"Simple test stdout: {result.stdout}")
        print(f"Simple test stderr: {result.stderr}")
        
        # Test 3: Can we run a minimal version of the scraper?
        print("Testing minimal scraper...")
        minimal_script = '''
import sys
print("Starting minimal scraper test")
try:
    import requests
    print("requests OK")
    import boto3
    print("boto3 OK")
    from bs4 import BeautifulSoup
    print("BeautifulSoup OK")
    from article_tagger import tag_article
    print("article_tagger OK")
    print("All imports successful")
except Exception as e:
    print(f"Import error: {e}")
    sys.exit(1)
print("Minimal test completed successfully")
'''
        
        with open('minimal_test.py', 'w') as f:
            f.write(minimal_script)
            
        result = subprocess.run([
            sys.executable, 'minimal_test.py'
        ], capture_output=True, text=True, timeout=30)
        
        print(f"Minimal test return code: {result.returncode}")
        print(f"Minimal test stdout: {result.stdout}")
        print(f"Minimal test stderr: {result.stderr}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Diagnostic test completed',
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Diagnostic test failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })
        }