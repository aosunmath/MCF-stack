import test from 'node:test';
import assert from 'node:assert/strict';
import {endSliceScale,endModelUrl} from '../site/assets/sun-wang-end-viewer.mjs';

test('height ratios 1:4:9 give physical size ratios 1:2:3, while rescaled slices agree',()=>{
  assert.deepEqual([1,4,9].map(r=>endSliceScale(r)),[1,2,3]);
  for(const r of [1,2.7,4,6.3,9])assert.equal(endSliceScale(r,true),1);
  for(const r of [0,-1,10,NaN,Infinity])assert.throws(()=>endSliceScale(r));
});

test('all bridge counts reuse the audited input-shrinker assets under the Pages prefix',()=>{
  const base='/MCF-stack/assets/solitons/sun-wang-doubled-sphere-end.json';
  for(const m of [6,10,14])assert.equal(endModelUrl(base,m),`/MCF-stack/assets/solitons/sphere-doubling-shrinker${m===10?'':`-${m}`}.json`);
  assert.throws(()=>endModelUrl(base,2));
});
