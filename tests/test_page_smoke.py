"""Whole-page smoke: the shipped page must boot with rows AND pins AND no JS errors.

Exists because a scope bug once shipped where render() threw on every call:
markers looked fine (created before render) while the LIST stayed empty —
invisible to any test that counted only markers. Both halves get asserted now,
plus the console.
"""
import pathlib, re, shutil, socket, subprocess, threading, http.server, functools
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = shutil.which("chromium-browser") or shutil.which("chromium") or \
         shutil.which("google-chrome") or shutil.which("chrome")

@pytest.mark.skipif(CHROME is None, reason="no chromium available")
def test_page_boots_with_rows_pins_and_clean_console(tmp_path):
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]
    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=str(ROOT / "site"))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True); t.start()
    try:
        r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                            "--enable-logging=stderr", "--virtual-time-budget=10000",
                            "--dump-dom", f"http://127.0.0.1:{port}/index.html"],
                           capture_output=True, text=True, timeout=90)
    finally:
        srv.shutdown()
    dom, console = r.stdout, r.stderr
    assert dom.count("leaflet-marker-icon") > 300, "map under-painted"
    assert dom.count('class="clickable') >= 20, "node list did not render"
    errs = [l for l in console.splitlines()
            if re.search(r"Uncaught|ReferenceError|TypeError|SyntaxError", l)]
    assert not errs, "console errors:\n" + "\n".join(errs[:5])
