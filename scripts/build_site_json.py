#!/usr/bin/env python3
# takes the messy api dump and makes one tidy site.json

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = json.loads((ROOT / "content" / "api-content.json").read_text(encoding="utf-8"))
OUT = ROOT / "content" / "site.json"


def page_by_slug(slug: str, lang: str):
    for p in API["pages"]:
        if p.get("slug") == slug and p.get("lang") == lang:
            return p
    # try without lang match
    for p in API["pages"]:
        if p.get("slug") == slug:
            return p
    return None


def find_page(*slugs: str, lang: str):
    for slug in slugs:
        hit = page_by_slug(slug, lang)
        if hit:
            return hit
    return None


def classify_types(item: dict) -> list[str]:
    blob = " ".join(
        [
            item.get("title") or "",
            json.dumps(item.get("fields") or {}, ensure_ascii=False),
            " ".join(c.get("slug", "") + " " + c.get("name", "") for c in item.get("categories") or []),
            item.get("url") or "",
        ]
    ).lower()
    types = []
    if any(x in blob for x in ("facade", "ფასად", "cladding", "ventilated")):
        types.append("facade")
    if any(x in blob for x in ("interior", "ინტერიერ", "bathroom", "bath")):
        types.append("interior")
    if not types:
        types.append("project")
    return types


def merge_bilingual(items: list[dict], kind: str) -> list[dict]:
    """Merge KA/EN rows that share similar identity."""
    by_key: dict[str, dict] = {}
    for item in items:
        slug = item.get("slug") or ""
        # strip language-ish differences by normalizing slug roots when possible
        key = slug
        entry = by_key.setdefault(
            key,
            {
                "slug": slug,
                "kind": kind,
                "title": {},
                "excerpt": {},
                "content": {},
                "fields": {"ka": {}, "en": {}},
                "urls": {},
                "images": [],
                "featured_image": None,
                "categories": [],
                "types": [],
                "date": item.get("date"),
            },
        )
        lang = item.get("lang") or "ka"
        entry["title"][lang] = item.get("title")
        entry["excerpt"][lang] = item.get("excerpt")
        entry["content"][lang] = item.get("content")
        entry["fields"][lang] = item.get("fields") or {}
        entry["urls"][lang] = item.get("url")
        if item.get("featured_image") and not entry["featured_image"]:
            entry["featured_image"] = item["featured_image"]
        for img in item.get("images") or []:
            if img not in entry["images"]:
                entry["images"].append(img)
        for c in item.get("categories") or []:
            if c not in entry["categories"]:
                entry["categories"].append(c)
        for t in classify_types(item):
            if t not in entry["types"]:
                entry["types"].append(t)
        if not entry.get("date"):
            entry["date"] = item.get("date")
    return sorted(by_key.values(), key=lambda x: (x.get("date") or ""), reverse=True)


def services_from_page(lang: str) -> dict:
    page = find_page("services", "servisebi", lang=lang) or find_page("services", lang="en")
    lists = (page or {}).get("content", {}).get("lists") or []
    headings = (page or {}).get("content", {}).get("headings") or []
    paras = (page or {}).get("content", {}).get("paragraphs") or []

    if lang == "en":
        return {
            "title": "Services",
            "intro": paras[:2],
            "interior": {
                "title": "IPS Interior",
                "items": [
                    {"title": "Interior consulting services", "points": lists[0] if len(lists) > 0 else []},
                    {"title": "Supply of interior materials", "points": lists[1] if len(lists) > 1 else []},
                ],
            },
            "facade": {
                "title": "IPS Facade",
                "items": [
                    {"title": "Facade design", "points": lists[2] if len(lists) > 2 else []},
                    {"title": "Supply of cladding materials", "points": lists[3] if len(lists) > 3 else []},
                    {"title": "Installation of cladding materials", "points": lists[4] if len(lists) > 4 else []},
                    {"title": "Supply of building materials", "points": lists[5] if len(lists) > 5 else []},
                ],
            },
            "raw": page.get("content") if page else {},
        }
    return {
        "title": "სერვისები",
        "intro": paras[:2],
        "interior": {
            "title": "IPS ინტერიერი",
            "items": [
                {"title": "ინტერიერის საკონსულტაციო მომსახურება", "points": lists[0] if len(lists) > 0 else []},
                {"title": "ინტერიერის მასალების მიწოდება", "points": lists[1] if len(lists) > 1 else []},
            ],
        },
        "facade": {
            "title": "IPS ფასადი",
            "items": [
                {"title": "ფასადის პროექტირება", "points": lists[2] if len(lists) > 2 else []},
                {"title": "საფასადე მასალების მიწოდება", "points": lists[3] if len(lists) > 3 else []},
                {"title": "საფასადე მასალების მონტაჟი", "points": lists[4] if len(lists) > 4 else []},
                {"title": "სამშენებლო მასალების მიწოდება", "points": lists[5] if len(lists) > 5 else []},
            ],
        },
        "raw": page.get("content") if page else {},
    }


def about_from_page(lang: str) -> dict:
    page = find_page("about-us", "chven-shesakheb", lang=lang)
    paras = (page or {}).get("content", {}).get("paragraphs") or []
    if lang == "en":
        return {
            "title": "About us",
            "mission_title": "Mission and Vision",
            "mission": paras[:3],
            "history": [
                {"year": "2016", "label": "IPS Interior", "text": next((p for p in paras if "2016" in p), "IPS Interior started in 2016")},
                {"year": "2019", "label": "IPS Facade", "text": next((p for p in paras if "2019" in p), "IPS Facade added in 2019")},
            ],
            "team_title": "Team and Career",
            "team": [p for p in paras if any(x in p.lower() for x in ("team", "career", "values", "vacanc"))][:4] or paras[3:7],
            "values": ["Mastery", "Confidence", "Curiosity", "Accuracy"],
            "csr_title": "Social Responsibility",
            "csr": [p for p in paras if "social" in p.lower() or "csr" in p.lower() or "responsibility" in p.lower()][:3] or paras[-4:-1],
            "contact": {
                "address": "Tbilisi, Chavchavadze Ave. 49d",
                "phone": "+995 32 225 24 24",
                "email": "info@ips.ge",
            },
            "raw": page.get("content") if page else {},
            "all_paragraphs": paras,
        }
    return {
        "title": "ჩვენ შესახებ",
        "mission_title": "მისია და ხედვა",
        "mission": paras[:3],
        "history": [
            {"year": "2016", "label": "IPS ინტერიერი", "text": next((p for p in paras if "2016" in p), "")},
            {"year": "2019", "label": "IPS ფასადი", "text": next((p for p in paras if "2019" in p), "")},
        ],
        "team_title": "გუნდი და კარიერა",
        "team": paras[5:9],
        "values": ["ოსტატობა", "თავდაჯერებულობა", "ცნობისმოყვარეობა", "სიზუსტე"],
        "csr_title": "სოციალური პასუხისმგებლობა",
        "csr": paras[9:12],
        "contact": {
            "address": "თბილისი, ჭავჭავაძის გამზ. 49დ",
            "phone": "+995 32 225 24 24",
            "email": "info@ips.ge",
        },
        "raw": page.get("content") if page else {},
        "all_paragraphs": paras,
    }


def main() -> None:
    projects = merge_bilingual(API["projects"], "project")
    brands = merge_bilingual(API["brands"], "brand")
    posts = merge_bilingual(API["posts"], "post")

    # brand categories from names/fields
    for b in brands:
        cats = []
        blob = json.dumps(b, ensure_ascii=False).lower()
        if "interior" in blob or "ინტერიერ" in blob:
            cats.append("interior")
        if "facade" in blob or "ფასად" in blob:
            cats.append("facade")
        # use type taxonomies
        for c in b.get("categories") or []:
            slug = (c.get("slug") or "") + " " + (c.get("name") or "")
            if "interior" in slug.lower() or "ინტერიერ" in slug.lower():
                if "interior" not in cats:
                    cats.append("interior")
            if "facade" in slug.lower() or "ფასად" in slug.lower():
                if "facade" not in cats:
                    cats.append("facade")
        if not cats:
            cats = ["facade"]
        b["types"] = cats
        b["name"] = b["title"].get("en") or b["title"].get("ka") or b["slug"]
        b["logo"] = b.get("featured_image")
        b["image"] = b.get("featured_image")

    for p in projects:
        p["image"] = p.get("featured_image") or (p.get("images") or [None])[0]
        # ensure title keys
        if not p["title"].get("en"):
            p["title"]["en"] = p["title"].get("ka")
        if not p["title"].get("ka"):
            p["title"]["ka"] = p["title"].get("en")

    for p in posts:
        p["image"] = p.get("featured_image") or (p.get("images") or [None])[0]
        if not p["title"].get("en"):
            p["title"]["en"] = p["title"].get("ka")
        if not p["title"].get("ka"):
            p["title"]["ka"] = p["title"].get("en")

    site = {
        "source": "https://ips.ge/",
        "generated_from": "content/api-content.json",
        "home": {
            "en": {
                "hero_title": "Building Services & Materials",
                "hero_lead": "Interior and facade — started with knowledge, finished with mastery.",
                "interior_title": "Interior materials and services",
                "interior_lead": "Selection | Delivery | Installation",
                "facade_title": "Facade materials and services",
                "facade_lead": "Projecting | Delivery | Installation",
                "cta_projects": "See our projects",
                "cta_video": "Watch the video",
            },
            "ka": {
                "hero_title": "სამშენებლო სერვისები & მასალები",
                "hero_lead": "ინტერიერი და ფასადი — ცოდნით დაწყებული, ოსტატობით დასრულებული.",
                "interior_title": "ინტერიერის მასალები და სერვისები",
                "interior_lead": "შერჩევა | მიწოდება | მონტაჟი",
                "facade_title": "საფასადო მასალები და სერვისები",
                "facade_lead": "პროექტირება | მიწოდება | მონტაჟი",
                "cta_projects": "ნახეთ ჩვენი პროექტები",
                "cta_video": "ნახეთ ვიდეო",
            },
        },
        "about": {"en": about_from_page("en"), "ka": about_from_page("ka")},
        "services": {"en": services_from_page("en"), "ka": services_from_page("ka")},
        "nav": {
            "ka": [
                {"label": "IPS ინტერიერი", "children": [
                    {"label": "სერვისები", "href": "services.html#interior"},
                    {"label": "ბრენდები", "href": "brands.html?type=interior"},
                    {"label": "პროექტები", "href": "projects.html?type=interior"},
                ]},
                {"label": "IPS ფასადი", "children": [
                    {"label": "სერვისები", "href": "services.html#facade"},
                    {"label": "ბრენდები", "href": "brands.html?type=facade"},
                    {"label": "პროექტები", "href": "projects.html?type=facade"},
                ]},
                {"label": "სერვისები", "href": "services.html"},
                {"label": "პროექტები", "children": [
                    {"label": "ყველა პროექტი", "href": "projects.html"},
                    {"label": "ინტერიერის პროექტები", "href": "projects.html?type=interior"},
                    {"label": "ფასადის პროექტები", "href": "projects.html?type=facade"},
                ]},
                {"label": "ჩვენ შესახებ", "children": [
                    {"label": "მისია და ისტორია", "href": "about.html#mission"},
                    {"label": "გუნდი და კარიერა", "href": "about.html#team"},
                    {"label": "სოციალური პასუხისმგებლობა", "href": "about.html#social"},
                    {"label": "კონტაქტი", "href": "about.html#contact"},
                ]},
                {"label": "სიახლე და ბლოგი", "href": "news.html"},
            ],
            "en": [
                {"label": "IPS Interior", "children": [
                    {"label": "Services", "href": "services.html#interior"},
                    {"label": "Brands", "href": "brands.html?type=interior"},
                    {"label": "Projects", "href": "projects.html?type=interior"},
                ]},
                {"label": "IPS Facade", "children": [
                    {"label": "Services", "href": "services.html#facade"},
                    {"label": "Brands", "href": "brands.html?type=facade"},
                    {"label": "Projects", "href": "projects.html?type=facade"},
                ]},
                {"label": "Services", "href": "services.html"},
                {"label": "Projects", "children": [
                    {"label": "All projects", "href": "projects.html"},
                    {"label": "Interior projects", "href": "projects.html?type=interior"},
                    {"label": "Facade projects", "href": "projects.html?type=facade"},
                ]},
                {"label": "About us", "children": [
                    {"label": "Mission & history", "href": "about.html#mission"},
                    {"label": "Team & career", "href": "about.html#team"},
                    {"label": "Social responsibility", "href": "about.html#social"},
                    {"label": "Contact", "href": "about.html#contact"},
                ]},
                {"label": "News & Blog", "href": "news.html"},
            ],
        },
        "footer_nav": {
            "ka": [
                {"label": "სერვისები", "href": "services.html"},
                {"label": "პროექტები", "href": "projects.html"},
                {"label": "ბრენდები", "href": "brands.html"},
                {"label": "ჩვენ შესახებ", "href": "about.html"},
                {"label": "სიახლე და ბლოგი", "href": "news.html"},
                {"label": "კონტაქტი", "href": "about.html#contact"},
            ],
            "en": [
                {"label": "Services", "href": "services.html"},
                {"label": "Projects", "href": "projects.html"},
                {"label": "Brands", "href": "brands.html"},
                {"label": "About us", "href": "about.html"},
                {"label": "News & Blog", "href": "news.html"},
                {"label": "Contact", "href": "about.html#contact"},
            ],
        },
        "projects": projects,
        "brands": brands,
        "posts": posts,
        "pages": API["pages"],
        "stats": {
            "projects": len(projects),
            "brands": len(brands),
            "posts": len(posts),
            "pages": len(API["pages"]),
        },
    }

    OUT.write_text(json.dumps(site, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", OUT)
    print(json.dumps(site["stats"], indent=2))


if __name__ == "__main__":
    main()
