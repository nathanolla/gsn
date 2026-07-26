# Privacy

GSN is a static site. There is no backend, no accounts, no cookies, no analytics scripts,
and no tracking of any kind.

**Your location never leaves your browser.** The home pin (browser geolocation, a typed
ZIP/city, or a map click) and every distance/bearing computation are handled entirely
client-side. The pin is remembered in your own browser's localStorage. A location appears
in a URL only when you explicitly click **Share view** — that's you choosing to share it.

**Third parties this site talks to** (standard web requests — they see your IP like any
site you visit):
- OpenStreetMap tile servers (map imagery) and, only when you type a ZIP/city, the OSM
  Nominatim geocoder (it receives the text you typed). See the
  [OSMF privacy policy](https://wiki.osmfoundation.org/wiki/Privacy_Policy).
- The static-site host serves the files and keeps its own standard infrastructure logs
  per its privacy policy. We do not receive, access, or analyze them.

**If we ever add usage metrics**, the standing policy is: aggregate only, IP addresses
truncated to network prefix, no user identifiers, no cross-site anything, nothing
personally trackable — enough to know roughly where traffic comes from and no more. Any
such change lands as a PR to this file first.
