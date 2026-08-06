[README.md](https://github.com/user-attachments/files/30806059/README.md)# Surfridge Golf Co. — static site

## Files
- `index.html` — home
- `store.html` — shop (links out to Amazon)
- `reviews.html` — course reviews + advice
- `css/style.css` — all styles (design tokens at the top of the file)
- `js/main.js` — mobile nav, scroll reveal, newsletter form handler

## Running it
Open `index.html` in a browser, or serve the folder:
`python3 -m http.server 8000`

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

