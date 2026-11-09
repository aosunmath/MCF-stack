// Similarity motion is exact; sampled spatial profiles retain their stated numerical status.
export function motion(variant, kind, clock, model='') {
  if(kind==='stationary') return {scale:1,angle:0,z:0,time:clock};
  if(kind==='translator') return {scale:1,angle:0,z:-variant.h*clock,time:clock};
  const {A,B}=variant;
  if(B===0) return {scale:1,angle:A*clock,z:0,time:clock};
  const q=Math.sign(B)*clock;
  return {scale:Math.exp(q/2),angle:A*q/(2*B),z:0,time:model==='halldorsson-dense'?-Math.exp(q):Math.expm1(q)/(2*B)};
}
export function transform(point, m) {
  const c=Math.cos(m.angle),s=Math.sin(m.angle);
  return [m.scale*(c*point[0]-s*point[1]),m.scale*(s*point[0]+c*point[1]),m.scale*point[2]+m.z];
}

if(typeof document!=='undefined') {
 const main=document.querySelector('main[data-model]');
 if(main) init(main).catch(error=>{document.querySelector('#error').textContent='The interactive figure could not load. The section also includes a static drawing.'; console.error(error);});
}
async function init(main) {
 const model=main.dataset.model;
 const data=JSON.parse(document.querySelector('#geometry').textContent);
 const select=document.querySelector('#profile'),time=document.querySelector('#time'),zoom=document.querySelector('#zoom');
 const output=document.querySelector('#time-value'),play=document.querySelector('#play'),canvas=document.querySelector('canvas'),ctx=canvas.getContext('2d');
 let variant=data.variants[0],yaw=.55,pitch=.38,playing=false,previous=0,drag=null;
 let center,span;
 data.variants.forEach((v,i)=>{const o=document.createElement('option');o.value=String(i);o.textContent=v.name;select.append(o);});
 if(data.variants.length===1)select.disabled=true;
 if(data.motion==='stationary'){time.closest('label').hidden=true;play.hidden=true;output.textContent='Stationary for every t ∈ ℝ';}
 function fit() {
  const low=[Infinity,Infinity,Infinity],high=[-Infinity,-Infinity,-Infinity];
  variant.vertices.forEach(p=>p.forEach((x,i)=>{low[i]=Math.min(low[i],x);high[i]=Math.max(high[i],x);}));
  center=low.map((v,i)=>(v+high[i])/2);
  span=Math.max(...high.map((v,i)=>v-low[i]),.1);
  document.querySelector('#note').textContent=variant.note;
  document.querySelector('#time-label').textContent=data.motion==='similarity'&&variant.B!==0?'Logarithmic time':'Time';
 }
 function draw() {
  const width=canvas.clientWidth,height=canvas.clientHeight,dpr=Math.min(devicePixelRatio||1,1.5);
  if(canvas.width!==Math.round(width*dpr)||canvas.height!==Math.round(height*dpr)){canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);}
  ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle='#f5f9fa';ctx.fillRect(0,0,width,height);
  const m=motion(variant,data.motion,Number(time.value),model);
  if(data.motion!=='stationary')output.textContent=`t = ${m.time.toFixed(3)}${data.motion==='similarity'&&variant.B<0&&model!=='halldorsson-dense'?` < T = ${(-1/(2*variant.B)).toFixed(3)}`:''}`;
  const scale=.76*Math.min(width,height)/span*Number(zoom.value);
  function project(p) {
   let [x,y,z]=p.map((v,i)=>v-center[i]);
   if(data.dimension===2)return [width/2+x*scale,height/2-y*scale,0];
   const a=x*Math.cos(yaw)-y*Math.sin(yaw),b=x*Math.sin(yaw)+y*Math.cos(yaw);
   return [width/2+a*scale,height/2-(z*Math.cos(pitch)-b*Math.sin(pitch))*scale,b*Math.cos(pitch)+z*Math.sin(pitch)];
  }
  const points=variant.vertices.map(p=>project(transform(p,m)));
  if(data.dimension===3){
   const faces=variant.faces.map(f=>({f,z:(points[f[0]][2]+points[f[1]][2]+points[f[2]][2])/3})).sort((a,b)=>a.z-b.z);
   ctx.lineWidth=.3;
   for(const {f} of faces){
    const [a,b,c]=f.map(i=>points[i]);
    const signed=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
    ctx.fillStyle=signed>0?'#a8ccd5':'#5796ad';ctx.strokeStyle='#4b8296';
    ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.lineTo(c[0],c[1]);ctx.closePath();ctx.fill();ctx.stroke();
   }
  }
  ctx.strokeStyle='#185e7c';ctx.lineWidth=data.dimension===2?1.8:1;
  for(const path of variant.paths){ctx.beginPath();path.forEach((i,j)=>{const p=points[i];if(j===0)ctx.moveTo(p[0],p[1]);else ctx.lineTo(p[0],p[1]);});ctx.stroke();}
  if(variant.circle){
   const o=project([0,0,0]);ctx.strokeStyle='#b36a36';ctx.setLineDash([6,5]);ctx.beginPath();ctx.arc(o[0],o[1],variant.circle*m.scale*scale,0,2*Math.PI);ctx.stroke();ctx.setLineDash([]);
  }
  // A world-length scale bar remains valid under zoom and time changes.
  const unit=Math.pow(10,Math.floor(Math.log10(span/(6*Number(zoom.value)))));
  ctx.fillStyle='rgba(245,249,250,.94)';ctx.fillRect(12,height-60,150,47);
  ctx.fillStyle='#314f5b';ctx.strokeStyle='#314f5b';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(22,height-28);ctx.lineTo(22+unit*scale,height-28);ctx.stroke();ctx.font='13px system-ui';ctx.fillText(`${unit.toPrecision(1)} spatial units`,22,height-40);
 }
 function stop(){playing=false;play.textContent='Play';}
 select.addEventListener('change',()=>{variant=data.variants[Number(select.value)];time.value='0';zoom.value='1';stop();fit();draw();});
 for(const input of [time,zoom])input.addEventListener('input',draw);
 document.querySelector('#reset').addEventListener('click',()=>{time.value='0';zoom.value='1';yaw=.55;pitch=.38;stop();draw();});
 play.addEventListener('click',()=>{playing=!playing;play.textContent=playing?'Pause':'Play';if(playing){previous=0;requestAnimationFrame(frame);}});
 function frame(now){if(!playing)return;if(previous&&now-previous<45){requestAnimationFrame(frame);return;}const dt=previous?(now-previous)/1000:0;previous=now;let v=Number(time.value)+dt*.3;if(v>Number(time.max)){time.value=time.max;stop();}else time.value=String(v);draw();if(playing)requestAnimationFrame(frame);}
 if(data.dimension===3){
  canvas.style.touchAction='none';
  canvas.addEventListener('pointerdown',e=>{drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;yaw+=(e.clientX-drag[0])*.008;pitch=Math.max(-1.5,Math.min(1.5,pitch+(e.clientY-drag[1])*.008));drag=[e.clientX,e.clientY];draw();});
  for(const type of ['pointerup','pointercancel'])canvas.addEventListener(type,()=>{drag=null;});
  canvas.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;e.preventDefault();if(e.key==='ArrowLeft')yaw-=.12;if(e.key==='ArrowRight')yaw+=.12;if(e.key==='ArrowUp')pitch+=.1;if(e.key==='ArrowDown')pitch-=.1;draw();});
 }
 document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
 new ResizeObserver(draw).observe(canvas);fit();draw();main.dataset.ready='true';
}
