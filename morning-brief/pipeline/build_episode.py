#!/usr/bin/env python3
"""Morning Signal — build episode.mp3 + episode.json from stories-*.json and script.json.

Usage:
    TTS_CACHE=~/.cache/morning-signal-tts python3 pipeline/build_episode.py episodes/2026-11-04
Options:
    --workers N     synthesis processes (default: os.cpu_count())
    --threads N     onnxruntime intra-op threads per worker (default 1)
    --speed X       speaking rate (default 1.05)
    --no-index      don't update ../index.json
See CONTRACT.md for the file formats.
"""
import argparse
import datetime as dt
import hashlib
import json
import multiprocessing as mp
import os
import subprocess
import sys
import tempfile
import time

import numpy as np
import soundfile as sf

SR = 24000
DESKS = [("ai", "AI"), ("media", "Media & Creative"), ("sustainability", "Sustainability")]
SECTIONS = {"intro", "ai", "media", "sustainability", "crossover", "outro"}
GAP_LINE = 0.25        # between lines in a conversation
GAP_STORY = 0.45       # when a new story starts inside a section
GAP_SECTION_PRE = 0.35  # section change: pre-chime silence
GAP_SECTION_POST = 0.45  # section change: post-chime silence (total ~0.8 s + chime)
TARGET_LUFS = -16.0

# ----------------------------------------------------------------- TTS workers
_kokoro = None


def _tts_cache_dir():
    return os.environ.get("TTS_CACHE") or os.path.expanduser("~/.cache/morning-signal-tts")


def _init_worker(threads):
    global _kokoro
    import onnxruntime as ort
    from kokoro_onnx import Kokoro
    d = _tts_cache_dir()
    opts = ort.SessionOptions()
    opts.intra_op_num_threads = threads
    opts.inter_op_num_threads = 1
    sess = ort.InferenceSession(os.path.join(d, "model_quantized.onnx"), sess_options=opts,
                                providers=["CPUExecutionProvider"])
    _kokoro = Kokoro.from_session(sess, os.path.join(d, "voices.bin"))


def _synth(job):
    """job = (idx, text, voice, speed, out_path). Returns (idx, seconds_audio, seconds_compute)."""
    idx, text, voice, speed, out = job
    t0 = time.time()
    samples, sr = _kokoro.create(text, voice=voice, speed=speed, lang="en-us")
    assert sr == SR, sr
    tmp = out + ".tmp.wav"
    sf.write(tmp, np.asarray(samples, dtype=np.float32), SR, subtype="FLOAT")
    os.replace(tmp, out)
    return idx, len(samples) / SR, time.time() - t0


# ----------------------------------------------------------------- audio helpers
def chime(sr=SR):
    """Soft two-note bell sting (~0.75 s), generated procedurally."""
    out = np.zeros(int(sr * 0.75), dtype=np.float32)
    for start, f0, amp in ((0.0, 659.25, 0.16), (0.11, 987.77, 0.12)):  # E5 then B5
        n = len(out) - int(start * sr)
        t = np.arange(n) / sr
        env = (1 - np.exp(-t / 0.006)) * np.exp(-t / 0.18)
        tone = (np.sin(2 * np.pi * f0 * t) + 0.25 * np.sin(2 * np.pi * 2 * f0 * t)
                + 0.08 * np.sin(2 * np.pi * 3.01 * f0 * t))
        out[int(start * sr):] += (amp * env * tone).astype(np.float32)
    # gentle fade to zero
    fade = int(sr * 0.05)
    out[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
    return out


def trim(x, thresh=0.004, pad=0.03):
    """Trim leading/trailing near-silence, keeping a small pad."""
    idx = np.where(np.abs(x) > thresh)[0]
    if idx.size == 0:
        return x
    p = int(pad * SR)
    return x[max(0, idx[0] - p): min(len(x), idx[-1] + p)]


def silence(sec):
    return np.zeros(int(round(sec * SR)), dtype=np.float32)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"command failed: {' '.join(cmd)}\n{r.stderr[-2000:]}")
    return r


def loudnorm_encode(wav_in, mp3_out, meta):
    """Two-pass EBU R128 loudnorm (linear) then MP3 CBR 64k mono with ID3 tags."""
    af1 = f"loudnorm=I={TARGET_LUFS}:TP=-1.5:LRA=11:print_format=json"
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", wav_in, "-af", af1, "-f", "null", "-"])
    txt = r.stderr
    m = json.loads(txt[txt.rindex("{"): txt.rindex("}") + 1])
    af2 = (f"loudnorm=I={TARGET_LUFS}:TP=-1.5:LRA=11:linear=true"
           f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
           f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
           f":offset={m['target_offset']}")
    cmd = ["ffmpeg", "-hide_banner", "-y", "-i", wav_in, "-af", af2, "-ar", str(SR), "-ac", "1",
           "-c:a", "libmp3lame", "-b:a", "64k", "-id3v2_version", "3", "-write_xing", "1"]
    for k, v in meta.items():
        cmd += ["-metadata", f"{k}={v}"]
    run(cmd + [mp3_out])
    return float(m["input_i"])


def probe_duration(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
             "default=nw=1:nk=1", path])
    return float(r.stdout.strip())


# ----------------------------------------------------------------- main
def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def write_json(p, obj):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, p)


def update_index(ep_dir, episode):
    episodes_root = os.path.dirname(os.path.abspath(ep_dir))
    idx_path = os.path.join(episodes_root, "index.json")
    idx = load_json(idx_path) if os.path.exists(idx_path) else {"episodes": []}
    path = os.path.basename(os.path.abspath(ep_dir)) + "/"
    entries = [e for e in idx.get("episodes", []) if e.get("date") != episode["date"] and e.get("path") != path]
    entries.append({"date": episode["date"], "title": episode["title"], "tagline": episode["tagline"],
                    "duration_sec": episode["duration_sec"], "path": path})
    entries.sort(key=lambda e: e["date"], reverse=True)
    write_json(idx_path, {"episodes": entries})
    return idx_path


def ensure_gitignore(ep_dir):
    """Make sure .cache is ignored: append to the nearest morning-brief/.gitignore or episode dir."""
    root = os.path.abspath(os.path.join(ep_dir, "..", ".."))
    target = os.path.join(root, ".gitignore") if os.path.exists(os.path.join(root, "CONTRACT.md")) \
        else os.path.join(ep_dir, ".gitignore")
    existing = open(target).read() if os.path.exists(target) else ""
    if ".cache/" not in existing.split():
        with open(target, "a") as f:
            f.write(("" if existing.endswith("\n") or not existing else "\n") + ".cache/\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode_dir")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--speed", type=float, default=1.05)
    ap.add_argument("--no-index", action="store_true")
    a = ap.parse_args()

    T0 = time.time()
    ep = os.path.abspath(a.episode_dir)
    tts = _tts_cache_dir()
    for f in ("model_quantized.onnx", "voices.bin"):
        if not os.path.exists(os.path.join(tts, f)):
            sys.exit(f"missing {tts}/{f} — run pipeline/setup_tts.sh (and set TTS_CACHE)")

    script = load_json(os.path.join(ep, "script.json"))
    date = script.get("date") or os.path.basename(ep)
    hosts = script["hosts"]
    stories = {}  # id -> (desk, story)
    desk_stories = {}
    for desk, _ in DESKS:
        p = os.path.join(ep, f"stories-{desk}.json")
        lst = load_json(p).get("stories", []) if os.path.exists(p) else []
        if not os.path.exists(p):
            print(f"warning: {p} missing", file=sys.stderr)
        desk_stories[desk] = lst
        for s in lst:
            stories[s["id"]] = s

    lines = [l for l in script["lines"] if l.get("text", "").strip()]
    for i, l in enumerate(lines):
        if l["speaker"] not in hosts:
            sys.exit(f"line {i}: unknown speaker {l['speaker']!r}")
        if l.get("story_id") and l["story_id"] not in stories:
            print(f"warning: line {i}: story_id {l['story_id']!r} not in stories", file=sys.stderr)

    # ---- synthesis (cached)
    cache = os.path.join(ep, ".cache")
    os.makedirs(cache, exist_ok=True)
    ensure_gitignore(ep)
    paths, jobs = [], []
    for i, l in enumerate(lines):
        voice = hosts[l["speaker"]]["voice"]
        text = " ".join(l["text"].split())
        key = hashlib.sha1(f"{voice}|{a.speed}|{text}".encode()).hexdigest()[:20]
        out = os.path.join(cache, f"{key}.wav")
        paths.append(out)
        if not os.path.exists(out) and out not in {j[4] for j in jobs}:
            jobs.append((i, text, voice, a.speed, out))
    print(f"[build] {date}: {len(lines)} lines, {len(lines) - len(jobs)} cached, {len(jobs)} to synthesize "
          f"({a.workers} workers x {a.threads} threads, cpu_count={os.cpu_count()})", flush=True)

    t_syn = time.time()
    synth_audio = synth_cpu = 0.0
    if jobs:
        jobs.sort(key=lambda j: -len(j[1]))  # longest first for better load balance
        workers = max(1, min(a.workers, len(jobs)))
        ctx = mp.get_context("fork" if sys.platform.startswith("linux") else "spawn")
        with ctx.Pool(workers, initializer=_init_worker, initargs=(a.threads,)) as pool:
            for n, (idx, secs, cpu) in enumerate(pool.imap_unordered(_synth, jobs), 1):
                synth_audio += secs
                synth_cpu += cpu
                print(f"  [{n:>3}/{len(jobs)}] line {idx:>3}  {secs:5.1f}s audio  {cpu:5.1f}s", flush=True)
    t_syn = time.time() - t_syn

    # ---- assemble
    sting = chime()
    parts, starts = [], []
    pos = 0
    prev_section = prev_story = None

    def add(x):
        nonlocal pos
        parts.append(x)
        pos += len(x)

    add(sting)                       # opening sting
    add(silence(GAP_SECTION_POST))
    for i, l in enumerate(lines):
        sec = l.get("section", "intro")
        if i > 0:
            if sec != prev_section:
                add(silence(GAP_SECTION_PRE)); add(sting); add(silence(GAP_SECTION_POST))
            elif l.get("story_id") and l.get("story_id") != prev_story:
                add(silence(GAP_STORY))
            else:
                add(silence(GAP_LINE))
        audio, sr = sf.read(paths[i], dtype="float32")
        starts.append(pos / SR)
        add(trim(audio))
        prev_section = sec
        if l.get("story_id"):
            prev_story = l["story_id"]
    add(silence(GAP_SECTION_PRE)); add(sting); add(silence(0.6))   # closing sting
    mix = np.concatenate(parts)
    peak = float(np.max(np.abs(mix))) or 1.0
    if peak > 0.98:
        mix *= 0.98 / peak

    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, "mix.wav")
        sf.write(wav, mix, SR, subtype="FLOAT")
        mp3 = os.path.join(ep, "episode.mp3")
        meta = {"title": f"Morning Signal — {date}: {script.get('title', '')}".rstrip(": "),
                "artist": "Morning Signal", "album": "Morning Signal", "date": date,
                "genre": "Podcast"}
        t_enc = time.time()
        in_lufs = loudnorm_encode(wav, mp3 + ".tmp.mp3", meta)
        os.replace(mp3 + ".tmp.mp3", mp3)
        # Audio-only MP4 (AAC) copy for downloading: the claude.ai artifact viewer only
        # lets pages save allow-listed types (mp4 yes, mp3 no); phones play it as audio.
        m4 = os.path.join(ep, "episode.mp4")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", mp3,
                        "-vn", "-c:a", "aac", "-b:a", "64k", "-ac", "1",
                        "-metadata", f"title={meta['title']}", "-metadata", "artist=Morning Signal",
                        "-movflags", "+faststart", m4 + ".tmp.mp4"], check=True)
        os.replace(m4 + ".tmp.mp4", m4)
        t_enc = time.time() - t_enc
    duration = round(probe_duration(mp3), 2)

    # ---- episode.json
    first_start = {}
    for i, l in enumerate(lines):
        sid = l.get("story_id")
        if sid and sid not in first_start:
            first_start[sid] = round(starts[i], 2)
    sections = []
    for desk, name in DESKS:
        sections.append({"id": desk, "name": name,
                         "stories": [dict(s, start_sec=first_start.get(s["id"])) for s in desk_stories[desk]]})
    intro = next((l["text"] for l in lines if l.get("section") == "intro"), lines[0]["text"] if lines else "")
    transcript = [{"speaker": hosts[l["speaker"]].get("name", l["speaker"]), "text": l["text"],
                   "start_sec": round(starts[i], 2), "story_id": l.get("story_id"),
                   "section": l.get("section")} for i, l in enumerate(lines)]
    episode = {
        "date": date,
        "title": script.get("title", f"Morning Signal — {date}"),
        "tagline": script.get("tagline") or intro,
        "audio": "episode.mp3",
        "download": "episode.mp4",
        "duration_sec": duration,
        "hosts": hosts,
        "sections": sections,
        "transcript": transcript,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    write_json(os.path.join(ep, "episode.json"), episode)
    if not a.no_index:
        print(f"[build] updated {update_index(ep, episode)}")

    total = time.time() - T0
    unmentioned = [s for s in stories if s not in first_start]
    print(f"[build] episode.mp3 {duration:.1f}s ({duration / 60:.1f} min), input {in_lufs:.1f} LUFS -> {TARGET_LUFS}")
    if jobs:
        print(f"[build] synthesis: {synth_audio:.1f}s audio in {t_syn:.1f}s wall "
              f"({t_syn / max(synth_audio, 1e-9):.2f} s wall per s audio; "
              f"{synth_cpu / max(synth_audio, 1e-9):.2f} s worker-time per s audio)")
    print(f"[build] encode {t_enc:.1f}s, total {total:.1f}s")
    if unmentioned:
        print(f"[build] note: {len(unmentioned)} stories not mentioned in script (start_sec null): "
              f"{', '.join(unmentioned)}")
    print(f"[build] wrote {os.path.join(ep, 'episode.json')}")


if __name__ == "__main__":
    main()
