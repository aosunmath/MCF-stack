import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {schematicHeight, schematicPoint, scherkenoidMesh, SCHERKENOID_WIDTHS} from '../site/assets/scherkenoid-geometry.mjs';

const close = (a, b, tolerance = 1e-8) => assert.ok(Math.abs(a - b) < tolerance, `${a} != ${b}`);

test('Scherkenoid drawing has vertical reflection lines and horizontal, not vertical, periods', () => {
  for (const ratio of SCHERKENOID_WIDTHS) {
    const w = ratio * Math.PI;
    for (const z of [-3, 0, 3]) {
      for (let n = -3; n <= 3; n++) assert.deepEqual(schematicPoint(n * w, z, w), [0, n * w, z]);
      for (const y of [.2 * w, .67 * w]) {
        const p = schematicPoint(y, z, w), periodic = schematicPoint(y + 2 * w, z, w), reflected = schematicPoint(-y, z, w);
        close(periodic[0], p[0]); close(periodic[1] - p[1], 2 * w); close(periodic[2], p[2]);
        close(reflected[0], -p[0]); close(reflected[1], -p[1]); close(reflected[2], p[2]);
        close(schematicHeight(p[0], p[1], w), z);
      }
      // The joining profile is smooth to second order across each reflection line.
      const h = 1e-4, minus = schematicPoint(-h, z, w)[0], plus = schematicPoint(h, z, w)[0];
      close((minus + plus) / h ** 2, 0);
    }
    close(schematicPoint(1e-6, 0, w)[0] / 1e-6, 1, 1e-6);
  }
});

test('Boundary heights and recentered grim wings use the catalogue upward convention', () => {
  for (const ratio of SCHERKENOID_WIDTHS) {
    const w = ratio * Math.PI, A = ratio ** 2, b = Math.sqrt(A - 1);
    assert.ok(schematicHeight(1e-12, w / 2, w) < -20);
    assert.ok(schematicHeight(1, 1e-12, w) > 20);
    assert.ok(schematicHeight(1, w - 1e-12, w) > 20);
    const a = 1e5, x = 1.3, y = .29 * w;
    const actual = schematicHeight(a + x, y, w) - schematicHeight(a, w / 2, w);
    const limit = -A * Math.log(Math.sin(Math.PI * y / w)) + b * x;
    close(actual, limit, 4e-5);
  }
});

test('The drawing is explicitly not a translator solution', () => {
  // At width pi: X=e^z sin y. Compute the inverse-graph PDE residual analytically.
  const y = .8, z = .3, X = Math.exp(z) * Math.sin(y), Xy = Math.exp(z) * Math.cos(y);
  const residual = (1 + X * X) * (-X) - 2 * Xy * X * Xy + (1 + Xy * Xy) * X + (1 + Xy * Xy + X * X) * X;
  close(residual, X); assert.ok(residual > .5);
  const published = JSON.parse(readFileSync(new URL('../site/assets/solitons/scherkenoid-ends.json', import.meta.url)));
  assert.equal(published.status, 'schematic');
  assert.match(published.description, /Not a numerically solved or exact/);
  assert.deepEqual(published, scherkenoidMesh());
});

test('All width presets give a connected manifold patch with a single display boundary', () => {
  for (const ratio of SCHERKENOID_WIDTHS) for (const fundamental of [false, true]) {
    const mesh = scherkenoidMesh(ratio, 2, fundamental, 12), n = mesh.vertices.length;
    const edges = new Map(), adjacent = Array.from({length: n}, () => []);
    for (const face of mesh.faces) for (let j = 0; j < 3; j++) {
      const a = face[j], b = face[(j + 1) % 3], key = [Math.min(a, b), Math.max(a, b)].join(',');
      edges.set(key, (edges.get(key) || 0) + 1); adjacent[a].push(b); adjacent[b].push(a);
    }
    const seen = new Set([0]), stack = [0];
    while (stack.length) for (const j of adjacent[stack.pop()]) if (!seen.has(j)) {seen.add(j); stack.push(j);}
    assert.equal(seen.size, n); assert.equal(n - edges.size + mesh.faces.length, 1);
    const boundary = new Map();
    for (const [edge, count] of edges) {
      assert.ok(count === 1 || count === 2);
      if (count === 1) for (const v of edge.split(',').map(Number)) boundary.set(v, (boundary.get(v) || 0) + 1);
    }
    assert.ok([...boundary.values()].every(degree => degree === 2));
    assert.ok(mesh.vertices.every(p => p.every(Number.isFinite) && Math.abs(p[0]) <= 5.5 + 1e-9));
    assert.ok(mesh.vertices.length < 65536);
  }
});
