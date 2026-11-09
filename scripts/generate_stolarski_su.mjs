// Original drawings from exact Lawlor geometry; no source figures are copied.
import {writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {SS,profile,slicePoint,neckMesh,neckScale,surfaceScene} from '../site/assets/stolarski-su-viewer.mjs';
const out=fileURLToPath(new URL('../site/assets/solitons/',import.meta.url));
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;');
let svg='';
function start(w,h,title,desc){svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" role="img" aria-labelledby="title desc"><title id="title">${escape(title)}</title><desc id="desc">${escape(desc)}</desc><rect width="${w}" height="${h}" fill="#f7fafb"/>`;}
function text(s,x,y,size=18,color='#284b5c',anchor='start'){svg+=`<text x="${x}" y="${y}" font-family="system-ui,sans-serif" font-size="${size}" fill="${color}" text-anchor="${anchor}">${escape(s)}</text>`;}
function path(points,color,width=1,dash=''){svg+=`<polyline points="${points.map(p=>p.map(x=>x.toFixed(2)).join(',')).join(' ')}" fill="none" stroke="${color}" stroke-width="${width}"${dash?` stroke-dasharray="${dash}"`:''}/>`;}
function plot(a,cx,cy,size,color=null){
  const screen=([r,h])=>[cx+size*h,cy-size*r],curve=profile(3,a,160),mid=curve.length>>1;
  for(const sign of [-1,1]){
    path(curve.slice(0,mid+1).map(p=>screen(p.map(v=>v*sign))),color??'#277e9b',2.5);
    path(curve.slice(mid).map(p=>screen(p.map(v=>v*sign))),color??'#b7743e',2.5);
  }
}
function rays(cx,cy,size){for(const sign of [-1,1])for(const end of [-1,1])path([[cx,cy],[cx+size*end*SS.radius*.5,cy-size*sign*SS.radius*Math.sqrt(3)/2]],'#a3b2b9',1,'4 5');}

start(1000,760,'Stolarski–Su: a neck collapsing at three times','Asymptotic illustration using exact Lawlor profiles. Three projected two-dimensional slices and their planar profiles at the same spatial scale; not numerical flow slices.');
text('A shrinking neck, two different blow-up limits',28,41,28);
text('Stolarski–Su · n = 3, K = 2 · full flow in C³ = R⁶',28,73,18);
text('Asymptotic model only · exact Lawlor geometry with a prescribed shrinking scale',28,103,16,'#627a85');
for(const [i,t]of SS.times.entries()){
  const x=10+i*330,a=neckScale(t,2),box={x:x+5,y:155,w:315,h:230};
  text(`τ = ${t.toFixed(1)}`,x+160,139,22,'#284b5c','middle');
  const scene=surfaceScene(3,a,box,undefined,[40,40]);
  for(const p of scene.polygons)svg+=`<polygon points="${p.points.map(q=>q.map(v=>v.toFixed(2)).join(',')).join(' ')}" fill="${p.color}" stroke="${p.color}" stroke-width=".4"/>`;
  path(Array.from({length:81},(_,j)=>scene.project(slicePoint([a,0],Math.PI*j/80))),'#834d85',2.5);
  const bx=x+240,by=382;path([[bx,by],[bx+scene.scale,by]],'#526d7a',1.5);text('1 unit',bx+scene.scale/2,by-7,11,'#526d7a','middle');
  text(`neck size a/a₀ = ${(1-t).toFixed(1)}`,x+160,414,17,'#834d85','middle');
  rays(x+160,510,33);plot(a,x+160,510,33);
  text('planar profile ±w',x+160,604,14,'#627a85','middle');
  if(i)path([[x-5,122],[x-5,613]],'#dce5e9');
}
text('Blue / ochre: two sides of the neck. Purple: its waist. Gray rays: limiting planes.',28,642,17);
text('Half of a 2D slice is projected to expose the neck. Crossings are projection artifacts.',28,669,16);
text('τ = (t − t₀)/(T − t₀),  a/a₀ = (1 − τ)ᴷ⁄². All panels share one camera and scale.',28,697,17);
text('The actual flow includes a PDE correction. A shrinking family of minimal necks is not itself MCF.',28,725,15);
text('Source: arXiv:2607.03152v1, Theorem 1.1, Remark 1, §2.2, equations (7)–(13).',28,747,12,'#627a85');
writeFileSync(out+'stolarski-su.svg',svg+'</svg>\n');

start(1000,570,'Two zooms of the same neck pinch','Parabolic rescaling makes the neck collapse to rays, while the finer Type II rescaling retains a smooth Lawlor neck. Exact profiles, schematic time law; n=3 and K=2.');
text('The scale determines what you see',28,40,28);
text('n = 3, K = 2 · planar sections of the asymptotic model · q = 1 − τ',28,72,17);
const colors=['#277e9b','#b7743e','#834d85'];
for(const [i,mode]of ['parabolic','neck'].entries()){
  const cx=250+500*i,cy=294,size=65;
  text(i?'Neck zoom: q⁻ᴷ⁄² L(t)':'Parabolic zoom: q⁻¹⁄² L(t)',cx,116,22,'#284b5c','middle');
  text(i?'Smooth Lawlor neck survives':'Neck disappears; tangent planes remain',cx,145,16,'#627a85','middle');
  rays(cx,cy,size);
  if(i)plot(SS.a0,cx,cy,size,'#834d85');
  else SS.times.forEach((t,j)=>plot(neckScale(t,2,mode),cx,cy,size,colors[j]));
  text(i?'All three model profiles coincide':'Three times approach the dashed rays',cx,467,16,'#627a85','middle');
}
path([[500,99],[500,480]],'#dce5e9');
for(const [j,t]of SS.times.entries()){path([[40+j*170,508],[66+j*170,508]],colors[j],3);text(`τ = ${t.toFixed(1)}`,75+j*170,514,16);}
text('The true flow converges to these limits; this figure omits its parabolic correction.',28,550,16);
writeFileSync(out+'stolarski-su-limits.svg',svg+'</svg>\n');
const mesh=neckMesh(3,SS.a0,16,24);
writeFileSync(out+'stolarski-su.json',JSON.stringify({name:'stolarski-su',kind:'stolarski-su-asymptotic',status:'asymptotic-model',source:SS.source,sourceLocators:['Theorem 1.1 (3)–(5)','Remark 1','Section 2.2, equations (7)–(10)','Section 2.3, equation (13)','Section 5.3'],dimension:3,ambientDimension:6,formula:'w = a (1 + i sinh(v))^(1/n); X = w u, u in S^(n-1)',timeLaw:'tau = (t-t0)/(T-t0), q=1-tau; a_model=a0*q^(K/2)',omitted:'The modulated scale and PDE correction of the actual flow are not computed.',slice:'u=(cos(phi),sin(phi),0,...); orthogonal projection from C^2 to R^3',displayRadius:SS.radius,initialModelScale:SS.a0,times:SS.times,vertices:mesh.vertices,faces:mesh.faces,paths:[]})+'\n');
console.log('Generated Stolarski–Su time sequence, scale comparison, and geometry manifest.');
