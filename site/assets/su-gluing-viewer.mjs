// Original coordinate-slice viewer. The matching region is schematic.
export function translateSuPoint(point, time) {
  return [point[0],point[1],point[2]+time,point[3]];
}

export function projectSuPoint(point, time, beta, intersection) {
  const p=translateSuPoint(point,time);
  return [p[0]*Math.cos(beta)+p[1]*Math.sin(beta),p[3]-intersection[1],p[2]-intersection[0]];
}

export function initSuGluingFigure(figure,data,rotatePoint) {
  const canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d');
  if(!ctx)return;
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  const status=figure.querySelector('.soliton-status'),help=figure.querySelector('.soliton-help');
  figure.classList.add('su-gluing-figure');
  const defaults=()=>({yaw:data.view.yaw,pitch:data.view.pitch,zoom:1,beta:Math.PI/6,time:0,view:'profile',wire:false,inputs:false,cutaway:true});
  let state=defaults(),dragging=null,scheduled=false,playing=false,last=0,frame=0;
  const label=document.createElement('p');label.className='su-view-label';stage.append(label);
  const viewLabel=document.createElement('label');viewLabel.textContent='View ';
  const view=document.createElement('select');view.setAttribute('aria-label','Su construction view');
  for(const [value,title] of [['slice','Projected slice'],['profile','Flow profile']]){
    const o=document.createElement('option');o.value=value;o.textContent=title;view.append(o);
  }
  viewLabel.append(view);controls.prepend(viewLabel);
  const timeRow=document.createElement('div');timeRow.className='su-time-controls';
  const play=document.createElement('button');play.type='button';play.textContent='Play flow';play.setAttribute('aria-pressed','false');
  const timeLabel=document.createElement('label');timeLabel.textContent='Time t ';
  const slider=document.createElement('input');slider.type='range';slider.min='-1';slider.max='1';slider.step='.01';slider.value='0';slider.setAttribute('aria-label','Flow time');
  const output=document.createElement('output');output.textContent='0.00';timeLabel.append(slider,output);timeRow.append(play,timeLabel);
  for(const t of [-1,0,1]){
    const button=document.createElement('button');button.type='button';button.textContent=`t = ${t}`;
    button.addEventListener('click',()=>{pause();state.time=t;sync();});timeRow.append(button);
  }
  controls.append(timeRow);
  const projectionLabel=document.createElement('label');projectionLabel.textContent='Projection angle ';
  const projection=document.createElement('input');projection.type='range';projection.min='-90';projection.max='90';projection.step='1';projection.value='30';projection.setAttribute('aria-label','Projection angle in the z1 plane');
  const angleOutput=document.createElement('output');projectionLabel.append(projection,angleOutput);controls.append(projectionLabel);
  const cutLabel=document.createElement('label'),cut=document.createElement('input');cut.type='checkbox';cut.checked=true;cut.setAttribute('aria-label','Show half of the model slice');cutLabel.append(cut,'Half slice');controls.append(cutLabel);
  const inputLabel=document.createElement('label');
  const inputs=document.createElement('input');inputs.type='checkbox';inputs.setAttribute('aria-label','Show exact input profiles');inputLabel.append(inputs,'Show exact input profiles');controls.append(inputLabel);
  const detail=document.createElement('button');detail.type='button';detail.textContent='Inspect neck';controls.append(detail);
  const legend=document.createElement('p');legend.className='su-legend';
  for(const [name,color] of [['First cylinder','#36759d'],['Neck + matching','#cc7337'],['Second cylinder','#32978b']]){
    const item=document.createElement('span'),dot=document.createElement('i');dot.style.background=color;item.append(dot,name);legend.append(item);
  }
  controls.after(legend);
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function pause(){playing=false;cancelAnimationFrame(frame);play.textContent='Play flow';play.setAttribute('aria-pressed','false');last=0;}
  function tick(now){
    if(!playing)return;
    if(last)state.time=Math.min(1,state.time+(now-last)/4500);
    last=now;sync();
    if(state.time>=1)pause();else frame=requestAnimationFrame(tick);
  }
  function sync(){
    slider.value=String(state.time);output.textContent=state.time.toFixed(2);view.value=state.view;
    projection.value=String(Math.round(state.beta*180/Math.PI));angleOutput.textContent=`${projection.value}°`;
    projectionLabel.hidden=state.view!=='slice';cutLabel.hidden=state.view!=='slice';cut.checked=state.cutaway;inputLabel.hidden=state.view!=='profile';inputs.checked=state.inputs;
    figure.querySelector('[data-view-action="wire"]').hidden=state.view!=='slice';
    figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed',String(state.wire));
    label.textContent=state.view==='slice'?`C³ model · ${state.cutaway?'half of the ':''}z₂ = 0 slice · projection to ℝ³`:'C³ model · selected meridians in the z₃-plane';
    help.textContent=state.view==='slice'?'Drag or use arrow keys to rotate. Half slice removes ω₁ > 0 to reveal the neck; its straight edges are artificial cuts. Projection angle changes which z₁ coordinate is omitted.':'Blue and teal are the two grim inputs; copper is the neck and illustrative matching. The two curves are selected meridians, not a count of ends.';
    status.textContent='Lε,t = Lε + t e₃ for all real t. The displayed window is −1 ≤ t ≤ 1, at fixed scale and fixed ε = 0.22. The geometry is a construction model; Su’s final nonlinear correction is not computed. Projection crossings and display cuts do not describe the topology of the full embedded translator.';
    canvas.setAttribute('aria-label',`${state.view==='slice'?'Projected two-dimensional slice':'Selected meridians'} of a Su gluing model in C3. Time ${state.time.toFixed(2)}; fixed neck scale. Schematic matching, not a numerical translator. Arrow keys rotate the slice; plus and minus zoom.`);
    requestDraw();
  }
  function draw(){
    scheduled=false;
    const box=stage.getBoundingClientRect(),w=box.width,h=box.height,dpr=Math.min(window.devicePixelRatio||1,2);
    if(!w||!h)return;
    if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);}
    ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle='#f7fafb';ctx.fillRect(0,0,w,h);
    const profile=state.view==='profile';
    const scale=(profile?Math.min((w-70)/4.5,(h-85)/6.2):Math.min(w/8.5,(h-90)/6.5))*state.zoom;
    const toWorld=p=>profile?[p[3]-data.intersection[1],p[2]+state.time,0]:rotatePoint(projectSuPoint(p,state.time,state.beta,data.intersection),state);
    // A fixed camera: never recenter or refit as time changes.
    const screen=p=>[w/2+scale*p[0],h*.59-scale*(p[1]-(profile?.7:.2))];
    const stroke=(points,color,width=1,dash=[])=>{
      ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.stroke();ctx.setLineDash([]);
    };
    ctx.font='12px sans-serif';ctx.fillStyle='#526b78';
    if(profile){
      for(let height=-2;height<=5;height++){
        stroke([screen([-2.3,height]),screen([2.3,height])],'#dce6ea');
        ctx.fillText(String(height),12,screen([0,height])[1]+4);
      }
      for(let y=0;y<=4;y++){
        const x=y-data.intersection[1];stroke([screen([x,-2]),screen([x,5])],'#dce6ea');
        ctx.fillText(String(y),screen([x,0])[0]-4,h-22);
      }
      ctx.fillText('Re z₃ ↑',12,57);ctx.fillText('Im z₃ →',w-75,h-22);
      if(state.inputs)for(const path of data.inputs)stroke(path.map(p=>screen(toWorld(p))),'#879ba5',1.5,[5,5]);
      ctx.lineCap='round';
      for(const curve of data.profiles)for(let i=0;i<curve.vertices.length-1;i++){
        stroke([screen(toWorld(curve.vertices[i])),screen(toWorld(curve.vertices[i+1]))],`rgb(${curve.colors[i]})`,3);
      }
      ctx.lineCap='butt';
    }else{
      const points=data.vertices.map(toWorld),pixels=points.map(screen);
      // Grid belongs to the ambient frame, not to the moving surface.
      for(let i=-3;i<=3;i++){
        stroke([screen(rotatePoint([i,-3,-1.2],state)),screen(rotatePoint([i,3,-1.2],state))],'#dce6ea');
        stroke([screen(rotatePoint([-3,i,-1.2],state)),screen(rotatePoint([3,i,-1.2],state))],'#dce6ea');
      }
      const faces=data.faces.filter(f=>!state.cutaway||f.every(i=>data.vertices[i][0]<1e-8)).map((f,i)=>({f,i,z:points[f[0]][2]+points[f[1]][2]+points[f[2]][2]})).sort((a,b)=>a.z-b.z);
      for(const {f} of faces){
        const [a,b,c]=f.map(i=>points[i]),u=b.map((v,i)=>v-a[i]),v=c.map((v,i)=>v-a[i]);
        const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
        const light=.48+.5*Math.abs(.3*n[0]+.5*n[1]+.8*n[2])/(Math.hypot(...n)||1);
        const color=data.vertexColors[f[0]].map(c=>Math.min(255,Math.round(c*light+20)));
        ctx.beginPath();f.forEach((i,j)=>j?ctx.lineTo(...pixels[i]):ctx.moveTo(...pixels[i]));ctx.closePath();
        ctx.fillStyle=`rgb(${color})`;ctx.fill();ctx.strokeStyle=state.wire?'#183f5260':ctx.fillStyle;ctx.lineWidth=state.wire?.5:.35;ctx.stroke();
      }
      const a=screen(rotatePoint([3,2,-.6],state)),b=screen(rotatePoint([3,2,.9],state));
      stroke([a,b],'#183f52',2);
      const angle=Math.atan2(b[1]-a[1],b[0]-a[0]);
      stroke([[b[0]-9*Math.cos(angle-.4),b[1]-9*Math.sin(angle-.4)],b,[b[0]-9*Math.cos(angle+.4),b[1]-9*Math.sin(angle+.4)]],'#183f52',2);
      ctx.fillStyle='#183f52';ctx.fillText('+Re z₃',b[0]-25,b[1]-12);
    }
    ctx.fillStyle='#f7fafb';ctx.fillRect(0,0,w,45);
    ctx.fillStyle='#183f52';ctx.font='14px sans-serif';ctx.fillText(`t = ${state.time.toFixed(2)}   ·   ε fixed`,14,h-7);
    canvas.dataset.time=state.time.toFixed(2);canvas.dataset.view=state.view;canvas.dataset.zoom=state.zoom.toFixed(3);
    canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;canvas.dataset.projection=state.beta.toFixed(3);
    canvas.dataset.epsilon=String(data.epsilon);canvas.dataset.mesh=String(state.wire);
    canvas.dataset.cutaway=String(state.cutaway);
  }
  slider.addEventListener('input',()=>{pause();state.time=Number(slider.value);sync();});
  play.addEventListener('click',()=>{if(playing){pause();return;}if(state.time>=1)state.time=-1;playing=true;play.textContent='Pause flow';play.setAttribute('aria-pressed','true');last=0;frame=requestAnimationFrame(tick);});
  view.addEventListener('change',()=>{state.view=view.value;state.zoom=1;sync();});
  projection.addEventListener('input',()=>{state.beta=Number(projection.value)*Math.PI/180;sync();});
  inputs.addEventListener('change',()=>{state.inputs=inputs.checked;requestDraw();});
  cut.addEventListener('change',()=>{state.cutaway=cut.checked;sync();});
  detail.addEventListener('click',()=>{pause();state.time=0;state.view='profile';state.zoom=2.5;sync();});
  function zoom(f){state.zoom=Math.max(.5,Math.min(4,state.zoom*f));requestDraw();}
  for(const b of figure.querySelectorAll('[data-view-action]'))b.addEventListener('click',()=>{
    const action=b.dataset.viewAction;
    if(action==='in')zoom(1.2);if(action==='out')zoom(1/1.2);
    if(action==='wire'){state.wire=!state.wire;sync();}
    if(action==='reset'){pause();state=defaults();dragging=null;sync();}
  });
  canvas.addEventListener('pointerdown',e=>{if(state.view!=='slice')return;dragging={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!dragging)return;state.yaw+=(e.clientX-dragging.x)*.009;state.pitch+=(e.clientY-dragging.y)*.009;dragging={x:e.clientX,y:e.clientY};requestDraw();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>{dragging=null;});
  canvas.addEventListener('keydown',e=>{
    const keys={'+':()=>zoom(1.2),'=':()=>zoom(1.2),'-':()=>zoom(1/1.2)};
    if(state.view==='slice')Object.assign(keys,{ArrowLeft:()=>state.yaw-=.12,ArrowRight:()=>state.yaw+=.12,ArrowUp:()=>state.pitch-=.12,ArrowDown:()=>state.pitch+=.12});
    if(keys[e.key]){e.preventDefault();keys[e.key]();requestDraw();}
  });
  canvas.addEventListener('wheel',e=>{if(document.activeElement!==canvas)return;e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
  if('IntersectionObserver' in window)new IntersectionObserver(entries=>{if(!entries[0].isIntersecting)pause();}).observe(figure);
  sync();controls.hidden=false;help.hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;
  new ResizeObserver(requestDraw).observe(stage);
}
