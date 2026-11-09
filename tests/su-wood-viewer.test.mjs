import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {profilePoint,profileMesh,lift,scene,snapshotSVG,TIMES} from '../site/assets/su-wood-viewer.mjs';
const near=(a,b,tol=1e-9)=>assert.ok(Math.abs(a-b)<tol,`${a} != ${b}`);
const mul=([a,b],[c,d])=>[a*c-b*d,a*d+b*c];
test('Closed hyperbolic formula agrees with Su–Wood (31) in the original polar coordinates',()=>{
  for(const [u,v,mu] of [[.7,-.4,1],[-.3,.9,.6],[1.2,.4,1.4],[0,0,1]]){
    const polar=w=>{const s=Math.atan(Math.tanh(w)),r=1/Math.sqrt(Math.cos(2*s));return {s,r,l:[r*Math.cos(s),r*Math.sin(s)],B:.5*Math.asinh(Math.tan(2*s))};};
    const x=polar(u),y=polar(v),z=mul(x.l,y.l).map(a=>mu*a);
    const expected=[...z,(mu*mu*y.r*y.r-x.r*x.r)/2,mu*mu*y.B-x.B];
    const got=profilePoint(Math.sinh(u+v),v-u,mu);got.forEach((a,i)=>near(a,expected[i]));
  }
});
test('All flow times give exactly the same coordinates and rendered geometry',()=>{
  for(const t of [...TIMES,-100,100]){
    assert.deepEqual(profileMesh(.8,t,8),profileMesh(.8,0,8));
    assert.deepEqual(scene({t}),scene({t:0}));
  }
  for(const mu of [0,-1,NaN,Infinity])assert.throws(()=>profilePoint(0,0,mu),RangeError);
});
test('Full six-dimensional lift is Lagrangian and has constant calibrated phase',()=>{
  // Independent finite differences of all three tangents; check omega=0 and
  // Im(dz1 wedge dz2 wedge dz3)=0, with positive nonzero real determinant.
  const determinant=m=>{
    let out=[0,0];
    for(const [perm,sign] of [[[0,1,2],1],[[1,2,0],1],[[2,0,1],1],[[2,1,0],-1],[[1,0,2],-1],[[0,2,1],-1]]){
      const c=mul(mul(m[0][perm[0]],m[1][perm[1]]),m[2][perm[2]]);out=out.map((v,i)=>v+sign*c[i]);
    }return out;
  };
  for(const [p,b,theta,mu] of [[0,0,0,1],[.7,-.4,.8,.6],[-1.1,.9,2,1.4]]){
    const a=[theta,p,b],f=q=>lift(profilePoint(q[1],q[2],mu),q[0]),h=1e-5;
    const D=a.map((_,i)=>{const plus=f(a.map((v,j)=>v+(i===j?h:0))),minus=f(a.map((v,j)=>v-(i===j?h:0)));return plus.map((v,j)=>(v-minus[j])/(2*h));});
    for(let i=0;i<3;i++)for(let j=0;j<3;j++)near([0,2,4].reduce((s,k)=>s+D[i][k]*D[j][k+1]-D[i][k+1]*D[j][k],0),0,1e-7);
    const det=determinant(D.map(v=>[[v[0],v[1]],[v[2],v[3]],[v[4],v[5]]]));near(det[1],0,1e-7);assert.ok(det[0]>0);
    const q=profilePoint(p,b,mu),x=lift(q,theta);near(x.reduce((s,v)=>s+v*v,0),q.reduce((s,v)=>s+v*v,0));
  }
});
test('Exact default graphical projection and deterministic fallback retain dimensional caveats',()=>{
  for(const p of [-2,0,2])for(const b of [-1.2,0,1.2]){
    const q=profilePoint(p,b);[Math.cosh(b),p,p*Math.sinh(b),b].forEach((v,i)=>near(q[i],v));
  }
  assert.equal(snapshotSVG(),fs.readFileSync(new URL('../site/assets/solitons/su-wood-stationary.svg',import.meta.url),'utf8'));
  for(const label of ['t = −2','t = 0','t = 2','not a surface MCF in R³','Same camera, scale'])assert.ok(snapshotSVG().includes(label));
});
