// Equal-angle Lawlor model for the Su–Tsai–Wood infinite-time neck.
// The profile is exact; its time-dependent dilation is NOT an MCF solution.
export function neckScale(tau, m=3) {
  if (!Number.isInteger(m) || m<3 || m>6) throw new RangeError('Use 3 ≤ m ≤ 6.');
  if (!(tau>=0)) throw new RangeError('Model time must be nonnegative.');
  return tau===Infinity?0:(1+tau)**(-1/(m-2));
}

export function lawlorProfile(m=3, epsilon=1, radius=3, count=240) {
  neckScale(0,m);
  if (!(epsilon>0 && radius>epsilon) || !Number.isInteger(count) || count<2) throw new RangeError('Invalid profile window.');
  // gamma(v) = eps exp(-i pi/(2m)) (sinh(v)+i)^(1/m).
  // This is the equal-angle neck in §2.3, in a rotated unit-waist normalization.
  const vmax=Math.acosh((radius/epsilon)**m);
  return Array.from({length:count+1},(_,i)=>{
    const v=vmax*(2*i/count-1);
    const r=epsilon*Math.cosh(v)**(1/m);
    const theta=(Math.atan2(1,Math.sinh(v))-Math.PI/2)/m;
    return [r*Math.cos(theta),r*Math.sin(theta)];
  });
}

const BLUE='#247b99', GOLD='#b57139', INK='#183b4e', MUTED='#657b87', BORDER='#d8e4e9';
export function initLawlorFlowFigure(figure) {
  const canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d');
  if(!ctx)return;
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  figure.classList.add('lawlor-flow-figure');
  let tau=0,m=3,limit=false,zoom=1,playing=false,frame=null,previous=0,scheduled=false;
  canvas.setAttribute('aria-label','Equal-angle Lawlor neck: signed generating profiles at a fixed spatial scale and at neck scale. These are local models of a flow in a flat complex torus, not a computed mean curvature flow.');
  controls.querySelector('[data-view-action=wire]').remove();
  const help=figure.querySelector('.soliton-help');
  help.textContent='Choose a stage or play the model. The fixed-scale panel shows the closing neck; the other magnifies by ε₀/ε. Opposite profile points represent one sphere Sᵐ⁻¹ in the full neck, so the two branches are not two components.';
  const timeLabel=document.createElement('label'),output=document.createElement('output'),slider=document.createElement('input');
  slider.type='range';slider.min='0';slider.max=String(Math.log(65));slider.step='.005';slider.value='0';slider.setAttribute('aria-label','Lawlor neck model time');
  timeLabel.append(output,slider);
  const dimension=document.createElement('label');dimension.textContent='Dimension m ';
  const select=document.createElement('select');select.setAttribute('aria-label','Lagrangian dimension');
  for(let j=3;j<=6;j++){const option=document.createElement('option');option.value=j;option.textContent=String(j);select.append(option);}
  dimension.append(select);controls.prepend(timeLabel,dimension);
  const play=document.createElement('button');play.type='button';play.textContent='Play model';play.setAttribute('aria-pressed','false');controls.append(play);
  const timeline=document.createElement('div');timeline.className='lawlor-timeline';timeline.setAttribute('role','group');timeline.setAttribute('aria-label','Compare stages of neck collapse');
  const stages=[0,1,5,Infinity],buttons=[];
  for(const time of stages){const button=document.createElement('button');button.type='button';button.textContent=time===Infinity?'Limit · τ → ∞':`τ = ${time}`;button.addEventListener('click',()=>{stop();limit=time===Infinity;if(!limit){tau=time;slider.value=String(Math.log1p(tau));}update();});buttons.push(button);timeline.append(button);}
  stage.after(timeline);
  const summary=document.createElement('p');summary.className='lawlor-topology';timeline.after(summary);
  const status=figure.querySelector('.soliton-status');
  function sync(){
    const epsilon=neckScale(limit?Infinity:tau,m),timeText=limit?'∞':tau.toFixed(2);
    output.textContent=`Model time τ = ${timeText}`;
    for(let j=0;j<buttons.length;j++){
      const button=buttons[j],eps=neckScale(stages[j],m);
      button.setAttribute('aria-pressed',String(limit?stages[j]===Infinity:Math.abs(tau-stages[j])<.001));
      if(button.dataset.dimension!==String(m)){
        let svg='<svg viewBox="-3.3 -1.9 6.6 3.8" aria-hidden="true">';
        const a=Math.PI/(2*m),ray=[3*Math.cos(a),3*Math.sin(a)];
        for(const sign of [-1,1])svg+=`<path d="M ${-ray[0]} ${sign*ray[1]} L ${ray[0]} ${-sign*ray[1]}" fill="none" stroke="${eps?'#bdcad0':sign>0?BLUE:GOLD}" stroke-width="${eps?.035:.065}" ${eps?'stroke-dasharray=".12 .12"':''}/>`;
        if(eps){const profile=lawlorProfile(m,eps,3,80);for(const sign of [-1,1])for(const [half,col] of [[profile.slice(0,41),BLUE],[profile.slice(40),GOLD]])svg+=`<path d="${half.map(([x,y],i)=>`${i?'L':'M'} ${sign*x} ${-sign*y}`).join(' ')}" fill="none" stroke="${col}" stroke-width=".075"/>`;}
        svg+='</svg>';
        button.innerHTML=svg+`<span>${stages[j]===Infinity?'Limit · τ → ∞':`τ = ${stages[j]}`}</span>`;button.dataset.dimension=String(m);
      }
    }
    summary.textContent=limit?`Global limit: X₁ ∪ X₂, two special Lagrangian m-tori meeting at one point. The neck-scale limit is still a smooth Lawlor neck.`:`Finite time: Tᵐ # Tᵐ is connected and embedded in Cᵐ/Γ. The local neck has fibers S${m===3?'²':m===4?'³':m===5?'⁴':'⁵'} and radius ε/ε₀ = ${epsilon.toFixed(3)}.`;
    status.textContent=limit?'Infinite-time limit only: two transverse tangent planes at fixed scale, and a smooth Lawlor neck after rescaling.':`Leading-order model: ε/ε₀ = (1 + τ)^(−1/${m-2}). Equal characteristic angles π/${m}. The global gluing correction and exact flow time are not computed.`;
    canvas.dataset.time=limit?'infinity':String(tau);canvas.dataset.scale=String(epsilon);canvas.dataset.dimension=String(m);canvas.dataset.zoom=String(zoom);canvas.dataset.playing=String(playing);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function update(){sync();requestDraw();}
  function draw(){
    scheduled=false;
    const {width,height}=stage.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2);
    canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,width,height);
    const stacked=width<540,gap=12,pad=10,pw=stacked?width-20:(width-32)/2,ph=stacked?(height-32)/2:height-20;
    for(let panel=0;panel<2;panel++){
      const x=pad+(stacked?0:panel*(pw+gap)),y=pad+(stacked?panel*(ph+gap):0);
      ctx.fillStyle='#fff';ctx.strokeStyle=BORDER;ctx.lineWidth=1;ctx.beginPath();ctx.roundRect(x,y,pw,ph,10);ctx.fill();ctx.stroke();
      ctx.fillStyle=INK;ctx.font='600 15px system-ui';ctx.fillText(panel?'At neck scale':'At a fixed spatial scale',x+14,y+25);
      ctx.font='12px system-ui';ctx.fillStyle=MUTED;ctx.fillText(panel?(limit?'Rescaled limit: Lawlor neck':'Magnify by ε₀ / ε'):'Same axes at every model time',x+14,y+46);
      const cx=x+pw/2,cy=y+(ph+40)/2,scale=Math.min((pw-45)/6.4,(ph-115)/3.8)*(panel?1:zoom);
      const transform=([a,b])=>[cx+scale*a,cy-scale*b];
      function path(points,color,width=2.8,dash=[]){ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.beginPath();points.forEach((p,j)=>j?ctx.lineTo(...transform(p)):ctx.moveTo(...transform(p)));ctx.stroke();ctx.setLineDash([]);}
      const epsilon=panel?1:neckScale(limit?Infinity:tau,m),angle=Math.PI/(2*m);
      ctx.save();ctx.beginPath();ctx.rect(x+7,y+54,pw-14,ph-96);ctx.clip();
      path([[-20,0],[20,0]],'#edf1f3',1);
      path([[0,-20],[0,20]],'#edf1f3',1);
      for(const sign of [-1,1]){
        const ray=[Math.cos(angle)*10,sign*Math.sin(angle)*10];
        path([ray.map(a=>-a),ray],epsilon===0?(sign>0?BLUE:GOLD):'#afbec6',epsilon===0?2.8:1.4,epsilon===0?[]:[5,5]);
      }
      if(epsilon>0){
        const profile=lawlorProfile(m,epsilon,8,320),half=profile.length>>1;
        for(const sign of [-1,1]){
          path(profile.slice(0,half+1).map(p=>p.map(a=>sign*a)),BLUE,3);
          path(profile.slice(half).map(p=>p.map(a=>sign*a)),GOLD,3);
        }
        // This dashed ruler records radius, not an extra segment of the neck.
        path([[0,0],[epsilon,0]],'#8a6b35',1.4,[3,3]);
        for(const sign of [-1,1]){ctx.fillStyle='#bd963d';ctx.beginPath();ctx.arc(...transform([sign*epsilon,0]),3.3,0,2*Math.PI);ctx.fill();}
      }
      ctx.fillStyle=INK;ctx.beginPath();ctx.arc(cx,cy,2.5,0,2*Math.PI);ctx.fill();ctx.restore();
      ctx.fillStyle=MUTED;ctx.font='12px system-ui';ctx.textAlign='center';
      ctx.fillText(epsilon===0?'Singular point x★':panel?'Unit waist after rescaling':`ε / ε₀ = ${epsilon.toFixed(3)} > 0`,cx,y+ph-36);
      ctx.fillText(panel?'Local geometry persists as the neck shrinks':epsilon===0?'Two planes; one transverse intersection':'Dashed lines: fixed tangent-plane profiles',cx,y+ph-17);ctx.textAlign='left';
    }
  }
  function stop(){playing=false;play.textContent='Play model';play.setAttribute('aria-pressed','false');if(frame!==null)cancelAnimationFrame(frame);frame=null;previous=0;}
  function animate(now){if(!playing)return;if(previous){const q=Number(slider.value)+(now-previous)/7000;slider.value=String(Math.min(Number(slider.max),q));tau=Math.expm1(Number(slider.value));if(q>=Number(slider.max))stop();}previous=now;update();if(playing)frame=requestAnimationFrame(animate);}
  play.addEventListener('click',()=>{if(playing){stop();update();return;}if(limit||Number(slider.value)>=Number(slider.max)){tau=0;slider.value='0';}limit=false;playing=true;play.textContent='Pause model';play.setAttribute('aria-pressed','true');previous=0;update();frame=requestAnimationFrame(animate);});
  slider.addEventListener('input',()=>{stop();limit=false;tau=Math.expm1(Number(slider.value));update();});
  select.addEventListener('change',()=>{m=Number(select.value);update();});
  function setZoom(value){zoom=Math.max(.8,Math.min(5,value));update();}
  controls.addEventListener('click',event=>{const action=event.target.dataset.viewAction;if(action==='in')setZoom(zoom*1.25);if(action==='out')setZoom(zoom/1.25);if(action==='reset'){stop();tau=0;m=3;limit=false;zoom=1;select.value='3';slider.value='0';update();}});
  canvas.addEventListener('keydown',event=>{if(event.key==='+'||event.key==='='){event.preventDefault();setZoom(zoom*1.25);}if(event.key==='-'){event.preventDefault();setZoom(zoom/1.25);}});
  document.addEventListener('visibilitychange',()=>{if(document.hidden){stop();update();}});
  new ResizeObserver(requestDraw).observe(stage);
  figure.classList.add('is-interactive');controls.hidden=false;help.hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;update();
}
