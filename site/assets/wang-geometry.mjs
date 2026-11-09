// An explicit convex illustration, NOT a solution of the translator equation.
// F_h(x) = |x'|²/2 + ((1+h*x3²)^(3/4)-1)/(6h).
export const WANG_WINDOW=3.8;
export function axialHeight(s,h=1){return Math.expm1(.75*Math.log1p(h*s*s))/(6*h);}
export function modelHeight(x,y,s,h=1){return (x*x+y*y)/2+axialHeight(s,h);}
export function axialTip(h=1){return Math.sqrt(Math.expm1((4/3)*Math.log1p(6*h))/h);}
export function axialSlope(s,h=1){return .25*s/(1+h*s*s)**.25;}
const unit=p=>{const l=Math.hypot(...p);return p.map(v=>v/l);};

export function wangMesh(mode='level',h=1,rows=100,columns=64){
  if(!['level','slice','limit'].includes(mode)||!(h>=1&&Number.isFinite(h)))throw new Error('Invalid Wang illustration parameters');
  const vertices=[],normals=[],faces=[],paths=[];
  const limit=mode==='limit',slice=mode==='slice';
  const extent=slice||limit?WANG_WINDOW:Math.min(WANG_WINDOW,axialTip(h));
  for(let i=0;i<=rows;i++){
    // Cosine spacing resolves the tips of a closed level surface.
    const s=extent*(-Math.cos(Math.PI*i/rows));
    for(let j=0;j<=columns;j++){
      if(slice){
        const x=-1.7+3.4*j/columns,z=modelHeight(x,0,s,h);
        vertices.push([s,x,z]);normals.push(unit([-axialSlope(s,h),-x,1]));
      }else{
        const a=2*Math.PI*j/columns;
        const r=limit?Math.SQRT2:Math.sqrt(Math.max(0,2*(1-axialHeight(s,h))));
        const x=r*Math.cos(a),y=r*Math.sin(a);
        vertices.push([s,x,y]);
        normals.push(unit([limit?0:axialSlope(s,h),x,y]));
      }
      if(i<rows&&j<columns){const a=i*(columns+1)+j,b=a+columns+1;faces.push([a,b,a+1],[a+1,b,b+1]);}
    }
  }
  for(let i=0;i<=rows;i+=10)paths.push(Array.from({length:columns+1},(_,j)=>i*(columns+1)+j));
  for(let j=0;j<columns;j+=8)paths.push(Array.from({length:rows+1},(_,i)=>i*(columns+1)+j));
  return {vertices,normals,faces,paths,extent,clipped:!slice&&!limit&&axialTip(h)>WANG_WINDOW};
}

export function wangRotation(yaw,pitch){
  const cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);
  return [cy,-sy*sp,sy*cp,-sy,-cy*sp,cy*cp,0,cp,sp];
}
