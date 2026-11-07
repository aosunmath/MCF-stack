// Precomputed equivariant PDE snapshots; no geometric interpolation in time.
export function rightLobe(quarter) {
  return [...quarter,...quarter.slice(0,-1).reverse().map(([a,b])=>[a,-b])];
}
export function fullProfile(quarter) {
  const right=rightLobe(quarter);
  return [...right,...right.slice(1).map(([a,b])=>[-a,-b])];
}
export function sphereMesh(quarter,segments=32,stride=2) {
  const sampled=quarter.filter((_,i)=>i%stride===0);
  if((quarter.length-1)%stride)sampled.push(quarter.at(-1));
  const lobe=rightLobe(sampled), vertices=[], faces=[], groups=[];
  // One right lobe times S1 parametrizes S2, with each boundary circle collapsed.
  // The two poles are distinct domain points at the same image point in R4.
  vertices.push([0,0,0,0]);
  for(let i=1;i<lobe.length-1;i++)for(let j=0;j<segments;j++){
    const [a,b]=lobe[i],v=2*Math.PI*j/segments,c=Math.cos(v),s=Math.sin(v);
    vertices.push([a*c,a*s,b*c,b*s]);
  }
  const end=vertices.length;vertices.push([0,0,0,0]);
  const index=(row,j)=>1+(row-1)*segments+(j+segments)%segments;
  for(let j=0;j<segments;j++){
    faces.push([0,index(1,j+1),index(1,j)]);groups.push(0);
    for(let i=1;i<lobe.length-2;i++){
      const a=index(i,j),b=index(i,j+1),c=index(i+1,j),d=index(i+1,j+1);
      faces.push([a,b,d],[a,d,c]);groups.push(i<sampled.length-1?0:1,i<sampled.length-1?0:1);
    }
    faces.push([index(lobe.length-2,j),index(lobe.length-2,j+1),end]);groups.push(1);
  }
  return {vertices,faces,groups};
}

export function initWhitneyFlowFigure(figure,data,rotatePoint) {
  const canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d');
  if(!ctx)return;
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  figure.classList.add('whitney-flow-figure');
  let frame=0,mode='sequence',state={yaw:.64,pitch:.43,fourD:.55,zoom:1},wire=false,drag=null,scheduled=false,timer=null;
  const meshCache=new Map();
  const mesh=i=>{if(!meshCache.has(i))meshCache.set(i,sphereMesh(data.frames[i].quarter));return meshCache.get(i);};
  const status=figure.querySelector('.soliton-status'),help=figure.querySelector('.soliton-help');
  const choice=document.createElement('select');choice.setAttribute('aria-label','Whitney flow view');
  for(const [value,text] of [['sequence','Time sequence'],['surface','Surface projection'],['profile','Planar profile']]){
    const option=document.createElement('option');option.value=value;option.textContent=text;choice.append(option);
  }
  const play=document.createElement('button');play.type='button';play.textContent='Play flow';
  const timeLabel=document.createElement('label'),output=document.createElement('output'),slider=document.createElement('input');
  slider.type='range';slider.min='0';slider.max=String(data.frames.length-1);slider.step='1';slider.value='0';slider.setAttribute('aria-label','Whitney flow time');
  timeLabel.className='whitney-time';timeLabel.append(output,slider);
  const rotationLabel=document.createElement('label');rotationLabel.textContent='4D rotation';
  const rotation=document.createElement('input');rotation.type='range';rotation.min='0';rotation.max=String(Math.PI/2);rotation.step='.01';rotation.value='.55';rotation.setAttribute('aria-label','Whitney projection rotation in four dimensions');rotationLabel.append(rotation);
  controls.prepend(choice,play,timeLabel);controls.append(rotationLabel);
  const legend=document.createElement('p');legend.className='whitney-legend';
  legend.textContent='Blue and orange mark the two hemispheres. The black dot marks the true double point. Other overlaps can be projection artifacts.';
  stage.after(legend);
  const text=(s,x,y,size=12,color='#476170')=>{ctx.font=`${size}px system-ui, sans-serif`;ctx.fillStyle=color;ctx.fillText(s,x,y);};
  function surface(i,cx,cy,scale){
    const m=mesh(i),q=m.vertices.map(p=>rotatePoint(p,state));
    const sorted=m.faces.map((f,index)=>({f,index,z:f.reduce((v,k)=>v+q[k][2],0)})).sort((a,b)=>a.z-b.z);
    for(const {f,index} of sorted){
      const [a,b,c]=f.map(k=>q[k]),u=b.map((v,k)=>v-a[k]),v=c.map((w,k)=>w-a[k]);
      const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
      const light=.48+.45*Math.abs(.3*n[0]+.5*n[1]+.8*n[2])/(Math.hypot(...n)||1);
      const rgb=(m.groups[index]===0?[43,139,159]:[207,123,70]).map(v=>Math.round(v*light+255*(1-light)*.32));
      ctx.beginPath();f.forEach((k,j)=>j?ctx.lineTo(cx+scale*q[k][0],cy-scale*q[k][1]):ctx.moveTo(cx+scale*q[k][0],cy-scale*q[k][1]));ctx.closePath();
      ctx.fillStyle=`rgb(${rgb})`;ctx.fill();ctx.strokeStyle=wire?'rgba(25,56,67,.3)':ctx.fillStyle;ctx.lineWidth=wire?.5:.25;ctx.stroke();
    }
    ctx.fillStyle='#183f52';ctx.beginPath();ctx.arc(cx,cy,2.5,0,Math.PI*2);ctx.fill();
  }
  function profile(i,cx,cy,scale,axes=true){
    if(axes){ctx.strokeStyle='#d7e1e5';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(cx-1.12*scale,cy);ctx.lineTo(cx+1.12*scale,cy);ctx.moveTo(cx,cy-.45*scale);ctx.lineTo(cx,cy+.45*scale);ctx.stroke();}
    const quarter=data.frames[i].quarter;
    for(const sign of [1,-1])for(const flip of [1,-1]){
      ctx.strokeStyle=flip===1?'#21667f':'#b96934';ctx.lineWidth=2.2;ctx.beginPath();
      quarter.forEach(([a,b],j)=>j?ctx.lineTo(cx+sign*scale*a,cy-sign*flip*scale*b):ctx.moveTo(cx+sign*scale*a,cy-sign*flip*scale*b));ctx.stroke();
    }
    ctx.fillStyle='#183f52';ctx.beginPath();ctx.arc(cx,cy,2.5,0,Math.PI*2);ctx.fill();
  }
  function draw(){
    scheduled=false;
    const {width:w,height:h}=stage.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2);
    canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);
    text('n = 2 · sphere in ℝ⁴ · fixed spatial scale',14,24,w<420?11:13);
    if(mode==='sequence'){
      const cellw=w/2,cellh=(h-40)/2;
      data.snapshots.forEach((i,k)=>{
        const x=(k%2)*cellw,y=36+Math.floor(k/2)*cellh,cx=x+cellw/2;
        ctx.fillStyle='#fff';ctx.fillRect(x+6,y+2,cellw-12,cellh-10);ctx.strokeStyle='#d6e1e6';ctx.lineWidth=1;ctx.strokeRect(x+6,y+2,cellw-12,cellh-10);
        text(`t = ${data.frames[i].t.toFixed(3)}`,x+15,y+22,14,'#183f52');
        text(i===0?'Exact initial data':'Numerical flow',x+15,y+40,10);
        const scale=Math.min(cellw*.38,cellh*.31);
        surface(i,cx,y+cellh*.42,scale);
        text('ℝ⁴ → ℝ³ projection',x+15,y+cellh*.65,10);
        profile(i,cx,y+cellh*.80,Math.min(cellw*.39,cellh*.39));
        text('Generating profile',x+15,y+cellh-17,10);
      });
    }else if(mode==='surface'){
      surface(frame,w/2,h*.53,Math.min(w*.40,h*.36)*state.zoom);
      text('Linear projection ℝ⁴ → ℝ³',14,h-18,12);
    }else{
      const scale=Math.min(w*.42,h*.75)*state.zoom;
      profile(frame,w/2,h*.5,scale);
      text('Re γ',w-55,h*.5+20);text('Im γ',w/2+10,50);
      text('Planar generating curve, not ordinary curve shortening',14,h-18,w<420?10:12);
    }
    canvas.dataset.view=mode;canvas.dataset.time=String(data.frames[frame].t);canvas.dataset.zoom=String(state.zoom);canvas.dataset.mesh=String(wire);canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)},${state.fourD.toFixed(3)}`;
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function stop(){clearInterval(timer);timer=null;play.textContent='Play flow';}
  function sync(){
    choice.value=mode;slider.value=String(frame);output.textContent=mode==='sequence'?'Choose a time':`t = ${data.frames[frame].t.toFixed(3)}`;
    rotationLabel.hidden=mode==='profile';
    figure.querySelector('[data-view-action=wire]').disabled=mode==='profile';
    for(const a of ['in','out'])figure.querySelector(`[data-view-action=${a}]`).disabled=mode==='sequence';
    help.textContent=mode==='sequence'?'Four times on the same spatial scale. Choose a time or play the flow to inspect one surface.':'Drag the surface to rotate; use + / − to zoom. The time control selects computed snapshots. Scaling and camera stay fixed as time changes.';
    status.textContent=mode==='sequence'?'t = 0 is exact initial geometry; later frames are numerical PDE approximations. The last frame is before the singularity, not an estimate of its time.':`${frame===0?'Exact initial geometry':'Numerical PDE snapshot'} at t = ${data.frames[frame].t.toFixed(3)}. ${mode==='profile'?'Either lobe generates the whole sphere; using both would double-cover it.':'Projection of (a cos v, a sin v, b cos v, b sin v), where γ = a + ib.'}`;
    canvas.setAttribute('aria-label',`Whitney sphere ${mode==='sequence'?'time sequence at t = 0, 0.03, 0.06 and 0.09':`${mode} at t = ${data.frames[frame].t.toFixed(3)}`}. Exact initial data; positive times numerical. Surface dimension two, ambient dimension four. Arrow keys rotate, plus and minus zoom.`);
    requestDraw();
  }
  choice.addEventListener('change',()=>{stop();mode=choice.value;state.zoom=1;sync();});
  slider.addEventListener('input',()=>{stop();frame=Number(slider.value);if(mode==='sequence')mode='surface';sync();});
  rotation.addEventListener('input',()=>{state.fourD=Number(rotation.value);requestDraw();});
  play.addEventListener('click',()=>{
    if(timer){stop();return;}
    if(mode==='sequence')mode='surface';if(frame===data.frames.length-1)frame=0;
    play.textContent='Pause flow';sync();
    timer=setInterval(()=>{frame++;if(frame>=data.frames.length-1){frame=data.frames.length-1;stop();}sync();},110);
  });
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  new IntersectionObserver(items=>{if(!items[0].isIntersecting)stop();}).observe(figure);
  function zoom(f){if(mode==='sequence')return;state.zoom=Math.min(5,Math.max(.4,state.zoom*f));requestDraw();}
  for(const button of controls.querySelectorAll('[data-view-action]'))button.addEventListener('click',()=>{
    const a=button.dataset.viewAction;
    if(a==='in')zoom(1.2);if(a==='out')zoom(1/1.2);
    if(a==='wire'){wire=!wire;button.setAttribute('aria-pressed',String(wire));requestDraw();}
    if(a==='reset'){stop();frame=0;mode='sequence';wire=false;state={yaw:.64,pitch:.43,fourD:.55,zoom:1};rotation.value='.55';figure.querySelector('[data-view-action=wire]').setAttribute('aria-pressed','false');sync();}
  });
  canvas.addEventListener('pointerdown',e=>{if(mode!=='surface')return;drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;state.yaw+=(e.clientX-drag[0])*.009;state.pitch+=(e.clientY-drag[1])*.009;drag=[e.clientX,e.clientY];requestDraw();});
  for(const event of ['pointerup','pointercancel'])canvas.addEventListener(event,()=>{drag=null;});
  canvas.addEventListener('keydown',e=>{
    const actions={'+':()=>zoom(1.2),'=':()=>zoom(1.2),'-':()=>zoom(1/1.2)};
    if(mode==='surface')Object.assign(actions,{ArrowLeft:()=>state.yaw-=.12,ArrowRight:()=>state.yaw+=.12,ArrowUp:()=>state.pitch-=.12,ArrowDown:()=>state.pitch+=.12});
    if(actions[e.key]){e.preventDefault();actions[e.key]();requestDraw();}
  });
  canvas.addEventListener('wheel',e=>{if(mode==='sequence'||document.activeElement!==canvas)return;e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  figure.querySelector('img').hidden=true;canvas.hidden=false;controls.hidden=false;help.hidden=false;
  new ResizeObserver(requestDraw).observe(stage);sync();
}
