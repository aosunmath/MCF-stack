// Abresch–Langer numerical profiles in Hvec = -Xperp/2 normalization.
// See documentation/abresch-langer-controls.md for the quadrature derivation.
const TAU=2*Math.PI;
export const ABRESCH_LANGER_LIMIT=100;

export function validateAbreschLanger(m,ell) {
  if(!Number.isInteger(m)||!Number.isInteger(ell)||m<1||ell<1)
    throw new Error('Enter positive whole numbers for m and ℓ.');
  if(m>ABRESCH_LANGER_LIMIT||ell>ABRESCH_LANGER_LIMIT)
    throw new Error(`This viewer supports m and ℓ up to ${ABRESCH_LANGER_LIMIT}.`);
  if(2*m<=ell||2*m*m>=ell*ell)
    throw new Error('Choose indices with 1/2 < m/ℓ < 1/√2. Try (2, 3) or (3, 5).');
  let a=m,b=ell;
  while(b){const r=a%b;a=b;b=r;}
  if(a!==1)
    throw new Error(`Use coprime indices: (${m}, ${ell}) traces (${m/a}, ${ell/a}) ${a} times.`);
}

// The support function obeys h''+h=2/h. For its maximum a, let
// q=log(a/h), Q=log(a/h_min), D=a²(1-exp(-2q))-4q=(h')².
function lowerTurningPoint(a) {
  let lo=1e-12,hi=a*a/4;
  for(let k=0;k<60;k++){
    const q=(lo+hi)/2;
    if(a*a*(-Math.expm1(-2*q))-4*q>0)lo=q;else hi=q;
  }
  return (lo+hi)/2;
}

function phase(a,Q,u) {
  const q=Q*Math.sin(u)**2,delta=Q*Math.cos(u)**2;
  const h=a*Math.exp(-q),minimum=a*Math.exp(-Q);
  // Use the nearer turning point to avoid subtraction at either endpoint.
  const squaredSpeed=q<Q/2?a*a*(-Math.expm1(-2*q))-4*q
    :4*delta-minimum*minimum*Math.expm1(2*delta);
  return {h,speed:Math.sqrt(Math.max(0,squaredSpeed))};
}

function angularDensity(a,Q,u) {
  const minimum=a*Math.exp(-Q);
  if(u<1e-14)return a*Math.sqrt(2*Q/(a*a-2));
  if(Math.PI/2-u<1e-14)return minimum*Math.sqrt(2*Q/(2-minimum*minimum));
  const {h,speed}=phase(a,Q,u);
  return 2*Q*Math.sin(u)*Math.cos(u)*h/speed;
}

function periodIntegral(a,intervals=1024,record=false) {
  // q=Q sin²(u) removes both endpoint square-root singularities.
  const Q=lowerTurningPoint(a),du=Math.PI/(2*intervals),samples=[];
  let angle=0,previous=angularDensity(a,Q,0);
  if(record)samples.push([0,a,0]);
  for(let i=1;i<=intervals;i++){
    const u=i*du,next=angularDensity(a,Q,u);
    angle+=du/6*(previous+4*angularDensity(a,Q,u-du/2)+next);
    previous=next;
    if(record&&i%4===0){
      const {h,speed}=phase(a,Q,u);
      samples.push([angle,h,i===intervals?0:-speed]);
    }
  }
  return {period:2*angle,samples};
}

export function abreschLanger(m,ell) {
  validateAbreschLanger(m,ell);
  const target=TAU*m/ell;
  let lo=Math.sqrt(2)+1e-4,hi=32;
  for(let i=0;i<46;i++){
    const a=(lo+hi)/2;
    if(periodIntegral(a).period>target)lo=a;else hi=a;
  }
  const supportMaximum=(lo+hi)/2;
  const {period,samples}=periodIntegral(supportMaximum,1024,true);
  const refinedPeriod=periodIntegral(supportMaximum,2048).period;
  const periodError=Math.abs(period-target),quadratureChange=Math.abs(refinedPeriod-period);
  if(!Number.isFinite(period)||periodError>1e-9||quadratureChange>1e-9)
    throw new Error('The numerical period check failed. Please try another pair.');
  const cycle=samples.concat(samples.slice(1,-1).reverse().map(([t,h,p])=>[period-t,h,-p]));
  const vertices=[];
  for(let k=0;k<ell;k++)for(const [t,h,p] of cycle){
    const theta=k*period+t,c=Math.cos(theta),s=Math.sin(theta);
    vertices.push([h*c-p*s,h*s+p*c,0]);
  }
  // Retain the actual numerical closing point; do not force a closed polygon.
  vertices.push([supportMaximum*Math.cos(ell*period),supportMaximum*Math.sin(ell*period),0]);
  const closureError=Math.hypot(...vertices.at(-1).map((x,i)=>x-vertices[0][i]));
  return {vertices,supportMaximum,period,periodError,quadratureChange,closureError};
}
