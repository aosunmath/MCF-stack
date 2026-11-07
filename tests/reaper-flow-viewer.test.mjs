import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {grimReaper,timeSlice} from '../site/assets/reaper-flow-viewer.mjs';
const data=JSON.parse(readFileSync(new URL('../site/assets/solitons/grim-reaper-chains.json',import.meta.url)));

test('model overlay has the correct strips, signs and graphical CSF velocity',()=>{
  for(let k=1;k<=3;k++){
    const before=grimReaper(k,-3),after=grimReaper(k,-2);
    for(let i=1;i<before.length-1;i++){
      const [x,y]=before[i],angle=y-(k-1)*Math.PI;
      assert.ok(angle>0&&angle<Math.PI);
      assert.ok(Math.abs(after[i][0]-x-(-1)**k)<1e-10);
      if(angle>.01&&angle<Math.PI-.01){
        const slope=(-1)**(k+1)/Math.tan(angle),second=(-1)**k/Math.sin(angle)**2;
        assert.ok(Math.abs(second/(1+slope*slope)-(-1)**k)<1e-10);
      }
    }
  }
});

test('time interpolation is bounded to computed times and preserves snapshots',()=>{
  assert.deepEqual(timeSlice(data,-100),data.frames[0].points);
  assert.deepEqual(timeSlice(data,100),data.frames.at(-1).points);
  for(const index of [30,60,90,120,150])assert.deepEqual(timeSlice(data,data.frames[index].t),data.frames[index].points);
  const mid=timeSlice(data,-5.95);
  assert.ok(Math.abs(mid[450][0]-(data.frames[0].points[450][0]+data.frames[1].points[450][0])/2)<1e-10);
});
