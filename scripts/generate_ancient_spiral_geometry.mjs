// Original numerical illustration of ZOKA, arXiv:2204.05253v3, §2 and Appendix A.
// Run: node scripts/generate_ancient_spiral_geometry.mjs (no dependencies).
import {writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
import {spiralFrame, snapshotSVG} from '../site/assets/ancient-spiral-viewer.mjs';

export function rk4(f, t, y, h) {
  const a=f(t,y), b=f(t+h/2,y.map((v,i)=>v+h*a[i]/2));
  const c=f(t+h/2,y.map((v,i)=>v+h*b[i]/2)), d=f(t+h,y.map((v,i)=>v+h*c[i]));
  return y.map((v,i)=>v+h*(a[i]+2*b[i]+2*c[i]+d[i])/6);
}

export function solveModel(h=.002) {
  // κ=<X,T>, hence tangent angle φ=|X|²/2 for X(0)=0, T(0)=(1,0).
  const rhs=(_s,[x,y])=>[Math.cos((x*x+y*y)/2),Math.sin((x*x+y*y)/2)];
  let xy=[0,0], angle=0, previous=0, step=0;
  const branch=[[Math.PI/2,0,0]], stride=Math.round(.05/h);
  while(angle<51) {
    xy=rk4(rhs,step*h,xy,h);step++;
    const a=Math.atan2(xy[1],xy[0]);
    angle+=Math.atan2(Math.sin(a-previous),Math.cos(a-previous));previous=a;
    if(step%stride===0)branch.push([angle+Math.PI/2,...xy]);
  }
  const correction=[[0,0]];
  const f=(p,[F])=>{
    const u=-Math.asin(Math.tanh(p)),v=-Math.log(Math.cosh(p));
    return [2*v-(u*u+v*v)/2-1-Math.tanh(p)*F];
  };
  let F=[0];
  for(let j=1;j<=Math.round(14/h);j++){
    F=rk4(f,(j-1)*h,F,h);
    if(j%Math.round(.02/h)===0)correction.push([j*h,F[0]]);
  }
  return {branch,correction};
}

if(process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const data={kind:'ancient-spiral-asymptotic',status:'numerical-ode',
    source:'https://arxiv.org/abs/2204.05253v3',
    description:'Numerical Yin–Yang ODE with the corrected asymptotic cap, not a computed ancient CSF solution.',
    time:{min:-24,max:-8,value:-18},snapshots:[-24,-18,-12,-8],...solveModel()};
  const frame=spiralFrame(data,-18);
  data.vertices=frame.body.map(p=>[...p,0]);data.faces=[];data.paths=[data.vertices.map((_,i)=>i)];
  const out=new URL('../site/assets/solitons/',import.meta.url);
  writeFileSync(new URL('ancient-spiral-curves.json',out),JSON.stringify(data)+'\n');
  writeFileSync(new URL('ancient-spiral-curves.svg',out),snapshotSVG(data));
  console.log(`Wrote Yin–Yang table (${data.branch.length} points), cap correction and four snapshots.`);
}
