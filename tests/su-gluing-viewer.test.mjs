import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {translateSuPoint,projectSuPoint} from '../site/assets/su-gluing-viewer.mjs';
const data=JSON.parse(readFileSync(new URL('../site/assets/solitons/su-glued-translators.json',import.meta.url)));

test('flow translates only Re z3 and preserves all ambient distances',()=>{
  const p=data.vertices[70],q=data.vertices[3020];
  const distance=(p,q)=>Math.hypot(...p.map((x,i)=>x-q[i]));
  for(const t of [-5,-1,0,1,8]){
    const pt=translateSuPoint(p,t),qt=translateSuPoint(q,t);
    assert.deepEqual(pt,[p[0],p[1],p[2]+t,p[3]]);
    assert.ok(Math.abs(distance(pt,qt)-distance(p,q))<1e-12);
  }
});

test('projection retains unit translation at every projection angle',()=>{
  for(const beta of [-Math.PI/2,0,Math.PI/6,Math.PI/2]){
    for(const p of [data.vertices[0],data.vertices[3000]]){
      const a=projectSuPoint(p,-1,beta,data.intersection),b=projectSuPoint(p,1,beta,data.intersection);
      assert.equal(a[0],b[0]);assert.equal(a[1],b[1]);assert.ok(Math.abs(b[2]-a[2]-2)<1e-12);
    }
  }
});
