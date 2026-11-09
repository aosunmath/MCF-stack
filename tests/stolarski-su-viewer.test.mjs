import test from 'node:test';
import assert from 'node:assert/strict';
import {SS,validCase,neckScale,lawlorPoint,profile,slicePoint,neckMesh,surfaceScene,defaultCamera,project4} from '../site/assets/stolarski-su-viewer.mjs';
const close=(a,b,eps=1e-8)=>assert.ok(Math.abs(a-b)<eps,`${a} != ${b}`);
const mul=([a,b],[c,d])=>[a*c-b*d,a*d+b*c];
const power=(p,n)=>Array.from({length:n}).reduce(a=>mul(a,p),[1,0]);

test('Lawlor profile lies on Re(w^n)=a^n and its radius has a unique minimum',()=>{
  for(const n of [3,4,5,6])for(const a of [.03,.2,.7]){
    for(const v of [-4,-1,0,.4,3]){
      const w=lawlorPoint(n,a,v),wn=power(w,n);
      close(wn[0],a**n);close(wn[1],a**n*Math.sinh(v));
      assert.ok(Math.hypot(...w)>=a-1e-12);
    }
    close(Math.hypot(...lawlorPoint(n,a,0)),a);
    const p=profile(n,a);close(Math.hypot(...p[0]),SS.radius);close(Math.hypot(...p.at(-1)),SS.radius);
    close(p[p.length>>1][0],a);close(p[p.length>>1][1],0);
  }
});

test('neck is Lagrangian with constant phase and satisfies the stationary graphical PDE',()=>{
  const delta=1e-4;
  for(const n of [3,4,6])for(const a of [.2,.7])for(const v of [-2,-.4,0,1.5]){
    const w=lawlorPoint(n,a,v),lo=lawlorPoint(n,a,v-delta),hi=lawlorPoint(n,a,v+delta);
    const d=hi.map((q,i)=>(q-lo[i])/(2*delta)),dd=hi.map((q,i)=>(q-2*w[i]+lo[i])/(delta**2));
    const volume=mul(power(w,n-1),d);close(volume[0]/Math.hypot(...volume),0,1e-7);
    const [f,x]=w,[fp,xp]=d,[fpp,xpp]=dd;
    const fx=fp/xp,fxx=(fpp*xp-fp*xpp)/xp**3;
    close(fxx/(1+fx*fx)+(n-1)*(x*fx-f)/(x*x+f*f),0,4e-5);
    // omega(d_v X,d_phi X)=0 on a great-circle orbit.
    const phi=.73,cos=Math.cos(phi),sin=Math.sin(phi);
    const dv=[d[0]*cos,d[0]*sin,d[1]*cos,d[1]*sin],dp=[-w[0]*sin,w[0]*cos,-w[1]*sin,w[1]*cos];
    close(dv[0]*dp[2]+dv[1]*dp[3]-dv[2]*dp[0]-dv[3]*dp[1],0);
  }
});

test('prescribed moving neck has a nonzero MCF residual; scales stay distinct',()=>{
  for(const n of [3,4,6])for(const k of [2,3,4])for(const t of [0,.6,.9,.98]){
    const q=1-t,a=neckScale(t,k,'physical',n);
    close(neckScale(t,k,'parabolic',n),a/Math.sqrt(q));
    close(neckScale(t,k,'neck',n),a/q**(k/2));
    const at=-SS.a0*k/2*q**(k/2-1);
    assert.ok(at<0); // At the waist f_t=a'(t), but the stationary RHS is 0.
  }
  assert.ok(neckScale(.98,4,'parabolic')<neckScale(.9,4,'parabolic'));
  assert.equal(neckScale(.98,4,'neck'),neckScale(0,4,'neck'));
  for(const [n,k]of [[2,2],[3,5],[3,1],[4,1],[3,2.5]]){assert.equal(validCase(n,k),false);assert.throws(()=>neckScale(.5,k,'physical',n));}
  assert.equal(validCase(4,100),true);
  for(const t of [-1,1,NaN,Infinity])assert.throws(()=>neckScale(t,2));
});

test('mesh is a connected annular slice with two boundary circles, not a whole n-manifold',()=>{
  const mesh=neckMesh(3,.07,20,32),edges=new Map(),adj=mesh.vertices.map(()=>new Set());
  for(const f of mesh.faces)for(let i=0;i<3;i++){
    const a=f[i],b=f[(i+1)%3],key=[a,b].sort((x,y)=>x-y).join(',');
    assert.ok(a>=0&&a<mesh.vertices.length);edges.set(key,(edges.get(key)||0)+1);adj[a].add(b);adj[b].add(a);
  }
  assert.ok([...edges.values()].every(v=>v===1||v===2));
  assert.equal([...edges.values()].filter(v=>v===1).length,64);
  assert.equal(mesh.vertices.length-edges.size+mesh.faces.length,0);
  const seen=new Set([0]),queue=[0];for(const a of queue)for(const b of adj[a])if(!seen.has(b)){seen.add(b);queue.push(b);}assert.equal(seen.size,mesh.vertices.length);
  assert.ok(mesh.vertices.every(p=>p.length===4&&p.every(Number.isFinite)));
});

test('projection and time panels use a fixed camera, origin, and radius',()=>{
  const state=defaultCamera(),box={x:0,y:0,w:320,h:250};
  const early=surfaceScene(3,.7,box,state,[12,20]),late=surfaceScene(3,.0001,box,state,[12,20]);
  close(early.scale,late.scale);assert.deepEqual(early.project([0,0,0,0]),late.project([0,0,0,0]));
  for(const scene of [early,late])assert.ok(scene.polygons.every(p=>p.points.flat().every(Number.isFinite)));
  const p=slicePoint([1,.4],.7);assert.ok(Math.hypot(...project4(p,state))<=Math.hypot(...p)+1e-12);
  for(const phi of [0,.7,1.8])close(Math.hypot(...slicePoint([.7,0],phi)),.7);
  const full=surfaceScene(3,.7,box,{...state,cutaway:false},[12,20]);
  assert.equal(early.polygons.length*2,full.polygons.length);
});
