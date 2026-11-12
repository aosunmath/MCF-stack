// High-dimensional hypersurfaces are represented by (|x|, |y|) orbit profiles.
export function exponent(p,q,k){
  const N=p+q, alpha=(3-N+Math.sqrt(N*N-10*N+17))/2;
  return {alpha,beta:k/(1-alpha)};
}
export function interpolate(x,xs,ys){
  if(x<=xs[0])return ys[0];
  if(x>=xs.at(-1))return ys.at(-1);
  let a=0,b=xs.length-1;
  while(b-a>1){const m=(a+b)>>1;if(xs[m]>x)b=m;else a=m;}
  return ys[a]+(ys[b]-ys[a])*(x-xs[a])/(xs[b]-xs[a]);
}
export function scaleFor(view,t,b){return view==='inner'?b:view==='parabolic'?Math.sqrt(Math.abs(t)):1;}

export async function initSimonsCone(figure,config){
  const response=await fetch(new URL('./solitons/simons-cone-experiment.json',import.meta.url));
  if(!response.ok)throw Error('Simons-cone numerical data unavailable');
  const data=await response.json(),canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d');
  const controls=figure.querySelector('.soliton-controls'),help=figure.querySelector('.soliton-help'),status=figure.querySelector('.soliton-status');
  figure.classList.add('simons-cone-figure');
  controls.innerHTML='';
  const add=(tag,text,parent=controls)=>{const el=document.createElement(tag);if(text)el.textContent=text;parent.append(el);return el;};
  const select=(label,choices)=>{const l=add('label',label),s=add('select','',l);s.setAttribute('aria-label',label);for(const [v,t]of choices){const o=add('option',t,s);o.value=v;}return s;};
  const scenario=select('Construction',[['low','Low mode: n=5, k=2'],['bounded','Bounded H: n=4, k=4'],['compact','Compact: p=3, q=5, k=4'],['pde','Forward nonlinear PDE in R8']]);
  scenario.value=config.scenario;
  const view=select('Spatial scale',[['physical','Original coordinates'],['parabolic','Parabolic magnification'],['inner','Inner magnification']]);
  const label=add('label','Time / approach to singularity'),slider=add('input','',label);slider.type='range';slider.min=0;slider.max=100;slider.value=config.scenario==='pde'?55:35;slider.setAttribute('aria-label','Time / approach to singularity');
  const play=add('button','Play'),zin=add('button','Zoom +'),zout=add('button','Zoom −'),reset=add('button','Reset');
  for(const b of [play,zin,zout,reset])b.type='button';
  zin.setAttribute('aria-label','Zoom in');zout.setAttribute('aria-label','Zoom out');
  let zoom=1,playing=false,last=0,raf;
  canvas.setAttribute('aria-label','Orbit-space profile of a high-dimensional hypersurface. Left and right change time; plus and minus zoom.');
  help.textContent='Profile in (|x|, |y|), not a surface in three-space. Dashed gray: cone. Colored: computed profile. Use the time and scale controls; +/− zoom.';
  controls.hidden=false;help.hidden=false;canvas.hidden=false;figure.querySelector('img').hidden=true;
  function draw(){
    const width=canvas.clientWidth,height=canvas.clientHeight,dpr=devicePixelRatio||1;
    canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);
    ctx.fillStyle='#f7fafb';ctx.fillRect(0,0,width,height);
    const s=scenario.value, isPde=s==='pde';
    let p=s==='low'?5:s==='compact'?3:4,q=s==='low'?5:s==='compact'?5:4,k=s==='low'?2:4;
    const profile=data.profiles.find(d=>d.p===p&&d.q===q), {beta}=exponent(p,q,k);
    let t,b,points,kind,frame;
    if(isPde){
      frame=Math.round(Number(slider.value)/100*(data.pde.times.length-1));
      t=data.pde.times[frame];b=data.pde.axis[frame];
      points=data.pde.r.map((r,i)=>[r,data.pde.values[frame][i]]);
      kind='Nonlinear PDE · regularized trace';
    }else{
      const tau=10**(-.05-Number(slider.value)*.017);
      t=-tau;b=.7*tau**beta;
      points=profile.r.map((r,i)=>[b*r,b*profile.u[i]]);
      kind='Minimal ODE + asymptotic scale';
    }
    const parabolic=view.options[1];parabolic.disabled=isPde&&t===0;
    if(parabolic.disabled&&view.value==='parabolic')view.value='physical';
    const scale=scaleFor(view.value,t,b);
    // Inner display uses the measured numerical axis radius b, not a fitted rate.
    const extent=(view.value==='inner'?4:2)/zoom,mu=profile.cone_slope;
    const margin={left:52,right:22,top:65,bottom:47},pw=width-margin.left-margin.right,ph=height-margin.top-margin.bottom;
    const xMax=extent,yMax=extent*Math.max(1,mu)*1.05;
    const xy=(x,y)=>[margin.left+x/xMax*pw,height-margin.bottom-y/yMax*ph];
    ctx.font='12px system-ui';ctx.fillStyle='#153342';ctx.fillText(kind,16,22);
    ctx.font='11px system-ui';ctx.fillStyle='#476170';ctx.fillText(`ℝ^${p} × ℝ^${q} · ${isPde?'t':'model t'} = ${t.toPrecision(3)} · b = ${b.toPrecision(3)}`,16,42);
    for(let i=0;i<=4;i++){
      const x=xMax*i/4,y=yMax*i/4;
      ctx.strokeStyle='#dce6e9';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(...xy(x,0));ctx.lineTo(...xy(x,yMax));ctx.stroke();
      ctx.beginPath();ctx.moveTo(...xy(0,y));ctx.lineTo(...xy(xMax,y));ctx.stroke();
      ctx.fillStyle='#476170';ctx.textAlign='center';ctx.fillText(x.toPrecision(2),xy(x,0)[0],height-28);
      ctx.textAlign='right';ctx.fillText(y.toPrecision(2),44,xy(0,y)[1]+4);
    }
    ctx.save();ctx.beginPath();ctx.rect(margin.left,margin.top,pw,ph);ctx.clip();
    ctx.strokeStyle='#74838b';ctx.setLineDash([6,5]);ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(...xy(0,0));ctx.lineTo(...xy(xMax,mu*xMax));ctx.stroke();ctx.setLineDash([]);
    if(isPde){
      ctx.strokeStyle='#b5c5cd';ctx.lineWidth=1.3;ctx.beginPath();
      data.pde.r.forEach((r,i)=>{const z=xy(r/scale,data.pde.values[0][i]/scale);if(i===0)ctx.moveTo(...z);else ctx.lineTo(...z);});ctx.stroke();
    }
    ctx.strokeStyle=s==='pde'?'#c66434':'#007f86';ctx.lineWidth=2.8;ctx.beginPath();points.forEach(([x,y],i)=>{const z=xy(x/scale,y/scale);if(i===0)ctx.moveTo(...z);else ctx.lineTo(...z);});ctx.stroke();ctx.restore();
    ctx.fillStyle='#153342';ctx.textAlign='center';ctx.fillText('r / spatial scale',margin.left+pw/2,height-8);
    ctx.save();ctx.translate(12,margin.top+ph/2);ctx.rotate(-Math.PI/2);ctx.fillText('Q / spatial scale',0,0);ctx.restore();ctx.textAlign='left';
    const audit=data.audit;
    status.textContent=isPde
      ? `Forward experiment, 0 ≤ t ≤ 0.5, ε = 0.01, K = 0.2. Initial curve shown faintly. Smooth axis; fixed boundary at r = 5. Observed grid difference ${audit.grid_240_480_max_error_all_times.toExponential(2)} (240 versus 480 intervals). Inner view divides by the computed axis radius b(t). No singular-trace convergence or type-II rate is certified.`
      : `Asymptotic model: b = 0.7 |t|^β, β = ${beta.toFixed(5)}. Original, parabolic, and inner scales divide lengths by 1, √|t|, and b. The ODE leaf is minimal; its changing dilations are not MCF. ${s==='compact'?'Only the local profile is shown; the compact cap is omitted. ':''}${s==='low'?'Guo–Šešum: n ≥ 5, k = 2; |H| blows up.':'The bounded-H theorem concerns the constructed flow, not this leading minimal model.'}`;
    Object.assign(canvas.dataset,{scenario:s,time:String(t),axis:String(b),scale:view.value,zoom:String(zoom),frame:String(frame??-1)});
  }
  function stop(){playing=false;play.textContent='Play';cancelAnimationFrame(raf);}
  function tick(now){if(!playing)return;if(now-last>90){let value=Number(slider.value)+1;if(value>100){stop();return;}slider.value=value;draw();last=now;}raf=requestAnimationFrame(tick);}
  play.addEventListener('click',()=>{if(playing){stop();return;}if(Number(slider.value)>=100)slider.value=0;playing=true;play.textContent='Pause';last=0;raf=requestAnimationFrame(tick);});
  slider.addEventListener('input',()=>{stop();draw();});
  scenario.addEventListener('change',()=>{stop();zoom=1;draw();});view.addEventListener('change',draw);
  zin.addEventListener('click',()=>{zoom=Math.min(8,zoom*1.25);draw();});zout.addEventListener('click',()=>{zoom=Math.max(.25,zoom/1.25);draw();});
  reset.addEventListener('click',()=>{stop();zoom=1;slider.value=35;view.value='physical';draw();});
  canvas.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','+','-','='].includes(e.key)){e.preventDefault();stop();if(e.key==='ArrowLeft')slider.value=Math.max(0,Number(slider.value)-3);else if(e.key==='ArrowRight')slider.value=Math.min(100,Number(slider.value)+3);else zoom=Math.max(.25,Math.min(8,zoom*(e.key==='-'?.8:1.25)));draw();}});
  new ResizeObserver(draw).observe(canvas);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  draw();
}
