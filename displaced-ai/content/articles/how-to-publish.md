Everything on this site comes from the `content` folder. You can change it straight from the GitHub website.

## Add an article

1. Open the `displaced-ai/content/articles` folder on GitHub and choose **Add file → Create new file**.
2. Name it something short with dashes, like `my-first-interview.md`, and write the article in Markdown.
3. Open `displaced-ai/content/site.json`, click the pencil icon, and add an entry to `"articles"`:

```json
{
  "slug": "my-first-interview",
  "title": "My first interview",
  "date": "2026-11-10",
  "author": "Your name",
  "summary": "One sentence that appears in the article list.",
  "tags": ["Interview"],
  "file": "content/articles/my-first-interview.md"
}
```

4. Click **Commit changes**. The site updates within a minute or two.

## Add a video

Add an entry to `"videos"` with **one** of these:

- `"youtube": "https://www.youtube.com/watch?v=..."`: any YouTube link works.
- `"vimeo": "https://vimeo.com/123456789"`
- `"file": "videos/clip.mp4"`: upload the file to the `videos` folder first. Keep files under 100 MB; for anything longer, YouTube or Vimeo is better.

## Add a link

Add an entry to `"links"`. Links with the same `"group"` are listed together.

```json
{ "group": "Reporting", "title": "Article name", "url": "https://...", "note": "Why it matters." }
```

## A note on commas

`site.json` is strict: entries in a list are separated by commas, and the last entry has no comma after it. If the site stops loading after an edit, a missing or extra comma is the usual cause.
