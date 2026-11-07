import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {networkPoint} from '../site/assets/expanding-network-viewer.mjs';

const data=JSON.parse(readFileSync(new URL('../site/assets/solitons/expanding-network.json',import.meta.url)));

test('homothetic normal velocity agrees with the numerically measured curvature',()=>{
  const arm=data.paths[0].map(i=>data.vertices[i]);
  for(const time of [.05,.25,1,4])for(const vertical of [false,true]){
    const i=40,h=.01*Math.sqrt(time),dt=1e-5*time;
    const p=networkPoint(arm[i],time,vertical);
    const before=networkPoint(arm[i-1],time,vertical),after=networkPoint(arm[i+1],time,vertical);
    const v=after.map((x,k)=>(x-before[k])/(2*h)),speed=Math.hypot(...v);
    const normal=[-v[1]/speed,v[0]/speed];
    const acc=after.map((x,k)=>(x-2*p[k]+before[k])/(h*h));
    const curvature=acc.reduce((sum,x,k)=>sum+x*normal[k],0)/(speed*speed);
    const earlier=networkPoint(arm[i],time-dt,vertical),later=networkPoint(arm[i],time+dt,vertical);
    const normalVelocity=later.reduce((sum,x,k)=>sum+(x-earlier[k])/(2*dt)*normal[k],0);
    assert.ok(Math.abs(curvature-normalVelocity)<2e-5);
  }
});

test('quarter-turn keeps the prescribed ray set and changes the central edge',()=>{
  for(const ray of [[1,1],[-1,1],[-1,-1],[1,-1]]){
    const p=networkPoint(ray,1,true);
    assert.equal(Math.abs(p[0]),Math.abs(p[1]));
  }
  assert.deepEqual(networkPoint([data.junction,0],1,true),[-0,data.junction]);
  assert.throws(()=>networkPoint([0,0],-1));
  assert.throws(()=>networkPoint([0,0],NaN));
});
