# Displaced AI website

A free, static website for the Displaced AI project. It hosts **articles** (Markdown), **video** (YouTube, Vimeo or your own .mp4 files) and **links**. No database, no build step, no paid hosting.

## Put it online for free (GitHub Pages)

1. On GitHub, open this repository → **Settings → Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**, pick `main` and `/ (root)`, then **Save**.
3. After a minute the site is live at `https://<your-username>.github.io/sustainable/displaced-ai/`.

Prefer a cleaner address? Create a new repository (for example `displaced-ai`), copy the contents of this folder into it, and enable Pages there: the site will be at `https://<your-username>.github.io/displaced-ai/`. You can also add a custom domain under Settings → Pages.

The same folder works unchanged on other free hosts (Netlify, Cloudflare Pages): just upload the folder.

## Update content

Everything lives in `content/`:

| What | Where |
| --- | --- |
| Site title, headline, tagline, footer | `content/site.json` → `"site"` |
| Articles | one `.md` file in `content/articles/` + an entry in `"articles"` |
| Videos | an entry in `"videos"` with `youtube`, `vimeo` or `file` |
| Links | an entry in `"links"` (grouped by `"group"`) |
| About page | `content/about.md` |
| Images | upload to `content/images/`, use `![alt](content/images/name.jpg)` |

The "How to add articles, videos and links" article on the site walks through this step by step.

## Preview on your own computer

The pages load content with `fetch`, so opening `index.html` directly from disk won't work. From this folder run:

```
python3 -m http.server 8000
```

and open http://localhost:8000.

## Files

- `index.html`: page shell
- `styles.css`: design (colours and fonts are set at the top)
- `app.js`: loads `content/site.json` and draws each page
