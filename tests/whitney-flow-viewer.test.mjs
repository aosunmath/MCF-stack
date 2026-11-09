import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {rightLobe,fullProfile,sphereMesh} from '../site/assets/whitney-flow-viewer.mjs';
const data=JSON.parse(fs.readFileSync(new URL('../site/assets/solitons/whitney-flow.json',import.meta.url)));

test('one lobe generates one closed sphere with two distinct poles',()=>{
  const mesh=sphereMesh(data.frames[0].quarter,16,4),edges=new Map(),adj=mesh.vertices.map(()=>new Set());
  for(const face of mesh.faces){
    assert.equal(new Set(face).size,3);
    for(let i=0;i<3;i++){
      const a=face[i],b=face[(i+1)%3],key=[a,b].sort((a,b)=>a-b).join(',');
      edges.set(key,(edges.get(key)||0)+1);adj[a].add(b);adj[b].add(a);
    }
  }
  assert([...edges.values()].every(n=>n===2));
  assert.equal(mesh.vertices.length-edges.size+mesh.faces.length,2);
  const seen=new Set(),todo=[0];while(todo.length){const i=todo.pop();if(seen.has(i))continue;seen.add(i);todo.push(...adj[i]);}
  assert.equal(seen.size,mesh.vertices.length);
  assert.deepEqual(mesh.vertices[0],[0,0,0,0]);assert.deepEqual(mesh.vertices.at(-1),mesh.vertices[0]);
  assert(mesh.vertices.slice(1,-1).every(p=>Math.hypot(...p)>0));
  assert.deepEqual(new Set(mesh.groups),new Set([0,1]));
});

test('reconstruction preserves exact equivariant coordinate identities',()=>{
  for(const frame of [data.frames[0],data.frames[90]]){
    const m=sphereMesh(frame.quarter);
    for(const [x1,x2,y1,y2] of m.vertices)assert(Math.abs(x1*y2-x2*y1)<1e-13);
    assert(Math.abs(Math.max(...m.vertices.map(p=>Math.hypot(...p)))-frame.quarter.at(-1)[0])<1e-8);
    const lobe=rightLobe(frame.quarter),profile=fullProfile(frame.quarter);
    assert(lobe.every(p=>p[0]>=0));assert(lobe[0].every(v=>v===0));
    assert.equal(profile.length,4*(frame.quarter.length-1)+1);
    assert(profile.some(p=>p[0]<0));
  }
});
