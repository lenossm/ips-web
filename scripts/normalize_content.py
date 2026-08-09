#!/usr/bin/env python3
# cleans up the scraped json into a ka/en content pack

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "content" / "site-content.json"
OUT = ROOT / "content" / "site.json"

SKIP_IMG = re.compile(
    r"(simbolo|symbol-|flags/|icon|logo|favicon|avatar|gravatar|wp-include|emoji)",
    re.I,
)

FIELD_LABELS = {
    "services": ("Services", "სერვისები"),
    "work_done": ("Work done", "შესრულებული სამუშაო", "შესრულებული სამუშაოები"),
    "materials": ("Materials used", "გამოყენებული მასალები"),
    "brands": ("Brands", "ბრენდები"),
}


def slug_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    parts = [p for p in path.split("/") if p and p != "en"]
    return parts[-1] if parts else "home"


def pick_image(images: list[str], local_map: dict[str, str], local_images: list[str]) -> str | None:
    # Prefer remote uploads that look like project photos, mapped to local when possible
    candidates = []
    for src in images:
        if SKIP_IMG.search(src):
            continue
        if "/wp-content/uploads/" not in src:
            continue
        candidates.append(src)
    for src in candidates:
        if src in local_map:
            return local_map[src]
        return src  # remote fallback
    for loc in local_images:
        if not SKIP_IMG.search(loc):
            return loc
    return candidates[0] if candidates else (local_images[0] if local_images else None)


def parse_fields_from_html(html: str) -> dict[str, str]:
    soup = BeautifulSoup(html or "", "lxml")
    text = soup.get_text("\n", strip=True)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    # drop chrome
    lines = [ln for ln in lines if ln not in ("Skip to content", "IPS") and "liquid-themes" not in ln.lower()]

    fields: dict[str, str] = {}
    order = ["services", "work_done", "materials", "brands"]
    label_to_key: dict[str, str] = {}
    for key, labels in FIELD_LABELS.items():
        for lab in labels:
            label_to_key[lab.lower()] = key

    i = 0
    while i < len(lines):
        key = label_to_key.get(lines[i].lower())
        if not key:
            i += 1
            continue
        buf: list[str] = []
        i += 1
        while i < len(lines):
            if lines[i].lower() in label_to_key or lines[i] in ("Projects", "პროექტები"):
                break
            if lines[i] in (",", "·", "|"):
                i += 1
                continue
            buf.append(lines[i].rstrip(","))
            i += 1
        val = ", ".join([b for b in buf if b and b.lower() not in label_to_key])
        val = re.sub(r"\s+,", ",", val)
        val = re.sub(r",\s*,", ",", val).strip(" ,")
        if val and key not in fields:
            fields[key] = val
    return fields


def classify_project(fields: dict[str, str], url: str, heading: str) -> list[str]:
    blob = " ".join(fields.values()).lower() + " " + heading.lower() + " " + url.lower()
    types: list[str] = []
    if any(x in blob for x in ("facade", "ფასად", "cladding", "ventilated")):
        types.append("facade")
    if any(x in blob for x in ("interior", "ინტერიერ", "bathroom", "bath")):
        types.append("interior")
    if not types:
        types.append("facade" if "facade" in url else "interior")
    return types


def brand_name(page: dict) -> str:
    h = page.get("heading") or page.get("title") or ""
    h = re.sub(r"\s*[-|–]\s*IPS.*$", "", h).strip()
    h = re.sub(r"^(IPS\s+)?(Interior|Facade|ინტერიერის|ფასადის)?\s*Brand(s)?\s*", "", h, flags=re.I)
    slug = slug_from_url(page["url"]).replace("-", " ").title()
    return h or slug


def page_by_path(pages: dict, path: str) -> dict | None:
    for base in ("https://ips.ge", "https://www.ips.ge"):
        for suffix in (path, path.rstrip("/") + "/", path.rstrip("/")):
            hit = pages.get(base + suffix)
            if hit:
                return hit
    return None


def clean_paras(paras: list[str]) -> list[str]:
    out = []
    skip = ("[email protected]", "Name and Surname", "e-mail", "Cover letter", "Upload your resume", "Send", "Application form")
    for p in paras:
        if any(s.lower() in p.lower() for s in skip):
            continue
        if "liquid-themes" in p.lower():
            continue
        if len(p) < 3:
            continue
        out.append(p)
    return out


def main() -> None:
    raw = json.loads(SRC.read_text(encoding="utf-8"))
    pages = raw["pages"]
    local_map = raw.get("image_map") or {}

    # --- Services EN/KA from lists ---
    svc_en = page_by_path(pages, "/en/services/") or {}
    svc_ka = page_by_path(pages, "/services/") or {}

    services = {
        "en": {
            "title": "Services",
            "interior": {
                "title": "IPS Interior",
                "items": [
                    {
                        "title": "Interior consulting services",
                        "points": (svc_en.get("lists") or [None])[0] or [],
                    },
                    {
                        "title": "Supply of interior materials",
                        "points": (svc_en.get("lists") or [None, None])[1] or [],
                    },
                ],
            },
            "facade": {
                "title": "IPS Facade",
                "items": [
                    {
                        "title": "Facade design",
                        "points": (svc_en.get("lists") or [None] * 3)[2] or [],
                    },
                    {
                        "title": "Supply of cladding materials",
                        "points": (svc_en.get("lists") or [None] * 4)[3] or [],
                    },
                    {
                        "title": "Installation of cladding materials",
                        "points": (svc_en.get("lists") or [None] * 5)[4] or [],
                    },
                    {
                        "title": "Supply of building materials",
                        "points": (svc_en.get("lists") or [None] * 6)[5] or [],
                    },
                ],
            },
        },
        "ka": {
            "title": "სერვისები",
            "interior": {
                "title": "IPS ინტერიერი",
                "items": [
                    {
                        "title": "ინტერიერის საკონსულტაციო მომსახურება",
                        "points": (svc_ka.get("lists") or [None])[0] or [],
                    },
                    {
                        "title": "ინტერიერის მასალების მიწოდება",
                        "points": (svc_ka.get("lists") or [None, None])[1] or [],
                    },
                ],
            },
            "facade": {
                "title": "IPS ფასადი",
                "items": [
                    {
                        "title": "ფასადის პროექტირება",
                        "points": (svc_ka.get("lists") or [None] * 3)[2] or [],
                    },
                    {
                        "title": "საფასადე მასალების მიწოდება",
                        "points": (svc_ka.get("lists") or [None] * 4)[3] or [],
                    },
                    {
                        "title": "საფასადე მასალების მონტაჟი",
                        "points": (svc_ka.get("lists") or [None] * 5)[4] or [],
                    },
                    {
                        "title": "სამშენებლო მასალების მიწოდება",
                        "points": (svc_ka.get("lists") or [None] * 6)[5] or [],
                    },
                ],
            },
        },
    }

    # --- About ---
    about_en = page_by_path(pages, "/en/about-us/") or {}
    about_ka = page_by_path(pages, "/about-us/") or {}
    about = {
        "en": {
            "title": "About us",
            "mission_title": "Mission and Vision",
            "mission": clean_paras(about_en.get("paragraphs") or [])[:3],
            "history": [
                {"year": "2016", "label": "IPS Interior", "text": "The company IPS started its activity in the direction of interior in 2016"},
                {"year": "2019", "label": "IPS Facade", "text": "In 2019, the direction of facades was also added"},
            ],
            "team_title": "Team and Career",
            "team": clean_paras(about_en.get("paragraphs") or [])[5:8],
            "values": ["Mastery", "Confidence", "Curiosity", "Accuracy"],
            "csr_title": "Social Responsibility",
            "csr": clean_paras(about_en.get("paragraphs") or [])[8:10],
            "contact": {
                "address": "Tbilisi, Chavchavadze Ave. 49d",
                "phone": "+995 32 225 24 24",
                "email": "info@ips.ge",
            },
        },
        "ka": {
            "title": "ჩვენ შესახებ",
            "mission_title": "მისია და ხედვა",
            "mission": clean_paras(about_ka.get("paragraphs") or [])[:3],
            "history": [
                {"year": "2016", "label": "IPS ინტერიერი", "text": "კომპანია IPS-მა ინტერიერის მიმართულებით 2016 წელს დაიწყო საქმიანობა"},
                {"year": "2019", "label": "IPS ფასადი", "text": "2019 წელს შეემატა ფასადების მიმართულებაც"},
            ],
            "team_title": "გუნდი და კარიერა",
            "team": clean_paras(about_ka.get("paragraphs") or [])[5:8],
            "values": ["ოსტატობა", "თავდაჯერებულობა", "ცნობისმოყვარეობა", "სიზუსტე"],
            "csr_title": "სოციალური პასუხისმგებლობა",
            "csr": clean_paras(about_ka.get("paragraphs") or [])[8:10],
            "contact": {
                "address": "თბილისი, ჭავჭავაძის გამზ. 49დ",
                "phone": "+995 32 225 24 24",
                "email": "info@ips.ge",
            },
        },
    }

    # --- Home copy ---
    home = {
        "en": {
            "hero_title": "Building Services & Materials",
            "hero_lead": "Interior and facade — started with knowledge, finished with mastery.",
            "interior_title": "Interior materials and services",
            "interior_lead": "Selection | Delivery | Installation",
            "facade_title": "Facade materials and services",
            "facade_lead": "Projecting | Delivery | Installation",
            "cta_video": "Watch the video",
            "cta_projects": "See our projects",
        },
        "ka": {
            "hero_title": "სამშენებლო სერვისები & მასალები",
            "hero_lead": "ინტერიერი და ფასადი — ცოდნით დაწყებული, ოსტატობით დასრულებული.",
            "interior_title": "ინტერიერის მასალები და სერვისები",
            "interior_lead": "შერჩევა | მიწოდება | მონტაჟი",
            "facade_title": "საფასადო მასალები და სერვისები",
            "facade_lead": "პროექტირება | მიწოდება | მონტაჟი",
            "cta_video": "ნახეთ ვიდეო",
            "cta_projects": "ნახეთ ჩვენი პროექტები",
        },
    }

    # --- Projects ---
    projects: list[dict] = []
    by_slug: dict[str, dict] = {}

    for url, page in (raw.get("projects") or {}).items():
        slug = slug_from_url(url)
        lang = "en" if "/en/" in url else "ka"
        fields = parse_fields_from_html(page.get("html") or "")
        image = pick_image(page.get("images") or [], local_map, page.get("local_images") or [])
        types = classify_project(fields, url, page.get("heading") or "")
        entry = by_slug.setdefault(
            slug,
            {
                "slug": slug,
                "types": types,
                "image": image,
                "images": [],
                "urls": {},
                "title": {},
                "fields": {"en": {}, "ka": {}},
            },
        )
        entry["urls"][lang] = url
        entry["title"][lang] = page.get("heading") or slug
        entry["fields"][lang] = fields
        if image and not entry.get("image"):
            entry["image"] = image
        # collect photo-like images
        for src in page.get("images") or []:
            if SKIP_IMG.search(src):
                continue
            loc = local_map.get(src, src)
            if loc not in entry["images"]:
                entry["images"].append(loc)
        # merge types
        for t in types:
            if t not in entry["types"]:
                entry["types"].append(t)

    # Prefer EN title as default display
    for slug, entry in by_slug.items():
        if not entry["title"].get("en") and entry["title"].get("ka"):
            entry["title"]["en"] = entry["title"]["ka"]
        if not entry["title"].get("ka") and entry["title"].get("en"):
            entry["title"]["ka"] = entry["title"]["en"]
        projects.append(entry)

    projects.sort(key=lambda p: (p["title"].get("en") or p["slug"]).lower())

    # --- Brands ---
    brands: list[dict] = []
    brand_by_slug: dict[str, dict] = {}
    interior_brand_slugs = set()
    facade_brand_slugs = set()

    # detect from listing pages which brands appear
    for path, bucket in [
        ("/interior-brands/", interior_brand_slugs),
        ("/en/ips-interior-brands/", interior_brand_slugs),
        ("/facade-brands/", facade_brand_slugs),
        ("/en/ips-facade-brands/", facade_brand_slugs),
    ]:
        pg = page_by_path(pages, path)
        if not pg:
            continue
        html = pg.get("html") or ""
        for m in re.finditer(r"https://ips\.ge/(?:en/)?brand/([a-z0-9\-]+)/", html):
            bucket.add(m.group(1))

    for url, page in (raw.get("brands") or {}).items():
        slug = slug_from_url(url)
        lang = "en" if "/en/" in url else "ka"
        logo = pick_image(page.get("images") or [], local_map, page.get("local_images") or [])
        # prefer logo-looking images for brands
        for src in page.get("images") or []:
            if "logo" in src.lower() or "ips.ge_" in src.lower():
                logo = local_map.get(src, src)
                break
        entry = brand_by_slug.setdefault(
            slug,
            {
                "slug": slug,
                "name": brand_name(page),
                "logo": logo,
                "categories": [],
                "urls": {},
                "description": {},
            },
        )
        entry["urls"][lang] = url
        paras = clean_paras(page.get("paragraphs") or [])
        if paras:
            entry["description"][lang] = paras[0]
        if slug in interior_brand_slugs and "interior" not in entry["categories"]:
            entry["categories"].append("interior")
        if slug in facade_brand_slugs and "facade" not in entry["categories"]:
            entry["categories"].append("facade")
        if not entry["categories"]:
            # heuristic from sibling pages / description
            entry["categories"].append("facade")

    brands = sorted(brand_by_slug.values(), key=lambda b: b["name"].lower())

    # --- News ---
    news_pages = []
    for url, page in pages.items():
        if "/news" in url or "/blog" in url or "/get-to-know" in url:
            if url.rstrip("/").endswith(("news-blogs", "news-and-blogs")):
                continue
            news_pages.append(
                {
                    "url": url,
                    "lang": "en" if "/en/" in url else "ka",
                    "slug": slug_from_url(url),
                    "title": page.get("heading") or page.get("title"),
                    "excerpt": (clean_paras(page.get("paragraphs") or []) or [""])[0],
                    "image": pick_image(page.get("images") or [], local_map, page.get("local_images") or []),
                }
            )

    # --- Navigation (structured) ---
    nav = {
        "ka": [
            {
                "label": "IPS ინტერიერი",
                "children": [
                    {"label": "სერვისები", "href": "services.html#interior"},
                    {"label": "ბრენდები", "href": "brands.html?type=interior"},
                    {"label": "პროექტები", "href": "projects.html?type=interior"},
                ],
            },
            {
                "label": "IPS ფასადი",
                "children": [
                    {"label": "სერვისები", "href": "services.html#facade"},
                    {"label": "ბრენდები", "href": "brands.html?type=facade"},
                    {"label": "პროექტები", "href": "projects.html?type=facade"},
                ],
            },
            {"label": "სერვისები", "href": "services.html"},
            {
                "label": "პროექტები",
                "children": [
                    {"label": "ყველა პროექტი", "href": "projects.html"},
                    {"label": "ინტერიერის პროექტები", "href": "projects.html?type=interior"},
                    {"label": "ფასადის პროექტები", "href": "projects.html?type=facade"},
                ],
            },
            {
                "label": "ჩვენ შესახებ",
                "children": [
                    {"label": "მისია და ისტორია", "href": "about.html#mission"},
                    {"label": "გუნდი და კარიერა", "href": "about.html#team"},
                    {"label": "სოციალური პასუხისმგებლობა", "href": "about.html#social"},
                    {"label": "კონტაქტი", "href": "about.html#contact"},
                ],
            },
            {"label": "სიახლე და ბლოგი", "href": "news.html"},
        ],
        "en": [
            {
                "label": "IPS Interior",
                "children": [
                    {"label": "Services", "href": "services.html#interior"},
                    {"label": "Brands", "href": "brands.html?type=interior"},
                    {"label": "Projects", "href": "projects.html?type=interior"},
                ],
            },
            {
                "label": "IPS Facade",
                "children": [
                    {"label": "Services", "href": "services.html#facade"},
                    {"label": "Brands", "href": "brands.html?type=facade"},
                    {"label": "Projects", "href": "projects.html?type=facade"},
                ],
            },
            {"label": "Services", "href": "services.html"},
            {
                "label": "Projects",
                "children": [
                    {"label": "All projects", "href": "projects.html"},
                    {"label": "Interior projects", "href": "projects.html?type=interior"},
                    {"label": "Facade projects", "href": "projects.html?type=facade"},
                ],
            },
            {
                "label": "About us",
                "children": [
                    {"label": "Mission & history", "href": "about.html#mission"},
                    {"label": "Team & career", "href": "about.html#team"},
                    {"label": "Social responsibility", "href": "about.html#social"},
                    {"label": "Contact", "href": "about.html#contact"},
                ],
            },
            {"label": "News & Blog", "href": "news.html"},
        ],
    }

    site = {
        "source": "https://ips.ge/",
        "generated_from": "content/site-content.json",
        "home": home,
        "about": about,
        "services": services,
        "nav": nav,
        "projects": projects,
        "brands": brands,
        "news": news_pages,
        "stats": {
            "projects": len(projects),
            "brands": len(brands),
            "news": len(news_pages),
        },
    }

    OUT.write_text(json.dumps(site, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(json.dumps(site["stats"], indent=2))


if __name__ == "__main__":
    main()
