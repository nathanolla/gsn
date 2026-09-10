"""Data-contract tests for GSN nodes — every assertion is a defect class we shipped.

Run: python3 -m pytest tests/ -q  (CI runs this on every push)
"""
import glob, os, re, subprocess, pathlib
import yaml, pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
NODES = sorted(glob.glob(str(ROOT / "nodes" / "*.yaml")))
LAYERS = {"franchise", "independent", "knowledge", "event"}
CAPS = {"full-service", "satellite", "depot", "performance", "heritage", "knowledge", "event"}
METHODS = {"website", "community-endorsement", "official-locator"}

def load(p): return yaml.safe_load(open(p, encoding="utf-8"))
ALL = {p: load(p) for p in NODES}

def test_nodes_exist():
    assert len(ALL) > 100

def test_ids_match_filenames_and_are_unique():
    seen = set()
    for p, d in ALL.items():
        stem = os.path.splitext(os.path.basename(p))[0]
        assert d["id"] == stem, f"{p}: id != filename"
        assert d["id"] not in seen, f"duplicate id {d['id']}"
        seen.add(d["id"])

def test_vocabulary_is_legal():
    for p, d in ALL.items():
        assert d["layer"] in LAYERS, f"{p}: layer {d['layer']!r}"
        caps = d["capability"] if isinstance(d["capability"], list) else [d["capability"]]
        for c in caps:
            assert c in CAPS, f"{p}: capability {c!r}"

def test_coordinates_are_real_or_flagged():
    # 0.0/0.0 exports junk waypoints into GPX/KML; a node either has real
    # coords or must not exist (held back). city-centroid precision is fine
    # when flagged via geocode:.
    for p, d in ALL.items():
        if d["layer"] == "knowledge" and d.get("lat") in (None, "", 0, 0.0):
            continue  # doctrine: knowledge nodes may be coordinate-free
        lat, lon = float(d.get("lat") or 0), float(d.get("lon") or 0)
        assert not (lat == 0.0 and lon == 0.0), f"{p}: null island coords"
        assert -90 <= lat <= 90 and -180 <= lon <= 180, f"{p}: coords out of range"

def test_every_node_has_provenance():
    for p, d in ALL.items():
        obs = d.get("observations")
        assert isinstance(obs, list) and obs, f"{p}: no observations"
        ok = any(isinstance(o, dict) and o.get("method") in METHODS
                 and o.get("date") and o.get("fact") for o in obs)
        assert ok, f"{p}: no dated observation with a legal method"

def test_urls_are_absolute_lowercase_scheme():
    for p, d in ALL.items():
        u = d.get("url")
        if u:
            assert re.match(r"^https?://", u), f"{p}: url not absolute: {u}"

def test_banned_source_never_returns():
    hay = subprocess.run(["grep", "-ril", "guzzitech", str(ROOT / "nodes"), str(ROOT / "site")],
                         capture_output=True, text=True).stdout.strip()
    assert hay == "", f"banned source referenced in: {hay}"

def test_eras_are_legal_vocabulary():
    ERAS = {"loop-frame", "tonti", "small-block", "spine-frame", "carc", "v85", "v100-pads"}
    tagged = 0
    for p, d in ALL.items():
        eras = d.get("eras")
        if eras is None:
            continue  # doctrine: absent means unknown, not none
        assert isinstance(eras, list) and eras, f"{p}: eras must be a non-empty list"
        for e in eras:
            assert e in ERAS, f"{p}: illegal era {e!r}"
        tagged += 1
    assert tagged >= 5, "era seeding regressed — the filter UI would render dead"


def test_event_nodes_are_time_bounded():
    import datetime, re as _re
    n_events = 0
    for p, d in ALL.items():
        if d["layer"] != "event":
            assert not d.get("event_start") and not d.get("event_end"), \
                f"{p}: event dates on a non-event layer"
            continue
        n_events += 1
        s, e = str(d.get("event_start", "")), str(d.get("event_end", ""))
        assert _re.match(r"^\d{4}-\d{2}-\d{2}$", s), f"{p}: bad event_start"
        assert _re.match(r"^\d{4}-\d{2}-\d{2}$", e), f"{p}: bad event_end"
        assert s <= e, f"{p}: event ends before it starts"
        assert d.get("lat") is not None, f"{p}: event without coordinates"
        assert "event" in d["capability"], f"{p}: event layer needs event capability"
    assert n_events >= 1, "events layer has no data — the chip would render dead"
