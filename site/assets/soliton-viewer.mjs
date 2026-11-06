// Original lightweight geometry viewer. No external scripts or telemetry.
export function rotatePoint(p, state) {
  let [x,y,z,w] = p;
  if (w !== undefined) y = y*Math.cos(state.fourD)-w*Math.sin(state.fourD);
  const horizontal=x*Math.cos(state.yaw)-y*Math.sin(state.yaw);
  const depth=x*Math.sin(state.yaw)+y*Math.cos(state.yaw);
  return [horizontal,z*Math.cos(state.pitch)-depth*Math.sin(state.pitch),z*Math.sin(state.pitch)+depth*Math.cos(state.pitch)];
}

export function ancientOval(t, count=240) {
  if (!(t<0)) throw new Error('The smooth oval requires t < 0.');
  const ymax=Math.acosh(Math.exp(-t)), a=[], b=[];
  for (let i=0;i<=count;i++) {
    const y=-ymax+2*ymax*i/count;
    const x=Math.acos(Math.min(1,Math.exp(t)*Math.cosh(y)));
    a.push([x,y,0]);b.push([-x,y,0]);
  }
  return a.concat(b.reverse());
}

function init(figure, data) {
  const canvas=figure.querySelector('canvas'), ctx=canvas.getContext('2d');
  if (!ctx) return;
  const stage=figure.querySelector('.soliton-stage');
  const resetState=()=>({yaw:data.flat?0:.64,pitch:data.flat?-Math.PI/2:.43,zoom:1,fourD:.55});
  let state=resetState(), vertices=data.vertices, dragging=null, wire=false, scheduled=false;
  const lo=[0,1,2].map(i=>Math.min(...vertices.map(p=>p[i])));
  const hi=[0,1,2].map(i=>Math.max(...vertices.map(p=>p[i])));
  const center=lo.map((v,i)=>(v+hi[i])/2);
  // Keep one scale throughout the time slider, including its largest oval.
  const radius=data.dynamic?.kind==='ancient-oval'
    ? Math.hypot(Math.PI/2,Math.acosh(Math.exp(-data.dynamic.min)))
    : Math.max(...vertices.map(p=>Math.hypot(...p.slice(0,3).map((v,i)=>v-center[i]))));
  const centered=()=>vertices.map(p=>p.map((v,i)=>i<3?v-center[i]:v));
  let points=centered();
  function draw() {
    scheduled=false;
    const box=stage.getBoundingClientRect(), width=box.width, height=box.height;
    const dpr=Math.min(window.devicePixelRatio||1,2);
    if(canvas.width!==Math.round(width*dpr)||canvas.height!==Math.round(height*dpr)) {
      canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);
    }
    ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,width,height);
    const scale=Math.min(width*.43,height*.42)/(radius||1)*state.zoom;
    const q=points.map(p=>rotatePoint(p,state));
    const screen=q.map(p=>[width/2+scale*p[0],height/2-scale*p[1]]);
    const faces=data.faces.map(face=>({face,z:face.reduce((v,i)=>v+q[i][2],0)/3})).sort((a,b)=>a.z-b.z);
    for(const {face} of faces) {
      const [a,b,c]=face.map(i=>q[i]);
      const u=b.map((v,i)=>v-a[i]),v=c.map((val,i)=>val-a[i]);
      const normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
      const light=.42+.52*Math.abs((.3*normal[0]+.5*normal[1]+.8*normal[2])/(Math.hypot(...normal)||1));
      const rgb=[67,139,169].map(base=>Math.round(base*light+255*(1-light)*.25));
      ctx.beginPath();face.forEach((i,j)=>j?ctx.lineTo(...screen[i]):ctx.moveTo(...screen[i]));ctx.closePath();
      ctx.fillStyle=`rgb(${rgb.join(',')})`;ctx.fill();
      if(wire){ctx.strokeStyle='rgba(24,63,82,.32)';ctx.lineWidth=.5;ctx.stroke();}
    }
    ctx.strokeStyle='#21667f';ctx.lineWidth=2.5;
    for(const path of data.paths) {
      ctx.beginPath();path.forEach((i,j)=>j?ctx.lineTo(...screen[i]):ctx.moveTo(...screen[i]));ctx.stroke();
    }
    canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;
    canvas.dataset.zoom=state.zoom.toFixed(3);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function zoom(f){state.zoom=Math.max(.35,Math.min(4,state.zoom*f));requestDraw();}
  canvas.addEventListener('pointerdown',e=>{dragging={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!dragging)return;state.yaw+=(e.clientX-dragging.x)*.009;state.pitch+=(e.clientY-dragging.y)*.009;dragging={x:e.clientX,y:e.clientY};requestDraw();});
  canvas.addEventListener('pointerup',()=>{dragging=null;});
  canvas.addEventListener('pointercancel',()=>{dragging=null;});
  // Wheel zoom requires focus: scrolling the reading page remains predictable.
  canvas.addEventListener('wheel',e=>{if(document.activeElement!==canvas)return;e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  canvas.addEventListener('keydown',e=>{
    const keys={ArrowLeft:()=>state.yaw-=.12,ArrowRight:()=>state.yaw+=.12,ArrowUp:()=>state.pitch-=.12,ArrowDown:()=>state.pitch+=.12,'+':()=>zoom(1.15),'=':()=>zoom(1.15),'-':()=>zoom(1/1.15)};
    if(keys[e.key]){e.preventDefault();keys[e.key]();requestDraw();}
  });
  for(const button of figure.querySelectorAll('[data-view-action]')) button.addEventListener('click',()=>{
    const action=button.dataset.viewAction;
    if(action==='in')zoom(1.2);
    if(action==='out')zoom(1/1.2);
    if(action==='reset'){state=resetState();requestDraw();}
    if(action==='wire'){wire=!wire;button.setAttribute('aria-pressed',String(wire));requestDraw();}
  });
  if(vertices[0].length===4){
    const label=document.createElement('label');label.textContent='4D rotation ';
    const input=document.createElement('input');input.type='range';input.min='0';input.max=String(Math.PI/2);input.step='.01';input.value=String(state.fourD);input.setAttribute('aria-label','Rotation in the second and fourth coordinates');
    input.addEventListener('input',()=>{state.fourD=Number(input.value);requestDraw();});label.append(input);figure.querySelector('.soliton-controls').append(label);
  }
  if(data.dynamic?.kind==='ancient-oval'){
    const label=document.createElement('label');const output=document.createElement('output');output.textContent='t = -2.00';
    const input=document.createElement('input');input.type='range';input.min=String(data.dynamic.min);input.max=String(data.dynamic.max);input.step='.02';input.value=String(data.dynamic.value);input.setAttribute('aria-label','Ancient oval time');
    input.addEventListener('input',()=>{const t=Number(input.value);vertices=ancientOval(t);data.paths=[Array.from({length:vertices.length},(_,i)=>i)];points=centered();output.textContent=`t = ${t.toFixed(2)}`;requestDraw();});
    label.append(output,input);figure.querySelector('.soliton-controls').append(label);
  }
  figure.querySelector('.soliton-controls').hidden=false;
  figure.querySelector('.soliton-help').hidden=false;
  figure.querySelector('img').hidden=true;canvas.hidden=false;
  new ResizeObserver(requestDraw).observe(stage);requestDraw();
}

if(typeof document!=='undefined') {
  const start=async figure=>{
    try {const response=await fetch(figure.dataset.soliton);if(!response.ok)throw new Error('geometry unavailable');init(figure,await response.json());}
    catch {figure.querySelector('.soliton-status').textContent='The static drawing is shown; interactive geometry is unavailable.';}
  };
  const figures=[...document.querySelectorAll('[data-soliton]')];
  if('IntersectionObserver'in window){const observer=new IntersectionObserver(items=>{for(const item of items)if(item.isIntersecting){observer.unobserve(item.target);start(item.target);}},{rootMargin:'250px'});figures.forEach(f=>observer.observe(f));}
  else figures.forEach(start);
}
