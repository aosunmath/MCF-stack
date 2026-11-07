// Finite-start curve-shortening data; never extrapolate it to eternal time.
export function timeSlice(data,t) {
  const frames=data.frames;
  const time=Math.max(frames[0].t,Math.min(frames.at(-1).t,t));
  let hi=frames.findIndex(f=>f.t>=time);
  if(hi<=0)return frames[0].points;
  if(frames[hi].t===time)return frames[hi].points;
  const a=frames[hi-1],b=frames[hi],w=(time-a.t)/(b.t-a.t);
  return a.points.map((p,i)=>p.map((v,k)=>v+(b.points[i][k]-v)*w));
}

export function grimReaper(k,t,count=500) {
  return Array.from({length:count+1},(_,i)=>{
    // Exponential sampling resolves horizontal tails as well as the tip.
    const q=-15+30*i/count,angle=2*Math.atan(Math.exp(q));
    return [(-1)**k*(-Math.log(Math.sin(angle))+t),(k-1)*Math.PI+angle];
  });
}

export function initReaperFlow(figure,data) {
  const stage=figure.querySelector('.soliton-stage'),canvas=figure.querySelector('canvas');
  const ctx=canvas.getContext('2d'); if(!ctx)return;
  const controls=figure.querySelector('.soliton-controls'),help=figure.querySelector('.soliton-help');
  figure.classList.add('reaper-flow');
  let t=-6,zoom=1,pan=[0,0],models=false,playing=false,previous=0,drag=null;
  controls.replaceChildren();
  const button=(text,fn)=>{const b=document.createElement('button');b.type='button';b.textContent=text;b.addEventListener('click',fn);controls.append(b);return b;};
  const play=button('Play',()=>{playing=!playing;play.textContent=playing?'Pause':'Play';previous=0;if(playing){if(t>=9)t=-6;requestAnimationFrame(tick);}});
  const label=document.createElement('label'),out=document.createElement('output'),slider=document.createElement('input');
  slider.type='range';slider.min='-6';slider.max='9';slider.step='.05';slider.value='-6';slider.setAttribute('aria-label','Curve-shortening time');
  label.append(out,slider);controls.append(label);
  const stop=()=>{playing=false;play.textContent='Play';};
  slider.addEventListener('input',()=>{stop();t=Number(slider.value);draw();});
  const overlay=button('Grim-reaper models',()=>{models=!models;overlay.setAttribute('aria-pressed',String(models));draw();});
  overlay.setAttribute('aria-pressed','false');
  button('Zoom +',()=>{zoom=Math.min(3,zoom*1.2);draw();});
  button('Zoom −',()=>{zoom=Math.max(.6,zoom/1.2);draw();});
  button('Reset',()=>{stop();t=-6;zoom=1;pan=[0,0];models=false;overlay.setAttribute('aria-pressed','false');draw();});
  const strip=document.createElement('div');strip.className='reaper-snapshots';strip.setAttribute('aria-label','Six time snapshots');
  for(const time of [-6,-3,0,3,6,9]){
    const b=document.createElement('button');b.type='button';b.setAttribute('aria-label',`Show curve at time ${time}`);
    const pts=timeSlice(data,time),path=pts.map(([x,y],i)=>`${i?'L':'M'}${((x+12)*10).toFixed(2)},${(100-y*10).toFixed(2)}`).join(' ');
    // All thumbnails have the same 20-by-10 spatial window.
    b.innerHTML=`<span>t = ${time}</span><svg viewBox="0 0 200 110" aria-hidden="true"><path d="M0 100H200 M0 ${100-Math.PI*10}H200 M0 ${100-2*Math.PI*10}H200 M0 ${100-3*Math.PI*10}H200" stroke="#bdccd2" stroke-width=".8" stroke-dasharray="3 3"/><path d="${path}" fill="none" stroke="#176b85" stroke-width="1.8"/></svg>`;
    b.dataset.time=time;b.addEventListener('click',()=>{stop();t=time;draw();});strip.append(b);
  }
  controls.after(strip);
  help.textContent='One connected curve in the plane. Drag to pan; + / − zoom. The six snapshots share a fixed scale. Dashed horizontal lines mark y = 0, π, 2π, 3π; the two outer ends continue left.';
  const note=document.createElement('p');note.className='reaper-model-note';
  note.textContent='Blue: finite-start numerical flow. Orange dashed: exact separate translators, describing the distant past only. Their late-time separation from the blue curve is expected.';
  strip.after(note);
  const stageLabel=document.createElement('p');stageLabel.className='reaper-view-label';stage.append(stageLabel);
  function draw(){
    const {width:w,height:h}=stage.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2);
    canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
    const scale=Math.min((w-74)/20,(h-100)/(3*Math.PI))*zoom;
    const screen=([x,y])=>[w/2+(x+2)*scale+pan[0],h/2-(y-1.5*Math.PI)*scale+pan[1]+7];
    const curve=(points,color,width,dash=[])=>{
      ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...screen(p)):ctx.moveTo(...screen(p)));ctx.stroke();ctx.setLineDash([]);
    };
    ctx.save();ctx.beginPath();ctx.rect(40,43,w-54,h-76);ctx.clip();
    for(let k=0;k<=3;k++)curve([[-80,k*Math.PI],[80,k*Math.PI]],'#acbfc8',1,[4,5]);
    curve([[0,-30],[0,40]],'#d9e1e6',1);
    if(models)for(let k=1;k<=3;k++){
      curve(grimReaper(k,t),'#ba702a',1.5,[6,5]);
      const [x,y]=screen([(-1)**k*t,(k-.5)*Math.PI]);
      const sign=(-1)**k;
      ctx.strokeStyle='#9c571b';ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(x,y-15);ctx.lineTo(x+sign*30,y-15);ctx.lineTo(x+sign*23,y-19);ctx.moveTo(x+sign*30,y-15);ctx.lineTo(x+sign*23,y-11);ctx.stroke();
      ctx.fillStyle='#9c571b';ctx.font='12px system-ui';ctx.fillText(`G${['','₁','₂','₃'][k]}`,x-8,y-24);
    }
    curve(timeSlice(data,t),'#176b85',2.7);
    ctx.restore();ctx.fillStyle='#526b77';ctx.font='12px system-ui';
    for(let k=0;k<=3;k++){
      const y=screen([0,k*Math.PI])[1];if(y>=46&&y<=h-33)ctx.fillText(['0','π','2π','3π'][k],9,y+4);
    }
    for(const x of [-10,-5,0,5]){
      const sx=screen([x,0])[0];if(sx>40&&sx<w-14){ctx.fillText(String(x),sx-5,h-17);}
    }
    ctx.fillText('x',w-21,h-17);ctx.fillText('y',12,48);
    stageLabel.textContent=`t = ${t.toFixed(2)} · finite-start numerical flow`;
    out.textContent=`t = ${t.toFixed(2)}`;slider.value=String(t);canvas.dataset.time=t.toFixed(2);canvas.dataset.models=String(models);
    canvas.setAttribute('aria-label',`Numerical three-reaper curve-shortening flow at time ${t.toFixed(2)}. Two ends extend left. Use the time slider or snapshot buttons to compare times.`);
    strip.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(Math.abs(Number(b.dataset.time)-t)<.05)));
  }
  function tick(now){if(!playing)return;if(previous)t=Math.min(9,t+Math.min((now-previous)/1000,.1)*1.5);previous=now;draw();if(t>=9)stop();else requestAnimationFrame(tick);}
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  canvas.addEventListener('pointerdown',e=>{drag=[e.clientX,e.clientY,...pan];canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(drag){pan=[drag[2]+e.clientX-drag[0],drag[3]+e.clientY-drag[1]];draw();}});
  const endDrag=()=>{drag=null;};canvas.addEventListener('pointerup',endDrag);canvas.addEventListener('pointercancel',endDrag);canvas.addEventListener('lostpointercapture',endDrag);
  canvas.addEventListener('keydown',e=>{
    if(!['+','=','-','ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;e.preventDefault();
    if(e.key==='+'||e.key==='=')zoom=Math.min(3,zoom*1.2);else if(e.key==='-')zoom=Math.max(.6,zoom/1.2);else {const d={ArrowLeft:[-20,0],ArrowRight:[20,0],ArrowUp:[0,-20],ArrowDown:[0,20]}[e.key];pan=pan.map((v,i)=>v+d[i]);}draw();
  });
  figure.querySelector('img').hidden=true;canvas.hidden=false;controls.hidden=false;help.hidden=false;
  new ResizeObserver(draw).observe(stage);draw();
}
