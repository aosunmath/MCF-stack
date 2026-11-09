import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {HMW_CASES,hmwModelUrl} from '../site/assets/hmw-rays-viewer.mjs';

test('every symmetry loads its own audited model and genus',()=>{
  const base='../site/assets/solitons/hmw-platonic-polygon.json';
  for(const [key,label] of Object.entries(HMW_CASES)){
    const model=JSON.parse(readFileSync(new URL(hmwModelUrl(base,key),import.meta.url)));
    assert.equal(model.case,key);
    assert.equal(model.status,'schematic');
    assert.equal(model.rayCount,model.genus+1);
    assert.ok(label.endsWith(`genus ${model.genus}`));
  }
  assert.equal(hmwModelUrl(base,'cube'),base);
  assert.throws(()=>hmwModelUrl(base,'../unrelated'));
});
