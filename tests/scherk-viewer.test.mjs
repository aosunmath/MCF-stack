import test from 'node:test';
import assert from 'node:assert/strict';
import {scherkTiles} from '../site/assets/scherk-viewer.mjs';

test('vertical corner half-turns occupy alternating domains, preserving height',()=>{
  const tiles=scherkTiles('periodic');assert.equal(tiles.length,13);
  assert.deepEqual(scherkTiles('patch'),[[0,0]]);
  const keys=new Set(tiles.map(p=>p.join(',')));assert.equal(keys.size,tiles.length);
  for(const [i,j] of tiles){assert.equal(Math.abs((i-j)%2),0);assert.ok(keys.has([-i,-j].join(',')));}
  // A corner half-turn maps a patch centre (i,j) to (1-i,1-j).
  for(const [i,j] of tiles)if(Math.abs(1-i)<=2&&Math.abs(1-j)<=2)assert.ok(keys.has([1-i,1-j].join(',')));
  assert.throws(()=>scherkTiles('all rectangles'));
});
