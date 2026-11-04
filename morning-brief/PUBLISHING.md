# Publishing

The phone app is a private claude.ai Artifact:

**https://claude.ai/artifact/VGsPuvHTh5PQz2aqwRHRtZ**

- Page: `app/index.html`. Capabilities: `downloads` (saves the episode as an audio-only `.mp4`,
  since the viewer allow-list has no mp3).
- Supporting files: `episodes/index.json` and `episodes/<date>/{episode.json, episode.mp3, episode.mp4}`,
  at those exact paths. Later publishes only need to add the new day's files plus `index.json`; older
  episodes stay in the artifact.
- From a new session: run the Artifact tool's `read` on the URL first, then publish with
  `url` set to it, `file_path` set to `app/index.html`, and `files` set to the new paths. Omit
  `capabilities` so the stored set is kept.
- On a phone: open the link in the browser (signed in to claude.ai) or the Claude app, then use
  Add to Home Screen.

The same folder also works on any static host (GitHub Pages, Netlify). Copy `app/*` to the
root, with `episodes/` next to it. There the plain MP3 download link and the web-app manifest work as well.
