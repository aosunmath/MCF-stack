import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {normalFrame,snapshotSVG} from '../site/assets/minimal-ancient-viewer.mjs';
const d=JSON.parse(fs.readFileSync(new URL('../site/assets/solitons/minimal-ancient-flows.json',import.meta.url)));
test('Time slices stay normal, are on opposite sides, and have the declared growth rate',()=>{
 const a=normalFrame(d,-3),b=normalFrame(d,-2),c=normalFrame(d,-3,-1),g=normalFrame(d,-3,1,3);
 for(let i=0;i<a.length;i+=97){
  const p=d.vertices[i],v=a[i].map((x,k)=>x-p[k]);
  const dot=v.reduce((s,x,k)=>s+x*d.normals[i][k],0);assert.ok(dot>=-1e-15);
  for(let k=0;k<3;k++){
   assert.ok(Math.abs(v[k]-dot*d.normals[i][k])<1e-8);
   assert.ok(Math.abs(b[i][k]-p[k]-Math.E*v[k])<1e-10);
   assert.ok(Math.abs(a[i][k]+c[i][k]-2*p[k])<1e-10);
   assert.ok(Math.abs(g[i][k]-p[k]-3*v[k])<1e-10);
  }
 }
});
test('The model cannot silently extrapolate to later times or invalid parameters',()=>{
 for(const t of [NaN,Infinity,-5.1,.1])assert.throws(()=>normalFrame(d,t),RangeError);
 assert.throws(()=>normalFrame(d,-1,0),RangeError);assert.throws(()=>normalFrame(d,-1,1,5),RangeError);
});
test('Static plate retains every time and the numerical-model qualification',()=>{
 const svg=snapshotSVG(d);for(const t of d.snapshots)assert.ok(svg.includes(`τ = ${t}`));
 assert.ok(svg.includes('displacement ×3'));assert.ok(svg.includes('Not nonlinear ancient flow slices'));
 assert.equal(svg,fs.readFileSync(new URL('../site/assets/solitons/minimal-ancient-flows.svg',import.meta.url),'utf8'));
});
