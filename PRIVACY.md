# Privacy

**Principle: privacy by architecture, not by promise.** The strongest line in a privacy
policy is a description of what the system makes impossible.

## What's impossible
**Your location never leaves your browser.** GSN is a static site: the full dataset ships
to your browser, and the locate-me feature uses the browser Geolocation API (behind the
browser's own permission prompt) with all nearest-node math running on-device. The server
cannot log what it never receives. Your home pin is remembered only in your own browser's
localStorage. A location appears in a URL only when you explicitly click **Share view** —
that is you choosing to share it. Fallback is a typed ZIP/city; there is no IP-geolocation
anywhere.

## What's collected
Almost nothing.
- **No accounts, no cookies, no analytics scripts, no tracking.** No cookies means no
  cookie banner — honestly earned.
- **Owner-infrastructure logs** (if/when any GSN origin runs on owner infrastructure):
  IP addresses are truncated at the web server — /24 for IPv4, /48 for IPv6. No full IPs
  at rest, ever.
- **Metrics** (none today): if ever added, they will be self-hosted, cookieless,
  aggregate-only (Plausible/umami/GoatCounter class) on owner infrastructure —
  country/region traffic origin and page counts, nothing else. No IPs stored, no
  cross-site anything. Any change lands as a PR to this file first.

## What's public
**Contributions are public Git records by nature**, under whatever identity the
contributor chooses on the forge. That is the one structural asterisk on "no accounts" —
this policy says so plainly.

Contributor photos, if the project ever accepts them, have all metadata (GPS, timestamps,
device identifiers) stripped by the build pipeline on ingest — the leak is impossible
rather than discouraged.

## Third parties (disclosed, not hidden)
Standard web requests reach these providers, which see your IP like any site you visit:
- **OpenStreetMap** tile servers (map imagery), and — only when you type a ZIP/city — the
  OSM Nominatim geocoder (it receives the text you typed).
  [OSMF privacy policy](https://wiki.osmfoundation.org/wiki/Privacy_Policy)
- **The public mirror host** (GitHub Pages) serves the files and keeps its own standard
  infrastructure logs per [GitHub's privacy statement](https://docs.github.com/site-policy/privacy-policies/github-privacy-statement).
  We do not receive, access, or analyze them.
- If a CDN/proxy (e.g. Cloudflare) fronts an owner-infrastructure origin in the future,
  it terminates TLS and sees visitor IPs; it will be named here as a processor with a
  link to its policy. The truncated-IP promise governs owner logs; third parties get
  disclosed, not hidden.
