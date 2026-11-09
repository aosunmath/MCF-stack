import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {grimHeight,sectionAt} from '../site/assets/delta-wing-viewer.mjs';
const data=JSON.parse(readFileSync(new URL('../site/assets/solitons/delta-wing.json',import.meta.url)));

test('The tilted grim limit has the claimed strip width and unit translator speed',()=>{
  for(const b of [2,Math.PI/Math.sqrt(2),3]){
    const c=Math.PI/(2*b),a=Math.sqrt(1/(c*c)-1);
    for(const y of [0,.3*b,.85*b]){
      const h=1e-4,p=a,q=Math.tan(c*y)/c;
      const uyy=(grimHeight(y+h,b)-2*grimHeight(y,b)+grimHeight(y-h,b))/(h*h);
      const speed=(1+p*p)*uyy/(1+p*p+q*q);
      assert.ok(Math.abs(speed-1)<2e-6);
    }
  }
  assert.throws(()=>grimHeight(2,2));assert.throws(()=>grimHeight(0,1));
});
test('Computed transverse sections interpolate continuously and recenter at zero',()=>{
  assert.deepEqual(sectionAt(data,0),data.sections[0]);
  assert.deepEqual(sectionAt(data,6),data.sections.at(-1));
  const mid=sectionAt(data,.125);
  assert.ok(mid.every(([y,z],i)=>Math.abs(z-(data.sections[0][i][1]+data.sections[1][i][1])/2)<1e-10));
  assert.equal(mid[80][1],0);
  assert.throws(()=>sectionAt(data,7));assert.throws(()=>sectionAt(data,-1));
  const error=sectionAt(data,6).reduce((max,[y,z])=>Math.max(max,Math.abs(z-grimHeight(y,data.halfWidth))),0);
  assert.ok(error<.13,'The outer section should approach the tilted grim profile');
});
