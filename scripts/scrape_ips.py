#!/usr/bin/env python3
# first scraper i wrote, html based. scrape_api.py replaced it mostly

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE = "https://ips.ge"
OUT = Path(__file__).resolve().parent / "content"
OUT.mkdir(exist_ok=True)
IMG_DIR = OUT / "images"
IMG_DIR.mkdir(exist_ok=True)

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
        "Accept-Language": "ka,en;q=0.8",
    }
)

SEED_PAGES = [
    "/",
    "/en/",
    "/services/",
    "/en/services/",
    "/about-us/",
    "/en/about-us/",
    "/interior/",
    "/en/interior/",
    "/facade/",
    "/en/facade/",
    "/interior-brands/",
    "/en/ips-interior-brands/",
    "/facade-brands/",
    "/en/ips-facade-brands/",
    "/all-projects/",
    "/en/all-projects/",
    "/all-projects/interior-projects/",
    "/en/all-projects/interior-projects/",
    "/all-projects/facade-projects/",
    "/en/all-projects/facade-projects/",
    "/interior-services/",
    "/en/interior-services/",
    "/facade-services/",
    "/en/facade-services/",
]


def get(url: str, retries: int = 3) -> BeautifulSoup | None:
    for i in range(retries):
        try:
            r = SESSION.get(url, timeout=45)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            r.encoding = r.apparent_encoding or "utf-8"
            return BeautifulSoup(r.text, "lxml")
        except Exception as exc:  # noqa: BLE001
            if i == retries - 1:
                print(f"FAIL {url}: {exc}")
                return None
            time.sleep(1.2 * (i + 1))
    return None


def abs_url(href: str | None) -> str | None:
    if not href:
        return None
    href = href.strip()
    if href.startswith(("mailto:", "tel:", "javascript:", "#")):
        return None
    return urljoin(BASE, href)


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    text = text.replace(
        "This site is registered on portal.liquid-themes.com as a development site. Switch to production mode to remove this warning.",
        "",
    ).strip()
    return text


def lang_of(url: str) -> str:
    path = urlparse(url).path
    return "en" if path.startswith("/en/") or path == "/en" else "ka"


def extract_nav(soup: BeautifulSoup) -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()
    for a in soup.select("header a, .main-nav a, #menu-primary a, nav a"):
        href = abs_url(a.get("href"))
        label = clean_text(a.get_text(" ", strip=True))
        if not href or not label or href in seen:
            continue
        if urlparse(href).netloc and "ips.ge" not in urlparse(href).netloc:
            continue
        seen.add(href)
        items.append({"label": label, "url": href, "lang": lang_of(href)})
    return items


def extract_main_html(soup: BeautifulSoup) -> str:
    main = (
        soup.select_one("main")
        or soup.select_one("#content")
        or soup.select_one(".lqd-contents")
        or soup.select_one(".content")
        or soup.body
    )
    if not main:
        return ""
    clone = BeautifulSoup(str(main), "lxml")
    for bad in clone.select(
        "script, style, noscript, iframe, .liquid-warning, .ld-notice, nav, header, footer, .site-header, .site-footer"
    ):
        bad.decompose()
    # keep relative images absolute
    for img in clone.select("img[src]"):
        src = abs_url(img.get("src"))
        if src:
            img["src"] = src
    for a in clone.select("a[href]"):
        href = abs_url(a.get("href"))
        if href:
            a["href"] = href
    return str(clone)


def extract_images(soup: BeautifulSoup) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for img in soup.select("img[src]"):
        src = abs_url(img.get("src"))
        if not src or src in seen:
            continue
        if "flags/" in src or "data:image" in src:
            continue
        seen.add(src)
        urls.append(src)
    # background images in style attrs
    for el in soup.select("[style*='background']"):
        style = el.get("style") or ""
        for m in re.finditer(r"url\((['\"]?)(.*?)\1\)", style):
            src = abs_url(m.group(2))
            if src and src not in seen and "flags/" not in src:
                seen.add(src)
                urls.append(src)
    return urls


def extract_project_fields(soup: BeautifulSoup) -> dict:
    fields: dict[str, str] = {}
    # common liquid/portfolio meta patterns
    for block in soup.select("li, p, div, span"):
        label = clean_text(block.get_text(" ", strip=True))
        if not label:
            continue
        for key_ka, key_en, out in [
            ("სერვისები", "Services", "services"),
            ("შესრულებული სამუშაო", "Work done", "work_done"),
            ("გამოყენებული მასალები", "Materials used", "materials"),
            ("ბრენდები", "Brands", "brands"),
        ]:
            if label.startswith(key_ka) or label.startswith(key_en):
                # try next sibling text
                nxt = block.find_next_sibling()
                val = clean_text(nxt.get_text(" ", strip=True)) if nxt else ""
                if not val:
                    # same element after label
                    val = clean_text(re.sub(rf"^({key_ka}|{key_en})\s*", "", label, flags=re.I))
                if val and out not in fields:
                    fields[out] = val
    return fields


def page_record(url: str, soup: BeautifulSoup) -> dict:
    title = clean_text(soup.title.get_text() if soup.title else "")
    h1 = soup.select_one("h1")
    h2 = soup.select_one("h1, h2.entry-title, .ld-fh-element h2, article h2")
    heading = clean_text((h1 or h2).get_text(" ", strip=True) if (h1 or h2) else title)
    # remove site suffix
    heading = re.sub(r"\s*[-|–]\s*IPS\s*$", "", heading).strip()
    title = re.sub(r"\s*[-|–]\s*IPS\s*$", "", title).strip()

    paragraphs = [
        clean_text(p.get_text(" ", strip=True))
        for p in soup.select("main p, #content p, article p, .lqd-column p")
        if clean_text(p.get_text(" ", strip=True))
    ]
    # unique preserve order
    seen_p: set[str] = set()
    paras: list[str] = []
    for p in paragraphs:
        if p not in seen_p and len(p) > 2:
            seen_p.add(p)
            paras.append(p)

    headings = [
        clean_text(h.get_text(" ", strip=True))
        for h in soup.select("main h2, main h3, main h4, #content h2, #content h3, #content h4, article h2, article h3, article h4")
        if clean_text(h.get_text(" ", strip=True))
    ]

    lists: list[list[str]] = []
    for ul in soup.select("main ul, #content ul, article ul"):
        items = [clean_text(li.get_text(" ", strip=True)) for li in ul.select(":scope > li")]
        items = [i for i in items if i]
        if items:
            lists.append(items)

    return {
        "url": url,
        "lang": lang_of(url),
        "title": title or heading,
        "heading": heading or title,
        "paragraphs": paras,
        "headings": headings,
        "lists": lists,
        "images": extract_images(soup),
        "html": extract_main_html(soup),
        "fields": extract_project_fields(soup) if "/project/" in url else {},
    }


def collect_links(soup: BeautifulSoup) -> set[str]:
    links: set[str] = set()
    for a in soup.select("a[href]"):
        href = abs_url(a.get("href"))
        if not href:
            continue
        parsed = urlparse(href)
        if "ips.ge" not in parsed.netloc:
            continue
        path = parsed.path.rstrip("/") + ("/" if parsed.path.endswith("/") or not Path(parsed.path).suffix else "")
        # normalize
        if any(
            x in path
            for x in (
                "/wp-admin",
                "/wp-login",
                "/feed",
                "/cdn-cgi",
                ".pdf",
                ".jpg",
                ".png",
                ".webp",
                ".svg",
                ".jpeg",
                ".gif",
            )
        ):
            continue
        links.add(f"{parsed.scheme}://{parsed.netloc}{parsed.path}")
    return links


def download_image(url: str) -> str | None:
    try:
        name = re.sub(r"[^a-zA-Z0-9._-]+", "-", Path(urlparse(url).path).name)
        if not name or name == "-":
            return None
        dest = IMG_DIR / name
        if dest.exists() and dest.stat().st_size > 0:
            return f"content/images/{name}"
        r = SESSION.get(url, timeout=60)
        r.raise_for_status()
        dest.write_bytes(r.content)
        return f"content/images/{name}"
    except Exception as exc:  # noqa: BLE001
        print(f"IMG FAIL {url}: {exc}")
        return None


def main() -> None:
    queue: list[str] = [urljoin(BASE, p) for p in SEED_PAGES]
    seen: set[str] = set()
    pages: dict[str, dict] = {}
    nav: list[dict] = []

    # BFS crawl limited to ips.ge content paths
    while queue:
        url = queue.pop(0)
        # normalize trailing slash for non-files
        if not Path(urlparse(url).path).suffix and not url.endswith("/"):
            url += "/"
        if url in seen:
            continue
        seen.add(url)
        print(f"GET {url}")
        soup = get(url)
        if not soup:
            continue
        if not nav:
            nav = extract_nav(soup)
        rec = page_record(url, soup)
        pages[url] = rec

        for link in collect_links(soup):
            path = urlparse(link).path
            interesting = any(
                seg in path
                for seg in (
                    "/project/",
                    "/brand/",
                    "/all-projects",
                    "/interior",
                    "/facade",
                    "/services",
                    "/about",
                    "/news",
                    "/blog",
                    "/contact",
                    "/team",
                    "/career",
                    "/social",
                    "/get-to-know",
                )
            ) or path in ("/", "/en/")
            if interesting and link not in seen:
                queue.append(link)
        time.sleep(0.25)

    # categorize
    projects = {u: p for u, p in pages.items() if "/project/" in u}
    brands = {u: p for u, p in pages.items() if "/brand/" in u}
    other = {u: p for u, p in pages.items() if u not in projects and u not in brands}

    # download a reasonable set of images (featured-ish: first few per page + brand logos)
    local_map: dict[str, str] = {}
    image_urls: list[str] = []
    for p in pages.values():
        image_urls.extend(p.get("images") or [])
    # prefer uploads
    image_urls = [u for u in dict.fromkeys(image_urls) if "/wp-content/uploads/" in u]
    print(f"Downloading up to {min(len(image_urls), 180)} images…")
    for url in image_urls[:180]:
        local = download_image(url)
        if local:
            local_map[url] = local
        time.sleep(0.05)

    # attach local paths
    for p in pages.values():
        p["local_images"] = [local_map[i] for i in p.get("images", []) if i in local_map]

    payload = {
        "source": BASE,
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "counts": {
            "pages": len(pages),
            "projects": len(projects),
            "brands": len(brands),
            "images_local": len(local_map),
        },
        "nav": nav,
        "pages": pages,
        "projects": projects,
        "brands": brands,
        "other": other,
        "image_map": local_map,
    }

    out_json = OUT / "site-content.json"
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", out_json)
    print(json.dumps(payload["counts"], indent=2))


if __name__ == "__main__":
    main()
