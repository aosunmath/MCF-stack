import {TIMES,COLORS,neckpinchProfile,scales,innerRadius,bowlHeight,project,surfacePolygons,shade,timeLabel} from './neckpinch-geometry.mjs';

export function initNeckpinchFigure(figure,data){
  const canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d');if(!ctx)return;
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls'),status=figure.querySelector('.soliton-status');
  figure.classList.add('neckpinch-figure');
  let mode='sequence',s=1e-3,yaw=-.28,pitch=.2,zoom=1,wire=false,scheduled=false,drag=null,playing=false,last=0,animation=0,playProgress=3;
  let cacheKey='',cached=[];
  const views=document.createElement('div');views.className='neckpinch-views';
  const buttons={};
  for(const [key,title] of [['sequence','Time sequence'],['surface','Single surface'],['profile','Profile overlay'],['limits','Blow-up limits']]){
    const button=document.createElement('button');button.type='button';button.textContent=title;buttons[key]=button;
    button.addEventListener('click',()=>{stop();mode=key;zoom=1;sync();requestDraw();});views.append(button);
  }
  controls.prepend(views);
  const time=document.createElement('label'),output=document.createElement('output'),slider=document.createElement('input');
  time.className='neckpinch-time';slider.type='range';slider.min='3';slider.max='7';slider.step='.01';slider.value='3';slider.setAttribute('aria-label','Approach singular time, negative logarithm of T minus t');time.append(output,slider);
  const play=document.createElement('button');play.type='button';play.textContent='Play toward T';
  controls.append(time,play);
  const help=figure.querySelector('.soliton-help');
  canvas.setAttribute('aria-label','Degenerate neckpinch in three-space: a time sequence, a rotatable surface, overlaid meridians, or three blow-up limits. Illustrative compact slices, not a numerical solution of mean curvature flow.');
  function stop(){playing=false;cancelAnimationFrame(animation);play.textContent='Play toward T';}
  function tick(now){
    if(!playing)return;
    const value=playProgress+(now-last)/10000;last=now;playProgress=value;
    slider.value=String(Math.min(7,value));s=10**(-Number(slider.value));sync();requestDraw();
    if(value>=7)stop();else animation=requestAnimationFrame(tick);
  }
  play.addEventListener('click',()=>{if(playing){stop();return;}if(Number(slider.value)>=7)slider.value='3';playProgress=Number(slider.value);playing=true;play.textContent='Pause';last=performance.now();animation=requestAnimationFrame(tick);});
  slider.addEventListener('input',()=>{stop();s=10**(-Number(slider.value));sync();requestDraw();});
  function sync(){
    for(const [key,b] of Object.entries(buttons))b.setAttribute('aria-pressed',String(key===mode));
    time.hidden=play.hidden=mode!=='surface';
    controls.querySelector('[data-view-action=wire]').hidden=!['sequence','surface'].includes(mode);
    output.textContent=`s = T − t = ${s.toExponential(2)}`;
    canvas.dataset.mode=mode;canvas.dataset.time=String(s);canvas.dataset.zoom=String(zoom);canvas.dataset.rotation=`${yaw},${pitch}`;
    stage.dataset.mode=mode;legend.hidden=mode!=='profile';note.hidden=mode!=='limits';
    help.textContent=mode==='sequence'?'Read left to right, then down. Every panel uses the same spatial scale. Drag to rotate all four views; + / − zoom. The final panel is a singular target, outside the smooth time interval.':mode==='surface'?'Move the time slider toward T. Drag to rotate; arrow keys also rotate. Zoom + / − keeps the spatial frame fixed as time changes.':mode==='profile'?'Upper and lower meridians at three illustrative times and the cusp target, on the same axes. The inset magnifies the neighborhood of the origin, with equal horizontal and vertical scales.':'Each panel uses its own coordinates. The middle panel rescales the axial and radial directions differently. The bowl is a numerical ODE solution; the other curves are analytic limiting profiles.';
    status.textContent=mode==='surface'?`Leading tip position a ≈ ${scales(s).tip.toFixed(5)}; leading tip |H| ≈ ${scales(s).H.toFixed(2)}.`:mode==='limits'?'The tip scale uses |H|, giving a speed-one bowl. Scaling by |A| would instead give speed √2.':mode==='sequence'?'Gold marks the moving tip. The fixed origin is labeled 0 in every panel.':'';
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function text(t,x,y,color='#183f52',size=13,bold=false){ctx.fillStyle=color;ctx.font=`${bold?'600 ':''}${size}px system-ui`;ctx.fillText(t,x,y);}
  function line(points,color='#9bb0b9',width=1,dash=[]){ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.stroke();ctx.setLineDash([]);}
  function card(x,y,w,h){ctx.fillStyle='#fff';ctx.strokeStyle='#d7e3e8';ctx.lineWidth=1;ctx.beginPath();ctx.roundRect(x,y,w,h,9);ctx.fill();ctx.stroke();}
  function dot(p,color,r=3){ctx.fillStyle=color;ctx.beginPath();ctx.arc(...p,r,0,2*Math.PI);ctx.fill();}
  function drawSurface(x,y,w,h,s,color,faces){
    const scale=Math.min((w-38)/.9,(h-66)/.64)*zoom,cx=x+w/2-.25*scale,cy=y+(h+30)/2;
    const screen=p=>[cx+scale*p[0],cy-scale*p[1]];
    ctx.save();ctx.beginPath();ctx.rect(x+3,y+30,w-6,h-36);ctx.clip();
    line([screen(project([-.15,0,0],yaw,pitch)),screen(project([.66,0,0],yaw,pitch))],'#b6c7ce',1,[4,4]);
    for(const face of faces){ctx.beginPath();face.points.forEach((p,i)=>i?ctx.lineTo(...screen(p)):ctx.moveTo(...screen(p)));ctx.closePath();ctx.fillStyle=shade(color,face.light);ctx.fill();ctx.strokeStyle=wire?'#203e4c55':ctx.fillStyle;ctx.lineWidth=wire?.45:.35;ctx.stroke();}
    const origin=screen(project([0,0,0],yaw,pitch));
    line([[origin[0],y+h-20],[origin[0],origin[1]+6]],'#a78c72',1,[3,4]);
    text('0',origin[0]-3,y+h-7,'#617987',11);
    const tip=s>0?scales(s).tip:0;dot(screen(project([tip,0,0],yaw,pitch)),s>0?'#d48c2e':'#8c5877',3.5);
    ctx.restore();
  }
  function draw(){
    scheduled=false;const {width:w,height:h}=stage.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2);
    canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
    if(mode==='sequence'||mode==='surface'){
      const times=mode==='sequence'?TIMES:[s],key=JSON.stringify([times,yaw,pitch]);
      if(key!==cacheKey){cached=times.map(t=>surfacePolygons(neckpinchProfile(t,data),yaw,pitch,28));cacheKey=key;}
      const columns=mode==='sequence'&&w>=520?2:1,rows=Math.ceil(times.length/columns),gap=10,pw=(w-gap*(columns+1))/columns,ph=(h-gap*(rows+1))/rows;
      times.forEach((t,i)=>{const x=gap+(i%columns)*(pw+gap),y=gap+Math.floor(i/columns)*(ph+gap);card(x,y,pw,ph);text(mode==='surface'?`s = T − t = ${s.toExponential(2)}`:timeLabel(t),x+13,y+24,COLORS[i],w<520?14:13,true);drawSurface(x,y,pw,ph,t,COLORS[i],cached[i]);});
    }else if(mode==='profile'){
      const panels=[{x:12,y:16,w:w-24,h:h*.48,xmin:-.15,xmax:.63,caption:'Whole meridian · common spatial axes'},
                    {x:12,y:h*.52,w:w-24,h:h*.48-12,xmin:-.14,xmax:.17,caption:'Near the origin · equal axis scales'}];
      for(const p of panels){card(p.x,p.y,p.w,p.h);text(p.caption,p.x+12,p.y+23,'#183f52',13,true);
        const scale=Math.min((p.w-30)/(p.xmax-p.xmin),(p.h-62)/(p.xmax>.5?.66:.22))*zoom;
        const screen=([x,r])=>[p.x+p.w/2+(x-(p.xmin+p.xmax)/2)*scale,p.y+p.h*.57-r*scale];
        ctx.save();ctx.beginPath();ctx.rect(p.x+5,p.y+35,p.w-10,p.h-40);ctx.clip();
        line([screen([p.xmin,0]),screen([p.xmax,0])]);line([screen([0,-1]),screen([0,1])],'#bac9cf',1,[3,4]);
        TIMES.forEach((t,i)=>{const profile=neckpinchProfile(t,data).filter(([x])=>x>=p.xmin&&x<=p.xmax);for(const sign of [-1,1])line(profile.map(([x,r])=>screen([x,sign*r])),COLORS[i],t===0?2.4:1.8,t===0?[4,3]:[]);dot(screen([t?scales(t).tip:0,0]),COLORS[i]);});ctx.restore();
      }
    }else{
      const stacked=w<650,cols=stacked?1:3,rows=stacked?3:1,gap=10,pw=(w-gap*(cols+1))/cols,ph=(h-gap*(rows+1))/rows;
      for(let i=0;i<3;i++){
        const x=gap+(i%cols)*(pw+gap),y=gap+Math.floor(i/cols)*(ph+gap);card(x,y,pw,ph);
        text(['At the origin','Between the scales','At the moving tip'][i],x+12,y+23,COLORS[i],14,true);
        const bounds=[[-2.5,2.5,1.8],[-1.3,1.25,2.1],[0,4.6,3.2]][i];
        const scale=Math.min((pw-30)/(bounds[1]-bounds[0]),(ph-100)/(2*bounds[2]))*zoom;
        const screen=([a,r])=>[x+pw/2+(a-(bounds[0]+bounds[1])/2)*scale,y+ph*.51-r*scale];
        ctx.save();ctx.beginPath();ctx.rect(x+5,y+34,pw-10,ph-79);ctx.clip();
        line([screen([bounds[0],0]),screen([bounds[1],0])]);
        let curve=[];
        for(let j=0;j<=240;j++){
          if(i===0)curve.push([-2.5+5*j/240,Math.SQRT2]);
          if(i===1){const a=-Math.cbrt(2)+(1.25+Math.cbrt(2))*j/240;curve.push([a,Math.sqrt(Math.max(0,2+a**3))]);}
          if(i===2){const r=3.2*j/240;curve.push([bowlHeight(r,data),r]);}
        }
        for(const sign of [-1,1])line(curve.map(([a,r])=>screen([a,sign*r])),COLORS[i],2.4);
        if(i===0){const curve=Array.from({length:241},(_,j)=>{const a=-2.5+5*j/240;return [a,innerRadius(a,1e-3)];});for(const sign of [-1,1])line(curve.map(([a,r])=>screen([a,sign*r])),'#b47731',1.4,[4,3]);}
        ctx.restore();
        text(['(x, r) / √s','ξ = x/s¹ᐟ³, ρ = r/√s','(X, R) = Htip (x − a, r)'][i],x+12,y+ph-37,'#526b77',12);
        text(['Cylinder + cubic correction*','ρ = √(2 + ξ³) · anisotropic','X = P(R) · numerical bowl'][i],x+12,y+ph-16,'#526b77',12);
      }
    }
  }
  function setZoom(v){zoom=Math.max(.6,Math.min(5,v));sync();requestDraw();}
  controls.querySelector('[data-view-action=in]').addEventListener('click',()=>setZoom(zoom*1.25));
  controls.querySelector('[data-view-action=out]').addEventListener('click',()=>setZoom(zoom/1.25));
  controls.querySelector('[data-view-action=wire]').addEventListener('click',e=>{wire=!wire;e.currentTarget.setAttribute('aria-pressed',String(wire));requestDraw();});
  controls.querySelector('[data-view-action=reset]').addEventListener('click',()=>{stop();yaw=-.28;pitch=.2;zoom=1;s=1e-3;slider.value='3';sync();requestDraw();});
  canvas.addEventListener('pointerdown',e=>{if(!['sequence','surface'].includes(mode))return;stop();drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;yaw+=(e.clientX-drag[0])*.008;pitch+=(e.clientY-drag[1])*.008;drag=[e.clientX,e.clientY];sync();requestDraw();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>{drag=null;});
  canvas.addEventListener('keydown',e=>{if(['+','=','-'].includes(e.key)){e.preventDefault();setZoom(zoom*(e.key==='-'?.8:1.25));}else if(['sequence','surface'].includes(mode)&&e.key.startsWith('Arrow')){e.preventDefault();yaw+=e.key==='ArrowRight'?.1:e.key==='ArrowLeft'?-.1:0;pitch+=e.key==='ArrowUp'?.1:e.key==='ArrowDown'?-.1:0;sync();requestDraw();}});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  new IntersectionObserver(entries=>{if(!entries[0].isIntersecting)stop();}).observe(figure);
  const legend=document.createElement('p');legend.className='neckpinch-legend';
  TIMES.forEach((t,i)=>{const span=document.createElement('span');span.style.color=COLORS[i];span.textContent=t===0?'Dashed: cusp target':timeLabel(t);legend.append(span);});
  controls.after(legend);
  const note=document.createElement('p');note.className='soliton-help';note.textContent='* Dashed curve: the leading cubic Hermite correction at s = 10⁻³, not the exact rescaled slice.';figure.querySelector('figcaption').before(note);
  figure.querySelector('img').hidden=true;canvas.hidden=false;controls.hidden=false;help.hidden=false;
  new ResizeObserver(requestDraw).observe(stage);sync();requestDraw();
}
