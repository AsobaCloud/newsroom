"""
Article Tagging Module for News Collection System

This module provides functions to tag articles with geographic and topical information
to help with newsletter curation and article organization.
"""

import re
from typing import List, Dict, Set

# Geographic mapping: cities, countries, regions -> continents
GEOGRAPHIC_MAPPING = {
    # Americas
    "united states": "Americas", "usa": "Americas", "us": "Americas",
    "new york": "Americas", "washington dc": "Americas", "washington d.c.": "Americas",
    "los angeles": "Americas", "san francisco": "Americas", "chicago": "Americas",
    "houston": "Americas", "toronto": "Americas", "mexico city": "Americas",
    "são paulo": "Americas", "sao paulo": "Americas", "buenos aires": "Americas",
    "calgary": "Americas", "austin": "Americas", "portland": "Americas",
    "panama city": "Americas", "san jose": "Americas", "palo alto": "Americas",
    "mountain view": "Americas", "seattle": "Americas", "boston": "Americas",
    "canada": "Americas", "mexico": "Americas", "brazil": "Americas",
    "argentina": "Americas", "chile": "Americas", "colombia": "Americas",
    "peru": "Americas", "venezuela": "Americas", "ecuador": "Americas",
    "bolivia": "Americas", "paraguay": "Americas", "uruguay": "Americas",
    "guyana": "Americas", "suriname": "Americas", "french guiana": "Americas",
    "cuba": "Americas", "jamaica": "Americas", "haiti": "Americas",
    "dominican republic": "Americas", "puerto rico": "Americas",
    "guatemala": "Americas", "honduras": "Americas", "el salvador": "Americas",
    "nicaragua": "Americas", "costa rica": "Americas", "panama": "Americas",
    
    # Europe
    "united kingdom": "Europe", "uk": "Europe", "britain": "Europe",
    "london": "Europe", "paris": "Europe", "berlin": "Europe", "brussels": "Europe",
    "amsterdam": "Europe", "madrid": "Europe", "rome": "Europe", "moscow": "Europe",
    "warsaw": "Europe", "istanbul": "Europe", "kyiv": "Europe", "kiev": "Europe",
    "gibraltar": "Europe", "copenhagen": "Europe", "munich": "Europe",
    "barcelona": "Europe", "aberdeen": "Europe", "stavanger": "Europe",
    "france": "Europe", "germany": "Europe", "italy": "Europe", "spain": "Europe",
    "poland": "Europe", "russia": "Europe", "ukraine": "Europe", "turkey": "Europe",
    "netherlands": "Europe", "belgium": "Europe", "denmark": "Europe",
    "sweden": "Europe", "norway": "Europe", "finland": "Europe",
    "switzerland": "Europe", "austria": "Europe", "czech republic": "Europe",
    "hungary": "Europe", "romania": "Europe", "bulgaria": "Europe",
    "greece": "Europe", "portugal": "Europe", "ireland": "Europe",
    "european union": "Europe", "eu": "Europe",
    
    # Asia
    "china": "Asia", "japan": "Asia", "india": "Asia", "south korea": "Asia",
    "singapore": "Asia", "thailand": "Asia", "indonesia": "Asia",
    "philippines": "Asia", "uae": "Asia", "israel": "Asia",
    "tokyo": "Asia", "beijing": "Asia", "shanghai": "Asia", "hong kong": "Asia",
    "seoul": "Asia", "mumbai": "Asia", "delhi": "Asia", "bangkok": "Asia",
    "jakarta": "Asia", "manila": "Asia", "dubai": "Asia", "tel aviv": "Asia",
    "bangalore": "Asia", "shenzhen": "Asia", "baku": "Asia", "doha": "Asia",
    "kuwait city": "Asia",     "gaza": "Asia", "gaza city": "Asia", "ramallah": "Asia",
    "jerusalem": "Asia", "damascus": "Asia", "beirut": "Asia",
    "palestine": "Asia", "west bank": "Asia", "hamas": "Asia",
    "south asia": "Asia", "southeast asia": "Asia", "middle east": "Asia",
    "asean": "Asia", "gulf states": "Asia", "persian gulf": "Asia",
    "south china sea": "Asia", "east asia": "Asia", "central asia": "Asia",
    
    # Africa
    "egypt": "Africa", "nigeria": "Africa", "south africa": "Africa",
    "kenya": "Africa", "morocco": "Africa", "ethiopia": "Africa",
    "cairo": "Africa", "lagos": "Africa", "johannesburg": "Africa",
    "nairobi": "Africa", "casablanca": "Africa", "addis ababa": "Africa",
    "north africa": "Africa", "sub-saharan africa": "Africa",
    "west africa": "Africa", "east africa": "Africa", "southern africa": "Africa",
    
    # Oceania
    "australia": "Oceania", "new zealand": "Oceania",
    "sydney": "Oceania", "melbourne": "Oceania", "auckland": "Oceania",
    "wellington": "Oceania", "pacific islands": "Oceania",
    
    # Global/Unclear
    "global": "Global", "worldwide": "Global", "international": "Global",
    "world": "Global", "earth": "Global", "planet": "Global",
    "suez": "Global", "suez canal": "Global",  # Strategic global location
}

# Core topic categories mapping
CORE_TOPICS = {
    "energy": [
        "energy", "electricity", "renewable energy", "solar power", "wind energy",
        "battery storage", "smart grid", "microgrid", "electric vehicles",
        "capacity market", "demand response", "carbon pricing", "carbon tax",
        "feed-in tariff", "grid reliability", "transmission planning",
        "levelized cost of energy", "power purchase agreement", "green bond",
        "esg investment", "coal", "rare earth minerals", "lithium", "nuclear",
        "gas", "oil", "supply chain"
    ],
    "ai": [
        "artificial intelligence", "ai", "machine learning", "ml", "neural network",
        "deep learning", "cybersecurity", "digital twin", "predictive analytics"
    ],
    "blockchain": [
        "blockchain", "cryptocurrency", "bitcoin", "ethereum", "crypto",
        "defi", "web3"
    ],
    "insurance": [
        "insurance", "catastrophe modeling", "exposure data", "reinsurance",
        "underwriting", "climate risk"
    ],
    "geopolitics": [
        "war", "civil unrest", "protest", "climate risk", "conflict",
        "diplomacy", "sanctions", "trade war", "military", "defense",
        "security", "terrorism", "refugees", "migration"
    ]
}

def detect_continents(article_content: str) -> List[str]:
    """
    Extract continent mentions from article content.
    
    Args:
        article_content: The full text content of the article
        
    Returns:
        List of continent tags (e.g., ["Asia", "Europe"] or ["Global"])
    """
    if not article_content:
        return ["Unclear"]
    
    content_lower = article_content.lower()
    continents = set()
    
    # Check for geographic mentions
    for location, continent in GEOGRAPHIC_MAPPING.items():
        if location in content_lower:
            continents.add(continent)
    
    # Handle special cases
    if len(continents) > 1:
        # Multiple continents mentioned - mark as Global
        return ["Global"]
    elif len(continents) == 1:
        return list(continents)
    else:
        # No clear geographic focus
        return ["Unclear"]

def get_matched_keywords(article_content: str, keywords_list: List[str]) -> List[str]:
    """
    Get list of specific keywords that matched the article content.
    
    Args:
        article_content: The full text content of the article
        keywords_list: List of keywords to check against
        
    Returns:
        List of matched keywords
    """
    if not article_content or not keywords_list:
        return []
    
    content_lower = article_content.lower()
    matched_keywords = []
    
    for keyword in keywords_list:
        keyword_lower = keyword.lower()
        # Use word boundary matching for better accuracy
        pattern = r'\b' + re.escape(keyword_lower) + r'\b'
        if re.search(pattern, content_lower):
            matched_keywords.append(keyword)
    
    return matched_keywords

def get_core_topic_categories(matched_keywords: List[str]) -> List[str]:
    """
    Map matched keywords to core topic categories.
    
    Args:
        matched_keywords: List of keywords that matched the article
        
    Returns:
        List of core topic categories
    """
    if not matched_keywords:
        return []
    
    categories = set()
    
    for keyword in matched_keywords:
        keyword_lower = keyword.lower()
        for category, keywords in CORE_TOPICS.items():
            if keyword_lower in [k.lower() for k in keywords]:
                categories.add(category)
    
    return list(categories)

def tag_article(article_content: str, keywords_list: List[str]) -> Dict[str, List[str]]:
    """
    Main function to tag an article with all relevant tags.
    
    Args:
        article_content: The full text content of the article
        keywords_list: List of keywords to check against
        
    Returns:
        Dictionary with tagging results:
        {
            'continents': List[str],
            'matched_keywords': List[str],
            'core_topics': List[str]
        }
    """
    matched_keywords = get_matched_keywords(article_content, keywords_list)
    
    return {
        'continents': detect_continents(article_content),
        'matched_keywords': matched_keywords,
        'core_topics': get_core_topic_categories(matched_keywords)
    }

def log_potential_cities(article_content: str) -> None:
    """
    Log potential cities/regions that might be missing from our mapping.
    This helps identify cities to add to the geographic mapping.
    
    Args:
        article_content: The full text content of the article
    """
    # This could be enhanced to actually log to a file or database
    # For now, it's a placeholder for future expansion
    pass