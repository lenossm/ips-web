#!/usr/bin/env python3
# builds the static preview pages from site.json
# run this whenever content or templates change

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))
OUT = ROOT / "preview"
OUT.mkdir(exist_ok=True)

CSS = "../assets/css/main.css"
PAGES_CSS = "../assets/css/pages.css"
JS = "../assets/js/main.js"
PAGES_JS = "../assets/js/preview-nav.js"
TRANS_JS = "../assets/js/transitions.js"


def e(text: str | None) -> str:
    return html.escape(text or "")


def img_src(path: str | None) -> str:
    if not path:
        return ""
    if str(path).startswith("http"):
        return path
    return "../" + str(path).replace("\\", "/")


def localize_href(href: str, lang: str) -> str:
    if lang != "en":
        return href
    mapping = {
        "services.html": "services-en.html",
        "projects.html": "projects-en.html",
        "brands.html": "brands-en.html",
        "about.html": "about-en.html",
        "news.html": "news-en.html",
        "index.html": "index-en.html",
    }
    for src, dst in mapping.items():
        if href.startswith(src):
            return href.replace(src, dst, 1)
    if href.startswith("project-") and not href.endswith("-en.html"):
        return href.replace(".html", "-en.html")
    if href.startswith("brand-") and not href.endswith("-en.html"):
        return href.replace(".html", "-en.html")
    if href.startswith("post-") and not href.endswith("-en.html"):
        return href.replace(".html", "-en.html")
    return href


def nav_html(lang: str) -> str:
    lis = []
    for item in SITE["nav"][lang]:
        if item.get("children"):
            kids = "".join(
                f'<li><a href="{e(localize_href(c["href"], lang))}">{e(c["label"])}</a></li>'
                for c in item["children"]
            )
            lis.append(
                f'<li class="has-children"><a href="#">{e(item["label"])}</a><ul class="sub-menu">{kids}</ul></li>'
            )
        else:
            lis.append(
                f'<li><a href="{e(localize_href(item["href"], lang))}">{e(item["label"])}</a></li>'
            )
    return '<ul class="nav-list">' + "".join(lis) + "</ul>"


def footer_nav_html(lang: str) -> str:
    items = SITE.get("footer_nav", {}).get(lang) or []
    return '<ul class="footer-nav">' + "".join(
        f'<li><a href="{e(localize_href(i["href"], lang))}">{e(i["label"])}</a></li>' for i in items
    ) + "</ul>"


def header(lang: str, active: str = "") -> str:
    switch_ka = {
        "home": "index.html",
        "services": "services.html",
        "projects": "projects.html",
        "brands": "brands.html",
        "about": "about.html",
        "news": "news.html",
    }
    switch_en = {
        "home": "index-en.html",
        "services": "services-en.html",
        "projects": "projects-en.html",
        "brands": "brands-en.html",
        "about": "about-en.html",
        "news": "news-en.html",
    }
    return f"""
<div class="scroll-progress" data-scroll-progress aria-hidden="true"></div>
<div class="page-transition" data-page-transition aria-hidden="true"></div>
<header class="site-header" data-header>
  <div class="site-header__inner">
    <a class="brand" href="{'index.html' if lang=='ka' else 'index-en.html'}" aria-label="IPS">
      <span class="brand__mark" aria-hidden="true">
        <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="4" y="4" width="40" height="40" stroke="currentColor" stroke-width="2"/>
          <path d="M14 34V14h8.2c4.4 0 7.2 2.4 7.2 6.2 0 3.8-2.8 6.2-7.2 6.2H18.5V34H14zm4.5-11.4h3.4c2.1 0 3.3-1 3.3-2.6s-1.2-2.6-3.3-2.6h-3.4v5.2zM36 14v4h-6.5v16H25V14h11z" fill="currentColor"/>
        </svg>
      </span>
      <span class="brand__text">IPS</span>
    </a>
    <nav class="site-nav" aria-label="Menu">{nav_html(lang)}</nav>
    <div class="site-header__actions">
      <div class="lang-switch" aria-label="Language">
        <a class="lang-switch__link{' is-active' if lang=='ka' else ''}" href="{switch_ka.get(active,'index.html')}" lang="ka">ქარ</a>
        <span class="lang-switch__sep" aria-hidden="true"></span>
        <a class="lang-switch__link{' is-active' if lang=='en' else ''}" href="{switch_en.get(active,'index-en.html')}" lang="en">EN</a>
      </div>
      <button class="nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="mobile-nav">
        <span class="nav-toggle__label">{'მენიუ' if lang=='ka' else 'Menu'}</span>
        <span class="nav-toggle__icon" aria-hidden="true"><span></span><span></span></span>
      </button>
    </div>
  </div>
  <div class="mobile-nav" id="mobile-nav" data-mobile-nav hidden>{nav_html(lang)}</div>
</header>
"""


def footer(lang: str) -> str:
    c = SITE["about"][lang]["contact"]
    return f"""
<footer class="site-footer">
  <div class="site-footer__grain" aria-hidden="true"></div>
  <div class="container site-footer__grid">
    <div class="site-footer__brand">
      <p class="site-footer__logo">IPS</p>
      <p class="site-footer__tag">{e(SITE['home'][lang]['hero_title'])}</p>
      <p class="site-footer__since">{'2016-დან' if lang=='ka' else 'Since 2016'}</p>
    </div>
    <div class="site-footer__nav">
      <p class="site-footer__label">{'ნავიგაცია' if lang=='ka' else 'Navigate'}</p>
      {footer_nav_html(lang)}
    </div>
    <div class="site-footer__contact">
      <p class="site-footer__label">{'კონტაქტი' if lang=='ka' else 'Contact'}</p>
      <address class="site-footer__address">
        {e(c['address'])}<br>
        <a href="tel:+995322252424">{e(c['phone'])}</a><br>
        <a href="mailto:{e(c['email'])}">{e(c['email'])}</a>
      </address>
    </div>
    <div class="site-footer__social">
      <p class="site-footer__label">{'სოციალური მედია' if lang=='ka' else 'Social media'}</p>
      <ul class="social-list">
        <li><a href="https://www.facebook.com/ips.ge" target="_blank" rel="noopener">Facebook</a></li>
        <li><a href="https://www.instagram.com/ips.ge" target="_blank" rel="noopener">Instagram</a></li>
        <li><a href="https://www.linkedin.com/company/ips-interior-facade" target="_blank" rel="noopener">LinkedIn</a></li>
      </ul>
    </div>
  </div>
  <div class="container site-footer__bottom">
    <p>&copy; 2026 IPS. {'ყველა უფლება დაცულია' if lang=='ka' else 'All rights reserved'}</p>
  </div>
</footer>
<script src="{JS}"></script>
<script src="{PAGES_JS}"></script>
<script src="{TRANS_JS}"></script>
"""


def shell(lang: str, title: str, body: str, active: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{e(title)} — IPS</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Georgian:wght@400;500;600;700&family=Noto+Serif+Georgian:wght@500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{CSS}">
  <link rel="stylesheet" href="{PAGES_CSS}">
</head>
<body class="lang-{lang}">
{header(lang, active)}
<main id="main" class="site-main">
{body}
</main>
{footer(lang)}
</body>
</html>
"""


def rewrite_rich_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    # point images to local when possible later; keep remote ok
    html_out = raw_html
    html_out = re.sub(r'src="(https://ips\\.ge/wp-content/uploads/[^"]+)"', r'src="\1"', html_out)
    # strip liquid warning
    html_out = html_out.replace(
        "This site is registered on portal.liquid-themes.com as a development site. Switch to production mode to remove this warning.",
        "",
    )
    return html_out


def content_for(item: dict, lang: str) -> dict:
    return (item.get("content") or {}).get(lang) or (item.get("content") or {}).get("en") or (item.get("content") or {}).get("ka") or {}


def has_georgian(text: str) -> bool:
    return any("\u10a0" <= ch <= "\u10ff" for ch in (text or ""))


def title_for(item: dict, lang: str, fallback: bool = True) -> str:
    titles = item.get("title") or {}
    ka = (titles.get("ka") or "").strip()
    en = (titles.get("en") or "").strip()
    ka_best = ka if has_georgian(ka) else (en if has_georgian(en) else ka)
    en_best = en if en and not has_georgian(en) else (ka if ka and not has_georgian(ka) else en)

    if lang == "ka":
        if ka_best:
            return ka_best
        return en_best if fallback else ""
    if en_best:
        return en_best
    return ka_best if fallback else ""


def project_card(p: dict, lang: str) -> str:
    title = title_for(p, lang)
    href = f"project-{p['slug']}.html" if lang == "ka" else f"project-{p['slug']}-en.html"
    src = img_src(p.get("image") or p.get("featured_image"))
    media = f'<img src="{e(src)}" alt="{e(title)}" loading="lazy">' if src else '<span class="project-tile__placeholder"></span>'
    types = " ".join(p.get("types") or [])
    return f"""
<a class="project-tile" href="{href}" data-types="{e(types)}">
  <span class="project-tile__media">{media}</span>
  <span class="project-tile__meta">
    <span class="project-tile__type">{e(', '.join(p.get('types') or []))}</span>
    <span class="project-tile__title">{e(title)}</span>
  </span>
</a>"""


def brand_card(b: dict, lang: str) -> str:
    href = f"brand-{b['slug']}.html" if lang == "ka" else f"brand-{b['slug']}-en.html"
    src = img_src(b.get("logo") or b.get("featured_image"))
    img = f'<img src="{e(src)}" alt="{e(b.get("name") or "")}" loading="lazy">' if src else ""
    cats = " ".join(b.get("types") or [])
    return f"""
<a class="brand-card" href="{href}" data-types="{e(cats)}">
  <div class="brand-card__logo">{img}</div>
  <h3 class="brand-card__name">{e(b.get('name') or title_for(b, lang))}</h3>
  <p class="brand-card__cats">{e(', '.join(b.get('types') or []))}</p>
</a>"""


def post_card(p: dict, lang: str) -> str:
    title = title_for(p, lang)
    if not title:
        return ""
    href = f"post-{p['slug']}.html" if lang == "ka" else f"post-{p['slug']}-en.html"
    excerpt = (p.get("excerpt") or {}).get(lang) or (p.get("excerpt") or {}).get("en") or ""
    src = img_src(p.get("image") or p.get("featured_image"))
    media = f'<img src="{e(src)}" alt="">' if src else ""
    date = (p.get("date") or "")[:10]
    return f"""
<article class="post-card">
  <a class="post-card__media" href="{href}">{media}</a>
  <div class="post-card__body">
    <p class="post-date">{e(date)}</p>
    <h2 class="post-card__title"><a href="{href}">{e(title)}</a></h2>
    <p>{e(excerpt)}</p>
    <a class="text-link" href="{href}">{'ვრცლად' if lang=='ka' else 'Read more'}</a>
  </div>
</article>"""


def contact_form(lang: str) -> str:
    labels = {
        "ka": {
            "name": "სახელი და გვარი",
            "email": "ელ-ფოსტა",
            "phone": "ტელეფონი",
            "message": "შეტყობინება",
            "send": "გაგზავნა",
            "ok": "შეტყობინება გაიგზავნა.",
            "err": "გაგზავნა ვერ მოხერხდა. სცადეთ თავიდან ან მოგვწერეთ info@ips.ge",
        },
        "en": {
            "name": "Full name",
            "email": "Email",
            "phone": "Phone",
            "message": "Message",
            "send": "Send message",
            "ok": "Message sent successfully.",
            "err": "Could not send. Please try again or email info@ips.ge",
        },
    }[lang]
    return f"""
<form class="contact-form" data-contact-form action="https://formsubmit.co/ajax/info@ips.ge" method="POST">
  <input type="hidden" name="_subject" value="IPS website contact">
  <input type="hidden" name="_template" value="table">
  <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off">
  <div class="contact-form__row">
    <label>{e(labels['name'])}<input name="name" required autocomplete="name"></label>
    <label>{e(labels['email'])}<input type="email" name="email" required autocomplete="email"></label>
  </div>
  <label>{e(labels['phone'])}<input type="tel" name="phone" autocomplete="tel"></label>
  <label>{e(labels['message'])}<textarea name="message" required></textarea></label>
  <button class="btn btn--metal" type="submit">{e(labels['send'])}</button>
  <p class="contact-form__status" data-form-status data-ok="{e(labels['ok'])}" data-err="{e(labels['err'])}" aria-live="polite"></p>
</form>
"""


def home_page(lang: str) -> str:
    h = SITE["home"][lang]
    a = SITE["about"][lang]
    featured = SITE["projects"][:8]
    posts = [p for p in SITE.get("posts", []) if title_for(p, lang, fallback=False)][:3]
    projects_href = localize_href("projects.html", lang)
    about_href = localize_href("about.html", lang)
    services_href = localize_href("services.html", lang)
    news_href = localize_href("news.html", lang)
    body = f"""
<section class="hero" data-reveal="hero">
  <div class="hero__media" aria-hidden="true"><div class="hero__image"></div><div class="hero__veil"></div><div class="hero__grid"></div></div>
  <div class="hero__frame" aria-hidden="true"></div>
  <div class="hero__content">
    <p class="hero__brand">IPS</p>
    <div class="hero__rule" aria-hidden="true"></div>
    <h1 class="hero__title" data-reveal-item>{e(h['hero_title'])}</h1>
    <p class="hero__lead" data-reveal-item>{e(h['hero_lead'])}</p>
    <div class="hero__actions" data-reveal-item>
      <a class="btn btn--light" href="{projects_href}">{e(h['cta_projects'])}</a>
      <a class="btn btn--ghost" href="{services_href}">{'სერვისები' if lang=='ka' else 'Services'}</a>
    </div>
  </div>
  <div class="hero__meta" aria-hidden="true"><span>{'თბილისი' if lang=='ka' else 'Tbilisi'}</span><span>2016</span></div>
  <div class="hero__scroll" aria-hidden="true"><span></span></div>
</section>

<section class="directions" id="directions">
  <div class="directions__pair">
    <a class="direction direction--interior" href="{services_href}#interior" data-reveal>
      <span class="direction__bg"></span><span class="direction__shade"></span>
      <span class="direction__body">
        <span class="direction__eyebrow">{'IPS ინტერიერი' if lang=='ka' else 'IPS Interior'}</span>
        <span class="direction__title">{e(h['interior_title'])}</span>
        <span class="direction__lead">{e(h['interior_lead'])}</span>
        <span class="direction__cta">{'სერვისები' if lang=='ka' else 'Services'}</span>
      </span>
    </a>
    <a class="direction direction--facade" href="{services_href}#facade" data-reveal>
      <span class="direction__bg"></span><span class="direction__shade"></span>
      <span class="direction__body">
        <span class="direction__eyebrow">{'IPS ფასადი' if lang=='ka' else 'IPS Facade'}</span>
        <span class="direction__title">{e(h['facade_title'])}</span>
        <span class="direction__lead">{e(h['facade_lead'])}</span>
        <span class="direction__cta">{'სერვისები' if lang=='ka' else 'Services'}</span>
      </span>
    </a>
  </div>
</section>

<section class="mission" data-reveal>
  <div class="container mission__grid">
    <div class="mission__copy">
      <h2 class="mission__title">{e((a.get('mission') or [a.get('mission_title')])[-1] if a.get('mission') else a.get('mission_title'))}</h2>
      <p class="mission__text">{e(' '.join((a.get('mission') or [])[:2]))}</p>
      <a class="text-link" href="{about_href}">{e(a['title'])}</a>
    </div>
    <ul class="values">
      {''.join(f'<li class="values__item" data-reveal-item><span>0{i}</span>{e(v)}</li>' for i,v in enumerate(a.get('values') or [],1))}
    </ul>
  </div>
</section>

<section class="projects-strip" data-reveal>
  <div class="container projects-strip__head">
    <h2 class="section-title">{'შერჩეული პროექტები' if lang=='ka' else 'Selected projects'}</h2>
    <p class="section-lead">{len(SITE['projects'])} {'პროექტი' if lang=='ka' else 'projects'}</p>
    <a class="text-link" href="{projects_href}">{'ყველა პროექტი' if lang=='ka' else 'All projects'}</a>
  </div>
  <div class="container projects-strip__track">{''.join(project_card(p, lang) for p in featured)}</div>
</section>

<section class="news-strip" data-reveal>
  <div class="container projects-strip__head">
    <h2 class="section-title">{'სიახლე და ბლოგი' if lang=='ka' else 'News & Blog'}</h2>
    <a class="text-link" href="{news_href}">{'ყველა' if lang=='ka' else 'View all'}</a>
  </div>
  <div class="container post-list">{''.join(post_card(p, lang) for p in posts)}</div>
</section>

<section class="cta-band" id="contact" data-reveal>
  <div class="container cta-band__inner">
    <h2 class="cta-band__title">{'დაგვიკავშირდით' if lang=='ka' else 'Get in touch'}</h2>
    <p class="cta-band__text">{e(a['contact']['address'])} · {e(a['contact']['phone'])}</p>
    {contact_form(lang)}
  </div>
</section>
"""
    return shell(lang, "IPS", body, "home")


def services_page(lang: str) -> str:
    s = SITE["services"][lang]
    blocks = []
    for key in ("interior", "facade"):
        block = s[key]
        items = "".join(
            f"<article class='service-card'><h3>{e(item['title'])}</h3><ul>{''.join(f'<li>{e(pt)}</li>' for pt in item.get('points') or [])}</ul></article>"
            for item in block.get("items") or []
        )
        blocks.append(f"<section class='content-section' id='{key}' data-reveal><div class='container'><h2 class='section-title'>{e(block['title'])}</h2><div class='service-grid'>{items}</div></div></section>")
    raw = rewrite_rich_html((s.get("raw") or {}).get("html") or "")
    extra = f"<section class='content-section'><div class='container'><div class='rich-content'>{raw}</div></div></section>" if raw else ""
    intro = "".join(f"<p class='section-lead' style='margin:0 auto 2rem;text-align:center'>{e(p)}</p>" for p in s.get("intro") or [])
    body = f"<div class='page-hero'><div class='container'><h1 class='page-hero__title'>{e(s['title'])}</h1>{intro}</div></div>" + "".join(blocks) + extra
    return shell(lang, s["title"], body, "services")


def projects_page(lang: str) -> str:
    title = "პროექტები" if lang == "ka" else "Projects"
    filters = "".join(
        f'<button type="button" data-filter="{f}" class="filter-bar__btn{" is-active" if f=="all" else ""}">{lab}</button>'
        for f, lab in [("all", "ყველა" if lang == "ka" else "All"), ("interior", "ინტერიერი" if lang == "ka" else "Interior"), ("facade", "ფასადი" if lang == "ka" else "Facade")]
    )
    grid = "".join(project_card(p, lang) for p in SITE["projects"])
    body = f"""
<div class="page-hero"><div class="container"><h1 class="page-hero__title">{e(title)}</h1>
<p class="page-hero__lead">{len(SITE['projects'])} {'პროექტი' if lang=='ka' else 'projects'}</p></div></div>
<div class="filter-bar container" data-filter-bar>{filters}</div>
<div class="container project-grid" data-filter-grid>{grid}</div>
"""
    return shell(lang, title, body, "projects")


def project_page(p: dict, lang: str) -> str:
    title = title_for(p, lang)
    fields = (p.get("fields") or {}).get(lang) or (p.get("fields") or {}).get("en") or (p.get("fields") or {}).get("ka") or {}
    labels = {
        "services": "სერვისები" if lang == "ka" else "Services",
        "work_done": "შესრულებული სამუშაო" if lang == "ka" else "Work done",
        "materials": "გამოყენებული მასალები" if lang == "ka" else "Materials used",
        "brands": "ბრენდები" if lang == "ka" else "Brands",
    }
    meta = "".join(
        f"<div class='meta-row'><dt>{e(labels[k])}</dt><dd>{e(v)}</dd></div>"
        for k, v in fields.items()
        if v and k in labels
    )
    # include any other tiny field details
    extra_fields = "".join(
        f"<div class='meta-row'><dt>{e(k.replace('_',' '))}</dt><dd>{e(str(v))}</dd></div>"
        for k, v in fields.items()
        if v and k not in labels and not str(k).startswith("_")
    )
    src = img_src(p.get("image") or p.get("featured_image"))
    hero = f'<img src="{e(src)}" alt="{e(title)}">' if src else '<div class="project-single__fallback"></div>'
    content = content_for(p, lang)
    rich = rewrite_rich_html(content.get("html") or "")
    gallery_imgs = [i for i in (p.get("images") or []) if i and i != (p.get("image") or p.get("featured_image"))][:9]
    gallery = ""
    if gallery_imgs:
        gallery = '<div class="container gallery">' + "".join(f'<img src="{e(img_src(g))}" alt="" loading="lazy">' for g in gallery_imgs) + "</div>"
    back = localize_href("projects.html", lang)
    body = f"""
<article class="project-single">
  <div class="project-single__hero">{hero}
    <div class="project-single__overlay"><div class="container">
      <p class="project-single__type">{e(', '.join(p.get('types') or []))}</p>
      <h1 class="project-single__title">{e(title)}</h1>
    </div></div>
  </div>
  <div class="container content-wrap">
    <a class="text-link detail-back" href="{back}">{'← პროექტები' if lang=='ka' else '← Projects'}</a>
    <dl class="meta-list">{meta}{extra_fields}</dl>
    <div class="rich-content">{rich}</div>
  </div>
  {gallery}
</article>
"""
    return shell(lang, title, body, "projects")


def brands_page(lang: str) -> str:
    title = "ბრენდები" if lang == "ka" else "Brands"
    filters = "".join(
        f'<button type="button" data-filter="{f}" class="filter-bar__btn{" is-active" if f=="all" else ""}">{lab}</button>'
        for f, lab in [("all", "ყველა" if lang == "ka" else "All"), ("interior", "ინტერიერი" if lang == "ka" else "Interior"), ("facade", "ფასადი" if lang == "ka" else "Facade")]
    )
    grid = "".join(brand_card(b, lang) for b in SITE["brands"])
    body = f"""
<div class="page-hero"><div class="container"><h1 class="page-hero__title">{e(title)}</h1>
<p class="page-hero__lead">{len(SITE['brands'])} {'ბრენდი' if lang=='ka' else 'brands'}</p></div></div>
<div class="filter-bar container" data-filter-bar>{filters}</div>
<div class="container brand-grid" data-filter-grid>{grid}</div>
"""
    return shell(lang, title, body, "brands")


def brand_page(b: dict, lang: str) -> str:
    title = b.get("name") or title_for(b, lang)
    content = content_for(b, lang)
    rich = rewrite_rich_html(content.get("html") or "")
    excerpt = (b.get("excerpt") or {}).get(lang) or ""
    src = img_src(b.get("logo") or b.get("featured_image"))
    logo = f'<img src="{e(src)}" alt="{e(title)}" style="max-height:4rem;margin:0 auto 2rem;filter:brightness(0) invert(1)">' if src else ""
    back = localize_href("brands.html", lang)
    body = f"""
<div class="page-hero"><div class="container"><h1 class="page-hero__title">{e(title)}</h1>
<p class="page-hero__lead">{e(', '.join(b.get('types') or []))}</p></div></div>
<div class="container content-wrap" style="text-align:center">
  <a class="text-link detail-back" href="{back}">{'← ბრენდები' if lang=='ka' else '← Brands'}</a>
  {logo}
  <p style="max-width:40rem;margin:0 auto 2rem;color:var(--fog)">{e(excerpt)}</p>
  <div class="rich-content" style="text-align:left">{rich}</div>
</div>
"""
    return shell(lang, title, body, "brands")


def about_page(lang: str) -> str:
    a = SITE["about"][lang]
    mission = "".join(f"<p>{e(p)}</p>" for p in a.get("mission") or [])
    history = "".join(f"<li><strong>{e(h['year'])}</strong><span>{e(h['label'])}</span><p>{e(h['text'])}</p></li>" for h in a.get("history") or [])
    team = "".join(f"<p>{e(p)}</p>" for p in a.get("team") or [])
    csr = "".join(f"<p>{e(p)}</p>" for p in a.get("csr") or [])
    all_paras = "".join(f"<p>{e(p)}</p>" for p in a.get("all_paragraphs") or [])
    values = "".join(f"<li class='values__item'><span>0{i}</span>{e(v)}</li>" for i, v in enumerate(a.get("values") or [], 1))
    raw = rewrite_rich_html((a.get("raw") or {}).get("html") or "")
    body = f"""
<div class="page-hero"><div class="container"><h1 class="page-hero__title">{e(a['title'])}</h1></div></div>
<section class="content-section" id="mission"><div class="container prose"><h2>{e(a['mission_title'])}</h2>{mission}
<h2>{'ისტორია' if lang=='ka' else 'History'}</h2><ol class="history-list">{history}</ol></div></section>
<section class="content-section" id="team"><div class="container prose"><h2>{e(a['team_title'])}</h2>{team}<ul class="values">{values}</ul></div></section>
<section class="content-section" id="social"><div class="container prose"><h2>{e(a['csr_title'])}</h2>{csr}</div></section>
<section class="content-section"><div class="container"><div class="rich-content">{raw or all_paras}</div></div></section>
<section class="content-section" id="contact"><div class="container">
  <h2 style="text-align:center">{'კონტაქტი' if lang=='ka' else 'Contact'}</h2>
  <address class="contact-block">
    <p>{e(a['contact']['address'])}</p>
    <p><a href="tel:+995322252424">{e(a['contact']['phone'])}</a></p>
    <p><a href="mailto:{e(a['contact']['email'])}">{e(a['contact']['email'])}</a></p>
  </address>
  {contact_form(lang)}
</div></section>
"""
    return shell(lang, a["title"], body, "about")


def news_page(lang: str) -> str:
    title = "სიახლე და ბლოგი" if lang == "ka" else "News & Blog"
    cards = [post_card(p, lang) for p in SITE.get("posts", []) if title_for(p, lang, fallback=True)]
    cards = [c for c in cards if c]
    body = f"""
<div class="page-hero"><div class="container"><h1 class="page-hero__title">{e(title)}</h1>
<p class="page-hero__lead">{len(cards)} {'სტატია' if lang=='ka' else 'articles'}</p></div></div>
<div class="container content-wrap post-list">{''.join(cards)}</div>
"""
    return shell(lang, title, body, "news")


def post_page(p: dict, lang: str) -> str:
    title = title_for(p, lang)
    if not title_for(p, lang, fallback=False):
        # still generate page but prefer available language content
        title = title_for(p, lang, fallback=True)
    content = content_for(p, lang)
    rich = rewrite_rich_html(content.get("html") or "")
    date = (p.get("date") or "")[:10]
    src = img_src(p.get("image") or p.get("featured_image"))
    featured = f'<div class="single-featured"><img src="{e(src)}" alt="{e(title)}"></div>' if src else ""
    back = localize_href("news.html", lang)
    body = f"""
<div class="page-hero"><div class="container">
  <p class="page-hero__meta">{e(date)}</p>
  <h1 class="page-hero__title">{e(title)}</h1>
</div></div>
{featured}
<div class="container content-wrap">
  <a class="text-link detail-back" href="{back}">{'← სიახლეები' if lang=='ka' else '← News'}</a>
  <div class="rich-content">{rich}</div>
</div>
"""
    return shell(lang, title, body, "news")


def main() -> None:
    pages = {
        "index.html": home_page("ka"),
        "index-en.html": home_page("en"),
        "services.html": services_page("ka"),
        "services-en.html": services_page("en"),
        "projects.html": projects_page("ka"),
        "projects-en.html": projects_page("en"),
        "brands.html": brands_page("ka"),
        "brands-en.html": brands_page("en"),
        "about.html": about_page("ka"),
        "about-en.html": about_page("en"),
        "news.html": news_page("ka"),
        "news-en.html": news_page("en"),
    }

    for p in SITE["projects"]:
        pages[f"project-{p['slug']}.html"] = project_page(p, "ka")
        pages[f"project-{p['slug']}-en.html"] = project_page(p, "en")

    for b in SITE["brands"]:
        pages[f"brand-{b['slug']}.html"] = brand_page(b, "ka")
        pages[f"brand-{b['slug']}-en.html"] = brand_page(b, "en")

    for p in SITE.get("posts", []):
        pages[f"post-{p['slug']}.html"] = post_page(p, "ka")
        pages[f"post-{p['slug']}-en.html"] = post_page(p, "en")

    for name, content in pages.items():
        (OUT / name).write_text(content, encoding="utf-8")

    print(f"Generated {len(pages)} pages → {OUT}")


if __name__ == "__main__":
    main()
