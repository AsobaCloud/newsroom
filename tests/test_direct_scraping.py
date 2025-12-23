#!/usr/bin/env python3
"""
Direct Scraping Testing Script
Tests all proposed direct scraping sources for reliability, content extraction, and geographic relevance.
Only sources that pass ALL tests will be recommended for production.
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import re
import os
from urllib.parse import urljoin, urlparse
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Keywords to check for relevance
RELEVANCE_KEYWORDS = [
    'energy', 'oil', 'gas', 'renewable', 'solar', 'wind', 'nuclear', 'coal',
    'artificial intelligence', 'ai', 'machine learning', 'blockchain', 'cryptocurrency',
    'bitcoin', 'ethereum', 'fintech', 'technology', 'innovation'
]

# Geographic keywords for target regions
AFRICA_KEYWORDS = ['africa', 'african', 'nigeria', 'south africa', 'kenya', 'egypt', 'morocco', 'ghana', 'ethiopia']
LATAM_KEYWORDS = ['latin america', 'brazil', 'mexico', 'argentina', 'chile', 'colombia', 'peru', 'venezuela', 'uruguay']
MENA_KEYWORDS = ['middle east', 'gulf', 'saudi', 'uae', 'qatar', 'kuwait', 'bahrain', 'oman', 'jordan', 'lebanon', 'israel', 'palestine']

class DirectScrapingTester:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def test_direct_source(self, name, url, region, language='English'):
        """Test a single direct scraping source comprehensively"""
        logger.info(f"Testing direct source: {name} ({region})")
        
        result = {
            'name': name,
            'url': url,
            'region': region,
            'language': language,
            'status': 'FAILED',
            'tests_passed': 0,
            'total_tests': 7,
            'errors': [],
            'article_links_found': 0,
            'content_extraction_success': 0,
            'relevant_articles': 0,
            'geographic_articles': 0,
            'response_time': 0,
            'anti_bot_detected': False
        }
        
        try:
            # Test 1: Accessibility
            start_time = time.time()
            response = self.session.get(url, timeout=15)
            result['response_time'] = time.time() - start_time
            
            if response.status_code != 200:
                result['errors'].append(f"HTTP {response.status_code}")
                return result
                
            # Test 2: Anti-bot detection
            if self.detect_anti_bot(response):
                result['anti_bot_detected'] = True
                result['errors'].append("Anti-bot measures detected")
                return result
                
            result['tests_passed'] += 2
            
            # Test 3: HTML parsing
            try:
                soup = BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                result['errors'].append(f"HTML parsing failed: {str(e)}")
                return result
                
            result['tests_passed'] += 1
            
            # Test 4: Article link discovery
            article_links = self.find_article_links(soup, url)
            result['article_links_found'] = len(article_links)
            
            if len(article_links) < 5:
                result['errors'].append(f"Too few article links found: {len(article_links)}")
                return result
                
            result['tests_passed'] += 1
            
            # Test 5: Content extraction
            extraction_success = 0
            for link in article_links[:10]:  # Test first 10 articles
                if self.test_content_extraction(link):
                    extraction_success += 1
                    
            result['content_extraction_success'] = extraction_success
            
            if extraction_success < 3:
                result['errors'].append(f"Content extraction failed for most articles: {extraction_success}/10")
                return result
                
            result['tests_passed'] += 1
            
            # Test 6: Relevance check
            relevant_count = 0
            for link in article_links[:15]:  # Check first 15 articles
                if self.is_relevant_article(link):
                    relevant_count += 1
                    
            result['relevant_articles'] = relevant_count
            
            if relevant_count == 0:
                result['errors'].append("No relevant articles found")
                return result
                
            result['tests_passed'] += 1
            
            # Test 7: Geographic relevance
            geographic_count = 0
            for link in article_links[:15]:
                if self.is_geographically_relevant(link, region):
                    geographic_count += 1
                    
            result['geographic_articles'] = geographic_count
            
            if geographic_count == 0:
                result['errors'].append(f"No {region} relevant articles found")
                return result
                
            result['tests_passed'] += 1
            
            # All tests passed
            result['status'] = 'PASSED'
            logger.info(f"✅ {name} - All tests passed")
            
        except requests.exceptions.RequestException as e:
            result['errors'].append(f"Request failed: {str(e)}")
        except Exception as e:
            result['errors'].append(f"Unexpected error: {str(e)}")
            
        return result
        
    def detect_anti_bot(self, response):
        """Detect if the site has anti-bot measures"""
        content = response.text.lower()
        
        # Common anti-bot indicators
        anti_bot_indicators = [
            'cloudflare', 'captcha', 'access denied', 'blocked', 'forbidden',
            'rate limit', 'too many requests', 'please wait', 'verifying',
            'security check', 'robot', 'bot detection'
        ]
        
        return any(indicator in content for indicator in anti_bot_indicators)
        
    def find_article_links(self, soup, base_url):
        """Find article links on the page"""
        article_links = []
        
        # Common selectors for article links
        selectors = [
            'a[href*="/article"]',
            'a[href*="/news"]',
            'a[href*="/story"]',
            'a[href*="/post"]',
            'a[href*="/entry"]',
            '.article a',
            '.news-item a',
            '.story a',
            '.post a',
            'h1 a', 'h2 a', 'h3 a',
            '.headline a',
            '.title a'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    if self.is_valid_article_url(full_url):
                        article_links.append(full_url)
                        
        # Remove duplicates and limit
        return list(set(article_links))[:20]
        
    def is_valid_article_url(self, url):
        """Check if URL looks like an article"""
        # Skip non-article URLs
        skip_patterns = [
            '/tag/', '/category/', '/author/', '/search/', '/page/',
            '/rss', '/feed', '/api/', '/static/', '/css/', '/js/',
            '/images/', '/img/', '/video/', '/audio/'
        ]
        
        if any(pattern in url.lower() for pattern in skip_patterns):
            return False
            
        # Must have some content indicators
        content_patterns = [
            '/article/', '/news/', '/story/', '/post/', '/entry/',
            '/2024/', '/2025/', '/january/', '/february/', '/march/',
            '/april/', '/may/', '/june/', '/july/', '/august/',
            '/september/', '/october/', '/november/', '/december/'
        ]
        
        return any(pattern in url.lower() for pattern in content_patterns)
        
    def test_content_extraction(self, article_url):
        """Test if we can extract content from an article"""
        try:
            response = self.session.get(article_url, timeout=10)
            if response.status_code != 200:
                return False
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find article content
            content_selectors = [
                'article', '.article-content', '.post-content', '.entry-content',
                '.story-content', '.news-content', '.content', 'main'
            ]
            
            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    break
                    
            # If no specific content area found, try to get all text
            if not content:
                content = soup.get_text(strip=True)
                
            # Check if we got meaningful content
            return len(content) > 200 and not self.detect_anti_bot(response)
            
        except:
            return False
            
    def is_relevant_article(self, article_url):
        """Check if article is relevant to our keywords"""
        try:
            response = self.session.get(article_url, timeout=10)
            if response.status_code != 200:
                return False
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get title and content
            title = ""
            if soup.title:
                title = soup.title.get_text().lower()
                
            content = ""
            content_selectors = [
                'article', '.article-content', '.post-content', '.entry-content',
                '.story-content', '.news-content', '.content', 'main'
            ]
            
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text().lower()
                    break
                    
            if not content:
                content = soup.get_text().lower()
                
            text = title + " " + content
            return any(keyword in text for keyword in RELEVANCE_KEYWORDS)
            
        except:
            return False
            
    def is_geographically_relevant(self, article_url, region):
        """Check if article is geographically relevant"""
        try:
            response = self.session.get(article_url, timeout=10)
            if response.status_code != 200:
                return False
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get title and content
            title = ""
            if soup.title:
                title = soup.title.get_text().lower()
                
            content = ""
            content_selectors = [
                'article', '.article-content', '.post-content', '.entry-content',
                '.story-content', '.news-content', '.content', 'main'
            ]
            
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text().lower()
                    break
                    
            if not content:
                content = soup.get_text().lower()
                
            text = title + " " + content
            
            if region == 'Africa':
                return any(keyword in text for keyword in AFRICA_KEYWORDS)
            elif region == 'Latin America':
                return any(keyword in text for keyword in LATAM_KEYWORDS)
            elif region == 'MENA':
                return any(keyword in text for keyword in MENA_KEYWORDS)
            return True  # For general sources
            
        except:
            return False
            
    def test_all_sources(self):
        """Test all proposed direct scraping sources"""
        sources_to_test = [
            # Africa
            ("AllAfrica Energy", "https://allafrica.com/energy/", "Africa"),
            ("African Business Central", "https://africanbusinesscentral.com/", "Africa"),
            ("Energy Central Africa", "https://www.energycentral.com/africa/", "Africa"),
            
            # Latin America
            ("Valor Econômico Energia", "https://www.valor.com.br/energia", "Latin America"),
            ("La Nación Energía", "https://www.lanacion.com.ar/energia", "Latin America"),
            ("El País Economía", "https://brasil.elpais.com/economia/", "Latin America"),
            
            # MENA
            ("Al Arabiya Business", "https://english.alarabiya.net/business", "MENA"),
            ("Gulf News Business", "https://gulfnews.com/business", "MENA"),
            ("Arab News Business", "https://www.arabnews.com/business", "MENA"),
        ]
        
        logger.info(f"Testing {len(sources_to_test)} direct scraping sources...")
        
        for name, url, region in sources_to_test:
            result = self.test_direct_source(name, url, region)
            self.results.append(result)
            
            # Add delay to be respectful
            time.sleep(2)
            
        return self.results
        
    def generate_report(self):
        """Generate comprehensive test report"""
        passed = [r for r in self.results if r['status'] == 'PASSED']
        failed = [r for r in self.results if r['status'] == 'FAILED']
        
        report = {
            'summary': {
                'total_tested': len(self.results),
                'passed': len(passed),
                'failed': len(failed),
                'success_rate': len(passed) / len(self.results) * 100 if self.results else 0
            },
            'passed_sources': passed,
            'failed_sources': failed,
            'recommendations': self.get_recommendations()
        }
        
        return report
        
    def get_recommendations(self):
        """Get recommendations for production deployment"""
        passed = [r for r in self.results if r['status'] == 'PASSED']
        
        recommendations = {
            'deploy_immediately': [],
            'deploy_with_monitoring': [],
            'do_not_deploy': []
        }
        
        for result in passed:
            if (result['tests_passed'] == 7 and 
                result['response_time'] < 5 and 
                result['content_extraction_success'] >= 7):
                recommendations['deploy_immediately'].append(result['name'])
            elif (result['tests_passed'] >= 6 and 
                  result['response_time'] < 8 and 
                  result['content_extraction_success'] >= 5):
                recommendations['deploy_with_monitoring'].append(result['name'])
            else:
                recommendations['do_not_deploy'].append(result['name'])
                
        return recommendations

def main():
    """Main testing function"""
    tester = DirectScrapingTester()
    
    print("🔍 Starting Direct Scraping Testing...")
    print("=" * 50)
    
    results = tester.test_all_sources()
    report = tester.generate_report()
    
    # Save detailed results
    os.makedirs('results', exist_ok=True)
    with open('results/direct_scraping_test_results.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    print(f"\n📊 TEST RESULTS SUMMARY")
    print(f"Total Tested: {report['summary']['total_tested']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
    
    print(f"\n✅ SOURCES READY FOR PRODUCTION:")
    for source in report['recommendations']['deploy_immediately']:
        print(f"  - {source}")
        
    print(f"\n⚠️  SOURCES NEED MONITORING:")
    for source in report['recommendations']['deploy_with_monitoring']:
        print(f"  - {source}")
        
    print(f"\n❌ SOURCES NOT RECOMMENDED:")
    for source in report['recommendations']['do_not_deploy']:
        print(f"  - {source}")
    
    print(f"\n📄 Detailed results saved to: results/direct_scraping_test_results.json")
    
    return report

if __name__ == "__main__":
    main()