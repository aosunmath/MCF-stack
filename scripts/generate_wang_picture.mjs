// Generate a reproducible mathematical schematic and its interactive descriptor.
import {writeFileSync} from 'node:fs';
import {wangMesh,wangRotation} from '../site/assets/wang-geometry.mjs';
const out=new URL('../site/assets/solitons/',import.meta.url);
const mesh=wangMesh('level',1,64,48);
writeFileSync(new URL('anisotropic-quadratic.json',out),JSON.stringify({
  kind:'wang-level-schematic',status:'schematic',...mesh,
  source:'Xu-Jia Wang, Annals of Mathematics 173 (2011), Theorems 1.2–1.3 and Section 5, pp. 1225–1234.',
  formula:'f(x)=(x1²+x2²)/2+((1+x3²)^(3/4)-1)/6; F_h(x)=f(sqrt(h)*x)/h',
  note:'Original convex schematic, not a numerical translator; k=2 is an illustrated blow-down model, not asserted for every family member.'
})+'\n');
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;');
const text=(x,y,s,size=16,color='#183f52')=>`<text x="${x}" y="${y}" font-size="${size}" fill="${color}">${esc(s)}</text>`;
function surface(mode,cx,cy,scale){
  const d=wangMesh(mode,1,72,48),rot=wangRotation(.3,.45);
  const project=p=>[0,1,2].map(i=>rot[i]*p[0]+rot[i+3]*p[1]+rot[i+6]*p[2]);
  const ps=d.vertices.map(project),screen=p=>[cx+scale*p[0],cy-scale*p[1]];
  const faces=d.faces.map(f=>({f,depth:f.reduce((s,i)=>s+ps[i][2],0)/3})).sort((a,b)=>a.depth-b.depth);
  let svg='';
  for(const {f} of faces){
    const n=project(d.normals[f[0]]),sign=n[2]<0?-1:1;
    const light=.5+.5*Math.max(0,sign*(-.35*n[0]+.55*n[1]+.85*n[2])/Math.hypot(.35,.55,.85));
    const tint=mode==='limit'?[199,138,69]:[71,158,171],rgb=tint.map(v=>Math.round(v*light)).join(',');
    svg+=`<polygon points="${f.map(i=>screen(ps[i]).map(v=>v.toFixed(2)).join(',')).join(' ')}" fill="rgb(${rgb})" stroke="rgb(${rgb})" stroke-width=".35"/>`;
  }
  // Meridian and latitude wires only on front-facing vertices.
  for(const path of d.paths){let open=false,part='';for(const i of path){
    if(project(d.normals[i])[2]<0){open=false;continue;}
    part+=(open?'L':'M')+screen(ps[i]).map(v=>v.toFixed(2)).join(',');open=true;
  }svg+=`<path d="${part}" fill="none" stroke="#183f52" stroke-opacity=".35" stroke-width=".7"/>`;}
  return svg;
}
let body=text(26,35,'Wang’s entire convex translators',24)+text(26,61,'A hypersurface in ℝ⁴, seen through its level surfaces',16);
body+=text(26,103,'FINITE HEIGHT · SCHEMATIC',14,'#21667f');
body+=surface('level',308,207,54);
body+=text(26,321,'Compact convex level in (x₁,x₂,x₃)',18)+text(26,347,'Circle symmetry in (x₁,x₂); axial dependence in x₃.',15);
body+='<line x1="26" y1="371" x2="614" y2="371" stroke="#cad9df"/>';
body+=text(26,404,'k = 2 BLOW-DOWN MODEL',14,'#a56a2d');
body+=surface('limit',310,500,42);
body+=text(26,598,'Q = (x₁² + x₂²)/2;  {Q = 1} = S¹(√2) × ℝ',18);
body+=text(26,626,'The free direction is x₃. Both cylinder ends are truncated.',15);
body+=text(26,659,'Finite shape is illustrative; no translator PDE is solved.',15);
const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="640" height="680" viewBox="0 0 640 680" role="img" aria-labelledby="title desc"><title id="title">Level geometry of Wang’s higher-dimensional convex translators</title><desc id="desc">A teal closed elongated convex schematic level surface above an ochre exact round cylinder of radius square root of two. These are two-dimensional horizontal sections in the base R3 of a graph in R4, not the full translator. The finite shape uses a stated illustrative convex function. The cylinder represents the k equals two quadratic blow-down model, with both ends cut off for display.</desc><rect width="640" height="680" fill="#f7fafb"/><g font-family="Arial, Helvetica, sans-serif">${body}</g></svg>\n`;
writeFileSync(new URL('anisotropic-quadratic.svg',out),svg);
console.log('Generated Wang level schematic and exact quadratic-cylinder comparison.');
