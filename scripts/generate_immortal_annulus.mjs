// Reproducible original schematic; no PDE solution or physical time data.
import {writeFileSync} from 'node:fs';
import {ANNULUS,annulusGeometry} from '../site/assets/immortal-annulus-viewer.mjs';
const out=new URL('../site/assets/solitons/',import.meta.url);
const initial=annulusGeometry(0);
writeFileSync(new URL('immortal-annulus.json',out),JSON.stringify({name:'immortal-annulus',kind:'immortal-annulus-stages',status:'schematic',parameters:ANNULUS,...initial}));
let svg='<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480" viewBox="0 0 640 480" role="img" aria-labelledby="title desc" font-family="system-ui, sans-serif"><title id="title">Immortal annulus: three finite stages and the infinite-time limit</title><desc id="desc">Original cutaway schematics at the same scale show a narrowing positive neck and two sheets flattening locally. At infinite time one plane is counted twice. The far ends retain their original asymptotic heights; only a fixed radial window is drawn. These are not computed MCF time slices.</desc><rect width="640" height="480" fill="#f7fafb"/>';
const text=(x,y,s,size=14,color='#294f60')=>{svg+=`<text x="${x}" y="${y}" font-size="${size}" fill="${color}">${s}</text>`;};
text(20,30,'Immortal annulus · a sequence of schematic stages',21);
text(20,53,'0 &lt; t₁ &lt; t₂ &lt; t₃ · the same local window and scale',14,'#58717d');
const project=([x,y,z],cx,cy)=>{const yaw=.25,pitch=.25,d=x*Math.sin(yaw)+y*Math.cos(yaw);return [cx+21*(x*Math.cos(yaw)-y*Math.sin(yaw)),cy-21*(z*Math.cos(pitch)-d*Math.sin(pitch)),z*Math.sin(pitch)+d*Math.cos(pitch)];};
for(const [k,p,title,note] of [[0,0,'t₁ · Earlier','One connected annulus'],[1,.5,'t₂ · Intermediate','A smaller neck; closer sheets'],[2,1,'t₃ · Later','Neck still positive at finite time'],[3,null,'t → ∞ · Local limit','One plane counted twice']]){
  const x=16+(k%2)*312,y=72+Math.floor(k/2)*175,cx=x+148,cy=y+84;
  svg+=`<rect x="${x}" y="${y}" width="296" height="162" rx="8" fill="white" stroke="#d8e4e9"/>`;
  text(x+13,y+25,title,16);
  if(p===null){
    const points=Array.from({length:129},(_,i)=>project([5*Math.cos(i*Math.PI/64),5*Math.sin(i*Math.PI/64),0],cx,cy));
    svg+=`<polygon points="${points.map(q=>q.slice(0,2).join(',')).join(' ')}" fill="#b5ced5" stroke="#436c7d"/>`;
    text(cx-12,cy+5,'× 2',18);
  }else{
    const g=annulusGeometry(p,48,48),q=g.vertices.map(v=>project(v,cx,cy));
    const faces=g.faces.map((f,i)=>({f,i,z:f.reduce((s,j)=>s+q[j][2],0)/3})).filter(({f})=>f.every(i=>g.vertices[i][1]>=-1e-8)).sort((a,b)=>a.z-b.z);
    for(const {f,i} of faces){
      const c=g.faceGroups[i]?'#65a0b3':'#d5a16b';
      svg+=`<polygon points="${f.map(j=>q[j].slice(0,2).map(x=>x.toFixed(2)).join(',')).join(' ')}" fill="${c}" stroke="${c}" stroke-width=".25"/>`;
    }
    for(const j of [0,24])svg+=`<polyline points="${Array.from({length:49},(_,i)=>q[i*48+j].slice(0,2).join(',')).join(' ')}" fill="none" stroke="#315b6a" stroke-width="1.3"/>`;
  }
  text(x+13,y+145,note,13);
}
text(20,441,'Cutaways expose the neck. The far ends still approach fixed planes ±h.',14);
text(20,465,'Qualitative stages only: no physical times or convergence rate are assigned.',13,'#58717d');
svg+='</svg>\n';writeFileSync(new URL('immortal-annulus.svg',out),svg);
console.log('Generated immortal-annulus.json and immortal-annulus.svg');
