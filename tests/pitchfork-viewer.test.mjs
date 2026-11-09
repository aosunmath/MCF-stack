import test from 'node:test';
import assert from 'node:assert/strict';
import {pitchforkX,pitchforkSlice} from '../site/assets/pitchfork-viewer.mjs';

test('the joining line and half-turn agree at all illustrated heights',()=>{
  for(const z of [-5,-2,0,3,7]){
    assert.equal(pitchforkX(0,z),0);
    for(const y of [.001,.3,1,2,3.1])assert.ok(Math.abs(pitchforkX(y,z)+pitchforkX(-y,z))<1e-12);
  }
});
test('section segments stay within the window without joining distinct branches',()=>{
  for(const z of [-5,0,4,7]){
    const points=pitchforkSlice(z);
    assert.ok(points.length>10);assert.equal(points.length%2,0);
    for(let i=0;i<points.length;i+=2){
      const [a,b]=points.slice(i,i+2);
      assert.ok(Math.abs(a[0])<=6.00000001&&Math.abs(b[0])<=6.00000001);
      assert.ok(Math.abs(a[1]-b[1])<.004);
      assert.equal(a[2],z);assert.equal(b[2],z);
    }
  }
});
test('a fixed vertical line crosses one low sheet and three high sheets',()=>{
  const roots=z=>{
    const points=pitchforkSlice(z,6,12000),ys=[];
    for(let i=0;i<points.length;i+=2){const [a,b]=points.slice(i,i+2);if((a[0]-1)*(b[0]-1)<0)ys.push(a[1]+(1-a[0])*(b[1]-a[1])/(b[0]-a[0]));}
    return ys;
  };
  const low=roots(-5),high=roots(7);
  assert.equal(low.length,1);assert.ok(Math.abs(low[0])<.2);
  assert.equal(high.length,3);
  for(const [i,target] of [-Math.PI,0,Math.PI].entries())assert.ok(Math.abs(high[i]-target)<.1);
});
