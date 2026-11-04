# Morning Signal

A daily two-host audio briefing plus a reading edition, covering **AI**, **Media & Creative** and
**Sustainability**. You listen in the phone's browser, so no podcast app is needed. The file formats are in
[CONTRACT.md](CONTRACT.md).

## Layout
```
config/sources.json        source registry
pipeline/                  setup_tts.sh, build_episode.py, validate.py, make_test_fixture.py
app/                       phone web app (reads episodes/index.json + episode.json)
episodes/index.json        list of episodes, newest first
episodes/YYYY-MM-DD/       stories-{ai,media,sustainability}.json, script.json,
                           episode.json, episode.mp3, qa-report.md (.cache/ is git-ignored)
```

## Daily run
```bash
# 1. TTS (once per container; idempotent, ~10 s from scratch; uses npm, not the open web)
export TTS_CACHE=~/.cache/morning-signal-tts
pipeline/setup_tts.sh

D=episodes/$(date +%F)
# 2. Desks: write $D/stories-ai.json, stories-media.json, stories-sustainability.json
# 3. Producer: write $D/script.json (two hosts; tag the first line about each story with story_id)

# 4. Build: synthesizes the lines in parallel, adds chimes and gaps, normalizes to -16 LUFS,
#    writes episode.mp3 + episode.json, and updates episodes/index.json
python3 pipeline/build_episode.py $D        # --workers N --threads N --speed 1.05 --no-index

# 5. Validate: schemas, URLs, ids, audio duration/level/clipping. A non-zero exit means FAIL
python3 pipeline/validate.py $D

# 6. Publish: commit episodes/ + app/ and deploy (static hosting)
```
After a script edit, re-run step 4. It only re-synthesizes the lines that changed, because each line's audio
is cached in `$D/.cache`.

Test the pipeline on fake data. This never touches `episodes/`:
```bash
EP=$(python3 pipeline/make_test_fixture.py /tmp/claude-0/fixture-episode)
python3 pipeline/build_episode.py $EP && python3 pipeline/validate.py $EP
```
