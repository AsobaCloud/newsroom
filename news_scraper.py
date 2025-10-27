#!/usr/bin/env python3
"""
2025 News Scraper with Static Website Hosting
Target: All news available from 2025 on energy/AI/blockchain topics with full article content
Destination: s3://news-collection-website/ (static website hosting)
Features: Master index for browsing all collected dates
"""

import os
import re
import json
import time
import boto3
import logging
import requests
import hashlib
import sys
import argparse
from datetime import datetime, date
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse, quote
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Import the article tagging module
from article_tagger import tag_article

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("news_scraper")

# Set fresh mode flag - check environment variable first, then command line args
FRESH_MODE = os.environ.get('FRESH_MODE', 'false').lower() == 'true'

# Only parse command line arguments if not in Lambda environment
if not os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    parser = argparse.ArgumentParser(description='News Collection Script with Static Website Hosting')
    parser.add_argument('-fresh', '--fresh', action='store_true', 
                       help='Run in fresh mode - bypass idempotency and reprocess all articles')
    args = parser.parse_args()
    FRESH_MODE = args.fresh

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------

# S3 Configuration - NEW BUCKET FOR STATIC WEBSITE
S3_BUCKET_NAME = "news-collection-website"
# Generate datestamped folder name
today = datetime.now().strftime("%Y-%m-%d")
S3_FOLDER_NEWS = f"news/{today}"

# Track progress - use /tmp in Lambda environment
PROGRESS_FILE = "/tmp/news_scraper_progress.json" if os.environ.get('AWS_LAMBDA_FUNCTION_NAME') else "news_scraper_progress.json"

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

# News sources for 2025 content - Actually working RSS feeds
NEWS_SOURCES = {
    'rss_feeds': [
        # BBC News (confirmed working)
        'https://feeds.bbci.co.uk/news/rss.xml',
        'https://feeds.bbci.co.uk/news/world/rss.xml',
        'https://feeds.bbci.co.uk/news/business/rss.xml',
        'https://feeds.bbci.co.uk/news/technology/rss.xml',
        'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
        
        # CNN (trying common working formats)
        'http://rss.cnn.com/rss/cnn_topstories.rss',
        'http://rss.cnn.com/rss/edition.rss',
        'http://rss.cnn.com/rss/cnn_world.rss',
        
        # Guardian (confirmed working)
        'https://www.theguardian.com/world/rss',
        'https://www.theguardian.com/business/rss',
        'https://www.theguardian.com/technology/rss',
        'https://www.theguardian.com/environment/rss',
        
        # Al Jazeera
        'https://www.aljazeera.com/xml/rss/all.xml',
        
        # Financial/Business
        'https://www.marketwatch.com/rss/topstories',
        'https://feeds.finance.yahoo.com/rss/2.0/headline',
        
        # Tech/Industry
        'https://feeds.arstechnica.com/arstechnica/index',
        'https://techcrunch.com/feed/',
        'https://www.wired.com/feed/rss',
        'https://feeds.feedburner.com/venturebeat/SZYF',
        
        # Academic/Research
        'https://rss.arxiv.org/rss/econ',
        'https://rss.arxiv.org/rss/cs.AI',
        'https://rss.arxiv.org/rss/cs.CL',
        
        # Energy/Policy focused
        'https://www.energy.gov/rss/all.xml',
        'https://www.whitehouse.gov/feed/',
        
        # International
        'https://feeds.cfr.org/feeds/site/current.xml',
        
        # Energy Industry Publications (verified working)
        'https://feeds.feedburner.com/EnergyCentral',
        'https://feeds.feedburner.com/TDWorld',
        'https://www.powermag.com/feed/',
        'https://www.tdworld.com/rss.xml',
        'https://feeds.feedburner.com/RenewableEnergyWorld',
        'https://www.renewableenergyworld.com/rss/',
        'https://www.cleanenergywire.org/rss.xml',
        'https://feeds.feedburner.com/GreentechMedia',
        'https://www.worldoil.com/rss/',
        
        # Energy Technology & Storage
        'https://feeds.feedburner.com/SmartGridNews',
        'https://feeds.feedburner.com/EnergyStorageNews',
        'https://feeds.feedburner.com/NuclearEnergyInstitute',
        'https://feeds.feedburner.com/WorldNuclearNews',
        
        # Supply Chain & Materials
        'https://feeds.feedburner.com/CriticalMaterials',
        'https://www.mining.com/rss/',
        
        # International Energy Organizations
        'https://feeds.feedburner.com/IEA',
        'https://www.irena.org/rss/',
        
        # Regional Energy Sources
        'https://feeds.feedburner.com/EnergyPost',
        'https://www.canadianenergy.com/rss/',
        
        # Energy News & Analysis
        'https://feeds.feedburner.com/EnergyInDepth',
        'https://feeds.feedburner.com/EnergyWire',
        'https://feeds.feedburner.com/GlobalEnergy',
        'https://feeds.feedburner.com/WorldEnergy',
        'https://feeds.feedburner.com/EnergyTransition',
        'https://feeds.feedburner.com/AfricaIntelligence',
        'https://feeds.feedburner.com/IntelligenceOnline',

        # Intelligence & Security Analysis
        'https://feeds.feedburner.com/Stratfor',
        'https://feeds.feedburner.com/CSIS',
        'https://feeds.feedburner.com/CFR',
        'https://feeds.feedburner.com/AtlanticCouncil',
        'https://feeds.feedburner.com/DefenseNews',
        'https://feeds.feedburner.com/DefenseOne',
        'https://feeds.feedburner.com/WarOnTheRocks',
        'https://feeds.feedburner.com/JustSecurity',
        'https://feeds.feedburner.com/Lawfare',
        'https://feeds.feedburner.com/ForeignAffairs',
        'https://feeds.feedburner.com/ForeignPolicy',

        # ===== TESTED & WORKING SOURCES (42 additional) =====
        # AFRICA (15 sources)
        'https://www.premiumtimesng.com/rss',
        'https://www.thisdaylive.com/rss',
        'https://guardian.ng/rss',
        'https://businessday.ng/rss',
        'https://www.citizen.co.za/rss',
        'https://dailynewsegypt.com/rss',
        'https://www.egyptindependent.com/rss',
        'https://www.moroccoworldnews.com/rss',
        'https://www.myjoyonline.com/rss',
        'https://dailynews.co.tz/rss',
        'https://observer.ug/rss',
        'https://www.independent.co.ug/rss',
        'https://www.namibian.com.na/rss',
        'https://www.gabonreview.com/rss',
        'https://expressodasilhas.cv/rss',

        # LATIN AMERICA (12 sources)
        'https://www.infomoney.com.br/rss',
        'https://www.excelsior.com.mx/rss',
        'https://www.elfinanciero.com.mx/rss',
        'https://www.latercera.com/rss',
        'https://www.larepublica.co/rss',
        'https://peru21.pe/rss',
        'https://www.eltiempo.com.ve/rss',
        'https://www.elcomercio.com/rss',
        'https://www.elpais.com.uy/rss',
        'https://www.stabroeknews.com/rss',
        'https://www.kaieteurnewsonline.com/rss',
        'https://www.guyanachronicle.com/rss',

        # MENA (15 sources)
        'https://www.aljazeera.com/rss',
        'https://www.tehrantimes.com/rss',
        'https://www.middleeastmonitor.com/feed/',
        'https://www.middleeasteye.net/rss',
        'https://www.newarab.com/rss',
        'https://www.al-monitor.com/rss',
        'https://themedialine.org/rss',
        'https://www.lemauricien.com/rss',
        'https://www.lanation.dj/rss',
        'https://www.dabangasudan.org/rss',
        'https://eyeradio.org/rss',
        'https://www.newsroom.gy/rss',
        'https://dailynewsegypt.com/rss',
        'https://www.egyptindependent.com/rss',
        'https://www.moroccoworldnews.com/rss'
    ],
    'news_apis': [
        'https://newsapi.org/v2/everything',  # Requires API key
        'https://api.nytimes.com/svc/search/v2/articlesearch.json'  # Requires API key
    ],
    'direct_scraping': [
        'https://www.reuters.com/technology/',
        'https://www.reuters.com/business/energy/',
        'https://techcrunch.com/',
        'https://www.theverge.com/',
        'https://arstechnica.com/',
        'https://www.wired.com/',
        'https://www.coindesk.com/',
        'https://cointelegraph.com/'
    ]
}

s3_client = boto3.client("s3", region_name="us-east-1")

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
            "last_updated": None
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
        if FRESH_MODE:
            return False
        return feed_url in self.progress["rss_feeds"].get("feeds_completed", [])
    
    def mark_source_complete(self, source_url):
        """Mark a source as completed"""
        if source_url not in self.progress["direct_scraping"]["sources_completed"]:
            self.progress["direct_scraping"]["sources_completed"].append(source_url)
            self.save_progress()
    
    def is_source_complete(self, source_url):
        """Check if source was already processed"""
        if FRESH_MODE:
            return False
        return source_url in self.progress["direct_scraping"].get("sources_completed", [])
    
    def increment_articles(self, count=1):
        """Increment total article count"""
        self.progress["total_articles"] += count
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
    if FRESH_MODE:
        return False
    return key in S3_MANIFEST

def url_already_processed(url: str) -> bool:
    """Check if URL was already processed (idempotency across runs)"""
    if FRESH_MODE:
        return False
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
# NEWS EXTRACTION UTILITIES
# -------------------------------------------------------------------------
def try_archive_fallback(url: str) -> Optional[str]:
    """Try to get article content from archive.is"""
    try:
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

def is_2025_article(article_date_str: str) -> bool:
    """Check if article is from 2025 or recent (since we might not have exact dates)"""
    if not article_date_str:
        # If no date, assume it's recent and include it
        return True
    
    # Try to extract year from date string
    year_match = re.search(r'202[5-9]', article_date_str)
    if year_match:
        year = int(year_match.group())
        return year >= 2025
    
    # Look for 2025 indicators in various formats
    if '2025' in article_date_str:
        return True
    
    # If we can't determine the year, assume it's recent and include it
    return True

def extract_full_article_content(url: str) -> Optional[str]:
    """Extract full article content from URL with archive.is fallback"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'ads']):
            element.decompose()
        
        # Try multiple selectors for article content
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
                    break
        
        if not article_content:
            # Fallback: get all paragraph text
            paragraphs = soup.find_all('p')
            article_content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        return article_content if len(article_content) > 100 else None
        
    except Exception as e:
        logger.debug(f"Direct extraction failed for {url}: {str(e)}")
        
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
# RSS FEED PROCESSING
# -------------------------------------------------------------------------
def process_single_rss_feed(feed_url):
    """Process a single RSS feed - designed for parallel execution"""
    if progress_tracker.is_feed_complete(feed_url):
        logger.info(f"Skipping completed feed: {feed_url}")
        return 0
        
    logger.info(f"Processing RSS feed: {feed_url}")
    feed_count = 0
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(feed_url, headers=headers, timeout=10)  # Reduced timeout
        response.raise_for_status()
        
        # Try different parsing methods
        soup = None
        items = []
        
        # Method 1: XML parser (preferred for RSS/Atom)
        try:
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')
            if not items:
                items = soup.find_all('entry')  # Atom feeds
        except:
            pass
        
        # Method 2: lxml parser fallback
        if not items:
            try:
                soup = BeautifulSoup(response.content, 'lxml')
                items = soup.find_all('item')
                if not items:
                    items = soup.find_all('entry')  # Atom feeds
            except:
                pass
        
        # Method 3: HTML parser fallback
        if not items:
            try:
                soup = BeautifulSoup(response.content, 'html.parser')
                items = soup.find_all('item')
                if not items:
                    items = soup.find_all('entry')  # Atom feeds
            except:
                pass
            
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
                        continue
                    
                    # Check for URL-based deduplication first (fastest check)
                    if url_already_processed(link):
                        logger.debug(f"URL already processed: {link}")
                        continue
                    
                    # Check if 2025 article - for debugging let's see what we're filtering
                    if not is_2025_article(pub_date):
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
                    
                    # Tag the article with geographic and topical information
                    combined_text = title + ' ' + description + ' ' + full_content
                    tags = tag_article(combined_text, NEWS_KEYWORDS)
                    
                    # Create metadata with tagging information
                    metadata = {
                        'title': title,
                        'url': link,
                        'pub_date': pub_date,
                        'description': description,
                        'source': 'RSS Feed',
                        'feed_url': feed_url,
                        'content_length': len(full_content),
                        'collection_date': datetime.now().isoformat(),
                        'tags': tags
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
        logger.info(f"Completed feed: {feed_url} ({feed_count} articles)")
        return feed_count
        
    except Exception as e:
        logger.error(f"Error processing RSS feed {feed_url}: {str(e)}")
        return 0

def process_rss_feeds():
    """Process RSS feeds in parallel for 2025 news articles"""
    logger.info("=== RSS FEEDS: Starting ===")
    
    # Filter out already completed feeds
    feeds_to_process = [feed for feed in NEWS_SOURCES['rss_feeds'] 
                       if not progress_tracker.is_feed_complete(feed)]
    
    if not feeds_to_process:
        logger.info("All RSS feeds already completed")
        return
    
    logger.info(f"Processing {len(feeds_to_process)} RSS feeds in parallel...")
    
    # Process feeds in parallel with max 10 workers to avoid overwhelming servers
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_single_rss_feed, feeds_to_process))
    
    total_processed = sum(results)
    logger.info(f"=== RSS FEEDS: Complete ({total_processed} total articles) ===")

# -------------------------------------------------------------------------
# DIRECT WEBSITE SCRAPING
# -------------------------------------------------------------------------
def scrape_website_articles(base_url: str, max_articles: int = 50):
    """Scrape articles directly from news websites"""
    if progress_tracker.is_source_complete(base_url):
        logger.info(f"Skipping completed source: {base_url}")
        return 0
        
    logger.info(f"Scraping website: {base_url}")
    articles_found = 0
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(base_url, headers=headers, timeout=30)
        response.raise_for_status()
        
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
                if article_date and not is_2025_article(article_date):
                    continue
                
                # Extract full content
                full_content = extract_full_article_content(article_url)
                if not full_content:
                    continue
                
                # Check content for keywords too
                if not matches_keywords(full_content):
                    continue
                
                # Tag the article with geographic and topical information
                combined_text = title + ' ' + full_content
                tags = tag_article(combined_text, NEWS_KEYWORDS)
                
                # Create metadata with tagging information
                metadata = {
                    'title': title,
                    'url': article_url,
                    'date': article_date or 'Unknown',
                    'source': 'Direct Scraping',
                    'base_url': base_url,
                    'content_length': len(full_content),
                    'collection_date': datetime.now().isoformat(),
                    'tags': tags
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
# HTML INDEX GENERATORS
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
        
        # Generate HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Collection - {today}</title>
    <link rel="stylesheet" href="https://asoba.co/includes/common.css">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            display: block;
        }}
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        .content {{
            padding: 30px;
        }}
        .article {{
            border-bottom: 1px solid #eee;
            padding: 20px 0;
            transition: background-color 0.2s;
        }}
        .article:hover {{
            background-color: #f9f9f9;
        }}
        .article:last-child {{
            border-bottom: none;
        }}
        .article-title {{
            margin: 0 0 10px 0;
            font-size: 1.3em;
            font-weight: 600;
        }}
        .article-title a {{
            color: #333;
            text-decoration: none;
            transition: color 0.2s;
        }}
        .article-title a:hover {{
            color: #667eea;
        }}
        .article-meta {{
            display: flex;
            gap: 15px;
            margin-bottom: 10px;
            font-size: 0.9em;
            color: #666;
        }}
        .article-source {{
            background: #e3f2fd;
            color: #1976d2;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        .article-date {{
            color: #888;
        }}
        .article-length {{
            color: #888;
        }}
        .article-description {{
            color: #555;
            margin-top: 10px;
            line-height: 1.5;
        }}
        .article-description p {{
            margin: 0 0 10px 0;
        }}
        .article-description p:last-child {{
            margin-bottom: 0;
        }}
        .view-content {{
            margin-top: 15px;
        }}
        .view-content a {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.9em;
            transition: background-color 0.2s;
        }}
        .view-content a:hover {{
            background: #5a6fd8;
        }}
        .filters {{
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        .filter-group {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            align-items: center;
        }}
        .filter-group label {{
            font-weight: 500;
            color: #333;
            margin-bottom: 5px;
            display: block;
        }}
        .filter-group select, .filter-group input {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 0.9em;
            width: 100%;
        }}
        .filter-row {{
            display: flex;
            flex-direction: column;
        }}
        .back-link {{
            margin-bottom: 20px;
        }}
        .back-link a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        .back-link a:hover {{
            text-decoration: underline;
        }}
        .article-tags {{
            margin: 10px 0;
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }}
        .tag {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        .tag-continent {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        .tag-topic {{
            background: #f3e5f5;
            color: #7b1fa2;
        }}
        .tag-keywords {{
            background: #e8f5e8;
            color: #2e7d32;
        }}
        @media (max-width: 768px) {{
            .stats {{
                flex-direction: column;
                gap: 15px;
            }}
            .filter-group {{
                flex-direction: column;
                align-items: flex-start;
            }}
            .article-meta {{
                flex-direction: column;
                gap: 5px;
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
        <div class="container">
            <div class="header">
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
        
        <div class="content">
            <div class="back-link">
                <a href="http://news-collection-website.s3-website-us-east-1.amazonaws.com/">← Back to All Dates</a>
            </div>
            
            <div class="filters">
                <div class="filter-group">
                    <div class="filter-row">
                        <label for="sourceFilter">Filter by source:</label>
                        <select id="sourceFilter">
                            <option value="">All sources</option>
                            {''.join(f'<option value="{source}">{source}</option>' for source in sorted(set(article.get('source', 'Unknown') for article in articles)))}
                        </select>
                    </div>
                    <div class="filter-row">
                        <label for="continentFilter">Filter by continent:</label>
                        <select id="continentFilter">
                            <option value="">All continents</option>
                            <option value="Africa">Africa</option>
                            <option value="Americas">Americas</option>
                            <option value="Asia">Asia</option>
                            <option value="Europe">Europe</option>
                            <option value="Global">Global</option>
                            <option value="Oceania">Oceania</option>
                        </select>
                    </div>
                    <div class="filter-row">
                        <label for="topicFilter">Filter by topic:</label>
                        <select id="topicFilter">
                            <option value="">All topics</option>
                            <option value="ai">AI</option>
                            <option value="energy">Energy</option>
                            <option value="blockchain">Blockchain</option>
                            <option value="insurance">Insurance</option>
                            <option value="geopolitics">Geopolitics</option>
                        </select>
                    </div>
                    <div class="filter-row">
                        <label for="keywordFilter">Filter by keyword:</label>
                        <select id="keywordFilter">
                            <option value="">All keywords</option>
                            {''.join(f'<option value="{keyword}">{keyword.title()}</option>' for keyword in sorted(set([kw for article in articles for kw in article.get('tags', {}).get('matched_keywords', [])])))}
                        </select>
                    </div>
                    <div class="filter-row">
                        <label for="searchInput">Search:</label>
                        <input type="text" id="searchInput" placeholder="Search articles...">
                    </div>
                </div>
            </div>
            
            <div id="articlesList">"""
        
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
            
            # Extract tag information
            tags = article.get('tags', {})
            continents = tags.get('continents', [])
            core_topics = tags.get('core_topics', [])
            matched_keywords = tags.get('matched_keywords', [])
            
            # Create tag display
            tag_elements = []
            if continents:
                tag_elements.append(f'<span class="tag tag-continent">{" ".join(continents)}</span>')
            if core_topics:
                tag_elements.append(f'<span class="tag tag-topic">{" ".join(core_topics)}</span>')
            if matched_keywords:
                tag_elements.append(f'<span class="tag tag-keywords">{" ".join(matched_keywords[:3])}</span>')
            
            tags_html = ''.join(tag_elements)
            
            # Create data attributes for filtering
            continents_str = ' '.join(continents) if continents else ''
            topics_str = ' '.join(core_topics) if core_topics else ''
            keywords_str = ' '.join(matched_keywords) if matched_keywords else ''
            
            html_content += f"""
                <div class="article" data-source="{article.get('source', 'Unknown')}" data-title="{article.get('title', '').lower()}" data-description="{description.lower()}" data-continents="{continents_str}" data-topics="{topics_str}" data-keywords="{keywords_str}">
                    <h3 class="article-title">
                        <a href="{article['url']}" target="_blank">{article.get('title', 'No Title')}</a>
                    </h3>
                    <div class="article-meta">
                        <span class="article-source">{article.get('source', 'Unknown')}</span>
                        <span class="article-date">{formatted_date}</span>
                        <span class="article-length">{article.get('content_length', 0):,} chars</span>
                    </div>
                    {'<div class="article-tags">' + tags_html + '</div>' if tags_html else ''}
                    {'<div class="article-description">' + description + '</div>' if description else ''}
                    <div class="view-content">
                        <a href="{content_path}" target="_blank">📖 View Full Content</a>
                    </div>
                </div>"""
        
        html_content += """
            </div>
        </div>
    </div>
    
    <script>
        // Filter functionality
        const sourceFilter = document.getElementById('sourceFilter');
        const continentFilter = document.getElementById('continentFilter');
        const topicFilter = document.getElementById('topicFilter');
        const keywordFilter = document.getElementById('keywordFilter');
        const searchInput = document.getElementById('searchInput');
        const articlesList = document.getElementById('articlesList');
        const articles = document.querySelectorAll('.article');
        
        function filterArticles() {
            const selectedSource = sourceFilter.value.toLowerCase();
            const selectedContinent = continentFilter.value;
            const selectedTopic = topicFilter.value;
            const selectedKeyword = keywordFilter.value.toLowerCase();
            const searchTerm = searchInput.value.toLowerCase();
            
            articles.forEach(article => {
                const source = article.dataset.source.toLowerCase();
                const title = article.dataset.title;
                const description = article.dataset.description;
                const continents = article.dataset.continents || '';
                const topics = article.dataset.topics || '';
                const keywords = article.dataset.keywords || '';
                
                const sourceMatch = !selectedSource || source.includes(selectedSource);
                const continentMatch = !selectedContinent || continents.includes(selectedContinent);
                const topicMatch = !selectedTopic || topics.includes(selectedTopic);
                const keywordMatch = !selectedKeyword || keywords.toLowerCase().includes(selectedKeyword);
                const searchMatch = !searchTerm || title.includes(searchTerm) || description.includes(searchTerm);
                
                if (sourceMatch && continentMatch && topicMatch && keywordMatch && searchMatch) {
                    article.style.display = 'block';
                } else {
                    article.style.display = 'none';
                }
            });
        }
        
        sourceFilter.addEventListener('change', filterArticles);
        continentFilter.addEventListener('change', filterArticles);
        topicFilter.addEventListener('change', filterArticles);
        keywordFilter.addEventListener('change', filterArticles);
        searchInput.addEventListener('input', filterArticles);
        
        // Initialize
        filterArticles();
    </script>
    </main>
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
    """Add today's card to the master HTML index file"""
    logger.info("📄 Adding today's card to master HTML index...")
    
    try:
        # Load the existing archive index page
        try:
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key="index.html")
            html_content = response['Body'].read().decode('utf-8')
        except:
            # If no existing file, load from local template
            with open('index.html', 'r') as f:
                html_content = f.read()
        
        # Get today's stats
        article_count = 0
        sources = set()
        
        # Count articles from today's folder
        try:
            paginator = s3_client.get_paginator('list_objects_v2')
            
            # Count RSS articles
            page_iterator = paginator.paginate(
                Bucket=S3_BUCKET_NAME,
                Prefix=f"news/{today}/rss/metadata/"
            )
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        if obj['Key'].endswith('.json'):
                            try:
                                response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=obj['Key'])
                                metadata = json.loads(response['Body'].read().decode('utf-8'))
                                article_count += 1
                                if 'source' in metadata:
                                    sources.add(metadata['source'])
                            except Exception as e:
                                logger.debug(f"Error loading metadata: {e}")
            
            # Count direct scraping articles
            page_iterator = paginator.paginate(
                Bucket=S3_BUCKET_NAME,
                Prefix=f"news/{today}/direct/metadata/"
            )
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        if obj['Key'].endswith('.json'):
                            try:
                                response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=obj['Key'])
                                metadata = json.loads(response['Body'].read().decode('utf-8'))
                                article_count += 1
                                if 'source' in metadata:
                                    sources.add(metadata['source'])
                            except Exception as e:
                                logger.debug(f"Error loading metadata: {e}")
        except Exception as e:
            logger.debug(f"Error counting articles for {today}: {e}")
        
        # Create today's card HTML using the same structure as blog.html content cards
        today_card = f"""
            <article class="content-card" data-type="news" onclick="window.location.href='news/{today}/index.html'">
                <div class="card-image" style="background: linear-gradient(135deg, var(--primary-blue) 0%, #9D93D6 100%);">
                    <span class="content-type-badge" style="background: var(--primary-blue); color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: 500;">News</span>
                </div>
                <div class="card-content">
                    <h3 class="card-title">Daily News Collection - {today}</h3>
                    <p class="card-excerpt">Complete collection of {article_count} articles from {len(sources)} sources covering energy, AI, and blockchain topics.</p>
                    <div class="card-meta">
                        <span class="card-date">{today}</span>
                        <span class="card-read-time">{article_count} articles</span>
                    </div>
                </div>
            </article>
        """
        
        # Use BeautifulSoup to properly handle HTML manipulation
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the content grid
        content_grid = soup.find('main', class_='content-grid')
        if content_grid:
            # Find and remove any existing cards for today
            existing_cards = content_grid.find_all('article', {'data-type': 'news'})
            for card in existing_cards:
                title = card.find('h3', class_='card-title')
                if title and f'Daily News Collection - {today}' in title.get_text():
                    logger.info(f"Removing existing card for {today}")
                    card.decompose()
            
            # Parse the new card and add it
            new_card_soup = BeautifulSoup(today_card, 'html.parser')
            new_card = new_card_soup.find('article')
            if new_card:
                # Insert at the beginning of content-grid
                content_grid.insert(0, new_card)
                logger.info(f"Added new card for {today}")
        
        # Convert back to HTML string
        html_content = str(soup)
        
        # Upload the updated HTML file to S3
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
            logger.info(f"✓ Updated master HTML index: s3://{S3_BUCKET_NAME}/index.html")
            return True
        else:
            logger.error("Failed to upload master HTML index to S3")
            return False
            
    except Exception as e:
        logger.error(f"Error updating master HTML index: {str(e)}")
        return False
        
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
        
        # Generate HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Collection Archive</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 3em;
            font-weight: 300;
        }}
        .header p {{
            margin: 15px 0 0 0;
            opacity: 0.9;
            font-size: 1.2em;
        }}
        .overview {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 30px;
        }}
        .overview-stat {{
            text-align: center;
        }}
        .overview-number {{
            font-size: 2.5em;
            font-weight: bold;
            display: block;
        }}
        .overview-label {{
            font-size: 1em;
            opacity: 0.8;
        }}
        .content {{
            padding: 40px;
        }}
        .date-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        .date-card {{
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.2s;
            background: white;
        }}
        .date-card:hover {{
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        .date-card h3 {{
            margin: 0 0 15px 0;
            color: #333;
            font-size: 1.3em;
        }}
        .date-card a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }}
        .date-card a:hover {{
            text-decoration: underline;
        }}
        .date-stats {{
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            font-size: 0.9em;
            color: #666;
        }}
        .date-stat {{
            background: #f8f9fa;
            padding: 4px 8px;
            border-radius: 4px;
        }}
        .date-description {{
            color: #555;
            font-size: 0.9em;
            margin-bottom: 15px;
        }}
        .view-button {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.9em;
            transition: background-color 0.2s;
        }}
        .view-button:hover {{
            background: #5a6fd8;
        }}
        .search-section {{
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        .search-group {{
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .search-group input {{
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 1em;
            flex: 1;
            min-width: 200px;
        }}
        .no-dates {{
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }}
        .no-dates h3 {{
            margin: 0 0 10px 0;
            font-size: 1.5em;
        }}
        @media (max-width: 768px) {{
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
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
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
# MAIN EXECUTION
# -------------------------------------------------------------------------
def main():
    if FRESH_MODE:
        logger.info("🔄 FRESH MODE: Bypassing idempotency - reprocessing all articles")
        # Clear progress file in fresh mode
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
            logger.info("🗑️ Cleared progress file for fresh collection")
        # Reset progress tracker
        progress_tracker.progress = {
            "rss_feeds": {"feeds_completed": []},
            "direct_scraping": {"sources_completed": []},
            "total_articles": 0,
            "last_updated": None
        }
    else:
        logger.info("💾 IDEMPOTENT MODE: Skipping already processed articles")
    
    logger.info("🚀 Starting 2025 News Collection with Static Website")
    logger.info(f"Target S3 location: s3://{S3_BUCKET_NAME}/{S3_FOLDER_NEWS}/")
    logger.info(f"Website URL: http://{S3_BUCKET_NAME}.s3-website-us-east-1.amazonaws.com")
    logger.info(f"Current progress: {progress_tracker.progress['total_articles']} articles")
    
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
        
        if os.path.exists(PROGRESS_FILE):
            logger.info(f"💾 Progress saved to: {PROGRESS_FILE}")

if __name__ == "__main__":
    main()