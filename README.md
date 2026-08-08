# Surfridge Golf Co. — static site

## Files
- `index.html` — home
- `store.html` — shop (links out to Amazon)
- `reviews.html` — course reviews + advice
- `css/style.css` — all styles (design tokens at the top of the file)
- `js/main.js` — mobile nav, scroll reveal, newsletter form handler

## Running it
Open `index.html` in a browser, or serve the folder:
`python3 -m http.server 8000`

## Course reviews

Reviews are generated, not hand-written. Each one is a JSON file in `_reviews/`:

    _reviews/<slug>.json    ->   reviews/<slug>/index.html   +   a card on reviews.html

To add or edit one, write the JSON and run:

    python3 tools/build_reviews.py          # build
    python3 tools/build_reviews.py --check  # validate only, write nothing

The script validates every field, sorts by date (newest first), wires up prev/next
links, and emits schema.org Review JSON-LD for search engines. Never edit anything
under `reviews/` by hand — it gets overwritten.

The card grid in `reviews.html` lives between the `<!-- REVIEWS:START -->` and
`<!-- REVIEWS:END -->` markers and is fully managed by the script. Everything else on
that page is yours to edit.

The `surfridge-add-review` skill wraps this whole workflow if you'd rather just say
"add a review for Pebble Beach" in Cowork.

## Things you'll want to change

**Product photos.** Both tee products use real photos from `images/`, served as a
responsive `<picture>` (WebP + JPEG at 600/900px, centre-cropped square). To swap one,
regenerate all five files for that product at the same sizes and names.

**Prices.** Add `<p class="product__price">$12.99</p>` inside `.product__body` — the style is already defined.

**Newsletter.** `js/main.js` currently just shows a success message. Point the `<form>`
at your provider's endpoint (Mailchimp, ConvertKit, Formspree) and delete the JS handler.

**Amazon Associates.** If you're in the program, append your tag to the product links
and keep the disclosure line in the footer.

**Hero image.** `index.html` serves a responsive set from `images/` — WebP with JPEG
fallback at 800/1200/2000px wide. If you swap the photo, regenerate all six files at the
same sizes so the `srcset` stays accurate.

**Brand colors.** All in `:root` at the top of `css/style.css` — change `--surf-600`
and `--sunset-600` to re-theme the whole site.
