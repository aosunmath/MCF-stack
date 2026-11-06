// A Scherk-based construction picture, not a solution of the shrinker PDE.
export function kkmVertices(data, amplitude) {
  return data.vertices.map(([x,y,z],i)=>[x,y,amplitude===0||data.construction.endWeights[i]===0?z:z+amplitude*data.construction.endWeights[i]]);
}

export function kkmGeometry(data, amplitude, cutaway=false) {
  const vertices=kkmVertices(data,amplitude),faces=[];
  if(!cutaway)return {vertices,faces:data.faces.map((face,index)=>({face,index}))};
  function clip(polygon,normal){
    const result=[],dist=i=>normal[0]*vertices[i][0]+normal[1]*vertices[i][1];
    polygon.forEach((a,j)=>{
      const b=polygon[(j+1)%polygon.length],da=dist(a),db=dist(b);
      if(da<=0)result.push(a);
      if((da<0&&db>0)||(da>0&&db<0)){
        const t=da/(da-db);result.push(vertices.length);
        vertices.push(vertices[a].map((x,i)=>x+t*(vertices[b][i]-x)));
      }
    });return result;
  }
  data.faces.forEach((face,index)=>{
    // Split at x=0, then clip the two half-planes bounding the removed wedge.
    for(const side of [-1,1]){
      const polygon=clip(clip(face,[-side,0]),[-.35*side,1]);
      for(let j=1;j+1<polygon.length;j++)faces.push({face:[polygon[0],polygon[j],polygon[j+1]],index});
    }
  });
  return {vertices,faces};
}

export function initKKMFigure(figure, initial, rotatePoint) {
  const canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d');
  if(!ctx)throw new Error('Canvas unavailable');
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  const help=figure.querySelector('.soliton-help'),status=figure.querySelector('.soliton-status');
  let data=initial,vertices,visible,dragging=null,scheduled=false,requestId=0;
  const defaults=()=>({yaw:.42,pitch:.32,zoom:1,cutaway:false,wire:false,amplitude:.075});
  let state=defaults();
  const cache=new Map([[initial.construction.periods,initial]]);
  const legend=document.createElement('p');legend.className='soliton-help kkm-legend';
  for(const [label,color] of [['● Caps','#3c7690'],['● Scherk belt','#a35e28'],['● Disk / outer sheet','#507f8d']]){
    const span=document.createElement('span');span.textContent=label;span.style.color=color;legend.append(span);
  }
  stage.after(legend);
  const cut=document.createElement('button');cut.type='button';cut.textContent='Cutaway';cut.setAttribute('aria-pressed','false');
  const periodLabel=document.createElement('label');periodLabel.textContent='Illustrative periods k ';
  const periods=document.createElement('select');periods.setAttribute('aria-label','Illustrative Scherk period count');
  for(const k of [6,9,12]){const option=document.createElement('option');option.value=String(k);option.textContent=String(k);periods.append(option);}
  periods.value=String(initial.construction.periods);periodLabel.append(periods);
  const waveLabel=document.createElement('label'),waveOutput=document.createElement('output'),wave=document.createElement('input');
  wave.type='range';wave.min='0';wave.max='.15';wave.step='.005';wave.value=String(state.amplitude);
  wave.setAttribute('aria-label','Illustrative conical end waviness');waveLabel.append(waveOutput,wave);
  controls.append(cut,periodLabel,waveLabel);
  help.textContent='Drag to rotate; + / − zoom. Cutaway exposes the inner disk and lower cap; its cut edges are artificial. The period count and cone waviness are illustration choices.';
  function sync(){
    const geometry=kkmGeometry(data,state.amplitude,state.cutaway);vertices=geometry.vertices;visible=geometry.faces;
    cut.setAttribute('aria-pressed',String(state.cutaway));wave.value=String(state.amplitude);
    waveOutput.textContent=`End waviness: ${state.amplitude.toFixed(3)}`;
    periods.value=String(data.construction.periods);
    figure.querySelector('[data-view-action=wire]').setAttribute('aria-pressed',String(state.wire));
    status.textContent=`Construction model: k = ${data.construction.periods}, genus k − 1 = ${data.construction.genus}. These displayed values do not specify the theorem’s sufficiently large genus range. ${state.amplitude===0?'Zero waviness shows a plane-asymptotic construction model; the theorem’s end is nonplanar.':'The conical profile is illustrative, not computed from the shrinker equation.'}`;
    canvas.setAttribute('aria-label',`Rotatable Scherk-based construction schematic with ${data.construction.periods} periods and model genus ${data.construction.genus}. Not a computed self-shrinker. Arrow keys rotate; plus and minus zoom.`);
  }
  function draw(){
    scheduled=false;
    const {width,height}=stage.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2);
    if(canvas.width!==Math.round(width*dpr)||canvas.height!==Math.round(height*dpr)){
      canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);
    }
    ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,width,height);
    const scale=Math.min(width*.45/3.8,height*.40/2.2)*state.zoom;
    const q=vertices.map(p=>rotatePoint(p,state));
    const screen=q.map(p=>[width/2+scale*p[0],height/2+5-scale*p[1]]);
    const ordered=visible.map(({face,index})=>({face,index,z:face.reduce((s,i)=>s+q[i][2],0)/3})).sort((a,b)=>a.z-b.z);
    for(const {face,index} of ordered){
      const [a,b,c]=face.map(i=>q[i]),u=b.map((x,i)=>x-a[i]),v=c.map((x,i)=>x-a[i]);
      const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
      const light=.42+.52*Math.abs((.3*n[0]+.5*n[1]+.8*n[2])/(Math.hypot(...n)||1));
      const rgb=data.faceColors[index].map(base=>Math.round(base*light+255*(1-light)*.25));
      ctx.fillStyle=`rgb(${rgb.join(',')})`;ctx.strokeStyle=state.wire?'rgba(24,63,82,.3)':ctx.fillStyle;
      ctx.lineWidth=state.wire?.5:.4;ctx.beginPath();face.forEach((i,j)=>j?ctx.lineTo(...screen[i]):ctx.moveTo(...screen[i]));ctx.closePath();ctx.fill();ctx.stroke();
    }
    ctx.fillStyle='#183f52';ctx.font='13px sans-serif';ctx.fillText('Scherk-based construction schematic',14,24);
    ctx.fillStyle='#617785';ctx.font='12px sans-serif';
    ctx.fillText(state.cutaway?'Cutaway · artificial cut edges':'One outer sheet · edge truncated for display',14,height-15);
    canvas.dataset.view=state.cutaway?'cutaway':'surface';canvas.dataset.periods=String(data.construction.periods);
    canvas.dataset.zoom=state.zoom.toFixed(3);canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;
    canvas.dataset.amplitude=String(state.amplitude);canvas.dataset.faces=String(visible.length);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function zoom(f){state.zoom=Math.max(.35,Math.min(4,state.zoom*f));requestDraw();}
  cut.addEventListener('click',()=>{state.cutaway=!state.cutaway;sync();requestDraw();});
  wave.addEventListener('input',()=>{state.amplitude=Number(wave.value);sync();requestDraw();});
  periods.addEventListener('change',async()=>{
    const k=Number(periods.value),id=++requestId;
    status.textContent=`Loading the k = ${k} construction model…`;
    try{
      if(!cache.has(k)){
        const url=new URL(k===9?'kkm-shrinker.json':`kkm-shrinker-${k}.json`,new URL(figure.dataset.soliton,document.baseURI));
        const response=await fetch(url);if(!response.ok)throw new Error('Geometry unavailable');
        const next=await response.json();if(next.construction?.periods!==k)throw new Error('Wrong period count');cache.set(k,next);
      }
      if(id!==requestId)return;
      data=cache.get(k);sync();requestDraw();
    }catch{
      if(id!==requestId)return;
      periods.value=String(data.construction.periods);
      status.textContent=`Could not load k = ${k}; the k = ${data.construction.periods} model remains visible.`;
    }
  });
  for(const button of controls.querySelectorAll('[data-view-action]'))button.addEventListener('click',()=>{
    const action=button.dataset.viewAction;
    if(action==='in')zoom(1.2);
    if(action==='out')zoom(1/1.2);
    if(action==='wire'){state.wire=!state.wire;sync();requestDraw();}
    if(action==='reset'){++requestId;data=initial;state=defaults();sync();requestDraw();}
  });
  canvas.addEventListener('pointerdown',e=>{dragging={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!dragging)return;state.yaw+=(e.clientX-dragging.x)*.009;state.pitch+=(e.clientY-dragging.y)*.009;dragging={x:e.clientX,y:e.clientY};requestDraw();});
  for(const event of ['pointerup','pointercancel'])canvas.addEventListener(event,()=>{dragging=null;});
  canvas.addEventListener('wheel',e=>{if(document.activeElement!==canvas)return;e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  canvas.addEventListener('keydown',e=>{
    const keys={ArrowLeft:()=>state.yaw-=.12,ArrowRight:()=>state.yaw+=.12,ArrowUp:()=>state.pitch-=.12,ArrowDown:()=>state.pitch+=.12,'+':()=>zoom(1.15),'=':()=>zoom(1.15),'-':()=>zoom(1/1.15)};
    if(keys[e.key]){e.preventDefault();keys[e.key]();requestDraw();}
  });
  controls.hidden=false;help.hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;
  sync();new ResizeObserver(requestDraw).observe(stage);requestDraw();
}
