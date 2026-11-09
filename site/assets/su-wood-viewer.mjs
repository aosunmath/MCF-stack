// Su–Wood, arXiv:2507.01345v1, (31), Theorem 5.6 and Proposition 5.9.
// Exact m=3, SO(2) coordinates. Finite mesh sampling, no ODE/time integration.
export const TIMES=[-2,0,2];
export const DOMAIN={p:2,b:1.2};
const INK='#183f52',TAU=2*Math.PI;
export function profilePoint(p,b,mu=1,t=0){
  if(![p,b,mu,t].every(Number.isFinite)||mu<=0)throw new RangeError('Finite coordinates and positive profile scale required.');
  const a=Math.asinh(p),u=(a-b)/2,v=(a+b)/2;
  return [mu*Math.cosh(b),mu*p,(mu*mu*Math.cosh(2*v)-Math.cosh(2*u))/2,mu*mu*v-u];
}
export function lift([r,s,c,d],theta=0){
  if(!Number.isFinite(theta))throw new RangeError('Finite orbit angle required.');
  return [r*Math.cos(theta),s*Math.cos(theta),r*Math.sin(theta),s*Math.sin(theta),c,d];
}
export const projectProfile=([r,s,c,d],angle=0)=>[s*Math.cos(angle)+r*Math.sin(angle),c,d];
export const projectOrbit=([r,s,u,v,c,d])=>[s,c,(d+u)/Math.SQRT2];
export function profileMesh(mu=1,t=0,n=40){
  if(!Number.isInteger(n)||n<4||n>160)throw new RangeError('Mesh subdivisions must be 4–160.');
  const vertices=[],faces=[],paths=[];
  for(let j=0;j<=n;j++)for(let i=0;i<=n;i++)vertices.push(profilePoint(DOMAIN.p*(2*i/n-1),DOMAIN.b*(2*j/n-1),mu,t));
  const k=(j,i)=>j*(n+1)+i;
  for(let j=0;j<n;j++)for(let i=0;i<n;i++)faces.push([k(j,i),k(j,i+1),k(j+1,i+1),k(j+1,i)]);
  for(let i=0;i<=n;i+=4){paths.push(Array.from({length:n+1},(_,j)=>k(j,i)));paths.push(Array.from({length:n+1},(_,j)=>k(i,j)));}
  return {vertices,faces,paths};
}
const rotate=(p,yaw,pitch)=>{
  // Camera places Re W vertically, with Im W along the ground plane.
  const a=p[0]*Math.cos(yaw)-p[2]*Math.sin(yaw),b=p[0]*Math.sin(yaw)+p[2]*Math.cos(yaw);
  return [a,p[1]*Math.cos(pitch)-b*Math.sin(pitch),p[1]*Math.sin(pitch)+b*Math.cos(pitch)];
};
const phaseColor=(phase,light=1)=>{
  const f=(phase+Math.PI/2)/Math.PI,A=[47,126,170],B=[224,135,66];
  return `rgb(${A.map((c,i)=>Math.round((c*(1-f)+B[i]*f)*light+245*(1-light)*.25)).join(',')})`;
};
export function scene({mu=1,t=0,yaw=.65,pitch=.65,angle=0,theta=.45,orbits=false,wire=false}={}){
  const mesh=profileMesh(mu,t),transform=q=>rotate(orbits?projectOrbit(lift(q,theta)):projectProfile(q,angle),yaw,pitch);
  const points=mesh.vertices.map(transform),items=[];
  const line=(q,color,width=1,dash=[])=>{
    for(let i=1;i<q.length;i++)items.push({points:[q[i-1],q[i]],stroke:color,width,dash,depth:(q[i-1][2]+q[i][2])/2+.003});
  };
  if(!wire)for(const face of mesh.faces){
    const p=face.map(i=>points[i]),a=p[1].map((v,i)=>v-p[0][i]),b=p[3].map((v,i)=>v-p[0][i]);
    const n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],norm=Math.hypot(...n);
    const light=.65+.33*Math.abs((n[0]*.2+n[1]*.5+n[2]*.84)/(norm||1));
    const phase=face.reduce((s,i)=>s+Math.atan2(mesh.vertices[i][1],mesh.vertices[i][0]),0)/4;
    const fill=phaseColor(phase,light);
    items.push({points:p,fill,stroke:fill,width:.6,depth:p.reduce((s,v)=>s+v[2],0)/4});
  }
  for(const path of mesh.paths)line(path.map(i=>points[i]),wire?'#365c70':'#284e624d',wire?.9:.5);
  // Parameter axes on the surface, with one fixed marked point at their meeting.
  for(const axis of [0,1])line(Array.from({length:81},(_,i)=>transform(profilePoint(axis?0:2*(2*i/80-1),axis?1.2*(2*i/80-1):0,mu,t))),'#f5eedb',1.7);
  if(orbits)for(const p of [-1.5,0,1.5])for(const b of [-.85,0,.85]){
    const q=profilePoint(p,b,mu,t);
    line(Array.from({length:81},(_,i)=>rotate(projectOrbit(lift(q,TAU*i/80)),yaw,pitch)),'#935a2b',1.2,[3,3]);
  }
  const marker=transform(profilePoint(0,0,mu,t));
  return {items:items.sort((a,b)=>a.depth-b.depth),marker};
}
export function panel(box,options={}){
  const [x,y,w,h]=box,scale=Math.min((w-34)/7,(h-65)/7)*(options.zoom||1);
  const screen=p=>[x+w/2+p[0]*scale,y+h/2+6-p[1]*scale];
  const data=scene(options);
  return {scale,items:data.items.map(o=>({...o,points:o.points.map(screen)})),marker:screen(data.marker)};
}
export function snapshotSVG(){
  let svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1010" role="img" aria-labelledby="title desc"><title id="title">Su–Wood: the same geometry at every time</title><desc id="desc">Exact m=3 profile surface, projected from C2. A large view and three identical time panels. The full stationary special Lagrangian is a three-manifold in C3, reconstructed by a circle action. These projected surfaces are not surface mean curvature flows.</desc><rect width="1000" height="1010" fill="#f7fafb"/><g font-family="Arial,Helvetica,sans-serif" fill="#183f52"><text x="28" y="40" font-size="27" font-weight="600">Su–Wood: stationary at every time</text><text x="28" y="70" font-size="18">Exact profile surface · m = 3 · μ₁ = μ₂ = 1 · φ = 0</text>';
  const draw=(box,title,opts={})=>{
    const [x,y,w,h]=box,p=panel(box,opts);
    svg+=`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="8" fill="#edf3f5"/><text x="${x+15}" y="${y+27}" font-size="19" font-weight="600">${title}</text>`;
    for(const o of p.items)svg+=`<${o.fill?'polygon':'polyline'} points="${o.points.map(q=>q.map(a=>a.toFixed(2)).join(',')).join(' ')}" fill="${o.fill||'none'}" stroke="${o.stroke}" stroke-width="${o.width}"/>`;
    svg+=`<circle cx="${p.marker[0]}" cy="${p.marker[1]}" r="4" fill="#183f52" stroke="white" stroke-width="1.5"/><path d="M${x+w-100} ${y+h-20}h${p.scale}" stroke="#183f52" stroke-width="2"/><text x="${x+w-100}" y="${y+h-29}" font-size="13">1 unit</text>`;
  };
  draw([20,90,960,495],'Projection (Im Z, Re W, Im W) = (p, p sinh b, b)',{zoom:1.35});
  TIMES.forEach((t,i)=>draw([20+i*326,603,308,280],`t = ${t<0?'−2':t} · H = 0`,{t}));
  svg+='<text x="28" y="920" font-size="18">Same camera, scale, crop and marked point at t = −2, 0, 2.</text><text x="28" y="950" font-size="17">Color: arg Z, from blue (negative) to orange (positive). Re Z = cosh b is omitted.</text><text x="28" y="980" font-size="17">A profile of a 3-manifold in C³; not a surface MCF in R³. Su–Wood (31).</text></g></svg>\n';
  return svg;
}

export function initSuWoodFigure(figure){
  const canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d'),stage=figure.querySelector('.soliton-stage');
  const controls=figure.querySelector('.soliton-controls'),help=figure.querySelector('.soliton-help'),status=figure.querySelector('.soliton-status');
  figure.classList.add('suwood-figure');
  let mode='times',t=0,mu=1,angle=0,theta=.45,yaw=.65,pitch=.65,zoom=1,wire=false,playing=false,raf=0,last=0;
  controls.replaceChildren();
  const button=(name,fn)=>{const b=document.createElement('button');b.type='button';b.textContent=name;b.addEventListener('click',fn);controls.append(b);return b;};
  const stop=()=>{playing=false;last=0;cancelAnimationFrame(raf);play.textContent='Play time';play.setAttribute('aria-pressed','false');};
  const viewLabel=document.createElement('label'),view=document.createElement('select');view.setAttribute('aria-label','Geometry view');
  for(const [value,label] of [['times','Compare three times'],['profile','Explore profile'],['orbits','Circle symmetry in R⁶']]){const o=document.createElement('option');o.value=value;o.textContent=label;view.append(o);}viewLabel.append('View',view);controls.append(viewLabel);
  view.addEventListener('change',()=>{stop();mode=view.value;draw();});
  const play=button('Play time',()=>{if(playing){stop();return;}if(t>=2)t=-2;mode='profile';playing=true;play.textContent='Pause';play.setAttribute('aria-pressed','true');raf=requestAnimationFrame(tick);draw();});
  const slider=(name,min,max,step,callback)=>{const label=document.createElement('label'),output=document.createElement('output'),input=document.createElement('input');input.type='range';input.min=min;input.max=max;input.step=step;input.setAttribute('aria-label',name);label.append(output,input);controls.append(label);input.addEventListener('input',()=>{callback(Number(input.value));draw();});return {label,output,input};};
  const time=slider('Mean curvature flow time',-2,2,.01,v=>{stop();t=v;mode='profile';});
  const ratio=slider('Second Lawlor profile scale, not time',.6,1.4,.02,v=>mu=v);
  const fourth=slider('Projection angle, not time',-60,60,1,v=>angle=v*Math.PI/180);
  const orbit=slider('Circle orbit angle, not time',0,360,1,v=>theta=v*Math.PI/180);
  button('Zoom +',()=>{zoom=Math.min(2.4,zoom*1.2);draw();});button('Zoom −',()=>{zoom=Math.max(.5,zoom/1.2);draw();});
  const mesh=button('Mesh',()=>{wire=!wire;draw();});
  button('Reset view',()=>{stop();mode='times';t=0;mu=1;angle=0;theta=.45;yaw=.65;pitch=.65;zoom=1;wire=false;draw();});
  const note=document.createElement('p');note.className='suwood-note';controls.after(note);
  help.textContent='Drag or use arrow keys to rotate; + / − zoom. Blue → orange records arg Z. The marked parameter point stays fixed at every time. White curves mark p = 0 and b = 0.';
  function draw(){
    stage.dataset.view=mode;view.value=mode;orbit.label.hidden=mode!=='orbits';fourth.label.hidden=mode==='orbits';
    const {width:W,height:H}=stage.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2),mobile=W<520;
    canvas.width=Math.round(W*dpr);canvas.height=Math.round(H*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,W,H);
    ctx.fillStyle=INK;ctx.font=`600 ${mobile?12:15}px system-ui`;ctx.fillText('Stationary MCF: Lₜ = L₀ for all t ∈ R',12,24);
    ctx.font=`${mobile?10:12}px system-ui`;ctx.fillText(mode==='orbits'?'A 2D leaf + sampled SO(2) orbits in R⁶':'Exact 2D profile of a 3-manifold in C³',12,45);
    const boxes=mode==='times'?(mobile?TIMES.map((v,i)=>[v,[8,56+i*(H-60)/3,W-16,(H-68)/3]]):TIMES.map((v,i)=>[v,[8+i*(W-8)/3,56,(W-32)/3,H-64]])):[[t,[8,56,W-16,H-64]]];
    for(const [value,box] of boxes){
      const [x,y,w,h]=box,p=panel(box,{mu,t:value,angle,theta,yaw,pitch,zoom,wire,orbits:mode==='orbits'});
      ctx.fillStyle='#edf3f5';ctx.fillRect(x,y,w,h);ctx.save();ctx.beginPath();ctx.rect(x,y+32,w,h-57);ctx.clip();
      for(const o of p.items){ctx.beginPath();o.points.forEach((v,i)=>i?ctx.lineTo(...v):ctx.moveTo(...v));if(o.fill){ctx.closePath();ctx.fillStyle=o.fill;ctx.fill();}ctx.strokeStyle=o.stroke;ctx.lineWidth=o.width;ctx.setLineDash(o.dash||[]);ctx.stroke();}
      ctx.setLineDash([]);ctx.beginPath();ctx.arc(...p.marker,3.5,0,TAU);ctx.fillStyle=INK;ctx.fill();ctx.strokeStyle='#fff';ctx.lineWidth=1.2;ctx.stroke();ctx.restore();
      ctx.fillStyle=INK;ctx.font=`600 ${mobile?13:14}px system-ui`;ctx.fillText(`t = ${value.toFixed(mode==='times'?0:2).replace('-','−')}`,x+10,y+23);
      ctx.font='11px system-ui';ctx.fillText('H = 0 · fixed geometry',x+10,y+h-10);
      if(w>230){ctx.strokeStyle=INK;ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(x+w-75,y+h-17);ctx.lineTo(x+w-75+p.scale,y+h-17);ctx.stroke();ctx.fillText('1 unit',x+w-75,y+h-25);}
    }
    time.input.value=t;time.output.textContent=`Time t = ${t.toFixed(2)}`;ratio.input.value=mu;ratio.output.textContent=`μ₂ = ${mu.toFixed(2)} (shape)`;
    fourth.input.value=Math.round(angle*180/Math.PI);fourth.output.textContent=`Projection ${Math.round(angle*180/Math.PI)}°`;orbit.input.value=Math.round(theta*180/Math.PI);orbit.output.textContent=`Orbit θ = ${Math.round(theta*180/Math.PI)}°`;
    mesh.setAttribute('aria-pressed',String(wire));
    note.textContent=mode==='orbits'?'Circle reconstruction: X = (Z cos θ, Z sin θ, W) in C³. Brown dotted curves are sampled spatial SO(2) orbits. The colored sheet fixes θ; together these leaves form the 3-manifold. Projection: (Im z₁, Re z₃, (Im z₃ + Re z₂)/√2). Orbit angle is not flow time.':'Profile projection: (Im Z cos α + Re Z sin α, Re W, Im W). At α = 0 and μ₂ = 1 this is (p, p sinh b, b); the omitted coordinate is Re Z = cosh b. This is a 2D profile in C², not a surface MCF in R³. Apparent projection crossings do not imply intersections in C³.';
    status.textContent=`${mode==='times'?'Three identical time slices, using the same camera and scale. ':`Time t = ${t.toFixed(2)}; the geometry is unchanged. `}The full special Lagrangian has H = 0. μ₁ = 1, φ = 0; μ₂ changes the stationary example. Display crop: |p| ≤ 2, |b| ≤ 1.2; cut edges are not boundaries of the complete manifold.`;
    Object.assign(canvas.dataset,{view:mode,time:t.toFixed(2),mu:mu.toFixed(2),projection:angle.toFixed(3),orbit:theta.toFixed(3),zoom:zoom.toFixed(3),rotation:[yaw,pitch].join(',')});
    canvas.setAttribute('aria-label',`Exact Su–Wood ${mode==='orbits'?'projected circle reconstruction':'profile surface'}. ${mode==='times'?'Identical times −2, 0, 2.':`Time ${t.toFixed(2)}.`} Stationary three-manifold in C3; mean curvature zero.`);
  }
  function tick(now){if(!playing)return;if(last)t=Math.min(2,t+Math.min((now-last)/1000,.1)*.5);last=now;draw();if(t>=2)stop();else raf=requestAnimationFrame(tick);}
  let drag=null;canvas.addEventListener('pointerdown',e=>{drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;yaw+=(e.clientX-drag[0])*.008;pitch=Math.max(-1.4,Math.min(1.4,pitch+(e.clientY-drag[1])*.008));drag=[e.clientX,e.clientY];draw();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>drag=null);
  canvas.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-'].includes(e.key))return;e.preventDefault();if(e.key==='ArrowLeft')yaw-=.12;if(e.key==='ArrowRight')yaw+=.12;if(e.key==='ArrowUp')pitch-=.12;if(e.key==='ArrowDown')pitch+=.12;if(['+','=','-'].includes(e.key))zoom=Math.max(.5,Math.min(2.4,zoom*(e.key==='-'?1/1.2:1.2)));draw();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});new IntersectionObserver(e=>{if(!e[0].isIntersecting)stop();}).observe(figure);
  figure.querySelector('img').hidden=true;canvas.hidden=false;controls.hidden=false;help.hidden=false;new ResizeObserver(draw).observe(stage);draw();
}
