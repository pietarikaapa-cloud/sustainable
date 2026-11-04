# Morning Signal — data contract

Daily audio + reading briefing covering **AI**, **Media & Creative industries**, and
**Sustainability** (incl. where they intersect). Every agent in the pipeline reads and writes
these files and nothing else, so they can work in parallel.

```
morning-brief/
  config/sources.json              # source registry          (Sources agent)
  pipeline/                        # build scripts             (App/pipeline agent)
  app/                             # phone web app (PWA)       (Interface agent)
  episodes/index.json              # list of episodes, newest first
  episodes/YYYY-MM-DD/
    stories-ai.json                # raw finds per desk        (Daily scan agents)
    stories-media.json
    stories-sustainability.json
    script.json                    # two-host podcast script   (Producer agent)
    episode.json                   # final, app-facing         (pipeline build step)
    episode.mp3                    # final audio               (pipeline build step)
    qa-report.md                   # fact-check + app QA notes (QA agents)
```

## config/sources.json
```json
{
  "updated": "2026-11-04",
  "sections": {
    "ai":             [ { "name": "Wired", "url": "https://www.wired.com/", "rss": "https://www.wired.com/feed/rss", "type": "news|trade|research|newsletter|policy", "why": "one line", "tier": 1 } ],
    "media":          [ ... ],
    "sustainability": [ ... ]
  }
}
```
`tier` 1 = check every day, 2 = check when time allows, 3 = specialist/occasional.

## episodes/YYYY-MM-DD/stories-<desk>.json
```json
{
  "desk": "ai|media|sustainability",
  "date": "2026-11-04",
  "stories": [
    {
      "id": "ai-1",
      "headline": "Plain-English headline (max ~12 words)",
      "source": "Publication name",
      "url": "https://… (the original article — must be a real, working URL found via search)",
      "published": "2026-11-03",
      "summary": "2–4 sentence factual summary. Only claims supported by the source.",
      "why_it_matters": "1–2 sentences for someone working across AI / media / sustainability.",
      "crossover": ["media"],
      "kind": "news|research|deal|policy|launch|opinion",
      "confidence": "high|medium"
    }
  ]
}
```
Aim for 5–8 stories per desk, published in the last ~48h (research papers/reports: last 7 days).

## episodes/YYYY-MM-DD/script.json
```json
{
  "date": "2026-11-04",
  "title": "Episode title",
  "hosts": { "A": { "name": "Max", "voice": "am_michael" }, "B": { "name": "Nova", "voice": "af_heart" } },
  "lines": [
    { "speaker": "A", "text": "Spoken line. Write for the ear.", "story_id": null, "section": "intro" },
    { "speaker": "B", "text": "…", "story_id": "ai-1", "section": "ai" }
  ]
}
```
`section` is one of `intro | ai | media | sustainability | crossover | outro`.
The first line that discusses a story must carry its `story_id` (used for chapter jumps).

## episodes/YYYY-MM-DD/episode.json  (built by `pipeline/build_episode.py`)
```json
{
  "date": "2026-11-04",
  "title": "…",
  "tagline": "One-sentence teaser",
  "audio": "episode.mp3",
  "duration_sec": 812.4,
  "hosts": { … as in script … },
  "sections": [
    { "id": "ai", "name": "AI", "stories": [ { …story fields…, "start_sec": 63.2 } ] }
  ],
  "transcript": [ { "speaker": "Max", "text": "…", "start_sec": 0.0, "story_id": null } ],
  "generated_at": "ISO timestamp"
}
```

## episodes/index.json
```json
{ "episodes": [ { "date": "2026-11-04", "title": "…", "tagline": "…", "duration_sec": 812.4, "path": "2026-11-04/" } ] }
```

## Text-to-speech
Offline neural TTS: Kokoro-82M (Apache-2.0) via `kokoro-onnx` (pip). The open web is
blocked in the build container, so weights come from npm:
- model: `npm pack kokoro-q8-shards@1.0.0` → `cat kokoro-q8.part{0..5}.bin > model_quantized.onnx`
  (sha256 `fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478`)
- voices: `npm pack kokoro-local-runtime@0.1.0` → `package/voices/*.bin` (float32, reshape to
  (510,1,256)) → saved together with `np.savez` as `voices.bin`.
- usage: `Kokoro("model_quantized.onnx","voices.bin").create(text, voice="am_michael", speed=1.05, lang="en-us")`
  returns (float32 samples, 24000). ≈1.3 s of compute per second of audio on one core.
Good voices: am_michael, af_heart, bf_emma, bm_george, af_bella, am_fenrir.
