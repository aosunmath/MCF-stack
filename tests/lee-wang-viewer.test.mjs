import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {realSlice,lift,project6,shrinkerPoint,CUT_RADIUS,snapshotSVG} from '../site/assets/lee-wang-viewer.mjs';
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const near=(a,b,tol=1e-9)=>assert.ok(Math.abs(a-b)<tol,`${a} != ${b}`);
test('Every sampled time satisfies the exact quadric and fixed physical crop',()=>{
 for(const t of [-2,-1,-.25,-.04,0,.25,1]){
  const m=realSlice(t);
  for(const [x,y,z] of m.vertices){near(x*x+y*y-z*z,-2*t);assert.ok(Math.hypot(x,y,z)<=CUT_RADIUS+1e-12);}
  near(Math.max(...m.vertices.map(p=>Math.hypot(...p))),CUT_RADIUS);
  for(const f of m.faces)for(const i of f)assert.ok(i>=0&&i<m.vertices.length);
  if(t<0)near(Math.min(...m.vertices.map(([x,y])=>Math.hypot(x,y))),Math.sqrt(-2*t));
  if(t>0)near(Math.min(...m.vertices.map(p=>Math.abs(p[2]))),Math.sqrt(2*t));
 }
 for(const t of [NaN,Infinity,-2.01,1.01])assert.throws(()=>realSlice(t),RangeError);
});
test('Phase gluing, six-dimensional norms, and self-similar time normalization agree',()=>{
 for(const [a,u,s,t] of [[.4,.7,.3,-1],[2,-1.2,2,-.04],[.8,0,1,-2]]){
  const p=shrinkerPoint(a,u,s,t),q=shrinkerPoint(a+Math.PI,-u,s-Math.PI,t);
  p.forEach((v,i)=>near(v,q[i]));near(dot(p,p),2*u*u-2*t);
  const scaled=shrinkerPoint(a,u/Math.sqrt(-t),s,-1).map(v=>v*Math.sqrt(-t));
  p.forEach((v,i)=>near(v,scaled[i]));
  assert.ok(Math.hypot(...project6(p))<=Math.hypot(...p)+1e-12);
 }
 assert.throws(()=>shrinkerPoint(0,1,0,0),RangeError);
 assert.throws(()=>lift([1,2,3],NaN),RangeError);
});
test('Independent normal Hessian trace equals the normal time derivative in R6',()=>{
 // The three parameter tangents are orthogonal; trace their normal second
 // derivatives directly. This checks the actual map, not just its radius law.
 for(const [theta,u,s,t] of [[.7,.6,.3,-1],[1.2,-.8,1.1,-.2],[.4,0,.2,-.04]]){
  const h=1e-4,args=[theta,u,s],f=q=>shrinkerPoint(...q,t),p=f(args);
  const shift=(i,v)=>f(args.map((a,j)=>a+(i===j?v:0)));
  const tangent=args.map((_,i)=>shift(i,h).map((v,j)=>(v-shift(i,-h)[j])/(2*h)));
  const normal=v=>v.map((a,j)=>a-tangent.reduce((sum,e)=>sum+dot(v,e)/dot(e,e)*e[j],0));
  const trace=Array(6).fill(0);
  tangent.forEach((e,i)=>shift(i,h).forEach((v,j)=>trace[j]+=(v+shift(i,-h)[j]-2*p[j])/(h*h*dot(e,e))));
  const velocity=shrinkerPoint(theta,u,s,t+h).map((v,j)=>(v-shrinkerPoint(theta,u,s,t-h)[j])/(2*h));
  const H=normal(trace),V=normal(velocity);H.forEach((v,j)=>near(v,V[j],1e-5));
  for(let i=0;i<3;i++)for(let j=0;j<3;j++)near([0,2,4].reduce((v,k)=>v+tangent[i][k]*tangent[j][k+1]-tangent[i][k+1]*tangent[j][k],0),0,2e-7);
 }
});
test('Fallback drawing is reproducible and identifies the slice and singular limit',()=>{
 const svg=snapshotSVG();assert.equal(svg,fs.readFileSync(new URL('../site/assets/solitons/lw-quadric-shrinkers.svg',import.meta.url),'utf8'));
 for(const label of ['t = −1','t = −0.25','t = −0.04','t = 0','Singular at the origin','not a surface MCF in R³','Same camera and spatial scale'])assert.ok(svg.includes(label));
});
