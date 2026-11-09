import test from 'node:test';
import assert from 'node:assert/strict';
import {ancientOval,rotatePoint,revolutionFaces} from '../site/assets/soliton-viewer.mjs';
import {readFileSync} from 'node:fs';

test('Drugan cutaway removes only selected angular sectors and restores the complete surface',()=>{
  const d=JSON.parse(readFileSync(new URL('../site/assets/solitons/drugan-sphere.json',import.meta.url)));
  const full=revolutionFaces(d,360),cut=revolutionFaces(d,270);
  assert.equal(full.length,d.faces.length);
  assert.equal(cut.length,full.length*3/4);
  assert.ok(cut.every(({index})=>d.revolution.faceSectors[index]<36));
  assert.equal(revolutionFaces(d,0).length,0);
  assert.deepEqual(full.map(({face})=>face),d.faces);
});

test('ancient oval remains on its exact time-dependent implicit curve',()=>{
  for(const t of [-5,-2,-.1]) {
    const curve=ancientOval(t);
    for(const [x,y,z] of curve){assert.ok(Math.abs(Math.cos(x)-Math.exp(t)*Math.cosh(y))<1e-12);assert.equal(z,0);}
    assert.ok(Math.max(...curve.map(p=>p[0]))<Math.PI/2);
    assert.ok(Math.hypot(...curve[0].map((v,i)=>v-curve.at(-1)[i]))<1e-10);
  }
  assert.throws(()=>ancientOval(0));
});

test('camera rotations preserve distances, while R4 projection is labeled by dimension',()=>{
  const s={yaw:.7,pitch:-.4,fourD:.55};
  const p=[2,3,-1], q=rotatePoint(p,s);
  assert.ok(Math.abs(Math.hypot(...p)-Math.hypot(...q))<1e-12);
  const p4=[1,2,3,4];
  const q4=rotatePoint(p4,s), changed=rotatePoint(p4,{...s,fourD:0});
  assert.ok(Math.hypot(...q4)<=Math.hypot(...p4));
  assert.ok(Math.hypot(...q4.map((v,i)=>v-changed[i]))>.1);
});

test('explicit ancient torus curves and helices satisfy the vector flow equation', async()=>{
  const {explicitCurve}=await import('../site/assets/soliton-viewer.mjs');
  const dt=1e-5,index=73,count=600;
  for(const [kind,t] of [['torus-curve',-1.7],['helix',.4]]){
    const p=explicitCurve(kind,t,count)[index];
    const before=explicitCurve(kind,t-dt,count)[index],after=explicitCurve(kind,t+dt,count)[index];
    const r=Math.hypot(p[0],p[1]);
    const D=kind==='torus-curve'?r*r+4*r**8:1+r*r;
    const curvature=kind==='torus-curve'?[-p[0]/D,-p[1]/D,-4*p[2]/D,-4*p[3]/D]:[-p[0]/D,-p[1]/D,0];
    for(let i=0;i<p.length;i++)assert.ok(Math.abs((after[i]-before[i])/(2*dt)-curvature[i])<1e-7);
  }
  assert.throws(()=>explicitCurve('torus-curve',0));
});


test('Møller sheet and cutaway controls preserve the full limiting geometry',async()=>{
  const {configurationFaces}=await import('../site/assets/moller-viewer.mjs');
  const d=JSON.parse(readFileSync(new URL('../site/assets/solitons/moller-gluing.json',import.meta.url)));
  const all=configurationFaces(d,{degrees:360});
  const sphere=configurationFaces(d,{degrees:360,torus:false});
  const torus=configurationFaces(d,{degrees:360,sphere:false});
  assert.equal(all.length,d.faces.length);
  assert.equal(sphere.length+torus.length,all.length);
  assert.ok(sphere.every(({index})=>d.faceGroups[index]===0));
  assert.ok(torus.every(({index})=>d.faceGroups[index]===1));
  assert.equal(configurationFaces(d,{sphere:false,torus:false}).length,0);
  assert.equal(configurationFaces(d,{degrees:270}).length,all.length*3/4);
  assert.deepEqual(all.map(({face})=>face),d.faces);
});


test('genus-model WebGL rotations agree with the shared geometric projection',async()=>{
  const {modelRotation}=await import('../site/assets/moller-genus-viewer.mjs');
  for(const [yaw,pitch] of [[.35,.36],[1.8,-.5],[0,0]]){
    const p=[2,-1,3],m=modelRotation(yaw,pitch);
    const actual=[0,1,2].map(i=>m[i]*p[0]+m[i+3]*p[1]+m[i+6]*p[2]);
    const expected=rotatePoint(p,{yaw,pitch});
    actual.forEach((x,i)=>assert.ok(Math.abs(x-expected[i])<1e-12));
  }
});

test('AAAW exact ambient motion has the scaled normal curvature at nonzero times',async()=>{
  const {evolveRotatingCurve}=await import('../site/assets/soliton-viewer.mjs');
  const dt=1e-5;
  for(const name of ['rotator','screw','expanding','shrinking']){
    const d=JSON.parse(readFileSync(new URL(`../site/assets/solitons/aaaw-${name}.json`,import.meta.url)));
    const {alpha,omega,velocity}=d.dynamic;
    const state=d.integration.states[Math.floor(d.vertices.length/2)+43];
    const c=state.slice(0,3),T=state.slice(3);
    const a=[alpha*c[0]-omega*c[1],alpha*c[1]+omega*c[0],alpha*c[2]+velocity];
    const dot=a.reduce((s,x,j)=>s+x*T[j],0),curvature=a.map((x,j)=>x-dot*T[j]);
    for(const time of [-.4,.5]){
      const before=evolveRotatingCurve([c],time-dt,d.dynamic)[0],after=evolveRotatingCurve([c],time+dt,d.dynamic)[0];
      const speed=after.map((x,j)=>(x-before[j])/(2*dt));
      const scale=Math.sqrt(1+2*alpha*time);
      const rotatedT=evolveRotatingCurve([T],time,{alpha,omega,velocity:0})[0].map(x=>x/scale);
      const tangential=speed.reduce((s,x,j)=>s+x*rotatedT[j],0);
      const normal=speed.map((x,j)=>x-tangential*rotatedT[j]);
      const expected=evolveRotatingCurve([curvature],time,{alpha,omega,velocity:0})[0].map(x=>x/(scale*scale));
      normal.forEach((x,j)=>assert.ok(Math.abs(x-expected[j])<1e-7));
    }
  }
  assert.throws(()=>evolveRotatingCurve([[1,0,0]],1,{alpha:-.5,omega:1,velocity:0}));
  assert.throws(()=>evolveRotatingCurve([[1,0,0]],-1,{alpha:.5,omega:1,velocity:0}));
});

test('irrational-frequency curve satisfies Euclidean curve shortening in physical time',async()=>{
  const {explicitCurve}=await import('../site/assets/soliton-viewer.mjs');
  const dt=1e-5;
  for(const time of [-6,-1,-.05]){
    const p=explicitCurve('dense-torus',time,2400)[743];
    const before=explicitCurve('dense-torus',time-dt,2400)[743],after=explicitCurve('dense-torus',time+dt,2400)[743];
    const D=p[0]**2+p[1]**2+2*(p[2]**2+p[3]**2);
    const curvature=[-p[0]/D,-p[1]/D,-2*p[2]/D,-2*p[3]/D];
    p.forEach((_,j)=>assert.ok(Math.abs((after[j]-before[j])/(2*dt)-curvature[j])<1e-6));
    assert.ok(Math.abs(p.reduce((s,x)=>s+x*x,0)+2*time)<1e-10);
  }
  assert.throws(()=>explicitCurve('dense-torus',0));
});
