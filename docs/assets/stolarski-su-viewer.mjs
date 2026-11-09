// Stolarski–Su, arXiv:2607.03152v1, Theorem 1.1 and §2.2.
// Exact stationary Lawlor profiles; their prescribed shrinking scale is ONLY
// an asymptotic illustration. The parabolic correction has not been solved.
export const SS = Object.freeze({radius:2.5,a0:.7,times:[0,.6,.9],source:'https://arxiv.org/abs/2607.03152v1'});
export function validCase(n,k){return Number.isInteger(n)&&Number.isInteger(k)&&n>=3&&k>=2&&(n>3||k<=4);}
export function neckScale(t,k,view='physical',n=3){
  if(!validCase(n,k)||!Number.isFinite(t)||t<0||t>=1||!['physical','parabolic','neck'].includes(view))throw new RangeError('Require an allowed (n,K), 0 ≤ normalized time < 1, and a known scale.');
  return SS.a0*(1-t)**(view==='physical'?k/2:view==='parabolic'?(k-1)/2:0);
}
// w = a (1 + i sinh(v))^(1/n), principal root. Re(w^n) = a^n.
// This is the paper's gamma after the fixed unitary rotation exp(-i*pi/(2n)).
export function lawlorPoint(n,a,v){
  if(!Number.isInteger(n)||n<3||!(a>0)||!Number.isFinite(a)||!Number.isFinite(v))throw new RangeError('Invalid Lawlor profile parameters.');
  const r=a*Math.cosh(v)**(1/n),theta=Math.atan(Math.sinh(v))/n;
  return [r*Math.cos(theta),r*Math.sin(theta)];
}
export function profile(n,a,count=120,radius=SS.radius){
  if(!(radius>a)||!Number.isInteger(count)||count<2||count%2)throw new RangeError('Require an even sample count and radius > neck size.');
  const vmax=Math.acosh((radius/a)**n);
  return Array.from({length:count+1},(_,i)=>lawlorPoint(n,a,vmax*(2*i/count-1)));
}
export function slicePoint(w,phi){return [w[0]*Math.cos(phi),w[0]*Math.sin(phi),w[1]*Math.cos(phi),w[1]*Math.sin(phi)];}
export function neckMesh(n,a,rings=60,sectors=48){
  const curve=profile(n,a,rings),vertices=[],faces=[],groups=[];
  for(const w of curve)for(let j=0;j<sectors;j++)vertices.push(slicePoint(w,2*Math.PI*j/sectors));
  const at=(i,j)=>i*sectors+(j%sectors);
  for(let i=0;i<rings;i++)for(let j=0;j<sectors;j++){
    faces.push([at(i,j),at(i+1,j),at(i+1,j+1)],[at(i,j),at(i+1,j+1),at(i,j+1)]);
    groups.push(i<rings/2?0:1,i<rings/2?0:1);
  }
  return {vertices,faces,groups};
}
export const defaultCamera=()=>({yaw:1.1,pitch:.12,projection:.30,zoom:1,cutaway:true});
export function project4(p,state){
  // Orthogonal projection after rotating the (Re z2, Im z2) plane.
  const [x,y,z,w]=p,Y=y*Math.cos(state.projection)-w*Math.sin(state.projection);
  const h=x*Math.cos(state.yaw)-Y*Math.sin(state.yaw),d=x*Math.sin(state.yaw)+Y*Math.cos(state.yaw);
  return [h,z*Math.cos(state.pitch)-d*Math.sin(state.pitch),z*Math.sin(state.pitch)+d*Math.cos(state.pitch)];
}
export function surfaceScene(n,a,box,state=defaultCamera(),quality=[60,48]){
  const mesh=neckMesh(n,a,...quality),q=mesh.vertices.map(p=>project4(p,state));
  const scale=Math.min(box.w*.45/SS.radius,box.h*.43/(SS.radius*.8))*state.zoom;
  const screen=p=>[box.x+box.w/2+scale*p[0],box.y+box.h/2-scale*p[1]];
  const polygons=mesh.faces.map((face,i)=>{
    if(state.cutaway&&Math.floor(i/2)%quality[1]>=quality[1]/2)return null;
    const [a,b,c]=face.map(j=>q[j]),u=b.map((v,j)=>v-a[j]),v=c.map((w,j)=>w-a[j]);
    const normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
    const light=.53+.44*Math.abs((.2*normal[0]+.4*normal[1]+.89*normal[2])/(Math.hypot(...normal)||1));
    const base=mesh.groups[i]?[197,121,66]:[42,128,159];
    return {points:face.map(j=>screen(q[j])),depth:(a[2]+b[2]+c[2])/3,color:`rgb(${base.map(c=>Math.round(c*light+245*(1-light))).join(',')})`};
  }).filter(Boolean).sort((a,b)=>a.depth-b.depth);
  return {polygons,scale,project:p=>screen(project4(p,state))};
}

export function initStolarskiSu(figure){
  const canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d');if(!ctx)return;
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  const status=figure.querySelector('.soliton-status'),help=figure.querySelector('.soliton-help');
  figure.classList.add('stolarski-figure');
  let n=3,k=2,t=0,view='compare',scaleMode='physical',state=defaultCamera(),wire=false,drag=null,queued=false,playing=false,frame=0,last=0;
  const make=(tag,text)=>{const el=document.createElement(tag);if(text)el.textContent=text;return el;};
  function select(label,options){const wrap=make('label',label+' '),el=make('select');el.setAttribute('aria-label','Stolarski–Su '+label.toLowerCase());for(const [value,text]of options){const o=make('option',text);o.value=value;el.append(o);}wrap.append(el);controls.append(wrap);return el;}
  const viewSelect=select('View',[['compare','Compare times'],['slice','Explore a time'],['profile','Planar profile']]);
  const scaleSelect=select('Scale',[['physical','Physical'],['parabolic','Parabolic zoom'],['neck','Neck zoom']]);
  const nSelect=select('Dimension n',[3,4,5,6].map(v=>[v,String(v)]));
  const kSelect=select('Rate K',[2,3,4,5,6].map(v=>[v,String(v)]));
  const timeWrap=make('label','Normalized time '),time=make('input'),output=make('output');timeWrap.className='stolarski-time';
  time.type='range';time.min='0';time.max='.98';time.step='.001';time.value='0';time.setAttribute('aria-label','Stolarski–Su normalized time');timeWrap.append(time,output);controls.append(timeWrap);
  const play=make('button','Play time');play.type='button';controls.append(play);
  const cut=make('button','Half slice');cut.type='button';cut.addEventListener('click',()=>{state.cutaway=!state.cutaway;sync();});controls.append(cut);
  const phaseWrap=make('label','4D projection '),phase=make('input');phase.type='range';phase.min='-.75';phase.max='.75';phase.step='.01';phase.value=String(state.projection);phase.setAttribute('aria-label','Stolarski–Su projection angle');phaseWrap.append(phase);controls.append(phaseWrap);
  const note=make('p');note.className='stolarski-note';stage.after(note);
  const scaleNote=make('p');scaleNote.className='stolarski-scale-note';note.after(scaleNote);
  const presets=make('div');presets.className='stolarski-presets';
  for(const v of SS.times){const b=make('button',`τ = ${v.toFixed(1)}`);b.type='button';b.addEventListener('click',()=>{stop();t=v;view='slice';sync();});presets.append(b);}controls.append(presets);
  function stop(){playing=false;cancelAnimationFrame(frame);last=0;play.textContent='Play time';}
  function sync(){
    for(const option of kSelect.options)option.disabled=!validCase(n,Number(option.value));
    if(!validCase(n,k))k=4;
    viewSelect.value=view;scaleSelect.value=scaleMode;nSelect.value=String(n);kSelect.value=String(k);time.value=String(t);phase.value=String(state.projection);
    output.textContent=`τ = ${t.toFixed(3)}`;phaseWrap.hidden=cut.hidden=view==='profile';cut.setAttribute('aria-pressed',String(state.cutaway));stage.dataset.view=view;
    note.textContent=view==='profile'?`Exact Lawlor profiles ±w in one complex coordinate line. Full flow: dimension ${n} in C${n} = R${2*n}. Dashed rays represent the two limiting planes; they are not additional ends.`:
      `Projection of ${state.cutaway?'half of the':'the'} 2D slice w(cos φ, sin φ, 0, …) of the Lawlor model in C${n} = R${2*n}. Blue and ochre are its two sides; purple marks the waist. Projection crossings are not self-intersections of the embedded full neck.`;
    scaleNote.textContent=scaleMode==='physical'?'Physical view: the neck scale decreases like q^(K/2), where q = 1 − τ. All time panels use the same spatial scale.':
      scaleMode==='parabolic'?'Parabolic zoom by q^(−1/2): the neck still disappears, with scale q^((K−1)/2). The tangent flow is a stationary pair of planes.':
      'Neck zoom by q^(−K/2): the model stays fixed. This illustrates the smooth special Lagrangian blow-up limit; the true rescaled flow converges to such a neck.';
    const a=neckScale(t,k,'physical',n),display=neckScale(t,k,scaleMode,n);
    status.textContent=`Asymptotic illustration, not a PDE simulation. τ = (t − t₀)/(T − t₀), with t₀ a reference time near T. Model a/a₀ = ${(a/SS.a0).toPrecision(3)}; displayed waist = ${display.toPrecision(3)}. No slice at or after T is shown.`;
    canvas.setAttribute('aria-label',`Stolarski–Su asymptotic neck model: n=${n}, K=${k}, ${scaleMode} scale, ${view==='compare'?'times 0, 0.6 and 0.9':`normalized time ${t.toFixed(3)}`}. Not computed flow slices. Arrow keys rotate the projected slice; plus and minus zoom.`);
    requestDraw();
  }
  function line(points,color='#8d9da4',width=1,dash=[]){ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.stroke();ctx.setLineDash([]);}
  function text(s,x,y,size=13,color='#284b5c',align='left'){ctx.fillStyle=color;ctx.font=`${size}px system-ui,sans-serif`;ctx.textAlign=align;ctx.fillText(s,x,y);ctx.textAlign='left';}
  function drawProfile(a,box,large=false){
    const size=Math.min(box.w*.45/(SS.radius*.62),box.h*.43/SS.radius)*state.zoom;
    const screen=([r,h])=>[box.x+box.w/2+size*h,box.y+box.h/2-size*r];
    // Source's reflection-symmetric orientation: (x,y)=(Im w,Re w).
    for(const sign of [-1,1])for(const end of [-1,1])line([screen([0,0]),screen([sign*SS.radius*Math.cos(Math.PI/(2*n)),end*SS.radius*Math.sin(Math.PI/(2*n))])],'#a2afb5',1,[4,4]);
    const curve=profile(n,a,160),middle=curve.length>>1;
    for(const sign of [-1,1]){
      line(curve.slice(0,middle+1).map(p=>screen(p.map(v=>sign*v))),'#277e9b',large?3:2);
      line(curve.slice(middle).map(p=>screen(p.map(v=>sign*v))),'#b7743e',large?3:2);
    }
    line([screen([0,0]),screen([a,0])],'#834d85',2);
    const origin=screen([0,0]);ctx.fillStyle='#834d85';ctx.beginPath();ctx.arc(...origin,2.5,0,2*Math.PI);ctx.fill();
    if(large){text('Im w',box.x+box.w-46,origin[1]-7,12);text('Re w',origin[0]+7,box.y+17,12);text(`waist a = ${a.toPrecision(3)}`,box.x+14,box.y+box.h-12,12,'#834d85');}
  }
  function drawSlice(a,box,small=false){
    ctx.save();ctx.beginPath();ctx.rect(box.x,box.y,box.w,box.h);ctx.clip();
    const scene=surfaceScene(n,a,box,state,small?[40,36]:[64,48]);
    for(const p of scene.polygons){ctx.beginPath();p.points.forEach((q,i)=>i?ctx.lineTo(...q):ctx.moveTo(...q));ctx.closePath();ctx.fillStyle=p.color;ctx.fill();ctx.strokeStyle=wire?'#23485840':p.color;ctx.lineWidth=wire?.45:.45;ctx.stroke();}
    line(Array.from({length:81},(_,j)=>scene.project(slicePoint([a,0],(state.cutaway?1:2)*Math.PI*j/80))),'#834d85',small?1.8:2.5);
    for(const w of [profile(n,a,2)[0],profile(n,a,2)[2]])line(Array.from({length:81},(_,j)=>scene.project(slicePoint(w,(state.cutaway?1:2)*Math.PI*j/80))),'#536f7b',.7);
    const x=box.x+box.w-20-scene.scale,y=box.y+box.h-13;line([[x,y],[x+scene.scale,y]],'#526d7a',1.5);text('1 unit',x+scene.scale/2,y-7,10,'#526d7a','center');ctx.restore();
  }
  function draw(){
    queued=false;const {width:w,height:h}=stage.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2);canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
    text(`ASYMPTOTIC MODEL · n = ${n}, K = ${k}`,14,24,w<380?11:13);
    if(view==='compare'){
      const narrow=w<560,cols=narrow?1:3,pw=w/cols,ph=narrow?(h-38)/3:h-38;
      SS.times.forEach((tau,i)=>{
        const x=narrow?0:i*pw,y=38+(narrow?i*ph:0),a=neckScale(tau,k,scaleMode,n);
        text(`τ = ${tau.toFixed(1)}  ·  a/a₀ = ${((1-tau)**(k/2)).toPrecision(2)}`,x+pw/2,y+15,12,'#284b5c','center');
        if(narrow){drawSlice(a,{x:8,y:y+22,w:pw*.64,h:ph-28},true);drawProfile(a,{x:pw*.65,y:y+22,w:pw*.34,h:ph-28});}
        else{drawSlice(a,{x:x+3,y:y+25,w:pw-6,h:ph*.56},true);drawProfile(a,{x:x+8,y:y+ph*.61,w:pw-16,h:ph*.34});text('profile ±w',x+pw/2,y+ph-8,11,'#627a85','center');}
        if(i)line(narrow?[[10,y-5],[w-10,y-5]]:[[x,42],[x,h-10]],'#d9e4e8');
      });
    }else if(view==='profile')drawProfile(neckScale(t,k,scaleMode,n),{x:10,y:42,w:w-20,h:h-50},true);
    else{
      drawSlice(neckScale(t,k,scaleMode,n),{x:0,y:42,w,h:h-42});
      const bw=Math.min(140,w*.28),bh=140;ctx.fillStyle='#f7fafbea';ctx.fillRect(w-bw-8,45,bw,bh);drawProfile(neckScale(t,k,scaleMode,n),{x:w-bw-8,y:60,w:bw,h:bh-15});text('profile ±w',w-bw/2-8,57,10,'#627a85','center');
      text(`τ = ${t.toFixed(3)}`,14,46,13);
    }
    Object.assign(canvas.dataset,{time:String(t),dimension:String(n),rate:String(k),view,scale:scaleMode,neckScale:String(neckScale(t,k,scaleMode,n)),rotation:`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`,zoom:String(state.zoom),projection:String(state.projection),cutaway:String(state.cutaway),playing:String(playing)});
  }
  function requestDraw(){if(!queued){queued=true;requestAnimationFrame(draw);}}
  function zoom(f){state.zoom=Math.max(.45,Math.min(2.6,state.zoom*f));requestDraw();}
  function tick(now){if(!playing)return;const dt=last?Math.min(.05,(now-last)/1000):0;last=now;t=Math.min(.98,t+dt*.075);if(t>=.98)stop();sync();if(playing)frame=requestAnimationFrame(tick);}
  play.addEventListener('click',()=>{if(playing){stop();requestDraw();return;}if(t>=.98)t=0;if(view==='compare')view='slice';playing=true;last=0;play.textContent='Pause time';sync();frame=requestAnimationFrame(tick);});
  time.addEventListener('input',()=>{stop();t=Number(time.value);if(view==='compare')view='slice';sync();});
  viewSelect.addEventListener('change',()=>{stop();view=viewSelect.value;sync();});
  scaleSelect.addEventListener('change',()=>{scaleMode=scaleSelect.value;sync();});
  nSelect.addEventListener('change',()=>{n=Number(nSelect.value);sync();});
  kSelect.addEventListener('change',()=>{k=Number(kSelect.value);sync();});
  phase.addEventListener('input',()=>{state.projection=Number(phase.value);requestDraw();});
  for(const b of controls.querySelectorAll('[data-view-action]'))b.addEventListener('click',()=>{
    if(b.dataset.viewAction==='in')zoom(1.2);if(b.dataset.viewAction==='out')zoom(1/1.2);
    if(b.dataset.viewAction==='wire'){wire=!wire;b.setAttribute('aria-pressed',String(wire));requestDraw();}
    if(b.dataset.viewAction==='reset'){stop();n=3;k=2;t=0;view='compare';scaleMode='physical';state=defaultCamera();wire=false;controls.querySelector('[data-view-action=wire]').setAttribute('aria-pressed','false');sync();}
  });
  canvas.addEventListener('pointerdown',e=>{if(view==='profile')return;drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;state.yaw+=(e.clientX-drag[0])*.009;state.pitch=Math.max(-1.4,Math.min(1.4,state.pitch+(e.clientY-drag[1])*.007));drag=[e.clientX,e.clientY];requestDraw();});
  for(const event of ['pointerup','pointercancel'])canvas.addEventListener(event,()=>{drag=null;});
  canvas.addEventListener('keydown',e=>{const keys={ArrowLeft:()=>state.yaw-=.12,ArrowRight:()=>state.yaw+=.12,ArrowUp:()=>state.pitch=Math.max(-1.4,state.pitch-.12),ArrowDown:()=>state.pitch=Math.min(1.4,state.pitch+.12),'+':()=>zoom(1.2),'=':()=>zoom(1.2),'-':()=>zoom(1/1.2)};if(keys[e.key]){e.preventDefault();keys[e.key]();requestDraw();}});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  if('IntersectionObserver'in window)new IntersectionObserver(items=>{if(!items[0].isIntersecting)stop();}).observe(figure);
  new ResizeObserver(requestDraw).observe(stage);
  help.textContent='Drag or use arrow keys to rotate the slice; zoom applies to every time panel. The projection slider changes the omitted fourth coordinate. Half slice removes half the spherical orbit to expose the neck; cut edges and outer rims are display cuts. Play stops before the singular time.';
  figure.querySelector('img').hidden=true;canvas.hidden=false;controls.hidden=false;help.hidden=false;sync();
}
