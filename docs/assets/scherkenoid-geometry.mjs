// Source-informed connected schematic; NOT a solution of the translator PDE.
// HMW, arXiv:1903.04617v4, Theorem 9.2 and Figures 5, 11.
// alpha = pi/2 throughout. See documentation/scherkenoid-picture.md.
export const SCHERKENOID_WIDTHS = [1, 1.25, 1.5];

export function schematicHeight(x, y, width) {
  const a = (width / Math.PI) ** 2, b = Math.sqrt(a - 1);
  return a * Math.log(Math.abs(x / ((width / Math.PI) * Math.sin(Math.PI * y / width))))
    + b * (Math.hypot(1, x) - 1);
}

export function schematicPoint(y, z, width) {
  const a = (width / Math.PI) ** 2, b = Math.sqrt(a - 1);
  const sine = Math.sin(Math.PI * y / width);
  if (Math.abs(sine) < 1e-14) return [0, y, z];
  const target = z / a + Math.log((width / Math.PI) * Math.abs(sine));
  let lo = 0, hi = Math.exp(target);
  if (b === 0) return [Math.sign(sine) * hi, y, z];
  for (let i = 0; i < 45; i++) {
    const q = (lo + hi) / 2;
    if (Math.log(q) + b / a * (Math.hypot(1, q) - 1) > target) hi = q;
    else lo = q;
  }
  return [Math.sign(sine) * (lo + hi) / 2, y, z];
}

export function scherkenoidMesh(widthRatio = 1, periods = 2, fundamental = false, resolution = 44) {
  if (!SCHERKENOID_WIDTHS.includes(widthRatio) || ![1, 2, 3].includes(periods)) throw new Error('Unsupported scherkenoid display parameters');
  const width = Math.PI * widthRatio;
  const y0 = fundamental ? 0 : -periods * width;
  const pieces = fundamental ? 1 : periods * 2;
  const ny = pieces * resolution, nz = 64;
  const xmin = -5.5, xmax = 5.5, zmin = -3.5, zmax = 4.5;
  const vertices = [], faces = [], vertexColors = [], paths = [];
  for (let j = 0; j <= ny; j++) {
    const y = y0 + pieces * width * j / ny;
    const top = Math.min(zmax, schematicHeight(xmax, y, width));
    for (let k = 0; k <= nz; k++) {
      const p = schematicPoint(y, zmin + (top - zmin) * k / nz, width);
      vertices.push(p);
      const t = Math.min(1, Math.abs(p[0]) / 2.1), s = t * t * (3 - 2 * t);
      const core = [66, 126, 153], wing = p[0] >= 0 ? [222, 157, 85] : [108, 181, 163];
      vertexColors.push(core.map((v, i) => Math.round(v * (1 - s) + wing[i] * s)));
      if (j < ny && k < nz) {
        const i = j * (nz + 1) + k, next = i + nz + 1;
        faces.push([i, next, next + 1], [i, next + 1, i + 1]);
      }
    }
    if (j % resolution === 0) paths.push(Array.from({length: nz + 1}, (_, k) => j * (nz + 1) + k));
  }
  return {
    name: 'scherkenoid-ends', kind: 'scherkenoid-schematic', status: 'schematic',
    widthRatio, periods, fundamental, vertices, faces, vertexColors, paths,
    bounds: {xmin, xmax, y0, y1: y0 + pieces * width, zmin, zmax},
    view: {yaw: fundamental ? .9 : 1.04, pitch: .35},
    description: 'Connected schematic at alpha = pi/2, with the correct half-strip boundary signs, vertical reflection lines, period 2w, and local tilted grim-reaper limits. Not a numerically solved or exact scherkenoid.'
  };
}
