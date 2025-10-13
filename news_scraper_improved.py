#!/usr/bin/env python3
"""
2025 News Scraper with Static Website Hosting - IMPROVED VERSION
Target: All news available from 2025 on energy/AI/blockchain topics with full article content
Destination: s3://news-collection-website/ (static website hosting)
Features: Master index for browsing all collected dates

PHASE 1 IMPROVEMENTS:
- Fixed broken RSS feeds
- Improved content extraction success rate
- Added proper HTTP error handling
- Enhanced error logging and debugging
"""

import os
import re
import json
import time
import boto3
import logging
import requests
import hashlib
import argparse
import sys
from datetime import datetime, date
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse, quote
from bs4 import BeautifulSoup
from article_tagger import tag_article
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger("news_scraper_improved")

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------

# S3 Configuration - NEW BUCKET FOR STATIC WEBSITE
S3_BUCKET_NAME = "news-collection-website"
# Generate datestamped folder name
today = datetime.now().strftime("%Y-%m-%d")
S3_FOLDER_NEWS = f"news/{today}"

# Fresh mode flag (set by command line argument)
FRESH_MODE = False

# Track progress
PROGRESS_FILE = "news_scraper_progress.json"

# Search keywords - comprehensive energy, AI, blockchain, and finance terms
NEWS_KEYWORDS = [
    # Core topics
    "energy", "electricity", "blockchain", "artificial intelligence", "AI", "insurance",
    
    # Energy technologies
    "renewable energy", "solar power", "wind energy", "battery storage",
    "smart grid", "microgrid", "electric vehicles", "capacity market",
    "demand response", "carbon pricing", "carbon tax", "feed-in tariff",
    "grid reliability", "transmission planning", "levelized cost of energy", 
    "power purchase agreement", "green bond", "ESG investment", "coal", "rare earth minerals", "lithium", "nuclear",
    "gas","oil","supply chain",

    
    # Insurance/Risk
    "catastrophe modeling", "exposure data", "reinsurance", "underwriting", 
    "climate risk", "war","civil unrest","protest","climate risk",
    
    # Technology
    "cybersecurity", "digital twin", "predictive analytics",
    
    # Major agencies and regulatory bodies
    "Federal Energy Regulatory Commission", "FERC",
    "North American Electric Reliability Corporation", "NERC",
    "Department of Energy", "DOE",
    "Environmental Protection Agency", "EPA",
    "National Renewable Energy Laboratory", "NREL",
    "International Energy Agency", "IEA",
    "Commodity Futures Trading Commission", "CFTC",
    "Insurance Regulatory and Development Authority", "IRDAI",
    "Standard & Poor's", "Moody's", "Fitch",
    "Bloomberg"
]

# PHASE 1 FIX: Updated news sources - removed broken feeds, added working ones
NEWS_SOURCES = {
    'rss_feeds': [
        # BBC News (confirmed working)
        'https://feeds.bbci.co.uk/news/rss.xml',
        'https://feeds.bbci.co.uk/news/world/rss.xml',
        'https://feeds.bbci.co.uk/news/business/rss.xml',
        'https://feeds.bbci.co.uk/news/technology/rss.xml',
        'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
        
        # CNN (working feeds)
        'http://rss.cnn.com/rss/cnn_topstories.rss',
        'http://rss.cnn.com/rss/edition.rss',
        'http://rss.cnn.com/rss/cnn_world.rss',
        'http://rss.cnn.com/rss/edition_technology.rss',  # Added working tech feed
        
        # Guardian (confirmed working)
        'https://www.theguardian.com/world/rss',
        'https://www.theguardian.com/business/rss',
        'https://www.theguardian.com/technology/rss',
        'https://www.theguardian.com/environment/rss',
        
        # Al Jazeera
        'https://www.aljazeera.com/xml/rss/all.xml',
        
        # Financial/Business - FIXED: Replaced broken feeds
        'https://feeds.reuters.com/reuters/businessNews',  # Replaced Yahoo Finance
        'https://feeds.reuters.com/reuters/technologyNews',  # Added Reuters tech
        
        # Tech/Industry
        'https://feeds.arstechnica.com/arstechnica/index',
        'https://techcrunch.com/feed/',
        'https://www.wired.com/feed/rss',
        'https://feeds.feedburner.com/oreilly/radar',  # Replaced broken VentureBeat
        
        # Academic/Research - FIXED: Removed broken arXiv feeds
        # 'https://rss.arxiv.org/rss/econ',  # Removed - not working
        # 'https://rss.arxiv.org/rss/cs.AI',  # Removed - not working
        # 'https://rss.arxiv.org/rss/cs.CL',  # Removed - not working
        
        # Energy/Policy focused - FIXED: Replaced broken feeds
        'https://www.eia.gov/rss/todayinenergy.xml',  # Replaced broken energy.gov
        'https://feeds.cfr.org/feeds/site/current.xml'
    ],
    'news_apis': [
        'https://newsapi.org/v2/everything',  # Requires API key
        'https://api.nytimes.com/svc/search/v2/articlesearch.json'  # Requires API key
    ],
    'direct_scraping': [
        'https://techcrunch.com/',
        'https://www.theverge.com/',
        'https://arstechnica.com/',
        'https://www.wired.com/',
        'https://www.coindesk.com/',
        'https://cointelegraph.com/'
        # Removed Reuters due to 401 errors
    ]
}

s3_client = boto3.client("s3", region_name="us-east-1")

# -------------------------------------------------------------------------
# PHASE 1 FIX: Enhanced Error Handling and Retry Logic
# -------------------------------------------------------------------------

def retry_with_backoff(max_retries=3, base_delay=1):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Max retries exceeded for {func.__name__}: {e}")
                        raise
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Retry {attempt + 1}/{max_retries} for {func.__name__} in {delay}s: {e}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

def handle_http_errors(response: requests.Response) -> bool:
    """Handle HTTP errors gracefully with detailed logging"""
    if response.status_code == 401:
        logger.warning(f"Authentication required for {response.url}")
        return False
    elif response.status_code == 404:
        logger.warning(f"Resource not found: {response.url}")
        return False
    elif response.status_code == 403:
        logger.warning(f"Access forbidden: {response.url}")
        return False
    elif response.status_code >= 500:
        logger.warning(f"Server error {response.status_code}: {response.url}")
        return False
    elif response.status_code == 400:
        logger.warning(f"Bad request: {response.url}")
        return False
    return True

def validate_feed(feed_url: str) -> bool:
    """Validate RSS feed before processing"""
    try:
        logger.debug(f"Validating feed: {feed_url}")
        response = requests.head(feed_url, timeout=10)
        if response.status_code == 200:
            logger.debug(f"Feed validation successful: {feed_url}")
            return True
        else:
            logger.warning(f"Feed validation failed {response.status_code}: {feed_url}")
            return False
    except Exception as e:
        logger.warning(f"Feed validation error for {feed_url}: {e}")
        return False

# -------------------------------------------------------------------------
# PHASE 1 FIX: Site-Specific Content Extractors
# -------------------------------------------------------------------------

def extract_cnn_content(soup: BeautifulSoup) -> Optional[str]:
    """CNN-specific content extraction with video handling"""
    logger.debug("Using CNN-specific content extractor")
    
    # Handle video content
    video_content = soup.find('div', class_='video-content')
    if video_content:
        logger.debug("Found CNN video content")
        return video_content.get_text(strip=True)
    
    # Standard article content selectors for CNN
    content_selectors = [
        '.article__content',
        '.l-container .zn-body__paragraph',
        '.article-content',
        '.story-body',
        'article .zn-body__paragraph'
    ]
    
    for selector in content_selectors:
        content_element = soup.select_one(selector)
        if content_element:
            content = content_element.get_text(strip=True)
            if len(content) > 200:
                logger.debug(f"CNN content extracted using selector '{selector}': {len(content)} chars")
                return content
    
    logger.warning("CNN content extraction failed - no suitable selectors found")
    return None

def extract_venturebeat_content(soup: BeautifulSoup) -> Optional[str]:
    """VentureBeat-specific content extraction"""
    logger.debug("Using VentureBeat-specific content extractor")
    
    content_selectors = [
        '.article-content',
        '.entry-content',
        '.post-content',
        '.article-body',
        'article .content'
    ]
    
    for selector in content_selectors:
        content_element = soup.select_one(selector)
        if content_element:
            content = content_element.get_text(strip=True)
            if len(content) > 200:
                logger.debug(f"VentureBeat content extracted using selector '{selector}': {len(content)} chars")
                return content
    
    logger.warning("VentureBeat content extraction failed - no suitable selectors found")
    return None

def extract_arstechnica_content(soup: BeautifulSoup) -> Optional[str]:
    """ArsTechnica-specific content extraction"""
    logger.debug("Using ArsTechnica-specific content extractor")
    
    content_selectors = [
        '.article-content',
        '.entry-content',
        'article .post-content',
        '.article-body',
        'article .content'
    ]
    
    for selector in content_selectors:
        content_element = soup.select_one(selector)
        if content_element:
            content = content_element.get_text(strip=True)
            if len(content) > 200:
                logger.debug(f"ArsTechnica content extracted using selector '{selector}': {len(content)} chars")
                return content
    
    logger.warning("ArsTechnica content extraction failed - no suitable selectors found")
    return None

def extract_reuters_content(soup: BeautifulSoup) -> Optional[str]:
    """Reuters-specific content extraction"""
    logger.debug("Using Reuters-specific content extractor")
    
    content_selectors = [
        '.StandardArticleBody_body',
        '.ArticleBodyWrapper',
        '.article-body',
        '.story-body',
        'article .content'
    ]
    
    for selector in content_selectors:
        content_element = soup.select_one(selector)
        if content_element:
            content = content_element.get_text(strip=True)
            if len(content) > 200:
                logger.debug(f"Reuters content extracted using selector '{selector}': {len(content)} chars")
                return content
    
    logger.warning("Reuters content extraction failed - no suitable selectors found")
    return None

# -------------------------------------------------------------------------
# PROGRESS TRACKING
# -------------------------------------------------------------------------
class ProgressTracker:
    def __init__(self, progress_file=PROGRESS_FILE):
        self.progress_file = progress_file
        self.progress = self.load_progress()
    
    def load_progress(self):
        """Load progress from file or initialize new"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {
            "rss_feeds": {"feeds_completed": []},
            "direct_scraping": {"sources_completed": []},
            "total_articles": 0,
            "last_updated": None,
            "extraction_stats": {
                "successful_extractions": 0,
                "failed_extractions": 0,
                "site_specific_success": 0
            }
        }
    
    def save_progress(self):
        """Save current progress"""
        self.progress["last_updated"] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def mark_feed_complete(self, feed_url):
        """Mark a feed as completed"""
        if feed_url not in self.progress["rss_feeds"]["feeds_completed"]:
            self.progress["rss_feeds"]["feeds_completed"].append(feed_url)
            self.save_progress()
    
    def is_feed_complete(self, feed_url):
        """Check if feed was already processed"""
        return feed_url in self.progress["rss_feeds"].get("feeds_completed", [])
    
    def mark_source_complete(self, source_url):
        """Mark a source as completed"""
        if source_url not in self.progress["direct_scraping"]["sources_completed"]:
            self.progress["direct_scraping"]["sources_completed"].append(source_url)
            self.save_progress()
    
    def is_source_complete(self, source_url):
        """Check if source was already processed"""
        return source_url in self.progress["direct_scraping"].get("sources_completed", [])
    
    def increment_articles(self, count=1):
        """Increment total article count"""
        self.progress["total_articles"] += count
        self.save_progress()
    
    def record_extraction_success(self, site_specific=False):
        """Record successful content extraction"""
        self.progress["extraction_stats"]["successful_extractions"] += 1
        if site_specific:
            self.progress["extraction_stats"]["site_specific_success"] += 1
        self.save_progress()
    
    def record_extraction_failure(self):
        """Record failed content extraction"""
        self.progress["extraction_stats"]["failed_extractions"] += 1
        self.save_progress()

progress_tracker = ProgressTracker()

# -------------------------------------------------------------------------
# IDEMPOTENT S3 OPERATIONS
# -------------------------------------------------------------------------
def get_s3_manifest():
    """Get manifest of all files already in S3 bucket/prefix"""
    manifest = set()
    article_urls = set()  # Track URLs we've already processed
    
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(
            Bucket=S3_BUCKET_NAME,
            Prefix=S3_FOLDER_NEWS + "/"
        )
        
        for page in page_iterator:
            if 'Contents' in page:
                for obj in page['Contents']:
                    manifest.add(obj['Key'])
                    
                    # Extract URLs from metadata files for URL-based deduplication
                    if obj['Key'].endswith('.json') and '/metadata/' in obj['Key']:
                        try:
                            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=obj['Key'])
                            metadata = json.loads(response['Body'].read().decode('utf-8'))
                            if 'url' in metadata:
                                article_urls.add(metadata['url'])
                        except Exception as e:
                            logger.debug(f"Could not extract URL from {obj['Key']}: {e}")
        
        logger.info(f"S3 manifest loaded: {len(manifest)} existing files, {len(article_urls)} unique article URLs")
        return manifest, article_urls
    except Exception as e:
        logger.error(f"Error loading S3 manifest: {str(e)}")
        return set(), set()

# Global manifest for idempotency
S3_MANIFEST, S3_PROCESSED_URLS = get_s3_manifest()

def exists_in_s3(key: str) -> bool:
    """Check if file exists in S3 using manifest"""
    return key in S3_MANIFEST

def url_already_processed(url: str) -> bool:
    """Check if URL was already processed (idempotency across runs)"""
    return url in S3_PROCESSED_URLS

def add_processed_url(url: str):
    """Add URL to processed set"""
    S3_PROCESSED_URLS.add(url)

def sanitize_filename(key: str) -> str:
    parts = key.split("/")
    filename = parts[-1].strip()
    filename = filename.replace("\\", "_")
    filename = re.sub(r"\s+", "_", filename)
    filename = re.sub(r"[^\w\.-]", "_", filename)
    parts[-1] = filename
    return "/".join(parts)

def upload_to_s3_if_not_exists(file_content: bytes, s3_key: str, content_type: str = "text/html"):
    s3_key = sanitize_filename(s3_key)
    
    # Check manifest first (faster than HEAD request)
    if exists_in_s3(s3_key):
        logger.debug(f"Skipping (exists in manifest): {s3_key}")
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

# -------------------------------------------------------------------------
# PHASE 1 FIX: Enhanced News Extraction Utilities
# -------------------------------------------------------------------------
@retry_with_backoff(max_retries=2, base_delay=1)
def try_archive_fallback(url: str) -> Optional[str]:
    """Try to get article content from archive.is with retry logic"""
    try:
        logger.debug(f"Attempting archive.is fallback for: {url}")
        # Try to find existing archive
        archive_search_url = f"https://archive.today/newest/{url}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(archive_search_url, headers=headers, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for archived version link
            archive_links = soup.find_all('a', href=re.compile(r'archive\.today|archive\.is'))
            if archive_links:
                archive_url = archive_links[0]['href']
                if not archive_url.startswith('http'):
                    archive_url = 'https://archive.today' + archive_url
                
                logger.info(f"Found archive version: {archive_url}")
                return extract_full_article_content(archive_url)
        
        # If no existing archive, try to create one
        logger.info(f"Attempting to archive: {url}")
        archive_create_url = "https://archive.today/submit/"
        data = {'url': url}
        
        response = requests.post(archive_create_url, data=data, headers=headers, timeout=60)
        if response.status_code == 200:
            # Archive creation initiated, but we won't wait for completion
            logger.info(f"Archive creation initiated for: {url}")
        
        return None
        
    except Exception as e:
        logger.debug(f"Archive.is fallback failed for {url}: {str(e)}")
        return None

def is_recent_article(article_date_str: str) -> bool:
    """Check if article is from the last 24 hours for fresh news"""
    if not article_date_str:
        # If no date, assume it's recent and include it
        return True
    
    try:
        from dateutil import parser
        from datetime import datetime, timedelta
        
        # Parse the article date
        article_date = parser.parse(article_date_str)
        
        # Get current time and 24 hours ago
        now = datetime.now(article_date.tzinfo) if article_date.tzinfo else datetime.now()
        twenty_four_hours_ago = now - timedelta(hours=24)
        
        # Check if article is within last 24 hours
        return article_date >= twenty_four_hours_ago
        
    except Exception as e:
        # If we can't parse the date, assume it's recent and include it
        logger.debug(f"Could not parse date '{article_date_str}': {e}")
        return True

def extract_full_article_content(url: str) -> Optional[str]:
    """Extract full article content from URL with enhanced site-specific handling"""
    try:
        logger.debug(f"Extracting content from: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # PHASE 1 FIX: Handle HTTP errors gracefully
        if not handle_http_errors(response):
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'ads']):
            element.decompose()
        
        # PHASE 1 FIX: Try site-specific extractors first
        domain = urlparse(url).netloc.lower()
        site_extractors = {
            'cnn.com': extract_cnn_content,
            'www.cnn.com': extract_cnn_content,
            'venturebeat.com': extract_venturebeat_content,
            'www.venturebeat.com': extract_venturebeat_content,
            'arstechnica.com': extract_arstechnica_content,
            'www.arstechnica.com': extract_arstechnica_content,
            'reuters.com': extract_reuters_content,
            'www.reuters.com': extract_reuters_content
        }
        
        if domain in site_extractors:
            logger.debug(f"Using site-specific extractor for {domain}")
            content = site_extractors[domain](soup)
            if content:
                logger.debug(f"Site-specific extraction successful: {len(content)} chars")
                progress_tracker.record_extraction_success(site_specific=True)
                return content
        
        # Fallback to generic extraction
        logger.debug("Using generic content extraction")
        content_selectors = [
            'article',
            '[data-module="ArticleBody"]',
            '.article-body',
            '.story-body',
            '.post-content',
            '.entry-content',
            '.content',
            'main',
            '.article-content'
        ]
        
        article_content = None
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                article_content = content_element.get_text(strip=True)
                if len(article_content) > 200:  # Ensure we got substantial content
                    logger.debug(f"Generic extraction successful using selector '{selector}': {len(article_content)} chars")
                    break
        
        if not article_content:
            # Fallback: get all paragraph text
            paragraphs = soup.find_all('p')
            article_content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        if article_content and len(article_content) > 100:
            progress_tracker.record_extraction_success(site_specific=False)
            return article_content
        else:
            logger.warning(f"Content extraction failed - insufficient content: {len(article_content) if article_content else 0} chars")
            progress_tracker.record_extraction_failure()
            return None
        
    except Exception as e:
        logger.warning(f"Direct extraction failed for {url}: {str(e)}")
        progress_tracker.record_extraction_failure()
        
        # Try archive.is fallback
        logger.info(f"Trying archive.is fallback for: {url}")
        return try_archive_fallback(url)

def matches_keywords(text: str) -> bool:
    """Check if text contains any of our keywords"""
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Use word boundary matching for better accuracy
    import re
    for keyword in NEWS_KEYWORDS:
        keyword_lower = keyword.lower()
        # Create a regex pattern that matches the keyword as a whole word
        pattern = r'\b' + re.escape(keyword_lower) + r'\b'
        if re.search(pattern, text_lower):
            return True
    
    return False

# -------------------------------------------------------------------------
# PHASE 1 FIX: Enhanced RSS Feed Processing
# -------------------------------------------------------------------------
@retry_with_backoff(max_retries=2, base_delay=1)
def process_rss_feeds():
    """Process RSS feeds for 2025 news articles with enhanced error handling"""
    logger.info("=== RSS FEEDS: Starting ===")
    total_processed = 0
    
    # PHASE 1 FIX: Validate feeds before processing
    valid_feeds = []
    for feed_url in NEWS_SOURCES['rss_feeds']:
        if not FRESH_MODE and progress_tracker.is_feed_complete(feed_url):
            logger.info(f"Skipping completed feed: {feed_url}")
            continue
        elif FRESH_MODE and progress_tracker.is_feed_complete(feed_url):
            logger.info(f"Fresh mode: Reprocessing completed feed: {feed_url}")
        
        if validate_feed(feed_url):
            valid_feeds.append(feed_url)
        else:
            logger.warning(f"Skipping invalid feed: {feed_url}")
    
    logger.info(f"Processing {len(valid_feeds)} valid feeds out of {len(NEWS_SOURCES['rss_feeds'])} total")
    
    for feed_url in valid_feeds:
        logger.info(f"Processing RSS feed: {feed_url}")
        feed_count = 0
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(feed_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # PHASE 1 FIX: Handle HTTP errors
            if not handle_http_errors(response):
                logger.error(f"Skipping feed due to HTTP error: {feed_url}")
                continue
            
            # Try different parsing methods
            soup = None
            items = []
            
            # Method 1: XML parser
            try:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')
                if not items:
                    items = soup.find_all('entry')  # Atom feeds
            except Exception as e:
                logger.debug(f"XML parsing failed for {feed_url}: {e}")
                pass
            
            # Method 2: HTML parser fallback
            if not items:
                try:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    items = soup.find_all('item')
                    if not items:
                        items = soup.find_all('entry')  # Atom feeds
                except Exception as e:
                    logger.debug(f"HTML parsing failed for {feed_url}: {e}")
                    pass
            
            # Method 3: lxml parser fallback
            if not items:
                try:
                    soup = BeautifulSoup(response.content, 'lxml-xml')
                    items = soup.find_all('item')
                    if not items:
                        items = soup.find_all('entry')  # Atom feeds
                except Exception as e:
                    logger.debug(f"lxml parsing failed for {feed_url}: {e}")
                    pass
            
            logger.debug(f"Found {len(items)} items in feed: {feed_url}")
            
            for item in items:
                try:
                    title = item.find('title').get_text() if item.find('title') else 'No Title'
                    
                    # Handle different link formats (RSS vs Atom)
                    link = None
                    if item.find('link'):
                        link_elem = item.find('link')
                        if link_elem.get('href'):  # Atom format
                            link = link_elem.get('href')
                        else:  # RSS format
                            link = link_elem.get_text()
                    
                    # Handle different date formats
                    pub_date = ''
                    if item.find('pubDate'):
                        pub_date = item.find('pubDate').get_text()
                    elif item.find('published'):  # Atom format
                        pub_date = item.find('published').get_text()
                    elif item.find('updated'):  # Atom format
                        pub_date = item.find('updated').get_text()
                    
                    # Handle different description formats
                    description = ''
                    if item.find('description'):
                        description = item.find('description').get_text()
                    elif item.find('summary'):  # Atom format
                        description = item.find('summary').get_text()
                    elif item.find('content'):  # Atom format
                        description = item.find('content').get_text()
                    
                    if not link:
                        logger.debug("Skipping item - no link found")
                        continue
                    
                    # Check for URL-based deduplication first (fastest check)
                    if url_already_processed(link):
                        logger.debug(f"URL already processed: {link}")
                        continue
                    
                    # Check if 2025 article - for debugging let's see what we're filtering
                    if not is_recent_article(pub_date):
                        logger.debug(f"Filtering out non-2025 article: {title[:50]}... (date: {pub_date})")
                        continue
                    
                    # Check if matches keywords
                    combined_text = title + ' ' + description
                    if not matches_keywords(combined_text):
                        logger.debug(f"Filtering out article (no keywords): {title[:50]}... (text: {combined_text[:100]}...)")
                        continue
                    
                    # Generate unique ID
                    article_id = hashlib.md5(link.encode()).hexdigest()
                    
                    # Check if already processed by file existence (backup check)
                    metadata_key = f"{S3_FOLDER_NEWS}/rss/metadata/{article_id}.json"
                    content_key = f"{S3_FOLDER_NEWS}/rss/content/{article_id}.html"
                    
                    if exists_in_s3(metadata_key) and exists_in_s3(content_key):
                        logger.debug(f"Already processed by file check: {article_id}")
                        add_processed_url(link)  # Update our URL cache
                        continue
                    
                    # Extract full article content
                    full_content = extract_full_article_content(link)
                    if not full_content:
                        logger.warning(f"Could not extract content from: {link}")
                        continue
                    
                    # Create metadata
                    # Tag the article with geographic and topical information using comprehensive content
                    comprehensive_content = f"{title} {description} {full_content}"
                    article_tags = tag_article(comprehensive_content, NEWS_KEYWORDS)
                    
                    metadata = {
                        'title': title,
                        'url': link,
                        'pub_date': pub_date,
                        'description': description,
                        'source': 'RSS Feed',
                        'feed_url': feed_url,
                        'content_length': len(full_content),
                        'collection_date': datetime.now().isoformat(),
                        'continents': article_tags['continents'],
                        'matched_keywords': article_tags['matched_keywords'],
                        'core_topics': article_tags['core_topics']
                    }
                    
                    # Save metadata
                    if upload_to_s3_if_not_exists(
                        json.dumps(metadata, indent=2).encode("utf-8"),
                        metadata_key,
                        "application/json"
                    ):
                        # Save full content
                        if upload_to_s3_if_not_exists(full_content.encode('utf-8'), content_key):
                            feed_count += 1
                            progress_tracker.increment_articles()
                            add_processed_url(link)  # Track URL for future idempotency
                            logger.info(f"✓ Saved article: {title[:50]}...")
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logger.debug(f"Error processing RSS item: {str(e)}")
                    continue
            
            progress_tracker.mark_feed_complete(feed_url)
            total_processed += feed_count
            logger.info(f"Completed feed: {feed_url} ({feed_count} articles)")
            
        except Exception as e:
            logger.error(f"Error processing RSS feed {feed_url}: {str(e)}")
        
        time.sleep(2)  # Rate limiting between feeds
    
    logger.info(f"=== RSS FEEDS: Complete ({total_processed} total articles) ===")

# -------------------------------------------------------------------------
# PHASE 1 FIX: Enhanced Direct Website Scraping
# -------------------------------------------------------------------------
def scrape_website_articles(base_url: str, max_articles: int = 50):
    """Scrape articles directly from news websites with enhanced error handling"""
    if not FRESH_MODE and progress_tracker.is_source_complete(base_url):
        logger.info(f"Skipping completed source: {base_url}")
        return 0
    elif FRESH_MODE and progress_tracker.is_source_complete(base_url):
        logger.info(f"Fresh mode: Reprocessing completed source: {base_url}")
        
    logger.info(f"Scraping website: {base_url}")
    articles_found = 0
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(base_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # PHASE 1 FIX: Handle HTTP errors
        if not handle_http_errors(response):
            logger.error(f"Skipping source due to HTTP error: {base_url}")
            return 0
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find article links
        article_selectors = [
            'a[href*="/article/"]',
            'a[href*="/news/"]', 
            'a[href*="/story/"]',
            'a[href*="/post/"]',
            'a[href*="/blog/"]',
            '.article-link a',
            '.story-link a',
            '.headline a',
            'h1 a', 'h2 a', 'h3 a'
        ]
        
        article_links = set()
        for selector in article_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    if href.startswith('/'):
                        href = urljoin(base_url, href)
                    if href.startswith('http') and len(href) > 10:
                        article_links.add(href)
        
        logger.info(f"Found {len(article_links)} potential articles on {base_url}")
        
        for article_url in list(article_links)[:max_articles]:
            try:
                # Check for URL-based deduplication first (fastest check)
                if url_already_processed(article_url):
                    logger.debug(f"URL already processed: {article_url}")
                    continue
                
                # Generate unique ID
                article_id = hashlib.md5(article_url.encode()).hexdigest()
                
                # Check if already processed by file existence (backup check)
                metadata_key = f"{S3_FOLDER_NEWS}/direct/metadata/{article_id}.json"
                content_key = f"{S3_FOLDER_NEWS}/direct/content/{article_id}.html"
                
                if exists_in_s3(metadata_key) and exists_in_s3(content_key):
                    logger.debug(f"Already processed by file check: {article_id}")
                    add_processed_url(article_url)  # Update our URL cache
                    continue
                
                # Get article page
                article_response = requests.get(article_url, headers=headers, timeout=30)
                article_response.raise_for_status()
                
                # PHASE 1 FIX: Handle HTTP errors for individual articles
                if not handle_http_errors(article_response):
                    logger.warning(f"Skipping article due to HTTP error: {article_url}")
                    continue
                
                article_soup = BeautifulSoup(article_response.content, 'html.parser')
                
                # Extract title
                title_element = article_soup.find('title') or article_soup.find('h1')
                title = title_element.get_text().strip() if title_element else 'No Title'
                
                # Check if matches keywords
                if not matches_keywords(title):
                    continue
                
                # Extract date (try multiple selectors)
                date_selectors = [
                    '[datetime]',
                    '.publish-date',
                    '.article-date', 
                    '.post-date',
                    'time'
                ]
                
                article_date = None
                for selector in date_selectors:
                    date_element = article_soup.select_one(selector)
                    if date_element:
                        article_date = date_element.get('datetime') or date_element.get_text()
                        break
                
                # Check if 2025 article
                if article_date and not is_recent_article(article_date):
                    continue
                
                # Extract full content
                full_content = extract_full_article_content(article_url)
                if not full_content:
                    continue
                
                # Check content for keywords too
                if not matches_keywords(full_content):
                    continue
                
                # Create metadata
                # Tag the article with geographic and topical information using comprehensive content
                comprehensive_content = f"{title} {full_content}"
                article_tags = tag_article(comprehensive_content, NEWS_KEYWORDS)
                
                metadata = {
                    'title': title,
                    'url': article_url,
                    'date': article_date or 'Unknown',
                    'source': 'Direct Scraping',
                    'base_url': base_url,
                    'content_length': len(full_content),
                    'collection_date': datetime.now().isoformat(),
                    'continents': article_tags['continents'],
                    'matched_keywords': article_tags['matched_keywords'],
                    'core_topics': article_tags['core_topics']
                }
                
                # Save metadata
                if upload_to_s3_if_not_exists(
                    json.dumps(metadata, indent=2).encode("utf-8"),
                    metadata_key,
                    "application/json"
                ):
                    # Save full content
                    if upload_to_s3_if_not_exists(full_content.encode('utf-8'), content_key):
                        articles_found += 1
                        progress_tracker.increment_articles()
                        add_processed_url(article_url)  # Track URL for future idempotency
                        logger.info(f"✓ Scraped article: {title[:50]}...")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.debug(f"Error scraping article {article_url}: {str(e)}")
                continue
        
        progress_tracker.mark_source_complete(base_url)
        
    except Exception as e:
        logger.error(f"Error scraping website {base_url}: {str(e)}")
        
    return articles_found

def process_direct_scraping():
    """Process direct website scraping"""
    logger.info("=== DIRECT SCRAPING: Starting ===")
    total_processed = 0
    
    for source_url in NEWS_SOURCES['direct_scraping']:
        articles_count = scrape_website_articles(source_url)
        total_processed += articles_count
        logger.info(f"Completed source: {source_url} ({articles_count} articles)")
        time.sleep(3)  # Rate limiting between sites
    
    logger.info(f"=== DIRECT SCRAPING: Complete ({total_processed} total articles) ===")

# -------------------------------------------------------------------------
# HTML INDEX GENERATORS (Unchanged from original)
# -------------------------------------------------------------------------
def generate_date_html_index():
    """Generate HTML index file for the current date's collected articles"""
    logger.info("📄 Generating date HTML index...")
    
    try:
        # Get all metadata files from today's folder
        metadata_files = []
        
        # Get RSS metadata files
        try:
            paginator = s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(
                Bucket=S3_BUCKET_NAME,
                Prefix=f"{S3_FOLDER_NEWS}/rss/metadata/"
            )
            
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        if obj['Key'].endswith('.json'):
                            metadata_files.append(obj['Key'])
        except Exception as e:
            logger.debug(f"Error listing RSS metadata files: {e}")
        
        # Get direct scraping metadata files
        try:
            page_iterator = paginator.paginate(
                Bucket=S3_BUCKET_NAME,
                Prefix=f"{S3_FOLDER_NEWS}/direct/metadata/"
            )
            
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        if obj['Key'].endswith('.json'):
                            metadata_files.append(obj['Key'])
        except Exception as e:
            logger.debug(f"Error listing direct metadata files: {e}")
        
        if not metadata_files:
            logger.warning("No metadata files found to generate HTML index")
            return False
        
        # Load all metadata
        articles = []
        for metadata_file in metadata_files:
            try:
                response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=metadata_file)
                metadata = json.loads(response['Body'].read().decode('utf-8'))
                articles.append(metadata)
            except Exception as e:
                logger.debug(f"Error loading metadata file {metadata_file}: {e}")
                continue
        
        # Sort articles by publication date (newest first)
        def sort_key(article):
            try:
                # Try to parse the pub_date
                if 'pub_date' in article and article['pub_date']:
                    from dateutil import parser
                    parsed_date = parser.parse(article['pub_date'])
                    # Make timezone-naive for comparison
                    if parsed_date.tzinfo is not None:
                        parsed_date = parsed_date.replace(tzinfo=None)
                    return parsed_date
                elif 'date' in article and article['date']:
                    from dateutil import parser
                    parsed_date = parser.parse(article['date'])
                    # Make timezone-naive for comparison
                    if parsed_date.tzinfo is not None:
                        parsed_date = parsed_date.replace(tzinfo=None)
                    return parsed_date
                else:
                    return datetime.min
            except:
                return datetime.min
        
        articles.sort(key=sort_key, reverse=True)
        
        # Generate HTML content (same as original)
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Collection - {today} | Asoba</title>
    <link rel="icon" type="image/x-icon" href="https://docs.asoba.co/assets/images/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="https://docs.asoba.co/assets/images/logo.png">
    <link rel="apple-touch-icon" sizes="180x180" href="https://docs.asoba.co/assets/images/logo.png">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap">
    <style>
        /* Color theme from Asoba brand guide */
        :root {{
            --primary-black: #000000;
            --primary-blue: #455BF1;
            --accent-blue: #3748c8;
            --text-dark: #333;
            --text-light: #4D4D4D;
            --background-light: #f5f5f5;
            --white: #FFFFFF;
            --neutral-light: #F9F9F9;
            --neutral-grey: #F4F4F4;
            --border-grey: #E0E0E0;
            --success-green: #28ca42;
            --warning-orange: #f39c12;
        }}

        /* Reset and base styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'DM Sans', Helvetica, Arial, sans-serif;
            color: var(--text-dark);
            background-color: var(--white);
            line-height: 1.6;
        }}

        /* Header/Navigation Bar */
        .header-bar {{
            background-color: var(--primary-black);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 70px;
            z-index: 100;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 90px;
        }}

        .branding {{
            display: flex;
            align-items: center;
        }}

        .branding img {{
            width: 50px;
            height: 50px;
            object-fit: contain;
        }}

        .site-title {{
            color: var(--white);
            font-size: 20px;
            font-weight: 700;
            margin-left: 15px;
            white-space: nowrap;
        }}

        .top-links {{
            display: flex;
            gap: 15px;
            align-items: center;
        }}

        .top-links a {{
            color: var(--white);
            text-decoration: none;
            font: normal 12px / 16px 'DM Sans', Helvetica, Arial, sans-serif;
            padding: 5px;
            transition: color 0.3s ease;
        }}

        .top-links a:hover {{
            color: var(--primary-blue);
        }}

        /* Main content spacing */
        main {{
            margin-top: 70px;
        }}

        /* Container */
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 40px;
        }}

        /* Hero Section */
        .hero {{
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--accent-blue) 100%);
            color: var(--white);
            padding: 80px 0 100px;
            position: relative;
            overflow: hidden;
        }}

        .hero::before {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxjaXJjbGUgY3g9IjEwMCIgY3k9IjEwMCIgcj0iMSIgZmlsbD0id2hpdGUiIGZpbGwtb3BhY2l0eT0iMC4xIi8+Cjwvc3ZnPgo=') repeat;
            opacity: 0.3;
        }}

        .hero-content {{
            position: relative;
            z-index: 2;
            color: var(--white);
            max-width: 700px;
            text-align: center;
            margin: 0 auto;
        }}

        .hero h1 {{
            font-size: 3.8rem;
            font-weight: 800;
            margin-bottom: 25px;
            color: var(--white);
            line-height: 1.1;
        }}

        .hero p {{
            font-size: 1.25rem;
            margin-bottom: 40px;
            opacity: 0.95;
            color: var(--white);
        }}

        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 40px;
        }}

        .stat {{
            text-align: center;
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: 700;
            display: block;
            color: var(--white);
        }}

        .stat-label {{
            font-size: 1rem;
            opacity: 0.9;
            color: var(--white);
        }}

        /* Content Section */
        .content-section {{
            padding: 80px 0;
            background: var(--white);
        }}

        .content {{
            padding: 0;
        }}

        .back-link {{
            margin-bottom: 30px;
        }}

        .back-link a {{
            color: var(--primary-blue);
            text-decoration: none;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }}

        .back-link a:hover {{
            transform: translateX(-4px);
        }}

        .filters {{
            margin-bottom: 40px;
            padding: 30px;
            background: var(--neutral-light);
            border-radius: 12px;
            border: 1px solid var(--border-grey);
        }}

        .filter-group {{
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }}

        .filter-group label {{
            font-weight: 600;
            color: var(--text-dark);
            font-size: 1rem;
        }}

        .filter-group select, .filter-group input {{
            padding: 12px 16px;
            border: 1px solid var(--border-grey);
            border-radius: 8px;
            font-family: 'DM Sans', sans-serif;
            font-size: 1rem;
            transition: border-color 0.3s ease;
            background: var(--white);
        }}

        .filter-group select:focus, .filter-group input:focus {{
            outline: none;
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 3px rgba(69, 91, 241, 0.1);
        }}

        /* Article Cards */
        .articles-grid {{
            display: grid;
            gap: 30px;
        }}

        .article {{
            background: var(--white);
            border: 1px solid var(--border-grey);
            border-radius: 12px;
            padding: 30px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }}

        .article:hover {{
            transform: translateY(-5px);
            border-color: var(--primary-blue);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}

        .article-title {{
            margin: 0 0 15px 0;
            font-size: 1.5rem;
            font-weight: 700;
            line-height: 1.3;
        }}

        .article-title a {{
            color: var(--text-dark);
            text-decoration: none;
            transition: color 0.3s ease;
        }}

        .article-title a:hover {{
            color: var(--primary-blue);
        }}

        .article-meta {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            font-size: 0.9rem;
            flex-wrap: wrap;
        }}

        .article-source {{
            background: var(--primary-blue);
            color: var(--white);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .article-continent {{
            background: var(--success-green);
            color: var(--white);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .article-keyword {{
            background: var(--warning-orange);
            color: var(--white);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .article-core-topic {{
            background: var(--accent-blue);
            color: var(--white);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .article-date {{
            color: var(--text-light);
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .article-length {{
            color: var(--text-light);
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .article-description {{
            color: var(--text-light);
            margin-bottom: 25px;
            line-height: 1.6;
            font-size: 1rem;
        }}

        .article-description p {{
            margin: 0 0 15px 0;
        }}

        .article-description p:last-child {{
            margin-bottom: 0;
        }}

        .view-content {{
            margin-top: 20px;
        }}

        .view-content a {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: var(--primary-blue);
            color: var(--white);
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }}

        .view-content a:hover {{
            background: var(--accent-blue);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(69, 91, 241, 0.3);
        }}

        /* Footer */
        .copyright-footer {{
            background-color: var(--primary-black);
            color: var(--white);
            padding: 30px 0;
            text-align: center;
        }}

        .copyright-footer p {{
            font-size: 0.9rem;
            margin: 0;
            opacity: 0.8;
        }}

        /* Responsive Design */
        @media (max-width: 768px) {{
            .header-bar {{
                padding: 0 20px;
            }}

            .container {{
                padding: 0 20px;
            }}

            .hero h1 {{
                font-size: 2.8rem;
            }}

            .stats {{
                flex-direction: column;
                gap: 20px;
            }}

            .filter-group {{
                flex-direction: column;
                align-items: flex-start;
                gap: 15px;
            }}

            .article-meta {{
                flex-direction: column;
                gap: 10px;
            }}

            .article {{
                padding: 20px;
            }}
        }}

        @media (max-width: 480px) {{
            .hero h1 {{
                font-size: 2.2rem;
            }}

            .article-title {{
                font-size: 1.3rem;
            }}
        }}
    </style>
</head>
<body>
    <header class="header-bar">
        <div class="branding">
            <a href="https://asoba.co">
                <img src="https://docs.asoba.co/assets/images/logo.png" alt="Asoba">
            </a>
            <span class="site-title">Asoba</span>
        </div>
        <div class="top-links">
            <a href="https://asoba.co">Home</a>
            <a href="https://asoba.co/about.html">About</a>
            <a href="https://asoba.co/products.html">Products</a>
            <a href="https://asoba.co/blog.html">Insights</a>
            <a href="https://docs.asoba.co">Documentation</a>
        </div>
    </header>

    <main>
        <section class="hero">
            <div class="container">
                <div class="hero-content">
                    <h1>📰 News Collection</h1>
                    <p>Energy, AI, and Blockchain News - {today}</p>
                    <div class="stats">
                        <div class="stat">
                            <span class="stat-number">{len(articles)}</span>
                            <span class="stat-label">Articles</span>
                        </div>
                        <div class="stat">
                            <span class="stat-number">{len(set(article.get('source', 'Unknown') for article in articles))}</span>
                            <span class="stat-label">Sources</span>
                        </div>
                        <div class="stat">
                            <span class="stat-number">{sum(article.get('content_length', 0) for article in articles) // 1000}K</span>
                            <span class="stat-label">Words</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section class="content-section">
            <div class="container">
                <div class="content">
                    <div class="back-link">
                        <a href="http://news-collection-website.s3-website-us-east-1.amazonaws.com/">← Back to All Dates</a>
                    </div>
                    
                    <div class="filters">
                        <div class="filter-group">
                            <label for="sourceFilter">Filter by source:</label>
                            <select id="sourceFilter">
                                <option value="">All sources</option>
                                {''.join(f'<option value="{source}">{source}</option>' for source in sorted(set(article.get('source', 'Unknown') for article in articles)))}
                            </select>
                            <label for="continentFilter">Filter by continent:</label>
                            <select id="continentFilter" multiple>
                                {''.join(f'<option value="{continent}">{continent}</option>' for continent in sorted(set(continent for article in articles for continent in article.get('continents', []))))}
                            </select>
                            <label for="keywordFilter">Filter by keyword:</label>
                            <select id="keywordFilter" multiple>
                                {''.join(f'<option value="{keyword}">{keyword}</option>' for keyword in sorted(set(keyword for article in articles for keyword in article.get('matched_keywords', []))))}
                            </select>
                            <label for="topicFilter">Filter by topic:</label>
                            <select id="topicFilter" multiple>
                                {''.join(f'<option value="{topic}">{topic}</option>' for topic in sorted(set(topic for article in articles for topic in article.get('core_topics', []))))}
                            </select>
                            <label for="searchInput">Search:</label>
                            <input type="text" id="searchInput" placeholder="Search articles...">
                        </div>
                    </div>
                    
                    <div id="articlesList" class="articles-grid">"""
        
        # Add articles
        for i, article in enumerate(articles):
            # Extract article ID from metadata file path or generate from URL
            article_id = hashlib.md5(article['url'].encode()).hexdigest()
            
            # Determine content file path
            if 'feed_url' in article:
                content_path = f"rss/content/{article_id}.html"
            else:
                content_path = f"direct/content/{article_id}.html"
            
            # Format publication date
            pub_date = article.get('pub_date', article.get('date', 'Unknown'))
            if pub_date != 'Unknown':
                try:
                    from dateutil import parser
                    parsed_date = parser.parse(pub_date)
                    formatted_date = parsed_date.strftime('%B %d, %Y at %I:%M %p')
                except:
                    formatted_date = pub_date
            else:
                formatted_date = 'Unknown'
            
            # Clean description HTML
            description = article.get('description', '')
            if description:
                # Remove HTML tags for display
                soup = BeautifulSoup(description, 'html.parser')
                description = soup.get_text()[:300] + ('...' if len(soup.get_text()) > 300 else '')
            
            html_content += f"""
                <div class="article" data-source="{article.get('source', 'Unknown')}" data-title="{article.get('title', '').lower()}" data-description="{description.lower()}">
                    <h3 class="article-title">
                        <a href="{article['url']}" target="_blank">{article.get('title', 'No Title')}</a>
                    </h3>
                    <div class="article-meta">
                        <span class="article-source">{article.get('source', 'Unknown')}</span>
                        {''.join(f'<span class="article-continent">{continent}</span>' for continent in article.get('continents', []))}
                        {''.join(f'<span class="article-keyword">{keyword}</span>' for keyword in article.get('matched_keywords', [])[:3])}
                        {''.join(f'<span class="article-core-topic">{topic}</span>' for topic in article.get('core_topics', []))}
                        <span class="article-date">📅 {formatted_date}</span>
                        <span class="article-length">📄 {article.get('content_length', 0):,} chars</span>
                    </div>
                    {f'<div class="article-description">{description}</div>' if description else ''}
                    <div class="view-content">
                        <a href="{content_path}" target="_blank">📖 View Full Content</a>
                    </div>
                </div>"""
        
        html_content += """
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer class="copyright-footer">
        <div class="container">
            <p>&copy; 2025 Asoba Corporation. All rights reserved.</p>
        </div>
    </footer>
    
    <script>
        // Filter functionality
        const sourceFilter = document.getElementById('sourceFilter');
        const continentFilter = document.getElementById('continentFilter');
        const keywordFilter = document.getElementById('keywordFilter');
        const topicFilter = document.getElementById('topicFilter');
        const searchInput = document.getElementById('searchInput');
        const articlesList = document.getElementById('articlesList');
        const articles = document.querySelectorAll('.article');
        
        function filterArticles() {
            const selectedSource = sourceFilter.value.toLowerCase();
            const selectedContinents = Array.from(continentFilter.selectedOptions).map(option => option.value);
            const selectedKeywords = Array.from(keywordFilter.selectedOptions).map(option => option.value);
            const selectedTopics = Array.from(topicFilter.selectedOptions).map(option => option.value);
            const searchTerm = searchInput.value.toLowerCase();
            
            articles.forEach(article => {
                const source = article.dataset.source.toLowerCase();
                const title = article.dataset.title;
                const description = article.dataset.description;
                
                // Get article tags from the DOM
                const continentTags = Array.from(article.querySelectorAll('.article-continent')).map(span => span.textContent.trim());
                const keywordTags = Array.from(article.querySelectorAll('.article-keyword')).map(span => span.textContent.trim());
                const topicTags = Array.from(article.querySelectorAll('.article-core-topic')).map(span => span.textContent.trim());
                
                const sourceMatch = !selectedSource || source.includes(selectedSource);
                const searchMatch = !searchTerm || title.includes(searchTerm) || description.includes(searchTerm);
                const continentMatch = selectedContinents.length === 0 || selectedContinents.some(continent => continentTags.includes(continent));
                const keywordMatch = selectedKeywords.length === 0 || selectedKeywords.some(keyword => keywordTags.includes(keyword));
                const topicMatch = selectedTopics.length === 0 || selectedTopics.some(topic => topicTags.includes(topic));
                
                if (sourceMatch && searchMatch && continentMatch && keywordMatch && topicMatch) {
                    article.style.display = 'block';
                } else {
                    article.style.display = 'none';
                }
            });
        }
        
        sourceFilter.addEventListener('change', filterArticles);
        continentFilter.addEventListener('change', filterArticles);
        keywordFilter.addEventListener('change', filterArticles);
        topicFilter.addEventListener('change', filterArticles);
        searchInput.addEventListener('input', filterArticles);
        
        // Initialize
        filterArticles();
    </script>
</body>
</html>"""
        
        # Upload HTML file to S3 (force update for HTML files)
        html_key = f"{S3_FOLDER_NEWS}/index.html"
        try:
            logger.info(f"Uploading to S3: {html_key}")
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=html_key,
                Body=html_content.encode('utf-8'),
                ContentType="text/html"
            )
            # Add to manifest
            S3_MANIFEST.add(html_key)
            logger.info(f"✓ Uploaded: {html_key}")
            success = True
        except Exception as e:
            logger.error(f"Failed to upload {html_key}: {e}")
            success = False
        
        if success:
            logger.info(f"✓ Generated date HTML index: s3://{S3_BUCKET_NAME}/{html_key}")
            return True
        else:
            logger.error("Failed to upload date HTML index to S3")
            return False
            
    except Exception as e:
        logger.error(f"Error generating date HTML index: {str(e)}")
        return False

def generate_master_html_index():
    """Generate master HTML index file for browsing all collected dates"""
    logger.info("📄 Generating master HTML index...")
    
    try:
        # Get all date folders
        date_folders = []
        
        try:
            paginator = s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(
                Bucket=S3_BUCKET_NAME,
                Prefix="news/"
            )
            
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        if obj['Key'].endswith('/index.html') and 'news/' in obj['Key']:
                            # Extract date from path like "news/2025-10-09/index.html"
                            path_parts = obj['Key'].split('/')
                            if len(path_parts) >= 3:
                                date_folder = path_parts[1]  # e.g., "2025-10-09"
                                if date_folder not in date_folders:
                                    date_folders.append(date_folder)
        except Exception as e:
            logger.debug(f"Error listing date folders: {e}")
        
        # Sort dates (newest first)
        date_folders.sort(reverse=True)
        
        if not date_folders:
            logger.warning("No date folders found to generate master index")
            return False
        
        # Get statistics for each date
        date_stats = []
        for date_folder in date_folders:
            try:
                # Count articles in this date folder
                article_count = 0
                total_length = 0
                sources = set()
                
                # Count RSS articles
                try:
                    page_iterator = paginator.paginate(
                        Bucket=S3_BUCKET_NAME,
                        Prefix=f"news/{date_folder}/rss/metadata/"
                    )
                    
                    for page in page_iterator:
                        if 'Contents' in page:
                            for obj in page['Contents']:
                                if obj['Key'].endswith('.json'):
                                    article_count += 1
                                    # Load metadata to get stats
                                    try:
                                        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=obj['Key'])
                                        metadata = json.loads(response['Body'].read().decode('utf-8'))
                                        total_length += metadata.get('content_length', 0)
                                        sources.add(metadata.get('source', 'Unknown'))
                                    except:
                                        pass
                except:
                    pass
                
                # Count direct scraping articles
                try:
                    page_iterator = paginator.paginate(
                        Bucket=S3_BUCKET_NAME,
                        Prefix=f"news/{date_folder}/direct/metadata/"
                    )
                    
                    for page in page_iterator:
                        if 'Contents' in page:
                            for obj in page['Contents']:
                                if obj['Key'].endswith('.json'):
                                    article_count += 1
                                    # Load metadata to get stats
                                    try:
                                        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=obj['Key'])
                                        metadata = json.loads(response['Body'].read().decode('utf-8'))
                                        total_length += metadata.get('content_length', 0)
                                        sources.add(metadata.get('source', 'Unknown'))
                                    except:
                                        pass
                except:
                    pass
                
                date_stats.append({
                    'date': date_folder,
                    'article_count': article_count,
                    'total_length': total_length,
                    'source_count': len(sources)
                })
                
            except Exception as e:
                logger.debug(f"Error getting stats for {date_folder}: {e}")
                date_stats.append({
                    'date': date_folder,
                    'article_count': 0,
                    'total_length': 0,
                    'source_count': 0
                })
        
        # Generate HTML content with Asoba styling
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Collection Archive | Asoba</title>
    <link rel="icon" type="image/x-icon" href="https://docs.asoba.co/assets/images/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="https://docs.asoba.co/assets/images/logo.png">
    <link rel="apple-touch-icon" sizes="180x180" href="https://docs.asoba.co/assets/images/logo.png">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap">
    <style>
        /* Color theme from Asoba brand guide */
        :root {{
            --primary-black: #000000;
            --primary-blue: #455BF1;
            --accent-blue: #3748c8;
            --text-dark: #333;
            --text-light: #4D4D4D;
            --background-light: #f5f5f5;
            --white: #FFFFFF;
            --neutral-light: #F9F9F9;
            --neutral-grey: #F4F4F4;
            --border-grey: #E0E0E0;
            --success-green: #28ca42;
            --warning-orange: #f39c12;
        }}

        /* Reset and base styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'DM Sans', Helvetica, Arial, sans-serif;
            color: var(--text-dark);
            background-color: var(--white);
            line-height: 1.6;
        }}

        /* Header/Navigation Bar */
        .header-bar {{
            background-color: var(--primary-black);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 70px;
            z-index: 100;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 90px;
        }}

        .branding {{
            display: flex;
            align-items: center;
        }}

        .branding img {{
            width: 50px;
            height: 50px;
            object-fit: contain;
        }}

        .site-title {{
            color: var(--white);
            font-size: 20px;
            font-weight: 700;
            margin-left: 15px;
            white-space: nowrap;
        }}

        .top-links {{
            display: flex;
            gap: 15px;
            align-items: center;
        }}

        .top-links a {{
            color: var(--white);
            text-decoration: none;
            font: normal 12px / 16px 'DM Sans', Helvetica, Arial, sans-serif;
            padding: 5px;
            transition: color 0.3s ease;
        }}

        .top-links a:hover {{
            color: var(--primary-blue);
        }}

        /* Main content spacing */
        main {{
            margin-top: 70px;
        }}

        /* Container */
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 40px;
        }}

        /* Hero Section */
        .hero {{
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--accent-blue) 100%);
            color: var(--white);
            padding: 80px 0 100px;
            position: relative;
            overflow: hidden;
        }}

        .hero::before {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxjaXJjbGUgY3g9IjEwMCIgY3k9IjEwMCIgcj0iMSIgZmlsbD0id2hpdGUiIGZpbGwtb3BhY2l0eT0iMC4xIi8+Cjwvc3ZnPgo=') repeat;
            opacity: 0.3;
        }}

        .hero-content {{
            position: relative;
            z-index: 2;
            color: var(--white);
            max-width: 700px;
            text-align: center;
            margin: 0 auto;
        }}

        .hero h1 {{
            font-size: 3.8rem;
            font-weight: 800;
            margin-bottom: 25px;
            color: var(--white);
            line-height: 1.1;
        }}

        .hero p {{
            font-size: 1.25rem;
            margin-bottom: 40px;
            opacity: 0.95;
            color: var(--white);
        }}

        .overview {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 40px;
        }}

        .overview-stat {{
            text-align: center;
        }}

        .overview-number {{
            font-size: 2.5em;
            font-weight: 700;
            display: block;
            color: var(--white);
        }}

        .overview-label {{
            font-size: 1rem;
            opacity: 0.9;
            color: var(--white);
        }}

        /* Content Section */
        .content-section {{
            padding: 80px 0;
            background: var(--white);
        }}

        .content {{
            padding: 0;
        }}

        .date-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }}

        .date-card {{
            background: var(--white);
            border: 1px solid var(--border-grey);
            border-radius: 12px;
            padding: 30px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }}

        .date-card:hover {{
            transform: translateY(-5px);
            border-color: var(--primary-blue);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}

        .date-card h3 {{
            margin: 0 0 20px 0;
            color: var(--text-dark);
            font-size: 1.5rem;
            font-weight: 700;
        }}

        .date-card a {{
            color: var(--primary-blue);
            text-decoration: none;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }}

        .date-card a:hover {{
            transform: translateX(4px);
        }}

        .date-stats {{
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            font-size: 0.9rem;
            flex-wrap: wrap;
        }}

        .date-stat {{
            background: var(--neutral-light);
            color: var(--text-light);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }}

        .date-description {{
            color: var(--text-light);
            font-size: 0.9rem;
            margin-bottom: 20px;
            line-height: 1.5;
        }}

        .view-button {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: var(--primary-blue);
            color: var(--white);
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }}

        .view-button:hover {{
            background: var(--accent-blue);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(69, 91, 241, 0.3);
        }}

        .search-section {{
            margin-bottom: 40px;
            padding: 30px;
            background: var(--neutral-light);
            border-radius: 12px;
            border: 1px solid var(--border-grey);
        }}

        .search-group {{
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }}

        .search-group input {{
            padding: 12px 16px;
            border: 1px solid var(--border-grey);
            border-radius: 8px;
            font-family: 'DM Sans', sans-serif;
            font-size: 1rem;
            flex: 1;
            min-width: 200px;
            transition: border-color 0.3s ease;
        }}

        .search-group input:focus {{
            outline: none;
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 3px rgba(69, 91, 241, 0.1);
        }}

        .search-group select {{
            padding: 12px 16px;
            border: 1px solid var(--border-grey);
            border-radius: 8px;
            font-family: 'DM Sans', sans-serif;
            font-size: 1rem;
            background: var(--white);
            transition: border-color 0.3s ease;
            min-width: 150px;
        }}

        .search-group select:focus {{
            outline: none;
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 3px rgba(69, 91, 241, 0.1);
        }}

        .search-group select[multiple] {{
            min-height: 100px;
            min-width: 200px;
        }}

        .search-group select[multiple] option {{
            padding: 8px 12px;
            margin: 2px 0;
            border-radius: 4px;
        }}

        .search-group select[multiple] option:checked {{
            background: var(--primary-blue);
            color: var(--white);
        }}

        .no-dates {{
            text-align: center;
            padding: 80px 20px;
            color: var(--text-light);
        }}

        .no-dates h3 {{
            margin: 0 0 15px 0;
            font-size: 1.5rem;
            color: var(--text-dark);
        }}

        /* Footer */
        .copyright-footer {{
            background-color: var(--primary-black);
            color: var(--white);
            padding: 30px 0;
            text-align: center;
        }}

        .copyright-footer p {{
            font-size: 0.9rem;
            margin: 0;
            opacity: 0.8;
        }}

        /* Responsive Design */
        @media (max-width: 768px) {{
            .header-bar {{
                padding: 0 20px;
            }}

            .container {{
                padding: 0 20px;
            }}

            .hero h1 {{
                font-size: 2.8rem;
            }}

            .overview {{
                flex-direction: column;
                gap: 20px;
            }}

            .date-grid {{
                grid-template-columns: 1fr;
            }}

            .search-group {{
                flex-direction: column;
                align-items: stretch;
            }}

            .date-stats {{
                flex-direction: column;
                gap: 10px;
            }}
        }}

        @media (max-width: 480px) {{
            .hero h1 {{
                font-size: 2.2rem;
            }}
        }}
    </style>
</head>
<body>
    <header class="header-bar">
        <div class="branding">
            <a href="https://asoba.co">
                <img src="https://docs.asoba.co/assets/images/logo.png" alt="Asoba">
            </a>
            <span class="site-title">Asoba</span>
        </div>
        <div class="top-links">
            <a href="https://asoba.co">Home</a>
            <a href="https://asoba.co/about.html">About</a>
            <a href="https://asoba.co/products.html">Products</a>
            <a href="https://asoba.co/blog.html">Insights</a>
            <a href="https://docs.asoba.co">Documentation</a>
        </div>
    </header>

    <main>
        <section class="hero">
            <div class="container">
                <div class="hero-content">
                    <h1>📰 News Collection Archive</h1>
                    <p>Energy, AI, and Blockchain News Collection</p>
                    <div class="overview">
                        <div class="overview-stat">
                            <span class="overview-number">{len(date_folders)}</span>
                            <span class="overview-label">Collection Dates</span>
                        </div>
                        <div class="overview-stat">
                            <span class="overview-number">{sum(stat['article_count'] for stat in date_stats)}</span>
                            <span class="overview-label">Total Articles</span>
                        </div>
                        <div class="overview-stat">
                            <span class="overview-number">{sum(stat['total_length'] for stat in date_stats) // 1000}K</span>
                            <span class="overview-label">Total Words</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section class="content-section">
            <div class="container">
                <div class="content">
                    <div class="search-section">
                        <div class="search-group">
                            <input type="text" id="searchInput" placeholder="Search collection dates...">
                        </div>
                    </div>
                    
                    <div id="datesList" class="date-grid">"""
        
        # Add date cards
        for stat in date_stats:
            date_str = stat['date']
            article_count = stat['article_count']
            total_length = stat['total_length']
            source_count = stat['source_count']
            
            # Format date for display
            try:
                from dateutil import parser
                parsed_date = parser.parse(date_str)
                formatted_date = parsed_date.strftime('%B %d, %Y')
            except:
                formatted_date = date_str
            
            html_content += f"""
                <div class="date-card" data-date="{date_str}" data-articles="{article_count}">
                    <h3><a href="news/{date_str}/index.html">{formatted_date}</a></h3>
                    <div class="date-stats">
                        <span class="date-stat">{article_count} articles</span>
                        <span class="date-stat">{source_count} sources</span>
                        <span class="date-stat">{total_length // 1000}K words</span>
                    </div>
                    <div class="date-description">
                        Collection of energy, AI, and blockchain news from {formatted_date}
                    </div>
                    <a href="news/{date_str}/index.html" class="view-button">View Collection →</a>
                </div>"""
        
        html_content += """
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer class="copyright-footer">
        <div class="container">
            <p>&copy; 2025 Asoba Corporation. All rights reserved.</p>
        </div>
    </footer>
    
    <script>
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        const datesList = document.getElementById('datesList');
        const dateCards = document.querySelectorAll('.date-card');
        
        function filterDates() {
            const searchTerm = searchInput.value.toLowerCase();
            
            dateCards.forEach(card => {
                const date = card.dataset.date;
                const articles = card.dataset.articles;
                
                const dateMatch = date.includes(searchTerm);
                const articleMatch = articles.includes(searchTerm);
                
                if (dateMatch || articleMatch) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }
        
        searchInput.addEventListener('input', filterDates);
        
        // Initialize
        filterDates();
    </script>
</body>
</html>"""
        
        # Upload master HTML file to S3 root (force update for HTML files)
        try:
            logger.info(f"Uploading to S3: index.html")
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key="index.html",
                Body=html_content.encode('utf-8'),
                ContentType="text/html"
            )
            # Add to manifest
            S3_MANIFEST.add("index.html")
            logger.info(f"✓ Uploaded: index.html")
            success = True
        except Exception as e:
            logger.error(f"Failed to upload index.html: {e}")
            success = False
        
        if success:
            logger.info(f"✓ Generated master HTML index: s3://{S3_BUCKET_NAME}/index.html")
            return True
        else:
            logger.error("Failed to upload master HTML index to S3")
            return False
            
    except Exception as e:
        logger.error(f"Error generating master HTML index: {str(e)}")
        return False

# -------------------------------------------------------------------------
# PHASE 1 FIX: Enhanced Main Execution with Statistics
# -------------------------------------------------------------------------
def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='News scraper with optional fresh collection mode',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 news_scraper_improved.py          # Normal idempotent mode
  python3 news_scraper_improved.py -fresh   # Fresh collection mode
        """
    )
    
    parser.add_argument(
        '-fresh', '--fresh',
        action='store_true',
        help='Force fresh collection, bypassing idempotency (default: False)'
    )
    
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()
    global FRESH_MODE
    FRESH_MODE = args.fresh
    
    if FRESH_MODE:
        logger.info("🔄 FRESH MODE: Bypassing idempotency - will collect all articles")
        # Clear progress file in fresh mode
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
            logger.info("🗑️ Cleared progress file for fresh collection")
    else:
        logger.info("♻️ IDEMPOTENT MODE: Skipping completed feeds/sources")
    
    logger.info("🚀 Starting 2025 News Collection with Static Website - IMPROVED VERSION")
    logger.info(f"Target S3 location: s3://{S3_BUCKET_NAME}/{S3_FOLDER_NEWS}/")
    logger.info(f"Website URL: http://{S3_BUCKET_NAME}.s3-website-us-east-1.amazonaws.com")
    logger.info(f"Current progress: {progress_tracker.progress['total_articles']} articles")
    
    # PHASE 1 FIX: Log extraction statistics
    stats = progress_tracker.progress.get('extraction_stats', {})
    logger.info(f"Extraction stats: {stats.get('successful_extractions', 0)} successful, {stats.get('failed_extractions', 0)} failed")
    
    start_time = time.time()
    
    try:
        # Phase 1: RSS Feeds
        logger.info("\n📰 Phase 1: RSS feeds...")
        process_rss_feeds()
        
        # Phase 2: Direct scraping
        logger.info("\n🌐 Phase 2: Direct website scraping...")
        process_direct_scraping()
        
        # Phase 3: Generate date HTML index
        logger.info("\n📄 Phase 3: Generating date HTML index...")
        generate_date_html_index()
        
        # Phase 4: Generate master HTML index
        logger.info("\n📄 Phase 4: Generating master HTML index...")
        generate_master_html_index()
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Collection interrupted by user")
        logger.info(f"Progress saved. Resume by running the script again.")
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {str(e)}")
        raise
    finally:
        elapsed = time.time() - start_time
        logger.info(f"\n🎉 News collection session complete!")
        logger.info(f"⏱️ Total time: {elapsed/60:.1f} minutes")
        logger.info(f"📊 Total articles collected: {progress_tracker.progress['total_articles']}")
        logger.info(f"📁 Location: s3://{S3_BUCKET_NAME}/{S3_FOLDER_NEWS}/")
        logger.info(f"🌐 Website: http://{S3_BUCKET_NAME}.s3-website-us-east-1.amazonaws.com")
        logger.info(f"📄 Master Index: http://{S3_BUCKET_NAME}.s3-website-us-east-1.amazonaws.com/index.html")
        
        # PHASE 1 FIX: Log final extraction statistics
        final_stats = progress_tracker.progress.get('extraction_stats', {})
        logger.info(f"📈 Final extraction stats: {final_stats.get('successful_extractions', 0)} successful, {final_stats.get('failed_extractions', 0)} failed")
        logger.info(f"🎯 Site-specific extractions: {final_stats.get('site_specific_success', 0)}")
        
        if os.path.exists(PROGRESS_FILE):
            logger.info(f"💾 Progress saved to: {PROGRESS_FILE}")

if __name__ == "__main__":
    main()