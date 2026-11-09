import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {orbitRadius,flowFrame,projectFiber} from '../site/assets/lee-tsai-viewer.mjs';
const data=JSON.parse(fs.readFileSync(new URL('../site/assets/solitons/lee-tsai.json',import.meta.url)));
test('interior circle fibers remain positive at every finite saved time',()=>{
 for(const f of data.frames){for(const a of data.centers.slice(1,-1)){const i=data.x.findIndex(x=>Math.abs(x-a)<1e-10);assert.ok(orbitRadius(a,f.u[i],data.centers)>0);}}
 for(const a of data.centers)assert.equal(orbitRadius(a,0,data.centers),0);
});
test('playback interpolates finite data and keeps the limit separate',()=>{
 const a=flowFrame(data,3),b=flowFrame(data,3.1),m=flowFrame(data,3.05);
 assert.ok(Math.abs(m.height-(a.height+b.height)/2)<1e-12);
 assert.ok(flowFrame(data,12).neckRadii.every(x=>x>0));
 assert.ok(flowFrame(data,Infinity).u.every(x=>x===0));
 for(const t of [-1,12.1,NaN])assert.throws(()=>flowFrame(data,t),RangeError);
});
test('diagram rotation preserves its Euclidean display radius',()=>{
 const p=projectFiber(.4,.3,.7,1.2,.8);assert.ok(Math.abs(Math.hypot(...p)-.5)<1e-12);
});
