// Original lightweight geometry viewer. No external scripts or telemetry.
import {abreschLanger,ABRESCH_LANGER_LIMIT} from './abresch-langer.mjs';
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

// A cutaway removes angular sectors without modifying the solved meridian.
export function revolutionFaces(data, degrees) {
  if (!data.revolution) return data.faces.map((face,index)=>({face,index}));
  const count=Math.round(Math.max(0,Math.min(360,degrees))*data.revolution.segments/360);
  return data.faces.map((face,index)=>({face,index})).filter(({index})=>data.revolution.faceSectors[index]<count);
}

export function explicitCurve(kind,t,count=600) {
  if(!['torus-curve','helix'].includes(kind))throw new Error('Unknown curve family');
  if(kind==='torus-curve'&&!(t<0))throw new Error('Ancient torus curves require t < 0.');
  let lo=0,hi=Math.max(1,Math.sqrt(Math.max(0,kind==='torus-curve'?-2*t:1-2*t)));
  for(let j=0;j<90;j++){
    const r=(lo+hi)/2;
    const f=kind==='torus-curve'?r*r+r**8+2*t:Math.log(r)+r*r/2-.5+t;
    if(f>0)hi=r;else lo=r;
  }
  const r=(lo+hi)/2;
  return Array.from({length:count+1},(_,i)=>{
    if(kind==='torus-curve'){const a=2*Math.PI*i/count;return [r*Math.cos(a),r*Math.sin(a),r**4*Math.cos(2*a),r**4*Math.sin(2*a)];}
    const s=-2.5*Math.PI+5*Math.PI*i/count;return [r*Math.cos(s),r*Math.sin(s),s];
  });
}

function init(figure, data) {
  const canvas=figure.querySelector('canvas'), ctx=canvas.getContext('2d');
  if (!ctx) return;
  const stage=figure.querySelector('.soliton-stage');
  let viewLabel;
  if(data.viewLabel){
    viewLabel=document.createElement('p');viewLabel.className='soliton-view-label';
    viewLabel.textContent=data.viewLabel;stage.append(viewLabel);
  }
  const resetState=()=>({yaw:data.flat?0:.64,pitch:data.flat?-Math.PI/2:(data.view?.pitch??.43),zoom:1,fourD:.55});
  let state=resetState(), vertices=data.vertices, dragging=null, wire=false, scheduled=false;
  let degrees=data.revolution?.degrees??360, meridian=false;
  let visibleFaces=revolutionFaces(data,degrees), resetRevolution=()=>{};
  const lo=[0,1,2].map(i=>Math.min(...vertices.map(p=>p[i])));
  const hi=[0,1,2].map(i=>Math.max(...vertices.map(p=>p[i])));
  let center=lo.map((v,i)=>(v+hi[i])/2);
  // Keep one scale throughout the time slider, including its largest oval.
  let radius=data.view?.radius ?? (data.dynamic?.kind==='ancient-oval'
    ? Math.hypot(Math.PI/2,Math.acosh(Math.exp(-data.dynamic.min)))
    : Math.max(...vertices.map(p=>Math.hypot(...p.slice(0,3).map((v,i)=>v-center[i])))));
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
    let scale=Math.min(width*.43/((data.view?.horizontalRadius??radius)||1),height*.42/(radius||1))*state.zoom;
    if(meridian){
      const curve=data.revolution.meridian;
      const rmax=Math.max(...curve.map(p=>p[0])),zmax=Math.max(...curve.map(p=>Math.abs(p[1])));
      scale=Math.min(width*.78/rmax,height*.7/(2*zmax))*state.zoom;
      const screen=([r,z])=>[width/2+scale*(r-rmax/2),height/2-scale*z];
      ctx.strokeStyle='#8a9fa9';ctx.lineWidth=1;ctx.setLineDash([4,4]);
      for(const line of [[[0,-zmax*1.12],[0,zmax*1.12]],[[0,0],[rmax*1.08,0]]]){
        ctx.beginPath();ctx.moveTo(...screen(line[0]));ctx.lineTo(...screen(line[1]));ctx.stroke();
      }
      ctx.setLineDash([]);
      const mid=(curve.length-1)/2;
      for(const [piece,color] of [[curve.slice(0,mid+1),'#21667f'],[curve.slice(mid),'#af673b']]){
        ctx.strokeStyle=color;ctx.lineWidth=2.5;ctx.beginPath();
        piece.forEach((p,i)=>i?ctx.lineTo(...screen(p)):ctx.moveTo(...screen(p)));ctx.stroke();
      }
      ctx.fillStyle='#183f52';ctx.font='13px sans-serif';
      ctx.fillText('Height z',12,22);ctx.fillText('Radius r',width-65,height-15);
      canvas.dataset.view='meridian';canvas.dataset.zoom=state.zoom.toFixed(3);
      return;
    }
    const q=points.map(p=>rotatePoint(p,state));
    const screen=q.map(p=>[width/2+scale*p[0],height/2-scale*p[1]]);
    const faces=visibleFaces.map(({face,index})=>({face,index,z:face.reduce((v,i)=>v+q[i][2],0)/3})).sort((a,b)=>a.z-b.z);
    for(const {face,index} of faces) {
      const [a,b,c]=face.map(i=>q[i]);
      const u=b.map((v,i)=>v-a[i]),v=c.map((val,i)=>val-a[i]);
      const normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
      const light=.42+.52*Math.abs((.3*normal[0]+.5*normal[1]+.8*normal[2])/(Math.hypot(...normal)||1));
      const rgb=(data.palette?.[data.faceGroups?.[index]]??[67,139,169]).map(base=>Math.round(base*light+255*(1-light)*.25));
      ctx.beginPath();face.forEach((i,j)=>j?ctx.lineTo(...screen[i]):ctx.moveTo(...screen[i]));ctx.closePath();
      ctx.fillStyle=`rgb(${rgb.join(',')})`;ctx.fill();
      // Cover antialias seams between adjacent triangles in the cutaway mesh.
      if(data.revolution&&!wire){ctx.strokeStyle=ctx.fillStyle;ctx.lineWidth=data.view?.seamWidth??.4;ctx.stroke();}
      if(wire){ctx.strokeStyle='rgba(24,63,82,.32)';ctx.lineWidth=.5;ctx.stroke();}
    }
    ctx.strokeStyle='#21667f';ctx.lineWidth=2.5;
    for(const path of data.paths) {
      ctx.beginPath();path.forEach((i,j)=>j?ctx.lineTo(...screen[i]):ctx.moveTo(...screen[i]));ctx.stroke();
    }
    canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;
    canvas.dataset.zoom=state.zoom.toFixed(3);
    canvas.dataset.view='surface';canvas.dataset.revolution=String(degrees);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function zoom(f){state.zoom=Math.max(.35,Math.min(4,state.zoom*f));requestDraw();}
  canvas.addEventListener('pointerdown',e=>{if(meridian)return;dragging={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!dragging)return;state.yaw+=(e.clientX-dragging.x)*.009;state.pitch+=(e.clientY-dragging.y)*.009;dragging={x:e.clientX,y:e.clientY};requestDraw();});
  canvas.addEventListener('pointerup',()=>{dragging=null;});
  canvas.addEventListener('pointercancel',()=>{dragging=null;});
  // Wheel zoom requires focus: scrolling the reading page remains predictable.
  canvas.addEventListener('wheel',e=>{if(document.activeElement!==canvas)return;e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  canvas.addEventListener('keydown',e=>{
    if(meridian&&e.key.startsWith('Arrow'))return;
    const keys={ArrowLeft:()=>state.yaw-=.12,ArrowRight:()=>state.yaw+=.12,ArrowUp:()=>state.pitch-=.12,ArrowDown:()=>state.pitch+=.12,'+':()=>zoom(1.15),'=':()=>zoom(1.15),'-':()=>zoom(1/1.15)};
    if(keys[e.key]){e.preventDefault();keys[e.key]();requestDraw();}
  });
  for(const button of figure.querySelectorAll('[data-view-action]')) button.addEventListener('click',()=>{
    const action=button.dataset.viewAction;
    if(action==='in')zoom(1.2);
    if(action==='out')zoom(1/1.2);
    if(action==='reset'){state={...resetState(),fourD:state.fourD};resetRevolution();requestDraw();}
    if(action==='wire'){wire=!wire;button.setAttribute('aria-pressed',String(wire));requestDraw();}
  });
  if(data.name==='abresch-langer'){
    const controls=figure.querySelector('.soliton-controls');
    const form=document.createElement('form');form.className='al-controls';form.noValidate=true;
    const makeInput=(text,value,name)=>{
      const label=document.createElement('label');label.textContent=text;
      const input=document.createElement('input');input.type='number';input.min='1';input.max=String(ABRESCH_LANGER_LIMIT);input.step='1';input.value=String(value);input.required=true;
      input.setAttribute('aria-label',name);label.append(input);form.append(label);return input;
    };
    const mInput=makeInput('m (turning number)',2,'m, turning number');
    const ellInput=makeInput('ℓ (curvature periods)',3,'ell, curvature periods');
    const submit=document.createElement('button');submit.type='submit';submit.textContent='Draw curve';form.append(submit);
    const examples=document.createElement('div');examples.className='al-presets';
    const title=document.createElement('span');title.textContent='Try:';examples.append(title);
    const status=figure.querySelector('.soliton-status');
    let currentM=2,currentEll=3;
    const update=()=>{
      try{
        const m=mInput.valueAsNumber,ell=ellInput.valueAsNumber,result=abreschLanger(m,ell);
        vertices=result.vertices;data.paths=[Array.from({length:vertices.length},(_,i)=>i)];
        center=[0,0,0];radius=vertices.reduce((r,p)=>Math.max(r,Math.hypot(...p)),0);
        points=centered();state=resetState();currentM=m;currentEll=ell;
        canvas.dataset.m=String(m);canvas.dataset.ell=String(ell);
        canvas.dataset.closureError=String(result.closureError);
        canvas.setAttribute('aria-label',`Numerical Abresch–Langer curve with turning number ${m} and ${ell} curvature periods. Arrow keys rotate; plus and minus zoom.`);
        status.textContent=`Showing (m, ℓ) = (${m}, ${ell}). Numerical closing gap: ${result.closureError.toExponential(1)}; not a certified error bound.`;
        status.classList.remove('soliton-error');mInput.removeAttribute('aria-invalid');ellInput.removeAttribute('aria-invalid');
        requestDraw();
      }catch(error){
        status.textContent=`${error.message} Still showing (${currentM}, ${currentEll}).`;
        status.classList.add('soliton-error');mInput.setAttribute('aria-invalid','true');ellInput.setAttribute('aria-invalid','true');
      }
    };
    form.addEventListener('submit',event=>{event.preventDefault();update();});
    for(const [m,ell] of [[2,3],[3,5],[5,8],[12,17]]){
      const button=document.createElement('button');button.type='button';button.textContent=`(${m}, ${ell})`;
      button.setAttribute('aria-label',`Draw m ${m}, ell ${ell}`);
      button.addEventListener('click',()=>{mInput.value=String(m);ellInput.value=String(ell);update();});examples.append(button);
    }
    const hint=document.createElement('p');hint.className='al-hint';
    hint.textContent='Use coprime positive integers with 1/2 < m/ℓ < 1/√2. This viewer supports indices up to 100. “Open drawing” shows the fixed (2, 3) reference.';
    controls.prepend(form,status,examples,hint);update();
  }
  if(data.revolution){
    const controls=figure.querySelector('.soliton-controls');
    const button=document.createElement('button');button.type='button';button.textContent='Meridian';button.setAttribute('aria-pressed','false');
    const label=document.createElement('label'),output=document.createElement('output'),input=document.createElement('input');
    input.type='range';input.min='90';input.max='360';input.step=String(360/data.revolution.segments);
    input.setAttribute('aria-label','Revolution angle');
    const help=figure.querySelector('.soliton-help');
    const sync=()=>{
      button.setAttribute('aria-pressed',String(meridian));input.disabled=meridian;
      input.value=String(degrees);output.textContent=`Revolve: ${degrees}°`;
      visibleFaces=revolutionFaces(data,degrees);
      help.textContent=meridian
        ? (data.revolution.meridianHelp??'Generating curve in the (r, z) half-plane. Blue: shot from the upper pole. Orange: reflected continuation. Zoom buttons remain active.')
        : (data.revolution.surfaceHelp??'Drag to rotate; + / − zoom. The angle control removes sectors to reveal the sheets; cut edges are display boundaries. Meridian shows the generating curve.');
      if(viewLabel)viewLabel.textContent=meridian?(data.revolution.meridianLabel??data.viewLabel):data.viewLabel;
    };
    input.addEventListener('input',()=>{degrees=Number(input.value);sync();requestDraw();});
    button.addEventListener('click',()=>{meridian=!meridian;dragging=null;state.zoom=1;sync();requestDraw();});
    resetRevolution=()=>{meridian=false;degrees=data.revolution.degrees;sync();};
    label.append(output,input);controls.append(button,label);sync();
  }
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
  if(['torus-curve','helix'].includes(data.dynamic?.kind)){
    const label=document.createElement('label'),output=document.createElement('output');
    output.textContent=`t = ${data.dynamic.value.toFixed(2)}`;
    const input=document.createElement('input');input.type='range';input.min=String(data.dynamic.min);input.max=String(data.dynamic.max);input.step='.01';input.value=String(data.dynamic.value);
    input.setAttribute('aria-label',data.dynamic.kind==='helix'?'Eternal helix time':'Ancient torus curve time');
    input.addEventListener('input',()=>{const t=Number(input.value);vertices=explicitCurve(data.dynamic.kind,t);points=centered();output.textContent=`t = ${t.toFixed(2)}`;canvas.dataset.time=String(t);requestDraw();});
    label.append(output,input);figure.querySelector('.soliton-controls').append(label);
  }
  figure.querySelector('.soliton-controls').hidden=false;
  figure.querySelector('.soliton-help').hidden=false;
  figure.querySelector('img').hidden=true;canvas.hidden=false;
  new ResizeObserver(requestDraw).observe(stage);requestDraw();
}

if(typeof document!=='undefined') {
  const start=async figure=>{
    try {const response=await fetch(figure.dataset.soliton);if(!response.ok)throw new Error('geometry unavailable');const data=await response.json();
      if(data.kind==='apex-translators'){
        const {initApexFigure}=await import('./apex-viewer.mjs');
        initApexFigure(figure,data);
      } else if(data.kind==='delta-wing-pde'){
        const {initDeltaWingFigure}=await import('./delta-wing-viewer.mjs');
        initDeltaWingFigure(figure,data);
      } else if(data.kind==='moller-configuration'){
        const {initMollerFigure}=await import('./moller-viewer.mjs');
        initMollerFigure(figure,data,rotatePoint);
      } else if(data.kind==='moller-genus-model'){
        const {initMollerGenusFigure}=await import('./moller-genus-viewer.mjs');
        initMollerGenusFigure(figure,data);
      } else if(data.construction?.kind==='kkm'){
        const {initKKMFigure}=await import('./kkm-viewer.mjs');
        initKKMFigure(figure,data,rotatePoint);
      } else if(data.kind==='hmw-three-ended-schematic'){
        const {initHmwThreeFigure}=await import('./hmw-three-ended-viewer.mjs');
        initHmwThreeFigure(figure,data);
      } else if(data.kind==='hmw-sphere-plane-schematic'){
        const {initHmwFigure}=await import('./hmw-sphere-plane-viewer.mjs');
        initHmwFigure(figure,data);
      } else if(data.kind==='bns-schematic'){
        const {initBnsFigure}=await import('./bns-viewer.mjs');
        initBnsFigure(figure,data);
      } else if(data.kind==='ketover-schematic'){
        const {initKetoverFigure}=await import('./ketover-viewer.mjs');
        initKetoverFigure(figure,data);
      } else if(data.kind==='iw-schematic'){
        const {initIWFigure}=await import('./iw-viewer.mjs');
        initIWFigure(figure,data);
      } else if(data.kind==='trident-schematic'){
        const {initTridentFigure}=await import('./trident-viewer.mjs');
        initTridentFigure(figure,data);
      } else if(data.kind==='nguyen-scherk-schematic'){
        const {initNguyenFigure}=await import('./nguyen-viewer.mjs');
        initNguyenFigure(figure,data);
      } else if(data.kind==='shao-zou-schematic'){
        const {initShaoZouFigure}=await import('./shao-zou-viewer.mjs');
        initShaoZouFigure(figure,data);
      } else if(data.kind==='hmw-ray-schematic'){
        const {initHMWFigure}=await import('./hmw-rays-viewer.mjs');
        initHMWFigure(figure,data);
      } else if(data.kind==='platonic-doubling-schematic'){
        const {initPlatonicFigure}=await import('./platonic-viewer.mjs');
        initPlatonicFigure(figure,data);
      } else if(data.kind==='spherical-doubling-schematic'){
        const {initSphericalDoublingFigure}=await import('./spherical-doubling-viewer.mjs');
        initSphericalDoublingFigure(figure,data);
      } else init(figure,data);}
    catch {figure.querySelector('.soliton-status').textContent='The static drawing is shown; interactive geometry is unavailable.';}
  };
  const figures=[...document.querySelectorAll('[data-soliton]')];
  if('IntersectionObserver'in window){const observer=new IntersectionObserver(items=>{for(const item of items)if(item.isIntersecting){observer.unobserve(item.target);start(item.target);}},{rootMargin:'250px'});figures.forEach(f=>observer.observe(f));}
  else figures.forEach(start);
}
