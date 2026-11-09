import test from 'node:test';
import assert from 'node:assert/strict';
import {STAGES,profile,radialPoint,finiteStage,surfaceMesh,scene,sceneSVG} from '../site/assets/immortal-product-viewer.mjs';
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-10,`${a} != ${b}`);
test('finite profiles preserve both reflections and positive neck orbits',()=>{
  for(const f of STAGES.filter(s=>!s.limit)){
    assert.ok(f.a>0&&f.a<Math.PI/2&&f.h>0&&f.h<=.25);
    close(profile(0,f.a,f.h)[0],f.a);close(profile(Math.PI,f.a,f.h)[0],Math.PI-f.a);
    for(let j=0;j<=160;j++){
      const s=2*Math.PI*j/160,[x,y]=profile(s,f.a,f.h),[xr,yr]=profile(-s,f.a,f.h),[xe,ye]=profile(Math.PI-s,f.a,f.h);
      close(x,xr);close(y,-yr);close(x+xe,Math.PI);close(y,ye);
      assert.ok(x>0&&x<Math.PI&&Math.abs(y)<=.25);
    }
  }
});
test('radial map preserves latitude and encodes height without crossing the origin',()=>{
  for(const x of [.1,.7,Math.PI/2,3])for(const y of [-.25,0,.25]){
    const p=radialPoint(x,y,.8),r=Math.hypot(...p);close(r,1+2*y);close(p[2]/r,Math.cos(x));
  }
});
test('finite playback never closes a neck or silently reaches the infinite-time limit',()=>{
  for(let j=0;j<=100;j++){const f=finiteStage(j/100);assert.ok(f.a>=.0649&&f.h>=.0279&&!f.limit);}
  for(const q of [-1,1.01,NaN,Infinity])assert.throws(()=>finiteStage(q),RangeError);
});
test('whole finite schematic is periodic and limit is one unit sphere',()=>{
  const ns=32,nt=24,m=surfaceMesh(STAGES[0],false,ns,nt);
  for(let j=0;j<=nt;j++)m.vertices[j].forEach((v,k)=>close(v,m.vertices[ns*(nt+1)+j][k]));
  for(let i=0;i<=ns;i++)m.vertices[i*(nt+1)].forEach((v,k)=>close(v,m.vertices[i*(nt+1)+nt][k]));
  for(const p of surfaceMesh(STAGES[3],false,ns,nt).vertices)close(Math.hypot(...p),1);
  assert.deepEqual(new Set(surfaceMesh(STAGES[3]).sheets),new Set([0]));
});
test('overview stacks four panels on mobile and keeps an accessible static fallback',()=>{
  assert.ok(scene(350).height>scene(960).height);
  const svg=sceneSVG(scene());assert.match(svg,/multiplicity 2/);assert.match(svg,/not computed PDE/);assert.match(svg,/t₃ &gt; t₂|t₃ > t₂/);assert.match(svg,/× 2/);
});
