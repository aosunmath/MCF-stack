import test from 'node:test';
import assert from 'node:assert/strict';
import {LW,slicePoint,circlePoint,sliceMesh,surfaceScene} from '../site/assets/lee-wang-expander-viewer.mjs';
const dot=(a,b)=>a.reduce((sum,x,i)=>sum+x*b[i],0);
const close=(a,b,eps=1e-10)=>assert.ok(Math.abs(a-b)<eps,`${a} != ${b}`);

test('exact quadric, homothetic time scaling and both real sheets',()=>{
  for(const t of [.02,.25,1,4])for(const sign of [-1,1])for(const r of [0,.5,3.2])for(const theta of [0,.4,2.1]){
    const p=slicePoint(r,theta,t,sign);close(p[2]**2-p[0]**2-p[1]**2,2*t);
    slicePoint(r/Math.sqrt(t),theta,1,sign).forEach((v,i)=>close(v*Math.sqrt(t),p[i]));
  }
  for(const t of LW.times)close(slicePoint(0,0,t)[2],Math.sqrt(2*t));
  assert.throws(()=>slicePoint(1,0,-1));assert.throws(()=>slicePoint(Infinity,0,1));
});

test('circle orbit preserves lengths and has opposite real-sheet endpoints',()=>{
  const x=slicePoint(1,.7,1),norm=dot(x,x);
  for(const s of [0,.3,Math.PI/2,Math.PI,2*Math.PI]){
    const p=circlePoint(x,s);close(dot(p,p),norm);
    close(p[4]**2+p[5]**2-p[0]**2-p[1]**2-p[2]**2-p[3]**2,2);
  }
  const a=circlePoint(x,0),b=circlePoint(x,Math.PI),mid=circlePoint(x,Math.PI/2);
  a.forEach((v,i)=>close(b[i],-v));close(dot(a,mid),0);
  assert.ok(mid.some((v,i)=>i%2===1&&Math.abs(v)>.1));
});

test('the positive-time slice mesh consists of two disks with only outer boundaries',()=>{
  const g=sliceMesh(1,8,24),edges=new Map(),neighbors=g.vertices.map(()=>new Set());
  for(const f of g.faces){assert.equal(new Set(f).size,3);for(let j=0;j<3;j++){
    const a=f[j],b=f[(j+1)%3],key=[a,b].sort((x,y)=>x-y).join(',');edges.set(key,(edges.get(key)||0)+1);neighbors[a].add(b);neighbors[b].add(a);
  }}
  assert.equal(g.vertices.length-edges.size+g.faces.length,2);assert.equal([...edges.values()].filter(v=>v===1).length,48);
  for(const [key,count] of edges){assert.ok(count===1||count===2);if(count===1)for(const i of key.split(',').map(Number))close(Math.hypot(...g.vertices[i].slice(0,2)),LW.radius);}
  let components=0;const seen=new Set();for(let i=0;i<g.vertices.length;i++)if(!seen.has(i)){components++;const queue=[i];seen.add(i);for(const j of queue)for(const k of neighbors[j])if(!seen.has(k)){seen.add(k);queue.push(k);}}
  assert.equal(components,2);
  const scales=LW.times.map(t=>surfaceScene(t,{x:0,y:0,w:320,h:300}).scale);assert.ok(scales.every(s=>s===scales[0]));
});

// Independent differential check of the full three-fold F_t(a,b,s).
// H is the normal part of g^{ij} F_ij; compare with (dF/dt)^perp.
test('the full C3 parametrization is Lagrangian and satisfies MCF',()=>{
  for(const [a,b,t,s] of [[0,0,.25,.3],[.7,-.4,1,1.1],[2,1,4,2.5]]){
    const h=Math.sqrt(a*a+b*b+2*t),c=Math.cos(s),d=Math.sin(s);
    const basis=[[c,d,0,0,a*c/h,-a*d/h],[0,0,c,d,b*c/h,-b*d/h],[-a*d,a*c,-b*d,b*c,-h*d,-h*c]];
    const g=basis.map(u=>basis.map(v=>dot(u,v)));
    // g_as = g_bs = 0, so invert the 2x2 block and the circle direction.
    const det=g[0][0]*g[1][1]-g[0][1]**2;
    const inv=[[g[1][1]/det,-g[0][1]/det,0],[-g[0][1]/det,g[0][0]/det,0],[0,0,1/g[2][2]]];
    // Explicit function avoids sharing any implementation with the renderer.
    function normal(v){const coeff=inv.map(row=>row.reduce((sum,x,j)=>sum+x*dot(basis[j],v),0));return v.map((x,k)=>x-basis.reduce((sum,u,j)=>sum+u[k]*coeff[j],0));}
    const aa=(b*b+2*t)/h**3,bb=(a*a+2*t)/h**3,ab=-a*b/h**3;
    const Faa=[0,0,0,0,aa*c,-aa*d],Fbb=[0,0,0,0,bb*c,-bb*d],Fab=[0,0,0,0,ab*c,-ab*d];
    const Fss=circlePoint([a,b,h],s).map(v=>-v);
    const H=normal(Faa.map((v,k)=>inv[0][0]*v+2*inv[0][1]*Fab[k]+inv[1][1]*Fbb[k]+inv[2][2]*Fss[k]));
    const velocity=normal([0,0,0,0,c/h,-d/h]);H.forEach((v,i)=>close(v,velocity[i]));
    const radial=normal(circlePoint([a,b,h],s));H.forEach((v,i)=>close(v,radial[i]/(2*t)));
    for(const u of basis)for(const v of basis)close(u.reduce((sum,x,j)=>j%2===0?sum+x*v[j+1]-u[j+1]*v[j]:sum,0),0);
  }
});
