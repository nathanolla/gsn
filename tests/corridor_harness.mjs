// Slices the shipped corridor geometry (toXY/segDist) and checks known distances.
import { readFileSync } from "fs";
const html = readFileSync(new URL("../site/index.html", import.meta.url), "utf8");
function between(a,b,what){const i=html.indexOf(a);if(i<0){console.error("FAIL find "+what);process.exit(2);}
  const j=html.indexOf(b,i+a.length);if(j<0){console.error("FAIL end "+what);process.exit(2);}
  return html.slice(i,j+b.length);}
const toXYsrc=between("function toXY(ll){","];}","toXY");
const segsrc=between("function segDist(p,a,b){","Math.hypot(dx,dy);}","segDist");
const {toXY,segDist}=eval("(()=>{"+toXYsrc+"\n"+segsrc+"\nreturn{toXY,segDist};})()");
// Milan (45.4642,9.19) to Bologna (44.4949,11.3426); Modena (44.6471,10.9252) sits ~10-20km off the line
const A=toXY([45.4642,9.19]), B=toXY([44.4949,11.3426]), M=toXY([44.6471,10.9252]);
const dM=segDist(M,A,B);
// Zurich (47.3769,8.5417) is far from that line
const Z=toXY([47.3769,8.5417]); const dZ=segDist(Z,A,B);
console.log(JSON.stringify({modena_km:+(dM/1000).toFixed(1), zurich_km:+(dZ/1000).toFixed(1)}));
