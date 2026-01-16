# Newsroom - AI-Powered News Collection System

A sophisticated news scraper that collects, filters, and presents energy, AI, and blockchain news from multiple sources with intelligent keyword matching and static website hosting.

## Features

- **Smart Filtering**: Uses word boundary regex matching to ensure only relevant articles are collected
- **Multiple Sources**: Scrapes from BBC, CNN, Guardian, Al Jazeera, TechCrunch, Ars Technica, and more
- **Legislation Tracking**: Collects legislative content from US Congress, UK Parliament, EU, Australia, Brazil, and South Africa
- **Prediction Markets**: Fetches political prediction markets from Polymarket with country-level tagging
- **Static Website**: Automatically generates browsable HTML indexes for each collection date
- **S3 Integration**: Stores content in AWS S3 with date-organized folders
- **Idempotent**: Prevents duplicate processing of articles
- **Progress Tracking**: Saves progress to resume interrupted collections

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AWS**:
   ```bash
   aws configure
   ```

3. **Run the Scraper**:
   ```bash
   python3 news_scraper_final.py
   ```

4. **View Results**:
   - Master Index: `http://news-collection-website.s3-website-us-east-1.amazonaws.com/`
   - Date-specific: `http://news-collection-website.s3-website-us-east-1.amazonaws.com/news/YYYY-MM-DD/`

## Configuration

The scraper targets these keywords:
- **Energy**: renewable, solar, wind, nuclear, battery, grid, power, energy
- **AI**: artificial intelligence, machine learning, AI, ML, neural network, deep learning
- **Blockchain**: blockchain, cryptocurrency, bitcoin, ethereum, crypto, DeFi, Web3

## File Structure

```
newsroom/
├── news_scraper.py          # Main news scraper script
├── legislation_scraper.py   # Legislative feed scraper
├── polymarket_scraper.py    # Polymarket prediction markets scraper
├── article_tagger.py        # Geographic and topic tagging
├── news_storage.py          # Shared S3 storage utilities
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── lambda/
│   ├── lambda_news_scraper.py  # Lambda entry handler
│   └── lambda_wrapper.py       # Orchestrates all scrapers
├── scripts/
│   └── deploy_lambda.sh     # Lambda deployment script
└── docs/
    └── README_news_scraper.md  # Detailed setup instructions
```

## S3 Bucket Structure

```
s3://news-collection-website/
├── index.html                    # Master index (all dates)
└── news/
    └── YYYY-MM-DD/
        ├── index.html           # Date-specific index (all articles for that date)
        ├── metadata/            # All article metadata (news + legislation)
        ├── content/             # All article content (news + legislation)
        ├── rss/
        │   ├── metadata/        # RSS article metadata (legacy)
        │   └── content/         # RSS article content (legacy)
        └── direct/
            ├── metadata/        # Direct scrape metadata (legacy)
            └── content/         # Direct scrape content (legacy)
```

**Note**: News, legislation, and Polymarket articles are all stored in the same `metadata/` and `content/` folders at the date level. The HTML index generation scans all metadata folders to include all articles. Use the `source` field or `special_tags` to filter by type.

## Usage Examples

### Run News Scraper Only
```bash
python3 news_scraper.py
```

### Run Legislation Scraper Only
```bash
python3 legislation_scraper.py
```

### Run Polymarket Scraper Only
```bash
python3 polymarket_scraper.py
```

### Fresh Mode (Bypass Idempotency)
```bash
# Reprocess everything
python3 news_scraper.py --fresh
python3 legislation_scraper.py --fresh
```

## How It Works

### News Scraper (`news_scraper.py`)
1. Fetches articles from RSS feeds and direct scraping
2. Filters articles by keyword matching (energy, AI, blockchain, etc.)
3. Tags articles with geographic and topical information
4. Saves to S3 with metadata and content
5. Generates HTML indexes

### Legislation Scraper (`legislation_scraper.py`)
1. Fetches articles from legislative RSS feeds
2. **NO keyword filtering** - collects ALL articles from feeds
3. Tags articles with geographic information
4. Always adds `legislation` tag to metadata
5. Saves to same S3 bucket using shared storage utilities
6. Articles appear in same HTML indexes (filter by legislation tag)

### Polymarket Scraper (`polymarket_scraper.py`)
1. Fetches prediction markets from Polymarket Gamma API (no auth required)
2. Filters for political/geopolitical markets using keyword matching
3. Detects country mentions from market questions and descriptions
4. Tags with `prediction_market` special tag and detected countries
5. Saves to same S3 bucket using shared storage utilities
6. Typically collects 100-150 political markets per run

**Polymarket API**: `https://gamma-api.polymarket.com/markets`
- No authentication required
- Supports pagination via `limit` and `offset` parameters
- Returns market data including question, prices, volume, liquidity

## Shared Storage (`news_storage.py`)

All three scrapers use shared utilities:
- `save_article()`: Save article with metadata to S3
- `exists_in_s3()`: Check if file already exists
- `upload_to_s3_if_not_exists()`: Upload file if not already present
- `get_today_folder()`: Get today's folder path

## Tagging System

**Regular News Articles**:
- ✅ Geographic tags (continents)
- ✅ Keyword matching
- ✅ Topic categories (energy, AI, blockchain, insurance, geopolitics)

**Legislation Articles**:
- ✅ Always tagged with `special_tags: ['legislation']`
- ✅ Geographic tags (continents) detected automatically
- ❌ No keyword matching (collects all from legislative feeds)

**Polymarket Articles**:
- ✅ Always tagged with `special_tags: ['prediction_market']`
- ✅ Country-level tagging (e.g., "United States", "Ukraine", "Mexico")
- ✅ Geographic tags (continents) detected automatically
- ✅ Keyword filtering for political/geopolitical markets
- ✅ Market data stored (volume, liquidity, prices, outcomes)

## Lambda Deployment

The newsroom system runs as an AWS Lambda function in **us-east-1** that is triggered by:
- **Manual Update**: Click "Update" button in the UI (calls API Gateway endpoint)
- **Scheduled**: Daily at 11PM Central Time (5AM UTC) via EventBridge

When triggered, all three scrapers run in sequence:
1. `news_scraper.py` - Collects keyword-filtered news articles
2. `legislation_scraper.py` - Collects unfiltered legislative articles
3. `polymarket_scraper.py` - Collects political prediction markets

All scrapers share the same S3 bucket and save articles to the same date-organized folders, allowing them to appear together on the daily index pages.

### Deploying Updates

```bash
cd /path/to/newsroom
./scripts/deploy_lambda.sh
```

The deploy script:
- Creates/updates the Lambda function in us-east-1
- Sets up EventBridge rule for daily scheduling
- Packages all scrapers and dependencies

`lambda_wrapper.py` forces `FRESH_MODE=true` before invoking each scraper, clearing their progress trackers so every Lambda run reprocesses that day's feeds end-to-end. When running locally you can mirror this behaviour by passing `--fresh` (or setting `FRESH_MODE=true`) if you need to bypass idempotency manually.

## Recent Improvements

- **Polymarket Integration**: New scraper for political prediction markets with country-level tagging
- **Country Detection**: Polymarket articles tagged with specific countries (40+ countries supported)
- **Deploy Script Fix**: Added explicit us-east-1 region to all Lambda/EventBridge commands
- **Enhanced Keyword Matching**: Fixed false positives by implementing word boundary regex
- **Quality Control**: Reduced collection from 700+ low-quality articles to ~50 high-quality articles
- **Better Filtering**: Eliminated irrelevant content like "Celebrity Traitors" matching "AI"
- **Legislation Scraper**: Separate scraper for legislative content (bypasses keyword filtering, respects date filtering)
- **Shared Storage**: Extracted common S3 operations to reusable utilities
- **Date Filtering**: Legislation scraper now filters by past 24 hours (same timeframe as news scraper)
- **Error Handling**: Improved logging and error handling in Lambda wrapper

## License

MIT License - See LICENSE file for details.