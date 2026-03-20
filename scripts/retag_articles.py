#!/usr/bin/env python3
"""
Re-tag all historical articles in S3 with updated article_tagger.

Reads each metadata JSON + corresponding content HTML from S3,
re-runs tag_article() on the content, and writes updated metadata back.
No internet access needed — purely S3 reads/writes + local tagging.

Usage:
    python3 scripts/retag_articles.py                  # retag all dates
    python3 scripts/retag_articles.py --date 2026-03-19  # retag single date
    python3 scripts/retag_articles.py --dry-run          # preview without writing
"""

import argparse
import json
import logging
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3

# Add project root to path so we can import article_tagger
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from article_tagger import tag_article

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("retag_articles")

S3_BUCKET = "news-collection-website"
s3_client = boto3.client('s3', region_name='us-east-1')

# Keywords list matching news_scraper.py
NEWS_KEYWORDS = [
    "energy", "electricity", "blockchain", "artificial intelligence", "AI", "insurance",
    "renewable energy", "solar power", "wind energy", "battery storage",
    "smart grid", "microgrid", "electric vehicles", "capacity market",
    "demand response", "carbon pricing", "carbon tax", "feed-in tariff",
    "grid reliability", "transmission planning", "levelized cost of energy",
    "power purchase agreement", "green bond", "ESG investment", "coal",
    "rare earth minerals", "lithium", "nuclear", "gas", "oil", "supply chain",
    "catastrophe modeling", "exposure data", "reinsurance", "underwriting",
    "climate risk", "war", "civil unrest", "protest",
    "cybersecurity", "digital twin", "predictive analytics",
    "Federal Energy Regulatory Commission", "FERC",
    "North American Electric Reliability Corporation", "NERC",
    "Department of Energy", "DOE",
    "Environmental Protection Agency", "EPA",
    "National Renewable Energy Laboratory", "NREL",
    "International Energy Agency", "IEA",
    "Commodity Futures Trading Commission", "CFTC",
    "Insurance Regulatory and Development Authority", "IRDAI",
    "Standard & Poor's", "Moody's", "Fitch", "Bloomberg",
]


def list_date_folders():
    """List all date folders in the S3 bucket."""
    response = s3_client.list_objects_v2(
        Bucket=S3_BUCKET, Prefix='news/', Delimiter='/'
    )
    folders = []
    for cp in response.get('CommonPrefixes', []):
        date_str = cp['Prefix'].replace('news/', '').rstrip('/')
        if date_str and date_str != 'historical':
            folders.append(date_str)
    return sorted(folders)


def list_metadata_files(date_folder):
    """List all metadata JSON files for a date folder."""
    prefixes = [
        f"news/{date_folder}/metadata/",
        f"news/{date_folder}/rss/metadata/",
        f"news/{date_folder}/direct/metadata/",
    ]
    metadata_files = []
    paginator = s3_client.get_paginator('list_objects_v2')
    for prefix in prefixes:
        for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):
            for obj in page.get('Contents', []):
                if obj['Key'].endswith('.json'):
                    metadata_files.append(obj['Key'])
    return metadata_files


def get_content_key(metadata_key):
    """Derive the content file key from a metadata file key."""
    return metadata_key.replace('/metadata/', '/content/').replace('.json', '.html')


def retag_article(metadata_key, dry_run=False):
    """Re-tag a single article. Returns (metadata_key, old_tags, new_tags, updated)."""
    try:
        # Read metadata
        resp = s3_client.get_object(Bucket=S3_BUCKET, Key=metadata_key)
        metadata = json.loads(resp['Body'].read().decode('utf-8'))

        # Read content
        content_key = get_content_key(metadata_key)
        try:
            resp = s3_client.get_object(Bucket=S3_BUCKET, Key=content_key)
            content = resp['Body'].read().decode('utf-8', errors='replace')
        except s3_client.exceptions.NoSuchKey:
            return (metadata_key, None, None, False)

        # Build combined text (title + description + content) like the scraper does
        title = metadata.get('title', '')
        description = metadata.get('description', '')
        combined_text = f"{title} {description} {content}"

        # Re-tag
        new_tags = tag_article(combined_text, NEWS_KEYWORDS)

        # Preserve special_tags from original metadata (legislation, prediction_market, etc.)
        old_tags = metadata.get('tags', {})
        special_tags = old_tags.get('special_tags', [])
        if special_tags:
            new_tags['special_tags'] = special_tags

        # Check if tags actually changed
        if new_tags == old_tags:
            return (metadata_key, old_tags, new_tags, False)

        if dry_run:
            return (metadata_key, old_tags, new_tags, True)

        # Write updated metadata back to S3
        metadata['tags'] = new_tags
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=metadata_key,
            Body=json.dumps(metadata, indent=2).encode('utf-8'),
            ContentType='application/json',
        )
        return (metadata_key, old_tags, new_tags, True)

    except Exception as e:
        logger.error(f"Error retagging {metadata_key}: {e}")
        return (metadata_key, None, None, False)


def retag_date(date_folder, dry_run=False, max_workers=10):
    """Re-tag all articles for a date folder."""
    metadata_files = list_metadata_files(date_folder)
    if not metadata_files:
        logger.info(f"  {date_folder}: no metadata files")
        return 0, 0

    updated = 0
    unchanged = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(retag_article, key, dry_run): key
            for key in metadata_files
        }
        for future in as_completed(futures):
            key, old_tags, new_tags, was_updated = future.result()
            if was_updated:
                updated += 1
                old_countries = set(old_tags.get('countries', [])) if old_tags else set()
                new_countries = set(new_tags.get('countries', [])) if new_tags else set()
                added = new_countries - old_countries
                if added:
                    logger.debug(f"  +countries {added}: {key.split('/')[-1]}")
            else:
                unchanged += 1

    action = "Would update" if dry_run else "Updated"
    logger.info(f"  {date_folder}: {action} {updated}/{updated + unchanged} articles")
    return updated, unchanged


def main():
    parser = argparse.ArgumentParser(description='Re-tag historical articles with updated tagger')
    parser.add_argument('--date', help='Single date to retag (YYYY-MM-DD)')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    parser.add_argument('--workers', type=int, default=10, help='Parallel workers (default: 10)')
    args = parser.parse_args()

    if args.date:
        date_folders = [args.date]
    else:
        logger.info("Listing all date folders...")
        date_folders = list_date_folders()

    logger.info(f"Re-tagging {len(date_folders)} date folder(s) {'(DRY RUN)' if args.dry_run else ''}")

    total_updated = 0
    total_unchanged = 0

    for date_folder in date_folders:
        updated, unchanged = retag_date(date_folder, dry_run=args.dry_run, max_workers=args.workers)
        total_updated += updated
        total_unchanged += unchanged

    action = "Would update" if args.dry_run else "Updated"
    logger.info(f"\nDone. {action} {total_updated} articles, {total_unchanged} unchanged.")


if __name__ == '__main__':
    main()
