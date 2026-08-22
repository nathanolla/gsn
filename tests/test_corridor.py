"""Corridor geometry: shipped toXY/segDist give sane real-world distances."""
import json, pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parent.parent

def test_corridor_distances_are_sane():
    r = subprocess.run(["node", str(ROOT / "tests" / "corridor_harness.mjs")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    d = json.loads(r.stdout)
    # Modena lies close to the Milan-Bologna line; Zurich absolutely does not.
    assert d["modena_km"] < 30, d
    assert d["zurich_km"] > 150, d
