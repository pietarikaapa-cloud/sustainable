#!/usr/bin/env python3
"""Create a SMALL fake episode for testing the pipeline (never inside the real episodes/ folder).

Usage: python3 pipeline/make_test_fixture.py [/tmp/claude-0/fixture-episode]
Creates <root>/episodes/2026-11-04/{stories-*.json, script.json}; then run
  build_episode.py <root>/episodes/2026-11-04 && validate.py <root>/episodes/2026-11-04
"""
import json
import os
import sys

DATE = "2026-11-04"
root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/fixture-episode")
real = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "episodes"))
if root.startswith(real):
    sys.exit("refusing to write fixture into the real episodes/ folder")
ep = os.path.join(root, "episodes", DATE)
os.makedirs(ep, exist_ok=True)

FAKE = {
    "ai": [("Test lab releases a small open speech model", "research"),
           ("Fictional startup raises seed round for AI captions", "deal")],
    "media": [("Imaginary studio trials AI-assisted storyboards", "launch"),
              ("Pretend guild publishes creative AI guidelines", "policy")],
    "sustainability": [("Sample report tracks data-centre water use", "research"),
                       ("Mock city pilots solar bus shelters", "news")],
}
for desk, items in FAKE.items():
    stories = [{
        "id": f"{desk}-{i}", "headline": h, "source": "Example News",
        "url": f"https://example.com/{desk}/{i}", "published": DATE,
        "summary": f"FIXTURE: {h}. This is fake test content for the pipeline.",
        "why_it_matters": "Test data only.", "crossover": [], "kind": kind, "confidence": "high",
    } for i, (h, kind) in enumerate(items, 1)]
    with open(os.path.join(ep, f"stories-{desk}.json"), "w") as f:
        json.dump({"desk": desk, "date": DATE, "stories": stories}, f, indent=2)

L = lambda sp, t, sid, sec: {"speaker": sp, "text": t, "story_id": sid, "section": sec}
script = {
    "date": DATE, "title": "Fixture episode", "tagline": "A ten-line test of the Morning Signal pipeline.",
    "hosts": {"A": {"name": "Max", "voice": "am_michael"}, "B": {"name": "Nova", "voice": "af_heart"}},
    "lines": [
        L("A", "Good morning, this is Morning Signal. I'm Max.", None, "intro"),
        L("B", "And I'm Nova. This is a short test episode.", None, "intro"),
        L("A", "First up in AI, a test lab released a small open speech model.", "ai-1", "ai"),
        L("B", "Small models matter, because they can run on a phone without the cloud.", "ai-1", "ai"),
        L("A", "Over in media, an imaginary studio is trialling AI-assisted storyboards.", "media-1", "media"),
        L("B", "And a pretend guild has published guidelines for creative AI use.", "media-2", "media"),
        L("A", "On sustainability, a sample report tracks how much water data centres use.", "sustainability-1",
          "sustainability"),
        L("B", "Which connects straight back to the AI story. Compute has a footprint.", None, "sustainability"),
        L("A", "That's the signal for today.", None, "outro"),
        L("B", "See you tomorrow morning.", None, "outro"),
    ],
}
with open(os.path.join(ep, "script.json"), "w") as f:
    json.dump(script, f, indent=2)
print(ep)
