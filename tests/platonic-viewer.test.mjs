import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {PLATONIC_SOLIDS,platonicModelUrl} from '../site/assets/platonic-viewer.mjs';
import {sphericalGap} from '../site/assets/spherical-doubling-viewer.mjs';

test('all five options load the matching genus and face-center configuration',()=>{
  const base=new URL('../site/assets/solitons/ketover-platonic.json',import.meta.url).href;
  for(const [solid,,necks] of PLATONIC_SOLIDS){
    const data=JSON.parse(fs.readFileSync(new URL(platonicModelUrl(base,solid))));
    assert.equal(data.solid,solid);
    assert.equal(data.genus,necks-1);
    assert.equal(data.sites.length,necks);
    for(const factor of [.6,1.8]){
      const changed=sphericalGap(data.vertices,factor);
      assert.ok(changed.every(p=>p.every(Number.isFinite)&&Math.hypot(...p)>0));
    }
  }
  assert.equal(platonicModelUrl(base,'cube'),base);
  assert.throws(()=>platonicModelUrl(base,'polygon'));
});
