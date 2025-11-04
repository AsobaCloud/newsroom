#!/usr/bin/env python3
"""
Update Senado Content - Re-extract content for Brazilian Senate articles

This script iterates through historical legislation metadata, identifies senado.leg.br articles,
and re-extracts their content using the updated extraction logic.
"""

import json
import logging
import boto3
from typing import Dict, Optional

# Import extraction function from historical scraper
from historical_legislation_scraper import extract_full_article_content

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("update_senado_content")

S3_BUCKET_NAME = "news-collection-website"
HISTORICAL_FOLDER = "news/historical/legislation"

s3_client = boto3.client('s3')

def extract_senado_content(url: str) -> Optional[str]:
    """Extract content from senado.leg.br URL"""
    return extract_full_article_content(url)

def update_senado_articles():
    """Update content for all senado.leg.br articles"""
    logger.info("=== UPDATE SENADO CONTENT: Starting ===")
    
    # Get all metadata files
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(
        Bucket=S3_BUCKET_NAME,
        Prefix=f"{HISTORICAL_FOLDER}/metadata/"
    )
    
    senado_articles = []
    for page in pages:
        if 'Contents' not in page:
            continue
        
        for obj in page['Contents']:
            if obj['Key'].endswith('.json'):
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
    
    logger.info(f"Found {len(senado_articles)} senado.leg.br articles to update")
    
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
            article_id = metadata_key.split('/')[-1].replace('.json', '')
            content_key = f"{HISTORICAL_FOLDER}/content/{article_id}.html"
            
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
    
    logger.info(f"=== UPDATE SENADO CONTENT: Complete ({updated_count}/{len(senado_articles)} updated) ===")
    return updated_count

if __name__ == "__main__":
    try:
        updated = update_senado_articles()
        logger.info(f"\n✅ Senado content update complete!")
        logger.info(f"📊 Updated articles: {updated}")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        exit(1)
