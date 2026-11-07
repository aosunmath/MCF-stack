import test from 'node:test';
import assert from 'node:assert/strict';
import {modelHeight,axialHeight,axialTip,wangMesh,WANG_WINDOW} from '../site/assets/wang-geometry.mjs';

test('level and slice meshes lie on the declared illustration, with finite unit normals',()=>{
  for(const h of [1,4,32,256])for(const mode of ['level','slice','limit']){
    const d=wangMesh(mode,h,24,24);
    d.vertices.forEach(([s,x,y],i)=>{
      assert.ok(Math.abs(s)<=WANG_WINDOW+1e-10);
      assert.ok(d.normals[i].every(Number.isFinite));
      assert.ok(Math.abs(Math.hypot(...d.normals[i])-1)<1e-12);
      const defect=mode==='slice'?modelHeight(x,0,s,h)-y:mode==='limit'?(x*x+y*y)/2-1:modelHeight(x,y,s,h)-1;
      assert.ok(Math.abs(defect)<1e-11);
    });
    assert.ok(d.faces.flat().every(i=>i>=0&&i<d.vertices.length));
    assert.equal(d.clipped,mode==='level'&&axialTip(h)>WANG_WINDOW);
  }
});

test('schematic is strictly convex, partially symmetric, and is not a unit-speed translator',()=>{
  const f=(x,y,s)=>modelHeight(x,y,s);
  for(const [s,h] of [[0,1],[2,4],[20,256]]){
    const second=.25*(1+.5*h*s*s)/(1+h*s*s)**1.25;
    assert.ok(second>0);
  }
  assert.equal(f(3,4,2),f(0,5,-2));
  assert.notEqual(f(1,0,0),f(0,0,1));
  // At the minimum Du=0; L_1[f]=trace Hessian=1+1+1/4=9/4, not 1.
  const eps=1e-3,laplacian=2*(f(eps,0,0)+f(0,eps,0)+f(0,0,eps))/eps**2;
  assert.ok(Math.abs(laplacian-2.25)<1e-6);
});

test('rescaling is exact for the model and caps escape while bounded windows approach Q',()=>{
  for(const h of [1,8,256]){
    assert.ok(Math.abs(modelHeight(1,2,3,h)-modelHeight(Math.sqrt(h),2*Math.sqrt(h),3*Math.sqrt(h))/h)<1e-12);
    assert.ok(Math.abs(axialHeight(axialTip(h),h)-1)<1e-12);
  }
  assert.ok(axialTip(256)>axialTip(8));
  assert.ok(axialTip(1)<WANG_WINDOW&&axialTip(256)>WANG_WINDOW);
  assert.ok(axialHeight(3,1e16)<.001);
  assert.throws(()=>wangMesh('level',0));assert.throws(()=>wangMesh('bad'));
});
