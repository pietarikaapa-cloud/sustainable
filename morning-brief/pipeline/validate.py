#!/usr/bin/env python3
"""Morning Signal — validate an episode folder against CONTRACT.md.

Usage: python3 pipeline/validate.py episodes/2026-11-04
Exit code 0 = PASS (warnings allowed), 1 = FAIL.
"""
import json
import os
import re
import subprocess
import sys

import numpy as np

DESKS = ["ai", "media", "sustainability"]
SECTIONS = {"intro", "ai", "media", "sustainability", "crossover", "outro"}
KINDS = {"news", "research", "deal", "policy", "launch", "opinion"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL_RE = re.compile(r"^https?://[^\s/$.?#][^\s]*\.[^\s]+$", re.I)


class Report:
    def __init__(self):
        self.errors, self.warnings, self.oks = [], [], []

    def err(self, m): self.errors.append(m)
    def warn(self, m): self.warnings.append(m)
    def ok(self, m): self.oks.append(m)

    def check(self, cond, okmsg, errmsg):
        (self.ok if cond else self.err)(okmsg if cond else errmsg)
        return cond


def load(rep, path):
    if not os.path.exists(path):
        rep.err(f"missing file {os.path.basename(path)}")
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        rep.err(f"{os.path.basename(path)}: invalid JSON ({e})")
        return None


def nonempty_str(v):
    return isinstance(v, str) and v.strip() != ""


def check_story(rep, where, s, desk=None):
    if not isinstance(s, dict):
        rep.err(f"{where}: story is not an object"); return
    sid = s.get("id", "?")
    for k in ("id", "headline", "source", "summary"):
        if not nonempty_str(s.get(k)):
            rep.err(f"{where} {sid}: missing/empty '{k}'")
    url = s.get("url")
    if not (isinstance(url, str) and URL_RE.match(url)):
        rep.err(f"{where} {sid}: url not http(s): {url!r}")
    if desk and isinstance(s.get("id"), str) and not s["id"].startswith(desk + "-"):
        rep.warn(f"{where} {sid}: id does not start with '{desk}-'")
    if s.get("published") and not DATE_RE.match(str(s["published"])):
        rep.warn(f"{where} {sid}: published not YYYY-MM-DD: {s['published']!r}")
    if s.get("kind") and s["kind"] not in KINDS:
        rep.warn(f"{where} {sid}: unknown kind {s['kind']!r}")
    if s.get("confidence") and s["confidence"] not in ("high", "medium"):
        rep.warn(f"{where} {sid}: confidence should be high|medium")
    cr = s.get("crossover")
    if cr is not None and not (isinstance(cr, list) and all(c in DESKS for c in cr)):
        rep.warn(f"{where} {sid}: crossover should be a list of desks")
    if not nonempty_str(s.get("why_it_matters")):
        rep.warn(f"{where} {sid}: no why_it_matters")
    if isinstance(s.get("headline"), str) and len(s["headline"].split()) > 16:
        rep.warn(f"{where} {sid}: headline is {len(s['headline'].split())} words (aim ≤ ~12)")


def audio_stats(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", "24000", "-"],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode()[-500:])
    x = np.frombuffer(r.stdout, dtype=np.float32)
    return x, 24000


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration:format_tags=title,artist:stream=channels,bit_rate,codec_name",
                        "-of", "json", path], capture_output=True, text=True)
    return json.loads(r.stdout or "{}")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    ep = os.path.abspath(sys.argv[1])
    rep = Report()

    # ---- stories
    all_ids, stories = [], {}
    for desk in DESKS:
        p = os.path.join(ep, f"stories-{desk}.json")
        d = load(rep, p)
        if d is None:
            continue
        if not isinstance(d, dict) or not isinstance(d.get("stories"), list):
            rep.err(f"stories-{desk}.json: needs object with 'stories' list"); continue
        if d.get("desk") != desk:
            rep.err(f"stories-{desk}.json: desk is {d.get('desk')!r}")
        if not DATE_RE.match(str(d.get("date", ""))):
            rep.err(f"stories-{desk}.json: bad date {d.get('date')!r}")
        n = len(d["stories"])
        if n == 0:
            rep.err(f"stories-{desk}.json: no stories")
        elif not 5 <= n <= 8:
            rep.warn(f"stories-{desk}.json: {n} stories (aim 5–8)")
        for s in d["stories"]:
            check_story(rep, f"stories-{desk}", s, desk)
            if isinstance(s, dict) and "id" in s:
                all_ids.append(s["id"]); stories[s["id"]] = s
        rep.ok(f"stories-{desk}.json: {n} stories")
    dups = sorted({i for i in all_ids if all_ids.count(i) > 1})
    rep.check(not dups, "story ids unique", f"duplicate story ids: {dups}")

    # ---- script
    sc = load(rep, os.path.join(ep, "script.json"))
    script_ids = []
    if isinstance(sc, dict):
        if not DATE_RE.match(str(sc.get("date", ""))):
            rep.err(f"script.json: bad date {sc.get('date')!r}")
        if not nonempty_str(sc.get("title")):
            rep.err("script.json: missing title")
        hosts = sc.get("hosts")
        if not (isinstance(hosts, dict) and hosts and
                all(isinstance(h, dict) and nonempty_str(h.get("name")) and nonempty_str(h.get("voice"))
                    for h in hosts.values())):
            rep.err("script.json: hosts must map speaker -> {name, voice}")
            hosts = hosts if isinstance(hosts, dict) else {}
        lines = sc.get("lines")
        if not isinstance(lines, list) or not lines:
            rep.err("script.json: no lines")
            lines = []
        for i, l in enumerate(lines):
            if not isinstance(l, dict):
                rep.err(f"script line {i}: not an object"); continue
            if l.get("speaker") not in hosts:
                rep.err(f"script line {i}: unknown speaker {l.get('speaker')!r}")
            if not nonempty_str(l.get("text")):
                rep.err(f"script line {i}: empty text")
            if l.get("section") not in SECTIONS:
                rep.err(f"script line {i}: bad section {l.get('section')!r}")
            sid = l.get("story_id")
            if sid is not None:
                script_ids.append(sid)
                if sid not in stories:
                    rep.err(f"script line {i}: story_id {sid!r} not in any stories file")
        rep.ok(f"script.json: {len(lines)} lines, {len(set(script_ids))} stories referenced")
        missing = [i for i in stories if i not in script_ids]
        if missing:
            rep.warn(f"{len(missing)} stories never mentioned in script: {', '.join(missing)}")

    # ---- episode.json
    epj = load(rep, os.path.join(ep, "episode.json"))
    duration = None
    if isinstance(epj, dict):
        for k in ("date", "title", "tagline", "audio", "generated_at"):
            if not nonempty_str(epj.get(k)):
                rep.err(f"episode.json: missing '{k}'")
        duration = epj.get("duration_sec")
        if not isinstance(duration, (int, float)) or duration <= 0:
            rep.err(f"episode.json: bad duration_sec {duration!r}"); duration = None
        secs = epj.get("sections")
        if not isinstance(secs, list) or [s.get("id") for s in secs] != DESKS:
            rep.err(f"episode.json: sections must be {DESKS} in order")
            secs = secs if isinstance(secs, list) else []
        ep_ids = []
        for s in secs:
            if not nonempty_str(s.get("name")):
                rep.err(f"episode.json section {s.get('id')}: missing name")
            for st in s.get("stories", []):
                check_story(rep, f"episode.json/{s.get('id')}", st)
                ep_ids.append(st.get("id"))
                ss = st.get("start_sec", "absent")
                if ss == "absent":
                    rep.err(f"episode.json {st.get('id')}: start_sec key missing (use null)")
                elif ss is not None and (not isinstance(ss, (int, float)) or ss < 0 or
                                         (duration and ss > duration)):
                    rep.err(f"episode.json {st.get('id')}: bad start_sec {ss!r}")
        if stories and sorted(ep_ids) != sorted(stories):
            rep.err("episode.json stories differ from stories-*.json (rebuild?)")
        tr = epj.get("transcript")
        if not isinstance(tr, list) or not tr:
            rep.err("episode.json: empty transcript")
            tr = []
        prev = -1
        for i, t in enumerate(tr):
            if not (nonempty_str(t.get("speaker")) and nonempty_str(t.get("text"))
                    and isinstance(t.get("start_sec"), (int, float))):
                rep.err(f"transcript {i}: needs speaker, text, start_sec"); continue
            if t["start_sec"] <= prev:
                rep.err(f"transcript {i}: start_sec not increasing")
            if duration and t["start_sec"] > duration:
                rep.err(f"transcript {i}: start_sec beyond duration")
            prev = t["start_sec"]
        if isinstance(sc, dict) and len(tr) != len([l for l in sc.get("lines", []) if
                                                   isinstance(l, dict) and nonempty_str(l.get("text"))]):
            rep.err("episode.json transcript length != script lines (rebuild?)")
        if isinstance(sc, dict) and epj.get("hosts") != sc.get("hosts"):
            rep.warn("episode.json hosts differ from script.json")
        rep.ok(f"episode.json: {len(ep_ids)} stories, {len(tr)} transcript lines")

    # ---- audio
    mp3 = os.path.join(ep, (epj or {}).get("audio") or "episode.mp3")
    if not os.path.exists(mp3):
        rep.err(f"missing audio {os.path.basename(mp3)}")
    else:
        pr = probe(mp3)
        real = float(pr.get("format", {}).get("duration", 0))
        st = (pr.get("streams") or [{}])[0]
        if duration is not None:
            rep.check(abs(real - duration) <= 1.0, f"duration {real:.1f}s matches episode.json",
                      f"duration mismatch: mp3 {real:.2f}s vs episode.json {duration}")
        if st.get("codec_name") != "mp3":
            rep.err(f"audio codec is {st.get('codec_name')!r}, expected mp3")
        if st.get("channels") != 1:
            rep.warn(f"audio has {st.get('channels')} channels (expected mono)")
        tags = {k.lower(): v for k, v in pr.get("format", {}).get("tags", {}).items()}
        if tags.get("artist") != "Morning Signal":
            rep.warn(f"ID3 artist is {tags.get('artist')!r}")
        try:
            x, sr = audio_stats(mp3)
            rms = float(np.sqrt(np.mean(x.astype(np.float64) ** 2))) if x.size else 0.0
            rms_db = 20 * np.log10(max(rms, 1e-12))
            clip = float(np.mean(np.abs(x) >= 0.999)) if x.size else 0.0
            peak = float(np.max(np.abs(x))) if x.size else 0.0
            rep.check(rms_db > -40, f"audio level RMS {rms_db:.1f} dBFS",
                      f"audio near-silent (RMS {rms_db:.1f} dBFS)")
            rep.check(clip < 1e-4, f"no clipping (peak {peak:.3f})",
                      f"clipping: {clip * 100:.3f}% samples at full scale")
            # long silence check (>4 s)
            win = sr // 10
            n = len(x) // win
            if n:
                e = np.sqrt(np.mean(x[:n * win].reshape(n, win) ** 2, axis=1))
                quiet = e < 10 ** (-55 / 20)
                run = best = 0
                for q in quiet:
                    run = run + 1 if q else 0
                    best = max(best, run)
                if best / 10 > 4:
                    rep.warn(f"longest silence {best / 10:.1f}s")
        except Exception as ex:
            rep.err(f"could not decode audio: {ex}")

    # ---- report
    print(f"Morning Signal validation: {ep}")
    for m in rep.oks:
        print(f"  ok    {m}")
    for m in rep.warnings:
        print(f"  WARN  {m}")
    for m in rep.errors:
        print(f"  FAIL  {m}")
    status = "FAIL" if rep.errors else "PASS"
    print(f"{status}: {len(rep.errors)} errors, {len(rep.warnings)} warnings")
    sys.exit(1 if rep.errors else 0)


if __name__ == "__main__":
    main()
