// Reproduce the static time plate and viewer metadata with no external packages.
import {writeFileSync} from 'node:fs';
import {lawlorProfile,neckScale} from '../site/assets/lawlor-flow-viewer.mjs';
const out=new URL('../site/assets/solitons/',import.meta.url);
const blue='#247b99',gold='#b57139',ink='#183b4e',muted='#657b87';
const parts=[`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 780" role="img" aria-labelledby="title desc">
<title id="title">A neck closes only at infinite time</title>
<desc id="desc">Su–Tsai–Wood construction: four signed generating profiles of an equal-angle Lawlor neck in complex dimension three, at model times zero, one, five and infinity. All four have the same spatial scale. An inset magnifies the neck to unit waist. The global compact flow is a connected sum of two three-tori; the planar profiles are not the full submanifold or a simulated mean curvature flow.</desc>
<rect width="960" height="780" fill="#f7fafb"/>
<g font-family="Arial, Helvetica, sans-serif">`];
const text=(x,y,s,size=16,color=ink,weight=400,anchor='start')=>parts.push(`<text x="${x}" y="${y}" font-size="${size}" fill="${color}" font-weight="${weight}" text-anchor="${anchor}">${s}</text>`);
const line=(x1,y1,x2,y2,color=muted,width=1.5,dash='')=>parts.push(`<path d="M ${x1} ${y1} L ${x2} ${y2}" fill="none" stroke="${color}" stroke-width="${width}"${dash?` stroke-dasharray="${dash}"`:''}/>`);
const box=(x,y,w,h)=>parts.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="10" fill="white" stroke="#d8e4e9"/>`);
function profile(cx,cy,scale,eps,rad=3){
  const angle=Math.PI/6;
  for(const sign of [-1,1])line(cx-rad*scale*Math.cos(angle),cy+sign*rad*scale*Math.sin(angle),cx+rad*scale*Math.cos(angle),cy-sign*rad*scale*Math.sin(angle),eps?'#aebfc8':sign>0?blue:gold,eps?1.3:2.7,eps?'4 4':'');
  if(eps){const points=lawlorProfile(3,eps,rad,200),half=100;
    for(const sign of [-1,1])for(const [ps,col] of [[points.slice(0,half+1),blue],[points.slice(half),gold]])parts.push(`<path d="${ps.map(([x,y],i)=>`${i?'L':'M'} ${(cx+sign*scale*x).toFixed(3)} ${(cy-sign*scale*y).toFixed(3)}`).join(' ')}" fill="none" stroke="${col}" stroke-width="3" stroke-linecap="round"/>`);
    line(cx,cy,cx+eps*scale,cy,'#98732d',1.5,'3 3');
    for(const sign of [-1,1])parts.push(`<circle cx="${cx+sign*eps*scale}" cy="${cy}" r="3.5" fill="#bd963d"/>`);
  }
  parts.push(`<circle cx="${cx}" cy="${cy}" r="2.6" fill="${ink}"/>`);
}
text(28,38,'A neck closes only at infinite time',28,ink,600);
text(28,66,'Su–Tsai–Wood · m = 3 in C³ / Γ · exact local profiles, leading-order time model',16,muted);
text(28,100,'FIXED SPATIAL SCALE',12,muted,600);
const stages=[0,1,5,Infinity];
for(let j=0;j<4;j++){
  const x=24+j*234,eps=neckScale(stages[j]);box(x,116,210,232);
  text(x+16,145,j===3?'τ → ∞':`τ = ${stages[j]}`,20,ink,600);
  text(x+16,169,j===3?'Singular limit':'Smooth neck model',13,muted);
  profile(x+105,241,35,eps);
  text(x+105,315,j===3?'Two transverse planes':`ε / ε₀ = ${j===0?'1':j===1?'1/2':'1/6'}`,15,ink,500,'middle');
  if(j<3)text(x+222,242,'→',19,muted,400,'middle');
}
text(28,376,'The gold marks are opposite representatives of the waist sphere S².',15,ink);
text(28,399,'Signed profiles ±γ represent one connected 3-dimensional neck, not two separate components.',14,muted);
box(24,420,458,214);box(498,420,438,214);
text(42,448,'What is being drawn?',19,ink,600);
text(42,478,'γ(s) = ε (1 + is)¹⁄³,   s ∈ ℝ',20,ink);
text(42,507,'Each γ generates the sphere {γω : ω ∈ S²}.',16,ink);
text(42,534,'Blue and ochre mark the two sides of the neck.',15,muted);
text(42,562,'Their tangent planes stay fixed as ε decreases.',15,muted);
text(42,598,'Model clock: ε / ε₀ = (1 + τ)⁻¹',18,ink,500);
text(516,448,'Magnify by ε₀ / ε',19,ink,600);
profile(620,534,30,1,2.6);
text(724,506,'Unit-waist neck',16,ink,600);
text(724,532,'persists after',15,muted);
text(724,554,'rescaling.',15,muted);
text(516,607,'As t → ∞: smooth Lawlor-neck limit (Prop. 9.5).',14,muted);
text(28,669,'GLOBAL TOPOLOGY  ·  THE COMPACT FLOW',12,muted,600);
text(28,701,'T³ # T³',22,ink,600);text(175,701,'every finite time',16,muted);
line(350,693,450,693,muted);text(451,700,'→',24,muted);
text(501,701,'X₁ ∪ X₂',22,ink,600);text(656,701,'meeting at one point as t → ∞',16,muted);
text(28,739,'The full flow is not explicit. Changing the scale of a minimal neck alone does not solve MCF.',15,ink);
text(28,763,'Source: arXiv:2401.02228v3, §2.3, equation (1.1), and Proposition 9.5. Original profile drawing.',13,muted);
parts.push('</g></svg>\n');writeFileSync(new URL('su-tsai-wood.svg',out),parts.join('\n'));
const vertices=lawlorProfile().map(p=>[...p,0]);
writeFileSync(new URL('su-tsai-wood.json',out),JSON.stringify({kind:'lawlor-infinite-time',status:'exact-profile-asymptotic-time',vertices,faces:[],paths:[vertices.map((_,i)=>i)],source:{url:'https://arxiv.org/html/2401.02228v3',locators:['Section 2.3 and Proposition 2.13','equation (1.1)','Definition 3.3','Proposition 9.5']},model:{dimension:3,angles:'pi/m',profile:'gamma(s) = epsilon (1 + i s)^(1/m), principal root',scale:'epsilon/epsilon0 = (1+tau)^(-1/(m-2))',clock:'tau = c (m-2) epsilon0^(m-2) t / 2',domain:'s real; omega in S^(m-1); tau >= 0',limitations:'Exact local equal-angle Lawlor neck; time-dependent dilations are not MCF. No global gluing correction or PDE solution computed.'},snapshots:[0,1,5,'infinity']},null,2)+'\n');
