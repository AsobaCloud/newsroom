# Newsroom - AI-Powered News Collection System

A sophisticated news scraper that collects, filters, and presents energy, AI, and blockchain news from multiple sources with intelligent keyword matching and static website hosting.

## Features

- **Smart Filtering**: Uses word boundary regex matching to ensure only relevant articles are collected
- **Multiple Sources**: Scrapes from BBC, CNN, Guardian, Al Jazeera, TechCrunch, Ars Technica, and more
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
├── news_scraper_final.py    # Main scraper script
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── README_news_scraper.md  # Detailed setup instructions
```

## S3 Bucket Structure

```
s3://news-collection-website/
├── index.html                    # Master index
└── news/
    └── YYYY-MM-DD/
        ├── index.html           # Date-specific index
        ├── rss/
        │   ├── metadata/        # Article metadata
        │   └── content/         # Full article content
        └── direct/
            ├── metadata/        # Direct scrape metadata
            └── content/         # Direct scrape content
```

## Usage Examples

### Run News Scraper Only
```bash
python3 news_scraper.py
```

### Run Legislation Scraper Only
```bash
python3 legislation_scraper.py
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

## Shared Storage (`news_storage.py`)

Both scrapers use shared utilities:
- `save_article()`: Save article with metadata to S3
- `exists_in_s3()`: Check if file already exists
- `upload_to_s3_if_not_exists()`: Upload file if not already present
- `get_today_folder()`: Get today's folder path

## Tagging System

**Legislation Articles**:
- ✅ Always tagged with `special_tags: ['legislation']`
- ✅ Geographic tags (continents) detected automatically
- ❌ No keyword matching

**Regular News Articles**:
- ✅ Geographic tags
- ✅ Keyword matching
- ✅ Topic categories
- ✅ Legislation tag only if from legislation feed domain AND matches keywords

## Recent Improvements

- **Enhanced Keyword Matching**: Fixed false positives by implementing word boundary regex
- **Quality Control**: Reduced collection from 700+ low-quality articles to ~50 high-quality articles
- **Better Filtering**: Eliminated irrelevant content like "Celebrity Traitors" matching "AI"
- **Legislation Scraper**: New separate scraper for unfiltered legislative content
- **Shared Storage**: Extracted common S3 operations to reusable utilities

## License

MIT License - See LICENSE file for details.