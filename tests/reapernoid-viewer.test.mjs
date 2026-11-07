import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {frameAt,interpolate,surfaceVertices,limitHeight,surfacePlate,profilePlate} from '../site/assets/reapernoid-viewer.mjs';
const d=JSON.parse(fs.readFileSync(new URL('../site/assets/solitons/reapernoid.json',import.meta.url)));
test('Default revolution mesh is the actual sampled numerical profile',()=>{
 const v=surfaceVertices(d,0);assert.equal(v.length,d.vertices.length);
 v.forEach((p,i)=>p.forEach((x,k)=>assert.ok(Math.abs(x-d.vertices[i][k])<1e-10)));
 for(const t of d.cases[0].snapshots){const f=frameAt(d.cases[0],t),v=surfaceVertices(d,t);for(let i=0;i<d.mesh_x.length;i++){
  assert.ok(Math.abs(Math.hypot(...v[i*d.segments].slice(0,2))-interpolate(d.cases[0].x,f.u,d.mesh_x[i]))<1e-12);
  assert.equal(v[i*d.segments][2],d.mesh_x[i]);
 }}
});
test('Time interpolation preserves sampled slices and cannot extrapolate an eternal flow',()=>{
 for(const m of d.cases){assert.ok(m.frames.every((f,i)=>i===0||f.t>m.frames[i-1].t));for(const f of m.frames){const g=frameAt(m,f.t);g.u.forEach((x,i)=>assert.ok(Math.abs(x-f.u[i])<1e-12));}
 for(const t of [NaN,-1000,1000])assert.throws(()=>frameAt(m,t),RangeError);}
 assert.throws(()=>interpolate([-1,1],[2,2],2),RangeError);
});
test('Forward guides distinguish the line from the grim reaper with the recorded strip width',()=>{
 const [a,b]=d.cases;assert.equal(limitHeight(a,1),0);assert.equal(limitHeight(b,0),0);
 const h=1e-4,k=(limitHeight(b,h)-2*limitHeight(b,0)+limitHeight(b,-h))/(h*h);
 assert.ok(Math.abs(k-Math.PI/(2*b.half_width))<1e-6);
 assert.throws(()=>limitHeight(b,b.half_width),RangeError);
});
test('Time slices are not homothetic catenoids',()=>{
 const m=d.cases[0],a=frameAt(m,-8),b=frameAt(m,10);
 const early=interpolate(m.x,a.u,1)/a.neck_radius,late=interpolate(m.x,b.u,1)/b.neck_radius;
 assert.ok(Math.abs(early-late)>.1);
});
test('Static surface and profile plates match the tested viewer data',()=>{
 assert.equal(surfacePlate(d),fs.readFileSync(new URL('../site/assets/solitons/reapernoid.svg',import.meta.url),'utf8'));
 const svg=profilePlate(d);assert.equal(svg,fs.readFileSync(new URL('../site/assets/solitons/reapernoid-limits.svg',import.meta.url),'utf8'));
 for(const s of ['line limit','grim-reaper limit','no spatial rescaling','not finite-time slices'])assert.ok(svg.includes(s));
});
