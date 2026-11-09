import test from 'node:test';
import assert from 'node:assert/strict';
import {hmwAxes, hmwModelUrl, HMW_GENERA} from '../site/assets/hmw-sphere-plane-viewer.mjs';

test('HMW trace consists of g+1 distinct equally spaced lines, with opposite endpoints',()=>{
  for(const g of HMW_GENERA){
    const lines=hmwAxes(g);
    assert.equal(lines.length,g+1);
    lines.forEach(([a,b],j)=>{
      for(let k=0;k<3;k++)assert.ok(Math.abs(a[k]+b[k])<1e-12);
      assert.equal(b[2],0);
      assert.ok(Math.abs(Math.hypot(...b)-3.8)<1e-12);
      assert.ok(Math.abs(Math.atan2(b[1],b[0])-j*Math.PI/(g+1))<1e-12);
    });
  }
});
test('HMW routes keep the singular limit separate from finite-genus models',()=>{
  const base='../../assets/solitons/hmw-one-ended.json';
  assert.equal(hmwModelUrl(base,5),base);
  assert.equal(hmwModelUrl(base,11),'../../assets/solitons/hmw-one-ended-11.json');
  assert.equal(hmwModelUrl(base,'limit'),'../../assets/solitons/hmw-sphere-plane-limit.json');
  assert.throws(()=>hmwModelUrl(base,1));
});
