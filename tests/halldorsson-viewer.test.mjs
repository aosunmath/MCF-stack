import test from 'node:test';
import assert from 'node:assert/strict';
import {motion,transform} from '../site/assets/halldorsson-viewer.mjs';

test('similarity motions satisfy the physical rotation and dilation rates',()=>{
 for(const B of [-.5,-.25,0,.25,.5]){
  const A=1.3,v={A,B};
  for(const clock of [-1,0,1]){
   const m=motion(v,'similarity',clock),a=motion(v,'similarity',clock-1e-5),b=motion(v,'similarity',clock+1e-5);
   const dt=b.time-a.time;
   assert.ok(Math.abs((b.scale-a.scale)/dt-B/m.scale)<1e-7);
   assert.ok(Math.abs((b.angle-a.angle)/dt-A/(m.scale*m.scale))<1e-7);
   assert.ok(1+2*B*m.time>0);
  }
 }
});
test('canonical dense shrinker time and radius obey the time-minus-one normalization',()=>{
 for(const clock of [-2,0,2]){const m=motion({A:0,B:-.5},'similarity',clock,'halldorsson-dense');assert.ok(m.time<0);assert.ok(Math.abs(m.scale*m.scale+m.time)<1e-12);}
});
test('helicoidal motion translates downward at pitch-dependent speed; minimal profiles stay fixed',()=>{
 for(const t of [-2,0,2]){
  assert.deepEqual(transform([1,2,3],motion({h:2},'translator',t)),[1,2,3-2*t]);
  assert.deepEqual(transform([1,2,3],motion({},'stationary',t)),[1,2,3]);
 }
});
