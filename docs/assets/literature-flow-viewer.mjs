/* Fixed-scale time comparisons for source-reviewed examples. Geometry accuracy is
 * supplied by the catalogue; interaction never promotes a schematic to a PDE solve. */
const palette=['#087f8c','#c56535','#6d55a1','#88939d'];
export function rotateLiteraturePoint([x,y,z],yaw,pitch){
  const a=x*Math.cos(yaw)-y*Math.sin(yaw),b=x*Math.sin(yaw)+y*Math.cos(yaw);
  return [a,b*Math.cos(pitch)-z*Math.sin(pitch),b*Math.sin(pitch)+z*Math.cos(pitch)];
}
export function commonLiteratureBounds(frames){
  const lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];
  for(const frame of frames) for(const p of frame.vertices) p.forEach((v,i)=>{lo[i]=Math.min(lo[i],v);hi[i]=Math.max(hi[i],v);});
  const center=lo.map((v,i)=>(v+hi[i])/2);
  let radius=0;
  for(const frame of frames) for(const p of frame.vertices)radius=Math.max(radius,Math.hypot(...p.map((v,i)=>v-center[i])));
  return {center,radius:Math.max(radius,1e-6)};
}
export function initLiteratureFlow(figure,data){
  const stage=figure.querySelector('.soliton-stage'),canvas=stage.querySelector('canvas'),ctx=canvas.getContext('2d');
  const controls=figure.querySelector('.soliton-controls'),status=figure.querySelector('.soliton-status');
  const help=figure.querySelector('.soliton-help');
  stage.querySelector('img').hidden=true;canvas.hidden=false;controls.hidden=false;help.hidden=false;
  help.textContent='Compare the three times at the same scale. Drag to rotate; arrow keys rotate; + and − zoom. Profile, slice and schematic qualifications are stated below.';
  const label=document.createElement('label');label.textContent='Display ';
  const display=document.createElement('select');display.setAttribute('aria-label','Time display');
  [['all','Compare all times'],...data.timeLabels.map((v,i)=>[String(i),v])].forEach(([v,t])=>{const o=document.createElement('option');o.value=v;o.textContent=t;display.append(o);});label.append(display);controls.prepend(label);
  const viewLabel=document.createElement('label');viewLabel.textContent=' View ';
  const view=document.createElement('select');view.setAttribute('aria-label','Projection view');
  [['space','Spatial view'],['plane','Profile / xy'],['side','Side / xz']].forEach(([v,t])=>{const o=document.createElement('option');o.value=v;o.textContent=t;view.append(o);});viewLabel.append(view);controls.append(viewLabel);
  let activeFrames=data.variants?.[0]?.frames||data.frames;
  const planar=activeFrames.every(f=>f.vertices.every(v=>Math.abs(v[2])<1e-9));
  const home={yaw:planar?0:-.45,pitch:planar?0:-.8};let yaw=home.yaw,pitch=home.pitch,zoom=1,wire=false;
  if(planar)view.value='plane';
  let bounds=commonLiteratureBounds(activeFrames);
  const note=data.timeMode==='schematic-stages'?'Stages are schematic, without assigned physical times.':'All panels use one spatial origin and scale; time labels refer to the stated normalization.';
  status.textContent=note;
  function draw(){
    const width=Math.max(260,stage.clientWidth),compare=display.value==='all',vertical=compare&&width<590;
    const height=vertical?760:compare?360:440,dpr=window.devicePixelRatio||1;
    stage.style.height=height+'px';stage.style.aspectRatio='auto';canvas.style.width=width+'px';canvas.style.height=height+'px';
    if(canvas.width!==Math.round(width*dpr)||canvas.height!==Math.round(height*dpr)){canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);}
    ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle='#f8faf9';ctx.fillRect(0,0,width,height);
    const indices=compare?[0,1,2]:[Number(display.value)];
    indices.forEach((index,j)=>{
      const pw=compare&&!vertical?width/3:width,ph=vertical?height/3:height,ox=compare&&!vertical?j*pw:0,oy=vertical?j*ph:0;
      const scale=Math.min(pw-22,ph-82)*.47/bounds.radius*zoom,cx=ox+pw/2,cy=oy+ph*.55;
      ctx.save();ctx.beginPath();ctx.rect(ox+1,oy+1,pw-2,ph-2);ctx.clip();
      ctx.strokeStyle='#dce5e4';ctx.lineWidth=1;ctx.strokeRect(ox+.5,oy+.5,pw-1,ph-1);
      ctx.fillStyle='#29484f';ctx.font='600 14px system-ui';ctx.textAlign='center';ctx.fillText(data.timeLabels[index],cx,oy+27);
      const g=activeFrames[index],pts=g.vertices.map(p=>rotateLiteraturePoint(p.map((v,i)=>v-bounds.center[i]),yaw,pitch));
      const screen=p=>[cx+p[0]*scale,cy-p[1]*scale];
      const zero=screen(rotateLiteraturePoint(bounds.center.map(v=>-v),yaw,pitch));
      ctx.strokeStyle='#becbcd';ctx.lineWidth=.7;ctx.beginPath();ctx.moveTo(ox+12,zero[1]);ctx.lineTo(ox+pw-12,zero[1]);ctx.moveTo(zero[0],oy+42);ctx.lineTo(zero[0],oy+ph-18);ctx.stroke();
      const order=g.faces.map((f,i)=>({f,i,z:f.reduce((s,k)=>s+pts[k][2],0)/f.length})).sort((a,b)=>a.z-b.z);
      for(const {f,i} of order){ctx.beginPath();f.forEach((k,n)=>{const [x,y]=screen(pts[k]);n?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.closePath();const color=palette[(g.faceColors?.[i]||0)%4];ctx.fillStyle=color+'48';ctx.fill();if(wire){ctx.strokeStyle=color+'65';ctx.lineWidth=.55;ctx.stroke();}}
      g.paths.forEach((path,i)=>{ctx.beginPath();path.forEach((k,n)=>{const [x,y]=screen(pts[k]);n?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.strokeStyle=palette[(g.pathColors?.[i]||0)%4];ctx.lineWidth=1.5;ctx.stroke();});
      ctx.fillStyle='#60747a';ctx.font='11px system-ui';ctx.fillText(data.timeMode==='schematic-stages'?'schematic stage':'fixed spatial scale',cx,oy+ph-9);ctx.restore();
    });
  }
  if(data.variants){
    const modelLabel=document.createElement('label');modelLabel.textContent=' Drawing ';
    const model=document.createElement('select');model.setAttribute('aria-label','Geometric case');
    data.variants.forEach((v,i)=>{const o=document.createElement('option');o.value=String(i);o.textContent=v.label;model.append(o);});modelLabel.append(model);controls.prepend(modelLabel);
    model.addEventListener('change',()=>{activeFrames=data.variants[Number(model.value)].frames;bounds=commonLiteratureBounds(activeFrames);zoom=1;const flat=activeFrames.every(f=>f.vertices.every(v=>Math.abs(v[2])<1e-9));yaw=flat?0:-.45;pitch=flat?0:-.8;view.value=flat?'plane':'space';draw();});
  }
  display.addEventListener('change',draw);view.addEventListener('change',()=>{[yaw,pitch]=view.value==='plane'?[0,0]:view.value==='side'?[0,-Math.PI/2]:[-.45,-.8];draw();});
  controls.addEventListener('click',event=>{const action=event.target.closest('[data-view-action]')?.dataset.viewAction;if(!action)return;if(action==='in')zoom=Math.min(zoom*1.2,8);if(action==='out')zoom=Math.max(zoom/1.2,.2);if(action==='reset'){const flat=activeFrames.every(f=>f.vertices.every(v=>Math.abs(v[2])<1e-9));yaw=flat?0:-.45;pitch=flat?0:-.8;zoom=1;display.value='all';view.value=flat?'plane':'space';}if(action==='wire'){wire=!wire;event.target.setAttribute('aria-pressed',String(wire));}draw();});
  let drag=null;canvas.style.touchAction='pan-y';
  canvas.addEventListener('pointerdown',e=>{if(e.pointerType==='touch'&&!e.isPrimary)return;drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;yaw+=(e.clientX-drag[0])*.01;pitch+=(e.clientY-drag[1])*.01;drag=[e.clientX,e.clientY];draw();});
  for(const event of ['pointerup','pointercancel'])canvas.addEventListener(event,()=>{drag=null;});
  canvas.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-'].includes(e.key))return;e.preventDefault();if(e.key==='ArrowLeft')yaw-=.12;if(e.key==='ArrowRight')yaw+=.12;if(e.key==='ArrowUp')pitch+=.12;if(e.key==='ArrowDown')pitch-=.12;if(['+','='].includes(e.key))zoom=Math.min(8,zoom*1.15);if(e.key==='-')zoom=Math.max(.2,zoom/1.15);draw();});
  new ResizeObserver(draw).observe(stage);draw();
}
