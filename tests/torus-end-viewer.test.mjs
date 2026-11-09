import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {torusEndMesh,endNormals} from '../site/assets/torus-end-viewer.mjs';
const data=JSON.parse(fs.readFileSync(new URL('../site/assets/solitons/sun-wang-torus-end.json',import.meta.url)));
function topology(mesh){
  const edges=new Map();for(const f of mesh.faces)for(let k=0;k<3;k++){const edge=[f[k],f[(k+1)%3]].sort((a,b)=>a-b).join(',');edges.set(edge,(edges.get(edge)||0)+1);}
  assert.ok([...edges.values()].every(n=>n===1||n===2));
  return {chi:mesh.vertices.length-edges.size+mesh.faces.length,boundary:[...edges.values()].filter(n=>n===1).length};
}
test('The displayed quotient is an annulus with two display rims; a slice is a closed torus',()=>{
  const end=torusEndMesh(data.profile),slice=torusEndMesh(data.profile,'slice');
  assert.deepEqual(topology(end),{chi:0,boundary:2*data.profile.length});
  assert.deepEqual(topology(slice),{chi:0,boundary:0});
  assert.ok(endNormals(slice.vertices,slice.faces).every(n=>Math.abs(Math.hypot(...n)-1)<1e-9));
});
test('Height nine triples horizontal size without moving height into the spatial torus axes',()=>{
  const low=torusEndMesh(data.profile,'slice',1),high=torusEndMesh(data.profile,'slice',9);
  high.vertices.forEach((p,i)=>p.forEach((x,k)=>assert.ok(Math.abs(x-3*low.vertices[i][k])<1e-12)));
});
test('Dividing the horizontal coordinates by square root of height gives the constant meridian',()=>{
  const end=torusEndMesh(data.profile),normalized=torusEndMesh(data.profile,'normalized');
  end.vertices.forEach((p,i)=>{
    assert.ok(Math.abs(p[0]/Math.sqrt(p[2])-normalized.vertices[i][0])<1e-12);
    assert.ok(Math.abs(p[1]/Math.sqrt(p[2])-normalized.vertices[i][1])<1e-12);
    assert.equal(p[2],normalized.vertices[i][2]);
  });
  assert.deepEqual(end.vertices,data.vertices);assert.deepEqual(end.faces,data.faces);
});
test('The numerical profile has the Angenent radii, rather than circular-torus dimensions',()=>{
  const radii=data.profile.map(p=>p[0]);assert.ok(Math.abs(Math.max(...radii)-3.3147083)<1e-6);
  assert.ok(Math.abs(Math.min(...radii)-.437124)<.002);
  assert.equal(data.profile_source.audit.normalization,'Hvec=-Xperp/2');
  assert.throws(()=>torusEndMesh(data.profile,'slice',0));
});
