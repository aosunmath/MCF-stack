// Original qualitative model. The stage parameter is NOT MCF time.
export const ANNULUS = Object.freeze({height:1.1, neck:.72, decay:3.2, slope:1.2, radius:5});
export function neckRadius(stage) {
  if (!Number.isFinite(stage) || stage<0 || stage>1) throw new Error('Stage must lie in [0,1].');
  return ANNULUS.neck*Math.exp(-ANNULUS.decay*stage);
}
export function profileHeight(radius, stage) {
  const a=neckRadius(stage);
  if(radius<a)throw new Error('The radial graph starts at the neck.');
  return ANNULUS.height*Math.tanh(ANNULUS.slope*a*Math.acosh(radius/a)/ANNULUS.height);
}
export function annulusGeometry(stage, rows=72, sectors=64) {
  const a=neckRadius(stage),vmax=Math.acosh(ANNULUS.radius/a),vertices=[],faces=[],groups=[],paths=[];
  for(let i=0;i<=rows;i++){
    const v=vmax*(2*i/rows-1),r=a*Math.cosh(v),z=ANNULUS.height*Math.tanh(ANNULUS.slope*a*v/ANNULUS.height);
    for(let j=0;j<sectors;j++){const t=2*Math.PI*j/sectors;vertices.push([r*Math.cos(t),r*Math.sin(t),z]);}
  }
  for(let i=0;i<rows;i++)for(let j=0;j<sectors;j++){
    const a=i*sectors+j,b=i*sectors+(j+1)%sectors,c=b+sectors,d=a+sectors;
    faces.push([a,b,c],[a,c,d]);groups.push(i<rows/2?0:1,i<rows/2?0:1);
  }
  for(const row of [0,rows/2,rows])paths.push(Array.from({length:sectors+1},(_,j)=>row*sectors+j%sectors));
  return {vertices,faces,paths,faceGroups:groups,sectors,rows};
}
// Parametrize by height to resolve the far ends after compressing r to r/(r+R).
export function compactMeridian(stage,count=240) {
  const a=neckRadius(stage),points=[];
  for(let i=0;i<count;i++){
    const z=ANNULUS.height*i/count,v=ANNULUS.height*Math.atanh(z/ANNULUS.height)/(ANNULUS.slope*a);
    const logR=Math.log(a)+v+Math.log1p(Math.exp(-2*v))-Math.LN2;
    points.push([1/(1+ANNULUS.radius*Math.exp(-logR)),z]);
  }
  points.push([1,ANNULUS.height]); // asymptotic endpoint, not a finite surface point
  return points;
}
export function initImmortalAnnulus(figure,data,rotatePoint) {
  const canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d');
  if(!ctx)throw new Error('Canvas unavailable');
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  const status=figure.querySelector('.soliton-status'),help=figure.querySelector('.soliton-help');
  figure.classList.add('annulus-figure');
  const defaults=()=>({yaw:.5,pitch:.24,zoom:1,cutaway:true,wire:false,limit:false,progress:0});
  let state=defaults(),geometry=annulusGeometry(0),drag=null,scheduled=false,playing=false,last=0,frame=0;
  const sequence=document.createElement('div');sequence.className='annulus-sequence';
  const label=document.createElement('label');label.textContent='Earlier → later ';
  const slider=document.createElement('input');slider.type='range';slider.min='0';slider.max='1';slider.step='.005';slider.value='0';slider.setAttribute('aria-label','Illustrated finite-time stage');label.append(slider);
  const makeButton=(text,fn)=>{const b=document.createElement('button');b.type='button';b.textContent=text;b.addEventListener('click',fn);sequence.append(b);return b;};
  sequence.append(label);
  const play=makeButton('Play stages',()=>{if(playing)stop();else{state.limit=false;if(state.progress>=1)state.progress=0;playing=true;last=0;play.textContent='Pause';frame=requestAnimationFrame(animate);sync();}});
  const presets=[['Earlier',0],['Middle',.5],['Later',1]].map(([name,p])=>makeButton(name,()=>{stop();setStage(p);}));
  const limit=makeButton('Limit t → ∞',()=>{stop();state.limit=!state.limit;sync();});
  controls.prepend(sequence);
  const cut=document.createElement('button');cut.type='button';cut.textContent='Cutaway';controls.append(cut);
  cut.addEventListener('click',()=>{state.cutaway=!state.cutaway;sync();});
  function stop(){playing=false;cancelAnimationFrame(frame);play.textContent='Play stages';}
  function setStage(p){state.progress=p;state.limit=false;geometry=annulusGeometry(p);sync();}
  function animate(now){if(!playing)return;if(last)state.progress=Math.min(1,state.progress+(now-last)/10000);last=now;setStage(state.progress);if(state.progress>=1)stop();else frame=requestAnimationFrame(animate);}
  slider.addEventListener('input',()=>{stop();setStage(Number(slider.value));});
  function line(points,color,width=1,dash=[]){ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.stroke();ctx.setLineDash([]);}
  function draw(){
    scheduled=false;
    const box=stage.getBoundingClientRect(),w=box.width,h=box.height,dpr=Math.min(window.devicePixelRatio||1,2);
    if(!w||!h)return;
    canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);
    ctx.fillStyle='#f7fafb';ctx.fillRect(0,0,w,h);
    const surfaceH=h-205,scale=Math.min(w*.43/ANNULUS.radius,(surfaceH-55)*.43/2.1)*state.zoom;
    const project=p=>{const q=rotatePoint(p,state);return [w/2+q[0]*scale,surfaceH/2+15-q[1]*scale,q[2]];};
    ctx.save();ctx.beginPath();ctx.rect(0,35,w,surfaceH-35);ctx.clip();
    if(state.limit){
      const disk=Array.from({length:129},(_,i)=>project([5*Math.cos(i*Math.PI/64),5*Math.sin(i*Math.PI/64),0]));
      ctx.beginPath();disk.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.fillStyle='#b5ced5';ctx.fill();line(disk,'#436c7d',1.5);
      for(const y of [-3,-1,1,3]){const x=Math.sqrt(25-y*y);line([project([-x,y,0]),project([x,y,0])],'#759ca9',.7);}
    }else{
      const q=geometry.vertices.map(project);
      const faces=geometry.faces.map((f,i)=>({f,i,depth:f.reduce((s,j)=>s+q[j][2],0)/3})).filter(({f})=>!state.cutaway||f.every(i=>geometry.vertices[i][1]>=-1e-8)).sort((a,b)=>a.depth-b.depth);
      for(const {f,i} of faces){
        const [a,b,c]=f.map(j=>q[j]),u=b.map((v,j)=>(v-a[j])/(j<2?scale:1)),v=c.map((x,j)=>(x-a[j])/(j<2?scale:1));
        const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
        const light=.54+.44*Math.abs((n[0]*.3-n[1]*.5+n[2]*.8)/(Math.hypot(...n)||1));
        const rgb=(geometry.faceGroups[i]?[79,148,170]:[215,151,88]).map(x=>Math.round(x*light+255*(1-light)*.16));
        ctx.beginPath();f.forEach((j,k)=>k?ctx.lineTo(q[j][0],q[j][1]):ctx.moveTo(q[j][0],q[j][1]));ctx.closePath();ctx.fillStyle=`rgb(${rgb})`;ctx.fill();ctx.strokeStyle=state.wire?'#42616d60':ctx.fillStyle;ctx.lineWidth=state.wire?.5:.45;ctx.stroke();
      }
      for(const path of geometry.paths.filter((_,i)=>state.cutaway||i!==1)){let segment=[];for(const i of path){if(!state.cutaway||geometry.vertices[i][1]>=-1e-8)segment.push(q[i]);else if(segment.length){line(segment,'#315b6a',1);segment=[];}}if(segment.length)line(segment,'#315b6a',1);}
      if(state.cutaway)for(const j of [0,geometry.sectors/2])line(Array.from({length:geometry.rows+1},(_,i)=>q[i*geometry.sectors+j]),'#315b6a',1.5);
    }
    ctx.restore();ctx.font='13px system-ui';ctx.fillStyle='#294f60';
    ctx.fillText(state.limit?(w<450?'Limit t → ∞ · multiplicity 2':'Infinite-time local limit · one plane, multiplicity 2'):`${state.progress<.25?'Earlier':state.progress<.75?'Intermediate':'Later'} ${w<450?'stage':'finite stage'} · schematic`,14,23);
    ctx.fillStyle='#58717d';ctx.font='12px system-ui';ctx.fillText(state.limit?(w<450?'Plane truncated for display.':'The disk edge is a display truncation.'):(w<450?`${state.cutaway?'Cutaway':'Full surface'} · fixed scale`:`${state.cutaway?'Half removed to expose the neck':'Full rotational surface'} · fixed viewing scale`),14,surfaceH-8);
    const top=surfaceH+34,mid=top+62,left=36,right=w-37,span=right-left,ys=49/ANNULUS.height;
    line([[0,surfaceH],[w,surfaceH]],'#d8e4e9');
    ctx.fillStyle='#294f60';ctx.font='13px system-ui';ctx.fillText(w<450?'Profile · compressed radius':'Profile · radius compressed to show the far ends',14,surfaceH+23);
    ctx.fillStyle='#e7eff2';ctx.fillRect(left,top+5,span*.5,114);
    for(const [z,name] of [[ANNULUS.height,'+h'],[0,'0'],[-ANNULUS.height,'−h']]){line([[left,mid-z*ys],[right,mid-z*ys]],'#93a8b2',1,[4,4]);ctx.fillStyle='#58717d';ctx.font='11px system-ui';ctx.fillText(name,9,mid-z*ys+4);}
    line([[left,top+5],[left,top+119]],'#93a8b2');
    if(state.limit){line([[left,mid],[right,mid]],'#21667f',4);ctx.fillStyle='#294f60';ctx.fillText('× 2',left+span*.3,mid-10);}
    else for(const sign of [-1,1])line(compactMeridian(state.progress).map(([x,z])=>[left+x*span,mid-sign*z*ys]),sign>0?'#21667f':'#b7763c',2.3);
    ctx.fillStyle='#58717d';ctx.font='11px system-ui';ctx.fillText('0',left-3,top+134);ctx.fillText('R',left+span*.5-4,top+134);ctx.fillText('∞',right-5,top+134);
    ctx.font='12px system-ui';ctx.fillText(state.limit?(w<450?'Local limit; not a finite-time slice.':'Local convergence; the limit is not a finite-time slice.'):(w<450?'Shaded: local view; ends → ±h.':'Shaded: displayed radius. Far ends still approach ±h.'),14,h-13);
    canvas.dataset.stage=String(state.progress);canvas.dataset.limit=String(state.limit);canvas.dataset.cutaway=String(state.cutaway);canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;canvas.dataset.zoom=state.zoom.toFixed(3);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function sync(){
    slider.value=String(state.progress);slider.disabled=state.limit;
    presets.forEach((b,i)=>b.setAttribute('aria-pressed',String(!state.limit&&Math.abs(state.progress-i*.5)<.001)));
    limit.setAttribute('aria-pressed',String(state.limit));cut.setAttribute('aria-pressed',String(state.cutaway));cut.disabled=state.limit;
    figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed',String(state.wire));
    status.textContent=state.limit?'At t → ∞: the neck disappears and the two local sheets coincide. Multiplicity is shown as a count, not as two separated planes.':'Every displayed finite stage has a positive neck radius. The slider orders illustrative shapes; it specifies no physical times or convergence rate.';
    canvas.setAttribute('aria-label',state.limit?'Local infinite-time limit: one plane counted twice.':'Schematic immortal annulus at an ordered finite-time stage, with a positive neck and two asymptotically planar ends. Drag or arrow keys rotate; plus and minus zoom.');
    requestDraw();
  }
  function zoom(f){state.zoom=Math.max(.5,Math.min(5,state.zoom*f));requestDraw();}
  for(const b of figure.querySelectorAll('[data-view-action]'))b.addEventListener('click',()=>{
    const action=b.dataset.viewAction;if(action==='in')zoom(1.2);if(action==='out')zoom(1/1.2);
    if(action==='wire'){state.wire=!state.wire;sync();}
    if(action==='reset'){stop();state=defaults();geometry=annulusGeometry(0);drag=null;sync();}
  });
  canvas.addEventListener('pointerdown',e=>{if(e.offsetY>stage.clientHeight-205)return;drag={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;state.yaw+=(e.clientX-drag.x)*.009;state.pitch+=(e.clientY-drag.y)*.009;drag={x:e.clientX,y:e.clientY};requestDraw();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>{drag=null;});
  canvas.addEventListener('keydown',e=>{const actions={ArrowLeft:()=>state.yaw-=.12,ArrowRight:()=>state.yaw+=.12,ArrowUp:()=>state.pitch-=.12,ArrowDown:()=>state.pitch+=.12,'+':()=>zoom(1.2),'=':()=>zoom(1.2),'-':()=>zoom(1/1.2)};if(actions[e.key]){e.preventDefault();actions[e.key]();requestDraw();}});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  new ResizeObserver(requestDraw).observe(stage);
  help.textContent='Drag the surface to rotate; use Zoom + / − or the arrow keys. Blue and ochre distinguish the upper and lower portions of one connected surface. The profile uses a compressed radial axis; its heights are not exaggerated.';
  controls.hidden=false;help.hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;sync();
}
