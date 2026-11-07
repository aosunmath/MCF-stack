import {scherkenoidMesh, SCHERKENOID_WIDTHS} from './scherkenoid-geometry.mjs';
import {nguyenNormals} from './nguyen-viewer.mjs';

export function initScherkenoidFigure(figure, initial) {
  const canvas = figure.querySelector('canvas'), stage = figure.querySelector('.soliton-stage');
  const controls = figure.querySelector('.soliton-controls'), status = figure.querySelector('.soliton-status');
  const help = figure.querySelector('.soliton-help');
  const gl = canvas.getContext('webgl', {antialias: true, alpha: false});
  if (!gl) throw new Error('WebGL unavailable');
  function shader(type, source) {
    const s = gl.createShader(type); gl.shaderSource(s, source); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error('Shader compilation failed');
    return s;
  }
  const program = gl.createProgram();
  gl.attachShader(program, shader(gl.VERTEX_SHADER, `
    attribute vec3 position, normal, color;
    uniform mat3 rotation; uniform vec3 center; uniform vec2 scale;
    varying vec3 norm, tint;
    void main() {vec3 p=rotation*(position-center); norm=rotation*normal; tint=color;
      gl_Position=vec4(p.x*scale.x,p.y*scale.y,-p.z/50.0,1.0);}`));
  gl.attachShader(program, shader(gl.FRAGMENT_SHADER, `
    precision mediump float; varying vec3 norm, tint; uniform int lines;
    void main(){if(lines>0){gl_FragColor=lines==2?vec4(.65,.24,.12,1.):vec4(.14,.27,.31,1.);return;}
      vec3 n=normalize(norm); if(!gl_FrontFacing)n=-n;
      float light=.53+.45*max(0.,dot(n,normalize(vec3(-.3,.6,.8))));
      float shine=pow(max(0.,dot(n,normalize(vec3(-.15,.35,1.)))),35.);
      gl_FragColor=vec4(tint*light+.09*shine,1.);}`));
  gl.linkProgram(program); if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error('Shader linking failed');
  gl.useProgram(program);
  const uniforms = Object.fromEntries(['rotation', 'center', 'scale', 'lines'].map(k => [k, gl.getUniformLocation(program, k)]));
  const attributes = Object.fromEntries(['position', 'normal', 'color'].map(k => [k, {buffer: gl.createBuffer(), location: gl.getAttribLocation(program, k)}]));
  const buffers = Object.fromEntries(['surface', 'wire', 'axes'].map(k => [k, gl.createBuffer()]));
  let data = initial, counts = {}, pending = false, dragging = null;
  const defaults = () => ({width: 1, periods: 2, fundamental: false, yaw: initial.view.yaw, pitch: initial.view.pitch, zoom: 1, wire: false, axes: true});
  let state = defaults();
  const badge = document.createElement('p'); badge.className = 'scherkenoid-view-label'; stage.append(badge);

  function select(labelText, aria, options) {
    const label = document.createElement('label'), input = document.createElement('select');
    label.textContent = labelText; input.setAttribute('aria-label', aria);
    for (const [value, text] of options) {const option = document.createElement('option'); option.value = value; option.textContent = text; input.append(option);}
    label.append(input); controls.append(label); return input;
  }
  const view = select('View ', 'Scherkenoid view', [['surface', 'Connected surface'], ['fundamental', 'Fundamental piece']]);
  const width = select('Width ', 'Scherkenoid strip width', SCHERKENOID_WIDTHS.map(v => [String(v), v === 1 ? 'w = π' : `w = ${v}π`]));
  const periods = select('Periods shown ', 'Scherkenoid displayed periods', [1, 2, 3].map(n => [String(n), String(n)]));
  const axes = document.createElement('button'); axes.type = 'button'; axes.textContent = 'Reflection lines'; controls.append(axes);
  const legend = document.createElement('p'); legend.className = 'scherkenoid-legend';
  legend.textContent = 'Blue: central sheet · Gold / green: alternating wings · Rust: vertical reflection lines'; controls.after(legend);

  function upload() {
    if (data.vertices.length > 65535) throw new Error('Too many vertices');
    const values = {position: data.vertices, normal: nguyenNormals(data.vertices, data.faces), color: data.vertexColors.map(c => c.map(v => v / 255))};
    for (const [name, array] of Object.entries(values)) {
      const {buffer, location} = attributes[name]; gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(array.flat()), gl.STATIC_DRAW);
      gl.enableVertexAttribArray(location); gl.vertexAttribPointer(location, 3, gl.FLOAT, false, 0, 0);
    }
    const indices = {
      surface: data.faces.flat(), wire: data.faces.flatMap(([a, b, c]) => [a, b, b, c, c, a]),
      axes: data.paths.flatMap(path => path.slice(1).flatMap((v, i) => [path[i], v]))
    };
    for (const [name, array] of Object.entries(indices)) {
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, buffers[name]); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(array), gl.STATIC_DRAW); counts[name] = array.length;
    }
  }
  function draw() {
    pending = false;
    const box = stage.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.round(box.width * dpr), h = Math.round(box.height * dpr); if (!w || !h) return;
    if (canvas.width !== w || canvas.height !== h) {canvas.width = w; canvas.height = h;}
    gl.viewport(0, 0, w, h); gl.clearColor(247 / 255, 250 / 255, 251 / 255, 1); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    const cy = Math.cos(state.yaw), sy = Math.sin(state.yaw), cp = Math.cos(state.pitch), sp = Math.sin(state.pitch);
    gl.uniformMatrix3fv(uniforms.rotation, false, new Float32Array([cy, -sy * sp, sy * cp, -sy, -cy * sp, cy * cp, 0, cp, sp]));
    const b = data.bounds, center = state.fundamental ? [2.3, (b.y0 + b.y1) / 2, .3] : [0, 0, .3];
    gl.uniform3fv(uniforms.center, center);
    const horizontal = state.fundamental ? 4.7 : Math.hypot(5.5, b.y1);
    const scale = Math.min(w * .43 / horizontal, h * .36 / 4.7) * state.zoom;
    gl.uniform2f(uniforms.scale, 2 * scale / w, 2 * scale / h);
    // This screen/depth coordinate transform reverses orientation.
    gl.enable(gl.DEPTH_TEST); gl.frontFace(gl.CW); gl.disable(gl.CULL_FACE);
    gl.enable(gl.POLYGON_OFFSET_FILL); gl.polygonOffset(1, 1); gl.uniform1i(uniforms.lines, 0);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, buffers.surface); gl.drawElements(gl.TRIANGLES, counts.surface, gl.UNSIGNED_SHORT, 0);
    gl.disable(gl.POLYGON_OFFSET_FILL);
    for (const [show, name, line] of [[state.wire, 'wire', 1], [state.axes, 'axes', 2]]) if (show) {
      gl.uniform1i(uniforms.lines, line); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, buffers[name]); gl.drawElements(gl.LINES, counts[name], gl.UNSIGNED_SHORT, 0);
    }
    Object.assign(canvas.dataset, {width: String(state.width), periods: String(state.periods), view: state.fundamental ? 'fundamental' : 'surface', zoom: state.zoom.toFixed(3), rotation: `${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`, mesh: String(state.wire), axes: String(state.axes)});
  }
  function requestDraw() {if (!pending) {pending = true; requestAnimationFrame(draw);}}
  function sync() {
    view.value = state.fundamental ? 'fundamental' : 'surface'; width.value = String(state.width); periods.value = String(state.periods); periods.disabled = state.fundamental;
    axes.setAttribute('aria-pressed', String(state.axes)); figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed', String(state.wire));
    badge.textContent = `α = π/2 · w = ${state.width === 1 ? '' : state.width}π · upward convention`;
    const tilt = Math.sqrt(state.width ** 2 - 1);
    status.textContent = `Schematic, not a solved translator. ${state.fundamental ? 'One half-strip piece; half-turns about its two vertical boundary lines generate the surface.' : `${state.periods} horizontal periods are shown; the actual surface continues indefinitely.`} Far-wing slope: √((w/π)² − 1) = ${tilt.toFixed(3)}. Outer edges are display cuts.`;
    help.textContent = 'Drag to rotate; + / − zoom. Change the width to tilt the wings. Fundamental piece isolates the graph used in the paper’s reflection construction.';
    canvas.setAttribute('aria-label', `Connected scherkenoid schematic, alpha pi over two, width ${state.width} pi. ${state.fundamental ? 'One fundamental piece.' : `${state.periods} periods.`} Not a solved translator. Arrow keys rotate; plus and minus zoom.`);
    requestDraw();
  }
  function rebuild() {data = scherkenoidMesh(state.width, state.periods, state.fundamental); upload(); sync();}
  view.addEventListener('change', () => {state.fundamental = view.value === 'fundamental'; state.zoom = 1; state.yaw = state.fundamental ? .9 : 1.04; state.pitch = .35; rebuild();});
  width.addEventListener('change', () => {state.width = Number(width.value); rebuild();});
  periods.addEventListener('change', () => {state.periods = Number(periods.value); rebuild();});
  axes.addEventListener('click', () => {state.axes = !state.axes; sync();});
  function zoom(f) {state.zoom = Math.max(.5, Math.min(3, state.zoom * f)); requestDraw();}
  for (const button of figure.querySelectorAll('[data-view-action]')) button.addEventListener('click', () => {
    const action = button.dataset.viewAction;
    if (action === 'in') zoom(1.2); if (action === 'out') zoom(1 / 1.2);
    if (action === 'wire') {state.wire = !state.wire; sync();}
    if (action === 'reset') {state = defaults(); dragging = null; data = initial; upload(); sync();}
  });
  canvas.addEventListener('pointerdown', e => {dragging = {x: e.clientX, y: e.clientY}; canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove', e => {if (!dragging) return; state.yaw += (e.clientX - dragging.x) * .009; state.pitch += (e.clientY - dragging.y) * .009; dragging = {x: e.clientX, y: e.clientY}; requestDraw();});
  for (const name of ['pointerup', 'pointercancel', 'lostpointercapture']) canvas.addEventListener(name, () => {dragging = null;});
  canvas.addEventListener('keydown', e => {
    const keys = {ArrowLeft: () => state.yaw -= .12, ArrowRight: () => state.yaw += .12, ArrowUp: () => state.pitch -= .12, ArrowDown: () => state.pitch += .12, '+': () => zoom(1.2), '=': () => zoom(1.2), '-': () => zoom(1 / 1.2)};
    if (keys[e.key]) {e.preventDefault(); keys[e.key](); requestDraw();}
  });
  canvas.addEventListener('wheel', e => {if (document.activeElement !== canvas) return; e.preventDefault(); zoom(Math.exp(-e.deltaY * .0015));}, {passive: false});
  canvas.addEventListener('webglcontextlost', e => {e.preventDefault(); canvas.hidden = true; badge.hidden = true; legend.hidden = true; figure.querySelector('img').hidden = false; controls.hidden = true; help.hidden = true; status.textContent = 'The graphics context was lost; the static schematic is shown. Reload to restore interaction.';});
  upload(); sync(); controls.hidden = false; help.hidden = false; figure.querySelector('img').hidden = true; canvas.hidden = false;
  new ResizeObserver(requestDraw).observe(stage);
}
