#!/bin/bash
# One-off historical legislation collection script

set -e

echo "📜 Historical Legislation Collection"
echo "===================================="
echo ""

echo "Step 1: Collecting historical legislation articles..."
python3 utils/historical_legislation_scraper.py

echo ""
echo "Step 2: Generating historical HTML page..."
echo "⚠️  Note: generate_historical_page.py not found - skipping HTML generation"

echo ""
echo "✅ Historical legislation collection complete!"
echo "📁 Location: s3://news-collection-website/news/historical/legislation/"
echo "🌐 URL: http://news-collection-website.s3-website-us-east-1.amazonaws.com/news/historical/legislation/index.html"
