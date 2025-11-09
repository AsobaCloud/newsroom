#!/usr/bin/env python3
"""
Legislation Scraper - Collects ALL articles from legislative sources

This scraper bypasses keyword filtering to collect all legislation-related content
from government and legislative news sources. It uses the same S3 bucket and
storage utilities as news_scraper.py but does not filter by keywords.
"""

import os
import re
import json
import time
import logging
import requests
import hashlib
import sys
import argparse
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse, quote
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Import shared storage utilities
from news_storage import (
    save_article,
    get_today_folder,
    exists_in_s3,
    S3_BUCKET_NAME
)

# Import tagging functionality
from article_tagger import tag_article, detect_continents

# Import progress tracking (we'll create a shared one or duplicate the class)
import json as json_module

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("legislation_scraper")

# Set fresh mode flag
FRESH_MODE = os.environ.get('FRESH_MODE', 'false').lower() == 'true'

if not os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    parser = argparse.ArgumentParser(description='Legislation Scraper - Collects all legislative content')
    parser.add_argument('-fresh', '--fresh', action='store_true', 
                       help='Run in fresh mode - bypass idempotency and reprocess all articles')
    args = parser.parse_args()
    FRESH_MODE = args.fresh

# Track progress
PROGRESS_FILE = "/tmp/legislation_scraper_progress.json" if os.environ.get('AWS_LAMBDA_FUNCTION_NAME') else "legislation_scraper_progress.json"

# Progress tracking class (duplicated from news_scraper or could be extracted)
class ProgressTracker:
    def __init__(self, progress_file=PROGRESS_FILE):
        self.progress_file = progress_file
        self.progress = self.load_progress()
    
    def load_progress(self):
        """Load progress from file or initialize new"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json_module.load(f)
        return {
            "rss_feeds": {"feeds_completed": []},
            "total_articles": 0,
            "last_updated": None
        }
    
    def save_progress(self):
        """Save current progress"""
        self.progress["last_updated"] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json_module.dump(self.progress, f, indent=2)
    
    def mark_feed_complete(self, feed_url):
        """Mark a feed as completed"""
        if feed_url not in self.progress["rss_feeds"]["feeds_completed"]:
            self.progress["rss_feeds"]["feeds_completed"].append(feed_url)
            self.save_progress()
    
    def is_feed_complete(self, feed_url):
        """Check if feed was already processed"""
        if FRESH_MODE:
            return False
        return feed_url in self.progress["rss_feeds"].get("feeds_completed", [])

progress_tracker = ProgressTracker()

# URL deduplication tracking
processed_urls = set()

def url_already_processed(url: str) -> bool:
    """Check if URL was already processed"""
    if FRESH_MODE:
        return False
    return url in processed_urls

def add_processed_url(url: str):
    """Add URL to processed set"""
    processed_urls.add(url)

# Track processed URLs from S3
def load_processed_urls():
    """Load processed URLs from S3 metadata files"""
    global processed_urls
    today_folder = get_today_folder()
    
    try:
        import boto3
        s3 = boto3.client('s3')
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(
            Bucket=S3_BUCKET_NAME,
            Prefix=f"{today_folder}/"
        )
        
        for page in pages:
            if 'Contents' not in page:
                continue
            
            for obj in page['Contents']:
                if obj['Key'].endswith('.json') and '/metadata/' in obj['Key']:
                    try:
                        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=obj['Key'])
                        metadata = json_module.loads(response['Body'].read().decode('utf-8'))
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

# -------------------------------------------------------------------------
# LEGISLATION RSS FEEDS
# -------------------------------------------------------------------------

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

# -------------------------------------------------------------------------
# DATE FILTERING
# -------------------------------------------------------------------------

def is_recent_article(pub_date: str, days: int = 1) -> bool:
    """Check if article is from the past N days (default: 1 day = 24 hours)"""
    if not pub_date:
        return True  # If no date, include it (assume recent)
    
    try:
        from dateutil import parser
        from dateutil.tz import tzutc
        
        # Parse the publication date
        parsed_date = parser.parse(pub_date)
        
        # Make timezone-aware if not already
        if parsed_date.tzinfo is None:
            parsed_date = parsed_date.replace(tzinfo=tzutc())
        
        # Calculate the cutoff date (N days ago)
        cutoff_date = datetime.now(tzutc()) - timedelta(days=days)
        
        # Check if article is newer than cutoff
        return parsed_date >= cutoff_date
        
    except Exception as e:
        # If we can't parse the date, check if it's from 2025 or later
        # (fallback to same logic as news_scraper)
        year_patterns = [
            r'(\d{4})',  # Any 4-digit year
            r'(\d{4}-\d{2}-\d{2})',  # ISO format
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, pub_date)
            if match:
                year_str = match.group(1)[:4]
                try:
                    year = int(year_str)
                    # Only include if 2025 or later (current year)
                    return year >= 2025
                except ValueError:
                    continue
        
        # If we can't parse, assume it's recent and include it
        logger.debug(f"Could not parse date '{pub_date}', including article")
        return True

# -------------------------------------------------------------------------
# CONTENT EXTRACTION
# -------------------------------------------------------------------------

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
                        logger.info(f"? Extracted govinfo.gov XML content from {bill_id}")
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
                    logger.info(f"? Extracted senado.leg.br content from {url}")
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
            '.article-content',
            '.article-body',
            '.post-content',
            '.entry-content',
            'main',
            '#content',
            '.content',
        ]
        
        article_content = None
        for selector in article_selectors:
            content = soup.select_one(selector)
            if content:
                article_content = content
                break
        
        if not article_content:
            # Fallback: use body
            article_content = soup.find('body')
            if not article_content:
                article_content = soup
        
        # Extract text
        text = article_content.get_text(separator='\n', strip=True)
        return text if text else None
        
    except Exception as e:
        logger.warning(f"Error extracting content from {url}: {e}")
        return None

# -------------------------------------------------------------------------
# RSS FEED PROCESSING
# -------------------------------------------------------------------------

def process_single_legislation_feed(feed_url: str):
    """Process a single legislation RSS feed - NO KEYWORD FILTERING"""
    if progress_tracker.is_feed_complete(feed_url):
        logger.info(f"Skipping completed feed: {feed_url}")
        return 0
        
    logger.info(f"Processing legislation RSS feed: {feed_url}")
    feed_count = 0
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(feed_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse RSS/Atom
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        if not items:
            items = soup.find_all('entry')  # Atom feeds
        
        logger.info(f"Found {len(items)} items in feed")
        
        for item in items:
            try:
                # Extract item data
                title = item.find('title')
                title = title.get_text() if title else 'No Title'
                
                # Handle link
                link = None
                if item.find('link'):
                    link_elem = item.find('link')
                    if link_elem.get('href'):
                        link = link_elem.get('href')
                    else:
                        link = link_elem.get_text()
                
                # Handle date
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
                
                # Check if article is from the past 24 hours (recent)
                if not is_recent_article(pub_date, days=1):
                    logger.debug(f"Filtering out old article: {title[:50]}... (date: {pub_date})")
                    continue
                
                # Extract full article content
                full_content = extract_full_article_content(link)
                if not full_content:
                    logger.warning(f"Could not extract content from: {link}")
                    continue
                
                # Tag the article (but DON'T filter by keywords)
                combined_text = title + ' ' + description + ' ' + full_content
                
                # Tag the article for geographic/topical info
                # (legislation articles bypass keyword filtering)
                tags = {
                    'continents': detect_continents(combined_text),
                    'matched_keywords': [],  # No keyword matching for legislation
                    'core_topics': []  # No topic matching for legislation
                }
                
                # Always add legislation tag
                special_tags = ['legislation']
                
                # Enhanced tags with legislation
                enhanced_tags = {
                    **tags,
                    'special_tags': special_tags
                }
                
                # Save article (uses same folder structure as news_scraper)
                # folder_prefix=None means it goes in same location as regular news
                article_id = save_article(
                    title=title,
                    url=link,
                    pub_date=pub_date,
                    description=description,
                    full_content=full_content,
                    feed_url=feed_url,
                    tags=enhanced_tags,
                    source_type='Legislation Feed'
                )
                
                if article_id:
                    feed_count += 1
                    progress_tracker.mark_feed_complete(feed_url)  # Actually mark per article
                    add_processed_url(link)
                    logger.info(f"? Saved legislation article: {title[:50]}...")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.debug(f"Error processing RSS item: {str(e)}")
                continue
        
        progress_tracker.mark_feed_complete(feed_url)
        logger.info(f"Completed feed: {feed_url} ({feed_count} articles)")
        return feed_count
        
    except Exception as e:
        logger.error(f"Error processing RSS feed {feed_url}: {str(e)}")
        return 0

def process_legislation_feeds():
    """Process all legislation RSS feeds"""
    if FRESH_MODE:
        logger.info("?? FRESH MODE: Bypassing idempotency - reprocessing all legislation feeds")
        if os.path.exists(PROGRESS_FILE):
            try:
                os.remove(PROGRESS_FILE)
                logger.info("??? Cleared legislation progress file for fresh collection")
            except OSError as e:
                logger.warning(f"Could not remove legislation progress file: {e}")
        progress_tracker.progress = {
            "rss_feeds": {"feeds_completed": []},
            "total_articles": 0,
            "last_updated": None
        }
    else:
        logger.info("?? IDEMPOTENT MODE: Skipping already processed legislation feeds")

    logger.info("=== LEGISLATION SCRAPER: Starting ===")
    
    # Filter out already completed feeds
    feeds_to_process = [feed for feed in LEGISLATION_RSS_FEEDS 
                       if not progress_tracker.is_feed_complete(feed)]
    
    if not feeds_to_process:
        logger.info("All legislation feeds already completed")
        return
    
    logger.info(f"Processing {len(feeds_to_process)} legislation RSS feeds in parallel...")
    
    # Process feeds in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_single_legislation_feed, feeds_to_process))
    
    total_processed = sum(results)
    logger.info(f"=== LEGISLATION SCRAPER: Complete ({total_processed} total articles) ===")
    logger.info(f"? All legislation articles saved to s3://{S3_BUCKET_NAME}/{get_today_folder()}/")

# -------------------------------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        process_legislation_feeds()
        logger.info("Legislation scraping complete!")
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
