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
