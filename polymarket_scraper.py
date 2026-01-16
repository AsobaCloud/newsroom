#!/usr/bin/env python3
"""
Polymarket Scraper - Collects political prediction markets

Fetches prediction markets from Polymarket's Gamma API,
filters for political/relevant content, and stores with
country-level tagging for downstream filtering.
"""

import os
import re
import json
import logging
import requests
import hashlib
from datetime import datetime
from typing import Dict, List, Optional

from news_storage import save_article, get_today_folder, S3_BUCKET_NAME
from article_tagger import detect_continents

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("polymarket_scraper")

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------

POLYMARKET_API_URL = "https://gamma-api.polymarket.com/markets"
POLYMARKET_WEB_BASE = "https://polymarket.com/event"

# Political/geopolitical keywords for filtering markets
POLITICAL_KEYWORDS = [
    # Elections & Government
    "election", "president", "presidential", "congress", "senate",
    "governor", "parliament", "prime minister", "vote", "voter",
    "republican", "democrat", "conservative", "liberal",

    # US Politics figures
    "trump", "biden", "desantis", "harris", "pence", "newsom",

    # Geopolitics
    "war", "conflict", "invasion", "military", "nato", "sanctions",
    "tariff", "trade war", "treaty", "diplomacy", "nuclear",

    # Policy
    "legislation", "bill", "law", "policy", "regulation",
    "impeachment", "supreme court", "federal reserve", "fed rate",

    # International
    "putin", "zelensky", "xi jinping", "netanyahu", "eu ", "european union"
]

# Country detection patterns (full names)
COUNTRY_PATTERNS = {
    "United States": [
        r"\bUS\b", r"\bUSA\b", r"\bU\.S\.", r"United States",
        r"\bAmerica\b", r"\bAmerican\b", r"Washington D\.?C\.?"
    ],
    "United Kingdom": [
        r"\bUK\b", r"\bU\.K\.", r"United Kingdom", r"\bBritain\b",
        r"\bBritish\b", r"\bEngland\b", r"\bScotland\b", r"\bWales\b"
    ],
    "China": [
        r"\bChina\b", r"\bChinese\b", r"\bBeijing\b", r"\bXi Jinping\b"
    ],
    "Russia": [
        r"\bRussia\b", r"\bRussian\b", r"\bMoscow\b", r"\bPutin\b", r"\bKremlin\b"
    ],
    "Ukraine": [
        r"\bUkraine\b", r"\bUkrainian\b", r"\bKyiv\b", r"\bZelensky\b"
    ],
    "Israel": [
        r"\bIsrael\b", r"\bIsraeli\b", r"\bNetanyahu\b", r"\bTel Aviv\b", r"\bIDF\b"
    ],
    "Palestine": [
        r"\bPalestine\b", r"\bPalestinian\b", r"\bGaza\b", r"\bWest Bank\b", r"\bHamas\b"
    ],
    "Iran": [
        r"\bIran\b", r"\bIranian\b", r"\bTehran\b", r"\bKhamenei\b"
    ],
    "North Korea": [
        r"\bNorth Korea\b", r"\bNKorea\b", r"\bPyongyang\b", r"\bKim Jong"
    ],
    "South Korea": [
        r"\bSouth Korea\b", r"\bSKorea\b", r"\bSeoul\b"
    ],
    "Taiwan": [
        r"\bTaiwan\b", r"\bTaiwanese\b", r"\bTaipei\b"
    ],
    "Japan": [
        r"\bJapan\b", r"\bJapanese\b", r"\bTokyo\b"
    ],
    "Germany": [
        r"\bGermany\b", r"\bGerman\b", r"\bBerlin\b", r"\bScholz\b"
    ],
    "France": [
        r"\bFrance\b", r"\bFrench\b", r"\bParis\b", r"\bMacron\b"
    ],
    "Italy": [
        r"\bItaly\b", r"\bItalian\b", r"\bRome\b", r"\bMeloni\b"
    ],
    "Spain": [
        r"\bSpain\b", r"\bSpanish\b", r"\bMadrid\b"
    ],
    "Poland": [
        r"\bPoland\b", r"\bPolish\b", r"\bWarsaw\b"
    ],
    "Brazil": [
        r"\bBrazil\b", r"\bBrazilian\b", r"\bBrasilia\b", r"\bLula\b", r"\bBolsonaro\b"
    ],
    "Mexico": [
        r"\bMexico\b", r"\bMexican\b", r"\bMexico City\b"
    ],
    "Canada": [
        r"\bCanada\b", r"\bCanadian\b", r"\bOttawa\b", r"\bTrudeau\b"
    ],
    "Argentina": [
        r"\bArgentina\b", r"\bArgentine\b", r"\bBuenos Aires\b", r"\bMilei\b"
    ],
    "Australia": [
        r"\bAustralia\b", r"\bAustralian\b", r"\bCanberra\b", r"\bSydney\b"
    ],
    "India": [
        r"\bIndia\b", r"\bIndian\b", r"\bNew Delhi\b", r"\bModi\b"
    ],
    "Pakistan": [
        r"\bPakistan\b", r"\bPakistani\b", r"\bIslamabad\b"
    ],
    "Saudi Arabia": [
        r"\bSaudi Arabia\b", r"\bSaudi\b", r"\bRiyadh\b", r"\bMBS\b"
    ],
    "Turkey": [
        r"\bTurkey\b", r"\bTurkish\b", r"\bAnkara\b", r"\bErdogan\b"
    ],
    "Egypt": [
        r"\bEgypt\b", r"\bEgyptian\b", r"\bCairo\b"
    ],
    "South Africa": [
        r"\bSouth Africa\b", r"\bSouth African\b", r"\bPretoria\b", r"\bJohannesburg\b"
    ],
    "Nigeria": [
        r"\bNigeria\b", r"\bNigerian\b", r"\bAbuja\b", r"\bLagos\b"
    ],
    "Venezuela": [
        r"\bVenezuela\b", r"\bVenezuelan\b", r"\bCaracas\b", r"\bMaduro\b"
    ],
    "Syria": [
        r"\bSyria\b", r"\bSyrian\b", r"\bDamascus\b", r"\bAssad\b"
    ],
    "Afghanistan": [
        r"\bAfghanistan\b", r"\bAfghan\b", r"\bKabul\b", r"\bTaliban\b"
    ],
    "Iraq": [
        r"\bIraq\b", r"\bIraqi\b", r"\bBaghdad\b"
    ],
    "Lebanon": [
        r"\bLebanon\b", r"\bLebanese\b", r"\bBeirut\b", r"\bHezbollah\b"
    ],
    "Yemen": [
        r"\bYemen\b", r"\bYemeni\b", r"\bHouthi\b"
    ],
    "European Union": [
        r"\bEuropean Union\b", r"\bEU\b", r"\bBrussels\b"
    ]
}

# -------------------------------------------------------------------------
# COUNTRY DETECTION
# -------------------------------------------------------------------------

def detect_countries(text: str) -> List[str]:
    """
    Extract country mentions from text.
    Returns list of full country names.
    """
    if not text:
        return []

    countries = []
    for country, patterns in COUNTRY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                if country not in countries:
                    countries.append(country)
                break  # Found this country, move to next

    return sorted(countries)

# -------------------------------------------------------------------------
# MARKET FILTERING
# -------------------------------------------------------------------------

def is_political_market(market: Dict) -> bool:
    """Check if market is political/geopolitically relevant"""

    # Check category
    category = (market.get("category") or "").lower()
    if any(kw in category for kw in ["politics", "election", "government", "current-affairs"]):
        return True

    # Check question and description
    question = (market.get("question") or "").lower()
    description = (market.get("description") or "").lower()
    combined = question + " " + description

    for keyword in POLITICAL_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', combined):
            return True

    return False

# -------------------------------------------------------------------------
# API FETCHING
# -------------------------------------------------------------------------

def fetch_markets(limit: int = 100, offset: int = 0, closed: bool = False) -> List[Dict]:
    """Fetch markets from Polymarket API"""
    try:
        params = {
            "limit": limit,
            "offset": offset,
            "closed": str(closed).lower(),
            "order": "volume",
            "ascending": "false"
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; NewsCollector/1.0)"
        }

        response = requests.get(
            POLYMARKET_API_URL,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error fetching Polymarket API: {e}")
        return []

def fetch_all_political_markets(max_markets: int = 500) -> List[Dict]:
    """Fetch all open political markets with pagination"""
    all_markets = []
    offset = 0
    limit = 100

    while offset < max_markets:
        markets = fetch_markets(limit=limit, offset=offset, closed=False)

        if not markets:
            break

        # Filter for political markets
        political = [m for m in markets if is_political_market(m)]
        all_markets.extend(political)

        logger.info(f"Fetched {len(markets)} markets, {len(political)} political (offset {offset})")

        if len(markets) < limit:
            break  # No more results

        offset += limit

    return all_markets

# -------------------------------------------------------------------------
# MARKET TO ARTICLE CONVERSION
# -------------------------------------------------------------------------

def market_to_article_content(market: Dict) -> str:
    """Convert market data to HTML content for storage"""

    question = market.get("question", "Unknown Market")
    description = market.get("description", "")
    outcomes = market.get("outcomes", [])
    prices = market.get("outcomePrices", [])
    volume = float(market.get("volume", 0) or 0)
    liquidity = float(market.get("liquidity", 0) or 0)

    # Format prices as percentages
    price_display = []
    for i, outcome in enumerate(outcomes):
        if i < len(prices):
            try:
                pct = float(prices[i]) * 100
                price_display.append(f"{outcome}: {pct:.1f}%")
            except:
                price_display.append(f"{outcome}: N/A")

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{question}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }}
        .market-stats {{ background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .market-stats table {{ width: 100%; border-collapse: collapse; }}
        .market-stats td {{ padding: 8px 0; }}
        .market-stats td:first-child {{ font-weight: 600; width: 120px; }}
        .market-prices {{ margin: 20px 0; }}
        .market-prices ul {{ list-style: none; padding: 0; }}
        .market-prices li {{ padding: 8px 12px; background: #e3f2fd; margin: 4px 0; border-radius: 4px; }}
        .market-description {{ line-height: 1.6; color: #333; }}
        .market-metadata {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
        .market-metadata pre {{ background: #f8f8f8; padding: 15px; overflow-x: auto; font-size: 12px; border-radius: 4px; }}
    </style>
</head>
<body>
    <h1>{question}</h1>

    <div class="market-stats">
        <table>
            <tr><td>Volume:</td><td>${volume:,.0f}</td></tr>
            <tr><td>Liquidity:</td><td>${liquidity:,.0f}</td></tr>
            <tr><td>Status:</td><td>{"Closed" if market.get("closed") else "Open"}</td></tr>
            <tr><td>Category:</td><td>{market.get("category", "N/A")}</td></tr>
        </table>
    </div>

    <div class="market-prices">
        <h3>Current Prices</h3>
        <ul>
            {"".join(f"<li>{p}</li>" for p in price_display)}
        </ul>
    </div>

    <div class="market-description">
        <h3>Resolution Criteria</h3>
        <p>{description}</p>
    </div>

    <div class="market-metadata">
        <h3>Raw Data</h3>
        <pre>{json.dumps(market, indent=2, default=str)}</pre>
    </div>
</body>
</html>"""
    return html

# -------------------------------------------------------------------------
# MAIN PROCESSING
# -------------------------------------------------------------------------

def process_polymarket_feeds() -> int:
    """
    Fetch political prediction markets from Polymarket API.
    Returns number of markets saved.
    """
    logger.info("=== POLYMARKET SCRAPER: Starting ===")

    # Fetch all political markets
    markets = fetch_all_political_markets(max_markets=500)
    logger.info(f"Found {len(markets)} political markets")

    saved_count = 0

    for market in markets:
        try:
            market_id = market.get("id", "")
            question = market.get("question", "Unknown Market")
            slug = market.get("slug", market_id)
            description = market.get("description", "")
            start_date = market.get("startDate") or market.get("createdAt") or ""

            # Build URL
            url = f"{POLYMARKET_WEB_BASE}/{slug}"

            # Detect countries from question + description
            combined_text = f"{question} {description}"
            countries = detect_countries(combined_text)
            continents = detect_continents(combined_text)

            # Build tags
            tags = {
                "continents": continents,
                "countries": countries,
                "core_topics": ["geopolitics"],
                "matched_keywords": [],
                "special_tags": ["prediction_market"],
                "market_data": {
                    "volume": market.get("volume"),
                    "liquidity": market.get("liquidity"),
                    "outcomes": market.get("outcomes"),
                    "prices": market.get("outcomePrices"),
                    "closed": market.get("closed", False)
                }
            }

            # Convert to HTML content
            full_content = market_to_article_content(market)

            # Save using shared storage
            article_id = save_article(
                title=question,
                url=url,
                pub_date=start_date,
                description=description[:500] if description else "",
                full_content=full_content,
                feed_url=POLYMARKET_API_URL,
                tags=tags,
                source_type="Polymarket"
            )

            if article_id:
                saved_count += 1
                logger.info(f"Saved market: {question[:50]}... | Countries: {countries}")

        except Exception as e:
            logger.error(f"Error processing market {market.get('id')}: {e}")
            continue

    logger.info(f"=== POLYMARKET SCRAPER: Complete ({saved_count} markets saved) ===")
    logger.info(f"Articles saved to s3://{S3_BUCKET_NAME}/{get_today_folder()}/")
    return saved_count

# -------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------

if __name__ == "__main__":
    process_polymarket_feeds()
