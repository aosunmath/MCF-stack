import test from 'node:test';
import assert from 'node:assert/strict';
import {ANNULUS,neckRadius,profileHeight,annulusGeometry,compactMeridian} from '../site/assets/immortal-annulus-viewer.mjs';

test('finite schematic stages are connected annuli with two display boundaries',()=>{
  for(const stage of [0,.5,1]){
    const g=annulusGeometry(stage,24,32),edges=new Map(),neighbors=g.vertices.map(()=>new Set());
    for(const f of g.faces)for(let j=0;j<3;j++){
      const a=f[j],b=f[(j+1)%3],key=[a,b].sort((x,y)=>x-y).join(',');
      edges.set(key,(edges.get(key)||0)+1);neighbors[a].add(b);neighbors[b].add(a);
    }
    assert.equal(g.vertices.length-edges.size+g.faces.length,0);
    assert.equal([...edges.values()].filter(x=>x===1).length,64);
    assert.ok([...edges.values()].every(x=>x===1||x===2));
    const seen=new Set([0]),queue=[0];for(const a of queue)for(const b of neighbors[a])if(!seen.has(b)){seen.add(b);queue.push(b);}
    assert.equal(seen.size,g.vertices.length);
    const radii=g.vertices.map(([x,y])=>Math.hypot(x,y));
    assert.ok(Math.abs(Math.min(...radii)-neckRadius(stage))<1e-12);
    assert.ok(Math.min(...radii)>0);assert.ok(Math.abs(Math.max(...radii)-ANNULUS.radius)<1e-12);
    for(let i=0;i<=24;i++)for(let j=0;j<32;j++){
      const p=g.vertices[i*32+j],q=g.vertices[(24-i)*32+j];
      assert.ok(Math.abs(p[0]-q[0])+Math.abs(p[1]-q[1])+Math.abs(p[2]+q[2])<1e-10);
    }
  }
});

test('local flattening preserves fixed far-end heights and the compressed profile',()=>{
  assert.ok(neckRadius(0)>neckRadius(.5)&&neckRadius(.5)>neckRadius(1));
  for(const r of [1,2,5])assert.ok(profileHeight(r,0)>profileHeight(r,.5)&&profileHeight(r,.5)>profileHeight(r,1));
  for(const s of [0,.5,1]){
    assert.equal(profileHeight(neckRadius(s),s),0);
    assert.ok(Math.abs(profileHeight(1e150,s)-ANNULUS.height)<1e-9);
    const p=compactMeridian(s);assert.deepEqual(p.at(-1),[1,ANNULUS.height]);
    for(let i=1;i<p.length;i++)assert.ok(p[i][0]>=p[i-1][0]&&p[i][1]>p[i-1][1]);
    for(const [x,z] of p.slice(0,-1))if(x<.9999){const r=ANNULUS.radius*x/(1-x);assert.ok(Math.abs(profileHeight(Math.max(r,neckRadius(s)),s)-z)<1e-7);}
  }
  assert.throws(()=>neckRadius(Infinity));assert.throws(()=>neckRadius(-1));assert.throws(()=>profileHeight(0,0));
});
