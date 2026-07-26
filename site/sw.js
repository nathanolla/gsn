// GSN service worker — offline-first. Version stamped by build.py so a new build
// invalidates the shell cache; node data uses stale-while-revalidate.
const V = 'gsn-/*BUILD:SWVER*/47cb211cc8/*/';
const SHELL = ['./', 'index.html', 'nodes.geojson', 'manifest.json',
  'icon-192.png', 'icon-512.png', 'gsn-88x31.png',
  'vendor/leaflet/leaflet.css', 'vendor/leaflet/leaflet.js',
  'vendor/leaflet/images/marker-icon.png', 'vendor/leaflet/images/marker-shadow.png',
  'vendor/leaflet/images/layers.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(V).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks =>
    Promise.all(ks.filter(k => k !== V && k !== 'gsn-tiles').map(k => caches.delete(k)))
  ).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const u = new URL(e.request.url);
  // OSM map tiles: cache-first runtime cache so viewed areas survive going offline
  if (/\.basemaps\.cartocdn\.com$/.test(u.host)) {
    e.respondWith(caches.open('gsn-tiles').then(async c => {
      const hit = await c.match(e.request);
      if (hit) return hit;
      try { const r = await fetch(e.request); if (r.ok) c.put(e.request, r.clone()); return r; }
      catch (err) { return hit || Response.error(); }
    }));
    return;
  }
  // node data: stale-while-revalidate (fast, updates in background)
  if (u.pathname.endsWith('nodes.geojson')) {
    e.respondWith(caches.open(V).then(async c => {
      const hit = await c.match(e.request);
      const net = fetch(e.request).then(r => { if (r.ok) c.put(e.request, r.clone()); return r; }).catch(() => hit);
      return hit || net;
    }));
    return;
  }
  // same-origin shell: cache-first, fall back to cached index.html when offline
  if (u.origin === location.origin) {
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(r => {
      if (r.ok) caches.open(V).then(c => c.put(e.request, r.clone()));
      return r;
    }).catch(() => caches.match('index.html'))));
  }
});
