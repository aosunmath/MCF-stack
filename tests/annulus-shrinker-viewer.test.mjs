import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {shrinkerScale,continueExcursion} from '../site/assets/annulus-shrinker-viewer.mjs';

const data=JSON.parse(readFileSync(new URL('../site/assets/solitons/halldorsson-dense.json',import.meta.url)));

test('all frames contract the same segment with the canonical time law',()=>{
  assert.deepEqual(data.snapshot_times.map(shrinkerScale),[2,1,.5,.25]);
  assert.throws(()=>shrinkerScale(0),RangeError);
  assert.throws(()=>shrinkerScale(1),RangeError);
  for(const v of data.variants) {
    const initial=continueExcursion(v.base,v.alpha,7);
    for(const time of data.snapshot_times) {
      const moved=continueExcursion(v.base,v.alpha,7,time);
      for(const i of [0,113,400,800])for(let k=0;k<2;k++)assert.ok(Math.abs(moved[i][k]-initial[i][k]*Math.sqrt(-time))<1e-12);
    }
  }
});

test('continuations join smoothly while the displayed finite window remains open',()=>{
  for(const v of data.variants) {
    for(const j of [0,11,143]) {
      const a=continueExcursion(v.base,v.alpha,j),b=continueExcursion(v.base,v.alpha,j+1);
      assert.ok(Math.hypot(a.at(-1)[0]-b[0][0],a.at(-1)[1]-b[0][1])<1e-8);
    }
    const end=continueExcursion(v.base,v.alpha,11).at(-1),start=v.base[0];
    assert.ok(Math.hypot(end[0]-start[0],end[1]-start[1])>.01);
  }
});

test('normal velocity equals curvature, independently differentiated from sampled positions',()=>{
  for(const v of data.variants)for(const t of [-4,-1,-.25]) {
    const ds=v.period/(v.base.length-1),dt=1e-5;
    const curve=continueExcursion(v.base,v.alpha,0,t);
    for(const i of [40,150,300,400,650,750]) {
      const p=curve[i],a=curve[i-1],b=curve[i+1];
      const dx=(b[0]-a[0])/(2*ds),dy=(b[1]-a[1])/(2*ds),speed=Math.hypot(dx,dy);
      const ddx=(b[0]-2*p[0]+a[0])/(ds*ds),ddy=(b[1]-2*p[1]+a[1])/(ds*ds);
      const k=(dx*ddy-dy*ddx)/(speed**3);
      const before=continueExcursion([v.base[i]],0,0,t-dt)[0],after=continueExcursion([v.base[i]],0,0,t+dt)[0];
      const normalVelocity=(-(after[0]-before[0])*dy+(after[1]-before[1])*dx)/(2*dt*speed);
      assert.ok(Math.abs(k-normalVelocity)<.002,`${v.name}: ${k} vs ${normalVelocity}`);
    }
  }
});
