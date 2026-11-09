// Static no-JavaScript / print fallback using the interactive geometry itself.
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {TIMES,COLORS,neckpinchProfile,scales,project,surfacePolygons,shade,timeLabel} from '../site/assets/neckpinch-geometry.mjs';
const folder=fileURLToPath(new URL('../site/assets/solitons/',import.meta.url));
const data=JSON.parse(fs.readFileSync(folder+'neckpinch-scales.json'));
const svg=['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="700" viewBox="0 0 960 700" role="img" aria-labelledby="title desc">',
  '<title id="title">An approaching degenerate neckpinch at three times</title>',
  '<desc id="desc">An original asymptotic schematic of the odd cubic Angenent–Velázquez construction in three-space. The left tip approaches the origin at three illustrative times; the last panel is a cusp target. All panels use one equal-axis spatial scale. The compact slices are not numerical MCF solutions. Their tip caps use a numerical bowl ODE, with designed joins and outer caps.</desc>',
  '<rect width="960" height="700" fill="#f7fafb"/>',
  '<g font-family="system-ui, sans-serif" fill="#183f52">',
  '<text x="28" y="39" font-size="27" font-weight="600">One tip sharpens as t approaches T</text>',
  '<text x="28" y="68" font-size="18" fill="#526b77">n = 2 · m = 3 · K = 1 · common spatial scale · asymptotic schematic</text>'];
for(let i=0;i<4;i++){
  const x=20+(i%2)*470,y=90+Math.floor(i/2)*266,w=450,h=250,scale=300,cx=x+w/2-.25*scale,cy=y+140;
  const screen=p=>[cx+scale*p[0],cy-scale*p[1]],fmt=p=>p.map(v=>v.toFixed(2)).join(',');
  svg.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="12" fill="white" stroke="#d7e3e8"/>`,
    `<text x="${x+18}" y="${y+31}" font-size="21" font-weight="600" fill="${COLORS[i]}">${timeLabel(TIMES[i])}</text>`);
  const a=screen(project([-.15,0,0])),b=screen(project([.66,0,0]));
  svg.push(`<path d="M${fmt(a)} L${fmt(b)}" fill="none" stroke="#b6c7ce" stroke-dasharray="5 5"/>`);
  const profile=neckpinchProfile(TIMES[i],data);
  // Downsample only the smooth mesh for a compact, original vector drawing.
  const mesh=profile.filter((_,j)=>j%3===0||j===profile.length-1);
  for(const face of surfacePolygons(mesh,-.28,.2,32)){
    const color=shade(COLORS[i],face.light);
    svg.push(`<polygon points="${face.points.map(p=>fmt(screen(p))).join(' ')}" fill="${color}" stroke="${color}" stroke-width=".4"/>`);
  }
  const origin=screen(project([0,0,0])),tip=screen(project([TIMES[i]?scales(TIMES[i]).tip:0,0,0]));
  svg.push(`<path d="M${origin[0]},${origin[1]+8} V${y+212}" stroke="#a78c72" stroke-dasharray="3 4"/>`,
    `<circle cx="${tip[0]}" cy="${tip[1]}" r="4.5" fill="${i===3?COLORS[i]:'#d48c2e'}"/>`,
    `<text x="${origin[0]-18}" y="${y+232}" font-size="16" fill="#526b77">x = 0</text>`);
}
svg.push('<text x="28" y="646" font-size="18">The moving left tip (gold) approaches the cusp; the outer cap persists.</text>',
  '<text x="28" y="675" font-size="17" fill="#526b77">AV97, pp. 16–25. Designed compact slices; only the limiting bowl is ODE-integrated.</text>',
  '</g></svg>');
fs.writeFileSync(folder+'neckpinch-scales.svg',svg.join('\n')+'\n');
console.log('Rendered neckpinch-scales.svg');
