#!/usr/bin/env python3
"""
Historical Legislation Scraper - One-off collection of all accessible legislative articles

This scraper collects ALL legislative articles from RSS feeds (no date filtering)
and saves them to a historical subfolder for a one-time historical collection page.
"""

import os
import re
import json
import time
import logging
import requests
import hashlib
import sys
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse, quote
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Import shared storage utilities
from news_storage import (
    save_article,
    exists_in_s3,
    S3_BUCKET_NAME,
    s3_client,
    upload_to_s3_if_not_exists
)
from article_tagger import detect_continents

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("historical_legislation_scraper")

# Historical folder path
HISTORICAL_FOLDER = "news/historical/legislation"

# Legislation RSS feeds (same as legislation_scraper.py)
LEGISLATION_RSS_FEEDS = [
    # US Legislation - Working sources
    'https://www.govinfo.gov/rss/bills.xml',  # GPO Bills (100 items)
    'https://www.rollcall.com/feed/',  # Roll Call Congress news
    'https://www.senate.gov/rss/press-releases.xml',  # Senate press releases
    
    # South Africa - Legislative news sources
    'https://mg.co.za/feed/',  # Mail & Guardian (SA news)
    'https://mg.co.za/politics/feed/',  # Mail & Guardian Politics (SA legislation focus)
    
    # UK (nice to have)
    'https://bills.parliament.uk/RSS/AllBills.rss',
    
    # EU (nice to have)
    'https://eur-lex.europa.eu/rss/en/oj_latest.xml',
    
    # Australia (nice to have)
    'https://www.aph.gov.au/rss/housebills',
    'https://www.aph.gov.au/rss/senatebills',
    
    # Brazil (nice to have)
    'https://www.camara.leg.br/noticias/rss/todas-as-noticias.xml',
    'https://www12.senado.leg.br/noticias/rss',
]

# Track processed URLs
processed_urls = set()

def url_already_processed(url: str) -> bool:
    """Check if URL was already processed"""
    return url in processed_urls

def add_processed_url(url: str):
    """Add URL to processed set"""
    processed_urls.add(url)

def load_processed_urls():
    """Load processed URLs from S3 metadata files"""
    global processed_urls
    
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(
            Bucket=S3_BUCKET_NAME,
            Prefix=f"{HISTORICAL_FOLDER}/metadata/"
        )
        
        for page in pages:
            if 'Contents' not in page:
                continue
            
            for obj in page['Contents']:
                if obj['Key'].endswith('.json'):
                    try:
                        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=obj['Key'])
                        metadata = json.loads(response['Body'].read().decode('utf-8'))
                        if 'url' in metadata:
                            processed_urls.add(metadata['url'])
                    except Exception as e:
                        logger.debug(f"Error loading metadata {obj['Key']}: {e}")
                        continue
        
        logger.info(f"Loaded {len(processed_urls)} processed URLs from S3")
    except Exception as e:
        logger.warning(f"Could not load processed URLs from S3: {e}")

# Load processed URLs at startup
load_processed_urls()

def extract_full_article_content(url: str) -> Optional[str]:
    """Extract full article content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Special handling for govinfo.gov - extract bill ID and get XML/HTML content
        if 'govinfo.gov/app/details/' in url:
            # Extract bill ID from URL (e.g., BILLS-119hr5853ih from /app/details/BILLS-119hr5853ih)
            bill_id = url.split('/app/details/')[-1].split('/')[0]
            if bill_id:
                # Try XML first (cleanest format)
                xml_url = f"https://www.govinfo.gov/content/pkg/{bill_id}/xml/{bill_id}.xml"
                try:
                    xml_response = requests.get(xml_url, headers=headers, timeout=30)
                    if xml_response.status_code == 200 and len(xml_response.content) > 1000:
                        # Parse XML and convert to HTML-like structure
                        soup = BeautifulSoup(xml_response.content, 'xml')
                        # Wrap in a body tag for consistent structure
                        body_content = f"<body><div class='govinfo-content'>{str(soup)}</div></body>"
                        logger.info(f"✓ Extracted govinfo.gov XML content from {bill_id}")
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
                            return str(body)
                except Exception as e:
                    logger.debug(f"Could not get HTML for {bill_id}: {e}")
        
        # Special handling for Brazilian Senate (senado.leg.br) - extract from #textoMateria
        if 'senado.leg.br' in url:
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove scripts and styles
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get article content from #textoMateria
                texto_materia = soup.select_one('#textoMateria')
                if texto_materia:
                    # Get title from #materia > h1 if available
                    materia = soup.select_one('#materia')
                    title = ''
                    if materia:
                        title_elem = materia.find('h1')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                    
                    # Get content text
                    content_text = texto_materia.get_text(separator='\n', strip=True)
                    
                    # Build HTML structure
                    body_content = f"<body><div class='senado-content'><h1>{title}</h1><div id='textoMateria'>{content_text}</div></div></body>"
                    logger.info(f"✓ Extracted senado.leg.br content from {url}")
                    return body_content
            except Exception as e:
                logger.debug(f"Could not extract senado.leg.br content: {e}")
        
        # Standard extraction for other URLs
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find main article content
        article_selectors = [
            'article',
            'main',
            '.article-content',
            '.post-content',
            '.entry-content',
            '#content',
            '.content',
        ]
        
        content = None
        for selector in article_selectors:
            content = soup.select_one(selector)
            if content:
                break
        
        if not content:
            # Fallback: use body
            content = soup.find('body')
        
        if content:
            return str(content)
        
        return None
        
    except Exception as e:
        logger.warning(f"Could not extract content from {url}: {e}")
        return None

def save_historical_article(title: str, url: str, pub_date: str, description: str, 
                           full_content: str, feed_url: str, tags: Dict) -> Optional[str]:
    """Save article to historical folder"""
    # Generate unique ID from URL
    article_id = hashlib.md5(url.encode()).hexdigest()
    
    # Create metadata
    metadata = {
        'title': title,
        'url': url,
        'pub_date': pub_date,
        'description': description,
        'source': 'Legislation Feed',
        'feed_url': feed_url,
        'content_length': len(full_content),
        'collection_date': datetime.now().isoformat(),
        'tags': tags
    }
    
    # Save paths
    metadata_key = f"{HISTORICAL_FOLDER}/metadata/{article_id}.json"
    content_key = f"{HISTORICAL_FOLDER}/content/{article_id}.html"
    
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

def process_single_historical_feed(feed_url: str):
    """Process a single legislation RSS feed - NO DATE FILTERING"""
    logger.info(f"Processing historical legislation RSS feed: {feed_url}")
    feed_count = 0
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(feed_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse RSS
        soup = BeautifulSoup(response.content, 'xml')
        
        # Try RSS format first
        items = soup.find_all('item')
        if not items:
            items = soup.find_all('entry')  # Atom format
        
        if not items:
            logger.warning(f"No items found in feed: {feed_url}")
            return 0
        
        logger.info(f"Found {len(items)} items in feed: {feed_url}")
        
        for item in items:
            try:
                # Extract title
                title_elem = item.find('title')
                title = title_elem.get_text() if title_elem else 'No Title'
                
                # Extract link
                link = None
                if item.find('link'):
                    link_elem = item.find('link')
                    if link_elem.get('href'):
                        link = link_elem.get('href')
                    else:
                        link = link_elem.get_text()
                
                # Handle date (but don't filter by it)
                pub_date = ''
                if item.find('pubDate'):
                    pub_date = item.find('pubDate').get_text()
                elif item.find('published'):
                    pub_date = item.find('published').get_text()
                elif item.find('updated'):
                    pub_date = item.find('updated').get_text()
                
                # Handle description
                description = ''
                if item.find('description'):
                    description = item.find('description').get_text()
                elif item.find('summary'):
                    description = item.find('summary').get_text()
                elif item.find('content'):
                    description = item.find('content').get_text()
                
                if not link:
                    continue
                
                # Check if already processed
                if url_already_processed(link):
                    logger.debug(f"URL already processed: {link}")
                    continue
                
                # NO DATE FILTERING - collect all articles
                
                # Extract full article content
                full_content = extract_full_article_content(link)
                if not full_content:
                    logger.warning(f"Could not extract content from: {link}")
                    continue
                
                # Tag the article
                combined_text = title + ' ' + description + ' ' + full_content
                
                tags = {
                    'continents': detect_continents(combined_text),
                    'matched_keywords': [],  # No keyword matching for legislation
                    'core_topics': []  # No topic matching for legislation
                }
                
                # Always add legislation tag
                special_tags = ['legislation']
                enhanced_tags = {
                    **tags,
                    'special_tags': special_tags
                }
                
                # Save article to historical folder
                article_id = save_historical_article(
                    title=title,
                    url=link,
                    pub_date=pub_date,
                    description=description,
                    full_content=full_content,
                    feed_url=feed_url,
                    tags=enhanced_tags
                )
                
                if article_id:
                    feed_count += 1
                    add_processed_url(link)
                    logger.info(f"✓ Saved historical legislation article: {title[:50]}...")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.debug(f"Error processing RSS item: {str(e)}")
                continue
        
        logger.info(f"Completed feed: {feed_url} ({feed_count} articles)")
        return feed_count
        
    except Exception as e:
        logger.error(f"Error processing RSS feed {feed_url}: {str(e)}")
        return 0

def process_historical_feeds():
    """Process all legislation RSS feeds for historical collection"""
    logger.info("=== HISTORICAL LEGISLATION SCRAPER: Starting ===")
    logger.info(f"Saving to: s3://{S3_BUCKET_NAME}/{HISTORICAL_FOLDER}/")
    
    # Process feeds in parallel
    logger.info(f"Processing {len(LEGISLATION_RSS_FEEDS)} legislation RSS feeds in parallel...")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_single_historical_feed, LEGISLATION_RSS_FEEDS))
    
    total_processed = sum(results)
    logger.info(f"=== HISTORICAL LEGISLATION SCRAPER: Complete ({total_processed} total articles) ===")
    logger.info(f"✓ All historical articles saved to s3://{S3_BUCKET_NAME}/{HISTORICAL_FOLDER}/")
    
    return total_processed

if __name__ == "__main__":
    try:
        total = process_historical_feeds()
        logger.info(f"\n✅ Historical legislation collection complete!")
        logger.info(f"📊 Total articles collected: {total}")
        logger.info(f"📁 Location: s3://{S3_BUCKET_NAME}/{HISTORICAL_FOLDER}/")
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
