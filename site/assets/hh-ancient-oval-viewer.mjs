// Finite-seed numerical MCF. Frames are computed offline, not ellipsoid morphs.
export function frameProfile(frame, scale='rescaled') {
  if (!['rescaled','physical'].includes(scale)) throw new Error('Unknown spatial scale');
  const factor=scale==='physical'?Math.sqrt(-frame.time):1;
  return frame.profile.map(([x,r])=>[x*factor,r*factor]);
}
export function surfaceVertices(profile,segments=40) {
  const vertices=[[profile[0][0],0,0]];
  for(const [x,r] of profile.slice(1,-1)) for(let j=0;j<segments;j++) {
    const a=2*Math.PI*j/segments;vertices.push([x,r*Math.cos(a),r*Math.sin(a)]);
  }
  vertices.push([profile.at(-1)[0],0,0]);return vertices;
}
export function timeLabel(t){return Number(t.toPrecision(3)).toString().replace('-','−');}

export function initHHAncientOvalFigure(figure,data,rotatePoint) {
  const canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d');
  if(!ctx)throw new Error('Canvas unavailable');
  figure.classList.add('hh-flow');
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  const help=figure.querySelector('.soliton-help'),status=figure.querySelector('.soliton-status');
  let index=data.default_frame,scaleMode='rescaled',view='surface',wire=false,drag=null;
  const camera=()=>({yaw:.20,pitch:.27,zoom:1});let state=camera();
  let vertices=[],profile=[],pending=false,playing=false,lastStep=0,animation=0;
  const label=document.createElement('p');label.className='hh-view-label';stage.append(label);
  const tools=document.createElement('div');tools.className='hh-time-controls';
  const play=document.createElement('button');play.type='button';play.textContent='Play toward extinction';play.setAttribute('aria-pressed','false');
  const time=document.createElement('label'),output=document.createElement('output'),slider=document.createElement('input');
  slider.type='range';slider.min='0';slider.max=String(data.frames.length-1);slider.step='1';slider.value=String(index);slider.setAttribute('aria-label','Ancient oval time (logarithmic steps)');
  time.append(output,slider);tools.append(play,time);controls.prepend(tools);
  function select(text,values,change){
    const label=document.createElement('label');label.append(text+' ');const input=document.createElement('select');input.setAttribute('aria-label',text);
    for(const [value,title] of values){const o=document.createElement('option');o.value=value;o.textContent=title;input.append(o);}
    input.addEventListener('change',()=>change(input.value));label.append(input);controls.append(label);return input;
  }
  const scaleSelect=select('Spatial scale',[['rescaled','Divide by √(−t)'],['physical','Original size']],value=>{scaleMode=value;state.zoom=1;update();});
  const viewSelect=select('View',[['surface','3D surface'],['profile','Meridian + limit guides'],['tip','Right tip + bowl limit']],value=>{view=value;drag=null;scaleSelect.disabled=view==='tip';update();});
  const strip=document.createElement('div');strip.className='hh-snapshots';
  const stripTitle=document.createElement('p');stripTitle.className='hh-strip-title';stripTitle.textContent='Compare rescaled shapes · equal spatial scale · select a time';
  controls.before(stripTitle,strip);
  const buttons=[];
  for(const i of data.snapshots){
    const f=data.frames[i],button=document.createElement('button');button.type='button';
    button.setAttribute('aria-label',`Show time ${f.time.toPrecision(3)}`);
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 220 92');svg.setAttribute('aria-hidden','true');
    const path=document.createElementNS(svg.namespaceURI,'path');
    const points=f.profile.concat([...f.profile].reverse().map(([x,r])=>[x,-r]));
    path.setAttribute('d',points.map(([x,r],j)=>`${j?'L':'M'}${110+x*18},${46-r*18}`).join(' ')+'Z');
    path.setAttribute('fill','#d3e7ee');path.setAttribute('stroke','#21667f');path.setAttribute('stroke-width','1.6');svg.append(path);
    const text=document.createElement('span');text.textContent=`t = ${timeLabel(f.time)}`;button.append(svg,text);
    button.addEventListener('click',()=>{stop();index=i;update();});strip.append(button);buttons.push([button,i]);
  }
  function bounds(){
    const first=frameProfile(data.frames[0],scaleMode);
    return {x:first[0][0],r:Math.max(...first.map(p=>p[1]),scaleMode==='rescaled'?2:0)};
  }
  function update(){
    const frame=data.frames[index];profile=frameProfile(frame,scaleMode);vertices=surfaceVertices(profile,data.segments);
    slider.value=String(index);output.textContent=`t = ${timeLabel(frame.time)} · length / width ≈ ${frame.aspect.toFixed(2)}`;
    slider.setAttribute('aria-valuetext',`Time ${frame.time.toPrecision(3)}, length to width ratio ${frame.aspect.toFixed(2)}`);
    label.textContent=scaleMode==='rescaled'?'Rescaled by 1 / √(−t) · fixed spatial scale':'Original size · fixed spatial scale · extinction at t = 0';
    help.textContent=view==='surface'?'Drag or use arrow keys to rotate; + / − zoom. Time advances in logarithmic steps. Original size shows the collapse; rescaling reveals the shape.':'Meridian rotated about the horizontal axis. In rescaled units: dashed gold lines mark the cylindrical radius √2; the dotted circle has radius 2 (the extinction limit).';
    if(view==='tip'){label.textContent='Right tip at the origin · lengths multiplied by tip mean curvature';help.textContent='Blue: numerical oval tip. Gold dashed: numerical unit-speed bowl profile (backward tip limit). This local window uses curvature scale, separate from the whole-surface views; finite-time profiles need not coincide.';}
    if(view==='profile'&&scaleMode==='physical')help.textContent='Meridian in original spatial units. All slices contract to the origin; use zoom to inspect late times. Limit guides are available in the rescaled view.';
    canvas.dataset.time=String(frame.time);canvas.dataset.scale=view==='tip'?'tip':scaleMode;canvas.dataset.view=view;
    canvas.setAttribute('aria-label',`Numerical surface oval at time ${frame.time.toPrecision(3)}; ${view==='tip'?'tip-centered curvature scale':scaleMode==='rescaled'?'divided by square root of minus time':'original spatial scale'}. ${view==='surface'?'Drag or arrow keys rotate.':'Meridian profile.'} Plus and minus zoom.`);
    buttons.forEach(([b,i])=>b.setAttribute('aria-pressed',String(i===index)));
    requestDraw();
  }
  function draw(){
    pending=false;const {width,height}=stage.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2);
    if(canvas.width!==Math.round(width*dpr)||canvas.height!==Math.round(height*dpr)){canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);}
    ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,width,height);
    const limit=bounds(),factor=(view==='tip'?Math.min(width*.75/5,height*.36/3):Math.min(width*.44/limit.x,height*.34/limit.r))*state.zoom;
    const screen=([x,y])=>[(view==='tip'?width*.76:width/2)+factor*x,height*.53-factor*y];
    const stroke=(points,color,dash=[],lineWidth=1.4)=>{
      ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...screen(p)):ctx.moveTo(...screen(p)));ctx.strokeStyle=color;ctx.setLineDash(dash);ctx.lineWidth=lineWidth;ctx.stroke();ctx.setLineDash([]);
    };
    if(view==='tip'){
      stroke([[-5,0],[.5,0]],'#a8bdc7',[3,4],1);
      const f=data.frames[index],a=f.profile[0][0],H=f.tip_curvature_rescaled;
      for(const sign of [-1,1]){
        stroke(data.bowl_profile.map(([x,r])=>[x,sign*r]),'#a66b27',[7,5],2);
        stroke(f.profile.slice(0,(f.profile.length+1)/2).map(([x,r])=>[(x-a)*H,sign*r*H]),'#21667f',[],2.8);
      }
    }else if(view==='profile'){
      stroke([[-limit.x*1.08,0],[limit.x*1.08,0]],'#a8bdc7',[3,4],1);
      if(scaleMode==='rescaled'){
        for(const sign of [-1,1])stroke([[-limit.x,sign*Math.SQRT2],[limit.x,sign*Math.SQRT2]],'#a66b27',[7,5]);
        stroke(Array.from({length:181},(_,i)=>[2*Math.cos(i*Math.PI/90),2*Math.sin(i*Math.PI/90)]),'#8c7a9b',[2,4]);
      }
      for(const sign of [-1,1])stroke(profile.map(([x,r])=>[x,sign*r]),'#21667f',[],2.8);
    }else{
      const q=vertices.map(p=>rotatePoint(p,state)),xy=q.map(screen);
      const faces=data.faces.map(face=>({face,depth:face.reduce((v,i)=>v+q[i][2],0)/3})).sort((a,b)=>a.depth-b.depth);
      for(const {face} of faces){
        const [a,b,c]=face.map(i=>q[i]),u=b.map((v,i)=>v-a[i]),v=c.map((n,i)=>n-a[i]);
        let n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]],norm=Math.hypot(...n)||1;
        if(n[2]<0)n=n.map(x=>-x);
        const light=.42+.57*Math.max(0,(-.25*n[0]+.55*n[1]+.79*n[2])/norm);
        ctx.fillStyle=`rgb(${[66,143,167].map(x=>Math.round(x*light)).join(',')})`;
        ctx.beginPath();face.forEach((i,j)=>j?ctx.lineTo(...xy[i]):ctx.moveTo(...xy[i]));ctx.closePath();ctx.fill();
        ctx.strokeStyle=wire?'#183f5255':ctx.fillStyle;ctx.lineWidth=wire?.5:.35;ctx.stroke();
      }
    }
    // A ruler preserves the meaning of fixed scale after camera zoom.
    const units=view==='tip'||scaleMode==='rescaled'?1:50,px=units*factor;
    if(px<width*.65){ctx.strokeStyle='#69828e';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(18,height-27);ctx.lineTo(18+px,height-27);ctx.stroke();ctx.fillStyle='#476170';ctx.font='12px sans-serif';ctx.fillText(`${units} ${view==='tip'?'curvature ':scaleMode==='rescaled'?'rescaled ':''}unit${units===1?'':'s'}`,18,height-10);}
    canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;canvas.dataset.zoom=state.zoom.toFixed(3);
  }
  function requestDraw(){if(!pending){pending=true;requestAnimationFrame(draw);}}
  function zoom(f){state.zoom=Math.max(.4,Math.min(128,state.zoom*f));requestDraw();}
  function stop(){playing=false;cancelAnimationFrame(animation);play.textContent='Play toward extinction';play.setAttribute('aria-pressed','false');}
  function tick(timestamp){
    if(!playing)return;
    if(timestamp-lastStep>100){lastStep=timestamp;index++;update();if(index===data.frames.length-1){stop();return;}}
    animation=requestAnimationFrame(tick);
  }
  play.addEventListener('click',()=>{if(playing){stop();return;}if(index===data.frames.length-1){index=0;update();}playing=true;lastStep=performance.now();play.textContent='Pause';play.setAttribute('aria-pressed','true');animation=requestAnimationFrame(tick);});
  slider.addEventListener('input',()=>{stop();index=Number(slider.value);update();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  canvas.addEventListener('pointerdown',e=>{if(view!=='surface')return;drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;state.yaw+=(e.clientX-drag[0])*.009;state.pitch+=(e.clientY-drag[1])*.009;drag=[e.clientX,e.clientY];requestDraw();});
  for(const event of ['pointerup','pointercancel'])canvas.addEventListener(event,()=>drag=null);
  canvas.addEventListener('wheel',e=>{if(document.activeElement!==canvas)return;e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  canvas.addEventListener('keydown',e=>{
    const actions={ArrowLeft:()=>state.yaw-=.12,ArrowRight:()=>state.yaw+=.12,ArrowUp:()=>state.pitch-=.12,ArrowDown:()=>state.pitch+=.12,'+':()=>zoom(1.2),'=':()=>zoom(1.2),'-':()=>zoom(1/1.2)};
    if(actions[e.key]&&!(view!=='surface'&&e.key.startsWith('Arrow'))){e.preventDefault();actions[e.key]();requestDraw();}
  });
  for(const button of controls.querySelectorAll('[data-view-action]'))button.addEventListener('click',()=>{
    const action=button.dataset.viewAction;
    if(action==='in')zoom(1.4);if(action==='out')zoom(1/1.4);
    if(action==='wire'){wire=!wire;button.setAttribute('aria-pressed',String(wire));requestDraw();}
    if(action==='reset'){stop();state=camera();index=data.default_frame;scaleMode='rescaled';view='surface';wire=false;controls.querySelector('[data-view-action=wire]').setAttribute('aria-pressed','false');scaleSelect.value=scaleMode;scaleSelect.disabled=false;viewSelect.value=view;update();}
  });
  status.textContent='Numerical PDE evolution of one finite convex seed. Grid and seed-length comparisons are recorded; no certified error to the ancient solution is claimed. The time slider ends before extinction.';
  controls.hidden=false;help.hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;
  new ResizeObserver(requestDraw).observe(stage);update();
}
