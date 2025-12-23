#!/usr/bin/env python3
"""
Update Today's Senado Content - Re-extract content for Brazilian Senate articles from today

This script finds all senado.leg.br articles from today (2025-11-03) and re-extracts their content.
"""

import json
import logging
import boto3
import sys
import os
from datetime import datetime
from typing import Dict, Optional

# Add utils directory to path if running from root
if os.path.dirname(__file__) not in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))

# Import extraction function from historical scraper
from historical_legislation_scraper import extract_full_article_content

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("update_today_senado_content")

S3_BUCKET_NAME = "news-collection-website"
TODAY_FOLDER = "news/2025-11-03"

s3_client = boto3.client('s3')

def extract_senado_content(url: str) -> Optional[str]:
    """Extract content from senado.leg.br URL"""
    return extract_full_article_content(url)

def update_today_senado_articles():
    """Update content for all senado.leg.br articles from today"""
    logger.info("=== UPDATE TODAY'S SENADO CONTENT: Starting ===")
    
    # Get all metadata files from today
    paginator = s3_client.get_paginator('list_objects_v2')
    senado_articles = []
    
    for page in paginator.paginate(
        Bucket=S3_BUCKET_NAME,
        Prefix=f"{TODAY_FOLDER}/"
    ):
        if 'Contents' not in page:
            continue
        
        for obj in page['Contents']:
            if obj['Key'].endswith('.json') and '/metadata/' in obj['Key']:
                try:
                    response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=obj['Key'])
                    metadata = json.loads(response['Body'].read().decode('utf-8'))
                    url = metadata.get('url', '')
                    
                    if 'senado.leg.br' in url:
                        senado_articles.append({
                            'metadata_key': obj['Key'],
                            'metadata': metadata,
                            'url': url
                        })
                except Exception as e:
                    logger.debug(f"Error loading metadata {obj['Key']}: {e}")
                    continue
    
    logger.info(f"Found {len(senado_articles)} senado.leg.br articles from today to update")
    
    if not senado_articles:
        logger.info("No senado.leg.br articles found for today")
        return 0
    
    updated_count = 0
    for article in senado_articles:
        try:
            url = article['url']
            metadata = article['metadata']
            metadata_key = article['metadata_key']
            
            logger.info(f"Updating: {metadata.get('title', '')[:50]}...")
            
            # Extract content
            content = extract_senado_content(url)
            if not content:
                logger.warning(f"Could not extract content from {url}")
                continue
            
            # Generate content key from metadata key
            # metadata key format: news/2025-11-03/metadata/{article_id}.json
            # content key format: news/2025-11-03/content/{article_id}.html
            article_id = metadata_key.split('/')[-1].replace('.json', '')
            content_key = f"{TODAY_FOLDER}/content/{article_id}.html"
            
            # Upload updated content
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=content_key,
                Body=content.encode('utf-8'),
                ContentType='text/html'
            )
            
            # Update metadata with new content length
            metadata['content_length'] = len(content)
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=metadata_key,
                Body=json.dumps(metadata, indent=2).encode('utf-8'),
                ContentType='application/json'
            )
            
            updated_count += 1
            logger.info(f"✓ Updated: {metadata.get('title', '')[:50]}... ({len(content)} chars)")
            
        except Exception as e:
            logger.error(f"Error updating article {article.get('url', '')}: {e}")
            continue
    
    logger.info(f"=== UPDATE TODAY'S SENADO CONTENT: Complete ({updated_count}/{len(senado_articles)} updated) ===")
    return updated_count

if __name__ == "__main__":
    try:
        updated = update_today_senado_articles()
        logger.info(f"\n✅ Today's senado content update complete!")
        logger.info(f"📊 Updated articles: {updated}")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        exit(1)
