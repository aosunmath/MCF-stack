import test from 'node:test';
import assert from 'node:assert/strict';
import {DPN_COUNTS,dpnModelUrl} from '../site/assets/dpn-viewer.mjs';
test('DPN viewer keeps all selectable models within the catalogue asset path',()=>{
 const base='../../assets/solitons/bowl-catenoid-gluing.json';
 for(const m of DPN_COUNTS)assert.equal(dpnModelUrl(base,m),`../../assets/solitons/bowl-catenoid-gluing${m===12?'':`-${m}`}.json`);
 assert.equal(dpnModelUrl(base,'input'),'../../assets/solitons/dpn-bowl-catenoid-input.json');
 for(const bad of [1,0,12.5,'12','../../etc'])assert.throws(()=>dpnModelUrl(base,bad),/Unsupported/);
});
