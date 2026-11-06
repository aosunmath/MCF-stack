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
