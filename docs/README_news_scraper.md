# News Scraper Setup and Usage Guide

## Overview
This news scraper collects energy, AI, and blockchain-related news articles from various RSS feeds and websites, storing them in an S3 bucket with date-labeled folders.

## Prerequisites
- Python 3.9 or higher
- AWS CLI configured with credentials
- Access to the `news-collection-website` S3 bucket

## Setup Instructions

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Configure AWS Credentials
Make sure your AWS credentials are configured:
```bash
aws configure list
```

If not configured, run:
```bash
aws configure
```
Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (us-east-1)
- Default output format (json)

### 3. Verify S3 Access
Test that you can access the S3 bucket:
```bash
aws s3 ls s3://news-collection-website/ --region us-east-1
```

## Usage

### Running the Scraper
```bash
python3 news_2025_scraper.py
```

### What the Script Does
1. **Creates date-labeled folders**: Content is stored in `s3://news-collection-website/news/YYYY-MM-DD/`
2. **Processes RSS feeds**: Scrapes news from multiple RSS sources
3. **Direct website scraping**: Scrapes articles directly from news websites
4. **Idempotent operation**: Skips already processed content
5. **Progress tracking**: Saves progress to `news_2025_progress.json`

### Output Structure
```
s3://news-collection-website/news/2025-10-09/
├── rss/
│   ├── metadata/          # Article metadata (JSON files)
│   └── content/           # Full article content (HTML files)
└── direct/
    ├── metadata/          # Article metadata (JSON files)
    └── content/           # Full article content (HTML files)
```

### Monitoring Progress
- Check the console output for real-time progress
- Progress is saved to `news_2025_progress.json`
- The script can be safely interrupted and resumed

### Stopping and Resuming
- Press `Ctrl+C` to stop the script
- Run the script again to resume from where it left off
- Already processed feeds and sources are automatically skipped

## Configuration

### Keywords
The script searches for articles containing these keywords:
- Energy: renewable energy, solar power, wind energy, battery storage, smart grid, etc.
- AI: artificial intelligence, AI, machine learning, etc.
- Blockchain: blockchain, cryptocurrency, etc.
- Insurance: insurance, risk management, etc.

### News Sources
- **RSS Feeds**: BBC, CNN, Guardian, Al Jazeera, Financial Times, etc.
- **Direct Scraping**: Reuters, TechCrunch, Wired, CoinDesk, etc.

### Rate Limiting
- 0.5-2 second delays between requests
- Respects website rate limits
- Uses proper User-Agent headers

## Troubleshooting

### Common Issues

1. **AWS Credentials Error**
   ```
   NoCredentialsError: Unable to locate credentials
   ```
   Solution: Run `aws configure` to set up credentials

2. **S3 Access Denied**
   ```
   AccessDenied: Access Denied
   ```
   Solution: Verify you have write access to the `news-collection-website` bucket

3. **Network Timeouts**
   - The script includes retry logic and fallback strategies
   - Some feeds may be temporarily unavailable

4. **Memory Usage**
   - The script loads the S3 manifest into memory
   - For very large datasets, consider running on a machine with adequate RAM

### Logs
- All operations are logged to the console
- Log level is set to INFO by default
- Progress is saved to `news_2025_progress.json`

## Performance Notes

- **Idempotency**: The script tracks processed URLs and files to avoid duplicates
- **Efficiency**: Uses S3 manifest for fast existence checks
- **Resumability**: Can be stopped and restarted without losing progress
- **Scalability**: Processes feeds in sequence to avoid overwhelming sources

## Expected Runtime
- Full run typically takes 30-60 minutes depending on network speed
- RSS feeds are processed first (faster)
- Direct scraping takes longer due to individual article processing

## Safety Features
- Rate limiting to respect website policies
- Error handling and graceful degradation
- Progress persistence across runs
- No duplicate processing
- Archive.is fallback for blocked content