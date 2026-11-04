#!/usr/bin/env bash
# Morning Signal — install offline Kokoro TTS (idempotent).
# Usage: pipeline/setup_tts.sh            (cache dir = $TTS_CACHE or ~/.cache/morning-signal-tts)
# Prints the cache dir on the last line; export TTS_CACHE=<that> before build_episode.py.
set -euo pipefail

CACHE="${TTS_CACHE:-$HOME/.cache/morning-signal-tts}"
SHA="fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478"
mkdir -p "$CACHE"

# 1. Python deps
if ! python3 -c "import kokoro_onnx, soundfile, numpy" 2>/dev/null; then
  echo "[setup] pip install kokoro-onnx soundfile numpy"
  pip install --quiet kokoro-onnx soundfile numpy
else
  echo "[setup] python deps present"
fi
command -v ffmpeg >/dev/null || { echo "[setup] ERROR: ffmpeg not found" >&2; exit 1; }

# 2. Model
MODEL="$CACHE/model_quantized.onnx"
if [[ -f "$MODEL" ]] && [[ "$(sha256sum "$MODEL" | cut -d' ' -f1)" == "$SHA" ]]; then
  echo "[setup] model present and verified"
else
  echo "[setup] fetching kokoro-q8-shards@1.0.0 from npm"
  WORK="$(mktemp -d "$CACHE/tmp.XXXX")"
  ( cd "$WORK" && npm pack --silent kokoro-q8-shards@1.0.0 >/dev/null && tar xzf kokoro-q8-shards-1.0.0.tgz )
  SHARDS=()
  for i in 0 1 2 3 4 5; do
    f="$(find "$WORK/package" -name "kokoro-q8.part$i.bin" | head -1)"
    [[ -n "$f" ]] || { echo "[setup] ERROR: shard part$i missing" >&2; exit 1; }
    SHARDS+=("$f")
  done
  cat "${SHARDS[@]}" > "$MODEL.partial"
  GOT="$(sha256sum "$MODEL.partial" | cut -d' ' -f1)"
  if [[ "$GOT" != "$SHA" ]]; then
    echo "[setup] ERROR: sha256 mismatch ($GOT)" >&2; rm -f "$MODEL.partial"; exit 1
  fi
  mv "$MODEL.partial" "$MODEL"
  rm -rf "$WORK"
  echo "[setup] model assembled and verified"
fi

# 3. Voices
VOICES="$CACHE/voices.bin"
if [[ -f "$VOICES" ]]; then
  echo "[setup] voices present"
else
  echo "[setup] fetching kokoro-local-runtime@0.1.0 from npm"
  WORK="$(mktemp -d "$CACHE/tmp.XXXX")"
  ( cd "$WORK" && npm pack --silent kokoro-local-runtime@0.1.0 >/dev/null && tar xzf kokoro-local-runtime-0.1.0.tgz )
  python3 - "$WORK/package/voices" "$CACHE" <<'PY'
import sys, os, glob, numpy as np
src, out = sys.argv[1], sys.argv[2]
voices = {}
for p in sorted(glob.glob(os.path.join(src, "*.bin"))):
    voices[os.path.splitext(os.path.basename(p))[0]] = np.fromfile(p, dtype=np.float32).reshape(510, 1, 256)
if not voices:
    sys.exit("no voices found")
tmp = os.path.join(out, "voices_tmp")          # np.savez appends .npz
np.savez(tmp, **voices)
os.replace(tmp + ".npz", os.path.join(out, "voices.bin"))
print(f"[setup] packed {len(voices)} voices")
PY
  rm -rf "$WORK"
fi

# 4. Smoke test
python3 - "$CACHE" <<'PY'
import sys, os
from kokoro_onnx import Kokoro
c = sys.argv[1]
k = Kokoro(os.path.join(c, "model_quantized.onnx"), os.path.join(c, "voices.bin"))
s, sr = k.create("Good morning.", voice="af_heart", speed=1.05, lang="en-us")
assert sr == 24000 and len(s) > 1000
print(f"[setup] TTS smoke test OK ({len(s)/sr:.2f}s)")
PY
echo "$CACHE"
