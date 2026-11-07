// AV97, n=2, m=3, K=1. This is an asymptotic illustration, not an MCF solver.
export const XI=Math.cbrt(2);
export const TIMES=[1e-3,1e-4,1e-6,0];
export const COLORS=['#337e9a','#517d42','#b47731','#8c5877'];
export const smooth=t=>{t=Math.max(0,Math.min(1,t));return t*t*t*(10+t*(-15+6*t));};

export function bowlHeight(r,data){
  const {step,height}=data.bowl;
  if(!Number.isFinite(r)||r<0||r>(height.length-1)*step)throw new Error('Bowl radius outside numerical data');
  if(r<step)return r*r/4+r**4/128;
  const i=Math.min(height.length-2,Math.floor(r/step)),f=r/step-i;
  return height[i]*(1-f)+height[i+1]*f;
}
export function scales(s){
  if(!(s>0))throw new Error('Smooth slices require T-t > 0');
  return {tip:-XI*Math.cbrt(s),H:XI/3*s**(-2/3),radial:Math.sqrt(s),axial:Math.cbrt(s)};
}
export function innerRadius(y,s){return Math.SQRT2+Math.sqrt(s)*(y**3-6*y)/(2*Math.SQRT2);}

export function neckpinchProfile(s,data){
  if(!Number.isFinite(s)||s<0||s>1e-3)throw new Error('Illustrative time outside [0, 0.001]');
  const b=.6;
  if(s===0)return Array.from({length:241},(_,i)=>{
    const x=b*i/240;return [x,Math.sqrt(Math.max(0,x**3*(1-(x/b)**4)))];
  });
  const {tip,H}=scales(s),r0=.9*Math.sqrt(2*s),join=-XI*Math.cbrt(s)*Math.cbrt(1-.9**2);
  const profile=[];
  // The tip uses the actual numerical bowl. A designed blend joins the
  // inverse intermediate profile; it is not the paper's existence proof.
  for(let i=0;i<=90;i++){
    const r=r0*i/90,xb=tip+bowlHeight(H*r,data)/H;
    const xi=-Math.cbrt(Math.max(0,2*s-r*r));
    const w=smooth((r/r0-.3)/.7);
    profile.push([xb*(1-w)+xi*w,r]);
  }
  const xs=[],bounds=[join,-.3*Math.abs(tip),.3*Math.abs(tip),.12,b],counts=[45,100,50,80];
  for(let j=0;j<counts.length;j++)for(let i=1;i<=counts[j];i++)xs.push(bounds[j]+(bounds[j+1]-bounds[j])*i/counts[j]);
  for(const x of xs){
    // Recover the cubic Hermite correction at the parabolic scale. The
    // cutoff is exactly one for |x| <= .1 |tip|, and zero outside .3 |tip|.
    const cut=1-smooth((Math.abs(x)/Math.abs(tip)-.1)/.2);
    const q=2*s+x**3-6*s*x*cut;
    const closing=x>0?1-(x/b)**4:1;
    profile.push([x,Math.sqrt(Math.max(0,q*closing))]);
  }
  return profile;
}

// Orthographic viewing with an equal spatial scale on all axes.
export function project([x,y,z],yaw=-.28,pitch=.2){
  const u=x*Math.cos(yaw)-y*Math.sin(yaw),v=x*Math.sin(yaw)+y*Math.cos(yaw);
  return [u,z*Math.cos(pitch)-v*Math.sin(pitch),z*Math.sin(pitch)+v*Math.cos(pitch)];
}
export function surfacePolygons(profile,yaw=-.28,pitch=.2,sectors=36){
  const rings=profile.map(([x,r])=>Array.from({length:sectors},(_,j)=>project([x,r*Math.cos(j*2*Math.PI/sectors),r*Math.sin(j*2*Math.PI/sectors)],yaw,pitch)));
  const faces=[];
  for(let i=0;i<rings.length-1;i++)for(let j=0;j<sectors;j++){
    const k=(j+1)%sectors,points=[rings[i][j],rings[i+1][j],rings[i+1][k],rings[i][k]];
    const a=points[0],u=points[1].map((v,i)=>v-a[i]),v=points[3].map((v,i)=>v-a[i]);
    const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
    const light=.45+.5*Math.abs((.2*n[0]+.4*n[1]+.8*n[2])/(Math.hypot(...n)||1));
    faces.push({points,depth:points.reduce((s,p)=>s+p[2],0)/4,light});
  }
  return faces.sort((a,b)=>a.depth-b.depth);
}
export function shade(hex,light){
  const c=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
  return `rgb(${c.map(v=>Math.round(v*light+245*(1-light)*.27)).join(',')})`;
}
export const timeLabel=s=>s===0?'Singular target · s = 0':`s = T − t = 10${({'-3':'⁻³','-4':'⁻⁴','-5':'⁻⁵','-6':'⁻⁶','-7':'⁻⁷'})[String(Math.round(Math.log10(s)))]??''}`;
