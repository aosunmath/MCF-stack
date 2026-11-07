// Costa's surface is sampled numerically; time follows a truncated-domain Jacobi mode.
const INK='#183f52',MUTED='#526b77',BLUE=[43,122,149],GOLD=[191,106,53];
export function normalFrame(data,t,side=1,gain=1){
  if(!Number.isFinite(t)||t<data.time.min||t>data.time.max||![1,-1].includes(side)||![1,3].includes(gain))throw new RangeError('Outside the linearized illustration parameters');
  const a=side*gain*data.amplitude*Math.exp(t);
  return data.vertices.map((p,i)=>p.map((x,k)=>x+a*data.mode[i]*data.normals[i][k]));
}
export function rotate([x,y,z],yaw,pitch){
  const a=x*Math.cos(yaw)-y*Math.sin(yaw),b=x*Math.sin(yaw)+y*Math.cos(yaw);
  return [a,z*Math.cos(pitch)-b*Math.sin(pitch),z*Math.sin(pitch)+b*Math.cos(pitch)];
}
function triangles(data,points,yaw,pitch,side){
  const q=points.map(p=>rotate(p,yaw,pitch)),base=side===1?BLUE:GOLD;
  const faces=data.faces.map(f=>{
    const [a,b,c]=f.map(i=>q[i]),u=b.map((x,k)=>x-a[k]),v=c.map((x,k)=>x-a[k]);
    const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]],l=Math.hypot(...n)||1;
    const light=.40+.60*Math.abs((n[0]*.22+n[1]*.4+n[2]*.89)/l);
    const color=base.map(x=>Math.round(x*light+40*(1-light)));
    return {f,depth:(a[2]+b[2]+c[2])/3,color:`rgb(${color.join(',')})`};
  }).sort((a,b)=>a.depth-b.depth);
  return {q,faces};
}
export function snapshotSVG(data){
  const W=1000,H=850,parts=[`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="title desc"><title id="title">Costa surface: a linearized ancient time sequence</title><desc id="desc">Four views of a sampled genus-one Costa surface with three open ends, displaced along a positive numerical Dirichlet Jacobi mode. Displacement is magnified three times. Not nonlinear ancient flow slices.</desc><rect width="1000" height="850" fill="#f7fafb"/><g font-family="system-ui,sans-serif" fill="${INK}"><text x="28" y="36" font-size="25" font-weight="600">Leaving the Costa surface · forward in model time</text><text x="28" y="64" font-size="16" fill="${MUTED}">Numerical linearized model · positive side · displacement ×3 · same spatial scale</text>`];
  for(let j=0;j<4;j++){
    const t=data.snapshots[j],x=26+j%2*488,y=84+Math.floor(j/2)*330,cx=x+235,cy=y+163,scale=28;
    const {q,faces}=triangles(data,normalFrame(data,t,1,3),data.view.yaw,data.view.pitch,1);
    const screen=i=>`${(cx+scale*q[i][0]).toFixed(2)},${(cy-scale*q[i][1]).toFixed(2)}`;
    parts.push(`<rect x="${x}" y="${y}" width="462" height="314" rx="8" fill="white" stroke="#d8e2e7"/><text x="${x+16}" y="${y+27}" font-size="20" font-weight="600">${j+1}. τ = ${t}</text>`);
    for(const f of faces)parts.push(`<polygon points="${f.f.map(screen).join(' ')}" fill="${f.color}" stroke="${f.color}" stroke-width=".6"/>`);
    parts.push(`<text x="${x+16}" y="${y+294}" font-size="14" fill="${MUTED}">Model max |u| = ${(data.amplitude*Math.exp(t)).toFixed(4)}</text>`);
  }
  parts.push(`<text x="28" y="775" font-size="17">As τ → −∞, both signs return to the same stationary Costa surface.</text><text x="28" y="803" font-size="15" fill="${MUTED}">X ± 0.11 exp(τ) φν, τ = λt. The screen magnifies the normal displacement, not time.</text><text x="28" y="830" font-size="14" fill="${MUTED}">Mramor–Payne, Theorem 1.1 and §3. Costa geometry: Melko (2010), eq. (17). Ends truncated.</text></g></svg>`);
  return parts.join('\n');
}

export function initMinimalAncientFigure(figure,data){
  figure.classList.add('minimal-ancient-figure');
  const stage=figure.querySelector('.soliton-stage'),canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d');if(!ctx)return;
  const controls=figure.querySelector('.soliton-controls'),help=figure.querySelector('.soliton-help'),status=figure.querySelector('.soliton-status');
  let t=data.time.value,side=1,gain=3,overview=true,yaw=data.view.yaw,pitch=data.view.pitch,zoom=1,wire=false,reference=false,playing=false,last=0,raf=0;
  const makeButton=text=>{const b=document.createElement('button');b.type='button';b.textContent=text;return b;};
  const four=makeButton('Four times'),play=makeButton('Play forward'),limit=makeButton('Minimal limit'),ghost=makeButton('Reference mesh');
  const timeLabel=document.createElement('label'),out=document.createElement('output'),slider=document.createElement('input');
  slider.type='range';slider.min=data.time.min;slider.max=data.time.max;slider.step='.02';slider.value=t;slider.setAttribute('aria-label','Linearized model time');timeLabel.append(out,slider);timeLabel.className='minimal-time-control';
  function select(label,items){const l=document.createElement('label'),s=document.createElement('select');s.setAttribute('aria-label',label.trim());l.append(label,s);for(const [v,text]of items){const o=document.createElement('option');o.value=v;o.textContent=text;s.append(o);}return [l,s];}
  const [sideLabel,sideSelect]=select('Side ',[['1','Positive (+ν)'],['-1','Negative (−ν)']]);
  const [gainLabel,gainSelect]=select('Displacement ',[['3','×3 (magnified)'],['1','×1 (model scale)']]);
  controls.prepend(four,play,limit,timeLabel,sideLabel,gainLabel,ghost);
  const note=document.createElement('p');note.className='minimal-ancient-note';note.textContent='Linearized time model on a truncated Costa surface. The three open rims are display cuts; the surface has one handle. No nonlinear ancient-flow slices are computed.';stage.after(note);
  help.textContent='Drag or use arrow keys to rotate all views together. Zoom to inspect the handle. Move the slider or Play forward for one evolving surface. Minimal limit shows the stationary surface. Reference mesh compares it with the moving model.';
  let minimal=false;
  function stop(){playing=false;cancelAnimationFrame(raf);play.textContent='Play forward';play.setAttribute('aria-pressed','false');}
  function sync(){
    out.textContent=`τ = ${t.toFixed(2)}`;slider.value=t;sideSelect.value=side;gainSelect.value=gain;
    four.setAttribute('aria-pressed',String(overview));limit.setAttribute('aria-pressed',String(minimal));ghost.setAttribute('aria-pressed',String(reference));
    canvas.dataset.time=t.toFixed(2);canvas.dataset.side=side;canvas.dataset.gain=gain;canvas.dataset.view=overview?'snapshots':minimal?'limit':'single';canvas.dataset.rotation=`${yaw.toFixed(3)},${pitch.toFixed(3)}`;canvas.dataset.zoom=zoom.toFixed(3);
    canvas.setAttribute('aria-label',`${overview?'Four times':minimal?'Stationary Costa limit':'Evolving linearized Costa model'}, ${side===1?'positive':'negative'} normal side, displacement magnified ${gain} times. Drag or arrow keys rotate; plus and minus zoom.`);
  }
  function txt(s,x,y,size=13,color=INK){ctx.fillStyle=color;ctx.font=`${size}px system-ui,sans-serif`;ctx.fillText(s,x,y);}
  let extent=[10,9];
  function panel(box,time,index){
    const [x,y,w,h]=box,scale=Math.min((w-24)/extent[0],(h-72)/extent[1])*zoom,cx=x+w/2,cy=y+36+(h-76)/2;
    const points=minimal&&!overview?data.vertices:normalFrame(data,time,side,gain),{q,faces}=triangles(data,points,yaw,pitch,side);
    const screen=p=>[cx+scale*p[0],cy-scale*p[1]];
    ctx.save();ctx.beginPath();ctx.rect(x,y,w,h);ctx.clip();ctx.fillStyle='white';ctx.fillRect(x,y,w,h);
    for(const f of faces){ctx.beginPath();f.f.forEach((i,k)=>k?ctx.lineTo(...screen(q[i])):ctx.moveTo(...screen(q[i])));ctx.closePath();ctx.fillStyle=f.color;ctx.fill();ctx.strokeStyle=wire?'#234b5b55':f.color;ctx.lineWidth=wire?.45:.65;ctx.stroke();}
    if(reference&&!minimal){
      const r=data.vertices.map(p=>rotate(p,yaw,pitch));ctx.strokeStyle='#142d4280';ctx.lineWidth=.6;ctx.setLineDash([2,3]);
      // A sparse overlay, deliberately including hidden lines to locate the stationary reference.
      for(let j=0;j<data.faces.length;j+=43){ctx.beginPath();data.faces[j].forEach((i,k)=>k?ctx.lineTo(...screen(r[i])):ctx.moveTo(...screen(r[i])));ctx.closePath();ctx.stroke();}ctx.setLineDash([]);
    }
    txt(minimal&&!overview?'τ → −∞ · minimal limit':`${index?index+'. ':''}τ = ${time.toFixed(2)}`,x+12,y+23,overview?14:18);
    txt(minimal&&!overview?'Normal displacement = 0':`max |u| = ${(data.amplitude*Math.exp(time)).toFixed(4)}`,x+12,y+h-14,12,MUTED);
    ctx.restore();
  }
  function draw(){
    sync();const W=stage.clientWidth,H=stage.clientHeight,dpr=Math.min(devicePixelRatio||1,2);canvas.width=W*dpr;canvas.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,W,H);
    extent=[0,0];for(const sign of [1,-1])for(const p of normalFrame(data,0,sign,3)){const q=rotate(p,yaw,pitch);for(let k=0;k<2;k++)extent[k]=Math.max(extent[k],2*Math.abs(q[k]));}
    if(overview){const g=10,w=(W-3*g)/2,h=(H-54-3*g)/2;data.snapshots.forEach((s,i)=>panel([g+i%2*(w+g),38+g+Math.floor(i/2)*(h+g),w,h],s,i+1));}
    else panel([8,38,W-16,H-46],t,0);
    txt(`Costa in ℝ³ · ${side===1?'+ν':'−ν'} side · displacement ×${gain}`,12,22,W<430?12:14);
    status.textContent=overview?'Forward order: top left → top right → bottom left → bottom right. One scale and one camera for all times.':minimal?'Both branches approach this same minimal surface backward in time.':`τ = λt; λ ≈ ${data.eigenvalue.toFixed(3)} for this truncated-domain mode. ${gain===3?'Normal displacement is magnified three times.':'Normal displacement is shown at model scale.'} ${reference?'Dashed mesh: stationary reference (hidden lines included).':''}`;
  }
  function tick(now){if(!playing)return;if(last)t=Math.min(0,t+(now-last)*.00035);last=now;draw();if(t>=0)stop();else raf=requestAnimationFrame(tick);}
  play.addEventListener('click',()=>{if(playing){stop();return;}overview=false;minimal=false;if(t>=0)t=-5;playing=true;last=0;play.textContent='Pause';play.setAttribute('aria-pressed','true');raf=requestAnimationFrame(tick);});
  four.addEventListener('click',()=>{stop();overview=true;minimal=false;draw();});
  limit.addEventListener('click',()=>{stop();overview=false;minimal=true;draw();});
  ghost.addEventListener('click',()=>{reference=!reference;draw();});
  slider.addEventListener('input',()=>{stop();t=Number(slider.value);overview=false;minimal=false;draw();});
  sideSelect.addEventListener('change',()=>{side=Number(sideSelect.value);draw();});gainSelect.addEventListener('change',()=>{gain=Number(gainSelect.value);draw();});
  for(const b of controls.querySelectorAll('[data-view-action]'))b.addEventListener('click',()=>{
    const a=b.dataset.viewAction;if(a==='in')zoom=Math.min(3,zoom*1.2);if(a==='out')zoom=Math.max(.5,zoom/1.2);if(a==='wire'){wire=!wire;b.setAttribute('aria-pressed',String(wire));}
    if(a==='reset'){stop();t=data.time.value;side=1;gain=3;overview=true;minimal=false;reference=false;wire=false;zoom=1;yaw=data.view.yaw;pitch=data.view.pitch;controls.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed','false');}draw();
  });
  let pointer=null;
  canvas.addEventListener('pointerdown',e=>{pointer=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!pointer)return;yaw+=(e.clientX-pointer[0])*.008;pitch=Math.max(-1.5,Math.min(1.5,pitch+(e.clientY-pointer[1])*.008));pointer=[e.clientX,e.clientY];draw();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>pointer=null);
  canvas.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-'].includes(e.key))return;e.preventDefault();if(e.key==='ArrowLeft')yaw-=.13;if(e.key==='ArrowRight')yaw+=.13;if(e.key==='ArrowUp')pitch-=.13;if(e.key==='ArrowDown')pitch+=.13;if(['+','=','-'].includes(e.key))zoom=Math.max(.5,Math.min(3,zoom*(e.key==='-'?1/1.2:1.2)));draw();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});new IntersectionObserver(e=>{if(!e[0].isIntersecting)stop();}).observe(figure);
  controls.hidden=false;help.hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;new ResizeObserver(draw).observe(stage);draw();
}
