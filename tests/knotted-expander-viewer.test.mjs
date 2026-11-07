import test from 'node:test';
import assert from 'node:assert/strict';
import {knottedNormals,knottedRims} from '../site/assets/knotted-expander-viewer.mjs';

test('Rim segments lie on the clipping plane and inside their source triangles',()=>{
  const v=[[0,0,0],[2,0,0],[0,2,0]];
  assert.deepEqual(knottedRims(v,[[0,1,2]],[[1,0,0]],1),[[1,0,0],[1,1,0]]);
  assert.deepEqual(knottedRims(v,[[0,1,2]],[[1,0,0]],3),[]);
  assert.deepEqual(knottedRims(v,[[0,1,2]],[[1,0,0]],0),[[0,0,0],[0,2,0]]);
});
test('Vertex normals use face orientation and remain finite',()=>{
  const v=[[0,0,0],[1,0,0],[0,1,0],[2,2,2]];
  assert.deepEqual(knottedNormals(v,[[0,1,2]]),[[0,0,1],[0,0,1],[0,0,1],[0,0,0]]);
  assert.equal(knottedNormals(v,[[0,2,1]])[0][2],-1);
});
