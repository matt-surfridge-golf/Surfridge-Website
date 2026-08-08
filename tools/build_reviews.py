#!/usr/bin/env python3
"""
Surfridge Golf Co. — review site generator.

Reads every JSON file in _reviews/ and writes:
  * reviews/<slug>/index.html   — one self-hosted review page each
  * reviews.html                — the card grid, rebuilt between the
                                  <!-- REVIEWS:START --> / <!-- REVIEWS:END --> markers

Run from anywhere:  python3 tools/build_reviews.py
Check without writing:  python3 tools/build_reviews.py --check
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEWS_DIR = ROOT / "_reviews"
OUT_DIR = ROOT / "reviews"
INDEX = ROOT / "reviews.html"

START = "<!-- REVIEWS:START -->"
END = "<!-- REVIEWS:END -->"

REQUIRED = ["slug", "title", "location", "author", "date", "score", "image", "image_alt", "body"]
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

LOGO = ("https://cdn.prod.website-files.com/64f0f1b35700efe402deae6c/"
        "64f0f260ea70a46c98e33770_surfridge-logo-script-flag.png")


# --------------------------------------------------------------------------- #
# Loading + validation
# --------------------------------------------------------------------------- #

def load_reviews() -> list[dict]:
    if not REVIEWS_DIR.is_dir():
        sys.exit(f"error: no _reviews/ directory at {REVIEWS_DIR}")

    reviews, problems = [], []
    for path in sorted(REVIEWS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            problems.append(f"{path.name}: invalid JSON — {e}")
            continue

        for field in REQUIRED:
            if field not in data or data[field] in ("", [], None):
                problems.append(f"{path.name}: missing required field '{field}'")

        slug = data.get("slug", "")
        if slug and not SLUG_RE.match(slug):
            problems.append(f"{path.name}: slug '{slug}' must be lowercase-hyphenated")
        if slug and path.stem != slug:
            problems.append(f"{path.name}: filename should match slug ('{slug}.json')")

        try:
            score = float(data.get("score", -1))
            if not 0 <= score <= 10:
                problems.append(f"{path.name}: score {score} outside 0–10")
        except (TypeError, ValueError):
            problems.append(f"{path.name}: score must be a number")

        if not isinstance(data.get("body"), list):
            problems.append(f"{path.name}: 'body' must be a list of paragraph strings")

        try:
            date.fromisoformat(str(data.get("date", "")))
        except ValueError:
            problems.append(f"{path.name}: date must be YYYY-MM-DD")

        data["_file"] = path.name
        reviews.append(data)

    if problems:
        print("Validation failed:\n  " + "\n  ".join(problems), file=sys.stderr)
        sys.exit(1)

    slugs = [r["slug"] for r in reviews]
    dupes = {s for s in slugs if slugs.count(s) > 1}
    if dupes:
        sys.exit(f"error: duplicate slugs: {', '.join(sorted(dupes))}")

    # newest first
    reviews.sort(key=lambda r: (r["date"], r["slug"]), reverse=True)
    return reviews


# --------------------------------------------------------------------------- #
# Shared chrome
# --------------------------------------------------------------------------- #

def e(s) -> str:
    return html.escape(str(s), quote=True)


def head(title, description, prefix, image=None, canonical=None) -> str:
    og_image = f'\n<meta property="og:image" content="{e(image)}">' if image else ""
    canon = f'\n<link rel="canonical" href="{e(canonical)}">' if canonical else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta name="theme-color" content="#14232B">{canon}

<meta property="og:type" content="article">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">{og_image}

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&amp;family=Inter:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}css/style.css">
</head>
<body>

<a class="skip-link" href="#main">Skip to content</a>
"""


def header(prefix) -> str:
    return f"""
<header class="site-header">
  <div class="container site-header__inner">
    <a class="brand" href="{prefix}index.html" aria-label="Surfridge Golf Co. — home">
      <img src="{LOGO}" alt="Surfridge Golf Co." width="160" height="44">
    </a>

    <button class="nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="primary-nav" aria-label="Toggle navigation menu">
      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
        <path d="M3 6h18M3 12h18M3 18h18"/>
      </svg>
    </button>

    <nav class="nav" id="primary-nav" data-nav aria-label="Primary">
      <ul class="nav__list">
        <li><a class="nav__link" href="{prefix}index.html#why">Why Surfridge</a></li>
        <li><a class="nav__link" href="{prefix}index.html#about">Who We Are</a></li>
        <li><a class="nav__link" href="{prefix}reviews.html">Reviews &amp; Advice</a></li>
      </ul>
      <a class="btn btn--primary btn--sm nav__cta btn--nav" href="{prefix}store.html">Shop</a>
    </nav>
  </div>
</header>
"""


def footer(prefix) -> str:
    return f"""
<footer class="site-footer">
  <div class="container">
    <div class="site-footer__grid">
      <div>
        <img src="{LOGO}" alt="Surfridge Golf Co." width="176" height="48" loading="lazy">
        <p class="site-footer__tagline">Premium, affordable golf products that embody the coastal lifestyle. Made in Los Angeles, played everywhere.</p>
      </div>
      <div>
        <h5>Shop</h5>
        <ul>
          <li><a href="{prefix}store.html">All products</a></li>
          <li><a href="{prefix}store.html#tees">Bamboo tees</a></li>
          <li><a href="{prefix}store.html">Accessories</a></li>
        </ul>
      </div>
      <div>
        <h5>Read</h5>
        <ul>
          <li><a href="{prefix}reviews.html">Course reviews</a></li>
          <li><a href="{prefix}reviews.html">Travel advice</a></li>
          <li><a href="{prefix}reviews.html">Swing tips</a></li>
        </ul>
      </div>
      <div>
        <h5>Company</h5>
        <ul>
          <li><a href="{prefix}index.html#about">Who we are</a></li>
          <li><a href="{prefix}index.html#why">Why Surfridge</a></li>
          <li><a href="mailto:hello@surfridgegolf.com">Contact</a></li>
        </ul>
      </div>
    </div>
    <div class="site-footer__bottom">
      <p>&copy; {date.today().year} Surfridge Golf Co. All rights reserved.</p>
      <p>As an Amazon Associate we may earn from qualifying purchases.</p>
    </div>
  </div>
</footer>

<script src="{prefix}js/main.js" defer></script>
</body>
</html>
"""


def newsletter() -> str:
    return """
  <section class="section section--tight">
    <div class="container">
      <div class="newsletter" data-reveal>
        <div>
          <h2>New reviews in your inbox</h2>
          <p>Course reviews, travel advice, and the occasional discount. Roughly one email a month.</p>
        </div>
        <form data-newsletter novalidate>
          <div class="form-row">
            <div class="field">
              <label for="email">Email address</label>
              <input class="input" id="email" name="email" type="email" placeholder="you@example.com" required autocomplete="email">
            </div>
            <div style="display:flex; align-items:flex-end;">
              <button class="btn btn--accent" type="submit">Subscribe</button>
            </div>
          </div>
          <p class="form-status" data-form-status role="status" aria-live="polite"></p>
          <p class="form-note">No spam. Unsubscribe any time.</p>
        </form>
      </div>
    </div>
  </section>
"""


# --------------------------------------------------------------------------- #
# Review page
# --------------------------------------------------------------------------- #

def fmt_date(iso: str) -> str:
    return date.fromisoformat(iso).strftime("%B %-d, %Y")


def render_score(score: float) -> str:
    """9.0 -> '9', 8.7 -> '8.7'"""
    return f"{score:g}"


def build_page(r: dict, prev: dict | None, nxt: dict | None) -> str:
    P = "../../"
    desc = r.get("verdict") or r["body"][0][:155]

    facts = ""
    if r.get("facts"):
        rows = "\n".join(
            f"        <dt>{e(k)}</dt>\n        <dd>{e(v)}</dd>"
            for k, v in r["facts"].items()
        )
        facts = f"""
      <div class="facts">
        <dl>
{rows}
        </dl>
      </div>
"""

    paras = "\n".join(f"      <p>{e(p)}</p>" for p in r["body"])

    kicker = f'\n      <p class="lead" style="color:rgba(255,255,255,0.86); max-width:38rem;">{e(r["kicker"])}</p>' if r.get("kicker") else ""

    pager_items = []
    if nxt:  # newer
        pager_items.append(
            f"""      <a class="pager--prev" href="../{e(nxt['slug'])}/">
        <p class="pager__dir">Newer review</p>
        <p class="pager__title">{e(nxt['title'])}</p>
      </a>"""
        )
    if prev:  # older
        pager_items.append(
            f"""      <a class="pager--next" href="../{e(prev['slug'])}/">
        <p class="pager__dir">Older review</p>
        <p class="pager__title">{e(prev['title'])}</p>
      </a>"""
        )
    pager = ""
    if pager_items:
        pager = f"""
  <section class="section section--tight section--sand">
    <div class="container">
      <nav class="pager" aria-label="More reviews">
{chr(10).join(pager_items)}
      </nav>
    </div>
  </section>
"""

    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Review",
        "itemReviewed": {"@type": "GolfCourse", "name": r["title"], "address": r["location"]},
        "reviewRating": {"@type": "Rating", "ratingValue": r["score"], "bestRating": 10, "worstRating": 0},
        "author": {"@type": "Person", "name": r["author"]},
        "datePublished": r["date"],
        "publisher": {"@type": "Organization", "name": "Surfridge Golf Co."},
    }, indent=2)

    return (
        head(f'{r["title"]} — Surfridge Golf Co.', desc, P, r["image"])
        + header(P)
        + f"""
<main id="main">

  <article>
    <header class="review-hero">
      <div class="review-hero__media">
        <img src="{e(r['image'])}" alt="{e(r['image_alt'])}" fetchpriority="high">
      </div>
      <div class="container review-hero__content">
        <p class="eyebrow eyebrow--light">Course review · {e(r['location'])}</p>
        <h1>{e(r['title'])}</h1>{kicker}
        <p class="review-meta">
          <span>By {e(r['author'])}</span>
          <span class="review-meta__sep" aria-hidden="true">·</span>
          <time datetime="{e(r['date'])}">{fmt_date(r['date'])}</time>
          <span class="review-meta__sep" aria-hidden="true">·</span>
          <span>Surfridge Score {render_score(r['score'])}</span>
        </p>
      </div>
    </header>

    <div class="section">
      <div class="container">
        <nav class="breadcrumb" aria-label="Breadcrumb">
          <ol>
            <li><a href="{P}index.html">Home</a></li>
            <li><a href="{P}reviews.html">Reviews</a></li>
            <li aria-current="page">{e(r['title'])}</li>
          </ol>
        </nav>
{facts}
        <div class="prose">
{paras}
        </div>

        <aside class="score" aria-label="Surfridge Score">
          <p class="score__num">{render_score(r['score'])}<span>/10</span></p>
          <div>
            <p class="score__label">Surfridge Score</p>
            <p class="score__verdict">{e(r.get('verdict', ''))}</p>
          </div>
        </aside>
      </div>
    </div>
  </article>
{pager}{newsletter()}
</main>

<script type="application/ld+json">
{jsonld}
</script>
"""
        + footer(P)
    )


# --------------------------------------------------------------------------- #
# Listing cards
# --------------------------------------------------------------------------- #

def build_cards(reviews: list[dict]) -> str:
    cards = []
    for r in reviews:
        cards.append(f"""        <li data-reveal>
          <a class="card card-link" href="reviews/{e(r['slug'])}/">
            <div class="card__media">
              <img src="{e(r['image'])}" alt="{e(r['image_alt'])}" loading="lazy">
              <span class="score-badge" aria-hidden="true">{render_score(r['score'])}</span>
            </div>
            <div class="card__body">
              <p class="eyebrow eyebrow--sunset" style="margin-bottom:0;">Course review · {e(r['location'])}</p>
              <h3>{e(r['title'])}</h3>
              <p class="card__meta">By {e(r['author'])} · <time datetime="{e(r['date'])}">{fmt_date(r['date'])}</time> · <span class="visually-hidden">Surfridge Score </span>{render_score(r['score'])}/10</p>
              <p class="card__foot" style="font-weight:600; color:var(--surf-600); font-size:var(--fs-sm);">Read the review &rarr;</p>
            </div>
          </a>
        </li>""")
    return "\n\n".join(cards)


def update_index(reviews: list[dict], check: bool) -> bool:
    if not INDEX.exists():
        sys.exit(f"error: {INDEX} not found")
    src = INDEX.read_text(encoding="utf-8")
    if START not in src or END not in src:
        sys.exit(f"error: {INDEX.name} is missing the {START} / {END} markers")

    before, rest = src.split(START, 1)
    _, after = rest.split(END, 1)
    new = f"{before}{START}\n\n{build_cards(reviews)}\n\n      {END}{after}"

    if new == src:
        return False
    if not check:
        INDEX.write_text(new, encoding="utf-8")
    return True


# --------------------------------------------------------------------------- #

def main() -> None:
    ap = argparse.ArgumentParser(description="Build Surfridge review pages")
    ap.add_argument("--check", action="store_true",
                    help="validate and report what would change, without writing")
    args = ap.parse_args()

    reviews = load_reviews()
    changed = []

    for i, r in enumerate(reviews):
        nxt = reviews[i - 1] if i > 0 else None            # newer
        prev = reviews[i + 1] if i + 1 < len(reviews) else None  # older
        out = OUT_DIR / r["slug"] / "index.html"
        page = build_page(r, prev, nxt)
        existing = out.read_text(encoding="utf-8") if out.exists() else None
        if existing != page:
            changed.append(str(out.relative_to(ROOT)))
            if not args.check:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(page, encoding="utf-8")

    if update_index(reviews, args.check):
        changed.append("reviews.html")

    verb = "would update" if args.check else "wrote"
    print(f"{len(reviews)} review(s) loaded.")
    if changed:
        print(f"{verb}:")
        for c in changed:
            print(f"  {c}")
    else:
        print("Everything already up to date.")

    print("\nLive URLs:")
    for r in reviews:
        print(f"  /reviews/{r['slug']}/   {r['title']}  ({render_score(r['score'])})")


if __name__ == "__main__":
    main()
