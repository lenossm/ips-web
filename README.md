# IPS

This is the website for IPS — interior and facade stuff. It's a WordPress theme I built, plus a second block-theme version if you'd rather click things together instead of touching code.

Two languages, Georgian and English. Dark look, big hero, smooth page transitions. Nothing too crazy under the hood.

## What's in here

- `style.css`, `functions.php`, `header.php`, `footer.php`, `front-page.php`, all the `page-*.php` / `single-*.php` files — the actual theme.
- `assets/` — the css and js. Real styles live in `assets/css/main.css`, the animations/interactions are in `assets/js/`.
- `inc/` — small helpers. `content.php` reads the content file, `demo-import.php` is the one-click importer.
- `content/` — the content itself (`site.json`) plus the raw stuff I pulled it from. You can ignore the `_*.txt` files, those were just me poking around.
- `scripts/` — python scripts I used to grab the content and build `site.json`. You don't need these to run the site, they're just how the data got made.
- `preview/` — static html preview so you can open it in a browser without WordPress. Just double-click `preview/index.html`.
- `ips-blocks/` — the block-theme version. Has its own `HOW-TO-USE.txt`.

## Running the normal theme

1. Zip the main folder (the one with `style.css` and `functions.php` in it).
2. WordPress → Appearance → Themes → Add New → Upload → pick the zip → Activate.
3. Appearance → **IPS Demo Import** → hit the button. That fills the site with all the pages, projects, brands and blog posts so you don't build them one by one.
4. Settings → Reading → set the home page.

Safe to press the import button twice, it updates instead of making duplicates.

## Just want to look at it

Open `preview/index.html`. It's plain html/css/js, no server needed.

## The block version

If you don't want to deal with PHP at all, use `ips-blocks/` instead — you assemble pages from patterns right in the editor. Steps are in `ips-blocks/HOW-TO-USE.txt`.

## Notes to self

- Contact form goes through FormSubmit, so swap the email in the form if it changes.
- If something looks broken after editing, check `functions.php` first, that's usually where I broke it.
- Reduced-motion is respected, so if animations look "off" it might just be that setting.
