"""Builds the Nexvio site twice:
  dist/     deploy build for Cloudflare (clean URLs like /de/websites)
  preview/  same pages with explicit .html links, for the Claude preview
"""
import json, os, re, shutil, sys
from html import escape as e

sys.path.insert(0, os.path.dirname(__file__))
from legal import LEGAL, OPERATOR
from demos import DEMOS_PAGE
from content import SLUGS, UI, PROCESS, SERVICE_CARDS, HOME, SERVICES, CONTACT, EXAMPLES, BOOKING, BOOKING_URL

BASE = "https://www.nexvio.de"   # placeholder until the domain is bought
EMAIL = "hallo@nexvio.de"        # placeholder
ROOT = os.path.dirname(os.path.abspath(__file__))
LANGS = ["de", "en"]
KEYS = ["home", "ai", "web", "apps", "dash", "demos", "contact"]
SERVICE_KEYS = ["ai", "web", "apps", "dash"]
FONTS = "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap"

LOGO = ('<svg viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="9" fill="#6a46f5"/>'
        '<path d="M9 22V10l8 12V10" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M21 13l3 3-3 3" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')

ICONS = {
    "ai": '<path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/><circle cx="12" cy="12" r="3.2"/>',
    "web": '<rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M3 9h18M7 6.5h.01M10 6.5h.01"/>',
    "apps": '<path d="M8 9l-4 3 4 3M16 9l4 3-4 3M13.5 6l-3 12"/>',
    "dash": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
}


def icon(key):
    return (f'<div class="service-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[key]}</svg></div>')


TOP_SCRIPT = (
    "(function(){if(location.hash)return;"
    "try{history.scrollRestoration='manual'}catch(e){}"
    "var moved=false,t0=Date.now();"
    "function stop(){moved=true}"
    "['wheel','touchstart','touchmove','keydown','mousedown'].forEach(function(v){addEventListener(v,stop,{passive:true,once:true})});"
    "function top(){if(moved)return;if(scrollY||document.documentElement.scrollTop){scrollTo(0,0);document.documentElement.scrollTop=0}}"
    "top();addEventListener('DOMContentLoaded',top);addEventListener('load',top);addEventListener('pageshow',top);"
    "var iv=setInterval(function(){top();if(moved||Date.now()-t0>3000)clearInterval(iv)},100);"
    "})();")


def url(lang, key):
    slug = SLUGS[lang][key]
    return f"{BASE}/{lang}/{slug}" if slug else f"{BASE}/{lang}/"


class Linker:
    def __init__(self, clean):
        self.clean = clean

    def page(self, cur_lang, lang, key):
        slug = SLUGS[lang][key]
        if self.clean:
            target = slug if slug else "./"
            if lang != cur_lang:
                target = f"../{lang}/{slug}"
        else:
            target = f"{slug or 'index'}.html"
            if lang != cur_lang:
                target = f"../{lang}/{target}"
        return target

    def asset(self, name):
        return f"../assets/{name}"


def head(lang, key, title, desc, jsonld):
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{url(l, key)}">' for l in LANGS)
    alts += f'<link rel="alternate" hreflang="x-default" href="{url("de", key)}">'
    og_locale = "de_DE" if lang == "de" else "en_US"
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in jsonld)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url(lang, key)}">
{alts}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Nexvio">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url(lang, key)}">
<meta property="og:locale" content="{og_locale}">
<meta name="theme-color" content="#fbfafd">
<link rel="icon" href="data:image/svg+xml,{e(LOGO.replace('#', '%23').replace(' aria-hidden="true"', ' xmlns="http://www.w3.org/2000/svg"'))}">
<link rel="stylesheet" href="{{ASSET}}styles.css?v={{VER}}">
{ld}
</head>
<body>
"""


def header(L, lang, key):
    ui = UI[lang]
    cur = ' aria-current="page"'
    links = "".join(
        f'<a href="{L.page(lang, lang, k)}"{cur if k == key else ""}>{e(ui["nav"][k])}</a>'
        for k in ["home"] + SERVICE_KEYS + ["demos"])
    langsw = "".join(
        f'<a href="{L.page(lang, l, key)}" hreflang="{l}" lang="{l}" aria-current="{str(l == lang).lower()}">{l.upper()}</a>'
        for l in LANGS)
    mobile = "".join(f'<a href="{L.page(lang, lang, k)}">{e(ui["nav"][k])}</a>' for k in ["home"] + SERVICE_KEYS + ["demos"])
    mobile += f'<a href="{L.page(lang, lang, "contact")}">{e(ui["cta"])}</a>'
    return f"""<header class="site-header">
  <div class="wrap nav">
    <a class="brand" href="{L.page(lang, lang, 'home')}" aria-label="Nexvio">{LOGO}nexvio</a>
    <nav class="nav-links" aria-label="{e(ui['nav']['ai'])} …">{links}</nav>
    <div class="nav-actions">
      <div class="lang" role="group" aria-label="{ui['lang_label']}">{langsw}</div>
      <a class="btn btn-primary" href="{L.page(lang, lang, 'contact')}">{e(ui['cta'])}</a>
      <button type="button" class="menu-btn" id="menu-btn" aria-expanded="false" aria-controls="mobile-menu">{ui['menu']}</button>
    </div>
  </div>
  <div class="mobile-menu" id="mobile-menu" hidden><div class="wrap"><nav aria-label="{ui['menu']}">{mobile}</nav></div></div>
</header>
<main>
"""


def contact_href(L, lang):
    return L.page(lang, lang, "contact") + ("#termin" if BOOKING_URL else "")


def cta_band(L, lang):
    ui = UI[lang]
    return f"""<section class="cta-band">
  <div class="wrap section-inner">
    <div><h2>{e(ui['band_h2'])}</h2><p>{e(ui['band_p'])}</p></div>
    <a class="btn btn-primary" href="{contact_href(L, lang)}">{e(ui['band_btn'])}</a>
  </div>
</section>
"""


def footer(L, lang):
    ui = UI[lang]
    svc = "".join(f'<li><a href="{L.page(lang, lang, k)}">{e(ui["nav"][k])}</a></li>' for k in SERVICE_KEYS)
    contact = CONTACT[lang]
    return f"""</main>
<footer>
  <div class="wrap foot">
    <div><a class="brand" href="{L.page(lang, lang, 'home')}">{LOGO}nexvio</a><p>{e(ui['footer_tag'])}</p></div>
    <div><h2>{'Leistungen' if lang == 'de' else 'Services'}</h2><ul>{svc}</ul></div>
    <div><h2>{e(contact['eyebrow'])}</h2><ul><li><a href="{L.page(lang, lang, 'contact')}">{e(ui['cta'])}</a></li><li><span>{EMAIL}</span></li></ul></div>
  </div>
  <div class="wrap foot-base">
    <span>© 2026 Nexvio</span>
    <div><a href="{L.page(lang, lang, 'imprint')}">{e(ui['imprint'])}</a><a href="{L.page(lang, lang, 'privacy')}">{e(ui['privacy'])}</a></div>
  </div>
</footer>
<script src="{{ASSET}}main.js?v={{VER}}"></script>
</body>
</html>
"""


def process_section(lang):
    ui = UI[lang]
    steps = "".join(
        f'<li><span class="num">{i:02d}</span><h3>{e(h)}</h3><p>{e(p)}</p><span class="dur">{e(d)}</span></li>'
        for i, (h, p, d) in enumerate(PROCESS[lang], 1))
    return f"""<section class="band">
  <div class="wrap section-inner">
    <div class="section-head"><p class="eyebrow">{e(ui['process_eyebrow'])}</p><h2>{e(ui['process_h2'])}</h2><p>{e(ui['process_lead'])}</p></div>
    <ol class="steps">{steps}</ol>
  </div>
</section>
"""


def render_log(title, tag, rows, foot):
    items = "".join(
        f'<li class="log-row done"><span class="log-time">{e(t)}</span><span class="log-state"></span><span>{e(a)}<span class="detail">{e(b)}</span></span></li>'
        for t, a, b in rows)
    return (f'<div class="log"><div class="log-head"><span class="log-title">{e(title)}</span><span class="log-tag">{e(tag)}</span></div>'
            f'<ol class="log-list" data-anim>{items}</ol>'
            f'<div class="log-foot"><span>{e(foot[0])}</span><span><strong>{e(foot[1])}</strong> {e(foot[2])}</span></div></div>')


def render_kpi(x):
    tiles = "".join(f'<div class="kpi-tile"><span>{e(l)}</span><b>{e(v)}</b><small>{e(d)}</small></div>' for l, v, d in x["tiles"])
    top = 200
    n = len(x["values"])
    bars = "".join(
        f'<div class="bar{" now" if i == n - 1 else ""}" style="height:{v / top * 100:.1f}%" title="{e(m)}: {v}"></div>'
        for i, (m, v) in enumerate(zip(x["months"], x["values"])))
    return (f'<div class="log"><div class="log-head"><span class="log-title">{e(x["title"])}</span><span class="log-tag">{e(x["tag"])}</span></div>'
            f'<div class="kpi-tiles">{tiles}</div>'
            f'<div class="kpi-chart"><p class="kpi-label">{e(x["chart_label"])}</p>'
            f'<div class="bars" role="img" aria-label="{e(x["chart_label"])}"><span class="gl" style="bottom:50%"><i>100</i></span><span class="gl" style="bottom:100%"><i>200</i></span>{bars}</div>'
            f'<div class="bar-axis"><span>{e(x["months"][0])}</span><span>{e(x["months"][-1])}</span></div></div>'
            f'<div class="log-foot"><span>{e(x["foot"][0])}</span><span><strong>{e(x["foot"][1])}</strong> {e(x["foot"][2])}</span></div></div>')


def render_design(x):
    nav = "".join(f"<span>{e(n)}</span>" for n in x["nav"])
    sw = "".join(
        f'<button type="button" class="sw sw{i}" data-v="{i}" aria-pressed="{str(i == 1).lower()}" aria-label="{e(x["variants_label"])}: {e(v)}"></button>'
        for i, v in enumerate(x["variants"], 1))
    site = (f'<div class="mnav"><b>{e(x["brand"])}</b><div>{nav}</div></div>'
            f'<div class="mhero"><p class="mh">{e(x["headline"])}</p><i class="ml"></i><i class="ml short"></i>'
            f'<span class="mbtn">{e(x["button"])}</span></div>'
            f'<div class="mcards"><div><i></i></div><div><i></i></div><div><i></i></div></div>')
    phone = (f'<div class="pnav"><b>{e(x["brand"])}</b><i></i></div>'
             f'<div class="mhero"><p class="mh">{e(x["headline"])}</p><i class="ml"></i><span class="mbtn">{e(x["button"])}</span></div>'
             f'<div class="pcard"></div><div class="pcard"></div>')
    return (f'<div class="log design-ex" data-v="1"><div class="log-head"><span class="log-title">{e(x["title"])}</span><span class="log-tag">{e(x["tag"])}</span></div>'
            f'<div class="mock"><div class="browser"><div class="bbar"><i></i><i></i><i></i><span>{e(x["url"])}</span></div>'
            f'<div class="msite">{site}</div></div><div class="phone"><div class="psite">{phone}</div></div></div>'
            f'<div class="variants"><span>{e(x["variants_label"])}</span><div role="group">{sw}</div></div>'
            f'<div class="log-foot"><span>{e(x["foot"][0])}</span><span><strong>{e(x["foot"][1])}</strong> {e(x["foot"][2])}</span></div></div>')


def render_example(x):
    if x["type"] == "kpi":
        return render_kpi(x)
    if x["type"] == "design":
        return render_design(x)
    return render_log(x["title"], x["tag"], x["rows"], x["foot"])


def org_ld(lang):
    return {"@context": "https://schema.org", "@type": "Organization", "name": "Nexvio", "url": f"{BASE}/{lang}/",
            "email": EMAIL, "description": HOME[lang]["desc"], "areaServed": ["DE", "AT", "CH"],
            "knowsLanguage": ["de", "en"]}


def page_home(L, lang):
    h = HOME[lang]; ui = UI[lang]
    jsonld = [org_ld(lang), {"@context": "https://schema.org", "@type": "WebSite", "name": "Nexvio", "url": f"{BASE}/{lang}/", "inLanguage": lang}]
    facts = "".join(f"<li>{e(f)}</li>" for f in h["facts"])
    cards = ""
    for k in SERVICE_KEYS:
        name, text, chips = SERVICE_CARDS[lang][k]
        chip_html = "".join(f"<li>{e(c)}</li>" for c in chips)
        cards += (f'<a class="service" href="{L.page(lang, lang, k)}">{icon(k)}<h3>{e(name)}</h3><p>{e(text)}</p>'
                  f'<ul class="chips">{chip_html}</ul><span class="more">{e(ui["more"])} →</span></a>')
    cases = "".join(
        f'<article class="case"><span class="industry">{e(i)}</span><h3>{e(t)}</h3><p>{e(p)}</p>'
        f'<div class="result"><b>{e(r)}</b><span>{e(s)}</span></div></article>'
        for i, t, p, r, s in h["cases"])
    body = f"""<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <p class="eyebrow">{e(h['eyebrow'])}</p>
      <h1>{e(h['h1a'])} <span class="accent">{e(h['h1b'])}</span></h1>
      <p class="lead">{e(h['lead'])}</p>
      <div class="hero-cta">
        <a class="btn btn-primary" href="{contact_href(L, lang)}">{e(h['cta1'])}</a>
        <a class="btn btn-ghost" href="#leistungen">{e(h['cta2'])}</a>
      </div>
      <ul class="facts">{facts}</ul>
    </div>
    {render_log(h['log_title'], h['log_tag'], h['log'], h['log_foot'])}
  </div>
</section>
<section class="band" id="leistungen">
  <div class="wrap section-inner">
    <div class="section-head"><p class="eyebrow">{e(h['svc_eyebrow'])}</p><h2>{e(h['svc_h2'])}</h2><p>{e(h['svc_lead'])}</p></div>
    <div class="services">{cards}</div>
  </div>
</section>
{process_section(lang)}
<section class="band tint">
  <div class="wrap section-inner">
    <div class="section-head"><p class="eyebrow">{e(h['cases_eyebrow'])}</p><h2>{e(h['cases_h2'])}</h2></div>
    <div class="cases">{cases}</div>
    <p class="note">{e(h['cases_note'])} <a href="{L.page(lang, lang, 'demos')}">{'Live-Demos ausprobieren' if lang == 'de' else 'Try the live demos'} →</a></p>
  </div>
</section>
{cta_band(L, lang)}"""
    return head(lang, "home", h["title"], h["desc"], jsonld) + header(L, lang, "home") + body + footer(L, lang)


def page_service(L, lang, key):
    s = SERVICES[lang][key]; ui = UI[lang]
    home_name = "Start" if lang == "de" else "Home"
    jsonld = [
        {"@context": "https://schema.org", "@type": "Service", "name": s["eyebrow"], "description": s["desc"],
         "provider": {"@type": "Organization", "name": "Nexvio", "url": f"{BASE}/{lang}/"}, "url": url(lang, key),
         "areaServed": ["DE", "AT", "CH"]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in s["faq"]]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": home_name, "item": url(lang, "home")},
            {"@type": "ListItem", "position": 2, "name": s["eyebrow"], "item": url(lang, key)}]},
    ]
    chips = "".join(f"<li>{e(c)}</li>" for c in s["chips"])
    tasks = "".join(f"<li><h3>{e(t)}</h3><p>{e(p)}</p></li>" for t, p in s["tasks"])
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in s["faq"])
    others = "".join(
        f'<a href="{L.page(lang, lang, k)}"><b>{e(SERVICE_CARDS[lang][k][0])}</b><span>{e(ui["more"])} →</span></a>'
        for k in SERVICE_KEYS if k != key)
    body = f"""<section class="hero sub">
  <div class="wrap hero-grid">
    <div class="page-hero">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="{L.page(lang, lang, 'home')}">{home_name}</a> / <span>{e(s['eyebrow'])}</span></nav>
      <p class="eyebrow">{e(s['eyebrow'])}</p>
      <h1>{e(s['h1'])}</h1>
      <p class="lead">{e(s['lead'])}</p>
      <ul class="chips">{chips}</ul>
      <div class="hero-cta"><a class="btn btn-primary" href="{contact_href(L, lang)}">{e(HOME[lang]['cta1'])}</a></div>
    </div>
    {render_example(EXAMPLES[lang][key])}
  </div>
</section>
<section class="band tint">
  <div class="wrap section-inner">
    <div class="section-head"><p class="eyebrow">{e(ui['tasks_eyebrow'])}</p><h2>{e(s['tasks_h2'])}</h2></div>
    <ul class="tasks">{tasks}</ul>
  </div>
</section>
{process_section(lang)}
<section class="band">
  <div class="wrap section-inner">
    <div class="section-head"><p class="eyebrow">{e(ui['faq_eyebrow'])}</p><h2>{e(ui['faq_h2'])}</h2></div>
    <div class="faq">{faq}</div>
  </div>
</section>
<section class="band tint">
  <div class="wrap section-inner" style="gap:24px">
    <p class="eyebrow">{e(ui['other_eyebrow'])}</p>
    <div class="others">{others}</div>
  </div>
</section>
{cta_band(L, lang)}"""
    return head(lang, key, s["title"], s["desc"], jsonld) + header(L, lang, key) + body + footer(L, lang)


def page_contact(L, lang):
    c = CONTACT[lang]; f = c["form"]
    jsonld = [{"@context": "https://schema.org", "@type": "ContactPage", "name": c["title"], "url": url(lang, "contact"),
               "mainEntity": org_ld(lang)}]
    steps = "".join(f'<li><span class="n">{i}</span><div><b>{e(h)}</b><p>{e(p)}</p></div></li>'
                    for i, (h, p) in enumerate(c["steps"], 1))
    opts = "".join(f"<option>{e(o)}</option>" for o in f["options"])
    booking = ""
    if BOOKING_URL:
        b = BOOKING[lang]
        joiner = "&" if "?" in BOOKING_URL else "?"
        src = BOOKING_URL + joiner + "gv=true&hl=" + lang
        open_url = BOOKING_URL + joiner + "hl=" + lang
        booking = f"""<section class="band tint" id="termin">
  <div class="wrap section-inner booking">
    <div class="section-head"><p class="eyebrow">{e(b['eyebrow'])}</p><h2>{e(b['h2'])}</h2><p>{e(b['p'])}</p></div>
    <div class="booking-frame" id="booking" data-src="{e(src)}">
      <div class="booking-gate">
        <p>{e(b['consent'])} <a href="{L.page(lang, lang, 'privacy')}">{e(b['privacy_link'])}</a></p>
        <div class="hero-cta">
          <button type="button" class="btn btn-primary" id="booking-load">{e(b['load'])}</button>
          <a class="btn btn-ghost" href="{e(open_url)}" target="_blank" rel="noopener">{e(b['open'])} ↗</a>
        </div>
      </div>
    </div>
    <p class="note">{e(b['or_form'])}</p>
  </div>
</section>
"""
    body = booking + f"""<section class="wrap contact">
  <div class="contact-info">
    <p class="eyebrow">{e(c['eyebrow'])}</p>
    <h1>{e(c['h1'])}</h1>
    <p class="lead">{e(c['lead'])}</p>
    <div class="mail"><code id="mail-addr">{EMAIL}</code><button type="button" class="copy" id="copy-mail" data-done="{e(c['copied'])}">{e(c['copy'])}</button></div>
    <p class="next-h">{e(c['steps_h'])}</p>
    <ol class="next">{steps}</ol>
  </div>
  <form id="contact-form" novalidate data-missing="{e(f['missing'])}" data-preview="{e(f['preview'])}">
    <div class="field-row">
      <div class="field"><label for="f-name">{e(f['name'])}</label><input id="f-name" name="name" autocomplete="name" required></div>
      <div class="field"><label for="f-company">{e(f['company'])}</label><input id="f-company" name="company" autocomplete="organization"></div>
    </div>
    <div class="field"><label for="f-mail">{e(f['mail'])}</label><input id="f-mail" name="email" type="email" autocomplete="email" required></div>
    <div class="field"><label for="f-topic">{e(f['topic'])}</label><select id="f-topic" name="topic">{opts}</select></div>
    <div class="field"><label for="f-msg">{e(f['msg'])}</label><textarea id="f-msg" name="message" placeholder="{e(f['ph'])}"></textarea></div>
    <button type="submit" class="btn btn-primary">{e(f['send'])}</button>
    <p class="form-status" id="form-status" role="status" hidden></p>
  </form>
</section>
"""
    return head(lang, "contact", c["title"], c["desc"], jsonld) + header(L, lang, "contact") + body + footer(L, lang)


def page_demos(L, lang):
    d = DEMOS_PAGE[lang]
    jsonld = [{"@context": "https://schema.org", "@type": "WebPage", "name": d["title"], "url": url(lang, "demos"),
               "description": d["desc"], "inLanguage": lang}]
    jump = "".join(f'<li><a href="#{k}">{e(d["tabs"][k])}</a></li>' for k in ("assist", "portal", "dash"))
    def sec(k, tint):
        x = d[k]
        return f"""<section class="band{' tint' if tint else ''}" id="{k}">
  <div class="wrap section-inner">
    <div class="section-head"><p class="eyebrow">{e(d['tabs'][k])} <span class="dx-badge">{e(d['badge'])}</span></p><h2>{e(x['h2'])}</h2><p>{e(x['p'])}</p></div>
    <div class="dx-frame" id="demo-{k}"></div>
  </div>
</section>
"""
    data = json.dumps({"assist": d["assist"], "portal": d["portal"], "dash": d["dash"]}, ensure_ascii=False).replace("</", "<\\/")
    body = f"""<section class="wrap page-hero demos-hero">
  <p class="eyebrow">{e(d['eyebrow'])}</p>
  <h1>{e(d['h1'])}</h1>
  <p class="lead">{e(d['lead'])}</p>
  <ul class="chips dx-jump">{jump}</ul>
</section>
{sec('assist', True)}{sec('portal', False)}{sec('dash', True)}
<section class="cta-band">
  <div class="wrap section-inner">
    <div><h2>{e(d['cta_h'])}</h2><p>{e(d['cta_p'])}</p></div>
    <a class="btn btn-primary" href="{contact_href(L, lang)}">{e(UI[lang]['band_btn'])}</a>
  </div>
</section>
<script>window.NX_DEMO = {data};</script>
<script src="{{ASSET}}demos.js?v={{VER}}" defer></script>
"""
    return head(lang, "demos", d["title"], d["desc"], jsonld) + header(L, lang, "demos") + body + footer(L, lang)


def page_legal(L, lang, key):
    d = LEGAL[lang][key]
    vals = dict(OPERATOR, email=EMAIL)
    body_html = d["body"].format(**vals)
    body_html = re.sub(r"\[\[(.+?)\]\]", r'<mark class="ph">\1</mark>', body_html)
    body = f"""<section class="wrap legal">
  <h1>{e(d['h1'])}</h1>
  {body_html}
</section>
"""
    html = head(lang, key, d["title"], d["desc"], []) + header(L, lang, key) + body + footer(L, lang)
    return html.replace('<meta name="description"', '<meta name="robots" content="noindex, follow">\n<meta name="description"', 1)


def root_page(L, full):
    de, en = ("/de/", "/en/") if L.clean else ("de/index.html", "en/index.html")
    inner = f"""<title>Nexvio</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="robots" content="noindex, follow">
<link rel="alternate" hreflang="de" href="{BASE}/de/"><link rel="alternate" hreflang="en" href="{BASE}/en/"><link rel="alternate" hreflang="x-default" href="{BASE}/de/">
<link rel="stylesheet" href="assets/styles.css?v=1">
<main class="wrap chooser">
  <a class="brand" href="{de}" style="justify-content:center">{LOGO}nexvio</a>
  <div class="row"><a class="btn btn-primary" href="{de}" hreflang="de">Deutsch</a><a class="btn btn-ghost" href="{en}" hreflang="en">English</a></div>
</main>
<script>
(function () {{
  var pref = null;
  try {{ pref = localStorage.getItem("nexvio-lang"); }} catch (e) {{}}
  var nav = (navigator.language || "de").slice(0, 2).toLowerCase();
  var lang = pref || (nav === "de" ? "de" : "en");
  location.replace(lang === "en" ? "{en}" : "{de}");
}})();
</script>
"""
    if full:
        return ('<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n</head>\n<body>\n'
                + inner + "</body>\n</html>\n")
    return inner


def build(outdir, clean):
    global VER
    import hashlib
    VER = hashlib.sha1(b"".join(open(os.path.join(ROOT, "src", n), "rb").read() for n in ("styles.css", "main.js", "demos.js"))).hexdigest()[:8]
    L = Linker(clean)
    if os.path.exists(outdir):
        shutil.rmtree(outdir)
    os.makedirs(os.path.join(outdir, "assets"))
    for name in ("styles.css", "main.js", "demos.js"):
        shutil.copy(os.path.join(ROOT, "src", name), os.path.join(outdir, "assets", name))
    shutil.copytree(os.path.join(ROOT, "src", "fonts"), os.path.join(outdir, "assets", "fonts"))
    for lang in LANGS:
        os.makedirs(os.path.join(outdir, lang))
        pages = {"home": page_home(L, lang), "contact": page_contact(L, lang),
                 "imprint": page_legal(L, lang, "imprint"), "privacy": page_legal(L, lang, "privacy"),
                 "demos": page_demos(L, lang)}
        for k in SERVICE_KEYS:
            pages[k] = page_service(L, lang, k)
        for k, html in pages.items():
            fname = (SLUGS[lang][k] or "index") + ".html"
            html = html.replace("{ASSET}", L.asset("")).replace("{VER}", VER)
            with open(os.path.join(outdir, lang, fname), "w", encoding="utf-8") as fh:
                fh.write(html)
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(root_page(L, full=clean))
    if clean:
        urls = "".join(
            f"<url><loc>{url(l, k)}</loc>"
            + "".join(f'<xhtml:link rel="alternate" hreflang="{a}" href="{url(a, k)}"/>' for a in LANGS)
            + "</url>\n" for l in LANGS for k in KEYS)
        with open(os.path.join(outdir, "sitemap.xml"), "w", encoding="utf-8") as fh:
            fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                     'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "</urlset>\n")
        with open(os.path.join(outdir, "robots.txt"), "w", encoding="utf-8") as fh:
            fh.write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")


if __name__ == "__main__":
    build(os.path.join(ROOT, "dist"), clean=True)
    build(os.path.join(ROOT, "preview"), clean=False)
    print("ok")
