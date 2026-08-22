// Executes the SHIPPED GPX/KML generation code from site/index.html against
// site/nodes.geojson. Code is sliced out of the page verbatim at run time, so
// a change to the shipped generators is automatically a change to what this
// tests — never a retyped copy (the estate's own rule).
import { readFileSync } from "fs";
const html = readFileSync(new URL("../site/index.html", import.meta.url), "utf8");
const geo  = JSON.parse(readFileSync(new URL("../site/nodes.geojson", import.meta.url), "utf8"));

function between(startAnchor, endAnchor, what, { includeEnd = true } = {}) {
  const i = html.indexOf(startAnchor);
  if (i < 0) { console.error("HARNESS-FAIL: cannot find start of " + what); process.exit(2); }
  const j = html.indexOf(endAnchor, i + startAnchor.length);
  if (j < 0) { console.error("HARNESS-FAIL: cannot find end of " + what); process.exit(2); }
  return html.slice(i, includeEnd ? j + endAnchor.length : j);
}

// xesc(): from its declaration to the end of its single line
const xescSrc = between("function xesc(s){", "[c]));}", "xesc()");
// descOf(): single-expression function
const descSrc = "function " + between("descOf(p){return ", ";}", "descOf()");
// The two `const w = visibleGeo().map(...)` builders, verbatim
const gpxExpr = between("const w=visibleGeo().map(f=>{const p=f.properties,[lng,lat]=f.geometry.coordinates;\n      return `  <wpt", ".join('\\n');", "gpx builder");
const kmlExpr = between("const w=visibleGeo().map(f=>{const p=f.properties,[lng,lat]=f.geometry.coordinates;\n      return `    <Placemark", ".join('\\n');", "kml builder");

const LOC = { lang: "en", intl: "en-US", units: "mi", rings: [100, 200, 300],
              vocab: { "full-service": "vollservice-TEST" } }; // prove vocab reaches exports
const mapped = geo.features.filter(f => f.geometry && f.geometry.coordinates);
const visibleGeo = () => mapped;

const strip = s => s.replace(/^const w=/, "").replace(/;\s*$/, "");
// One IIFE so the shipped functions and builders share a scope (ESM strict
// mode keeps eval declarations local — they must be evaluated together).
const { wG, wK } = eval("(() => { " + xescSrc + "\n" + descSrc + "\n"
  + "const wG = " + strip(gpxExpr) + ";\n"
  + "const wK = " + strip(kmlExpr) + ";\n"
  + "return { wG, wK }; })()");
const gpx = `<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.1" creator="Guzzi Support Network" xmlns="http://www.topografix.com/GPX/1/1">\n${wG}\n</gpx>\n`;
const kml = `<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2"><Document>\n    <name>Guzzi Support Network</name>\n${wK}\n</Document></kml>\n`;
console.log(JSON.stringify({ gpx, kml, n: mapped.length }));
