import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync,readFileSync} from 'node:fs';
import {KETOVER_GENERA,ketoverModelUrl,ketoverRing} from '../site/assets/ketover-viewer.mjs';

test('every selectable Ketover genus resolves to its shipped schematic',()=>{
  for(const g of KETOVER_GENERA){
    const url=ketoverModelUrl('/MCF-stack/assets/solitons/ketover-shrinkers.json',g);
    const file=new URL('../site'+url.replace('/MCF-stack',''),import.meta.url);
    assert.ok(existsSync(file));
    const data=JSON.parse(readFileSync(file));
    assert.equal(data.genus,g);assert.equal(data.status,'schematic');
    assert.equal(data.kind,'ketover-schematic');
  }
  assert.throws(()=>ketoverModelUrl('ketover-shrinkers.json',2));
});

test('neck guide closes in the horizontal plane at the model radius',()=>{
  const lines=ketoverRing();
  for(let i=0;i<lines.length;i++){
    for(const p of lines[i]){
      assert.equal(p[2],0);assert.ok(Math.abs(Math.hypot(...p)-2.2)<1e-12);
    }
    assert.ok(lines[i][1].every((v,j)=>Math.abs(v-lines[(i+1)%lines.length][0][j])<1e-12));
  }
});
