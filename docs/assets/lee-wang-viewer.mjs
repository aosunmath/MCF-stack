// Lee–Wang, arXiv:0802.0359v1, Theorem 1.1 and §§2–3.
// Exact coordinates, sampled for display. All six ambient coordinates are retained
// before projection. The rendered surface is a phase leaf, not the full 3-manifold.
export const CUT_RADIUS=3.6;
export const SHRINK_TIMES=[-1,-.25,-.04,0];
export const CONTINUATION_TIMES=[-1,0,.25,1];
const TAU=2*Math.PI,ORANGE='#bd6b2c',INK='#183f52';
function checkTime(t){if(!Number.isFinite(t)||t< -2||t>1)throw new RangeError('Display time must be between −2 and 1.');}
export function lift([x,y,z],s=0){
  if(!Number.isFinite(s))throw new RangeError('Phase must be finite.');
  const c=Math.cos(s),q=Math.sin(s);return [x*c,x*q,y*c,y*q,z*c,-z*q];
}
export function project6([a,b,c,d,e]){return [a,(c+b)/Math.SQRT2,(e+d)/Math.SQRT2];}
export function shrinkerPoint(theta,u,s,t){
  checkTime(t);if(!(t<0))throw new RangeError('Smooth shrinker coordinates require t < 0.');
  const r=Math.sqrt(u*u-2*t);return lift([r*Math.cos(theta),r*Math.sin(theta),u],s);
}
export function realSlice(t,angular=48,axial=36){
  checkTime(t);
  if(!Number.isInteger(angular)||angular<8||!Number.isInteger(axial)||axial<4||axial%2)throw new RangeError('Use at least eight angular and four even axial subdivisions.');
  const vertices=[],faces=[],rings=[],meridians=[];
  const extent=Math.sqrt((CUT_RADIUS**2-2*Math.abs(t))/2);
  for(const sign of (t>0?[-1,1]:[1])){
    const offset=vertices.length;
    for(let j=0;j<=axial;j++){
      const v=t>0?extent*j/axial:extent*(2*j/axial-1);
      const r=t>0?v:Math.sqrt(v*v-2*t),z=t>0?sign*Math.sqrt(v*v+2*t):v;
      for(let i=0;i<angular;i++)vertices.push([r*Math.cos(TAU*i/angular),r*Math.sin(TAU*i/angular),z]);
    }
    const index=(j,i)=>offset+j*angular+(i%angular);
    for(let j=0;j<axial;j++)for(let i=0;i<angular;i++)faces.push([index(j,i),index(j,i+1),index(j+1,i+1),index(j+1,i)]);
    for(let j=0;j<=axial;j+=3)rings.push(Array.from({length:angular+1},(_,i)=>index(j,i)));
    for(let i=0;i<angular;i+=6)meridians.push(Array.from({length:axial+1},(_,j)=>index(j,i)));
  }
  return {vertices,faces,rings,meridians,paths:[]};
}
const rotate=(p,yaw,pitch)=>{
  const a=p[0]*Math.cos(yaw)-p[1]*Math.sin(yaw),b=p[0]*Math.sin(yaw)+p[1]*Math.cos(yaw);
  return [a,p[2]*Math.cos(pitch)-b*Math.sin(pitch),p[2]*Math.sin(pitch)+b*Math.cos(pitch)];
};
const formatted=t=>t===0?'0':String(t).replace('-','−');
function scene(t,{yaw=.55,pitch=.28,phase=0,orbits=false,wire=false}={}){
  const mesh=realSlice(t),transform=p=>rotate(orbits?project6(lift(p,phase)):p,yaw,pitch);
  const q=mesh.vertices.map(transform),items=[];
  const segment=(points,color,width=.7,dash=[])=>{
    for(let i=1;i<points.length;i++)items.push({points:[points[i-1],points[i]],stroke:color,width,dash,depth:(points[i-1][2]+points[i][2])/2+.002});
  };
  if(orbits){
    for(const u of [-1.25,0,1.25])for(let k=0;k<6;k++){
      let x;
      if(t<=0){const r=Math.sqrt(u*u-2*t);x=[r*Math.cos(k*TAU/6),r*Math.sin(k*TAU/6),u];}
      else {const r=Math.abs(u);x=[r*Math.cos(k*TAU/6),r*Math.sin(k*TAU/6),Math.sqrt(r*r+2*t)];}
      segment(Array.from({length:73},(_,j)=>rotate(project6(lift(x,j*TAU/72)),yaw,pitch)),'#bcb0a5',.8,[3,3]);
    }
  }
  if(!wire)for(const f of mesh.faces){
    const p=f.map(i=>q[i]),a=p[1].map((v,i)=>v-p[0][i]),b=p[3].map((v,i)=>v-p[0][i]);
    const n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],length=Math.hypot(...n);
    if(length<1e-12)continue;
    const light=.42+.48*Math.abs((n[0]*.25+n[1]*.45+n[2]*.86)/length);
    const base=t===0?[176,146,111]:t>0?[126,159,120]:[62,143,175];
    const fill=`rgb(${base.map(c=>Math.round(c*light+235*(1-light)*.45)).join(',')})`;
    items.push({points:p,fill,stroke:fill,width:.45,depth:p.reduce((s,x)=>s+x[2],0)/4});
  }
  for(const line of [...mesh.rings,...mesh.meridians])segment(line.map(i=>q[i]),wire?'#366a80':'#285b7055',wire?.9:.45);
  // Orange marks the waist (or the two expander tips), never an artificial cap.
  if(t<0)segment(Array.from({length:97},(_,i)=>transform([Math.sqrt(-2*t)*Math.cos(i*TAU/96),Math.sqrt(-2*t)*Math.sin(i*TAU/96),0])),ORANGE,2.4);
  return items.sort((a,b)=>a.depth-b.depth);
}
function panel(t,box,options={}){
  const [x,y,w,h]=box,scale=Math.min((w-24)/(2*CUT_RADIUS),(h-78)/(2*CUT_RADIUS))*(options.zoom||1);
  const screen=p=>[x+w/2+p[0]*scale,y+h/2+7-p[1]*scale];
  const shapes=scene(t,options).map(o=>({...o,points:o.points.map(screen)}));
  return {shapes,scale,box,title:`t = ${formatted(t)}${t===0?' · cone':t>0?' · expander':''}`,detail:t<0?`Waist radius ${Math.sqrt(-2*t).toFixed(3)}`:t===0?'Singular at the origin':`Tip height ±${Math.sqrt(2*t).toFixed(3)}`};
}
export function snapshotSVG(){
  let svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 900" role="img" aria-labelledby="title desc"><title id="title">Lee–Wang shrinker approaching its cone</title><desc id="desc">Four exact real slices at times −1, −0.25, −0.04 and 0, shown at the same scale. Orange marks the shrinking waist. The full flow has dimension three in R6; these surfaces do not flow by their own mean curvature.</desc><rect width="1000" height="900" fill="#f7fafb"/><g font-family="Arial,Helvetica,sans-serif" fill="#183f52"><text x="28" y="38" font-size="25" font-weight="600">A shrinking waist, a noncompact cone</text><text x="28" y="66" font-size="17">Exact s = 0 slices · n = 3, k = 2 · x₁² + x₂² − x₃² = −2t</text>';
  SHRINK_TIMES.forEach((t,i)=>{
    const p=panel(t,[20+(i%2)*490,86+Math.floor(i/2)*366,470,350]);
    const [x,y,w,h]=p.box;
    svg+=`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="8" fill="#edf3f5"/><text x="${x+15}" y="${y+28}" font-size="21" font-weight="600">${p.title}</text>`;
    for(const o of p.shapes)svg+=`<${o.fill?'polygon':'polyline'} points="${o.points.map(q=>q.map(a=>a.toFixed(2)).join(',')).join(' ')}" fill="${o.fill||'none'}" stroke="${o.stroke}" stroke-width="${o.width}"/>`;
    svg+=`<text x="${x+15}" y="${y+h-14}" font-size="16">${p.detail}</text>`;
    svg+=`<path d="M${x+w-94} ${y+h-31}h${p.scale}" stroke="#183f52" stroke-width="2"/><text x="${x+w-94}" y="${y+h-14}" font-size="13">1 unit</text>`;
  });
  svg+='<text x="28" y="846" font-size="17">Same camera and spatial scale; cropped to |X| ≤ 3.6 at every time.</text><text x="28" y="875" font-size="17">A 2D slice of a 3-manifold in C³, not a surface MCF in R³. Lee–Wang, Theorem 1.1.</text></g></svg>\n';return svg;
}
export function initLeeWangFigure(figure){
  const canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d'),stage=figure.querySelector('.soliton-stage');
  const controls=figure.querySelector('.soliton-controls'),help=figure.querySelector('.soliton-help'),status=figure.querySelector('.soliton-status');
  figure.classList.add('lw-figure');
  let t=-1,phase=.7,mode='times',continuation=false,wire=false,zoom=1,yaw=.55,pitch=.28,playing=false,last=0,raf=0;
  const button=(name,fn)=>{const b=document.createElement('button');b.type='button';b.textContent=name;b.addEventListener('click',fn);controls.append(b);return b;};
  const stop=()=>{playing=false;last=0;cancelAnimationFrame(raf);play.textContent='Play forward';play.setAttribute('aria-pressed','false');};
  const setMode=value=>{stop();mode=value;draw();};
  controls.replaceChildren();
  const viewLabel=document.createElement('label'),view=document.createElement('select');view.setAttribute('aria-label','Geometry view');
  for(const [value,name] of [['times','Four times'],['single','One time'],['orbits','Circle action in R⁶']]){const o=document.createElement('option');o.value=value;o.textContent=name;view.append(o);}viewLabel.append('View',view);controls.append(viewLabel);view.addEventListener('change',()=>setMode(view.value));
  const play=button('Play forward',()=>{if(playing){stop();return;}if(mode==='times')mode='single';if(t>=(continuation?1:0))t=-2;playing=true;last=0;play.textContent='Pause';play.setAttribute('aria-pressed','true');raf=requestAnimationFrame(tick);});
  const timeLabel=document.createElement('label'),timeOut=document.createElement('output'),time=document.createElement('input');timeLabel.className='lw-time';time.type='range';time.min='-2';time.max='0';time.step='.01';time.setAttribute('aria-label','Mean curvature flow time');timeLabel.append(timeOut,time);controls.append(timeLabel);
  time.addEventListener('input',()=>{stop();t=Number(time.value);if(mode==='times')mode='single';draw();});
  const phaseLabel=document.createElement('label'),phaseOut=document.createElement('output'),phaseInput=document.createElement('input');phaseLabel.className='lw-phase';phaseInput.type='range';phaseInput.min='0';phaseInput.max='1';phaseInput.step='.01';phaseInput.setAttribute('aria-label','Circle phase, not time');phaseLabel.append(phaseOut,phaseInput);controls.append(phaseLabel);
  phaseInput.addEventListener('input',()=>{phase=Math.PI*Number(phaseInput.value);draw();});
  const expand=button('Include expander',()=>{stop();continuation=!continuation;if(!continuation)t=Math.min(t,0);draw();});
  const cone=button('Cone at t = 0',()=>{stop();t=0;mode='single';draw();});
  button('Zoom +',()=>{zoom=Math.min(2.5,zoom*1.2);draw();});button('Zoom −',()=>{zoom=Math.max(.5,zoom/1.2);draw();});
  const mesh=button('Mesh',()=>{wire=!wire;draw();});
  button('Reset view',()=>{stop();t=-1;phase=.7;mode='times';continuation=false;wire=false;zoom=1;yaw=.55;pitch=.28;draw();});
  help.textContent='Drag to rotate; arrow keys rotate and + / − zoom. All time panels use the same scale. Orange marks the waist. Cut edges only bound the displayed portion.';
  const note=document.createElement('p');note.className='lw-note';controls.after(note);
  function draw(){
    stage.dataset.view=mode;view.value=mode;phaseLabel.hidden=mode!=='orbits';
    const {width:W,height:H}=stage.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2);canvas.width=Math.round(W*dpr);canvas.height=Math.round(H*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,W,H);
    const mobile=W<450,top=38;
    const times=continuation?CONTINUATION_TIMES:SHRINK_TIMES;
    const boxes=mode==='times'?times.map((v,i)=>[v,[8+(i%2)*(W-8)/2,top+Math.floor(i/2)*(H-top)/2,(W-24)/2,(H-top)/2-8]]):[[t,[8,top,W-16,H-top-8]]];
    ctx.fillStyle=INK;ctx.font=`${mobile?11:13}px system-ui`;ctx.fillText(mode==='orbits'?'Projected phase leaf + sampled circle orbits':'Real slice s = 0 · x₁² + x₂² − x₃² = −2t',12,23);
    for(const [value,box] of boxes){
      const p=panel(value,box,{yaw,pitch,phase,orbits:mode==='orbits',zoom,wire}),[x,y,w,h]=box;
      ctx.fillStyle='#edf3f5';ctx.fillRect(x,y,w,h);ctx.save();ctx.beginPath();ctx.rect(x+1,y+33,w-2,h-63);ctx.clip();
      for(const o of p.shapes){ctx.beginPath();o.points.forEach((v,i)=>i?ctx.lineTo(...v):ctx.moveTo(...v));if(o.fill){ctx.closePath();ctx.fillStyle=o.fill;ctx.fill();}ctx.strokeStyle=o.stroke;ctx.lineWidth=o.width;ctx.setLineDash(o.dash||[]);ctx.stroke();}ctx.restore();ctx.setLineDash([]);
      ctx.fillStyle=INK;ctx.font=`600 ${mobile?12:15}px system-ui`;ctx.fillText(p.title,x+9,y+23);
      ctx.font=`${mobile?10:12}px system-ui`;ctx.fillText(p.detail,x+9,y+h-10);
      if(w>220){ctx.strokeStyle=INK;ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(x+w-80,y+h-26);ctx.lineTo(x+w-80+p.scale,y+h-26);ctx.stroke();ctx.fillText('1 unit',x+w-80,y+h-10);}
    }
    time.max=continuation?'1':'0';time.value=String(t);timeOut.textContent=`t = ${formatted(Number(t.toFixed(2)))}`;phaseInput.value=String(phase/Math.PI);phaseOut.textContent=`Phase s = ${(phase/Math.PI).toFixed(2)}π`;
    expand.setAttribute('aria-pressed',String(continuation));mesh.setAttribute('aria-pressed',String(wire));cone.setAttribute('aria-pressed',String(t===0&&mode==='single'));
    note.textContent=mode==='orbits'?'The phase s is a spatial coordinate, not time. A selected 2D leaf and dotted circle orbits are projected from R⁶ by P(z) = (Re z₁, (Re z₂ + Im z₁)/√2, (Re z₃ + Im z₂)/√2). Moving s from 0 to π implements the antipodal gluing. Projection crossings do not imply self-intersections.':'Exact phase slices of a three-dimensional flow in C³. The visible hyperboloid is not itself a surface mean curvature flow in R³. The fixed crop |X| ≤ 3.6 reveals convergence to a noncompact cone, rather than collapse of the entire manifold to a point.';
    status.textContent=continuation?'t < 0: shrinker; t = 0: singular cone; t > 0: companion expander. Lee–Wang prove a Brakke continuation without mass loss. The two expander slice sheets belong to one connected three-manifold.':mode==='times'?'Forward time: top left → top right → bottom left → bottom right. The waist radius is √(−2t).':t===0?'This is the singular cone at t = 0, not a smooth shrinker slice.':`Smooth shrinker at t = ${formatted(Number(t.toFixed(2)))}. The full flow satisfies Lₜ = √(−t) L₋₁.`;
    canvas.dataset.view=mode;canvas.dataset.time=t.toFixed(2);canvas.dataset.phase=phase.toFixed(3);canvas.dataset.zoom=zoom.toFixed(3);canvas.dataset.rotation=[yaw,pitch].join(',');
    canvas.setAttribute('aria-label',mode==='times'?`Exact Lee–Wang real slices at times ${times.join(', ')} with a shared scale. Full ambient space R6.`:`Lee–Wang ${mode==='orbits'?'projected circle action':'real slice'} at time ${t.toFixed(2)}. ${t===0?'Singular cone.':'Full flow has dimension three in R6.'}`);
  }
  function tick(now){if(!playing)return;if(last)t=Math.min(continuation?1:0,t+Math.min((now-last)/1000,.1)*.32);last=now;draw();if(t>=(continuation?1:0))stop();else raf=requestAnimationFrame(tick);}
  let drag=null;canvas.addEventListener('pointerdown',e=>{drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;yaw+=(e.clientX-drag[0])*.008;pitch=Math.max(-1.4,Math.min(1.4,pitch+(e.clientY-drag[1])*.008));drag=[e.clientX,e.clientY];draw();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>drag=null);
  canvas.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-'].includes(e.key))return;e.preventDefault();if(e.key==='ArrowLeft')yaw-=.12;if(e.key==='ArrowRight')yaw+=.12;if(e.key==='ArrowUp')pitch-=.12;if(e.key==='ArrowDown')pitch+=.12;if(['+','=','-'].includes(e.key))zoom=Math.max(.5,Math.min(2.5,zoom*(e.key==='-'?1/1.2:1.2)));draw();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});new IntersectionObserver(e=>{if(!e[0].isIntersecting)stop();}).observe(figure);
  figure.querySelector('img').hidden=true;canvas.hidden=false;controls.hidden=false;help.hidden=false;new ResizeObserver(draw).observe(stage);draw();
}
