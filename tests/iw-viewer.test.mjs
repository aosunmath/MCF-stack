import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync,readFileSync} from 'node:fs';
import {IW_GENERA,iwModelUrl} from '../site/assets/iw-viewer.mjs';

test('every selectable Ilmanen–White genus resolves to its shipped schematic',()=>{
  for(const g of IW_GENERA){
    const url=iwModelUrl('/MCF-stack/assets/solitons/iw-two-ended.json',g);
    const file=new URL('../site'+url.replace('/MCF-stack',''),import.meta.url);
    assert.ok(existsSync(file));
    const data=JSON.parse(readFileSync(file));
    assert.equal(data.genus,g);assert.equal(data.status,'schematic');
    assert.equal(data.kind,'iw-schematic');
  }
  assert.throws(()=>iwModelUrl('iw-two-ended.json',1));
});
