import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {similarity,innerScale,curveAt,FLOW_TIMES} from '../site/assets/aiv-viewer.mjs';
const data=JSON.parse(fs.readFileSync(new URL('../site/assets/solitons/aiv-data.json',import.meta.url)));
test('soliton time scaling keeps common spatial coordinates',()=>{
 assert.deepEqual(similarity([[2,4]],-.25),[[1,2]]);
 assert.deepEqual(similarity([[2,4]],.25,'expander'),[[1,2]]);
 assert.deepEqual(similarity([[2,4]],2,'minimal'),[[4,8]]);
});
test('the singular time is a cone and only matched shrinkers have continuations',()=>{
 assert(FLOW_TIMES.includes(0));
 assert(curveAt(data,1,0)[0].cone);
 assert.equal(curveAt(data,1,.25).length,3);
 assert.equal(curveAt(data,1,-1).length,1);
 assert.throws(()=>curveAt(data,0,1),RangeError);
});
test('formal inverse inner model swaps axes and has k/3 scale',()=>{
 const p=innerScale([[8,16]],-.125,2)[0];
 assert(Math.abs(p[0]-4)<1e-12);assert(Math.abs(p[1]-2)<1e-12);
});
test('published experiments contain data and continuous accuracy labels',()=>{
 for(const model of ['aiv-shrinkers','aiv-expanders','aiv-minimal','aiv-eight-fattening']){
  const text=fs.readFileSync(new URL(`../site/experiments/${model}.html`,import.meta.url),'utf8');
  assert(text.includes('id="geometry"'));assert(!text.includes('__DATA__'));
  assert(text.includes('FORMAL INNER MODEL ONLY'));assert(text.includes('does not solve MCF'));
  assert(!text.includes('fetch('));
 }
});
