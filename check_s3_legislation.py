#!/usr/bin/env python3
"""Check S3 for today's legislation articles"""
import boto3
from datetime import datetime

s3 = boto3.client('s3')
bucket = 'news-collection-website'
today = datetime.now().strftime('%Y-%m-%d')
today_folder = f"news/{today}"

print(f"Checking S3 for articles from {today}...")
print(f"Folder: s3://{bucket}/{today_folder}/")
print()

# List all objects under today's folder
try:
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=f"{today_folder}/")
    
    legislation_count = 0
    regular_count = 0
    total_metadata = 0
    
    for page in pages:
        if 'Contents' not in page:
            continue
        
        for obj in page['Contents']:
            key = obj['Key']
            
            # Count metadata files
            if key.endswith('.json') and '/metadata/' in key:
                total_metadata += 1
                
                # Download and check tags
                try:
                    response = s3.get_object(Bucket=bucket, Key=key)
                    import json
                    metadata = json.loads(response['Body'].read().decode('utf-8'))
                    tags = metadata.get('tags', {})
                    special_tags = tags.get('special_tags', [])
                    
                    if 'legislation' in special_tags:
                        legislation_count += 1
                        print(f"✓ Legislation article: {metadata.get('title', 'No title')[:60]}")
                        print(f"  Source: {metadata.get('source', 'Unknown')}")
                        print(f"  URL: {metadata.get('url', '')[:80]}")
                        print()
                    else:
                        regular_count += 1
                except Exception as e:
                    print(f"Error reading {key}: {e}")
    
    print(f"\nSummary for {today}:")
    print(f"  Total metadata files: {total_metadata}")
    print(f"  Legislation articles: {legislation_count}")
    print(f"  Regular articles: {regular_count}")
    
    if legislation_count == 0:
        print("\n⚠️  No legislation articles found!")
        print(f"Checking if {today_folder}/ exists...")
        
        # Check if folder exists
        response = s3.list_objects_v2(Bucket=bucket, Prefix=f"{today_folder}/", MaxKeys=1)
        if 'Contents' in response:
            print(f"✓ Folder exists")
        else:
            print(f"✗ Folder does not exist - no articles collected today yet")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
