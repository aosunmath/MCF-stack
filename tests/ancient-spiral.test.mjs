import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {solveModel} from '../scripts/generate_ancient_spiral_geometry.mjs';
import {spiralFrame,radiusAt,correctedCap,interpolate,snapshotSVG} from '../site/assets/ancient-spiral-viewer.mjs';
const data=JSON.parse(readFileSync(new URL('../site/assets/solitons/ancient-spiral-curves.json',import.meta.url)));
const cross=(a,b)=>a[0]*b[1]-a[1]*b[0],sub=(a,b)=>a.map((v,i)=>v-b[i]);
function area(f){const p=f.body.concat(f.cap.slice(1,-1));return Math.abs(p.reduce((s,a,i)=>s+cross(a,p[(i+1)%p.length]),0))/2;}
function crossingCount(points){
  const segments=points.map((a,i)=>{const b=points[(i+1)%points.length];return {a,b,i,lo:Math.min(a[0],b[0]),hi:Math.max(a[0],b[0]),bottom:Math.min(a[1],b[1]),top:Math.max(a[1],b[1])};}).sort((a,b)=>a.lo-b.lo);
  let active=[],count=0;
  for(const s of segments){
    active=active.filter(o=>o.hi>=s.lo);
    for(const o of active){
      const distance=Math.abs(s.i-o.i);
      if(distance<=1||distance===points.length-1||o.top<s.bottom||s.top<o.bottom)continue;
      const u=sub(s.b,s.a),v=sub(o.b,o.a),d=sub(o.a,s.a),det=cross(u,v);
      if(Math.abs(det)<1e-14)continue;
      const a=cross(d,v)/det,b=cross(d,u)/det;
      if(a>1e-8&&a<1-1e-8&&b>1e-8&&b<1-1e-8)count++;
    }
    active.push(s);
  }
  return count;
}

test('Yin–Yang ODE agrees under step refinement and obeys its first integral',()=>{
  const refined=solveModel(.001);
  for(const q of [2,5,16,36,48])assert.ok(Math.abs(radiusAt(data,q)-radiusAt(refined,q))<2e-7);
  for(let i=50;i<data.branch.length-1;i+=37){
    const [q,x,y]=data.branch[i],a=data.branch[i-1],b=data.branch[i+1];
    const r=Math.hypot(x,y),rq=(Math.hypot(b[1],b[2])-Math.hypot(a[1],a[2]))/(b[0]-a[0]);
    // The derivative uses the retained ds=.05 table, with O(ds²) difference error.
    assert.ok(Math.abs(r*r/2-q+Math.atan(rq/r))<.0002);
  }
  for(const p of [.5,2,6,10])assert.ok(Math.abs(interpolate(data.correction,p)-interpolate(refined.correction,p))<1e-7);
});

test('closed, noncrossing curves with a smooth central passage and cap joins',()=>{
  for(let t=-24;t<=-8;t+=.5){
    const f=spiralFrame(data,t),points=f.body.concat(f.cap.slice(1,-1));
    assert.deepEqual(f.cap[0],f.body.at(-1));assert.deepEqual(f.cap.at(-1),f.body[0]);
    assert.equal(crossingCount(points),0,`crossings at t=${t}`);
    const zero=f.body.findIndex(p=>Math.hypot(...p)<1e-12);assert.ok(zero>0&&zero<f.body.length-1);
    assert.ok(Math.hypot(...sub(f.body[zero-1],f.body[zero+1].map(x=>-x)))<1e-10);
    const angle=(u,v)=>Math.acos(Math.max(-1,Math.min(1,u.reduce((s,x,i)=>s+x*v[i],0)/(Math.hypot(...u)*Math.hypot(...v)))));
    assert.ok(angle(sub(f.body.at(-1),f.body.at(-2)),sub(f.cap[1],f.cap[0]))<.035);
    assert.ok(angle(sub(f.cap.at(-1),f.cap.at(-2)),sub(f.body[1],f.body[0]))<.035);
    assert.ok(points.every(p=>p.every(Number.isFinite)));
  }
});

test('time motion unwinds the arms, moves the cap clockwise/inward, and loses area',()=>{
  let previous=Infinity;
  for(let t=-23.5;t<=-8.5;t+=1){
    const f=spiralFrame(data,t),next=spiralFrame(data,t+.01);
    assert.ok(f.R<previous);previous=f.R;
    assert.ok(cross(f.tip,next.tip)<0);
    assert.ok(next.R<f.R&&next.width>f.width);
    const loss=(area(next)-area(f))/.01;
    assert.ok(Math.abs(loss+2*Math.PI)<.06,`area derivative ${loss} at ${t}`);
    assert.ok(next.body.length<f.body.length);
  }
});

test('cap uses the normal correction, snapshots are reproducible, and domains are checked',()=>{
  assert.equal(Math.hypot(...correctedCap(data,-18,0)),0);
  const p=2,F=interpolate(data.correction,p),a=correctedCap(data,-18,p);
  assert.ok(Math.abs(a[0]+Math.asin(Math.tanh(p))-F*Math.tanh(p)/72)<1e-12);
  assert.equal(snapshotSVG(data),readFileSync(new URL('../site/assets/solitons/ancient-spiral-curves.svg',import.meta.url),'utf8'));
  for(const t of [-25,-7,0,NaN])assert.throws(()=>spiralFrame(data,t),RangeError);
});
