// Display precomputed, audited ODE profiles. This viewer never solves a PDE.
export const FLOW_TIMES = [-1, -.25, -.04, 0, .04, .25, 1];
export function similarity(points,time,kind='shrinker') {
  const scale=kind==='minimal'?time:Math.sqrt(Math.abs(time));
  return points.map(([x,y])=>[scale*x,scale*y]);
}
export function innerScale(points,time,k=2) {
  return points.map(([y,x])=>[x*Math.abs(time)**(k/3),y*Math.abs(time)**(k/3)]);
}
export function curveAt(data,index,time) {
  const s=data.shrinkers[index];
  if(time===0)return [{name:'Singular limiting cone',points:[[0,0],[40,40*s.slope]],cone:true}];
  if(time<0)return [{name:`Shrinker m = ${s.m}`,points:similarity(s.points,time)}];
  if(index!==data.matched_shrinker_index)throw new RangeError('No matched continuation recorded for this shrinker');
  return data.continuations.map(r=>({name:r.name,points:similarity(r.points,time)}));
}

if(typeof document!=='undefined') {
 const data=JSON.parse(document.getElementById('geometry').textContent),model=document.body.dataset.model;
 const $=id=>document.getElementById(id),canvas=$('plot'),ctx=canvas.getContext('2d');
 const colors=['#126b84','#d7772f','#793eab','#20805a'];
 const names={'aiv-shrinkers':'AIV shrinkers and expanding continuations','aiv-expanders':'Axis-starting self-expanders','aiv-minimal':'Stationary minimal caps','aiv-eight-fattening':'The eight-dimensional fattening models'};
 document.title=$('title').textContent=names[model];
 const options=(select,items)=>{select.replaceChildren(...items.map(([value,label])=>{const o=document.createElement('option');o.value=value;o.textContent=label;return o;}));};
 let running=false,raf=0,last=0;
 if(model==='aiv-shrinkers') {
  options($('family'),[['1','m = 3: shrinker and three continuations'],['0','m = 2: shrinker only']]);
  $('parameter-control').hidden=true;$('time').min=0;$('time').max=6;$('time').step=1;$('time').value=0;
 } else if(model==='aiv-eight-fattening') {
  options($('family'),[['inner','Formal type II inner scale'],['expander','Expander slope criterion'],['minimal','Stationary caps at the cone']]);
  $('parameter-control').hidden=true;$('time').min=.04;$('time').max=1;$('time').step=.01;$('time').value=1;
 } else {
  const pairs=[...new Set(data.minimal.map(s=>`${s.p},${s.q}`))];
  options($('family'),pairs.map(k=>[k,`(p, q) = (${k.replace(',',', ')}), ambient R${k.split(',').reduce((a,x)=>a+Number(x),0)}`]));
  options($('parameter'),[['.03','0.03'],['.1','0.1'],['.3','0.3'],['1','1']]);$('parameter').value='.1';
  $('time').min=.04;$('time').max=2;$('time').step=.01;$('time').value=1;
  if(model==='aiv-minimal'){$('time-label').textContent='Spatial dilation a (stationary family)';$('parameter-control').hidden=true;$('play').hidden=true;}
 }
 function state() {
  const z=Number($('zoom').value);let curves=[],A=1,lim=4/z,label='',note='';
  if(model==='aiv-shrinkers') {
   const index=Number($('family').value),s=data.shrinkers[index];
   $('time').max=index===1?6:2;if(Number($('time').value)>Number($('time').max))$('time').value=0;
   const t=FLOW_TIMES[Number($('time').value)];A=s.slope;lim=2/z;
   curves=curveAt(data,index,t);label=`t = ${t}`;
   note=`Numerical axis radius a ≈ ${s.a.toPrecision(9)}; cone slope A ≈ ${A.toPrecision(11)}. `+(t===0?'The cone has a singular vertex.':t>0?'Three distinct numerical continuations of the same cone are shown. The region of the maximal level-set flow is not computed.':'The same numerical shrinker profile is scaled by √(−t).')+' Finite computed tails are clipped for display.';
  } else if(model==='aiv-eight-fattening') {
   A=Math.sqrt(5);const t=Number($('time').value),choice=$('family').value;lim=4/z;
   if(choice==='inner') {
    const r=data.minimal.find(s=>s.p===6&&s.q===2);curves=[{name:'Formal inner model',points:innerScale(r.points,-t)}];label=`t = −${t.toFixed(2)}, inner scale = ${t**(2/3)}`;
    $('time-label').textContent='Relative |t| (formal model)';
    note='FORMAL INNER MODEL ONLY. k = 2; length scale (−t)^(2/3). The stationary inverse-coordinate ODE profile is rescaled to illustrate the predicted inner region. This rescaled family alone does not solve MCF; no outer matching or nonlinear PDE evolution is computed.';
   } else if(choice==='expander') {
    const r=data.expanders.find(s=>s.p===2&&s.q===6&&s.a===.1);curves=[{name:'Expander, a = 0.1',points:similarity(r.points,t,'expander')}];label=`t = ${t.toFixed(2)}`;$('time-label').textContent='Positive time';
    note=`Numerical cone slope B ≈ ${r.slope.toPrecision(12)}, B − √5 ≈ ${(r.slope-A).toExponential(4)}. This tests the strict slope condition of Lemma 23 numerically; it does not prove fattening or realize the formal type II flow.`;
   } else {
    const r=data.minimal.find(s=>s.p===2&&s.q===6),v=data.minimal.find(s=>s.p===6&&s.q===2);
    curves=[{name:'y-cap',points:r.points},{name:'x-cap',points:v.points.map(([y,x])=>[x,y])}];label='Stationary: all t';note='Numerical stationary caps in R8. The y-cap crosses the Simoes cone; the x-cap stays on its minimizing side in the displayed window. This numerical observation is not an interval-certified proof.';
   }
  } else {
   const [p,q]=$('family').value.split(',').map(Number),t=Number($('time').value);A=Math.sqrt((q-1)/(p-1));
   if(model==='aiv-minimal') {
    const r=data.minimal.find(s=>s.p===p&&s.q===q);
    curves=[{name:'Stationary cap',points:similarity(r.points,t,'minimal')}];label=`Dilation a = ${t.toFixed(2)}`;lim=10/z;
    note=`Complete minimal hypersurface in R${p+q}; topology R${p} × S${q-1}, one end. Dilation changes the member of the stationary family, not time. The plot is the radial orbit space, not a planar MCF.`;
   } else {
    const a=Number($('parameter').value),r=data.expanders.find(s=>s.p===p&&s.q===q&&s.a===a);
    curves=[{name:`Expander, a = ${a}`,points:similarity(r.points,t,'expander')}];label=`t = ${t.toFixed(2)}`;
    note=`Numerical asymptotic slope B ≈ ${r.slope.toPrecision(11)}; B − A* ≈ ${(r.slope-A).toExponential(3)}. The dashed line is the minimal cone A* = √((q−1)/(p−1)), which need not be this expander's limiting cone. Each selected radius was integrated separately.`;
   }
  }
  return {curves,A,lim,label,note};
 }
 function path(points,transform,color,width=2,dash=[]) {
  ctx.beginPath();points.forEach(([x,y],i)=>{const [xx,yy]=transform(x,y);if(i)ctx.lineTo(xx,yy);else ctx.moveTo(xx,yy);});ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.stroke();ctx.setLineDash([]);
 }
 function draw() {
  const s=state();$('readout').textContent=s.label;$('note').textContent=s.note;
  const rect=canvas.getBoundingClientRect(),width=Math.max(280,rect.width),height=width<650?690:430,dpr=window.devicePixelRatio||1;
  canvas.style.height=`${height}px`;canvas.width=Math.round(width*dpr);canvas.height=height*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);
  ctx.fillStyle='#f8fbfc';ctx.fillRect(0,0,width,height);ctx.font='13px system-ui';
  const stacked=width<650,panels=stacked?[[58,32,width-80,255],[58,365,width-80,255]]:[[60,42,width/2-85,300],[width/2+60,42,width/2-85,300]];
  const vals=s.curves.flatMap(c=>c.points.filter(([x,y])=>x>=0&&x<=s.lim).map(([x,y])=>y-s.A*x));
  let max=Math.max(.00001,...vals.map(Math.abs))*1.12;
  if($('detail').checked)max=Math.min(max,model==='aiv-eight-fattening'?.002:.03);
  const drawPanel=(panel,deviation)=>{
   const [px,py,pw,ph]=panel;
   const yMax=s.lim*Math.max(1,s.A),ymin=deviation?-max:0,ymax=deviation?max:yMax;
   // Match physical x/y units in the orbit-space view.
   const scale=deviation?null:Math.min(pw/s.lim,ph/yMax);
   const w=deviation?pw:s.lim*scale,h=deviation?ph:yMax*scale;
   const transform=(x,y)=>[px+x/s.lim*w,py+h-(y-ymin)/(ymax-ymin)*h];
   ctx.strokeStyle='#b7c6ce';ctx.lineWidth=1;ctx.strokeRect(px,py,w,h);
   ctx.fillStyle='#294654';ctx.textAlign='left';ctx.fillText(deviation?(stacked?'Cone deviation · enlarged':'Cone deviation (vertical scale enlarged)'):(stacked?'Profile · equal x/y scale':'Orbit-space profile · equal coordinate scales'),px,py-15);
   for(let i=0;i<=4;i++){
    const x=s.lim*i/4,yy=ymin+(ymax-ymin)*i/4;
    ctx.fillStyle='#48616c';ctx.textAlign='center';ctx.fillText(x.toFixed(2),px+w*i/4,py+h+19);
    ctx.textAlign='right';ctx.fillText(Math.abs(yy)<.01&&yy!==0?yy.toExponential(1):yy.toFixed(2),px-7,py+h-h*i/4+4);
   }
   ctx.textAlign='center';ctx.fillStyle='#294654';ctx.fillText('x = |X|',px+w/2,py+h+39);
   ctx.save();ctx.translate(px-43,py+h/2);ctx.rotate(-Math.PI/2);ctx.fillText(deviation?'y − A x':'y = |Y|',0,0);ctx.restore();
   ctx.save();ctx.beginPath();ctx.rect(px,py,w,h);ctx.clip();
   path([[0,0],[s.lim,deviation?0:s.A*s.lim]],transform,'#7c8d95',1.2,[5,5]);
   s.curves.forEach((c,i)=>path(c.points.map(([x,y])=>[x,deviation?y-s.A*x:y]),transform,colors[i],2.2));ctx.restore();
  };
  drawPanel(panels[0],false);drawPanel(panels[1],true);
  $('legend').replaceChildren(...s.curves.map((c,i)=>{const el=document.createElement('span');el.textContent=c.name;el.style.color=colors[i];return el;}));
 }
 function stop(){running=false;cancelAnimationFrame(raf);$('play').textContent='Play';}
 function animate(ts){if(!running)return;if(ts-last>650){const slider=$('time'),next=Number(slider.value)+Number(slider.step)*(model==='aiv-shrinkers'?1:8);slider.value=next>Number(slider.max)?slider.min:next;draw();last=ts;}raf=requestAnimationFrame(animate);}
 for(const id of ['family','parameter','time','zoom','detail'])$(id).addEventListener('input',()=>{stop();draw();});
 $('play').addEventListener('click',()=>{if(running)stop();else{running=true;$('play').textContent='Pause';raf=requestAnimationFrame(animate);}});
 $('reset').addEventListener('click',()=>{stop();$('zoom').value=1;$('detail').checked=false;$('time').value=model==='aiv-shrinkers'?0:1;draw();});
 new ResizeObserver(draw).observe(canvas.parentElement);draw();
}
