# News Scraper Fixes & Improvements

## Overview
This document outlines the fixes and improvements needed for the news scraper based on analysis of the latest run output (121 articles collected in 6.2 minutes).

## Current Issues Identified

### 1. Failed RSS Feeds (4 sources)
- **Yahoo Finance**: 400 Bad Request error
- **Energy.gov**: 404 Not Found error  
- **Whitehouse.gov**: 404 Not Found error
- **MarketWatch**: Content extraction failed (0 articles)

### 2. Content Extraction Failures
- **CNN video content**: "Could not extract content from video URLs"
- **VentureBeat**: All 20 articles failed extraction (0 articles)
- **Reuters**: 401 Forbidden errors on direct scraping
- **ArsTechnica**: 0 articles extracted despite finding 36 potential articles

### 3. Data Quality Issues
- Generic article titles: "Tech Life...", "Tech Now..."
- Incomplete content extraction
- XML parsing warnings for arXiv feeds
- Some articles may be duplicates or low-quality

### 4. Performance Concerns
- Sequential processing limits throughput
- No connection pooling
- Fixed rate limiting regardless of site response
- 6.2 minutes for 121 articles could be optimized

## Phase 1 Fixes (Critical - Week 1)

### 1.1 Fix Broken RSS Feeds

#### Problem
Multiple RSS feeds are returning errors or no content:
- Yahoo Finance: 400 Bad Request
- Energy.gov: 404 Not Found
- Whitehouse.gov: 404 Not Found
- MarketWatch: Content extraction fails

#### Solution
- **Remove broken feeds** from the active list
- **Add feed validation** before processing
- **Implement proper error handling** for HTTP errors
- **Add fallback feeds** for missing sources

#### Implementation
```python
# Add feed validation function
def validate_feed(feed_url: str) -> bool:
    """Validate RSS feed before processing"""
    try:
        response = requests.head(feed_url, timeout=10)
        return response.status_code == 200
    except:
        return False

# Update feed list to remove broken ones
WORKING_RSS_FEEDS = [
    # Keep working feeds
    'https://feeds.bbci.co.uk/news/rss.xml',
    'https://feeds.bbci.co.uk/news/world/rss.xml',
    # ... other working feeds
]

# Add new working feeds
NEW_RSS_FEEDS = [
    'https://feeds.reuters.com/reuters/technologyNews',
    'https://feeds.reuters.com/reuters/businessNews',
    'https://rss.cnn.com/rss/edition_technology.rss',
    'https://feeds.feedburner.com/oreilly/radar',
]
```

### 1.2 Improve Content Extraction Success Rate

#### Problem
Many articles fail content extraction:
- CNN video content not handled
- VentureBeat completely fails
- ArsTechnica finds articles but extracts 0

#### Solution
- **Add site-specific extractors** for problematic sites
- **Improve content selectors** for better extraction
- **Add video content handling** for CNN
- **Implement better fallback strategies**

#### Implementation
```python
# Site-specific content extractors
def extract_cnn_content(soup: BeautifulSoup) -> str:
    """CNN-specific content extraction"""
    # Handle video content
    video_content = soup.find('div', class_='video-content')
    if video_content:
        return video_content.get_text(strip=True)
    
    # Standard article content
    content_selectors = [
        '.article__content',
        '.l-container .zn-body__paragraph',
        '.article-content'
    ]
    # ... implementation

def extract_venturebeat_content(soup: BeautifulSoup) -> str:
    """VentureBeat-specific content extraction"""
    content_selectors = [
        '.article-content',
        '.entry-content',
        '.post-content'
    ]
    # ... implementation

def extract_arstechnica_content(soup: BeautifulSoup) -> str:
    """ArsTechnica-specific content extraction"""
    content_selectors = [
        '.article-content',
        '.entry-content',
        'article .post-content'
    ]
    # ... implementation
```

### 1.3 Add Proper HTTP Error Handling

#### Problem
HTTP errors are not handled gracefully:
- 401 Forbidden errors crash processing
- 404 errors not handled properly
- No retry logic for temporary failures

#### Solution
- **Implement proper HTTP status code handling**
- **Add retry logic with exponential backoff**
- **Handle authentication errors gracefully**
- **Add circuit breaker for failing sources**

#### Implementation
```python
import time
from functools import wraps

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
                        raise
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

def handle_http_errors(response: requests.Response) -> bool:
    """Handle HTTP errors gracefully"""
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
    return True
```

### 1.4 Improve Error Logging and Debugging

#### Problem
Limited visibility into why extractions fail:
- Generic error messages
- No detailed logging of extraction attempts
- Hard to debug content extraction issues

#### Solution
- **Add detailed logging for each extraction step**
- **Log specific selectors being tried**
- **Add debug mode for troubleshooting**
- **Create extraction success metrics**

#### Implementation
```python
import logging

# Add debug logging
def extract_content_with_logging(url: str, soup: BeautifulSoup) -> Optional[str]:
    """Extract content with detailed logging"""
    logger.debug(f"Extracting content from: {url}")
    
    # Try site-specific extractors first
    site_extractors = {
        'cnn.com': extract_cnn_content,
        'venturebeat.com': extract_venturebeat_content,
        'arstechnica.com': extract_arstechnica_content
    }
    
    domain = urlparse(url).netloc
    if domain in site_extractors:
        logger.debug(f"Using site-specific extractor for {domain}")
        content = site_extractors[domain](soup)
        if content:
            logger.debug(f"Site-specific extraction successful: {len(content)} chars")
            return content
    
    # Fallback to generic extraction
    logger.debug("Using generic content extraction")
    # ... existing logic with more logging
```

## Phase 2 Fixes (High Priority - Week 2)

### 2.1 Implement Parallel Processing
- Use ThreadPoolExecutor for RSS feeds
- Parallel content extraction
- Batch S3 operations

### 2.2 Add Feed Health Monitoring
- Validate feeds before processing
- Track feed success rates
- Automatic broken feed detection

### 2.3 Improve Data Quality
- Better title extraction and cleaning
- Content-based deduplication
- Quality scoring for articles

## Phase 3 Fixes (Medium Priority - Week 3)

### 3.1 Add Comprehensive Monitoring
- Structured logging
- Performance metrics
- Health check endpoints

### 3.2 Implement Configuration Management
- YAML configuration files
- Environment-based settings
- Feed configuration management

### 3.3 Performance Optimizations
- Connection pooling
- Intelligent rate limiting
- S3 batch operations

## Phase 4 Fixes (Enhancement - Week 4)

### 4.1 Add Comprehensive Testing
- Unit tests for all components
- Integration tests
- Performance benchmarks

### 4.2 Implement Plugin Architecture
- Site-specific extractor plugins
- Configurable content selectors
- Extensible feed sources

### 4.3 Advanced Features
- Content quality scoring
- Automatic feed discovery
- Real-time monitoring dashboard

## Expected Outcomes

### Phase 1 (Critical)
- **Reliability**: 90%+ success rate for content extraction
- **Error Handling**: Graceful handling of all HTTP errors
- **Data Quality**: Elimination of extraction failures
- **Debugging**: Clear visibility into extraction process

### Overall (All Phases)
- **Reliability**: 95%+ success rate for content extraction
- **Performance**: 50% reduction in total runtime
- **Data Quality**: Elimination of generic titles and duplicates
- **Maintainability**: Easy configuration and monitoring
- **Scalability**: Support for 100+ news sources

## Implementation Notes

1. **Backward Compatibility**: All changes maintain existing functionality
2. **Configuration**: New features are configurable and optional
3. **Testing**: Each phase includes comprehensive testing
4. **Documentation**: All changes are documented and commented
5. **Monitoring**: Progress and success rates are tracked throughout

## Files to Modify

### Primary Files
- `news_scraper_final.py` - Main scraper logic
- `requirements.txt` - Dependencies
- `NEWS_SOURCES` - Feed configuration

### New Files
- `extractors/` - Site-specific content extractors
- `config/` - Configuration files
- `tests/` - Test suite
- `logs/` - Log files

## Risk Assessment

### Low Risk
- Error handling improvements
- Logging enhancements
- Feed validation

### Medium Risk
- Content extraction changes
- Parallel processing
- S3 operations

### High Risk
- Major architectural changes
- Plugin system
- Performance optimizations

## Success Metrics

### Phase 1 Success Criteria
- [ ] All broken RSS feeds identified and handled
- [ ] Content extraction success rate > 90%
- [ ] No HTTP errors crash the system
- [ ] Detailed logging for debugging
- [ ] All existing functionality preserved

### Overall Success Criteria
- [ ] 95%+ content extraction success rate
- [ ] 50% performance improvement
- [ ] Zero data quality issues
- [ ] Comprehensive test coverage
- [ ] Easy maintenance and configuration