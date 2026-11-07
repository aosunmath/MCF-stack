// Original qualitative model, never a numerical solution of the Chen–Sun PDE.
const PI=Math.PI;
const BLUE='#267b91', ORANGE='#be7545', GOLD='#9b6130', INK='#183f52', MUTED='#526b77';
export const STAGES=[
  {name:'t₁ · finite time',a:.52,h:.20,note:'Two open polar necks'},
  {name:'t₂ > t₁ · finite time',a:.23,h:.095,note:'Sheets closer; smaller necks'},
  {name:'t₃ > t₂ · finite time',a:.065,h:.028,note:'Still connected and smooth'},
  {name:'t → ∞ · limit',a:0,h:0,note:'One minimal sphere, multiplicity 2',limit:true},
];
export function profile(s,a,h){
  return [PI/2-(PI/2-a)*Math.cos(s),h*Math.tanh(1.7*Math.sin(s))/Math.tanh(1.7)];
}
export function radialPoint(x,y,theta){
  const r=1+2*y;
  return [r*Math.sin(x)*Math.cos(theta),r*Math.sin(x)*Math.sin(theta),r*Math.cos(x)];
}
export function finiteStage(q){
  if(!Number.isFinite(q)||q<0||q>1)throw new RangeError('Schematic stage must lie in [0, 1]');
  return {a:.52*(.065/.52)**q,h:.20*(.028/.20)**q,name:'Finite-time stage',note:'Schematic order; no calibrated time'};
}
export function surfaceMesh(frame,cutaway=true,ns=128,nt=64){
  const vertices=[],faces=[],sheets=[];
  // Remove a front-facing wedge for a cutaway; its edges are not boundaries of M(t).
  const lo=cutaway?PI*.92:0,span=cutaway?PI*1.5:2*PI;
  for(let i=0;i<=ns;i++)for(let j=0;j<=nt;j++){
    const [x,y]=frame.limit?[PI*i/ns,0]:profile(2*PI*i/ns,frame.a,frame.h);
    vertices.push(radialPoint(x,y,lo+span*j/nt));
  }
  for(let i=0;i<ns;i++)for(let j=0;j<nt;j++){
    const k=i*(nt+1)+j;
    faces.push([k,k+1,k+nt+2,k+nt+1]);
    sheets.push(frame.limit?0:Math.sin(2*PI*(i+.5)/ns)>0?1:-1);
  }
  return {vertices,faces,sheets};
}
function rotate([x,y,z],yaw,pitch){
  const u=x*Math.cos(yaw)-y*Math.sin(yaw),v=x*Math.sin(yaw)+y*Math.cos(yaw);
  return [u,z*Math.cos(pitch)-v*Math.sin(pitch),z*Math.sin(pitch)+v*Math.cos(pitch)];
}
function shade(hex,light){
  return '#'+[1,3,5].map(i=>Math.round(Math.min(255,parseInt(hex.slice(i,i+2),16)*light)).toString(16).padStart(2,'0')).join('');
}
export function scene(width=960,{overview=true,frame=STAGES[0],yaw=-.46,pitch=.23,zoom=1,cutaway=true,wire=false}={}){
  const columns=overview&&width>=560?2:1,frames=overview?STAGES:[frame],gap=14;
  const cardW=(width-gap*(columns+1))/columns,cardH=430,header=56;
  const height=header+Math.ceil(frames.length/columns)*(cardH+gap)+20,items=[];
  const text=(x,y,value,size=14,color=INK,bold=false,anchor='start')=>items.push({kind:'text',x,y,value,size,color,bold,anchor});
  const line=(points,color,width=1,dash=false)=>items.push({kind:'line',points,color,width,dash});
  const poly=(points,color)=>items.push({kind:'poly',points,color});
  const rect=(x,y,w,h,color)=>items.push({kind:'rect',x,y,w,h,color});
  rect(0,0,width,height,'#f7fafb');
  text(16,22,'S² × ℝ · qualitative time sequence',width<400?16:20,INK,true);
  text(16,44,'Radial drawing; product metric is not preserved.',width<400?11:13,MUTED);
  frames.forEach((f,index)=>{
    const left=gap+(index%columns)*(cardW+gap),top=header+Math.floor(index/columns)*(cardH+gap);
    rect(left,top,cardW,cardH,'#ffffff');
    text(left+14,top+25,(overview?`${index+1}. `:'')+f.name,cardW<320?15:18,INK,true);
    text(left+14,top+47,f.note,cardW<320?11:13,MUTED);
    const cx=left+cardW/2,cy=top+185,sc=Math.min((cardW-50)/3.1,86)*zoom;
    const screen=p=>[cx+sc*p[0],cy-sc*p[1]];
    items.push({kind:'clipStart',x:left+8,y:top+60,w:cardW-16,h:250});
    const mesh=surfaceMesh(f,cutaway,96,48),points=mesh.vertices.map(p=>rotate(p,yaw,pitch));
    const ordered=mesh.faces.map((face,i)=>({face,i,depth:face.reduce((a,k)=>a+points[k][2],0)/4})).sort((a,b)=>a.depth-b.depth);
    for(const {face,i} of ordered){
      const p=face.map(k=>points[k]),a=p[1].map((v,k)=>v-p[0][k]),b=p[3].map((v,k)=>v-p[0][k]);
      const n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],len=Math.hypot(...n)||1;
      const light=.72+.3*Math.abs((n[0]*-.3+n[1]*.4+n[2]*.86)/len);
      poly(p.map(screen),shade(mesh.sheets[i]<0?'#e8b88d':'#8ec7d5',light));
      if(wire&&i%3===0)line([...p,p[0]].map(screen),'#557b87',.35);
    }
    // Both cut meridians make sheet separation and the return through each neck legible.
    if(cutaway)for(const theta of [PI*.92,PI*2.42]){
      for(const sign of f.limit?[0]:[1,-1]){
        const curve=Array.from({length:161},(_,i)=>{
          const [x,y]=f.limit?[PI*i/160,0]:profile(sign*PI*i/160,f.a,f.h);
          return screen(rotate(radialPoint(x,y,theta),yaw,pitch));
        });line(curve,sign<0?ORANGE:BLUE,1.7);
      }
    }
    if(!f.limit){
      for(const x of [f.a,PI-f.a]){
        const ring=Array.from({length:81},(_,i)=>screen(rotate(radialPoint(x,0,PI*.92+PI*1.5*i/80),yaw,pitch)));
        // Highlight only the part retained by the display cut.
        if(cutaway)line(ring,GOLD,1.7);
      }
    }
    items.push({kind:'clipEnd'});
    if(f.limit)text(cx,top+299,'× 2',22,INK,true,'middle');
    if(index===0&&!f.limit){
      for(const [sign,name] of [[1,'N neck'],[-1,'S neck']]){
        const target=screen(rotate([0,0,sign*Math.cos(f.a)],yaw,pitch));
        const ly=top+(sign>0?85:292);text(left+14,ly,name,11,GOLD);
        line([[left+54,ly-3],target],GOLD,.8);
      }
    }
    text(cx,top+321,cutaway?'Cutaway · display edges only':'Whole surface · no boundary',11,MUTED,false,'middle');
    // Orbit space: one profile point represents an entire latitude circle.
    const x0=left+28,x1=left+cardW-28,y0=top+369,sx=(x1-x0)/PI,sy=150;
    line([[x0,y0],[x1,y0]],'#9eb2ba',1,true);
    for(const x of [x0,(x0+x1)/2,x1])line([[x,y0-35],[x,y0+35]],'#d1dee3',1,true);
    if(f.limit){line([[x0,y0],[x1,y0]],BLUE,3);text(cx,y0-12,'same segment counted twice',11,MUTED,false,'middle');}
    else for(const sign of [1,-1]){
      const p=Array.from({length:161},(_,i)=>{const [x,y]=profile(sign*PI*i/160,f.a,f.h);return [x0+x*sx,y0-y*sy];});
      line(p,sign>0?BLUE:ORANGE,2.1);
      for(const x of [f.a,PI-f.a])rect(x0+x*sx-2,y0-2,4,4,GOLD);
    }
    text(x0,top+418,'N · x = 0',11,MUTED,false,'middle');text(cx,top+418,'x = π/2',11,MUTED,false,'middle');text(x1,top+418,'S · x = π',11,MUTED,false,'middle');
    text(left+9,y0-23,'y',12,MUTED);
  });
  return {width,height,items};
}
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
export function sceneSVG(s){
  const coords=p=>p.map(([x,y])=>`${x.toFixed(2)},${y.toFixed(2)}`).join(' ');
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${s.width} ${s.height}" role="img" aria-labelledby="title description"><title id="title">Chen–Sun immortal compact flow: three finite stages and the double-sphere limit</title><desc id="description">Original schematic, not computed PDE time slices. Blue and ochre sheets meet at two polar necks. Neck circles remain positive at every finite stage. The limit is a single sphere counted twice. Lower panels show the closed orbit-space profiles. The radial coordinate map (p,y) to (1+2y)p distorts the product metric.</desc><g font-family="system-ui, sans-serif">`+s.items.map((p,i)=>{
    if(p.kind==='clipStart')return `<defs><clipPath id="surface-clip-${i}"><rect x="${p.x}" y="${p.y}" width="${p.w}" height="${p.h}"/></clipPath></defs><g clip-path="url(#surface-clip-${i})">`;
    if(p.kind==='clipEnd')return '</g>';
    if(p.kind==='text')return `<text x="${p.x}" y="${p.y}" fill="${p.color}" font-size="${p.size}" font-weight="${p.bold?600:400}" text-anchor="${p.anchor}">${escape(p.value)}</text>`;
    if(p.kind==='rect')return `<rect x="${p.x}" y="${p.y}" width="${p.w}" height="${p.h}" fill="${p.color}"/>`;
    if(p.kind==='poly')return `<polygon points="${coords(p.points)}" fill="${p.color}" stroke="${p.color}" stroke-width=".3"/>`;
    return `<polyline points="${coords(p.points)}" fill="none" stroke="${p.color}" stroke-width="${p.width}" ${p.dash?'stroke-dasharray="4 4"':''}/>`;
  }).join('\n')+'</g></svg>';
}
export function initImmortalProductFigure(figure){
  figure.classList.add('immortal-product-figure');
  const stage=figure.querySelector('.soliton-stage'),canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d');
  if(!ctx)return;
  const controls=figure.querySelector('.soliton-controls'),help=figure.querySelector('.soliton-help'),status=figure.querySelector('.soliton-status');
  let overview=true,q=0,limit=false,yaw=-.46,pitch=.23,zoom=1,cutaway=true,wire=false,playing=false,raf=0,last=0,drag=null;
  const button=(name)=>{const b=document.createElement('button');b.type='button';b.textContent=name;return b;};
  const all=button('All four stages'),play=button('Play stages'),end=button('Infinite-time limit'),cut=button('Cutaway');
  const label=document.createElement('label'),slider=document.createElement('input');
  label.textContent='Earlier → later';slider.type='range';slider.min=0;slider.max=1;slider.step=.005;slider.value=0;slider.setAttribute('aria-label','Schematic finite-time stage, not physical time');label.append(slider);
  controls.prepend(all,play,end,cut,label);
  figure.insertBefore(controls,stage);figure.insertBefore(help,stage);
  const legend=document.createElement('p');legend.className='immortal-product-legend';
  legend.innerHTML='<span style="color:#267b91">━ y &gt; 0 sheet</span> <span style="color:#a05c32">━ y &lt; 0 sheet</span> <span>Profiles below: y versus polar angle x.</span>';
  stage.after(legend);
  help.textContent='Drag or use arrow keys to rotate; + / − to zoom. The slider orders schematic stages, with no physical time or decay rate assigned. The limit is a separate view.';
  function sync(){
    all.setAttribute('aria-pressed',String(overview));end.setAttribute('aria-pressed',String(limit&&!overview));cut.setAttribute('aria-pressed',String(cutaway));
    play.textContent=playing?'Pause':'Play stages';play.setAttribute('aria-pressed',String(playing));slider.value=q;
    canvas.style.touchAction=overview?'pan-y':'none';
    canvas.dataset.view=overview?'overview':limit?'limit':'finite';canvas.dataset.stage=String(q);canvas.dataset.yaw=String(yaw);canvas.dataset.zoom=String(zoom);canvas.dataset.cutaway=String(cutaway);
    canvas.setAttribute('aria-label',overview?'Three ordered finite-time schematic surfaces and a separate multiplicity-two sphere limit, with generating profiles.':limit?'Infinite-time limit: one minimal sphere counted twice.':'Finite-time schematic: two sheets joined by two positive polar necks.');
  }
  function draw(){
    sync();const width=stage.getBoundingClientRect().width,s=scene(width,{overview,frame:limit?STAGES[3]:finiteStage(q),yaw,pitch,zoom,cutaway,wire});
    stage.style.height=s.height+'px';const dpr=Math.min(window.devicePixelRatio||1,2);
    canvas.width=Math.round(width*dpr);canvas.height=Math.round(s.height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);
    for(const p of s.items){
      if(p.kind==='clipStart'){ctx.save();ctx.beginPath();ctx.rect(p.x,p.y,p.w,p.h);ctx.clip();continue;}
      if(p.kind==='clipEnd'){ctx.restore();continue;}
      ctx.fillStyle=p.color;ctx.strokeStyle=p.color;
      if(p.kind==='rect'){ctx.fillRect(p.x,p.y,p.w,p.h);continue;}
      if(p.kind==='text'){ctx.font=`${p.bold?600:400} ${p.size}px system-ui,sans-serif`;ctx.textAlign=p.anchor==='middle'?'center':p.anchor;ctx.fillText(p.value,p.x,p.y);continue;}
      ctx.beginPath();p.points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));
      if(p.kind==='poly'){ctx.closePath();ctx.fill();ctx.lineWidth=.4;ctx.stroke();}else{ctx.lineWidth=p.width;ctx.setLineDash(p.dash?[4,4]:[]);ctx.stroke();ctx.setLineDash([]);}
    }
    status.textContent=overview?'Read the panels in numbered order. The first three drawings represent ordered finite times; the last is only the t → ∞ limit.':limit?'The two sheets coincide on S² × {0}. Both necks have collapsed at infinite time; this is not a smooth torus slice.':'Both necks remain open. The full surface is a connected closed torus (genus 1), even when the display is cut away.';
  }
  const stop=()=>{playing=false;cancelAnimationFrame(raf);sync();};
  function tick(now){if(!playing)return;if(last)q=Math.min(1,q+(now-last)/15000);last=now;draw();if(q===1)stop();else raf=requestAnimationFrame(tick);}
  all.onclick=()=>{stop();overview=true;draw();};end.onclick=()=>{stop();overview=false;limit=true;draw();};
  play.onclick=()=>{if(playing){stop();return;}overview=false;limit=false;if(q>=1)q=0;last=0;playing=true;raf=requestAnimationFrame(tick);};
  slider.oninput=()=>{q=Number(slider.value);stop();overview=false;limit=false;draw();};cut.onclick=()=>{cutaway=!cutaway;draw();};
  for(const b of controls.querySelectorAll('[data-view-action]'))b.onclick=()=>{
    const a=b.dataset.viewAction;if(a==='in')zoom=Math.min(1.25,zoom*1.1);if(a==='out')zoom=Math.max(.6,zoom/1.1);if(a==='wire'){wire=!wire;b.setAttribute('aria-pressed',String(wire));}
    if(a==='reset'){stop();overview=true;limit=false;q=0;yaw=-.46;pitch=.23;zoom=1;cutaway=true;wire=false;figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed','false');}draw();
  };
  canvas.onpointerdown=e=>{if(e.pointerType==='touch'&&overview)return;drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);};
  canvas.onpointermove=e=>{if(!drag)return;yaw+=(e.clientX-drag[0])*.008;pitch=Math.max(-1.1,Math.min(1.1,pitch+(e.clientY-drag[1])*.008));drag=[e.clientX,e.clientY];draw();};
  canvas.onpointerup=canvas.onpointercancel=()=>{drag=null;};
  canvas.onkeydown=e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-'].includes(e.key))return;e.preventDefault();if(e.key==='ArrowLeft')yaw-=.12;if(e.key==='ArrowRight')yaw+=.12;if(e.key==='ArrowUp')pitch=Math.min(1.1,pitch+.12);if(e.key==='ArrowDown')pitch=Math.max(-1.1,pitch-.12);if(['+','='].includes(e.key))zoom=Math.min(1.25,zoom*1.1);if(e.key==='-')zoom=Math.max(.6,zoom/1.1);draw();};
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});new IntersectionObserver(es=>{if(!es[0].isIntersecting)stop();}).observe(figure);
  controls.hidden=false;help.hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;
  let previousWidth=0;new ResizeObserver(()=>{const w=stage.getBoundingClientRect().width;if(w!==previousWidth){previousWidth=w;draw();}}).observe(stage);draw();
}
