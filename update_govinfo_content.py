#!/usr/bin/env python3
"""
Update existing govinfo.gov content files with actual content

This script:
1. Finds all govinfo.gov articles in historical/legislation/metadata/
2. Re-extracts content using XML/HTML sources
3. Updates content files in S3
"""

import json
import logging
import requests
import hashlib
from bs4 import BeautifulSoup
from news_storage import S3_BUCKET_NAME, s3_client, upload_to_s3_if_not_exists

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("update_govinfo_content")

HISTORICAL_FOLDER = "news/historical/legislation"

def extract_govinfo_content(url: str) -> str:
    """Extract actual content from govinfo.gov URL"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Extract bill ID from URL (e.g., BILLS-119hr5853ih from /app/details/BILLS-119hr5853ih)
    bill_id = url.split('/app/details/')[-1].split('/')[0]
    if not bill_id:
        raise ValueError(f"Could not extract bill ID from URL: {url}")
    
    # Try XML first (cleanest format)
    xml_url = f"https://www.govinfo.gov/content/pkg/{bill_id}/xml/{bill_id}.xml"
    try:
        xml_response = requests.get(xml_url, headers=headers, timeout=30)
        if xml_response.status_code == 200 and len(xml_response.content) > 1000:
            # Parse XML and convert to HTML-like structure
            soup = BeautifulSoup(xml_response.content, 'xml')
            # Wrap in a body tag for consistent structure
            body_content = f"<body><div class='govinfo-content'>{str(soup)}</div></body>"
            logger.info(f"✓ Extracted XML content from {bill_id}")
            return body_content
    except Exception as e:
        logger.debug(f"Could not get XML for {bill_id}: {e}")
    
    # Fallback to HTML version
    html_url = f"https://www.govinfo.gov/content/pkg/{bill_id}/html/{bill_id}.htm"
    try:
        html_response = requests.get(html_url, headers=headers, timeout=30)
        if html_response.status_code == 200 and len(html_response.content) > 1000:
            soup = BeautifulSoup(html_response.content, 'html.parser')
            # Get the body content
            body = soup.find('body')
            if body:
                logger.info(f"✓ Extracted HTML content from {bill_id}")
                return str(body)
    except Exception as e:
        logger.debug(f"Could not get HTML for {bill_id}: {e}")
    
    raise ValueError(f"Could not extract content for {bill_id}")

def update_govinfo_articles():
    """Find and update all govinfo.gov articles"""
    logger.info("=== Updating Govinfo.gov Content ===")
    
    # Find all metadata files
    paginator = s3_client.get_paginator('list_objects_v2')
    govinfo_articles = []
    
    logger.info("Scanning metadata files for govinfo.gov URLs...")
    for page in paginator.paginate(
        Bucket=S3_BUCKET_NAME,
        Prefix=f"{HISTORICAL_FOLDER}/metadata/"
    ):
        if 'Contents' not in page:
            continue
        
        for obj in page['Contents']:
            if not obj['Key'].endswith('.json'):
                continue
            
            try:
                response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=obj['Key'])
                metadata = json.loads(response['Body'].read().decode('utf-8'))
                
                url = metadata.get('url', '')
                if 'govinfo.gov/app/details/' in url:
                    govinfo_articles.append({
                        'metadata_key': obj['Key'],
                        'url': url,
                        'title': metadata.get('title', 'Unknown'),
                        'article_id': hashlib.md5(url.encode()).hexdigest()
                    })
            except Exception as e:
                logger.debug(f"Error loading metadata {obj['Key']}: {e}")
                continue
    
    logger.info(f"Found {len(govinfo_articles)} govinfo.gov articles to update")
    
    # Update each article
    updated_count = 0
    failed_count = 0
    
    for article in govinfo_articles:
        try:
            logger.info(f"Updating: {article['title'][:50]}...")
            
            # Extract content
            content = extract_govinfo_content(article['url'])
            
            # Upload content file
            content_key = f"{HISTORICAL_FOLDER}/content/{article['article_id']}.html"
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=content_key,
                Body=content.encode('utf-8'),
                ContentType='text/html'
            )
            
            # Update metadata with new content length
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=article['metadata_key'])
            metadata = json.loads(response['Body'].read().decode('utf-8'))
            metadata['content_length'] = len(content)
            
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=article['metadata_key'],
                Body=json.dumps(metadata, indent=2).encode('utf-8'),
                ContentType='application/json'
            )
            
            updated_count += 1
            logger.info(f"✓ Updated: {article['title'][:50]}...")
            
        except Exception as e:
            failed_count += 1
            logger.error(f"✗ Failed to update {article['title'][:50]}: {e}")
            continue
    
    logger.info(f"\n=== Update Complete ===")
    logger.info(f"✓ Updated: {updated_count}")
    logger.info(f"✗ Failed: {failed_count}")
    logger.info(f"📁 Location: s3://{S3_BUCKET_NAME}/{HISTORICAL_FOLDER}/")

if __name__ == "__main__":
    try:
        update_govinfo_articles()
        logger.info("\n✅ Govinfo content update complete!")
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
