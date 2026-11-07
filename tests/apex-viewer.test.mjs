import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {apexCase,quadraticHeight} from '../site/assets/apex-viewer.mjs';
const data=JSON.parse(fs.readFileSync(new URL('../site/assets/solitons/apex-ellipsoid.json',import.meta.url)));

test('selections retain their formula, PDE and ODE provenance',()=>{
  assert.equal(apexCase(data,'wing'),data);
  assert.equal(apexCase(data,'wing').status,'numerical-pde');
  assert.equal(apexCase(data,'grim').status,'formula');
  assert.equal(apexCase(data,'bowl').status,'numerical-ode');
  assert.throws(()=>apexCase(data,'interpolated'));
});
test('local comparison uses half the Hessian coefficient',()=>{
  for(const k of [0,.2442666335,.5,1]){
    const h=.01;
    assert.ok(Math.abs((quadraticHeight(k,h)+quadraticHeight(k,-h))/h**2-k)<1e-12);
  }
});
