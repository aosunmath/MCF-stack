import test from 'node:test';
import assert from 'node:assert/strict';
import {sphericalGap,sphericalModelUrl,sphericalNormals} from '../site/assets/spherical-doubling-viewer.mjs';

test('model choices resolve within the same asset directory',()=>{
  const base='../../assets/solitons/sphere-doubling-shrinker.json';
  assert.equal(sphericalModelUrl(base,10),base);
  assert.equal(sphericalModelUrl(base,14),'../../assets/solitons/sphere-doubling-shrinker-14.json');
  assert.throws(()=>sphericalModelUrl(base,2));
});

test('separation keeps the base sphere fixed and preserves radial ordering',()=>{
  const points=[[1.8,0,0],[2,0,0],[2.2,0,0]];
  assert.deepEqual(sphericalGap(points,1),points);
  for(const factor of [.6,1.8]){
    const result=sphericalGap(points,factor);
    assert.deepEqual(result[1],[2,0,0]);
    assert.ok(result[0][0]<2&&result[2][0]>2);
    assert.ok(Math.abs(result[2][0]-result[0][0]-.4*factor)<1e-12);
  }
  assert.throws(()=>sphericalGap(points,0));
});

test('normals follow oriented faces after a geometry update',()=>{
  const p=[[0,0,0],[1,0,0],[0,1,0]];
  assert.deepEqual(sphericalNormals(p,[[0,1,2]]),[[0,0,1],[0,0,1],[0,0,1]]);
  assert.deepEqual(sphericalNormals(p,[[0,2,1]]),[[0,0,-1],[0,0,-1],[0,0,-1]]);
});
