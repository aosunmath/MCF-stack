// Regenerate the connected construction schematic and its static fallback.
// Run with Node.js from any directory. No third-party dependencies.
import {writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {scherkenoidMesh} from '../site/assets/scherkenoid-geometry.mjs';
import {nguyenNormals} from '../site/assets/nguyen-viewer.mjs';
const out = fileURLToPath(new URL('../site/assets/solitons/', import.meta.url));
const data = scherkenoidMesh();
writeFileSync(out + 'scherkenoid-ends.json', JSON.stringify(data) + '\n');

const cy = Math.cos(data.view.yaw), sy = Math.sin(data.view.yaw), cp = Math.cos(data.view.pitch), sp = Math.sin(data.view.pitch);
const rotate = ([x, y, z]) => [cy * x - sy * y, cp * z - sp * (sy * x + cy * y), sp * z + cp * (sy * x + cy * y)];
const points = data.vertices.map(([x, y, z]) => rotate([x, y, z - .3]));
const normals = nguyenNormals(data.vertices, data.faces).map(rotate);
const screen = p => [320 + 30 * p[0], 218 - 30 * p[1]];
const dot = (a, b) => a.reduce((s, v, i) => s + v * b[i], 0);
const rgb = (face) => {
  let n = [0, 1, 2].map(k => face.reduce((s, i) => s + normals[i][k], 0) / 3);
  const length = Math.hypot(...n); n = n.map(v => v / length);
  if (n[2] < 0) n = n.map(v => -v);
  const light = .53 + .45 * Math.max(0, dot(n, [-.287, .575, .766]));
  const c = [0, 1, 2].map(k => Math.round(face.reduce((s, i) => s + data.vertexColors[i][k], 0) / 3 * light));
  return `rgb(${c.join(',')})`;
};
const polygons = data.faces.map(face => ({face, depth: face.reduce((s, i) => s + points[i][2], 0) / 3})).sort((a, b) => a.depth - b.depth).map(({face}) => {
  const p = face.map(i => screen(points[i]).map(v => v.toFixed(2)).join(',')).join(' '), color = rgb(face);
  return `<polygon points="${p}" fill="${color}" stroke="${color}" stroke-width=".7" stroke-linejoin="round"/>`;
}).join('\n');
writeFileSync(out + 'scherkenoid-ends.svg', `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="410" viewBox="0 0 640 410" role="img" aria-labelledby="title desc">
<title id="title">Scherkenoid: a connected reflection model</title>
<desc id="desc">Original schematic based on Hoffman, Martin and White, Figures 5 and 11. A central sheet opens into alternating wings. Alpha equals pi over two and width equals pi. The drawing uses the upward translation convention and is not an exact or numerically solved translator.</desc>
<rect width="640" height="410" fill="#f7fafb"/>
<g font-family="system-ui,sans-serif" fill="#244957"><text x="24" y="31" font-size="19" font-weight="600">Scherkenoid: connected surface</text><text x="24" y="54" font-size="13">α = π/2 · w = π · upward translation</text></g>
${polygons}
<g font-family="system-ui,sans-serif" fill="#476170" font-size="13"><text x="24" y="378">Two periods of a schematic reflection model.</text><text x="24" y="398">Not a solved translator. All outer edges are display cuts.</text></g></svg>\n`);

writeFileSync(out + 'scherkenoid-domain.svg', `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="410" viewBox="0 0 640 410" role="img" aria-labelledby="title desc">
<title id="title">Scherkenoid fundamental half-strip</title>
<desc id="desc">Exact domain and boundary data at alpha equals pi over two, in the upward convention. The domain is x greater than zero and y between zero and w, with w at least pi. Height tends to positive infinity on the two horizontal rays and negative infinity on the vertical segment. Half-turns about the vertical lines through the two corners extend the fundamental graph.</desc>
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#476170" stroke-width="1.3"/></marker></defs>
<rect width="640" height="410" fill="#f7fafb"/>
<g font-family="system-ui,sans-serif" fill="#244957">
<text x="24" y="32" font-size="19" font-weight="600">The fundamental half-strip</text>
<text x="24" y="56" font-size="14">Exact boundary data · α = π/2 · upward convention</text>
<path d="M154,127 H552 V286 H154 Z" fill="#e4f0ee"/>
<path d="M154,127 H564 M154,286 H564" fill="none" stroke="#b77839" stroke-width="3" marker-end="url(#arrow)"/>
<path d="M154,127 V286" stroke="#2c7b96" stroke-width="4"/>
<path d="M542,135 V278" stroke="#73948f" stroke-dasharray="4 5"/>
<g fill="#a64b29"><circle cx="154" cy="127" r="5"/><circle cx="154" cy="286" r="5"/></g>
<g font-size="17"><text x="302" y="113" fill="#9b5c27">height → +∞</text><text x="302" y="316" fill="#9b5c27">height → +∞</text><text x="24" y="207" fill="#21667f">height → −∞</text></g>
<text x="251" y="200" font-size="19">Ω = {x &gt; 0, 0 &lt; y &lt; w}</text>
<text x="282" y="228" font-size="16">w ≥ π; unbounded to the right</text>
<g font-size="14"><text x="111" y="119">(0, w)</text><text x="112" y="309">(0, 0)</text><text x="576" y="292">x</text></g>
<text x="24" y="358" font-size="14">Each corner lifts to a whole vertical reflection line.</text>
<text x="24" y="382" font-size="14">Two successive half-turns give the horizontal period (0, 2w, 0).</text>
</g></svg>\n`);
console.log(`Wrote ${data.vertices.length} vertices, ${data.faces.length} faces, and two SVG drawings.`);
