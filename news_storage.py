"""
Shared Storage Utilities for News Collection System

This module provides shared functions for storing articles to S3,
handling metadata, and managing progress tracking. Used by both
news_scraper.py (filtered content) and legislation_scraper.py (all legislation).
"""

import os
import json
import boto3
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger("news_storage")

# S3 Configuration - shared across all scrapers
S3_BUCKET_NAME = "news-collection-website"
s3_client = boto3.client('s3')

# Track uploaded files in memory (faster than repeated HEAD requests)
S3_MANIFEST = set()

def get_today_folder() -> str:
    """Get today's folder path for storing articles"""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"news/{today}"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for S3 compatibility"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"|?*\\'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def exists_in_s3(s3_key: str) -> bool:
    """Check if file exists in S3 (checks manifest first for speed)"""
    s3_key = sanitize_filename(s3_key)
    
    # Fast check: in-memory manifest
    if s3_key in S3_MANIFEST:
        return True
    
    # Slower check: actual S3 HEAD request
    try:
        s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        S3_MANIFEST.add(s3_key)  # Cache in manifest
        return True
    except s3_client.exceptions.NoSuchKey:
        return False
    except Exception as e:
        logger.error(f"Error checking S3 existence for {s3_key}: {e}")
        return False

def upload_to_s3_if_not_exists(file_content: bytes, s3_key: str, content_type: str = "text/html") -> bool:
    """
    Upload file to S3 if it doesn't already exist.
    Returns True if uploaded, False if already exists.
    """
    s3_key = sanitize_filename(s3_key)
    
    # Check manifest first (faster than HEAD request)
    if exists_in_s3(s3_key):
        logger.debug(f"Skipping (exists): {s3_key}")
        return False
    
    try:
        logger.info(f"Uploading to S3: {s3_key}")
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            ContentType=content_type
        )
        # Add to manifest
        S3_MANIFEST.add(s3_key)
        logger.info(f"✓ Uploaded: {s3_key}")
        return True
    except Exception as e:
        logger.error(f"Failed to upload {s3_key}: {e}")
        return False

def save_article(
    title: str,
    url: str,
    pub_date: str,
    description: str,
    full_content: str,
    feed_url: str,
    tags: Dict,
    source_type: str = "RSS Feed",
    folder_prefix: Optional[str] = None
) -> Optional[str]:
    """
    Save an article to S3 with metadata.
    
    Args:
        title: Article title
        url: Article URL
        pub_date: Publication date
        description: Article description
        full_content: Full article content (HTML)
        feed_url: Source RSS feed URL
        tags: Dictionary with tagging information (continents, topics, etc.)
        source_type: Type of source (default: "RSS Feed")
        folder_prefix: Optional folder prefix (e.g., "legislation" to separate from regular news)
    
    Returns:
        Article ID (MD5 hash of URL) if saved, None if already exists
    """
    # Generate unique ID from URL
    article_id = hashlib.md5(url.encode()).hexdigest()
    
    # Determine folder structure
    today_folder = get_today_folder()
    if folder_prefix:
        base_folder = f"{today_folder}/{folder_prefix}"
    else:
        base_folder = today_folder
    
    # Create metadata
    metadata = {
        'title': title,
        'url': url,
        'pub_date': pub_date,
        'description': description,
        'source': source_type,
        'feed_url': feed_url,
        'content_length': len(full_content),
        'collection_date': datetime.now().isoformat(),
        'tags': tags
    }
    
    # Save paths
    metadata_key = f"{base_folder}/metadata/{article_id}.json"
    content_key = f"{base_folder}/content/{article_id}.html"
    
    # Check if already exists
    if exists_in_s3(metadata_key) and exists_in_s3(content_key):
        logger.debug(f"Article already exists: {article_id}")
        return None
    
    # Save metadata
    if upload_to_s3_if_not_exists(
        json.dumps(metadata, indent=2).encode("utf-8"),
        metadata_key,
        "application/json"
    ):
        # Save full content
        if upload_to_s3_if_not_exists(
            full_content.encode('utf-8'),
            content_key
        ):
            logger.info(f"✓ Saved article: {title[:50]}...")
            return article_id
    
    return None

def get_all_articles_for_date(date_str: Optional[str] = None) -> List[Dict]:
    """
    Retrieve all article metadata for a given date (or today if not specified).
    
    Args:
        date_str: Date in YYYY-MM-DD format, or None for today
    
    Returns:
        List of article metadata dictionaries
    """
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    folder = f"news/{date_str}"
    articles = []
    
    try:
        # List all metadata files
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(
            Bucket=S3_BUCKET_NAME,
            Prefix=f"{folder}/"
        )
        
        for page in pages:
            if 'Contents' not in page:
                continue
            
            for obj in page['Contents']:
                if obj['Key'].endswith('.json') and '/metadata/' in obj['Key']:
                    try:
                        response = s3_client.get_object(
                            Bucket=S3_BUCKET_NAME,
                            Key=obj['Key']
                        )
                        metadata = json.loads(response['Body'].read())
                        articles.append(metadata)
                    except Exception as e:
                        logger.error(f"Error reading metadata {obj['Key']}: {e}")
                        continue
        
    except Exception as e:
        logger.error(f"Error retrieving articles for {date_str}: {e}")
    
    return articles
