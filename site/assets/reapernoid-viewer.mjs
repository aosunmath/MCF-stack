// Numerical finite-start rotational MCF; no eternal-limit certification is implied.
const INK='#183f52',MUTED='#526b77',BLUE='#247c98',GOLD='#ae7132';
export function interpolate(xs,ys,x){
  if(x<xs[0]-1e-7||x>xs.at(-1)+1e-7)throw new RangeError('Outside sampled profile');
  let a=0,b=xs.length-1;while(b-a>1){const m=(a+b)>>1;if(xs[m]<=x)a=m;else b=m;}
  const w=Math.max(0,Math.min(1,(x-xs[a])/(xs[b]-xs[a])));return ys[a]*(1-w)+ys[b]*w;
}
export function frameAt(model,t){
  const fs=model.frames;if(!Number.isFinite(t)||t<fs[0].t||t>fs.at(-1).t)throw new RangeError('Outside numerical time interval');
  let a=0,b=fs.length-1;while(b-a>1){const m=(a+b)>>1;if(fs[m].t<=t)a=m;else b=m;}
  const s=(t-fs[a].t)/(fs[b].t-fs[a].t),f={t,u:fs[a].u.map((v,i)=>v*(1-s)+fs[b].u[i]*s)};
  for(const key of ['neck_radius','neck_speed','meridian_tip_curvature'])f[key]=fs[a][key]*(1-s)+fs[b][key]*s;
  return f;
}
export function limitHeight(model,x){
  if(model.n===2||x===0)return 0;const c=Math.PI/(2*model.half_width);
  if(Math.abs(x)>=model.half_width)throw new RangeError('Outside grim-reaper strip');return -Math.log(Math.cos(c*x))/c;
}
export function surfaceVertices(data,t){
  const m=data.cases[0],f=frameAt(m,t),v=[];
  for(const x of data.mesh_x){const r=interpolate(m.x,f.u,x);for(let j=0;j<data.segments;j++){const a=2*Math.PI*j/data.segments;v.push([r*Math.cos(a),r*Math.sin(a),x]);}}
  return v;
}
function rotate([x,y,z],yaw,pitch){const a=x*Math.cos(yaw)-y*Math.sin(yaw),b=x*Math.sin(yaw)+y*Math.cos(yaw);return [a,z*Math.cos(pitch)-b*Math.sin(pitch),z*Math.sin(pitch)+b*Math.cos(pitch)];}
function surfaceScene(data,t,yaw,pitch){
  const q=surfaceVertices(data,t).map(p=>rotate(p,yaw,pitch));
  const faces=data.faces.map(f=>{const[a,b,c]=f.map(i=>q[i]),u=b.map((x,k)=>x-a[k]),v=c.map((x,k)=>x-a[k]);let n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];if(n[2]<0)n=n.map(x=>-x);const light=.40+.60*Math.max(0,(-.25*n[0]+.45*n[1]+.85*n[2])/(Math.hypot(...n)||1));return {f,z:(a[2]+b[2]+c[2])/3,color:`rgb(${[51,137,161].map(x=>Math.round(x*light)).join(',')})`};}).sort((a,b)=>a.z-b.z);
  return {q,faces};
}
const label=t=>Number(t.toFixed(2)).toString().replace('-','−');
export function surfacePlate(data){
  const parts=[`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 810" role="img" aria-labelledby="title desc"><title id="title">The reapernoid in three-space at four times</title><desc id="desc">Four numerical rotational mean curvature flow slices starting near a unit-neck catenoid. The open annular neck expands away from the axis. All panels use the same camera and spatial scale. Finite-start approximation, not a certified eternal flow.</desc><rect width="1000" height="810" fill="#f7fafb"/><g font-family="system-ui,sans-serif" fill="${INK}"><text x="28" y="36" font-size="25" font-weight="600">The reapernoid in ℝ³ · moving away from the axis</text><text x="28" y="64" font-size="16" fill="${MUTED}">Numerical MCF · four times at one spatial scale · catenoid neck radius = 1</text>`];
  for(let i=0;i<4;i++){
    const t=data.cases[0].snapshots[i],x=26+i%2*488,y=84+Math.floor(i/2)*310,cx=x+231,cy=y+151,sc=27;
    const {q,faces}=surfaceScene(data,t,data.view.yaw,data.view.pitch),screen=p=>`${(cx+sc*p[0]).toFixed(2)},${(cy-sc*p[1]).toFixed(2)}`;
    parts.push(`<rect x="${x}" y="${y}" width="462" height="294" rx="8" fill="white" stroke="#d8e2e7"/><text x="${x+16}" y="${y+28}" font-size="20" font-weight="600">${i+1}. t = ${label(t)}</text><path d="M${cx},${y+43}V${y+245}" stroke="#9eb5bf" stroke-width="1" stroke-dasharray="4 4"/>`);
    for(const f of faces)parts.push(`<polygon points="${f.f.map(j=>screen(q[j])).join(' ')}" fill="${f.color}" stroke="${f.color}" stroke-width=".5"/>`);
    parts.push(`<text x="${x+16}" y="${y+276}" font-size="15" fill="${MUTED}">Neck radius ≈ ${frameAt(data.cases[0],t).neck_radius.toFixed(3)}</text>`);
  }
  parts.push(`<text x="28" y="731" font-size="16">The surface changes shape; these are not dilations of a catenoid.</text><text x="28" y="759" font-size="15" fill="${MUTED}">Two open rims are display cuts at x = ±2. Time is shifted so that u(0, 0) = 2.</text><text x="28" y="786" font-size="14" fill="${MUTED}">Mramor–Payne, Theorem 1.3 and equation (2.7). Finite-start, truncated-domain approximation.</text></g></svg>`);
  return parts.join('\n');
}
export function profilePlate(data){
  const colors=['#a5c7d4','#68a8bf','#377f9c','#174b65'];
  const parts=[`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 750" role="img" aria-labelledby="title desc"><title id="title">Recentered reapernoid profiles have dimension-dependent forward limits</title><desc id="desc">Numerical profiles u(x,t)-u(0,t), with no spatial rescaling. In R3 the limiting profile is a line. In R4 the limiting profile is a grim reaper. Gold dashed curves show the proved limits, not finite-time slices.</desc><rect width="1000" height="750" fill="#f7fafb"/><g font-family="system-ui,sans-serif" fill="${INK}"><text x="28" y="36" font-size="25" font-weight="600">After recentering at the neck · different forward limits</text><text x="28" y="64" font-size="16" fill="${MUTED}">Height = u(x, t) − u(0, t). Translation only; no spatial rescaling.</text>`];
  data.cases.forEach((m,k)=>{
    const x=26+k*488,y=85,w=462,h=470,range=k===0?2:1.1,top=k===0?3:3.7,px=182/range,py=330/top,cx=x+231,cy=y+397;
    const screen=(a,b)=>[cx+a*px,cy-b*py];
    const path=points=>points.map(([a,b],i)=>{const[u,v]=screen(a,b);return `${i?'L':'M'}${u.toFixed(2)},${v.toFixed(2)}`;}).join(' ');
    parts.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="8" fill="white" stroke="#d8e2e7"/><text x="${x+16}" y="${y+30}" font-size="21" font-weight="600">${k===0?'n = 2 · surface in ℝ³':'n = 3 · hypersurface in ℝ⁴'}</text><text x="${x+16}" y="${y+55}" font-size="15" fill="${MUTED}">Meridian only · ${k===0?'line limit':'grim-reaper limit'}</text>`);
    for(let a=-2;a<=2;a++){const xx=a*range/2;const [sx,sy]=screen(xx,0);parts.push(`<path d="M${sx},${y+75}V${cy}" stroke="#e7eef1"/><text x="${sx}" y="${cy+22}" text-anchor="middle" font-size="13">${Number(xx.toFixed(2))}</text>`);}
    for(let b=0;b<=Math.floor(top);b++){const[sx,sy]=screen(-range,b);parts.push(`<path d="M${sx},${sy}H${cx+range*px}" stroke="#e7eef1"/><text x="${sx-9}" y="${sy+4}" text-anchor="end" font-size="12">${b}</text>`);}
    m.profile_snapshots.forEach((t,i)=>{const f=frameAt(m,t),points=m.x.map((a,j)=>[a,f.u[j]-f.neck_radius]).filter(p=>Math.abs(p[0])<=range+1e-7);parts.push(`<path d="${path(points)}" fill="none" stroke="${colors[i]}" stroke-width="2.5"/><text x="${x+26+(i%2)*210}" y="${y+439+Math.floor(i/2)*21}" font-size="14" fill="${colors[i]}">━━ t = ${label(t)}</text>`);});
    const limit=Array.from({length:181},(_,i)=>{const a=-range+2*range*i/180;return [a,limitHeight(m,a)];});
    parts.push(`<path d="${path(limit)}" fill="none" stroke="${GOLD}" stroke-width="2.5" stroke-dasharray="7 5"/><text x="${cx+range*px+12}" y="${cy+5}" font-size="14">x</text>`);
  });
  parts.push(`<text x="28" y="593" font-size="17">Gold dashed: the forward pointed limit proved in Theorem 1.3.</text><text x="28" y="625" font-size="16">ℝ³: curvature tends to zero. Higher dimensions: a grim reaper of the catenoid’s strip width.</text><text x="28" y="659" font-size="15" fill="${MUTED}">Finite-time numerical profiles need not equal their limits. Each neck continues moving outward.</text><text x="28" y="689" font-size="15" fill="${MUTED}">Only n = 2 and n = 3 are computed here; the theorem covers every n ≥ 2.</text><text x="28" y="721" font-size="14" fill="${MUTED}">Mramor–Payne, §4, especially (4.5) and p. 20. Numerical sensitivity checks accompany the data.</text></g></svg>`);
  return parts.join('\n');
}

export function initReapernoidFigure(figure,data){
  figure.classList.add('reapernoid-figure');
  const stage=figure.querySelector('.soliton-stage'),canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d');if(!ctx)throw new Error('Canvas unavailable');
  const controls=figure.querySelector('.soliton-controls'),help=figure.querySelector('.soliton-help'),status=figure.querySelector('.soliton-status');
  let view='surface',coordinates='centered',t=0,overview=true,zoom=1,yaw=data.view.yaw,pitch=data.view.pitch,wire=false,reference=false,playing=false,last=0,raf=0;
  const button=text=>{const b=document.createElement('button');b.type='button';b.textContent=text;return b;};
  const four=button('Four times'),play=button('Play forward'),ref=button('Catenoid reference');
  function select(title,options){const l=document.createElement('label'),s=document.createElement('select');s.setAttribute('aria-label',title);l.append(title+' ',s);for(const[v,title]of options){const o=document.createElement('option');o.value=v;o.textContent=title;s.append(o);}return[l,s];}
  const [viewLabel,viewSelect]=select('View',[['surface','Surface in ℝ³'],['profile2','Meridian in ℝ³'],['profile3','Meridian in ℝ⁴']]);
  const [coordLabel,coordSelect]=select('Profile coordinates',[['centered','Neck at height zero'],['original','Original radius']]);
  const timeLabel=document.createElement('label'),out=document.createElement('output'),slider=document.createElement('input');timeLabel.className='reapernoid-time';slider.type='range';slider.step='.01';slider.setAttribute('aria-label','Reapernoid numerical time');timeLabel.append(out,slider);controls.prepend(four,play,viewLabel,timeLabel,coordLabel,ref);
  const note=document.createElement('p');note.className='reapernoid-note';note.textContent='Numerical MCF from an outward normal offset δ = 0.0001 of a unit-neck catenoid. Time zero is chosen when the neck radius reaches 2. Finite starting time and artificial end boundaries are used.';stage.after(note);
  const model=()=>data.cases[view==='profile3'?1:0];
  const interval=()=>view==='surface'?model().surface_time:model().time;
  const snapshots=()=>view==='surface'?model().snapshots:model().profile_snapshots;
  function stop(){playing=false;cancelAnimationFrame(raf);play.textContent='Play forward';play.setAttribute('aria-pressed','false');}
  function sync(){
    const r=interval();slider.min=r.min;slider.max=r.max;slider.value=t;out.textContent=`t = ${label(t)}`;viewSelect.value=view;coordSelect.value=coordinates;coordSelect.disabled=view==='surface';
    controls.querySelector('[data-view-action="wire"]').disabled=view!=='surface';ref.setAttribute('aria-pressed',String(reference));four.setAttribute('aria-pressed',String(overview));
    canvas.dataset.view=view;canvas.dataset.time=t.toFixed(2);canvas.dataset.overview=String(overview);canvas.dataset.coordinates=coordinates;canvas.dataset.zoom=zoom.toFixed(3);canvas.dataset.rotation=`${yaw.toFixed(3)},${pitch.toFixed(3)}`;
    canvas.setAttribute('aria-label',`${overview?'Four numerical times':'Numerical time '+label(t)}; ${view==='surface'?'rotational surface in R3':view==='profile2'?'meridian of a surface in R3':'meridian of a hypersurface in R4, not a surface in R3'}. ${view!=='surface'&&coordinates==='centered'?'Neck translated to height zero, without rescaling.':''} Arrow keys rotate the surface; plus and minus zoom.`);
    help.textContent=view==='surface'?'Drag or use arrow keys to rotate all views together. The four surfaces share one spatial scale. Open rims cut the noncompact ends at x = ±2. Switch to a meridian view for later times and the forward limit.':'The blue curve is the numerical profile. Gold dashed is the forward limiting shape in neck-centered coordinates. Gray dotted is the stationary catenoid when selected. Each four-time comparison uses one spatial scale; + / − zoom.';
  }
  function text(s,x,y,size=13,color=INK){ctx.fillStyle=color;ctx.font=`${size}px system-ui,sans-serif`;ctx.fillText(s,x,y);}
  function stroke(points,screen,color,width=1.5,dash=[]){ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...screen(p)):ctx.moveTo(...screen(p)));ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.stroke();ctx.setLineDash([]);}
  function panel(box,time,index){
    const[x,y,w,h]=box,m=model(),f=frameAt(m,time);ctx.save();ctx.beginPath();ctx.rect(x,y,w,h);ctx.clip();ctx.fillStyle='white';ctx.fillRect(x,y,w,h);
    if(view==='surface'){
      const sc=Math.min((w-24)/15,(h-72)/10)*zoom,cx=x+w/2,cy=y+34+(h-72)/2,screen=p=>[cx+sc*p[0],cy-sc*p[1]],{q,faces}=surfaceScene(data,time,yaw,pitch);
      stroke([rotate([0,0,-3.8],yaw,pitch),rotate([0,0,3.8],yaw,pitch)],screen,'#a4b9c2',1,[4,4]);
      for(const a of faces){ctx.beginPath();a.f.forEach((j,k)=>k?ctx.lineTo(...screen(q[j])):ctx.moveTo(...screen(q[j])));ctx.closePath();ctx.fillStyle=a.color;ctx.fill();ctx.strokeStyle=wire?'#163c4b66':a.color;ctx.lineWidth=wire?.5:.55;ctx.stroke();}
      if(reference)for(let j=0;j<8;j++){const angle=2*Math.PI*j/8;stroke(data.mesh_x.map(z=>rotate([Math.cosh(z)*Math.cos(angle),Math.cosh(z)*Math.sin(angle),z],yaw,pitch)),screen,GOLD,1,[3,3]);}
    }else{
      const centered=coordinates==='centered',xr=m.n===2?2.2:1.1,yr=centered?(m.n===2?4:3.9):(m.n===2?41:53),left=35,right=18,top=41,bottom=64;
      const sx=(w-left-right)/(2*xr)*zoom,sy=(h-top-bottom)/yr*zoom,cx=x+w/2+8,cy=y+h-bottom;
      const screen=([a,b])=>[cx+sx*a,cy-sy*b];
      stroke([[-xr,0],[xr,0]],screen,'#b6c8d0',1);stroke([[0,0],[0,yr]],screen,'#e1eaee',1);
      for(const q of [-1,0,1]){const [ax,ay]=screen([q*(m.n===2?2:1),0]);text(String(q*(m.n===2?2:1)),ax-4,ay+17,11,MUTED);}
      ctx.save();ctx.beginPath();ctx.rect(x+left,y+top,w-left-right,h-top-bottom);ctx.clip();
      if(centered){const points=m.x.map(a=>[a,limitHeight(m,a)]);stroke(points,screen,GOLD,2,[6,4]);}
      if(reference)stroke(m.x.map((a,j)=>[a,m.reference[j]-(centered?1:0)]),screen,'#8a9ba3',1.3,[2,4]);
      stroke(m.x.map((a,j)=>[a,f.u[j]-(centered?f.neck_radius:0)]),screen,BLUE,2.5);ctx.restore();
      text(centered?'u − u(0,t)':'radius u',x+8,y+48,11,MUTED);text('x',x+w-14,cy+16,11,MUTED);
    }
    text(`${index?index+'. ':''}t = ${label(time)}`,x+12,y+24,overview?14:19);text(`Neck ≈ ${f.neck_radius.toFixed(3)}`,x+12,y+h-15,12,MUTED);ctx.restore();
  }
  function draw(){
    sync();const W=stage.clientWidth,H=stage.clientHeight,dpr=Math.min(devicePixelRatio||1,2);canvas.width=W*dpr;canvas.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,W,H);
    text(view==='surface'?'ℝ³ · numerical MCF · fixed spatial scale':`${view==='profile2'?'ℝ³':'ℝ⁴'} · meridian only · ${coordinates==='centered'?'neck translated to zero':'original radius'}`,12,22,W<440?11:14);
    if(overview){const gap=10,w=(W-3*gap)/2,h=(H-48-3*gap)/2;snapshots().forEach((t,i)=>panel([gap+(i%2)*(w+gap),38+gap+Math.floor(i/2)*(h+gap),w,h],t,i+1));}
    else panel([8,38,W-16,H-46],t,0);
    const f=frameAt(model(),t);status.textContent=overview?'Forward order: top left → top right → bottom left → bottom right. The same camera and spatial scale are used in every panel.':`Neck radius ≈ ${f.neck_radius.toFixed(3)}; outward speed ≈ ${f.neck_speed.toFixed(3)}; meridian curvature at the neck ≈ ${f.meridian_tip_curvature.toFixed(3)}. Slider positions interpolate saved numerical slices.`;
  }
  function tick(now){if(!playing)return;if(last)t=Math.min(interval().max,t+(now-last)/14000*(interval().max-interval().min));last=now;draw();if(t>=interval().max)stop();else raf=requestAnimationFrame(tick);}
  play.addEventListener('click',()=>{if(playing){stop();return;}overview=false;if(t>=interval().max)t=interval().min;playing=true;last=0;play.textContent='Pause';play.setAttribute('aria-pressed','true');raf=requestAnimationFrame(tick);});
  four.addEventListener('click',()=>{stop();overview=true;draw();});
  viewSelect.addEventListener('change',()=>{stop();view=viewSelect.value;t=0;zoom=1;overview=true;draw();});
  coordSelect.addEventListener('change',()=>{coordinates=coordSelect.value;zoom=1;draw();});ref.addEventListener('click',()=>{reference=!reference;draw();});
  slider.addEventListener('input',()=>{stop();t=Number(slider.value);overview=false;draw();});
  for(const b of controls.querySelectorAll('[data-view-action]'))b.addEventListener('click',()=>{const a=b.dataset.viewAction;if(a==='in')zoom=Math.min(3,zoom*1.2);if(a==='out')zoom=Math.max(.5,zoom/1.2);if(a==='wire'){wire=!wire;b.setAttribute('aria-pressed',String(wire));}if(a==='reset'){stop();view='surface';coordinates='centered';t=0;overview=true;zoom=1;yaw=data.view.yaw;pitch=data.view.pitch;wire=false;reference=false;controls.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed','false');}draw();});
  let pointer=null;canvas.addEventListener('pointerdown',e=>{if(view!=='surface')return;pointer=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});canvas.addEventListener('pointermove',e=>{if(!pointer)return;yaw+=(e.clientX-pointer[0])*.008;pitch+=(e.clientY-pointer[1])*.008;pointer=[e.clientX,e.clientY];draw();});for(const name of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(name,()=>pointer=null);
  canvas.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-'].includes(e.key))return;if(e.key.startsWith('Arrow')&&view!=='surface')return;e.preventDefault();if(e.key==='ArrowLeft')yaw-=.13;if(e.key==='ArrowRight')yaw+=.13;if(e.key==='ArrowUp')pitch-=.13;if(e.key==='ArrowDown')pitch+=.13;if(['+','=','-'].includes(e.key))zoom=Math.max(.5,Math.min(3,zoom*(e.key==='-'?1/1.2:1.2)));draw();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});new IntersectionObserver(e=>{if(!e[0].isIntersecting)stop();}).observe(figure);
  controls.hidden=false;help.hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;new ResizeObserver(draw).observe(stage);draw();
}
