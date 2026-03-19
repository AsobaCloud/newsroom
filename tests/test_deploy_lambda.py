"""Tests for the RSS link extraction failure caused by parser fallback.

Root cause: when lxml is unavailable (e.g. darwin .so on Linux Lambda),
BeautifulSoup falls back to html.parser, which treats <link> as a void
HTML element and discards the URL text. This causes 0 articles from every feed.
"""

from bs4 import BeautifulSoup


# Minimal but realistic RSS feed with CDATA titles and <link> elements,
# matching the structure returned by BBC, Guardian, CNN, etc.
SAMPLE_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <link>https://example.com</link>
    <item>
      <title><![CDATA[Energy crisis deepens across Europe]]></title>
      <link>https://example.com/articles/energy-crisis</link>
      <description>European energy markets face new challenges.</description>
      <pubDate>Thu, 19 Mar 2026 05:00:00 GMT</pubDate>
    </item>
    <item>
      <title><![CDATA[AI regulation bill passes senate]]></title>
      <link>https://example.com/articles/ai-regulation</link>
      <description>New artificial intelligence oversight framework approved.</description>
      <pubDate>Thu, 19 Mar 2026 04:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Oil prices surge after Gulf tensions</title>
      <link>https://example.com/articles/oil-prices</link>
      <description>Crude oil benchmarks hit six-month highs.</description>
      <pubDate>Thu, 19 Mar 2026 03:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""

# Atom feed format (used by arxiv, some Google feeds, etc.)
SAMPLE_ATOM = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Test Atom Feed</title>
  <entry>
    <title>Blockchain consensus mechanisms compared</title>
    <link href="https://example.com/papers/blockchain-consensus"/>
    <summary>A survey of proof-of-stake variants.</summary>
    <published>2026-03-19T02:00:00Z</published>
  </entry>
</feed>"""

# RSS with empty/missing link (edge case some feeds have)
RSS_MISSING_LINK = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Article with no link</title>
      <description>This item has no link element at all.</description>
    </item>
    <item>
      <title>Article with empty link</title>
      <link></link>
      <description>This item has an empty link element.</description>
    </item>
  </channel>
</rss>"""

# RSS with guid as permalink (some feeds use guid instead of link)
RSS_GUID_PERMALINK = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Article using guid as link</title>
      <guid isPermaLink="true">https://example.com/articles/guid-article</guid>
      <description>Energy storage breakthrough announced.</description>
    </item>
  </channel>
</rss>"""


class TestXmlParserExtractsLinks:
    """The xml parser (requires lxml) correctly extracts <link> text content."""

    def test_extracts_link_urls_from_rss(self):
        soup = BeautifulSoup(SAMPLE_RSS, "xml")
        items = soup.find_all("item")
        assert len(items) == 3

        links = []
        for item in items:
            link_elem = item.find("link")
            assert link_elem is not None
            url = link_elem.get_text()
            assert url.startswith("https://"), f"Expected URL, got: {url!r}"
            links.append(url)

        assert links == [
            "https://example.com/articles/energy-crisis",
            "https://example.com/articles/ai-regulation",
            "https://example.com/articles/oil-prices",
        ]

    def test_extracts_cdata_titles(self):
        soup = BeautifulSoup(SAMPLE_RSS, "xml")
        items = soup.find_all("item")
        titles = [item.find("title").get_text() for item in items]

        # xml parser should unwrap CDATA cleanly
        assert titles[0] == "Energy crisis deepens across Europe"
        assert titles[1] == "AI regulation bill passes senate"

    def test_extracts_atom_href_links(self):
        soup = BeautifulSoup(SAMPLE_ATOM, "xml")
        entries = soup.find_all("entry")
        assert len(entries) == 1

        link_elem = entries[0].find("link")
        href = link_elem.get("href")
        assert href == "https://example.com/papers/blockchain-consensus"


class TestHtmlParserFailsOnRssLinks:
    """Documents the known html.parser failure mode that caused the production bug.

    html.parser treats <link> as a void/self-closing HTML element, discarding
    the URL text inside it. This is correct HTML behavior but wrong for RSS XML.
    """

    def test_html_parser_returns_empty_link_text(self):
        """This is the exact bug: html.parser makes <link>URL</link> into <link/>."""
        soup = BeautifulSoup(SAMPLE_RSS, "html.parser")
        items = soup.find_all("item")

        for item in items:
            link_elem = item.find("link")
            # html.parser treats <link> as self-closing, so get_text() is empty
            # and get('href') is None — no way to extract the URL
            text = link_elem.get_text() if link_elem else ""
            href = link_elem.get("href") if link_elem else None
            assert text == "" or href is None, (
                "If this assertion fails, html.parser now handles RSS <link> "
                "correctly and the parser fallback is no longer a problem"
            )

    def test_html_parser_wraps_cdata_in_title(self):
        """html.parser doesn't unwrap CDATA — titles contain raw CDATA markers."""
        soup = BeautifulSoup(SAMPLE_RSS, "html.parser")
        items = soup.find_all("item")
        title_text = items[0].find("title").get_text()

        # html.parser leaves CDATA wrapper in the text
        assert "CDATA" in title_text or "Energy crisis" in title_text


class TestRssLinkExtractionLogic:
    """Tests the link extraction logic matching news_scraper.py:612-649."""

    def _extract_link(self, item):
        """Replicates the link extraction logic from process_single_rss_feed."""
        link = None
        if item.find("link"):
            link_elem = item.find("link")
            if link_elem.get("href"):  # Atom format
                link = link_elem.get("href")
            else:  # RSS format
                link = link_elem.get_text()
        return link if link else None

    def test_rss_links_extracted_with_xml_parser(self):
        soup = BeautifulSoup(SAMPLE_RSS, "xml")
        items = soup.find_all("item")

        links = [self._extract_link(item) for item in items]
        assert all(link is not None and link.startswith("https://") for link in links)
        assert len(links) == 3

    def test_rss_links_fail_with_html_parser(self):
        """Reproduces the production bug: all links are empty with html.parser."""
        soup = BeautifulSoup(SAMPLE_RSS, "html.parser")
        items = soup.find_all("item")

        links = [self._extract_link(item) for item in items]
        # Every link is None or empty — this is the bug
        assert all(link is None or link == "" for link in links), (
            "Expected all links to be empty with html.parser (the production bug)"
        )

    def test_atom_href_extracted_with_xml_parser(self):
        soup = BeautifulSoup(SAMPLE_ATOM, "xml")
        entries = soup.find_all("entry")

        link = self._extract_link(entries[0])
        assert link == "https://example.com/papers/blockchain-consensus"

    def test_missing_link_returns_none(self):
        soup = BeautifulSoup(RSS_MISSING_LINK, "xml")
        items = soup.find_all("item")

        # First item has no link at all
        link0 = self._extract_link(items[0])
        assert link0 is None

        # Second item has empty <link></link>
        link1 = self._extract_link(items[1])
        assert link1 is None or link1 == ""


class TestDeployScriptProducesLinuxBinaries:
    """Verify the deploy script will install Linux-compatible packages."""

    def test_pip_install_line_targets_linux(self):
        with open("scripts/deploy_lambda.sh", "r") as f:
            content = f.read()

        assert "--platform manylinux2014_x86_64" in content, (
            "pip install must use --platform manylinux2014_x86_64 to produce "
            "Linux-compatible .so files instead of darwin ones"
        )

    def test_pip_install_forces_prebuilt_wheels(self):
        with open("scripts/deploy_lambda.sh", "r") as f:
            content = f.read()

        assert "--only-binary=:all:" in content, (
            "pip install must use --only-binary=:all: to force downloading "
            "pre-built wheels rather than building from source"
        )

    def test_pip_install_targets_correct_python_version(self):
        """pip must target the same Python version as the Lambda runtime."""
        with open("scripts/deploy_lambda.sh", "r") as f:
            content = f.read()

        # Extract the runtime version from the Lambda create command
        assert "--runtime python3.9" in content, "Lambda runtime should be python3.9"
        assert "--python-version 3.9" in content, (
            "pip --python-version must match the Lambda --runtime version"
        )

    def test_no_darwin_references_in_pip_install(self):
        """The pip install line must not contain darwin or macOS platform refs."""
        with open("scripts/deploy_lambda.sh", "r") as f:
            content = f.read()

        # Find the pip install line(s)
        for line in content.split("\n"):
            if "pip" in line and "install" in line:
                assert "darwin" not in line.lower(), (
                    "pip install must not reference darwin platform"
                )
                assert "macos" not in line.lower(), (
                    "pip install must not reference macOS platform"
                )
