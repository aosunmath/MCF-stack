import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {frameProfile,surfaceVertices,timeLabel} from '../site/assets/hh-ancient-oval-viewer.mjs';
const data=JSON.parse(readFileSync(new URL('../site/assets/solitons/hh-ancient-ovals.json',import.meta.url)));
test('physical views undo parabolic rescaling without frame-by-frame auto-fit',()=>{
  for(const f of data.frames){const rescaled=frameProfile(f),physical=frameProfile(f,'physical');
    rescaled.forEach((p,i)=>p.forEach((x,k)=>assert.ok(Math.abs(physical[i][k]-x*Math.sqrt(-f.time))<1e-10)));
  }
  assert.throws(()=>frameProfile(data.frames[0],'arbitrary'));
});
test('every time slice uses a compatible closed revolution mesh with single poles',()=>{
  for(const f of [data.frames[0],data.frames[60],data.frames.at(-1)]){
    const v=surfaceVertices(f.profile,data.segments);assert.equal(v.length,data.vertices.length);
    assert.deepEqual(v[0],[f.profile[0][0],0,0]);assert.deepEqual(v.at(-1),[f.profile.at(-1)[0],0,0]);
    assert.ok(data.faces.flat().every(i=>i>=0&&i<v.length));
    for(const p of v)assert.ok(p.every(Number.isFinite));
  }
  const v=surfaceVertices(data.frames[data.default_frame].profile,data.segments);
  v.forEach((p,i)=>p.forEach((x,k)=>assert.ok(Math.abs(x-data.vertices[i][k])<1e-7)));
});
test('time labels retain late-time precision',()=>{
  assert.equal(timeLabel(-.001),'−0.001');assert.equal(timeLabel(-1000),'−1000');
});
