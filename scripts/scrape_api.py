#!/usr/bin/env python3
# pulls everything off the old ips.ge through its rest api
# posts, pages, projects, brands — both languages

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "content"
IMG = OUT / "images"
OUT.mkdir(exist_ok=True)
IMG.mkdir(exist_ok=True)

BASE = "https://ips.ge"
API = f"{BASE}/wp-json/wp/v2"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "IPS-FullScrape/2.0", "Accept": "application/json"})


def get_json(url: str, params: dict | None = None):
    for i in range(4):
        try:
            r = SESSION.get(url, params=params, timeout=60)
            r.raise_for_status()
            return r.json(), r.headers
        except Exception as exc:  # noqa: BLE001
            if i == 3:
                print("FAIL", url, exc)
                return None, {}
            time.sleep(1.2 * (i + 1))
    return None, {}


def fetch_all(endpoint: str, extra: dict | None = None) -> list:
    items: list = []
    page = 1
    while True:
        params = {"per_page": 100, "page": page, "_embed": "1"}
        if extra:
            params.update(extra)
        data, headers = get_json(f"{API}/{endpoint}", params)
        if data is None:
            break
        if isinstance(data, dict) and data.get("code"):
            break
        if not isinstance(data, list) or not data:
            break
        items.extend(data)
        total_pages = int(headers.get("X-WP-TotalPages", "1") or 1)
        lang = (extra or {}).get("lang", "ka")
        print(f"  {endpoint}[{lang}] page {page}/{total_pages} (+{len(data)})")
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.2)
    return items


def fetch_bilingual(endpoint: str) -> list:
    ka = fetch_all(endpoint)
    en = fetch_all(endpoint, {"lang": "en"})
    seen = set()
    out = []
    for item in ka + en:
        key = (item.get("id"), item.get("link"))
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def strip_html(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "lxml")
    for bad in soup.select("script, style, noscript"):
        bad.decompose()
    return re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()


def html_blocks(html: str) -> dict:
    soup = BeautifulSoup(html or "", "lxml")
    for bad in soup.select("script, style, noscript"):
        bad.decompose()
    paras = [p.get_text(" ", strip=True) for p in soup.select("p") if p.get_text(strip=True)]
    headings = [h.get_text(" ", strip=True) for h in soup.select("h1,h2,h3,h4,h5,h6") if h.get_text(strip=True)]
    lists = []
    for ul in soup.select("ul, ol"):
        items = [li.get_text(" ", strip=True) for li in ul.select(":scope > li") if li.get_text(strip=True)]
        if items:
            lists.append(items)
    images = []
    for img in soup.select("img[src]"):
        src = img.get("src")
        if src and src.startswith("http"):
            images.append(src)
    # keep cleaned html
    return {
        "paragraphs": paras,
        "headings": headings,
        "lists": lists,
        "images": images,
        "html": str(soup),
        "text": strip_html(html),
    }


def featured(item: dict) -> str | None:
    try:
        media = item.get("_embedded", {}).get("wp:featuredmedia", [])
        if media:
            return media[0].get("source_url")
    except Exception:  # noqa: BLE001
        pass
    return None


def lang_of(link: str) -> str:
    path = urlparse(link or "").path
    return "en" if path.startswith("/en/") else "ka"


def download(url: str | None) -> str | None:
    if not url:
        return None
    name = re.sub(r"[^a-zA-Z0-9._-]+", "-", Path(urlparse(url).path).name)
    if not name or name == "-":
        return None
    dest = IMG / name
    if dest.exists() and dest.stat().st_size > 0:
        return f"content/images/{name}"
    try:
        r = SESSION.get(url, timeout=60)
        r.raise_for_status()
        dest.write_bytes(r.content)
        return f"content/images/{name}"
    except Exception as exc:  # noqa: BLE001
        print("IMG FAIL", url, exc)
        return None


def normalize_item(item: dict, kind: str) -> dict:
    link = item.get("link") or ""
    title = BeautifulSoup(item.get("title", {}).get("rendered", ""), "lxml").get_text(strip=True)
    content_html = item.get("content", {}).get("rendered", "") or ""
    excerpt_html = item.get("excerpt", {}).get("rendered", "") or ""
    blocks = html_blocks(content_html)
    feat = featured(item)
    local_feat = download(feat)
    local_imgs = []
    for src in blocks["images"][:12]:
        loc = download(src)
        if loc:
            local_imgs.append(loc)
    if local_feat and local_feat not in local_imgs:
        local_imgs.insert(0, local_feat)

    meta = item.get("meta") or {}
    acf = item.get("acf") or {}
    # liquid / custom fields often in meta
    fields = {}
    for key, val in {**meta, **acf}.items():
        if val in (None, "", [], {}):
            continue
        if isinstance(val, (str, int, float)):
            fields[str(key)] = str(val)
        elif isinstance(val, list) and all(isinstance(x, (str, int, float)) for x in val):
            fields[str(key)] = ", ".join(map(str, val))

    # Also parse structured labels from content text for projects
    if kind == "project":
        text_lines = BeautifulSoup(content_html, "lxml").get_text("\n", strip=True).splitlines()
        label_map = {
            "services": ("Services", "სერვისები"),
            "work_done": ("Work done", "შესრულებული სამუშაო", "შესრულებული სამუშაოები"),
            "materials": ("Materials used", "გამოყენებული მასალები"),
            "brands": ("Brands", "ბრენდები"),
        }
        lower_to_key = {lab.lower(): k for k, labs in label_map.items() for lab in labs}
        lines = [ln.strip() for ln in text_lines if ln.strip()]
        i = 0
        while i < len(lines):
            key = lower_to_key.get(lines[i].lower())
            if not key:
                i += 1
                continue
            buf = []
            i += 1
            while i < len(lines) and lines[i].lower() not in lower_to_key and lines[i] not in ("Projects", "პროექტები"):
                if lines[i] not in (",",):
                    buf.append(lines[i].rstrip(","))
                i += 1
            if buf:
                fields[key] = ", ".join(buf)

    cats = []
    try:
        for t in item.get("_embedded", {}).get("wp:term", []):
            for term in t:
                cats.append({"id": term.get("id"), "name": term.get("name"), "slug": term.get("slug"), "taxonomy": term.get("taxonomy")})
    except Exception:  # noqa: BLE001
        pass

    return {
        "id": item.get("id"),
        "slug": item.get("slug"),
        "kind": kind,
        "lang": lang_of(link),
        "url": link,
        "title": title,
        "date": item.get("date"),
        "modified": item.get("modified"),
        "excerpt": strip_html(excerpt_html),
        "content": blocks,
        "fields": fields,
        "categories": cats,
        "featured_image": local_feat or feat,
        "images": local_imgs,
        "status": item.get("status"),
    }


def main() -> None:
    print("Fetching posts…")
    posts = fetch_bilingual("posts")
    print("Fetching pages…")
    pages = fetch_bilingual("pages")
    print("Fetching projects…")
    projects = fetch_bilingual("project")
    print("Fetching brands…")
    brands = fetch_bilingual("brand")

    print("Normalizing + downloading media…")
    norm_posts = [normalize_item(p, "post") for p in posts]
    norm_pages = [normalize_item(p, "page") for p in pages]
    norm_projects = [normalize_item(p, "project") for p in projects]
    norm_brands = [normalize_item(p, "brand") for p in brands]

    payload = {
        "source": BASE,
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "counts": {
            "posts": len(norm_posts),
            "pages": len(norm_pages),
            "projects": len(norm_projects),
            "brands": len(norm_brands),
        },
        "posts": norm_posts,
        "pages": norm_pages,
        "projects": norm_projects,
        "brands": norm_brands,
    }
    path = OUT / "api-content.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", path)
    print(json.dumps(payload["counts"], indent=2))


if __name__ == "__main__":
    main()
