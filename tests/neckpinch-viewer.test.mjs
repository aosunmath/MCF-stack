import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {neckpinchProfile,scales,bowlHeight,innerRadius,TIMES} from '../site/assets/neckpinch-geometry.mjs';
const data=JSON.parse(fs.readFileSync(new URL('../site/assets/solitons/neckpinch-scales.json',import.meta.url)));

test('Regular slices close at two poles, remain embedded meridians, and move the tip toward zero',()=>{
  let previous=-Infinity;
  for(const s of [1e-3,1e-4,1e-5,1e-6,1e-7]){
    const p=neckpinchProfile(s,data);
    assert.ok(p[0][0]>previous);previous=p[0][0];
    assert.equal(p[0][0],scales(s).tip);assert.equal(p[0][1],0);assert.equal(p.at(-1)[1],0);
    p.forEach(([x,r],i)=>{assert.ok(Number.isFinite(x)&&Number.isFinite(r));if(i>0&&i<p.length-1)assert.ok(r>0);if(i>0)assert.ok(x>p[i-1][0]);});
  }
});
test('The regular bowl tip has trace curvature one, rather than a paraboloid substituted globally',()=>{
  const r=1e-4;
  assert.ok(Math.abs(4*bowlHeight(r,data)/(r*r)-1)<1e-6);
  assert.ok(Math.abs(bowlHeight(3,data)-9/4)>.2);
  assert.ok(data.audit.refined_max_difference<1e-8);
  assert.equal(data.audit.full_flow_solved,false);
});
test('Parabolic correction has the signed cubic Hermite bulge and neck',()=>{
  const s=1e-5;
  assert.ok(innerRadius(-Math.sqrt(2),s)>Math.SQRT2);
  assert.ok(innerRadius(Math.sqrt(2),s)<Math.SQRT2);
  assert.equal(innerRadius(0,s),Math.SQRT2);
});
test('The final panel is a one-sided cusp and is excluded from smooth scaling formulas',()=>{
  assert.equal(TIMES.at(-1),0);const p=neckpinchProfile(0,data);
  assert.deepEqual(p[0],[0,0]);assert.ok(p.every(([x])=>x>=0));
  const [x,r]=p[1];assert.ok(Math.abs(r/x**1.5-1)<1e-6);
  assert.throws(()=>scales(0));assert.throws(()=>neckpinchProfile(-1,data));
});
test('Type-II scale separates from the parabolic scale as the singular time is approached',()=>{
  const a=scales(1e-3),b=scales(1e-7);
  assert.ok(1/b.H/b.radial<1/a.H/a.radial);
  assert.ok(Math.abs(b.H*(-b.tip)**2-2/3)<1e-12);
});
