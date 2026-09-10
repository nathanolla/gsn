"""Build- and i18n-level tests: the site the build emits, not just the data."""
import json, pathlib, re, subprocess, sys
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent

def run_build():
    return subprocess.run([sys.executable, str(ROOT / "build" / "build.py")],
                          capture_output=True, text=True)

def test_build_is_clean_and_idempotent():
    r1 = run_build(); assert r1.returncode == 0, r1.stdout + r1.stderr
    root = (ROOT / "site" / "index.html").read_text()
    assert root.count('class="langbar"') == 1, "language chooser duplicated"
    r2 = run_build(); assert r2.returncode == 0
    root2 = (ROOT / "site" / "index.html").read_text()
    assert root2.count('class="langbar"') == 1, "injection not idempotent"

def test_geojson_matches_nodes():
    g = json.loads((ROOT / "site" / "nodes.geojson").read_text())
    n_nodes = len(list((ROOT / "nodes").glob("*.yaml")))
    assert len(g["features"]) == n_nodes

def test_locale_pages_have_no_english_chrome_leak():
    for lang, probe in [("it", "IMPOSTA BASE"), ("de", "BASIS SETZEN"),
                        ("ja", "拠点を設定"), ("fr", "DÉFINIR BASE"),
                        ("es", "FIJAR BASE"), ("pl", "USTAW BAZĘ")]:
        page = (ROOT / "site" / lang / "index.html").read_text()
        assert probe in page, f"{lang}: expected translated button"
        assert "SET HOME" not in page, f"{lang}: english SET HOME leaked"
        assert f'<html lang="{lang}"' in page
        assert page.count('class="langbar"') == 1

def test_metric_locales_get_km_rings():
    for lang in ["it", "de", "fr", "es", "pl", "ja"]:
        page = (ROOT / "site" / lang / "index.html").read_text()
        m = re.search(r'window\.GSN_LOCALE=(\{.*?\})</script>', page)
        assert m, f"{lang}: no locale bundle"
        loc = json.loads(m.group(1))
        assert loc["units"] == "km" and loc["rings"] == [150, 300, 500]

def test_two_date_freshness_is_derived():
    g = json.loads((ROOT / "site" / "nodes.geojson").read_text())
    scraped = rider = 0
    for f in g["features"]:
        p = f["properties"]
        if "last_scraped" in p:
            scraped += 1
        if "last_rider" in p:
            rider += 1
            assert p["rider_method"] in ("called", "visited", "bought")
            # derived dates must trace back to a matching observation
            assert any(str(o["date"]) == p["last_rider"] and o["method"] == p["rider_method"]
                       for o in p["observations"])
    assert scraped > 300, "scraped-date derivation broke"
    assert rider >= 1, "rider-date derivation broke (artmoto is visited-dated)"

def test_geojson_carries_the_schema_contract():
    g = json.loads((ROOT / "site" / "nodes.geojson").read_text())
    p = g["properties"]
    assert p["schema_version"].startswith("1."), "v1 stability promise broken?"
    assert p["license"] == "ODbL-1.0" and "schema.md" in p["schema"]

def test_no_keyless_carto_tiles_remain():
    # Carto's keyless endpoint started watermarking API KEY REQUIRED on every
    # tile (2026-09-10). One tile source now: OSM, dark via CSS filter.
    for rel in ["index.html", "sw.js"]:
        t = (ROOT / "site" / rel).read_text()
        assert "cartocdn" not in t and "carto.com" not in t, f"{rel}: carto crept back"
    assert "tile.openstreetmap.org" in (ROOT / "site" / "sw.js").read_text()

def test_tile_requests_send_origin_referrer():
    # OSM's tile policy requires a Referer; the global no-referrer meta blocked
    # every tile with a 403 (2026-09-10). strict-origin sends the bare origin
    # only — the ?home= privacy property survives.
    t = (ROOT / "site" / "index.html").read_text()
    i = t.index("L.tileLayer(TILE_URL")
    assert "referrerPolicy:'strict-origin'" in t[i:i+300], \
        "tile layer lost its referrerPolicy — OSM will 403 again"
