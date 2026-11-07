import test from 'node:test';
import assert from 'node:assert/strict';
import {HMW_THREE_PARAMETERS,hmwThreeModelUrl,hmwThreeSites} from '../site/assets/hmw-three-ended-viewer.mjs';

test('three-ended models and the weight-three limit have distinct routes',()=>{
  const base='../../assets/solitons/hmw-three-ended.json';
  assert.equal(hmwThreeModelUrl(base,3),base);
  assert.equal(hmwThreeModelUrl(base,1),'../../assets/solitons/hmw-three-ended-1.json');
  assert.equal(hmwThreeModelUrl(base,7),'../../assets/solitons/hmw-three-ended-7.json');
  assert.equal(hmwThreeModelUrl(base,'limit'),'../../assets/solitons/hmw-three-plane-limit.json');
  assert.throws(()=>hmwThreeModelUrl(base,2));
});
test('upper and lower necks alternate between the horizontal trace lines',()=>{
  for(const g of HMW_THREE_PARAMETERS){
    const sites=hmwThreeSites(g);
    assert.deepEqual(sites.map(s=>s.length),[g+1,g+1]);
    sites.forEach((ring,gap)=>ring.forEach(([x,y])=>{
      assert.ok(Math.abs(Math.hypot(x,y)-1)<1e-12);
      assert.ok(Math.abs(Math.sin((g+1)*Math.atan2(y,x))-(gap===0?-1:1))<1e-12);
    }));
    // A half-turn about the x-axis exchanges the upper and lower sites.
    for(const [x,y] of sites[0])assert.ok(sites[1].some(([u,v])=>Math.hypot(x-u,y+v)<1e-12));
  }
});
