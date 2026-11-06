import test from 'node:test';
import assert from 'node:assert/strict';
import {abreschLanger,validateAbreschLanger} from '../site/assets/abresch-langer.mjs';

test('invalid indices explain the admissible range and repeated covers',()=>{
  for(const pair of [[0,3],[-2,3],[2.5,4],[NaN,3],[Infinity,5]])
    assert.throws(()=>abreschLanger(...pair),/positive whole numbers/);
  for(const pair of [[1,2],[3,4],[1,3]])
    assert.throws(()=>abreschLanger(...pair),/1\/2 < m\/ℓ < 1\/√2/);
  assert.throws(()=>abreschLanger(4,6),/traces \(2, 3\) 2 times/);
  assert.throws(()=>abreschLanger(71,101),/up to 100/);
});

test('energy quadrature agrees with independent SciPy DOP853 shooting',()=>{
  // Reference integrations of h''=2/h-h, rtol=2e-12, atol=2e-14,
  // max_step=.01, stopping at the next maximum; Brent period shooting.
  for(const [m,ell,maximum] of [
    [2,3,2.7345192018514157], [3,5,3.870040552916237],
    [5,8,3.4405570735754387], [12,17,1.622790210786712],
    [20,39,9.113111019988713]
  ]){
    const r=abreschLanger(m,ell);
    assert.ok(Math.abs(r.supportMaximum-maximum)<2e-9,`${m}, ${ell}`);
    assert.ok(Math.abs(r.period-2*Math.PI*m/ell)<1e-9);
  }
});

test('polygon geometry independently approximates the shrinker equation',()=>{
  for(const pair of [[2,3],[3,5],[5,8]]){
    const p=abreschLanger(...pair).vertices;
    for(let i=1;i<p.length-1;i++){
      const a=p[i-1],b=p[i],c=p[i+1];
      const u=[b[0]-a[0],b[1]-a[1]],v=[c[0]-b[0],c[1]-b[1]],w=[c[0]-a[0],c[1]-a[1]];
      const l=Math.hypot(...u),s=Math.hypot(...v);
      const curvature=2*(u[0]*v[1]-u[1]*v[0])/(l*s*Math.hypot(...w));
      const tx=u[0]/l+v[0]/s,ty=u[1]/l+v[1]/s;
      const support=(b[0]*ty-b[1]*tx)/Math.hypot(tx,ty);
      assert.ok(curvature>0);
      assert.ok(Math.abs(curvature-support/2)<6e-5);
    }
  }
});

test('every admitted pair through 100 produces finite, numerically closing geometry',()=>{
  let checked=0;
  for(let ell=1;ell<=100;ell++)for(let m=Math.floor(ell/2)+1;m<ell/Math.sqrt(2);m++){
    try{validateAbreschLanger(m,ell);}catch{continue;}
    const r=abreschLanger(m,ell);checked++;
    assert.ok(r.vertices.every(p=>p.length===3&&p.every(Number.isFinite)&&p[2]===0));
    assert.ok(r.closureError<1e-8,`${m}, ${ell}: closure`);
    assert.ok(r.quadratureChange<1e-9,`${m}, ${ell}: refinement`);
    assert.ok(r.periodError<1e-9,`${m}, ${ell}: period`);
  }
  assert.equal(checked,630);
});
