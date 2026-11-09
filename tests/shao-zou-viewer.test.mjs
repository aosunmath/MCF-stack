import test from 'node:test';
import assert from 'node:assert/strict';
import {shaoZouModelUrl,shaoZouGap,shaoZouSites,shaoZouNormals} from '../site/assets/shao-zou-viewer.mjs';

test('illustration URLs accept only supplied sheet and bridge counts',()=>{
  const base='../../assets/solitons/shao-zou-stacking.json';
  assert.equal(shaoZouModelUrl(base,4,10),base);
  assert.equal(shaoZouModelUrl(base,3,14),'../../assets/solitons/shao-zou-stacking-3-14.json');
  assert.throws(()=>shaoZouModelUrl(base,1,10));
  assert.throws(()=>shaoZouModelUrl(base,4,11));
});

test('site layout alternates half a step and has the correct vertical symmetry',()=>{
  for(const k of [2,3,4,5,6])for(const m of [6,10,14]){
    const sites=shaoZouSites(k,m);
    assert.equal(sites.length,k-1);
    const close=(p,q)=>Math.hypot(p[0]-q[0],p[1]-q[1])<1e-10;
    for(let g=0;g<k-1;g++){
      assert.equal(sites[g].length,m);
      const angle=k%2?Math.PI/m:0;
      for(const [x,y] of sites[g]){
        const reflected=[x*Math.cos(angle)+y*Math.sin(angle),x*Math.sin(angle)-y*Math.cos(angle)];
        assert.ok(sites[k-2-g].some(p=>close(p,reflected)));
      }
      if(g>0)assert.ok(!sites[g-1].some(p=>close(p,sites[g][0])));
      if(g>1)assert.deepEqual(sites[g],sites[g-2]);
    }
  }
});

test('separation changes only height and normals follow the deformed geometry',()=>{
  const vertices=[[0,0,-1],[1,0,0],[0,1,1]];
  const stretched=shaoZouGap(vertices,2);
  assert.deepEqual(stretched,[[0,0,-2],[1,0,0],[0,1,2]]);
  assert.deepEqual(shaoZouGap(vertices,1),vertices);
  assert.throws(()=>shaoZouGap(vertices,0));
  const normals=shaoZouNormals(stretched,[[0,1,2]]);
  for(const n of normals){
    assert.ok(Math.abs(Math.hypot(...n)-1)<1e-12);
    assert.ok(Math.abs(n[0]+2*n[2])<1e-12);
    assert.ok(Math.abs(n[1]+4*n[2])<1e-12);
  }
});
