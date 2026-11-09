import test from 'node:test';
import assert from 'node:assert/strict';
import {lawlorProfile,neckScale} from '../site/assets/lawlor-flow-viewer.mjs';
const multiply=([a,b],[c,d])=>[a*c-b*d,a*d+b*c];
const power=(z,n)=>Array.from({length:n}).reduce(p=>multiply(p,z),[1,0]);

test('equal-angle profile lies on Re(gamma^m) = epsilon^m with the correct waist and ends',()=>{
  for(const m of [3,4,5,6])for(const eps of [1,.5,.1,.02]){
    const ps=lawlorProfile(m,eps,3,320);
    assert.ok(Math.abs(Math.hypot(...ps[160])-eps)<1e-12);
    assert.ok(Math.abs(ps[160][1])<1e-12);
    for(const p of ps){
      assert.ok(Math.abs(power(p,m)[0]-eps**m)<2e-11);
      assert.ok(Math.abs(Math.atan2(p[1],p[0]))<Math.PI/(2*m));
      assert.ok(Math.hypot(...p)>=eps-1e-12);
    }
    assert.ok(Math.abs(Math.hypot(...ps[0])-3)<1e-12);
    assert.ok(Math.abs(ps[0][0]-ps.at(-1)[0])<1e-12);
    assert.ok(Math.abs(ps[0][1]+ps.at(-1)[1])<1e-12);
  }
});

test('profile has constant special Lagrangian phase: Re(gamma^(m-1) gamma prime) = 0',()=>{
  // Independent differentiation of gamma(s)=(1+i s)^(1/m).
  for(const m of [3,4,5,6])for(const s of [-5,-.5,0,.5,5]){
    const gamma=t=>{const r=Math.hypot(1,t)**(1/m),a=Math.atan(t)/m;return [r*Math.cos(a),r*Math.sin(a)];};
    const h=1e-5,a=gamma(s-h),b=gamma(s+h),d=b.map((v,i)=>(v-a[i])/(2*h));
    const determinant=multiply(power(gamma(s),m-1),d);
    assert.ok(Math.abs(determinant[0])<1e-9);
    assert.ok(Math.abs(determinant[1]-1/m)<1e-9);
  }
});

test('scale obeys the normalized leading ODE and vanishes only at infinite model time',()=>{
  for(const m of [3,4,5,6])for(const tau of [0,1,5,64,10000]){
    const eps=neckScale(tau,m),h=1e-4;
    const derivative=(neckScale(tau+h,m)**2-neckScale(tau,m)**2)/h;
    assert.ok(eps>0 && eps<=1);
    assert.ok(Math.abs(derivative+2/(m-2)*eps**m)<.00031);
    assert.equal(neckScale(Infinity,m),0);
  }
  assert.throws(()=>neckScale(-1));assert.throws(()=>neckScale(0,2));
});

test('magnifying the local model by its waist recovers one fixed profile',()=>{
  for(const m of [3,4,5,6])for(const eps of [.5,.1,.02]){
    const unit=lawlorProfile(m,1,3,120),scaled=lawlorProfile(m,eps,3*eps,120);
    for(let i=0;i<unit.length;i++)for(let j=0;j<2;j++)assert.ok(Math.abs(scaled[i][j]/eps-unit[i][j])<1e-12);
  }
});
