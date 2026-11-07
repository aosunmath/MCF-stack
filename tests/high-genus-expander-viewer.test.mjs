import test from 'node:test';
import assert from 'node:assert/strict';
import {expanderModelUrl,expanderSurface,expanderNormals} from '../site/assets/high-genus-expander-viewer.mjs';

test('only supported illustrative counts load from the same asset base',()=>{
  assert.equal(expanderModelUrl('/assets/solitons/high-genus-expanders.json',4),'/assets/solitons/high-genus-expanders.json');
  assert.equal(expanderModelUrl('/assets/solitons/high-genus-expanders.json',12),'/assets/solitons/high-genus-expanders-12.json');
  assert.throws(()=>expanderModelUrl('high-genus-expanders.json',8));
});
test('changing slice type reverses the core while retaining the cone shear and winding',()=>{
  const data={vertices:[[0,0,0],[1,0,1],[0,1,1]],faces:[[0,1,2]],endShear:[0,.1,.2],vertexColors:[[1,2,3],[2,3,4],[3,4,5]]};
  const a=expanderSurface(data,1),b=expanderSurface(data,2);
  assert.deepEqual(a.vertices,[[0,0,0],[1,0,1.1],[0,1,1.2]]);
  assert.deepEqual(b.vertices,[[0,0,0],[1,0,-.9],[0,1,-.8]]);
  assert.deepEqual(b.faces,[[0,2,1]]);
  assert.deepEqual(data.faces,[[0,1,2]]);
  assert.throws(()=>expanderSurface(data,0));
  for(const n of expanderNormals(b.vertices,b.faces))assert.ok(Math.abs(Math.hypot(...n)-1)<1e-12);
});
