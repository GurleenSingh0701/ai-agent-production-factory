import httpx
from bs4 import BeautifulSoup
import re
from typing import Dict, Any

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

async def scrape_website(url: str, timeout: float = 10.0) -> Dict[str, Any]:
    """
    Scrapes a web page asynchronously and extracts clean textual content.
    Returns a dictionary containing status, title, meta description, and scraped text.
    """
    target_url = url.strip()
    if not target_url.startswith(("http://", "https://")):
        target_url = f"https://{target_url}"

    headers = {"User-Agent": DEFAULT_USER_AGENT}

    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, verify=False) as client:
            response = await client.get(target_url, headers=headers)
            response.raise_for_status()
            html_content = response.text

        soup = BeautifulSoup(html_content, "html.parser")

        # Remove non-content elements
        for element in soup(["script", "style", "noscript", "header", "footer", "nav", "svg", "iframe", "form", "button"]):
            element.decompose()

        # Extract title
        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        # Extract meta description
        meta_desc = ""
        desc_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)}) or \
                   soup.find("meta", attrs={"property": re.compile(r"og:description", re.I)})
        if desc_tag and desc_tag.get("content"):
            meta_desc = desc_tag["content"].strip()

        # Extract visible body text
        text_blocks = [tag.get_text(separator=" ", strip=True) for tag in soup.find_all(["h1", "h2", "h3", "p", "li"])]
        full_text = " ".join([t for t in text_blocks if t])

        # Clean excessive whitespace
        full_text = re.sub(r"\s+", " ", full_text).strip()

        # Limit text length for LLM prompt context window (~3500 chars)
        if len(full_text) > 3500:
            full_text = full_text[:3500] + "... [truncated]"

        summary_text = f"Title: {title}\nMeta Description: {meta_desc}\nContent: {full_text}"

        return {
            "success": True,
            "url": target_url,
            "title": title,
            "meta_description": meta_desc,
            "scraped_text": summary_text,
        }

    except Exception as e:
        return {
            "success": False,
            "url": target_url,
            "error": str(e),
            "scraped_text": f"Failed to scrape website {target_url} directly (Error: {str(e)}). Proceeding with domain analysis.",
        }
