import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync,readFileSync} from 'node:fs';
import {BNS_GENERA,bnsModelUrl,bnsAxes} from '../site/assets/bns-viewer.mjs';

test('every selectable genus resolves to a labeled, shipped schematic',()=>{
  for(const g of BNS_GENERA){
    const url=bnsModelUrl('/MCF-stack/assets/solitons/bns-shrinkers.json',g);
    const file=new URL('../site'+url.replace('/MCF-stack',''),import.meta.url);
    assert.ok(existsSync(file));
    const data=JSON.parse(readFileSync(file));
    assert.equal(data.genus,g);assert.equal(data.status,'schematic');
    assert.equal(data.kind,'bns-schematic');
  }
  assert.throws(()=>bnsModelUrl('bns-shrinkers.json',4));
});

test('symmetry overlays contain precisely g+1 full horizontal axes',()=>{
  for(const g of BNS_GENERA){
    const axes=bnsAxes(g);
    assert.equal(axes.length,g+1);
    for(const [a,b] of axes){
      assert.equal(a[2],0);assert.equal(b[2],0);
      assert.ok(Math.abs(Math.hypot(...a)-5)<1e-12);
      assert.ok(a.every((x,i)=>Math.abs(x+b[i])<1e-12));
      assert.ok(Math.abs(Math.sin((g+1)*Math.atan2(b[1],b[0])))<1e-12);
    }
  }
});
