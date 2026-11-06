import test from 'node:test';
import assert from 'node:assert/strict';
import {nguyenModelUrl,nguyenNormals} from '../site/assets/nguyen-viewer.mjs';

test('Nguyen model routes distinguish a global period count from the local ingredient',()=>{
  const base='../../assets/solitons/nguyen-m-saddles.json';
  assert.equal(nguyenModelUrl(base,10),base);
  assert.equal(nguyenModelUrl(base,14),'../../assets/solitons/nguyen-m-saddles-14.json');
  assert.equal(nguyenModelUrl(base,'scherk'),'../../assets/solitons/nguyen-scherk-detail.json');
  assert.throws(()=>nguyenModelUrl(base,3));
});
test('Lighting normals preserve face orientation and avoid NaNs at degenerate faces',()=>{
  const v=[[0,0,0],[1,0,0],[0,1,0],[0,0,0]];
  assert.deepEqual(nguyenNormals(v,[[0,1,2],[0,3,0]]),[[0,0,1],[0,0,1],[0,0,1],[0,0,0]]);
  assert.deepEqual(nguyenNormals(v,[[0,2,1]])[0],[0,0,-1]);
});
