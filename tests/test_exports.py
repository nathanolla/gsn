"""GPX/KML export validation — runs the SHIPPED generators under node."""
import json, pathlib, subprocess, xml.etree.ElementTree as ET
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent

@pytest.fixture(scope="module")
def exports():
    r = subprocess.run(["node", str(ROOT / "tests" / "export_harness.mjs")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)

def test_gpx_is_wellformed_and_complete(exports):
    root = ET.fromstring(exports["gpx"])           # raises on malformed XML
    ns = "{http://www.topografix.com/GPX/1/1}"
    wpts = root.findall(f"{ns}wpt")
    assert len(wpts) == exports["n"], "waypoint count != feature count"
    for w in wpts:
        lat, lon = float(w.get("lat")), float(w.get("lon"))
        assert -90 <= lat <= 90 and -180 <= lon <= 180
        assert not (lat == 0.0 and lon == 0.0), "null island waypoint exported"
        assert w.find(f"{ns}name").text, "empty waypoint name"

def test_kml_is_wellformed_and_complete(exports):
    root = ET.fromstring(exports["kml"])
    ns = "{http://www.opengis.net/kml/2.2}"
    pms = root.findall(f"{ns}Document/{ns}Placemark")
    assert len(pms) == exports["n"]

def test_escaping_survives_hostile_names(exports):
    # 'A&D Motorcycles' and friends: ampersands must be entities in the raw
    # text (parseability is proven above; this pins the mechanism).
    raw = exports["gpx"]
    assert "&amp;" in raw, "expected at least one escaped ampersand (A&D Motorcycles)"
    assert " & " not in raw.replace("&amp;", ""), "raw ampersand leaked"

def test_vocab_reaches_export_descriptions(exports):
    # Harness injects a marker vocab for full-service; descOf must use it.
    assert "vollservice-TEST" in exports["gpx"], "LOC.vocab not applied in descOf"

def test_exports_respect_the_corridor():
    # The shipped export selector must apply the corridor filter — the promise
    # of corridor mode is "export the nodes that can save this trip", and a
    # visibleGeo() without nearRoute() silently exports the whole database.
    html = (ROOT / "site" / "index.html").read_text()
    i = html.index("function visibleGeo()")
    body = html[i:html.index("}", html.index("FEATS.filter", i)) + 1]
    assert "corridorOn()" in body and "nearRoute(" in body, (
        "visibleGeo() no longer applies the corridor filter to exports")
