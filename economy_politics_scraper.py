#!/usr/bin/env python3
"""
Economy & Politics Scraper - Collects articles about economic consumption
patterns and political dynamics across 12 target countries/regions.

Uses keyword filtering and country-level tagging, following the established
legislation_scraper.py pattern. Articles are tagged with special_tags:
['economy_politics'] and a target_country field.

Implements SEP-001.
"""

import os
import re
import time
import logging
import requests
import sys
import argparse
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Import shared storage utilities
from news_storage import (
    save_article,
    get_today_folder,
    S3_BUCKET_NAME
)

# Import tagging functionality
from article_tagger import detect_continents, detect_countries

import json as json_module

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("economy_politics_scraper")

# Set fresh mode flag
FRESH_MODE = os.environ.get('FRESH_MODE', 'false').lower() == 'true'

if not os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    parser = argparse.ArgumentParser(description='Economy & Politics Scraper')
    parser.add_argument('-fresh', '--fresh', action='store_true',
                       help='Run in fresh mode - bypass idempotency and reprocess all articles')
    args, _ = parser.parse_known_args()
    FRESH_MODE = args.fresh

# Track progress
PROGRESS_FILE = "/tmp/economy_politics_scraper_progress.json" if os.environ.get('AWS_LAMBDA_FUNCTION_NAME') else "economy_politics_scraper_progress.json"


class ProgressTracker:
    def __init__(self, progress_file=PROGRESS_FILE):
        self.progress_file = progress_file
        self.progress = self.load_progress()

    def load_progress(self):
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json_module.load(f)
        return {
            "rss_feeds": {"feeds_completed": []},
            "total_articles": 0,
            "last_updated": None
        }

    def save_progress(self):
        self.progress["last_updated"] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json_module.dump(self.progress, f, indent=2)

    def mark_feed_complete(self, feed_url):
        if feed_url not in self.progress["rss_feeds"]["feeds_completed"]:
            self.progress["rss_feeds"]["feeds_completed"].append(feed_url)
            self.save_progress()

    def is_feed_complete(self, feed_url):
        if FRESH_MODE:
            return False
        return feed_url in self.progress["rss_feeds"].get("feeds_completed", [])


progress_tracker = ProgressTracker()

# URL deduplication tracking
processed_urls = set()


def url_already_processed(url: str) -> bool:
    if FRESH_MODE:
        return False
    return url in processed_urls


def add_processed_url(url: str):
    processed_urls.add(url)


def load_processed_urls():
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


load_processed_urls()

# -------------------------------------------------------------------------
# KEYWORD SETS
# -------------------------------------------------------------------------

ECONOMIC_KEYWORDS = [
    "consumer spending", "retail sales", "consumer prices", "cost of living",
    "purchasing power", "household income", "consumer confidence", "inflation",
    "CPI", "GDP", "economic growth", "disposable income", "consumer debt",
    "credit", "mortgage", "housing market", "food prices", "fuel prices",
    "unemployment", "wages", "poverty", "inequality", "middle class",
    "standard of living", "trade balance", "imports", "exports", "currency",
    "exchange rate", "central bank", "interest rate", "monetary policy",
    "fiscal policy", "budget deficit", "government spending", "tax",
    "subsidy", "remittances", "foreign investment", "FDI", "retail",
    "e-commerce", "manufacturing output", "industrial production",
    "commodity prices",
]

POLITICAL_KEYWORDS = [
    "election", "voter", "polling", "approval rating", "political party",
    "coalition", "opposition", "parliament", "congress", "legislature",
    "referendum", "populism", "nationalism", "ideology", "left-wing",
    "right-wing", "conservative", "liberal", "progressive", "socialist",
    "democracy", "authoritarianism", "corruption", "protest", "civil society",
    "human rights", "press freedom", "judicial independence", "constitutional",
    "impeachment", "political crisis", "cabinet", "prime minister",
    "president", "governor", "political reform", "campaign", "ballot",
    "constituency", "partisan", "bipartisan", "filibuster", "veto",
    "executive order", "political polarization", "voter turnout",
    "disinformation", "propaganda", "censorship", "sanctions",
]

ALL_KEYWORDS = ECONOMIC_KEYWORDS + POLITICAL_KEYWORDS


def matches_economy_politics_keywords(text: str) -> bool:
    """Check if text matches any economy/politics keyword using word boundaries."""
    if not text:
        return False
    text_lower = text.lower()
    for keyword in ALL_KEYWORDS:
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, text_lower):
            return True
    return False


# -------------------------------------------------------------------------
# FEEDS BY COUNTRY/REGION
# -------------------------------------------------------------------------

FEEDS_BY_COUNTRY = {
    "Zimbabwe": [
        "https://www.zimlive.com/feed/",
        "https://www.zimlive.com/category/business/feed/",
        "https://www.zimlive.com/category/politics/feed/",
        "https://www.zimbabwesituation.com/feed/",
        "https://iharare.com/feed/",
        "https://www.newzimbabwe.com/feed/",
        "https://www.zimeye.net/feed/",
        "https://dailynews.co.zw/feed/",
        "https://www.263chat.com/feed/",
        "https://bulawayo24.com/index-id-national.rss",
    ],
    "India": [
        "https://www.livemint.com/rss/economy",
        "https://www.livemint.com/rss/politics",
        "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
        "https://economictimes.indiatimes.com/news/politics-and-nation/rssfeeds/1052732854.cms",
        "https://www.thehindubusinessline.com/economy/feeder/default.rss",
        "https://www.ndtvprofit.com/rss",
        "https://indianexpress.com/section/economy/feed/",
        "https://indianexpress.com/section/political-pulse/feed/",
        "https://scroll.in/feed",
        "https://www.hindustantimes.com/feeds/rss/business/rssfeed.xml",
        "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
        "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml",
    ],
    "China": [
        "https://www.caixinglobal.com/rss.html",
        "https://www.scmp.com/rss/4/feed",
        "https://www.scmp.com/rss/5/feed",
        "https://www.scmp.com/rss/6/feed",
        "https://www.scmp.com/rss/17/feed",
        "https://www.sixthtone.com/rss",
        "https://merics.org/en/rss.xml",
        "https://asia.nikkei.com/rss",
    ],
    "Brazil": [
        "https://braziljournal.com/feed/",
        "https://agenciabrasil.ebc.com.br/rss/economia/feed.xml",
        "https://agenciabrasil.ebc.com.br/rss/politica/feed.xml",
        "https://www.gazetadopovo.com.br/feed/rss/economia.xml",
        "https://www.gazetadopovo.com.br/feed/rss/republica.xml",
        "https://www.gazetadopovo.com.br/feed/rss/republica/congresso.xml",
        "https://riotimesonline.com/feed/",
        "https://en.mercopress.com/rss/brazil",
        "https://www.bbc.com/portuguese/topics/cz74k717pw5t/rss.xml",
    ],
    "USA": [
        "https://thehill.com/feed/",
        "https://www.politico.com/rss/politicopicks.xml",
        "https://feeds.feedburner.com/realclearpolitics/qlMj",
        "https://www.pewresearch.org/feed/",
        "https://www.aei.org/feed/",
        "https://www.heritage.org/rss/all",
        "https://www.census.gov/economic-indicators/indicator.xml",
        "https://fredblog.stlouisfed.org/feed/",
        "https://feeds.npr.org/1001/rss.xml",           # NPR News
        "https://feeds.npr.org/1006/rss.xml",           # NPR Business
        "https://www.pbs.org/newshour/feeds/rss/headlines",  # PBS NewsHour
        "https://feeds.propublica.org/propublica/main",  # ProPublica
        "https://www.cnbc.com/id/10001147/device/rss/rss.html",  # CNBC Top News
        "https://www.cnbc.com/id/10000664/device/rss/rss.html",  # CNBC Economy
        "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",  # NYT Politics
        "https://api.axios.com/feed/",                   # Axios
    ],
    "Eurozone": [
        "https://socialeurope.eu/feed",
        "https://www.politico.eu/feed/",
        "https://ecfr.eu/feed/",
        "https://euobserver.com/rss.xml",
        "https://www.bruegel.org/rss.xml",
        "https://www.ecb.europa.eu/rss/blog.html",
        "https://www.spiegel.de/international/index.rss",
        "https://www.france24.com/en/europe/rss",
        "https://english.elpais.com/rss/elpais/inenglish.xml",
        "https://rss.dw.com/rdf/rss-en-eu",
    ],
    "South Africa": [
        "https://www.dailymaverick.co.za/feed/",
        "https://feeds.24.com/articles/news24/TopStories/rss",
        "https://www.iol.co.za/cmlink/1.640",
        "https://www.moneyweb.co.za/feed/",
        "https://www.biznews.com/feed",
    ],
    "Nigeria": [
        "https://punchng.com/feed/",
        "https://www.thisdaylive.com/feed/",
        "https://www.thisdaylive.com/index.php/category/business/feed/",
        "https://www.thisdaylive.com/index.php/category/politics/feed/",
        "https://www.vanguardngr.com/feed/",
        "https://www.vanguardngr.com/category/business/feed/",
        "https://www.vanguardngr.com/category/politics/feed/",
        "https://businessday.ng/feed/",
        "https://businessday.ng/news/feed/",
        "https://businessday.ng/markets/feed/",
        "https://www.channelstv.com/feed/",
        "https://www.channelstv.com/category/business/feed/",
    ],
    "Kenya": [
        "https://www.standardmedia.co.ke/rss/headlines.php",
        "https://www.standardmedia.co.ke/rss/business.php",
        "https://www.standardmedia.co.ke/rss/politics.php",
        "https://www.capitalfm.co.ke/news/feed/",
    ],
    "Ghana": [
        "https://www.myjoyonline.com/feed/",
        "https://www.myjoyonline.com/business/feed/",
    ],
    "Mauritius": [
        "https://defimedia.info/feed",
    ],
    "DR Congo": [
        "https://www.radiookapi.net/feed",
        "https://actualite.cd/rss.xml",
    ],
}


def get_all_feeds_with_country() -> List[Tuple[str, str]]:
    """Return list of (feed_url, target_country) tuples."""
    feeds = []
    for country, feed_list in FEEDS_BY_COUNTRY.items():
        for url in feed_list:
            feeds.append((url, country))
    return feeds


# -------------------------------------------------------------------------
# DATE FILTERING
# -------------------------------------------------------------------------

def is_recent_article(pub_date: str, days: int = 1) -> bool:
    """Check if article is from the past N days (default: 1 day = 24 hours)"""
    if not pub_date:
        return True

    try:
        from dateutil import parser
        from dateutil.tz import tzutc

        parsed_date = parser.parse(pub_date)
        if parsed_date.tzinfo is None:
            parsed_date = parsed_date.replace(tzinfo=tzutc())

        cutoff_date = datetime.now(tzutc()) - timedelta(days=days)
        return parsed_date >= cutoff_date

    except Exception:
        year_patterns = [
            r'(\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
        ]

        for pattern in year_patterns:
            match = re.search(pattern, pub_date)
            if match:
                year_str = match.group(1)[:4]
                try:
                    year = int(year_str)
                    return year >= 2025
                except ValueError:
                    continue

        logger.debug(f"Could not parse date '{pub_date}', including article")
        return True


# -------------------------------------------------------------------------
# CONTENT EXTRACTION
# -------------------------------------------------------------------------

def extract_full_article_content(url: str) -> Optional[str]:
    """Extract full article content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        for script in soup(["script", "style"]):
            script.decompose()

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
            article_content = soup.find('body')
            if not article_content:
                article_content = soup

        text = article_content.get_text(separator='\n', strip=True)
        return text if text else None

    except Exception as e:
        logger.warning(f"Error extracting content from {url}: {e}")
        return None


# -------------------------------------------------------------------------
# RSS FEED PROCESSING
# -------------------------------------------------------------------------

def process_single_economy_politics_feed(feed_url: str, target_country: str):
    """Process a single RSS feed with keyword filtering and country tagging."""
    if progress_tracker.is_feed_complete(feed_url):
        logger.info(f"Skipping completed feed: {feed_url}")
        return 0

    logger.info(f"Processing economy/politics feed ({target_country}): {feed_url}")
    feed_count = 0

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        }
        response = requests.get(feed_url, headers=headers, timeout=10)
        response.raise_for_status()

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

                link = None
                if item.find('link'):
                    link_elem = item.find('link')
                    if link_elem.get('href'):
                        link = link_elem.get('href')
                    else:
                        link = link_elem.get_text()

                pub_date = ''
                if item.find('pubDate'):
                    pub_date = item.find('pubDate').get_text()
                elif item.find('published'):
                    pub_date = item.find('published').get_text()
                elif item.find('updated'):
                    pub_date = item.find('updated').get_text()

                description = ''
                if item.find('description'):
                    description = item.find('description').get_text()
                elif item.find('summary'):
                    description = item.find('summary').get_text()
                elif item.find('content'):
                    description = item.find('content').get_text()

                if not link:
                    continue

                if url_already_processed(link):
                    logger.debug(f"URL already processed: {link}")
                    continue

                if not is_recent_article(pub_date, days=1):
                    logger.debug(f"Filtering out old article: {title[:50]}... (date: {pub_date})")
                    continue

                # Extract full article content
                full_content = extract_full_article_content(link)
                if not full_content:
                    if description and len(description) > 50:
                        full_content = description
                        logger.info(f"Using RSS description as fallback for: {link}")
                    else:
                        logger.warning(f"Could not extract content from: {link}")
                        continue

                # Keyword filtering - article must match at least one keyword
                combined_text = title + ' ' + description + ' ' + full_content
                if not matches_economy_politics_keywords(combined_text):
                    logger.debug(f"No keyword match: {title[:50]}...")
                    continue

                # Tag the article for geographic/topical info
                tags = {
                    'continents': detect_continents(combined_text),
                    'countries': detect_countries(combined_text),
                    'matched_keywords': [k for k in ALL_KEYWORDS
                                         if re.search(r'\b' + re.escape(k.lower()) + r'\b',
                                                      combined_text.lower())],
                    'special_tags': ['economy_politics'],
                    'target_country': target_country,
                }

                article_id = save_article(
                    title=title,
                    url=link,
                    pub_date=pub_date,
                    description=description,
                    full_content=full_content,
                    feed_url=feed_url,
                    tags=tags,
                    source_type='Economy/Politics Feed'
                )

                if article_id:
                    feed_count += 1
                    add_processed_url(link)
                    logger.info(f"Saved economy/politics article ({target_country}): {title[:50]}...")

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


def process_economy_politics_feeds():
    """Process all economy/politics RSS feeds."""
    if FRESH_MODE:
        logger.info("FRESH MODE: Bypassing idempotency - reprocessing all economy/politics feeds")
        if os.path.exists(PROGRESS_FILE):
            try:
                os.remove(PROGRESS_FILE)
                logger.info("Cleared economy/politics progress file for fresh collection")
            except OSError as e:
                logger.warning(f"Could not remove progress file: {e}")
        progress_tracker.progress = {
            "rss_feeds": {"feeds_completed": []},
            "total_articles": 0,
            "last_updated": None
        }
    else:
        logger.info("IDEMPOTENT MODE: Skipping already processed economy/politics feeds")

    logger.info("=== ECONOMY/POLITICS SCRAPER: Starting ===")

    all_feeds = get_all_feeds_with_country()
    feeds_to_process = [(url, country) for url, country in all_feeds
                        if not progress_tracker.is_feed_complete(url)]

    if not feeds_to_process:
        logger.info("All economy/politics feeds already completed")
        return

    logger.info(f"Processing {len(feeds_to_process)} economy/politics RSS feeds in parallel...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(
            lambda args: process_single_economy_politics_feed(*args),
            feeds_to_process
        ))

    total_processed = sum(results)
    logger.info(f"=== ECONOMY/POLITICS SCRAPER: Complete ({total_processed} total articles) ===")
    logger.info(f"All economy/politics articles saved to s3://{S3_BUCKET_NAME}/{get_today_folder()}/")


# -------------------------------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        process_economy_politics_feeds()
        logger.info("Economy/politics scraping complete!")
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
