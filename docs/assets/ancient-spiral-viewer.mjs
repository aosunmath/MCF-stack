// Unit angular speed. Geometry in R²; all displayed times refer to the asymptotic model.
const PI=Math.PI, BLUE='#21667f', ORANGE='#b85a2a', INK='#183f52', MUTED='#526b77';
export function interpolate(table,x,column=1){
  if(x<table[0][0] || x>table.at(-1)[0])throw new RangeError('Outside the sampled model domain');
  let lo=0,hi=table.length-1;
  while(hi-lo>1){const m=(lo+hi)>>1;if(table[m][0]<=x)lo=m;else hi=m;}
  const a=table[lo],b=table[hi],w=(x-a[0])/(b[0]-a[0]);return a[column]*(1-w)+b[column]*w;
}
export function radiusAt(data,q){return Math.hypot(interpolate(data.branch,q),interpolate(data.branch,q,2));}
function root(f,a,b){
  let fa=f(a);if(fa*f(b)>0)throw new Error('Unbracketed cap intersection');
  for(let j=0;j<42;j++){const m=(a+b)/2;if(fa*f(m)<=0)b=m;else {a=m;fa=f(a);}}
  return (a+b)/2;
}
function rotate([x,y],a){return [x*Math.cos(a)-y*Math.sin(a),x*Math.sin(a)+y*Math.cos(a)];}
function smooth(x){if(x<=0)return 0;if(x>=1)return 1;const a=Math.exp(-1/x),b=Math.exp(-1/(1-x));return a/(a+b);}
export function correctedCap(data,t,p){
  const F=Math.sign(p)*interpolate(data.correction,Math.abs(p)),tau=-4*t;
  return [-Math.asin(Math.tanh(p))+F*Math.tanh(p)/tau,-Math.log(Math.cosh(p))-F/(tau*Math.cosh(p))];
}
export function spiralFrame(data,t){
  if(!Number.isFinite(t)||t<data.time.min||t>data.time.max)throw new RangeError('Time outside the ancient illustration interval');
  const R=radiusAt(data,-2*t),L=Math.log(-4*t),cut=-2*L;
  const toWorld=([u,v])=>rotate([R+u/R,v/R],-t);
  function arm(v,sign){
    const delta=root(d=>R*radiusAt(data,-2*t+d+sign*PI/2)*Math.sin(d)-v,-.7,0);
    const r=radiusAt(data,-2*t+delta+sign*PI/2);
    return {u:R*(r*Math.cos(delta)-R),q:-2*t+delta+sign*PI/2};
  }
  const plus=arm(cut,1),minus=arm(cut,-1);
  const branch=(q,sign)=>{
    const points=[];
    for(const [angle,x,y] of data.branch){if(angle>=q)break;points.push(rotate([sign*x,sign*y],t));}
    points.push(rotate([sign*interpolate(data.branch,q),sign*interpolate(data.branch,q,2)],t));return points;
  };
  const inner=branch(minus.q,-1).reverse(),outer=branch(plus.q,1);
  // Both branches meet at the origin with one tangent; there is no artificial inner cap.
  const body=inner.concat(outer.slice(1));
  const p0=root(p=>correctedCap(data,t,p)[1]-cut,-13,-1);
  const p1=root(p=>correctedCap(data,t,p)[1]-cut,1,13);
  const cap=[],local=[];
  for(let j=0;j<=240;j++){
    const p=p0+(p1-p0)*j/240;let [u,v]=correctedCap(data,t,p);
    const w=smooth((-v/L-.5)/1.5);
    if(w>0)u=(1-w)*u+w*arm(Math.max(cut,v),p<0?1:-1).u;
    local.push([u,v]);cap.push(toWorld([u,v]));
  }
  // Use identical join coordinates, avoiding roundoff gaps in the closed path.
  cap[0]=body.at(-1);cap[cap.length-1]=body[0];
  return {t,R,body,cap,local,tip:toWorld([0,0]),width:PI/R};
}

export function snapshotSVG(data){
  const path=(points,cx,cy,scale)=>points.filter((_,i)=>i%3===0||i===points.length-1).map(([x,y],i)=>`${i?'L':'M'}${(cx+x*scale).toFixed(2)},${(cy-y*scale).toFixed(2)}`).join(' ');
  const chunks=[`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 760" role="img" aria-labelledby="title desc"><title id="title">Ancient spiral: four times on the same spatial scale</title><desc id="desc">Numerical Yin–Yang arms, joined through the origin, and an orange corrected grim-reaper cap. The asymptotic model unwinds from t=-24 to -8. These are not computed ancient PDE slices.</desc><rect width="880" height="760" fill="#f7fafb"/><g font-family="system-ui,sans-serif" fill="${INK}"><text x="28" y="35" font-size="23" font-weight="600">Ancient spiral · forward in time</text><text x="28" y="61" font-size="15" fill="${MUTED}">Numerical rotating arms + asymptotic cap · same scale in all panels</text>`];
  data.snapshots.forEach((t,i)=>{
    const f=spiralFrame(data,t),x=28+(i%2)*432,y=82+Math.floor(i/2)*302,cx=x+198,cy=y+146,scale=10.4;
    chunks.push(`<rect x="${x}" y="${y}" width="410" height="286" rx="8" fill="white" stroke="#d8e2e7"/><text x="${x+16}" y="${y+28}" font-size="19" font-weight="600">${i+1}. t = ${t}</text>`);
    const b=path(f.body,cx,cy,scale),c=path(f.cap,cx,cy,scale);
    chunks.push(`<path d="${b} ${c.replace(/^M/,'L')} Z" fill="#e6f0f3"/><path d="${b}" fill="none" stroke="${BLUE}" stroke-width="1.3"/><path d="${c}" fill="none" stroke="${ORANGE}" stroke-width="3" stroke-linecap="round"/><circle cx="${cx}" cy="${cy}" r="2" fill="${INK}"/><text x="${x+16}" y="${y+268}" font-size="13" fill="${MUTED}">Cap radius ≈ ${f.R.toFixed(2)} · width ≈ ${f.width.toFixed(2)}</text>`);
  });
  chunks.push(`<text x="28" y="716" font-size="15">Blue arms rotate counterclockwise; the orange cap travels clockwise.</text><text x="28" y="741" font-size="14" fill="${MUTED}">Zhang–Olson–Khan–Angenent, §2 and Appendix A. Asymptotic model, not an exact ancient flow.</text></g></svg>`);
  return chunks.join('\n');
}

export function initAncientSpiralFigure(figure,data){
  figure.classList.add('ancient-spiral-figure');
  const stage=figure.querySelector('.soliton-stage'),canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d');
  if(!ctx)return;
  const controls=figure.querySelector('.soliton-controls'),help=figure.querySelector('.soliton-help'),status=figure.querySelector('.soliton-status');
  let t=data.time.value,overview=true,zoom=1,playing=false,last=0,raf=0;
  const frames=data.snapshots.map(t=>spiralFrame(data,t)),radius=10.7;
  const overviewButton=document.createElement('button');overviewButton.type='button';overviewButton.textContent='Four times';
  const play=document.createElement('button');play.type='button';play.textContent='Play forward';
  const label=document.createElement('label'),output=document.createElement('output'),slider=document.createElement('input');
  slider.type='range';slider.min=data.time.min;slider.max=data.time.max;slider.step='.02';slider.value=t;slider.setAttribute('aria-label','Ancient spiral model time');
  label.append(output,slider);controls.prepend(overviewButton,play,label);
  figure.querySelector('[data-view-action="wire"]').hidden=true;
  const legend=document.createElement('p');legend.className='spiral-legend';
  legend.innerHTML='<span><i style="background:#21667f"></i>Yin–Yang arms: counterclockwise</span><span><i style="background:#b85a2a"></i>Closing cap: clockwise</span>';
  stage.after(legend);
  help.textContent='Four times uses one spatial scale. Move the time slider or play to follow a single curve; its inset enlarges the moving cap in the paper’s (u, v) coordinates. Zoom changes only the main drawing.';
  function sync(){
    output.textContent=`t = ${t.toFixed(2)}`;slider.value=t;
    play.textContent=playing?'Pause':'Play forward';play.setAttribute('aria-pressed',String(playing));overviewButton.setAttribute('aria-pressed',String(overview));
    canvas.dataset.time=t.toFixed(2);canvas.dataset.view=overview?'snapshots':'single';canvas.dataset.zoom=zoom.toFixed(2);
    canvas.setAttribute('aria-label',overview?'Four asymptotic spiral curves, at times -24, -18, -12 and -8, on the same scale.':`Asymptotic spiral at t=${t.toFixed(2)}, with enlarged closing cap. Plus and minus zoom.`);
  }
  function line(points,screen,color,width,fill=false){
    ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...screen(p)):ctx.moveTo(...screen(p)));
    if(fill){ctx.closePath();ctx.fillStyle=color;ctx.fill();}else {ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();}
  }
  function text(s,x,y,size=13,color=INK){ctx.fillStyle=color;ctx.font=`${size}px system-ui,sans-serif`;ctx.fillText(s,x,y);}
  function drawCurve(f,box,index){
    const [x,y,w,h]=box,scale=Math.min(w*.45,(h-58)*.48)/radius*zoom,cx=x+w/2,cy=y+30+(h-50)/2;
    const screen=([a,b])=>[cx+scale*a,cy-scale*b];
    ctx.save();ctx.beginPath();ctx.rect(x,y,w,h);ctx.clip();
    line(f.body.concat(f.cap.slice(1)),screen,'#e4eff2',1,true);
    line(f.body,screen,BLUE,overview?1.25:1.6);line(f.cap,screen,ORANGE,3);
    const [tx,ty]=screen(f.tip);ctx.strokeStyle=ORANGE;ctx.lineWidth=1;ctx.beginPath();ctx.arc(tx,ty,7,0,2*PI);ctx.stroke();
    text(`${index?index+'. ':''}t = ${f.t.toFixed(2)}`,x+12,y+24,16);
    text(`R ≈ ${f.R.toFixed(2)}   w ≈ ${f.width.toFixed(2)}`,x+12,y+h-12,12,MUTED);
    ctx.restore();
    return {screen,scale};
  }
  function draw(){
    sync();const {width:W,height:H}=stage.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2);
    canvas.width=Math.round(W*dpr);canvas.height=Math.round(H*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,W,H);
    if(overview){
      const gap=12,w=(W-3*gap)/2,h=(H-3*gap)/2;
      frames.forEach((f,i)=>{const x=gap+(i%2)*(w+gap),y=gap+Math.floor(i/2)*(h+gap);ctx.fillStyle='white';ctx.fillRect(x,y,w,h);drawCurve(f,[x,y,w,h],i+1);});
      status.textContent='Forward order: top left → top right → bottom left → bottom right. All four are on the same spatial scale.';
    }else{
      const f=spiralFrame(data,t),narrow=W<560;
      drawCurve(f,[8,0,narrow?W-16:W-196,narrow?H-220:H]);
      const box=narrow?[W/2-93,H-216,186,204]:[W-190,72,180,290];
      const [x,y,w,h]=box;ctx.fillStyle='white';ctx.fillRect(...box);ctx.strokeStyle='#d3e0e6';ctx.lineWidth=1;ctx.strokeRect(...box);
      text('Cap enlarged',x+12,y+22,14);text('Moving (u, v) frame',x+12,y+42,11,MUTED);
      const sc=Math.min((w-30)/5,(h-88)/10),screen=([u,v])=>[x+w/2+u*sc,y+65-v*sc];
      ctx.save();ctx.beginPath();ctx.rect(x,y+49,w,h-53);ctx.clip();
      const grim=Array.from({length:161},(_,i)=>{const p=-9+18*i/160;return [-Math.asin(Math.tanh(p)),-Math.log(Math.cosh(p))];});
      ctx.setLineDash([4,4]);line(grim,screen,'#9caeb6',1.2);ctx.setLineDash([]);line(f.local,screen,ORANGE,2.3);ctx.restore();
      status.textContent=`Cap radius R ≈ ${f.R.toFixed(3)}; leading width π/R ≈ ${f.width.toFixed(3)}. Dashed inset: limiting grim reaper. Orange: corrected cap and its join to the arms.`;
    }
  }
  function stop(){playing=false;cancelAnimationFrame(raf);sync();}
  function tick(now){
    if(!playing)return;if(last)t=Math.min(data.time.max,t+(now-last)*.00065);last=now;draw();
    if(t>=data.time.max)stop();else raf=requestAnimationFrame(tick);
  }
  play.addEventListener('click',()=>{if(playing){stop();return;}overview=false;if(t>=data.time.max)t=data.time.min;playing=true;last=0;sync();raf=requestAnimationFrame(tick);});
  overviewButton.addEventListener('click',()=>{stop();overview=true;draw();});
  slider.addEventListener('input',()=>{t=Number(slider.value);stop();overview=false;draw();});
  for(const button of controls.querySelectorAll('[data-view-action]'))button.addEventListener('click',()=>{
    const action=button.dataset.viewAction;if(action==='in')zoom=Math.min(3,zoom*1.2);if(action==='out')zoom=Math.max(.5,zoom/1.2);
    if(action==='reset'){stop();zoom=1;t=data.time.value;overview=true;}draw();
  });
  canvas.addEventListener('keydown',e=>{if(['+','=','-'].includes(e.key)){e.preventDefault();zoom=Math.max(.5,Math.min(3,zoom*(e.key==='-'?1/1.2:1.2)));draw();}});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  new IntersectionObserver(entries=>{if(!entries[0].isIntersecting)stop();}).observe(figure);
  controls.hidden=false;help.hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;
  new ResizeObserver(draw).observe(stage);draw();
}
