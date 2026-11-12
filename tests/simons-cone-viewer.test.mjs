import test from 'node:test';
import assert from 'node:assert/strict';
import {exponent,interpolate,scaleFor} from '../site/assets/simons-cone-viewer.mjs';

test('cone rates respect block dimensions and the two scales',()=>{
  assert.deepEqual(exponent(4,4,4),{alpha:-2,beta:4/3});
  assert.equal(exponent(3,5,4).beta,4/3);
  const {beta}=exponent(5,5,2);assert.ok(beta>.5&&beta<1);
  const t=-.01,b=.7*Math.abs(t)**beta;
  assert.equal(scaleFor('physical',t,b),1);
  assert.equal(scaleFor('parabolic',t,b),.1);
  assert.equal(b/scaleFor('inner',t,b),1);
  assert.ok(b/scaleFor('parabolic',t,b)<1);
});
test('profile interpolation is bounded and linear on each sample interval',()=>{
  assert.equal(interpolate(.5,[0,1,2],[1,3,4]),2);
  assert.equal(interpolate(-1,[0,1],[2,4]),2);
  assert.equal(interpolate(3,[0,1],[2,4]),4);
});
