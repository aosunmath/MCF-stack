// Møller's singular limiting configuration, not a finite-genus solution.
export function configurationFaces(data, {sphere=true, torus=true, degrees=360}={}) {
  const removed=Math.round((360-degrees)*data.segments/360);
  return data.faces.map((face,index)=>({face,index})).filter(({index})=>
    (data.faceGroups[index]===0?sphere:torus) && data.faceSectors[index]>=removed);
}

export function initMollerFigure(figure, data, rotatePoint) {
  const canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d');
  if(!ctx)throw new Error('Canvas unavailable');
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  const defaults=()=>({yaw:data.view.yaw,pitch:data.view.pitch,zoom:1,sphere:true,torus:true,circles:true,degrees:data.view.degrees,meridian:false,wire:false});
  let state=defaults(),dragging=null,scheduled=false,visible=[];
  const sphereColor='#b57a2b',torusColor='#21667f',seamColor='#b34838';
  const buttons={};
  const help=figure.querySelector('.soliton-help');
  const legend=document.createElement('p');legend.className='soliton-help';legend.style.marginTop='10px';
  for(const [label,color] of [['● Sphere: radius 2',sphereColor],['● Torus: numerical ODE',torusColor],['● Intersection circles',seamColor]]){
    const span=document.createElement('span');span.textContent=label;span.style.color=color;span.style.display='inline-block';span.style.marginRight='16px';legend.append(span);
  }
  stage.after(legend);
  canvas.setAttribute('aria-label','Møller sphere–torus limiting configuration. Drag or use arrow keys to rotate; plus and minus zoom. Use Meridian for the generating curves. This is not the desingularized shrinker.');
  function line(points,color,width=2,dashed=false){
    ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dashed?[4,3]:[]);ctx.beginPath();
    points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.stroke();ctx.setLineDash([]);
  }
  function draw(){
    scheduled=false;
    const {width,height}=stage.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2);
    if(canvas.width!==Math.round(width*dpr)||canvas.height!==Math.round(height*dpr)){
      canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);
    }
    ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,width,height);
    ctx.fillStyle='#183f52';ctx.font='14px sans-serif';
    ctx.fillText(state.meridian?'Meridian in the (r, z) half-plane':'Singular sphere–torus limit',14,24);
    if(state.meridian){
      const scale=Math.min((width-70)/3.7,(height-90)/4.4)*state.zoom;
      const screen=([r,z])=>[width/2+scale*(r-1.7),height/2+8-scale*z];
      line([screen([0,-2.2]),screen([0,2.2])],'#94a9b3',1,true);
      line([screen([0,0]),screen([3.6,0])],'#94a9b3',1,true);
      for(const [i,on,color] of [[0,state.sphere,sphereColor],[1,state.torus,torusColor]]){
        if(on)line(data.meridians[i].map(screen),color,2.5);
      }
      if(state.circles)for(const p of data.intersections){
        ctx.beginPath();ctx.arc(...screen([p.r,p.z]),4,0,2*Math.PI);ctx.fillStyle=seamColor;ctx.fill();
      }
      ctx.fillStyle='#183f52';ctx.fillText('z',...screen([-.15,2.15]));ctx.fillText('r',...screen([3.5,-.25]));
      ctx.font='12px sans-serif';ctx.fillText('Intersections: r ≈ 1.783, z ≈ ±0.906',14,height-16);
    } else {
      const scale=Math.min(width*.44/data.view.radius,height*.40/2.2)*state.zoom;
      const q=data.vertices.map(p=>rotatePoint(p,state));
      const screen=q.map(p=>[width/2+scale*p[0],height/2+5-scale*p[1]]);
      const ordered=visible.map(({face,index})=>({face,index,z:face.reduce((s,i)=>s+q[i][2],0)/3})).sort((a,b)=>a.z-b.z);
      for(const {face,index} of ordered){
        const [a,b,c]=face.map(i=>q[i]),u=b.map((x,i)=>x-a[i]),v=c.map((x,i)=>x-a[i]);
        const normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
        const light=.42+.52*Math.abs((.3*normal[0]+.5*normal[1]+.8*normal[2])/(Math.hypot(...normal)||1));
        const rgb=data.palette[data.faceGroups[index]].map(base=>Math.round(base*light+255*(1-light)*.25));
        ctx.fillStyle=`rgb(${rgb.join(',')})`;ctx.strokeStyle=state.wire?'rgba(24,63,82,.32)':ctx.fillStyle;
        ctx.lineWidth=state.wire?.5:.4;ctx.beginPath();face.forEach((i,j)=>j?ctx.lineTo(...screen[i]):ctx.moveTo(...screen[i]));ctx.closePath();ctx.fill();ctx.stroke();
      }
      if(state.circles)for(const ring of data.paths)line(ring.map(i=>screen[i]),seamColor,1.8,true);
      ctx.fillStyle='#617785';ctx.font='12px sans-serif';
      ctx.fillText(state.degrees===270?'Quarter removed to expose the interior':'Full limiting configuration',14,height-16);
    }
    canvas.dataset.view=state.meridian?'meridian':'surface';canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;
    canvas.dataset.zoom=state.zoom.toFixed(3);canvas.dataset.revolution=String(state.degrees);
    canvas.dataset.sphere=String(state.sphere);canvas.dataset.torus=String(state.torus);canvas.dataset.circles=String(state.circles);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function sync(){
    visible=configurationFaces(data,state);
    for(const key of ['sphere','torus','circles','meridian'])buttons[key].setAttribute('aria-pressed',String(state[key]));
    buttons.cutaway.setAttribute('aria-pressed',String(state.degrees===270));buttons.cutaway.disabled=state.meridian;
    figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed',String(state.wire));
    figure.querySelector('[data-view-action="wire"]').disabled=state.meridian;
    help.textContent=state.meridian
      ?'The two marked points generate the two intersection circles. The torus profile comes from numerical ODE integration; the sphere has radius 2.'
      :'Drag to rotate; use + / − to zoom. Toggle Sphere, Torus, or Cutaway to inspect the sheets. Dashed red circles are shown through the surfaces. Cut edges are display boundaries.';
    requestDraw();
  }
  function zoom(f){state.zoom=Math.max(.5,Math.min(3,state.zoom*f));requestDraw();}
  for(const key of ['sphere','torus','circles','cutaway','meridian']){
    const b=document.createElement('button');b.type='button';b.textContent=key[0].toUpperCase()+key.slice(1);b.dataset.mollerAction=key;
    b.addEventListener('click',()=>{
      if(key==='cutaway')state.degrees=state.degrees===270?360:270;
      else state[key]=!state[key];
      if(key==='meridian'){state.zoom=1;dragging=null;}
      sync();
    });buttons[key]=b;controls.append(b);
  }
  for(const b of figure.querySelectorAll('[data-view-action]'))b.addEventListener('click',()=>{
    const action=b.dataset.viewAction;
    if(action==='in')zoom(1.2);
    if(action==='out')zoom(1/1.2);
    if(action==='wire'){state.wire=!state.wire;sync();}
    if(action==='reset'){state=defaults();dragging=null;sync();}
  });
  canvas.addEventListener('pointerdown',e=>{if(state.meridian)return;dragging={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!dragging)return;state.yaw+=(e.clientX-dragging.x)*.009;state.pitch+=(e.clientY-dragging.y)*.009;dragging={x:e.clientX,y:e.clientY};requestDraw();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>{dragging=null;});
  canvas.addEventListener('keydown',e=>{
    if(e.key==='+'||e.key==='='){e.preventDefault();zoom(1.2);}
    else if(e.key==='-'){e.preventDefault();zoom(1/1.2);}
    else if(!state.meridian&&['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){
      e.preventDefault();if(e.key==='ArrowLeft')state.yaw-=.12;if(e.key==='ArrowRight')state.yaw+=.12;
      if(e.key==='ArrowUp')state.pitch-=.12;if(e.key==='ArrowDown')state.pitch+=.12;requestDraw();
    }
  });
  canvas.addEventListener('wheel',e=>{if(document.activeElement!==canvas)return;e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  controls.hidden=false;help.hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;
  new ResizeObserver(requestDraw).observe(stage);sync();
}
