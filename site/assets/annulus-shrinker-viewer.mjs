// Numerical initial profile; exact homothetic evolution. No fetch in sandbox.
export function shrinkerScale(time) {
  if (!Number.isFinite(time) || time >= 0) throw new RangeError('A regular slice requires t < 0');
  return Math.sqrt(-time);
}

export function continueExcursion(base, alpha, index, time=-1) {
  const g=shrinkerScale(time), angle=2*Math.PI*alpha*index;
  const c=Math.cos(angle), s=Math.sin(angle);
  return base.map(([x,y])=>[g*(c*x-s*y),g*(s*x+c*y)]);
}

if (typeof document !== 'undefined') {
  const main=document.querySelector('main[data-model="halldorsson-dense"]');
  if(main) {
    try { init(main); }
    catch(error) {document.querySelector('#error').textContent='The interactive figure could not load. See the static drawing on the catalogue page.';console.error(error);}
  }
}

function init(main) {
  const data=JSON.parse(document.querySelector('#geometry').textContent);
  const get=id=>document.getElementById(id);
  const time=get('time'), select=get('profile'), count=get('excursions'), zoom=get('zoom'), guides=get('guides'), play=get('play');
  const frames=[...document.querySelectorAll('[data-time]')];
  let variant=data.variants[0], curves=[], playing=false, previous=null, animation=0;

  function prepare() {
    curves=Array.from({length:Number(count.value)},(_,j)=>continueExcursion(variant.base,variant.alpha,j));
    get('accuracy').textContent=`One-period refinement difference: ${variant.diagnostics.refinement_max.toExponential(1)} spatial units. Twelve-period continuation check: ${variant.diagnostics.continuation_max.toExponential(1)}. These are numerical diagnostics, not rigorous error bounds.`;
  }

  function plot(canvas,t,mini=false) {
    const ctx=canvas.getContext('2d'), width=canvas.clientWidth, height=canvas.clientHeight;
    const dpr=Math.min(globalThis.devicePixelRatio||1,2);
    if(!width||!height)return;
    if(canvas.width!==Math.round(width*dpr)||canvas.height!==Math.round(height*dpr)) {canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);}
    ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle='#f6f9fa';ctx.fillRect(0,0,width,height);
    // This world extent is independent of time and the truncation count.
    // All snapshot canvases also share exactly the same world extent.
    const extent=2.35*variant.r_max, px=(Math.min(width,height)-32)/(2*extent)*(mini?1:Number(zoom.value));
    const g=shrinkerScale(t), cx=width/2,cy=height/2;
    ctx.strokeStyle='#dce6ea';ctx.lineWidth=1;
    ctx.beginPath();ctx.moveTo(12,cy);ctx.lineTo(width-12,cy);ctx.moveTo(cx,12);ctx.lineTo(cx,height-12);ctx.stroke();
    if(!mini) {
      ctx.font='12px system-ui';ctx.fillStyle='#71828b';
      for(const x of [-4,-2,2,4])if(Math.abs(x*px)<width/2-25){ctx.fillText(String(x),cx+x*px-4,cy+16);}
      ctx.fillText('0',cx+5,cy+16);
    }
    if(guides.checked) {
      ctx.strokeStyle='#7b8790';ctx.setLineDash([5,5]);
      for(const radius of [variant.r_min,variant.r_max]) {ctx.beginPath();ctx.arc(cx,cy,radius*g*px,0,2*Math.PI);ctx.stroke();}
      ctx.setLineDash([]);
    }
    function stroke(points,color,lineWidth,opacity=1) {
      ctx.strokeStyle=color;ctx.lineWidth=lineWidth;ctx.globalAlpha=opacity;ctx.lineJoin='round';ctx.beginPath();
      points.forEach(([x,y],i)=>{if(i===0)ctx.moveTo(cx+x*g*px,cy-y*g*px);else ctx.lineTo(cx+x*g*px,cy-y*g*px);});ctx.stroke();ctx.globalAlpha=1;
    }
    for(let i=1;i<curves.length;i++)stroke(curves[i],'#216c83',mini?.8:1.25,curves.length>48?.3:.65);
    stroke(curves[0],'#c45b32',mini?1.8:2.8);
    // Endpoints mark truncation only; no segment joins the last point to the first.
    if(!mini) {
      for(const p of [curves[0][0],curves.at(-1).at(-1)]) {ctx.beginPath();ctx.arc(cx+p[0]*g*px,cy-p[1]*g*px,3,0,2*Math.PI);ctx.fillStyle='#203e4a';ctx.fill();}
      ctx.fillStyle='#506975';ctx.font='12px system-ui';ctx.fillText(`${count.value} excursions · finite segment`,14,23);
      // A fixed world-unit scale bar makes both time changes and zoom explicit.
      ctx.strokeStyle='#506975';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(16,height-19);ctx.lineTo(16+px,height-19);ctx.stroke();ctx.fillText('1 spatial unit',16,height-29);
    }
  }

  function drawMain() {
    const t=Number(time.value),g=shrinkerScale(t);
    get('time-value').textContent=`t = ${t.toFixed(4).replace(/0+$/,'').replace(/\.$/,'')}`;
    get('scale-value').textContent=`Scale √(−t) = ${g.toFixed(3)}`;
    get('parameters').textContent=`α = ${variant.target_expression} ≈ ${variant.alpha.toFixed(6)} · at this time: r_min ≈ ${(variant.r_min*g).toFixed(3)}, r_max ≈ ${(variant.r_max*g).toFixed(3)}`;
    frames.forEach(button=>button.setAttribute('aria-pressed',String(Math.abs(Number(button.dataset.time)-t)<1e-8)));
    get('flow').setAttribute('aria-label',`${count.value} excursions of the numerical annulus-dense curve at time ${t.toFixed(4)}; inner radius ${(variant.r_min*g).toFixed(3)}, outer radius ${(variant.r_max*g).toFixed(3)}; fixed spatial scale`);
    plot(get('flow'),t);
  }
  function drawAll(){drawMain();frames.forEach(button=>plot(button.querySelector('canvas'),Number(button.dataset.time),true));}
  function stop(){playing=false;previous=null;cancelAnimationFrame(animation);play.textContent='Play flow';play.setAttribute('aria-pressed','false');}
  function tick(now) {
    if(!playing)return;
    if(previous!==null)time.value=String(Math.min(Number(time.max),Number(time.value)+Math.min((now-previous)/1000,.1)*.38));
    previous=now;drawMain();
    if(Number(time.value)>=Number(time.max)){stop();return;}
    animation=requestAnimationFrame(tick);
  }
  play.addEventListener('click',()=>{
    if(playing){stop();return;}
    if(Number(time.value)>=Number(time.max))time.value=time.min;
    playing=true;previous=null;play.textContent='Pause';play.setAttribute('aria-pressed','true');animation=requestAnimationFrame(tick);
  });
  time.addEventListener('input',()=>{stop();drawMain();});
  frames.forEach(button=>button.addEventListener('click',()=>{stop();time.value=button.dataset.time;drawMain();}));
  select.addEventListener('change',()=>{stop();variant=data.variants[Number(select.value)];prepare();drawAll();});
  count.addEventListener('change',()=>{prepare();drawAll();});
  guides.addEventListener('change',drawAll);zoom.addEventListener('input',drawMain);
  get('reset').addEventListener('click',()=>{stop();select.value='0';variant=data.variants[0];count.value='12';time.value='-4';zoom.value='1';guides.checked=true;prepare();drawAll();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  const observer=new ResizeObserver(drawAll);observer.observe(get('flow'));frames.forEach(b=>observer.observe(b.querySelector('canvas')));
  prepare();drawAll();main.dataset.ready='true';
}
