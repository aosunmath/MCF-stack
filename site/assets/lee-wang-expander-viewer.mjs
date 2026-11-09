// Exact Lee–Wang unit-weight expander in C^3. All surfaces drawn here are
// two-dimensional real slices, not hypersurface mean curvature flows in R^3.
export const LW = Object.freeze({radius:3.2, times:[0,.25,1,4], source:'https://arxiv.org/abs/0802.0359v1'});
export function slicePoint(r,theta,t,sign=1) {
  if(!Number.isFinite(t)||t<0||!Number.isFinite(r)||r<0||!Number.isFinite(theta)||![-1,1].includes(sign)) throw new RangeError('Require t ≥ 0, r ≥ 0 and sheet sign ±1.');
  return [r*Math.cos(theta),r*Math.sin(theta),sign*Math.sqrt(r*r+2*t)];
}
// Coordinates ordered (Re z1, Im z1, Re z2, Im z2, Re z3, Im z3).
export function circlePoint(x,s) {
  if(x.length!==3||!x.every(Number.isFinite)||!Number.isFinite(s))throw new RangeError('A real point and finite phase are required.');
  return [x[0]*Math.cos(s),x[0]*Math.sin(s),x[1]*Math.cos(s),x[1]*Math.sin(s),x[2]*Math.cos(s),-x[2]*Math.sin(s)];
}
export function sliceMesh(t,rings=24,sectors=56) {
  const vertices=[],faces=[],groups=[];
  for(const sign of [1,-1]){
    const offset=vertices.length;vertices.push(slicePoint(0,0,t,sign));
    for(let i=1;i<=rings;i++)for(let j=0;j<sectors;j++)vertices.push(slicePoint(LW.radius*i/rings,2*Math.PI*j/sectors,t,sign));
    const idx=(i,j)=>offset+1+(i-1)*sectors+(j%sectors);
    for(let j=0;j<sectors;j++){faces.push([offset,idx(1,j),idx(1,j+1)]);groups.push(sign);}
    for(let i=1;i<rings;i++)for(let j=0;j<sectors;j++){
      faces.push([idx(i,j),idx(i+1,j),idx(i+1,j+1)],[idx(i,j),idx(i+1,j+1),idx(i,j+1)]);groups.push(sign,sign);
    }
  }
  return {vertices,faces,groups};
}
export function rotate(p,yaw=.55,pitch=.25) {
  const a=p[0]*Math.cos(yaw)-p[1]*Math.sin(yaw),b=p[0]*Math.sin(yaw)+p[1]*Math.cos(yaw);
  return [a,p[2]*Math.cos(pitch)-b*Math.sin(pitch),p[2]*Math.sin(pitch)+b*Math.cos(pitch)];
}
export function surfaceScene(t,box,state={yaw:.55,pitch:.25,zoom:1},quality=[24,56]) {
  const mesh=sliceMesh(t,...quality),q=mesh.vertices.map(p=>rotate(p,state.yaw,state.pitch));
  const scale=Math.min(box.w*.42/LW.radius,box.h*.42/4.5)*state.zoom;
  const project=p=>{const q=rotate(p,state.yaw,state.pitch);return [box.x+box.w/2+scale*q[0],box.y+box.h/2-scale*q[1]];};
  const polygons=mesh.faces.map((f,i)=>{
    const [a,b,c]=f.map(j=>q[j]),u=b.map((x,j)=>x-a[j]),v=c.map((x,j)=>x-a[j]);
    const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
    const shade=.54+.42*Math.abs((.25*n[0]-.45*n[1]+.86*n[2])/(Math.hypot(...n)||1));
    const base=mesh.groups[i]>0?[40,129,158]:[191,112,54];
    const color=`rgb(${base.map(v=>Math.round(v*shade+245*(1-shade))).join(',')})`;
    return {points:f.map(j=>project(mesh.vertices[j])),depth:(a[2]+b[2]+c[2])/3,color};
  }).sort((a,b)=>a.depth-b.depth);
  return {polygons,project,scale};
}

export function initLeeWangExpander(figure) {
  const canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d');if(!ctx)return;
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  const status=figure.querySelector('.soliton-status'),help=figure.querySelector('.soliton-help');
  figure.classList.add('lw-expander-figure');
  let t=1,s=0,mode='compare',state={yaw:.55,pitch:.25,zoom:1},mesh=false,cone=true,drag=null,queued=false,animation=null,frame=0,last=0;
  const element=(tag,text)=>{const el=document.createElement(tag);if(text)el.textContent=text;return el;};
  const button=(text,handler)=>{const b=element('button',text);b.type='button';b.addEventListener('click',handler);controls.append(b);return b;};
  const label=element('label','View '),select=element('select');select.setAttribute('aria-label','Lee–Wang view');
  for(const [value,text] of [['compare','Compare times'],['slice','Explore a time'],['orbit','How sheets connect']]){const o=element('option',text);o.value=value;select.append(o);}label.append(select);controls.prepend(label);
  const timeLabel=element('label','Time t '),time=element('input'),timeOut=element('output');
  time.type='range';time.min='.02';time.max='4';time.step='.01';time.value='1';time.setAttribute('aria-label','Lee–Wang expander time');timeLabel.append(time,timeOut);controls.append(timeLabel);
  const presets=element('div');presets.className='lw-time-presets';
  for(const value of LW.times){const b=element('button',value===0?'Cone limit':`t = ${value}`);b.type='button';b.addEventListener('click',()=>{stop();t=value;mode='slice';sync();});presets.append(b);}controls.append(presets);
  const play=button('Play time',()=>{if(animation==='time'){stop();return;}stop();if(t>=4||t===0)t=.02;mode=mode==='orbit'?'orbit':'slice';animation='time';last=0;sync();frame=requestAnimationFrame(tick);});
  const coneButton=button('Cone reference',()=>{cone=!cone;sync();});
  const phaseLabel=element('label','Circle phase s '),phase=element('input'),phaseOut=element('output');
  phase.type='range';phase.min='0';phase.max='1';phase.step='.005';phase.value='0';phase.setAttribute('aria-label','Circle phase, in multiples of pi');phaseLabel.append(phase,phaseOut);controls.append(phaseLabel);
  const trace=button('Trace connection',()=>{if(animation==='orbit'){stop();return;}stop();s=0;animation='orbit';last=0;sync();frame=requestAnimationFrame(tick);});
  const note=element('p');note.className='lw-expander-note';stage.after(note);
  function stop(){cancelAnimationFrame(frame);animation=null;last=0;play.textContent='Play time';trace.textContent='Trace connection';}
  function tick(now){if(!animation)return;const dt=last?Math.min(.05,(now-last)/1000):0;last=now;
    if(animation==='time'){t=Math.min(4,t+dt*.55);if(t===4)stop();}
    else{s=Math.min(Math.PI,s+dt*.65);if(s===Math.PI)stop();}
    sync();if(animation)frame=requestAnimationFrame(tick);
  }
  function sync(){
    select.value=mode;time.value=String(Math.max(.02,t));time.disabled=mode==='compare';timeOut.textContent=mode==='compare'?'four times':t===0?'0 (limit)':t.toFixed(2);
    phase.value=String(s/Math.PI);phaseOut.textContent=`${(s/Math.PI).toFixed(2)}π`;phaseLabel.hidden=trace.hidden=mode!=='orbit';
    play.textContent=animation==='time'?'Pause time':'Play time';trace.textContent=animation==='orbit'?'Pause connection':'Trace connection';
    coneButton.setAttribute('aria-pressed',String(cone));figure.dataset.lwView=mode;
    note.textContent=mode==='orbit'?'The circle lies in a two-dimensional plane in R⁶. Moving in s stays within the same time slice Lₜ; it is not time evolution. Its half-turn connects x on the blue sheet to −x on the ochre sheet.':
      'Exact s = 0 slices of a three-manifold in C³ = R⁶. Blue: x₃ ≥ 0; ochre: x₃ ≤ 0. Dashed gray: cone. These two-dimensional slices do not themselves solve mean curvature flow in R³.';
    status.textContent=mode==='compare'?'Same spatial scale at t = 0, 0.25, 1, 4. The t = 0 panel is the singular cone limit.':
      t===0?'t = 0: singular cone limit, outside the smooth expander interval t > 0.':`t = ${t.toFixed(2)}; slice tips x₃ = ±${Math.sqrt(2*t).toFixed(3)}. Lₜ = √t L₁. Display radius r ≤ ${LW.radius} is fixed in physical coordinates.`;
    canvas.setAttribute('aria-label',mode==='compare'?'Four exact real slices of the Lee–Wang expander in C3, at t = 0 (singular cone), 0.25, 1 and 4, with identical scales. Arrow keys rotate all slices.':mode==='orbit'?`Exact real slice at t = ${t.toFixed(2)} and its circle orbit in a plane in R6. Phase s = ${(s/Math.PI).toFixed(2)} pi connects opposite sheets.`:`Exact real slice at t = ${t.toFixed(2)} of the Lee–Wang expander in C3; not a flow in R3. Arrow keys rotate; plus and minus zoom.`);
    requestDraw();
  }
  function line(points,color='#8b9ca3',width=1,dash=[]){ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.stroke();ctx.setLineDash([]);}
  function text(str,x,y,size=13,color='#254858',align='left'){ctx.fillStyle=color;ctx.font=`${size}px system-ui, sans-serif`;ctx.textAlign=align;ctx.fillText(str,x,y);ctx.textAlign='left';}
  function dot(p,color){ctx.beginPath();ctx.arc(...p,4.5,0,2*Math.PI);ctx.fillStyle=color;ctx.fill();ctx.strokeStyle='#fff';ctx.lineWidth=1.5;ctx.stroke();}
  function slice(value,box,showPoints=false){
    ctx.save();ctx.beginPath();ctx.rect(box.x,box.y,box.w,box.h);ctx.clip();
    const scene=surfaceScene(value,box,state,mode==='compare'?[16,40]:[24,56]);
    for(const poly of scene.polygons){ctx.beginPath();poly.points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.closePath();ctx.fillStyle=poly.color;ctx.fill();ctx.strokeStyle=mesh?'#1b43553b':poly.color;ctx.lineWidth=mesh?.5:.4;ctx.stroke();}
    // Sparse dotted meridians of the cone are a reference overlay, not extra surfaces.
    if(cone)for(const sign of [1,-1])for(const theta of [0,Math.PI/2,Math.PI,3*Math.PI/2])line(Array.from({length:41},(_,i)=>scene.project(slicePoint(LW.radius*i/40,theta,0,sign))),'#637a858a',1,[3,4]);
    for(const sign of [1,-1]){
      line(Array.from({length:81},(_,i)=>scene.project(slicePoint(LW.radius,2*Math.PI*i/80,value,sign))),sign>0?'#266d87':'#98572d',1);
      dot(scene.project(slicePoint(0,0,value,sign)),sign>0?'#21667f':'#ad622d');
    }
    if(showPoints){const x=slicePoint(1,0,value);dot(scene.project(x),'#06384d');dot(scene.project(x.map(v=>-v)),'#8d3c10');text('x',...scene.project(x).map((v,i)=>v+(i? -9:8)),14);text('−x',...scene.project(x.map(v=>-v)).map((v,i)=>v+(i?18:8)),14);}
    // Inset triad: orientation only; the scale bar below supplies length.
    const base=[box.x+24,box.y+box.h-29];
    for(const [axis,name] of [[[1,0,0],'x₁'],[[0,1,0],'x₂'],[[0,0,1],'x₃']]){const q=rotate(axis,state.yaw,state.pitch),end=[base[0]+18*q[0],base[1]-18*q[1]];line([base,end],'#526e7c');text(name,end[0]+3,end[1]+3,10);}
    const bx=box.x+box.w-25-scene.scale,by=box.y+box.h-17;line([[bx,by],[bx+scene.scale,by]],'#476170',2);text('1 unit',bx+scene.scale/2,by-7,10,'#476170','center');ctx.restore();
  }
  function orbit(box){
    const x=slicePoint(1,0,t),radius=Math.hypot(...x),scale=Math.min(box.w*.32,box.h*.29)/Math.sqrt(10),R=radius*scale;
    const cx=box.x+box.w/2,cy=box.y+box.h/2;
    text('Circle orbit in R⁶',cx,box.y+22,13,'#254858','center');
    line([[cx-R-10,cy],[cx+R+10,cy]],'#a9b9c0');line([[cx,cy-R-10],[cx,cy+R+10]],'#a9b9c0');
    line(Array.from({length:101},(_,i)=>[cx+R*Math.cos(2*Math.PI*i/100),cy-R*Math.sin(2*Math.PI*i/100)]),'#becbd1',1.5);
    line(Array.from({length:81},(_,i)=>[cx+R*Math.cos(Math.PI*i/80),cy-R*Math.sin(Math.PI*i/80)]),'#297d96',2.5);
    dot([cx+R,cy],'#21667f');dot([cx-R,cy],'#ad622d');dot([cx+R*Math.cos(s),cy-R*Math.sin(s)],'#823f73');
    text('x',cx+R+8,cy+5);text('−x',cx-R-24,cy+5);
    text('s = 0',cx+R,cy+23,11,'#21667f','center');text('s = π',cx-R,cy+23,11,'#ad622d','center');
    text('imaginary direction',cx,cy-R-19,11,'#627a85','center');
    text(`s = ${(s/Math.PI).toFixed(2)}π`,cx,box.y+box.h-35,13,'#823f73','center');
    text('γₓ(s) = cos(s)x + sin(s)i(x₁,x₂,−x₃)',cx,box.y+box.h-14,box.w<300?10:12,'#476170','center');
  }
  function draw(){queued=false;const {width:w,height:h}=stage.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2);canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
    if(mode==='compare'){
      text('REAL SLICES · SAME SPATIAL SCALE',w/2,23,w<400?11:13,'#476170','center');
      const pw=w/2,ph=(h-40)/2;
      LW.times.forEach((value,i)=>{const x=(i%2)*pw,y=38+Math.floor(i/2)*ph;text(value===0?'t = 0 · cone limit':`t = ${value}`,x+pw/2,y+14,13,'#254858','center');slice(value,{x:x+6,y:y+18,w:pw-12,h:ph-23});});
      line([[w/2,38],[w/2,h-5]],'#dce5e9');line([[12,38+ph],[w-12,38+ph]],'#dce5e9');
    }else if(mode==='orbit'){
      const narrow=w<540;if(narrow){slice(t,{x:0,y:26,w,h:h*.52-26},true);orbit({x:0,y:h*.52,w,h:h*.48});}
      else{slice(t,{x:0,y:30,w:w*.53,h:h-30},true);orbit({x:w*.53,y:30,w:w*.47,h:h-30});}
      text(`Real slice at t = ${t.toFixed(2)}`,12,23,13);
    }else{text(t===0?'t = 0 · singular cone limit':`t = ${t.toFixed(2)} · x₃² − x₁² − x₂² = 2t`,12,24,13);slice(t,{x:0,y:35,w,h:h-35});}
    Object.assign(canvas.dataset,{time:String(t),phase:String(s/Math.PI),view:mode,zoom:state.zoom.toFixed(3),rotation:`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`,cone:String(cone)});
  }
  function requestDraw(){if(!queued){queued=true;requestAnimationFrame(draw);}}
  function zoom(f){state.zoom=Math.max(.5,Math.min(2.5,state.zoom*f));requestDraw();}
  select.addEventListener('change',()=>{stop();mode=select.value;if(mode==='orbit'&&t===0)t=1;sync();});
  time.addEventListener('input',()=>{stop();t=Number(time.value);sync();});
  phase.addEventListener('input',()=>{stop();s=Number(phase.value)*Math.PI;sync();});
  for(const b of controls.querySelectorAll('[data-view-action]'))b.addEventListener('click',()=>{
    if(b.dataset.viewAction==='in')zoom(1.2);if(b.dataset.viewAction==='out')zoom(1/1.2);
    if(b.dataset.viewAction==='wire'){mesh=!mesh;b.setAttribute('aria-pressed',String(mesh));requestDraw();}
    if(b.dataset.viewAction==='reset'){stop();t=1;s=0;mode='compare';state={yaw:.55,pitch:.25,zoom:1};mesh=false;cone=true;controls.querySelector('[data-view-action=wire]').setAttribute('aria-pressed','false');sync();}
  });
  canvas.addEventListener('pointerdown',e=>{drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;state.yaw+=(e.clientX-drag[0])*.009;state.pitch=Math.max(-1.35,Math.min(1.35,state.pitch+(e.clientY-drag[1])*.007));drag=[e.clientX,e.clientY];requestDraw();});
  for(const name of ['pointerup','pointercancel'])canvas.addEventListener(name,()=>{drag=null;});
  canvas.addEventListener('keydown',e=>{const keys={ArrowLeft:()=>state.yaw-=.12,ArrowRight:()=>state.yaw+=.12,ArrowUp:()=>state.pitch=Math.max(-1.35,state.pitch-.12),ArrowDown:()=>state.pitch=Math.min(1.35,state.pitch+.12),'+':()=>zoom(1.2),'=':()=>zoom(1.2),'-':()=>zoom(1/1.2)};if(keys[e.key]){e.preventDefault();keys[e.key]();requestDraw();}});
  canvas.addEventListener('wheel',e=>{if(document.activeElement!==canvas)return;e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  new IntersectionObserver(items=>{if(!items[0].isIntersecting)stop();}).observe(figure);
  new ResizeObserver(requestDraw).observe(stage);
  help.textContent='Drag or use arrow keys to rotate the real slices. Zoom applies equally to all time panels. Play time runs forward; Trace connection changes the circle phase at fixed time. Outer rims are display cutoffs.';
  figure.querySelector('img').hidden=true;canvas.hidden=false;controls.hidden=false;help.hidden=false;sync();
}
