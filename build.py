#!/usr/bin/env python3
"""Génère le site statique dans public/ à partir de products.json.

Usage : python3 site/build.py
Aucune dépendance : Python 3.8+ suffit.
"""
import datetime as dt
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"
DATA = json.loads((ROOT / "products.json").read_text(encoding="utf-8"))
SITE = DATA["site"]
PRODUCTS = sorted(DATA["products"], key=lambda p: p["week"], reverse=True)
APPS = DATA.get("apps", [])
TIMELINE_WEEKS = 8

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]

ICON_LEAF = ('<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8" '
             'stroke-linecap="round" aria-hidden="true"><path d="M6 26C6 14 14 6 27 5c0 13-8 21-20 21z"/>'
             '<path d="M6 26 18 14"/></svg>')
ICON_EXT = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6"/>'
            '<path d="M20 4 10 14"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>')
ICON_CHECK = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>')

e = html.escape


def date_fr(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d.day} {MOIS[d.month - 1]}"


def week_date(n):
    return dt.date.fromisoformat(SITE["start_date"]) + dt.timedelta(weeks=n - 1)


def versions(p):
    """Versions en vente (numérique, imprimée…). Ancien format : un seul etsy_url."""
    if p.get("versions"):
        return p["versions"]
    return [{"name": "", "detail": "", "price": p["price"], "etsy_url": p.get("etsy_url", "")}]


def etsy_link(p=None):
    if p:
        for v in versions(p):
            if v.get("etsy_url"):
                return v["etsy_url"]
    return SITE.get("etsy_shop_url") or ""


def display_price(p):
    return f'dès {p["price"]}' if len(versions(p)) > 1 else p["price"]


def version_options(p):
    items = []
    for i, v in enumerate(versions(p)):
        url = v.get("etsy_url") or SITE.get("etsy_shop_url")
        price = e(v["price"]) if v.get("price") else "Voir le prix"
        cls = "option primary" if i == 0 else "option"
        inner = (f'<span class="o-text"><b>{e(v["name"])}</b><small>{e(v["detail"])}</small></span>'
                 f'<span class="o-buy"><span class="o-price">{price}</span>'
                 f'<span class="o-cta">Acheter sur Etsy {ICON_EXT}</span></span>')
        if url:
            items.append(f'<a class="{cls}" href="{e(url)}" target="_blank" rel="noopener" '
                         f'data-etsy="{e(p["slug"])}-{i}">{inner}</a>')
        else:
            items.append(f'<div class="{cls} disabled">{inner}</div>')
    return f'<div class="options" id="versions">{"".join(items)}</div>'


def buy_button(p, cls="btn terra", label="Acheter sur Etsy"):
    url = etsy_link(p)
    if not url:
        return f'<span class="{cls} disabled">Bientôt sur Etsy</span>'
    return (f'<a class="{cls}" href="{e(url)}" target="_blank" rel="noopener" '
            f'data-etsy="{e(p["slug"]) if p else "shop"}">{label} {ICON_EXT}</a>')


def page(title, description, body, prefix="", canonical="", extra_head=""):
    shop = SITE.get("etsy_shop_url")
    shop_btn = (f'<a class="btn small" href="{e(shop)}" target="_blank" rel="noopener">Boutique Etsy</a>'
                if shop else "")
    canon = f'<link rel="canonical" href="{e(canonical)}">' if canonical else ""
    year = dt.date.today().year
    contact = (f'<p>Une question ? <a href="mailto:{e(SITE["contact_email"])}">{e(SITE["contact_email"])}</a></p>'
               if SITE.get("contact_email") else "")
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:type" content="website">
{canon}
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Cpath d='M6 26C6 14 14 6 27 5c0 13-8 21-20 21z' fill='%232f4a36'/%3E%3C/svg%3E">
<link rel="stylesheet" href="{prefix}style.css">
{extra_head}
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="{prefix}index.html">{ICON_LEAF}{e(SITE["name"])}</a>
    <nav class="nav">
      <a href="{prefix}index.html#boutique">Boutique</a>
      <a href="{prefix}index.html#appli">Appli Sève</a>
      <a href="{prefix}index.html#chaque-semaine">Chaque semaine</a>
      <a href="{prefix}index.html#comment-ca-marche">Comment ça marche</a>
      {shop_btn}
    </nav>
  </div>
</header>
{body}
<footer class="site-footer">
  <div class="wrap">
    <div>
      <a class="logo" href="{prefix}index.html">{ICON_LEAF}{e(SITE["name"])}</a>
      <p>{e(SITE["tagline"])}.</p>
    </div>
    <div>
      <p>Paiement et téléchargement sécurisés par Etsy.</p>
      {contact}
    </div>
    <small>© {year} {e(SITE["name"])} · Produits numériques à usage personnel.</small>
  </div>
</footer>
<script src="{prefix}main.js" defer></script>
</body>
</html>
"""


def card(p, prefix=""):
    img = p["images"][0]
    url = f'{prefix}produits/{p["slug"]}.html'
    is_new = p is PRODUCTS[0]
    tag = '<span class="tag">Nouveau</span>' if is_new else ""
    return f"""<article class="card">
  <a class="thumb" href="{url}"><img src="{prefix}img/{p["slug"]}/{img["file"]}" alt="{e(img["alt"])}" loading="lazy" width="1600" height="1200">{tag}</a>
  <div class="body">
    <span class="meta">Semaine {p["week"]} · {e(p["category"])}</span>
    <h3><a href="{url}">{e(p["title"])}</a></h3>
    <p class="sub">{e(p["subtitle"])}</p>
    <div class="foot"><span class="price">{e(display_price(p))}</span><a class="btn ghost small" href="{url}">Découvrir</a></div>
  </div>
</article>"""


def upcoming_card():
    n = max(p["week"] for p in PRODUCTS) + 1
    d = week_date(n)
    return f"""<article class="card upcoming">
  <span class="tag soft">Semaine {n}</span>
  <div class="count" data-countdown="{d.isoformat()}">{d.day} {MOIS[d.month - 1]}</div>
  <p class="muted">Le prochain produit arrive le {date_fr(d.isoformat())}.<br>Un nouveau produit digital chaque semaine.</p>
</article>"""


def timeline():
    by_week = {p["week"]: p for p in PRODUCTS}
    total = max(TIMELINE_WEEKS, max(by_week) + 3)
    next_week = max(by_week) + 1
    items = []
    for n in range(1, total + 1):
        d = week_date(n)
        if n in by_week:
            p = by_week[n]
            items.append(f'<a class="week done" href="produits/{p["slug"]}.html"><div class="n">Semaine {n} · {date_fr(d.isoformat())}</div>'
                         f'<div class="t">{e(p["title"])}</div></a>')
        elif n == next_week:
            items.append(f'<div class="week next"><div class="n">Semaine {n} · {date_fr(d.isoformat())}</div>'
                         f'<div class="t">Prochain produit</div></div>')
        else:
            items.append(f'<div class="week later"><div class="n">Semaine {n} · {date_fr(d.isoformat())}</div>'
                         f'<div class="t">À venir</div></div>')
    return "\n".join(items)


ICON_SEVE = ('<svg viewBox="30 24 48 52" aria-hidden="true"><path d="M54,78 C54,68 54.5,58 54,46" stroke="currentColor" '
             'stroke-width="4" stroke-linecap="round" fill="none"/><path fill="currentColor" d="M54,62 C46,62 38.5,56 36,44 '
             'C46,44 53,51 54,62 Z"/><path fill="currentColor" d="M54,54 C61,52 69,44 72,32 C61,33 54.5,41 54,54 Z"/></svg>')


def phone_mockup():
    tasks = [("Répondre aux mails clients", True), ("Préparer la réunion de 14 h", True),
             ("Arroser les plantes", True), ("Appeler le plombier", False), ("Courses : pain, citrons", False)]
    rows = "".join(f'<li class="{"done" if d else ""}"><span class="box"></span>{e(t)}</li>' for t, d in tasks)
    return f"""<div class="phone" aria-hidden="true">
  <div class="screen">
    <div class="ph-top"><span>9:41</span><span>●●●</span></div>
    <p class="ph-hello">Bonjour,</p>
    <p class="ph-date">Lundi 9 novembre</p>
    <div class="ph-garden">{ICON_SEVE}<div><b>3 tâches sur 5</b><span>terminées aujourd'hui</span><i><em style="width:60%"></em></i></div></div>
    <ul class="ph-tasks">{rows}</ul>
    <span class="ph-fab">+</span>
  </div>
</div>"""


def app_section():
    if not APPS:
        return ""
    a = APPS[0]
    feats = "".join(f"<li><b>{e(t)}</b>{e(d)}</li>" for t, d in a["features"])
    if a.get("store_url"):
        cta = (f'<a class="btn" href="{e(a["store_url"])}" target="_blank" rel="noopener">'
               f'Télécharger sur Google Play {ICON_EXT}</a>')
    else:
        cta = '<span class="btn disabled">Bientôt sur Google Play</span>'
    return f"""<section id="appli" class="app">
  <div class="wrap">
    <div>
      <p class="eyebrow">L'appli · {e(a["platform"])} · {e(a["price"])}</p>
      <h2 class="app-name">{ICON_SEVE}{e(a["name"])}</h2>
      <p class="app-tagline">{e(a["tagline"])}</p>
      <p class="lead">{e(a["description"])}</p>
      <ul class="features">{feats}</ul>
      <div class="actions">{cta}</div>
    </div>
    {phone_mockup()}
  </div>
</section>"""


def build_index():
    star = PRODUCTS[0]
    hero_img = star["images"][0]
    body = f"""<main>
<section class="hero">
  <div class="wrap">
    <div>
      <p class="eyebrow">Papeterie digitale à imprimer</p>
      <h1>{e(SITE["tagline"])}</h1>
      <p class="lead">Calendriers, planners et jolies choses à imprimer chez soi. Chaque lundi, un nouveau produit rejoint la boutique. Achat et téléchargement immédiat, en toute sécurité sur Etsy.</p>
      <div class="actions">
        <a class="btn" href="produits/{star["slug"]}.html">Voir la nouveauté</a>
        <a class="btn ghost" href="#boutique">Toute la boutique</a>
      </div>
    </div>
    <a class="hero-card" href="produits/{star["slug"]}.html">
      <img src="img/{star["slug"]}/{hero_img["file"]}" alt="{e(hero_img["alt"])}" width="1600" height="1200">
      <span class="tag">Semaine {star["week"]} · Nouveau</span>
    </a>
  </div>
</section>

{app_section()}

<section id="boutique" class="alt">
  <div class="wrap">
    <div class="section-head">
      <div><p class="eyebrow">La boutique</p><h2>Tous les produits</h2></div>
      <p class="muted">{len(PRODUCTS)} produit{"s" if len(PRODUCTS) > 1 else ""} · tous en téléchargement immédiat</p>
    </div>
    <div class="grid">
{chr(10).join(card(p) for p in PRODUCTS)}
{upcoming_card()}
    </div>
  </div>
</section>

<section id="chaque-semaine">
  <div class="wrap">
    <div class="section-head">
      <div><p class="eyebrow">Le rendez-vous du lundi</p><h2>Un produit par semaine</h2></div>
      <p class="muted">Revenez chaque semaine : la collection grandit.</p>
    </div>
    <div class="timeline">
{timeline()}
    </div>
  </div>
</section>

<section id="comment-ca-marche" class="alt">
  <div class="wrap">
    <div class="section-head"><div><p class="eyebrow">Simple et sécurisé</p><h2>Comment ça marche</h2></div></div>
    <div class="steps">
      <div class="step"><h3>Choisissez</h3><p>Parcourez les produits et leurs aperçus ici, page par page.</p></div>
      <div class="step"><h3>Achetez sur Etsy</h3><p>Le bouton « Acheter sur Etsy » vous emmène sur l'annonce. Le paiement est géré et sécurisé par Etsy.</p></div>
      <div class="step"><h3>Téléchargez et imprimez</h3><p>Vos fichiers PDF sont disponibles tout de suite dans Etsy → Achats. Imprimez chez vous ou en reprographie.</p></div>
    </div>
  </div>
</section>

<section id="faq">
  <div class="wrap faq">
    <p class="eyebrow">Questions fréquentes</p>
    <h2>Bon à savoir</h2>
    <details><summary>Est-ce que je vais recevoir un objet par la poste ?</summary><p>Pour la version numérique, non : vous recevez des fichiers PDF à imprimer, rien n'est expédié. Certains produits existent aussi en version imprimée, envoyée par la poste : c'est indiqué sur la page du produit.</p></details>
    <details><summary>Quand est-ce que je reçois mes fichiers ?</summary><p>Juste après le paiement. Retrouvez-les à tout moment dans votre compte Etsy, rubrique « Achats », ou dans l'e-mail de confirmation d'Etsy.</p></details>
    <details><summary>Pourquoi acheter sur Etsy ?</summary><p>Etsy s'occupe du paiement (carte, PayPal, Apple Pay…), de la facture et du téléchargement. Vos données bancaires ne passent jamais par ce site.</p></details>
    <details><summary>Sur quel papier imprimer ?</summary><p>Un papier mat épais (160 à 250 g) donne le plus beau rendu. Choisissez « taille réelle » dans les réglages de l'imprimante.</p></details>
    <details><summary>Puis-je partager ou revendre les fichiers ?</summary><p>Les fichiers sont réservés à un usage personnel. Vous pouvez les imprimer autant de fois que vous voulez pour vous ou pour offrir, mais pas les partager ni les revendre.</p></details>
  </div>
</section>
</main>"""
    canonical = (SITE["url"].rstrip("/") + "/") if SITE.get("url") else ""
    (PUBLIC / "index.html").write_text(
        page(f'{SITE["name"]} · {SITE["tagline"]}', SITE["description"], body, canonical=canonical),
        encoding="utf-8")


def build_product(p):
    prefix = "../"
    imgs = p["images"]
    thumbs = "\n".join(
        f'<button type="button" data-src="{prefix}img/{p["slug"]}/{im["file"]}" data-alt="{e(im["alt"])}"'
        f'{" aria-current=\"true\"" if i == 0 else ""} aria-label="Voir l\'image {i + 1}">'
        f'<img src="{prefix}img/{p["slug"]}/{im["file"]}" alt="" loading="lazy"></button>'
        for i, im in enumerate(imgs))
    badges = "".join(f"<li>{e(b)}</li>" for b in p.get("badges", []))
    sections = "\n".join(
        f'<h3>{e(s["title"])}</h3><ul>{"".join(f"<li>{e(i)}</li>" for i in s["items"])}</ul>'
        for s in p.get("sections", []))
    table = ""
    if p.get("table"):
        rows = "".join(f"<li><b>{e(a)}</b>{e(b)}</li>" for a, b in p["table"]["rows"])
        table = f'<h3>{e(p["table"]["title"])}</h3><ul class="months">{rows}</ul>'
    note = f'<h3>À propos</h3><p class="note">{e(p["note"])}</p>' if p.get("note") else ""

    if len(versions(p)) > 1:
        reassure = (f"<li>{ICON_CHECK}Numérique : PDF disponibles tout de suite après l'achat</li>"
                    f"<li>{ICON_CHECK}Imprimée : expédiée chez vous par la poste</li>")
        mobile_btn = '<a class="btn terra" href="#versions">Choisir ma version</a>'
    else:
        reassure = (f"<li>{ICON_CHECK}Fichiers PDF disponibles tout de suite après l'achat</li>"
                    f"<li>{ICON_CHECK}Produit numérique : rien n'est expédié</li>")
        mobile_btn = buy_button(p)
    page_url = f'{SITE["url"].rstrip("/")}/produits/{p["slug"]}.html' if SITE.get("url") else ""
    ld = {
        "@context": "https://schema.org", "@type": "Product",
        "name": p["title"], "description": p["subtitle"], "category": p["category"],
        "image": [f'{SITE["url"].rstrip("/")}/img/{p["slug"]}/{im["file"]}' if SITE.get("url") else f'img/{p["slug"]}/{im["file"]}' for im in imgs],
        "offers": [{"@type": "Offer", "name": v["name"] or p["title"], "priceCurrency": "EUR",
                    **({"price": v["price"].replace("€", "").replace(",", ".").strip()} if v.get("price") else {}),
                    "availability": "https://schema.org/InStock",
                    **({"url": v["etsy_url"]} if v.get("etsy_url") else {})} for v in versions(p)],
    }
    extra_head = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'

    body = f"""<main class="wrap">
<nav class="crumbs"><a href="{prefix}index.html">Accueil</a> › <a href="{prefix}index.html#boutique">{e(p["category"])}</a> › {e(p["title"])}</nav>
<div class="product">
  <div class="gallery">
    <div class="main"><img id="main-img" src="{prefix}img/{p["slug"]}/{imgs[0]["file"]}" alt="{e(imgs[0]["alt"])}" width="1600" height="1200"></div>
    <div class="thumbs">{thumbs}</div>
  </div>
  <aside class="buybox">
    <p class="eyebrow">Semaine {p["week"]} · {e(p["category"])}</p>
    <h1>{e(p["title"])}</h1>
    <p class="muted">{e(p["subtitle"])}</p>
    <span class="price">{e(display_price(p))}</span>
    <ul class="badges">{badges}</ul>
    {version_options(p) if len(versions(p)) > 1 else buy_button(p)}
    <ul class="reassure">
      <li>{ICON_CHECK}Paiement sécurisé par Etsy</li>
      {reassure}
    </ul>
  </aside>
</div>
<div class="details">
  <p class="intro">{e(p["intro"])}</p>
  {table}
  {sections}
  {note}
</div>
</main>
<div class="mobile-buy"><span class="price">{e(display_price(p))}</span>{mobile_btn}</div>"""
    out = PUBLIC / "produits"
    out.mkdir(parents=True, exist_ok=True)
    html_out = page(f'{p["title"]} · {SITE["name"]}', f'{p["subtitle"]}. {p["intro"][:110]}…', body,
                    prefix=prefix, canonical=page_url, extra_head=extra_head)
    html_out = html_out.replace("<body>", '<body class="has-mobile-buy">', 1)
    (out / f'{p["slug"]}.html').write_text(html_out, encoding="utf-8")


def build_seo():
    """sitemap.xml et robots.txt (si l'adresse du site est renseignée)."""
    if not SITE.get("url"):
        return
    base = SITE["url"].rstrip("/")
    today = dt.date.today().isoformat()
    urls = [f"{base}/"] + [f'{base}/produits/{p["slug"]}.html' for p in PRODUCTS]
    entries = "".join(f"<url><loc>{e(u)}</loc><lastmod>{today}</lastmod></url>" for u in urls)
    (PUBLIC / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{entries}</urlset>\n', encoding="utf-8")
    (PUBLIC / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")


def main():
    warnings = []
    for p in PRODUCTS:
        for im in p["images"]:
            if not (PUBLIC / "img" / p["slug"] / im["file"]).exists():
                sys.exit(f'Image manquante : public/img/{p["slug"]}/{im["file"]}')
        if not any(v.get("etsy_url") for v in versions(p)):
            warnings.append(f'« {p["title"]} » n\'a pas de lien Etsy (etsy_url) : bouton « Bientôt sur Etsy ».')
    build_index()
    for p in PRODUCTS:
        build_product(p)
    build_seo()
    print(f"Site généré dans {PUBLIC} ({len(PRODUCTS)} produit(s)).")
    for w in warnings:
        print("Attention :", w)


if __name__ == "__main__":
    main()
