#!/usr/bin/env python3
# merge ka/en duplicate projects + brands that share the same image

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "content" / "site.json"


def has_georgian(text: str) -> bool:
    return any("\u10a0" <= ch <= "\u10ff" for ch in (text or ""))


def merge_title(a: dict, b: dict) -> dict:
    out = {"ka": "", "en": ""}
    candidates = []
    for src in (a or {}, b or {}):
        for lang in ("ka", "en"):
            val = (src.get(lang) or "").strip()
            if val:
                candidates.append(val)

    ka_vals = [v for v in candidates if has_georgian(v)]
    en_vals = [v for v in candidates if not has_georgian(v)]
    out["ka"] = ka_vals[0] if ka_vals else (en_vals[0] if en_vals else "")
    out["en"] = en_vals[0] if en_vals else (ka_vals[0] if ka_vals else "")
    return out


def prefer_slug(a: str, b: str) -> str:
    """Prefer the cleaner latin slug."""
    a = a or ""
    b = b or ""
    score = lambda s: (
        0 if has_georgian(s.replace("-", "")) else 2,
        1 if any(c.isascii() and c.isalpha() for c in s) else 0,
        -len(s),
    )
    return a if score(a) >= score(b) else b


def merge_dict_lang(ba: dict, bb: dict) -> dict:
    merged = dict(ba or {})
    for key, val in (bb or {}).items():
        if not val:
            continue
        cur = merged.get(key)
        if not cur:
            merged[key] = val
            continue
        if key == "en":
            if isinstance(val, str) and not has_georgian(val):
                merged[key] = val
            elif isinstance(val, dict):
                merged[key] = val
        elif key == "ka":
            if isinstance(val, str) and has_georgian(val):
                merged[key] = val
            elif isinstance(val, dict):
                merged[key] = val
    return merged


def merge_items(items: list[dict], keyfn) -> list[dict]:
    groups: dict[str, dict] = {}
    order: list[str] = []

    for item in items:
        key = keyfn(item) or f"__slug__:{item.get('slug')}"
        if key not in groups:
            groups[key] = item
            order.append(key)
            continue

        base = groups[key]
        other = item

        chosen_slug = prefer_slug(base.get("slug", ""), other.get("slug", ""))
        if chosen_slug == other.get("slug") and other.get("slug") != base.get("slug"):
            # keep other as shell, pull base into it
            base, other = other, base
            groups[key] = base

        base["slug"] = chosen_slug
        base["title"] = merge_title(base.get("title") or {}, other.get("title") or {})

        for field in ("content", "excerpt", "fields"):
            if isinstance(base.get(field), dict) or isinstance(other.get(field), dict):
                base[field] = merge_dict_lang(base.get(field) or {}, other.get(field) or {})

        base["types"] = list(dict.fromkeys((base.get("types") or []) + (other.get("types") or [])))

        imgs: list[str] = []
        for src in (base.get("images") or []) + (other.get("images") or []):
            if src and src not in imgs:
                imgs.append(src)
        if imgs:
            base["images"] = imgs

        base["image"] = base.get("image") or other.get("image") or other.get("featured_image")
        base["featured_image"] = (
            base.get("featured_image") or other.get("featured_image") or base.get("image")
        )
        if other.get("logo") and not base.get("logo"):
            base["logo"] = other["logo"]

        urls = dict(base.get("urls") or {})
        for lk, lv in (other.get("urls") or {}).items():
            if lv and not urls.get(lk):
                urls[lk] = lv
        if urls:
            base["urls"] = urls

        # brand display name — prefer latin brand name
        name_a = str(base.get("name") or "")
        name_b = str(other.get("name") or "")
        if name_b and (not name_a or (has_georgian(name_a) and not has_georgian(name_b))):
            base["name"] = name_b
        elif not base.get("name"):
            base["name"] = base["title"].get("en") or base["title"].get("ka") or base.get("slug")

    return [groups[k] for k in order]


def main() -> None:
    site = json.loads(PATH.read_text(encoding="utf-8"))
    before_p = len(site["projects"])
    before_b = len(site["brands"])

    site["projects"] = merge_items(
        site["projects"],
        lambda p: (p.get("image") or p.get("featured_image") or "").replace("\\", "/"),
    )
    site["brands"] = merge_items(
        site["brands"],
        lambda b: (b.get("logo") or b.get("featured_image") or b.get("image") or "").replace("\\", "/"),
    )

    site["stats"] = {
        **(site.get("stats") or {}),
        "projects": len(site["projects"]),
        "brands": len(site["brands"]),
        "posts": len(site.get("posts") or []),
    }

    PATH.write_text(json.dumps(site, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"projects {before_p} -> {len(site['projects'])}")
    print(f"brands {before_b} -> {len(site['brands'])}")


if __name__ == "__main__":
    main()
