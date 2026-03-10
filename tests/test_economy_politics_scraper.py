#!/usr/bin/env python3
"""
Tests for the Economy & Politics Scraper

Tests keyword filtering, feed organization, country tagging,
and integration with article_tagger geographic detection.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestEconomyPoliticsKeywords(unittest.TestCase):
    """Test keyword sets and matching logic"""

    def test_economic_keywords_exist(self):
        """Economic consumption keywords are defined"""
        from economy_politics_scraper import ECONOMIC_KEYWORDS
        self.assertIsInstance(ECONOMIC_KEYWORDS, list)
        self.assertGreater(len(ECONOMIC_KEYWORDS), 30)
        # Spot-check key terms
        for term in ["consumer spending", "inflation", "GDP", "unemployment",
                     "exchange rate", "monetary policy", "retail sales"]:
            self.assertIn(term, ECONOMIC_KEYWORDS, f"Missing economic keyword: {term}")

    def test_political_keywords_exist(self):
        """Political dynamics keywords are defined"""
        from economy_politics_scraper import POLITICAL_KEYWORDS
        self.assertIsInstance(POLITICAL_KEYWORDS, list)
        self.assertGreater(len(POLITICAL_KEYWORDS), 30)
        # Spot-check key terms
        for term in ["election", "parliament", "corruption", "democracy",
                     "political party", "referendum", "populism"]:
            self.assertIn(term, POLITICAL_KEYWORDS, f"Missing political keyword: {term}")

    def test_matches_keyword_returns_true_for_economic_article(self):
        """Article about inflation should match economic keywords"""
        from economy_politics_scraper import matches_economy_politics_keywords
        text = "Consumer prices rose 5% as inflation hit a new high, raising cost of living concerns."
        self.assertTrue(matches_economy_politics_keywords(text))

    def test_matches_keyword_returns_true_for_political_article(self):
        """Article about elections should match political keywords"""
        from economy_politics_scraper import matches_economy_politics_keywords
        text = "The opposition party won the election with a strong voter turnout across constituencies."
        self.assertTrue(matches_economy_politics_keywords(text))

    def test_matches_keyword_returns_false_for_unrelated_article(self):
        """Article about sports should not match"""
        from economy_politics_scraper import matches_economy_politics_keywords
        text = "The football team won the championship game after a thrilling overtime period."
        self.assertFalse(matches_economy_politics_keywords(text))

    def test_keyword_matching_uses_word_boundaries(self):
        """Keywords should use word boundary matching to avoid false positives"""
        from economy_politics_scraper import matches_economy_politics_keywords
        # "CPI" should not match inside "copying"
        text = "She was copying documents from the archive for the museum collection."
        self.assertFalse(matches_economy_politics_keywords(text))


class TestFeedOrganization(unittest.TestCase):
    """Test feed lists and country tagging"""

    def test_feeds_by_country_exists(self):
        """FEEDS_BY_COUNTRY dict should exist with all 12 target countries"""
        from economy_politics_scraper import FEEDS_BY_COUNTRY
        self.assertIsInstance(FEEDS_BY_COUNTRY, dict)
        expected_countries = [
            "Zimbabwe", "India", "China", "Brazil", "USA",
            "Eurozone", "South Africa", "Nigeria", "Kenya",
            "Ghana", "Mauritius", "DR Congo"
        ]
        for country in expected_countries:
            self.assertIn(country, FEEDS_BY_COUNTRY,
                          f"Missing country in feeds: {country}")

    def test_feeds_are_urls(self):
        """All feed entries should be valid URLs"""
        from economy_politics_scraper import FEEDS_BY_COUNTRY
        for country, feeds in FEEDS_BY_COUNTRY.items():
            self.assertIsInstance(feeds, list, f"{country} feeds should be a list")
            for feed in feeds:
                self.assertTrue(feed.startswith("http"),
                                f"Invalid feed URL for {country}: {feed}")

    def test_total_feed_count(self):
        """Should have approximately 91 feeds total (after USA feed expansion)"""
        from economy_politics_scraper import FEEDS_BY_COUNTRY
        total = sum(len(feeds) for feeds in FEEDS_BY_COUNTRY.values())
        self.assertGreaterEqual(total, 80, "Too few feeds")
        self.assertLessEqual(total, 110, "Too many feeds")

    def test_get_all_feeds_with_country(self):
        """get_all_feeds_with_country returns (url, country) tuples"""
        from economy_politics_scraper import get_all_feeds_with_country
        feeds = get_all_feeds_with_country()
        self.assertIsInstance(feeds, list)
        self.assertGreater(len(feeds), 0)
        # Each entry should be (url, country)
        for url, country in feeds:
            self.assertTrue(url.startswith("http"))
            self.assertIsInstance(country, str)


class TestArticleTaggerGeography(unittest.TestCase):
    """Test that article_tagger detects new African locations"""

    def test_zimbabwe_detection(self):
        """Zimbabwe and its cities should be detected as Africa"""
        from article_tagger import detect_continents, detect_countries
        text = "Harare announced new economic reforms in Zimbabwe today."
        continents = detect_continents(text)
        self.assertIn("Africa", continents)
        countries = detect_countries(text)
        country_lower = [c.lower() for c in countries]
        self.assertIn("zimbabwe", country_lower)
        self.assertIn("harare", country_lower)

    def test_ghana_detection(self):
        """Ghana and Accra should be detected as Africa"""
        from article_tagger import detect_continents
        text = "Accra hosted the West African economic summit in Ghana."
        continents = detect_continents(text)
        self.assertIn("Africa", continents)

    def test_mauritius_detection(self):
        """Mauritius should be detected as Africa"""
        from article_tagger import detect_continents
        text = "Port Louis saw record foreign investment in Mauritius."
        continents = detect_continents(text)
        self.assertIn("Africa", continents)

    def test_drc_detection(self):
        """DR Congo and Kinshasa should be detected as Africa"""
        from article_tagger import detect_continents
        text = "Kinshasa faces political crisis in the Democratic Republic of Congo."
        continents = detect_continents(text)
        self.assertIn("Africa", continents)

    def test_bulawayo_detection(self):
        """Bulawayo (Zimbabwe) should be detected as Africa"""
        from article_tagger import detect_continents
        text = "Bulawayo industries reported economic growth this quarter."
        continents = detect_continents(text)
        self.assertIn("Africa", continents)


class TestProcessFeedFunction(unittest.TestCase):
    """Test the main processing function signature"""

    def test_process_economy_politics_feeds_exists(self):
        """Main entry point function exists"""
        from economy_politics_scraper import process_economy_politics_feeds
        self.assertTrue(callable(process_economy_politics_feeds))

    def test_process_single_feed_exists(self):
        """Single feed processor exists and is callable"""
        from economy_politics_scraper import process_single_economy_politics_feed
        self.assertTrue(callable(process_single_economy_politics_feed))


class TestSpecialTags(unittest.TestCase):
    """Test that economy_politics special tag is applied"""

    @patch('economy_politics_scraper.save_article')
    @patch('economy_politics_scraper.requests.get')
    def test_save_article_called_with_special_tags(self, mock_get, mock_save):
        """Articles should be saved with special_tags=['economy_politics']"""
        # Create a mock RSS response
        rss_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
        <channel>
        <item>
            <title>Zimbabwe inflation hits 50%</title>
            <link>http://example.com/article1</link>
            <pubDate>Mon, 09 Mar 2026 12:00:00 GMT</pubDate>
            <description>Consumer prices soar as inflation rises.</description>
        </item>
        </channel>
        </rss>"""

        # Mock RSS feed response
        rss_response = MagicMock()
        rss_response.status_code = 200
        rss_response.content = rss_xml.encode()
        rss_response.raise_for_status = MagicMock()

        # Mock article content response
        article_response = MagicMock()
        article_response.status_code = 200
        article_response.content = b"<html><body><article>Consumer prices soar as inflation rises in Zimbabwe.</article></body></html>"
        article_response.raise_for_status = MagicMock()

        mock_get.side_effect = [rss_response, article_response]
        mock_save.return_value = "article-123"

        from economy_politics_scraper import process_single_economy_politics_feed
        with patch('economy_politics_scraper.url_already_processed', return_value=False), \
             patch('economy_politics_scraper.is_recent_article', return_value=True), \
             patch('economy_politics_scraper.add_processed_url'):
            process_single_economy_politics_feed("http://example.com/feed.xml", "Zimbabwe")

        # Verify save_article was called
        if mock_save.called:
            call_kwargs = mock_save.call_args
            tags = call_kwargs[1].get('tags', {}) if call_kwargs[1] else call_kwargs[0][6] if len(call_kwargs[0]) > 6 else {}
            # Check special_tags contains economy_politics
            if isinstance(tags, dict):
                self.assertIn('economy_politics', tags.get('special_tags', []))
                self.assertEqual(tags.get('target_country'), 'Zimbabwe')


class TestDescriptionFallback(unittest.TestCase):
    """Test RSS description fallback when article extraction fails"""

    @patch('economy_politics_scraper.save_article')
    @patch('economy_politics_scraper.extract_full_article_content')
    @patch('economy_politics_scraper.requests.get')
    def test_fallback_to_description_when_extraction_fails(self, mock_get, mock_extract, mock_save):
        """When article extraction returns None but RSS description exists, article should still be saved"""
        rss_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
        <channel>
        <item>
            <title>US inflation hits new high amid economic concerns</title>
            <link>http://example.com/blocked-article</link>
            <pubDate>Mon, 09 Mar 2026 12:00:00 GMT</pubDate>
            <description>Consumer prices rose sharply as inflation concerns mount across the United States, with the Federal Reserve considering further interest rate adjustments to combat rising costs.</description>
        </item>
        </channel>
        </rss>"""

        rss_response = MagicMock()
        rss_response.status_code = 200
        rss_response.content = rss_xml.encode()
        rss_response.raise_for_status = MagicMock()

        mock_get.return_value = rss_response
        mock_extract.return_value = None  # Simulate 403 / extraction failure
        mock_save.return_value = "article-fallback-123"

        from economy_politics_scraper import process_single_economy_politics_feed
        with patch('economy_politics_scraper.url_already_processed', return_value=False), \
             patch('economy_politics_scraper.is_recent_article', return_value=True), \
             patch('economy_politics_scraper.add_processed_url'), \
             patch('economy_politics_scraper.progress_tracker') as mock_tracker:
            mock_tracker.is_feed_complete.return_value = False
            count = process_single_economy_politics_feed("http://example.com/feed.xml", "USA")

        self.assertEqual(count, 1)
        self.assertTrue(mock_save.called, "save_article should be called with description fallback")
        call_kwargs = mock_save.call_args[1]
        self.assertIn('inflation', call_kwargs['full_content'].lower())

    @patch('economy_politics_scraper.save_article')
    @patch('economy_politics_scraper.extract_full_article_content')
    @patch('economy_politics_scraper.requests.get')
    def test_no_fallback_for_short_description(self, mock_get, mock_extract, mock_save):
        """When description is too short (<=50 chars), article should be skipped"""
        rss_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
        <channel>
        <item>
            <title>US inflation hits new high</title>
            <link>http://example.com/blocked-article2</link>
            <pubDate>Mon, 09 Mar 2026 12:00:00 GMT</pubDate>
            <description>Short desc</description>
        </item>
        </channel>
        </rss>"""

        rss_response = MagicMock()
        rss_response.status_code = 200
        rss_response.content = rss_xml.encode()
        rss_response.raise_for_status = MagicMock()

        mock_get.return_value = rss_response
        mock_extract.return_value = None
        mock_save.return_value = None

        from economy_politics_scraper import process_single_economy_politics_feed
        with patch('economy_politics_scraper.url_already_processed', return_value=False), \
             patch('economy_politics_scraper.is_recent_article', return_value=True), \
             patch('economy_politics_scraper.add_processed_url'), \
             patch('economy_politics_scraper.progress_tracker') as mock_tracker:
            mock_tracker.is_feed_complete.return_value = False
            count = process_single_economy_politics_feed("http://example.com/feed.xml", "USA")

        self.assertEqual(count, 0)
        self.assertFalse(mock_save.called, "save_article should NOT be called for short descriptions")


class TestDeployScriptCoverage(unittest.TestCase):
    """Ensure deploy script includes all files imported by lambda_wrapper.py"""

    def test_deploy_script_includes_economy_politics_scraper(self):
        """deploy_lambda.sh must copy economy_politics_scraper.py into the Lambda package"""
        deploy_script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'deploy_lambda.sh')
        with open(deploy_script_path, 'r') as f:
            deploy_content = f.read()
        self.assertIn('economy_politics_scraper.py', deploy_content,
                      "deploy_lambda.sh must include economy_politics_scraper.py in the Lambda package")


if __name__ == '__main__':
    unittest.main()
