import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {kkmVertices,kkmGeometry} from '../site/assets/kkm-viewer.mjs';
const data=JSON.parse(readFileSync(new URL('../site/assets/solitons/kkm-shrinker.json',import.meta.url)));

test('illustrative cone shear preserves the compact core and all horizontal coordinates',()=>{
  assert.deepEqual(kkmVertices(data,0),data.vertices);
  const v=kkmVertices(data,.15);
  data.vertices.forEach((p,i)=>{
    assert.equal(v[i][0],p[0]);assert.equal(v[i][1],p[1]);
    if(Math.hypot(p[0],p[1])<=2.35)assert.equal(v[i][2],p[2]);
    if(Math.hypot(p[0],p[1])>=3.2){
      const expected=.15*Math.hypot(p[0],p[1])*Math.sin(9*Math.atan2(p[1],p[0]));
      assert.ok(Math.abs(v[i][2]-p[2]-expected)<2e-6);
    }
  });
});

test('cutaway clips along straight planes and resetting retains the original complete mesh',()=>{
  const cut=kkmGeometry(data,.075,true),full=kkmGeometry(data,.075,false);
  assert.ok(cut.faces.length<full.faces.length);
  for(const {face,index} of cut.faces){
    assert.ok(index>=0&&index<data.faces.length);
    for(const i of face){const [x,y]=cut.vertices[i];assert.ok(y<=.35*Math.abs(x)+1e-10);}
  }
  assert.deepEqual(full.faces.map(({face})=>face),data.faces);
  assert.deepEqual(full.vertices,kkmVertices(data,.075));
});
