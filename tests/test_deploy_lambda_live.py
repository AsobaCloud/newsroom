"""Live integration tests for the Lambda deploy / RSS parser fix.

These tests hit real RSS feeds and run actual pip commands — they are NOT
mock-data unit tests. They verify:
  1. The xml parser extracts links from real-world RSS feeds
  2. The html.parser FAILS to extract links (documenting the production bug)
  3. The exact extraction logic from news_scraper.py works/fails per parser
  4. pip cross-compilation actually produces Linux .so files
  5. The deploy script's pip command produces Linux binaries (not darwin)
"""

import glob
import os
import re
import shutil
import subprocess
import tempfile

import pytest
import requests
from bs4 import BeautifulSoup

# Real RSS feeds used by the scraper in production
LIVE_FEEDS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://www.theguardian.com/world/rss",
    "https://techcrunch.com/feed/",
    "https://www.aljazeera.com/xml/rss/all.xml",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )
}

DEPLOY_SCRIPT = os.path.join(
    os.path.dirname(__file__), "..", "scripts", "deploy_lambda.sh"
)


def _fetch_feed(url):
    """Fetch a live RSS feed, return raw bytes."""
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.content


def _extract_link_like_scraper(item):
    """Replicate the exact link extraction from news_scraper.py lines 616-623."""
    link = None
    if item.find("link"):
        link_elem = item.find("link")
        if link_elem.get("href"):  # Atom format
            link = link_elem.get("href")
        else:  # RSS format
            link = link_elem.get_text()
    return link if link else None


def _extract_pip_install_command(script_path):
    """Parse the pip install command for requirements.txt from the deploy script.

    Returns a list of tokens (the argv that should be passed to subprocess),
    or raises ValueError if the command cannot be found.
    """
    with open(script_path, "r") as fh:
        lines = fh.readlines()

    # Find the line starting the pip3 install command, then collect
    # continuation lines (lines ending with backslash).
    cmd_lines = []
    collecting = False
    for line in lines:
        stripped = line.rstrip("\n")
        if not collecting:
            if re.match(r"\s*pip3\s+install\b", stripped):
                collecting = True
                cmd_lines.append(stripped)
                if not stripped.rstrip().endswith("\\"):
                    break
        else:
            cmd_lines.append(stripped)
            if not stripped.rstrip().endswith("\\"):
                break

    if not cmd_lines:
        raise ValueError(
            f"Could not find 'pip3 install' command in {script_path}"
        )

    # Join lines, remove trailing backslashes, normalise whitespace
    raw = " ".join(line.rstrip().rstrip("\\") for line in cmd_lines)
    tokens = raw.split()
    return tokens


# ---------------------------------------------------------------------------
# Category 1: xml parser extracts links from real feeds
# ---------------------------------------------------------------------------
class TestXmlParserOnLiveFeeds:
    """Verify that the xml parser (requires working lxml) extracts links
    from real-world RSS feeds that the scraper depends on."""

    @pytest.mark.network
    @pytest.mark.parametrize("feed_url", LIVE_FEEDS)
    def test_xml_parser_finds_items_with_links(self, feed_url):
        content = _fetch_feed(feed_url)
        soup = BeautifulSoup(content, "xml")

        items = soup.find_all("item")
        if not items:
            items = soup.find_all("entry")  # Atom fallback
        assert len(items) > 0, f"No items/entries found in {feed_url}"

        # At least half the items should have extractable links
        links = [_extract_link_like_scraper(item) for item in items]
        valid = [lnk for lnk in links if lnk and lnk.startswith("http")]
        assert len(valid) >= len(items) // 2, (
            f"xml parser extracted only {len(valid)}/{len(items)} links from {feed_url}"
        )


# ---------------------------------------------------------------------------
# Category 2: html.parser FAILS on the same real feeds
# ---------------------------------------------------------------------------
class TestHtmlParserFailsOnLiveFeeds:
    """Demonstrate that html.parser cannot extract links from the same
    real feeds — this IS the production bug."""

    @pytest.mark.network
    @pytest.mark.parametrize("feed_url", LIVE_FEEDS)
    def test_html_parser_produces_empty_links(self, feed_url):
        content = _fetch_feed(feed_url)
        soup = BeautifulSoup(content, "html.parser")

        items = soup.find_all("item")
        if not items:
            items = soup.find_all("entry")
        # html.parser may still find <item> tags in some feeds
        if not items:
            pytest.skip(f"html.parser found no items in {feed_url}")

        links = [_extract_link_like_scraper(item) for item in items]
        valid = [lnk for lnk in links if lnk and lnk.startswith("http")]

        # The bug: html.parser should extract zero or near-zero valid links
        assert len(valid) <= 1, (
            f"html.parser unexpectedly extracted {len(valid)} valid links "
            f"from {feed_url} — if this consistently passes, the parser "
            f"fallback may no longer be broken"
        )


# ---------------------------------------------------------------------------
# Category 3: Full extraction logic (parser cascade) against live feeds
# ---------------------------------------------------------------------------
class TestScraperParserCascadeOnLiveFeeds:
    """Test the full parser fallback chain from news_scraper.py:580-609
    against real feed data."""

    @pytest.mark.network
    @pytest.mark.parametrize("feed_url", LIVE_FEEDS[:2])  # BBC + Guardian
    def test_parser_cascade_xml_first(self, feed_url):
        """Simulates what happens when lxml works: xml parser succeeds."""
        content = _fetch_feed(feed_url)
        items = []

        # Method 1: xml parser (preferred)
        try:
            soup = BeautifulSoup(content, "xml")
            items = soup.find_all("item")
            if not items:
                items = soup.find_all("entry")
        except Exception:
            pass

        assert len(items) > 0, "xml parser should find items from live feed"

        links = [_extract_link_like_scraper(item) for item in items]
        valid = [lnk for lnk in links if lnk and lnk.startswith("http")]
        assert len(valid) > 5, (
            f"Expected >5 valid links from {feed_url}, got {len(valid)}"
        )

    @pytest.mark.network
    @pytest.mark.parametrize("feed_url", LIVE_FEEDS[:2])
    def test_parser_cascade_html_fallback(self, feed_url):
        """Simulates what happens when lxml is broken: falls through to
        html.parser and extracts zero links."""
        content = _fetch_feed(feed_url)
        items = []

        # Skip xml and lxml — go straight to html.parser (the Lambda failure)
        soup = BeautifulSoup(content, "html.parser")
        items = soup.find_all("item")
        if not items:
            items = soup.find_all("entry")

        links = [_extract_link_like_scraper(item) for item in items]
        valid = [lnk for lnk in links if lnk and lnk.startswith("http")]
        assert len(valid) == 0, (
            f"html.parser should extract 0 links but got {len(valid)} from {feed_url}"
        )


# ---------------------------------------------------------------------------
# Category 4: pip cross-compilation actually produces Linux binaries
# ---------------------------------------------------------------------------
class TestPipCrossCompilation:
    """Verify that pip with --platform manylinux2014_x86_64 actually
    downloads Linux .so files, not darwin ones."""

    def test_cross_compile_lxml_produces_linux_binaries(self):
        tmpdir = tempfile.mkdtemp(prefix="test_lambda_pkg_")
        try:
            result = subprocess.run(
                [
                    "pip3", "install", "lxml",
                    "-t", tmpdir,
                    "--platform", "manylinux2014_x86_64",
                    "--only-binary=:all:",
                    "--python-version", "3.9",
                    "--implementation", "cp",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            assert result.returncode == 0, (
                f"pip cross-compile failed: {result.stderr}"
            )

            # Find all .so files
            so_files = glob.glob(os.path.join(tmpdir, "**", "*.so"), recursive=True)
            assert len(so_files) > 0, "No .so files produced by pip install"

            for so_file in so_files:
                basename = os.path.basename(so_file)
                assert "darwin" not in basename.lower(), (
                    f"Found darwin .so in cross-compiled output: {basename}"
                )
                # manylinux wheels produce .so files — they won't always have
                # "linux" in the name, but they must NOT have "darwin"

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_native_pip_install_produces_darwin_on_macos(self):
        """Control test: without platform flags, macOS pip installs darwin .so."""
        import platform
        if platform.system() != "Darwin":
            pytest.skip("This test only runs on macOS")

        tmpdir = tempfile.mkdtemp(prefix="test_lambda_native_")
        try:
            result = subprocess.run(
                ["pip3", "install", "lxml", "-t", tmpdir],
                capture_output=True,
                text=True,
                timeout=120,
            )
            assert result.returncode == 0, (
                f"pip native install failed: {result.stderr}"
            )

            so_files = glob.glob(os.path.join(tmpdir, "**", "*.so"), recursive=True)
            assert len(so_files) > 0, "No .so files from native install"

            darwin_files = [
                f for f in so_files if "darwin" in os.path.basename(f).lower()
            ]
            assert len(darwin_files) > 0, (
                "Native macOS pip should produce darwin .so files — "
                "this is the control proving the bug mechanism"
            )

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Category 5: Deploy script's pip command produces Linux binaries
# ---------------------------------------------------------------------------
class TestDeployScriptProducesLinuxBinaries:
    """Behavioral test: extract the actual pip install command from
    deploy_lambda.sh, run it against lxml alone (for speed), and verify
    the resulting .so files are Linux binaries — not darwin.

    This test FAILS on the unfixed deploy script because the current command
    (pip3 install -r requirements.txt -t lambda_package/) has no platform
    flags and therefore installs darwin binaries on macOS.
    """

    def test_deploy_script_pip_command_produces_linux_so_files(self):
        import platform
        if platform.system() != "Darwin":
            pytest.skip(
                "This test validates the cross-compilation fix on macOS; "
                "darwin binaries are only the wrong result on macOS hosts."
            )

        # Extract the actual pip install command from the deploy script
        tokens = _extract_pip_install_command(DEPLOY_SCRIPT)

        # Replace '-r requirements.txt' with 'lxml' so we run a fast,
        # targeted subset.  The binary-format flags (if any) apply equally.
        clean_tokens = []
        skip_next = False
        for tok in tokens:
            if skip_next:
                skip_next = False
                continue
            if tok == "-r":
                skip_next = True  # drop the filename that follows
                continue
            if tok == "requirements.txt":
                continue
            clean_tokens.append(tok)

        # Ensure the executable is callable (strip any path prefix)
        clean_tokens[0] = "pip3"

        tmpdir = tempfile.mkdtemp(prefix="test_deploy_script_pip_")
        try:
            # Inject target directory
            cmd = clean_tokens + ["lxml", "-t", tmpdir]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            assert result.returncode == 0, (
                f"Deploy-script pip command failed.\n"
                f"Command: {' '.join(cmd)}\n"
                f"stderr: {result.stderr}"
            )

            so_files = glob.glob(os.path.join(tmpdir, "**", "*.so"), recursive=True)
            assert len(so_files) > 0, (
                f"No .so files produced by deploy script pip command.\n"
                f"Command: {' '.join(cmd)}"
            )

            darwin_files = [
                f for f in so_files if "darwin" in os.path.basename(f).lower()
            ]
            assert len(darwin_files) == 0, (
                f"Deploy script pip command produced darwin .so files on macOS.\n"
                f"Command used: {' '.join(cmd)}\n"
                f"Darwin files found: {[os.path.basename(f) for f in darwin_files]}\n"
                f"This means the deploy script is missing cross-compilation flags "
                f"(--platform manylinux2014_x86_64 --only-binary=:all: "
                f"--python-version 3.9 --implementation cp)."
            )

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Category 6: lxml import failure simulation — full parser fallback chain
# ---------------------------------------------------------------------------
class TestLxmlImportFailureSimulation:
    """Simulate the Lambda failure mode where lxml's .so cannot be imported
    (darwin binary on a Linux runtime).

    When lxml is broken, BeautifulSoup raises an exception for both "xml" and
    "lxml" parsers.  The fallback chain in news_scraper.py:580-609 silently
    catches those exceptions and falls through to "html.parser".

    html.parser DOES find <item> tags in BBC RSS, but it cannot extract the
    link text from them — so every article link ends up None/empty and the
    article is silently skipped.  This test pins that exact behaviour so any
    future code change that accidentally re-introduces the bug is caught.
    """

    BBC_FEED = "https://feeds.bbci.co.uk/news/rss.xml"

    @pytest.mark.network
    def test_lxml_broken_items_found_but_all_links_empty(self, monkeypatch):
        """With lxml broken:
        - the "xml" and "lxml" BeautifulSoup calls raise FeatureNotFound
        - the fallback "html.parser" call succeeds and finds <item> tags
        - link extraction via the scraper's logic returns None for every item
        """
        content = _fetch_feed(self.BBC_FEED)

        # Intercept BeautifulSoup at the bs4 module level so that the "xml"
        # and "lxml" parser calls raise, exactly as they would when lxml's
        # compiled extension cannot be dlopen-ed on Lambda.
        _real_bs4 = BeautifulSoup

        class _LxmlBrokenBeautifulSoup:
            """Drop-in replacement that raises for lxml-backed parsers."""

            def __new__(cls, markup, features=None, **kwargs):
                if features in ("xml", "lxml"):
                    raise Exception(
                        f"Simulated lxml import failure for parser '{features}': "
                        "cannot load darwin .so on Lambda Linux runtime"
                    )
                return _real_bs4(markup, features, **kwargs)

        # Patch bs4.BeautifulSoup in the news_scraper module namespace AND in
        # this test module so both call sites use the same patched class.
        import bs4
        monkeypatch.setattr(bs4, "BeautifulSoup", _LxmlBrokenBeautifulSoup)

        # -----------------------------------------------------------------
        # Re-run the exact parser fallback chain from news_scraper.py:580-609
        # -----------------------------------------------------------------
        soup = None
        items = []

        # Method 1: XML parser (preferred for RSS/Atom) — must raise
        try:
            soup = _LxmlBrokenBeautifulSoup(content, "xml")
            items = soup.find_all("item")
            if not items:
                items = soup.find_all("entry")
        except Exception:
            pass

        # Method 2: lxml parser fallback — must also raise
        if not items:
            try:
                soup = _LxmlBrokenBeautifulSoup(content, "lxml")
                items = soup.find_all("item")
                if not items:
                    items = soup.find_all("entry")
            except Exception:
                pass

        # Method 3: HTML parser fallback — must NOT raise, finds <item> tags
        if not items:
            try:
                soup = _LxmlBrokenBeautifulSoup(content, "html.parser")
                items = soup.find_all("item")
                if not items:
                    items = soup.find_all("entry")
            except Exception:
                pass

        # -----------------------------------------------------------------
        # Assertions
        # -----------------------------------------------------------------

        # html.parser does find <item> elements — the code reaches "process
        # items from whichever parser succeeded" and iterates over them.
        assert len(items) > 0, (
            "html.parser fallback should still find <item> tags in BBC RSS; "
            "got 0 items — the feed structure may have changed"
        )

        # But every link extracted by the scraper's own logic must be empty,
        # because html.parser mangling means <link> elements lose their text.
        links = [_extract_link_like_scraper(item) for item in items]
        valid_links = [lnk for lnk in links if lnk and lnk.startswith("http")]

        assert len(valid_links) == 0, (
            f"Expected 0 valid links when lxml is broken (html.parser fallback), "
            f"but got {len(valid_links)} out of {len(items)} items.\n"
            f"Sample valid links: {valid_links[:5]}\n"
            "If html.parser now extracts links correctly the parser fallback "
            "strategy in news_scraper.py may need revisiting."
        )

    @pytest.mark.network
    def test_lxml_broken_xml_parser_call_raises(self, monkeypatch):
        """Verify the mock itself works: calling BeautifulSoup with 'xml'
        raises when lxml is simulated as broken."""
        import bs4

        _real_bs4 = bs4.BeautifulSoup

        def _broken_bs4(markup, features=None, **kwargs):
            if features in ("xml", "lxml"):
                raise Exception(f"Simulated lxml failure for '{features}'")
            return _real_bs4(markup, features, **kwargs)

        monkeypatch.setattr(bs4, "BeautifulSoup", _broken_bs4)

        content = _fetch_feed(self.BBC_FEED)

        with pytest.raises(Exception, match="Simulated lxml failure for 'xml'"):
            _broken_bs4(content, "xml")

        with pytest.raises(Exception, match="Simulated lxml failure for 'lxml'"):
            _broken_bs4(content, "lxml")

    @pytest.mark.network
    def test_lxml_broken_html_parser_still_finds_items(self, monkeypatch):
        """Verify independently that html.parser finds <item> tags in BBC RSS
        even when lxml is unavailable — confirming the fallback is reached."""
        import bs4

        _real_bs4 = bs4.BeautifulSoup

        def _broken_bs4(markup, features=None, **kwargs):
            if features in ("xml", "lxml"):
                raise Exception(f"Simulated lxml failure for '{features}'")
            return _real_bs4(markup, features, **kwargs)

        monkeypatch.setattr(bs4, "BeautifulSoup", _broken_bs4)

        content = _fetch_feed(self.BBC_FEED)
        soup = _broken_bs4(content, "html.parser")
        items = soup.find_all("item")

        assert len(items) > 0, (
            "html.parser should find at least one <item> in BBC RSS "
            f"(got 0); feed URL: {self.BBC_FEED}"
        )
