import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {commonLiteratureBounds,rotateLiteraturePoint} from '../site/assets/literature-flow-viewer.mjs';
const manifest=JSON.parse(fs.readFileSync(new URL('../documentation/literature-additions.json',import.meta.url)));
const load=e=>JSON.parse(fs.readFileSync(new URL('../site/assets/solitons/literature-'+e.id+'.json',import.meta.url)));
test('every added family has finite geometry, distinct time slices and declared accuracy',()=>{
 for(const e of manifest.entries){const d=load(e);assert.equal(d.frames.length,3,e.id);assert.ok(d.displayStatus);assert.notDeepEqual(d.frames[0].vertices,d.frames[2].vertices,e.id+' must illustrate motion');
  for(const f of [...d.frames,...(d.variants||[]).flatMap(v=>v.frames)]){assert.ok(f.vertices.length);for(const p of f.vertices){assert.equal(p.length,3);assert.ok(p.every(Number.isFinite),e.id);}for(const p of [...f.paths,...f.faces])for(const i of p)assert.ok(Number.isInteger(i)&&i>=0&&i<f.vertices.length,e.id);}
 }
});
test('homothetic frames preserve all geometry and apply the stated physical time scale',()=>{
 for(const e of manifest.entries.filter(e=>['shrinkers','expanders'].includes(e.category)&&e.visual.kind!=='tetrahedral-junction'&&e.visual.kind!=='graph-expander')){
  const d=load(e),ratios=e.category==='shrinkers'?[2,1,.5]:[.5,1,2];
  d.frames.forEach((f,k)=>f.vertices.forEach((v,i)=>v.forEach((x,j)=>assert.ok(Math.abs(x-ratios[k]*d.frames[1].vertices[i][j])<3e-7,e.id))));
 }
});
test('common bounds retain translating displacement and are rotation independent',()=>{
 const frames=[{vertices:[[0,0,0],[1,0,0]]},{vertices:[[0,0,4],[1,0,4]]}];const b=commonLiteratureBounds(frames);assert.deepEqual(b.center,[.5,0,2]);assert.ok(b.radius>2);
 const p=[2,3,4],q=rotateLiteraturePoint(p,.7,-.4);assert.ok(Math.abs(Math.hypot(...p)-Math.hypot(...q))<1e-12);
});
test('numerical junction and closure diagnostics remain within sampled tolerances',()=>{
 const d=JSON.parse(fs.readFileSync(new URL('../documentation/literature-figure-diagnostics.json',import.meta.url)));
 for(const [name,a] of Object.entries(d)){if(a.shooting_angle_error!==undefined)assert.ok(a.shooting_angle_error<1e-8,name);if(a.phase_closure_error!==undefined)assert.ok(a.phase_closure_error<1e-8,name);}
 assert.ok(d['graph-expander'].max_refinement_difference.every(x=>x<1.1e-4));assert.ok(d['lens-cluster'].slope_residual<1e-8);
});
