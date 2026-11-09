// Rebuild the exact slice plate and the interactive viewer's geometry manifest.
import {writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {LW,slicePoint,sliceMesh,surfaceScene} from '../site/assets/lee-wang-expander-viewer.mjs';
const out=fileURLToPath(new URL('../site/assets/solitons/',import.meta.url));
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;');
let svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 860" role="img" aria-labelledby="title desc"><title id="title">Lee–Wang expander: exact real slices at four times</title><desc id="desc">Cone limit t=0 and expanding two-sheeted quadrics at t=0.25, 1, 4, all at the same spatial scale. The full connected three-manifold lives in C3, not R3.</desc><rect width="800" height="860" fill="#f7fafb"/>';
function text(s,x,y,size=20,color='#254858',anchor='start'){svg+=`<text x="${x}" y="${y}" font-family="system-ui,sans-serif" font-size="${size}" fill="${color}" text-anchor="${anchor}">${escape(s)}</text>`;}
function path(points,color,width=1,dash=''){svg+=`<polyline points="${points.map(p=>p.map(x=>x.toFixed(2)).join(',')).join(' ')}" fill="none" stroke="${color}" stroke-width="${width}" ${dash?`stroke-dasharray="${dash}"`:''}/>`;}
text('Lee–Wang expander',28,37,26);text('Exact real slices · n = 3, k = 2 · full ambient space C³ = R⁶',28,67,17);
text('x₃ = ±√(x₁² + x₂² + 2t)       Lₜ = √t L₁,  t > 0',28,100,20);
for(const [i,t] of LW.times.entries()){
  const x=10+(i%2)*390,y=122+Math.floor(i/2)*310,box={x:x+4,y:y+30,w:382,h:275};
  text(t===0?'t = 0 · singular cone limit':`t = ${t}`,x+195,y+20,21,'#254858','middle');
  const scene=surfaceScene(t,box,undefined,[16,40]);
  for(const poly of scene.polygons)svg+=`<polygon points="${poly.points.map(p=>p.map(x=>x.toFixed(2)).join(',')).join(' ')}" fill="${poly.color}" stroke="${poly.color}" stroke-width="0.4"/>`;
  for(const sign of [1,-1]){
    for(const theta of [0,Math.PI/2,Math.PI,3*Math.PI/2])path(Array.from({length:41},(_,j)=>scene.project(slicePoint(LW.radius*j/40,theta,0,sign))),'#677f8980',1,'3 4');
    path(Array.from({length:81},(_,j)=>scene.project(slicePoint(LW.radius,2*Math.PI*j/80,t,sign))),sign>0?'#266d87':'#98572d',1.2);
    const p=scene.project(slicePoint(0,0,t,sign));svg+=`<circle cx="${p[0]}" cy="${p[1]}" r="3.5" fill="${sign>0?'#21667f':'#ad622d'}"/>`;
  }
  const by=box.y+box.h-7,bx=x+310;path([[bx,by],[bx+scene.scale,by]],'#476170',2);text('1 unit',bx+scene.scale/2,by-8,12,'#476170','middle');
}
path([[400,122],[400,732]],'#dbe5e9');path([[20,432],[780,432]],'#dbe5e9');
text('Same spatial scale; fixed display cutoff r ≤ 3.2. Dashed gray: cone.',28,766,17);
text('The two real sheets connect through the circle direction in R⁶.',28,797,17);
text('These slices are not themselves mean curvature flows in R³.',28,825,17);
text('Lee–Wang (2010), Theorem 1.1 and Propositions 2.1–2.2.',28,848,13,'#627a85');
svg+='</svg>\n';writeFileSync(out+'lw-quadric-expanders.svg',svg);
const mesh=sliceMesh(1,12,32);
writeFileSync(out+'lw-quadric-expanders.json',JSON.stringify({name:'lw-quadric-expanders',kind:'lee-wang-expander-exact',status:'exact-parametrization',source:LW.source,sourceLocators:['Theorem 1.1','Proposition 2.1','Section 2.2','Proposition 2.2'],dimension:3,ambientDimension:6,timeDomain:'t > 0; t = 0 is only a cone limit',slice:'x3^2 - x1^2 - x2^2 = 2t',displayRadius:LW.radius,times:LW.times,vertices:mesh.vertices,faces:mesh.faces,paths:[]})+'\n');
console.log('Generated Lee–Wang expander exact time slices.');
