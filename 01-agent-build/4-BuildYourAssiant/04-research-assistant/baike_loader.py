from __future__ import annotations

from typing import Iterator, List, Optional

import re
from urllib.parse import quote, urljoin, urlencode

import requests

try:
    # LangChain >= 0.2
    from langchain_core.document_loaders.base import BaseLoader
    from langchain_core.documents import Document
except Exception:  # pragma: no cover - fallback for older LangChain
    from langchain.document_loaders.base import BaseLoader  # type: ignore
    from langchain.schema import Document  # type: ignore


class BaiduBaikeLoader(BaseLoader):
    """
    Lightweight loader for Baidu Baike pages.

    - Attempts to resolve a query to a Baidu Baike item page.
    - Falls back to the search page and selects top N item links.
    - Extracts the summary and main text paragraphs when available.

    Parameters
    ----------
    query : str
        The search or entity name to fetch from Baike.
    load_max_docs : int
        Maximum number of item pages to load.
    doc_content_chars_max : Optional[int]
        If set, trims page content to this many characters.
    timeout : int
        HTTP request timeout in seconds.
    headers : Optional[dict]
        Optional extra headers. A default desktop UA is provided.
    """

    def __init__(
        self,
        query: str,
        load_max_docs: int = 2,
        doc_content_chars_max: Optional[int] = None,
        timeout: int = 12,
        headers: Optional[dict] = None,
    ) -> None:
        self.query = query.strip()
        self.load_max_docs = max(1, int(load_max_docs))
        self.doc_content_chars_max = doc_content_chars_max
        self.timeout = timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        if headers:
            self.headers.update(headers)

    def _get(self, url: str) -> requests.Response:
        resp = requests.get(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
        resp.raise_for_status()
        return resp

    def _extract_text(self, html: str) -> str:
        try:
            from bs4 import BeautifulSoup  # lazy import to avoid hard dependency
        except Exception:  # pragma: no cover
            # Fallback: very naive HTML text cleanup if bs4 is missing
            text = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", "", html)
            text = re.sub(r"<[^>]+>", "\n", text)
            text = re.sub(r"\n+", "\n", text)
            text = text.strip()
            if self.doc_content_chars_max is not None and self.doc_content_chars_max > 0:
                text = text[: self.doc_content_chars_max]
            return text

        soup = BeautifulSoup(html, "html.parser")

        # Prefer summary block
        summary = soup.select_one(".lemma-summary, .lemmaWgt-lemmaSummary")
        parts: List[str] = []
        if summary:
            paras = summary.select(".para") or summary.find_all("div", class_="para")
            if paras:
                parts.extend(p.get_text(strip=True) for p in paras)
            else:
                parts.append(summary.get_text("\n", strip=True))

        # Fallback to main content paragraphs
        if not parts:
            main = soup.select_one(".lemmaWgt-lemmaTitle, .lemmaWgt-lemmaInfo, .lemma-main")
            if not main:
                main = soup
            paras = main.find_all(["p", "div"], class_=re.compile(r"para|paragraph|content"))
            if paras:
                parts.extend(p.get_text(strip=True) for p in paras)
            else:
                # As a last resort, grab all text but avoid nav/footer
                for node in soup.select("#top,#bottom,script,style,nav,footer,header"):
                    node.extract()
                text = soup.get_text("\n", strip=True)
                parts.append(text)

        text = "\n".join([p for p in parts if p])
        if self.doc_content_chars_max is not None and self.doc_content_chars_max > 0:
            text = text[: self.doc_content_chars_max]
        return text

    def _search_links(self, html: str) -> List[str]:
        """Extract candidate item links from a Baike search page."""
        try:
            from bs4 import BeautifulSoup  # lazy import
        except Exception:  # pragma: no cover
            # Fallback: regex to approximate Baike item links
            hrefs = re.findall(r"href=\"(/item/[^\"]+)\"", html)
            seen: List[str] = []
            out: List[str] = []
            for h in hrefs:
                u = urljoin("https://baike.baidu.com/", h)
                if u not in seen:
                    seen.append(u)
                    out.append(u)
                if len(out) >= self.load_max_docs:
                    break
            return out

        soup = BeautifulSoup(html, "html.parser")
        links: List[str] = []
        # Typical result links
        for a in soup.select("a.result-title, .search-list a[href^='/item/'], a[href^='/item/']"):
            href = a.get("href")
            if not href:
                continue
            url = urljoin("https://baike.baidu.com/", href)
            if url not in links:
                links.append(url)
            if len(links) >= self.load_max_docs:
                break
        return links

    def lazy_load(self) -> Iterator[Document]:
        if not self.query:
            return iter(())

        # 1) Try direct item URL first
        direct_url = f"https://baike.baidu.com/item/{quote(self.query)}"
        try:
            resp = self._get(direct_url)
            final_url = resp.url
            if "/item/" in final_url:
                text = self._extract_text(resp.text)
                if text.strip():
                    yield Document(page_content=text, metadata={"source": final_url, "source_type": "baike"})
                    # If we only need one doc, stop here
                    if self.load_max_docs <= 1:
                        return
            # If redirected to a search page, continue to search parsing
            html = resp.text
        except Exception:
            # Fall back to explicit search endpoint
            params = urlencode({"word": self.query})
            search_url = f"https://baike.baidu.com/search?{params}"
            try:
                resp = self._get(search_url)
                html = resp.text
            except Exception:
                return iter(())

        # 2) Parse search page for top item links
        try:
            links = self._search_links(html)
        except Exception:
            links = []

        for url in links[: self.load_max_docs]:
            try:
                resp = self._get(url)
                text = self._extract_text(resp.text)
                if text.strip():
                    yield Document(page_content=text, metadata={"source": resp.url, "source_type": "baike"})
            except Exception:
                continue
