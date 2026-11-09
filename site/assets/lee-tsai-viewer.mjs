// Numerical quotient PDE; the 3D surface is an orbit-size diagram, not an embedding.
const COLORS=['#287c91','#ba7244','#796b9c'];
export function orbitRadius(x,u,centers){
  let phi=0;
  for(const a of centers){const r=Math.hypot(x-a,u);if(r<1e-10)return 0;phi+=.5/r;}
  return 1/Math.sqrt(phi);
}
export function flowFrame(data,time){
  if(time===Infinity)return {time,u:data.x.map(()=>0),height:0,neckRadii:[0,0]};
  if(!Number.isFinite(time)||time<0||time>12)throw new RangeError('Numerical times are between 0 and 12; the limit is separate.');
  const i=Math.min(data.frames.length-2,Math.floor(time*10+1e-9)),a=data.frames[i],b=data.frames[i+1];
  const q=(time-a.time)/(b.time-a.time),mix=(v,w)=>v+(w-v)*q;
  return {time,u:a.u.map((v,j)=>mix(v,b.u[j])),height:mix(a.height,b.height),neckRadii:a.neckRadii.map((v,j)=>mix(v,b.neckRadii[j]))};
}
export function projectFiber(x,r,theta,yaw=.1,pitch=.18){
  const y=r*Math.cos(theta),z=r*Math.sin(theta),h=x*Math.cos(yaw)-y*Math.sin(yaw),d=x*Math.sin(yaw)+y*Math.cos(yaw);
  return [h,z*Math.cos(pitch)-d*Math.sin(pitch),z*Math.sin(pitch)+d*Math.cos(pitch)];
}

export function initLeeTsaiFigure(figure,data){
  const canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d');if(!ctx)return;
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls'),status=figure.querySelector('.soliton-status');
  figure.classList.add('lee-tsai-figure');
  let mode='sequence',time=0,limit=false,zoom=1,yaw=.1,pitch=.18,rings=true,drag=null,pending=false,playing=false,last=0,animation;
  const makeButton=(text,fn)=>{const b=document.createElement('button');b.type='button';b.textContent=text;b.addEventListener('click',fn);return b;};
  const modes=document.createElement('div');modes.className='lee-tsai-modes';
  const modeButtons=new Map();
  for(const [key,title] of [['sequence','Compare times'],['single','Explore one time'],['quotient','Quotient curves']]){
    const b=makeButton(title,()=>{stop();mode=key;sync();requestDraw();});modes.append(b);modeButtons.set(key,b);
  }
  const label=document.createElement('label'),output=document.createElement('output'),slider=document.createElement('input');
  slider.type='range';slider.min='0';slider.max='12';slider.step='.1';slider.value='0';slider.setAttribute('aria-label','Numerical flow time');
  label.append(output,slider);
  const play=makeButton('Play flow',()=>{if(playing){stop();return;}mode='single';limit=false;if(time>=12)time=0;playing=true;last=0;status.setAttribute('aria-live','off');sync();animation=requestAnimationFrame(tick);});
  const end=makeButton('Limit t → ∞',()=>{stop();mode='single';limit=true;sync();requestDraw();});
  const presets=document.createElement('div');presets.className='lee-tsai-presets';
  for(const t of [0,3,12])presets.append(makeButton(`t = ${t}`,()=>{stop();mode='single';limit=false;time=t;sync();requestDraw();}));
  presets.append(end);
  controls.prepend(modes,label,play,presets);
  const ringButton=controls.querySelector('[data-view-action=wire]');ringButton.textContent='Circle fibers';
  figure.querySelector('.soliton-help').textContent='Compare fixed-scale snapshots, or choose a finite time. Drag a single fiber diagram to rotate; + / − zoom. The limit is a separate view. Each color marks an interval between centers.';
  canvas.setAttribute('aria-label','Lagrangian sphere approaching a three-sphere chain. Numerical quotient curves and a circle-fiber size diagram; not an embedding of the ambient four-manifold.');
  function stop(){playing=false;cancelAnimationFrame(animation);play.textContent='Play flow';status.setAttribute('aria-live','polite');}
  function tick(now){if(!playing)return;if(last)time=Math.min(12,time+(now-last)/1000);last=now;if(time>=12)stop();sync();requestDraw();if(playing)animation=requestAnimationFrame(tick);}
  function sync(){
    figure.dataset.leeTsaiMode=mode;canvas.dataset.mode=mode;canvas.dataset.time=limit?'infinity':time.toFixed(2);canvas.dataset.zoom=String(zoom);canvas.dataset.rotation=`${yaw},${pitch}`;
    slider.value=String(time);output.textContent=limit?'Limit t → ∞':`t = ${time.toFixed(1)}`;play.textContent=playing?'Pause':'Play flow';
    for(const [key,b] of modeButtons)b.setAttribute('aria-pressed',String(key===mode));
    end.setAttribute('aria-pressed',String(limit&&mode==='single'));ringButton.setAttribute('aria-pressed',String(rings));
    if(mode==='single'){
      const f=flowFrame(data,limit?Infinity:time);
      status.textContent=limit?'Infinite-time limit: three special Lagrangian spheres. The two interior fibers have collapsed; the actual spheres intersect transversely in four dimensions.':`Numerical t = ${time.toFixed(1)}: one smooth sphere. Neck orbit radius ≈ ${f.neckRadii[0].toFixed(4)}; maximum quotient height ≈ ${f.height.toFixed(5)}. Both necks remain positive.`;
    }else status.textContent=mode==='sequence'?'Three finite-time numerical snapshots and a separate theoretical limit. All panels use the same scales; quotient height is magnified ×6.':'The solid curves solve the weighted quotient equation numerically. The dashed baseline is the theoretical infinite-time limit. Vertical scale ×6, fixed throughout.';
    for(const action of ['in','out','wire'])controls.querySelector(`[data-view-action=${action}]`).disabled=mode==='quotient';
    canvas.style.cursor=mode==='single'?'grab':'default';
  }
  function requestDraw(){if(!pending){pending=true;requestAnimationFrame(draw);}}
  function line(points,color,width=1,dash=[]){ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.stroke();ctx.setLineDash([]);}
  function text(s,x,y,size=13,color='#203f50'){ctx.fillStyle=color;ctx.font=`${size}px system-ui`;ctx.fillText(s,x,y);}
  function fiber(frame,box){
    const [left,top,w,h]=box,scale=Math.min(w*.43,h*.72)*zoom,cx=left+w/2,cy=top+h/2;
    const screen=p=>[cx+scale*p[0],cy-scale*p[1]],N=24,faces=[];
    const xs=data.x.filter((_,i)=>i%2===0||i===data.x.length-1),us=frame.u.filter((_,i)=>i%2===0||i===data.x.length-1);
    const vertices=xs.map((x,i)=>Array.from({length:N},(_,j)=>projectFiber(x,orbitRadius(x,us[i],data.centers),j*Math.PI*2/N,yaw,pitch)));
    for(let i=0;i<xs.length-1;i++)for(let j=0;j<N;j++){
      const k=(j+1)%N,points=[vertices[i][j],vertices[i+1][j],vertices[i+1][k],vertices[i][k]];
      const band=Math.min(2,Math.floor(((xs[i]+xs[i+1])/2+1)*1.5));
      faces.push({points,band,depth:points.reduce((v,p)=>v+p[2],0),j});
    }
    ctx.save();ctx.beginPath();ctx.rect(left,top,w,h);ctx.clip();
    for(const f of faces.sort((a,b)=>a.depth-b.depth)){
      const light=.68+.29*Math.abs(Math.sin((f.j+.5)*Math.PI/12+.4));
      const base=COLORS[f.band],rgb=[1,3,5].map(i=>Math.round(parseInt(base.slice(i,i+2),16)*light));
      ctx.fillStyle=`rgb(${rgb.join(',')})`;ctx.strokeStyle=ctx.fillStyle;ctx.lineWidth=.4;
      ctx.beginPath();f.points.forEach((p,i)=>i?ctx.lineTo(...screen(p)):ctx.moveTo(...screen(p)));ctx.closePath();ctx.fill();ctx.stroke();
    }
    if(rings){
      // The full sampled orbits are diagram guides; dashed portions are not hidden-surface geometry.
      for(const i of [25,75,100,125,175,200,225,275]){
        const x=data.x[i],r=orbitRadius(x,frame.u[i],data.centers),neck=i===100||i===200;
        line(Array.from({length:65},(_,j)=>screen(projectFiber(x,r,j*Math.PI/32,yaw,pitch))),neck?'#e3ac52':'#e7f1f3',neck?1.8:.7,neck?[]:[2,3]);
      }
    }
    ctx.restore();
  }
  function quotient(frame,left,top,w,h,labels=true){
    const scale=(w-38)/2,cx=left+w/2,base=top+h-20;
    line([[left+14,base],[left+w-14,base]],'#b0c1ca');
    for(let i=0;i<4;i++){
      const x=cx+scale*data.centers[i];ctx.fillStyle='#203f50';ctx.beginPath();ctx.arc(x,base,3,0,2*Math.PI);ctx.fill();
      if(labels)text(`a${i+1}`,x-7,base+16,11);
    }
    line(data.x.map((x,i)=>[cx+scale*x,base-scale*6*frame.u[i]]),'#287c91',2.3);
  }
  function panel(frame,left,top,w,h){
    ctx.fillStyle='#fff';ctx.strokeStyle='#d7e2e7';ctx.lineWidth=1;ctx.beginPath();ctx.roundRect(left,top,w,h,8);ctx.fill();ctx.stroke();
    const isLimit=frame.time===Infinity;
    text(isLimit?'Limit t → ∞':`t = ${frame.time.toFixed(1)}`,left+14,top+25,17);
    text(isLimit?'Three spheres; two junctions':'One sphere; two positive necks',left+14,top+46,12,'#526b77');
    fiber(frame,[left+8,top+53,w-16,h-126]);
    quotient(frame,left+8,top+h-75,w-16,68);
  }
  function draw(){
    pending=false;const {width:w,height:h}=stage.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2);
    canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
    text('Circle-fiber size diagram · ambient dimension 4',14,23,12,'#526b77');
    if(mode==='sequence'){
      const stacked=w<560,gap=10,pad=10,ph=(h-64-gap*(stacked?3:1))/(stacked?4:2),pw=(w-2*pad-(stacked?0:gap))/(stacked?1:2);
      [0,3,12,Infinity].forEach((t,i)=>panel(flowFrame(data,t),pad+(stacked?0:i%2*(pw+gap)),34+(stacked?i:Math.floor(i/2))*(ph+gap),pw,ph));
      text('Quotient below each diagram: y × 6',14,h-9,11,'#526b77');
    }else if(mode==='single'){
      panel(flowFrame(data,limit?Infinity:time),10,34,w-20,h-64);
      text('Quotient: y × 6. Fiber radius: φ⁻¹ᐟ².',14,h-9,12,'#526b77');
    }else{
      const scale=(w-70)/2,cx=w/2,base=h*.65,colors=['#287c91','#ba7244','#796b9c'];
      for(const y of [0,.02,.04,.06]){
        const sy=base-scale*6*y;line([[35,sy],[w-35,sy]],'#d7e2e7',1,y===0?[4,4]:[]);text(y.toFixed(2),3,sy+4,11);
      }
      [0,3,12].forEach((t,i)=>{const f=flowFrame(data,t);line(data.x.map((x,j)=>[cx+scale*x,base-scale*6*f.u[j]]),colors[i],2.5);text(`t = ${t}`,25+i*(w-50)/3,h-62,14,colors[i]);});
      data.centers.forEach((a,i)=>{const x=cx+scale*a;ctx.fillStyle='#203f50';ctx.beginPath();ctx.arc(x,base,4,0,2*Math.PI);ctx.fill();text(`a${i+1}`,x-7,base+22,12);});
      text('Dashed baseline: limit t → ∞',25,h-30,12,'#526b77');text('Quotient height u; vertical magnification ×6',14,48,12,'#526b77');
    }
  }
  slider.addEventListener('input',()=>{stop();time=Number(slider.value);limit=false;mode='single';sync();requestDraw();});
  function setZoom(v){zoom=Math.max(.65,Math.min(2.6,v));sync();requestDraw();}
  controls.querySelector('[data-view-action=in]').addEventListener('click',()=>setZoom(zoom*1.2));
  controls.querySelector('[data-view-action=out]').addEventListener('click',()=>setZoom(zoom/1.2));
  controls.querySelector('[data-view-action=reset]').addEventListener('click',()=>{stop();mode='sequence';time=0;limit=false;zoom=1;yaw=.1;pitch=.18;rings=true;sync();requestDraw();});
  ringButton.addEventListener('click',()=>{rings=!rings;sync();requestDraw();});
  canvas.addEventListener('pointerdown',e=>{if(mode!=='single')return;drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;yaw+=(e.clientX-drag[0])*.006;pitch+=(e.clientY-drag[1])*.006;drag=[e.clientX,e.clientY];sync();requestDraw();});
  canvas.addEventListener('pointerup',()=>{drag=null;});canvas.addEventListener('pointercancel',()=>{drag=null;});
  canvas.addEventListener('keydown',e=>{
    if(['+','=','-'].includes(e.key)){e.preventDefault();setZoom(zoom*(e.key==='-'?1/1.2:1.2));}
    if(mode==='single'&&['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){e.preventDefault();if(e.key==='ArrowLeft')yaw-=.1;if(e.key==='ArrowRight')yaw+=.1;if(e.key==='ArrowUp')pitch-=.1;if(e.key==='ArrowDown')pitch+=.1;sync();requestDraw();}
  });
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  figure.querySelector('img').hidden=true;canvas.hidden=false;controls.hidden=false;figure.querySelector('.soliton-help').hidden=false;
  new ResizeObserver(requestDraw).observe(stage);sync();requestDraw();
}
