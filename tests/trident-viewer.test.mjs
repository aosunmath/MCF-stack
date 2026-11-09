import test from 'node:test';
import assert from 'node:assert/strict';
import {tridentModelUrl,tridentNormals} from '../site/assets/trident-viewer.mjs';

test('trident scale routes stay separate from Nguyen shrinking saddles',()=>{
  const base='../../assets/solitons/nguyen-tridents.json';
  assert.equal(tridentModelUrl(base,35),base);
  assert.equal(tridentModelUrl(base,22),'../../assets/solitons/nguyen-tridents-22.json');
  assert.equal(tridentModelUrl(base,50),'../../assets/solitons/nguyen-tridents-50.json');
  assert.throws(()=>tridentModelUrl(base,6));
});
test('trident lighting follows consistent triangle orientation',()=>{
  const v=[[0,0,0],[1,0,0],[0,1,0]];
  assert.deepEqual(tridentNormals(v,[[0,1,2]]),[[0,0,1],[0,0,1],[0,0,1]]);
  assert.deepEqual(tridentNormals(v,[[0,2,1]])[0],[0,0,-1]);
});
