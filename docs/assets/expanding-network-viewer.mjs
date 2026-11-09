// Numerical expander branches; only the exact homothety changes with time.
export function networkPoint(point, time, vertical=false) {
  if (!Number.isFinite(time) || time < 0) throw new Error('Time must be nonnegative.');
  const scale=Math.sqrt(time), [x,y]=point;
  return vertical?[-scale*y,scale*x]:[scale*x,scale*y];
}

export function initExpandingNetworkFigure(figure,data) {
  const canvas=figure.querySelector('canvas'),ctx=canvas.getContext('2d');
  if(!ctx)return;
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  figure.classList.add('network-figure');
  let time=1,zoom=1,showRays=true,scheduled=false;
  canvas.setAttribute('aria-label','Two numerical four-ended planar expanding trees. Use the time slider to expand them, and zoom buttons to inspect their 120-degree junctions.');
  const help=figure.querySelector('.soliton-help');
  help.textContent='Move time toward zero to recover the same four rays. End labels stay fixed in the plane. Zoom in to inspect the junctions; + / − also zoom when the picture has focus.';
  controls.querySelector('[data-view-action=wire]').remove();
  const label=document.createElement('label'),output=document.createElement('output'),input=document.createElement('input');
  input.type='range';input.min='.05';input.max='4';input.step='.05';input.value='1';
  input.setAttribute('aria-label','Expanding network time');
  label.append(output,input);controls.prepend(label);
  const initial=document.createElement('button');initial.type='button';initial.textContent='Initial rays (t = 0)';initial.setAttribute('aria-pressed','false');
  const rays=document.createElement('button');rays.type='button';rays.textContent='Show rays';rays.setAttribute('aria-pressed','true');
  controls.append(initial,rays);
  const status=figure.querySelector('.soliton-status');
  function sync(){
    output.textContent=`t = ${time.toFixed(2)}`;
    initial.setAttribute('aria-pressed',String(time===0));
    rays.setAttribute('aria-pressed',String(showRays));
    status.textContent=time===0?'Initial four-ray cone: a nonregular junction. The regular expanding trees are shown only for t > 0.':`Each tree: two triple junctions, four ends. Central edge length ≈ ${(2*data.junction*Math.sqrt(time)).toFixed(3)}. Numerical ODE approximation.`;
    canvas.dataset.time=String(time);canvas.dataset.zoom=String(zoom);
    canvas.dataset.rays=String(showRays);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function draw(){
    scheduled=false;
    const {width,height}=stage.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2);
    canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);
    ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,width,height);
    const stacked=width<560,gap=12,pad=12;
    const pw=stacked?width-2*pad:(width-2*pad-gap)/2;
    const ph=stacked?(height-2*pad-gap)/2:height-2*pad;
    for(let panel=0;panel<2;panel++){
      const left=pad+(stacked?0:panel*(pw+gap)),top=pad+(stacked?panel*(ph+gap):0);
      const color=panel?'#ae6038':'#21667f';
      ctx.fillStyle='#fff';ctx.strokeStyle='#d3e2e8';ctx.lineWidth=1;
      ctx.beginPath();ctx.roundRect(left,top,pw,ph,8);ctx.fill();ctx.stroke();
      ctx.fillStyle=color;ctx.font='600 15px system-ui';
      ctx.fillText(panel?'Vertical connection':'Horizontal connection',left+14,top+24);
      const plotTop=top+40,plotHeight=ph-75;
      const cx=left+pw/2,cy=plotTop+plotHeight/2;
      const scale=Math.min(pw-30,plotHeight)/4.2*zoom;
      const screen=([x,y])=>[cx+x*scale,cy-y*scale];
      function stroke(points,lineColor,lineWidth=2.6,dash=[]){
        ctx.strokeStyle=lineColor;ctx.lineWidth=lineWidth;ctx.setLineDash(dash);
        ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.stroke();ctx.setLineDash([]);
      }
      ctx.save();ctx.beginPath();ctx.rect(left+8,plotTop,pw-16,plotHeight);ctx.clip();
      if(showRays||time===0){
        for(const sx of [-1,1])for(const sy of [-1,1]){
          stroke([[cx,cy],[cx+sx*1000,cy+sy*1000]],time===0?color:'#a7b5bc',time===0?2.5:1.3,time===0?[]:[5,5]);
        }
      }
      if(time>0){
        for(const path of data.paths)stroke(path.map(i=>screen(networkPoint(data.vertices[i],time,Boolean(panel)))),color);
        for(const sign of [-1,1]){
          const p=screen(networkPoint([sign*data.junction,0],time,Boolean(panel)));
          ctx.fillStyle=color;ctx.strokeStyle='#fff';ctx.lineWidth=1.5;
          ctx.beginPath();ctx.arc(...p,4,0,2*Math.PI);ctx.fill();ctx.stroke();
        }
        // Angle arcs and short dashed segments refer to exact outward tangents.
        const [jx,jy]=screen(networkPoint([data.junction,0],time,Boolean(panel)));
        const anglePoints=[];
        for(let i=0;i<=40;i++){
          const theta=-Math.PI/3+i*Math.PI/60;
          const dx=15*Math.cos(theta),dy=15*Math.sin(theta);
          anglePoints.push(panel?[jx-dy,jy-dx]:[jx+dx,jy-dy]);
        }
        stroke(anglePoints,color,1);
        for(const theta of [-Math.PI/3,Math.PI/3]){
          const dx=24*Math.cos(theta),dy=24*Math.sin(theta);
          stroke([[jx,jy],panel?[jx-dy,jy-dx]:[jx+dx,jy-dy]],color,.8,[2,3]);
        }
        ctx.fillStyle=color;ctx.font='13px system-ui';ctx.textAlign=panel?'center':'left';
        ctx.fillText('120°',jx+(panel?0:23),jy+(panel?-29:4));ctx.textAlign='left';
      }
      // Keep labels at the same spatial directions, even when zoomed.
      const r=Math.min(pw-50,plotHeight-26)/2;
      ctx.fillStyle='#657d89';ctx.font='12px system-ui';
      for(const [sx,sy,n] of [[1,1,'1'],[-1,1,'2'],[-1,-1,'3'],[1,-1,'4']]){
        ctx.fillText(n,cx+sx*r+(sx<0?-12:6),cy-sy*r+4);
      }
      ctx.restore();
      ctx.fillStyle='#526b77';ctx.font='12px system-ui';
      ctx.fillText(time===0?'Same initial cone in both panels':panel?'Junction pairs: 1–2 and 3–4':'Junction pairs: 1–4 and 2–3',left+14,top+ph-13);
    }
  }
  function setZoom(value){zoom=Math.max(.8,Math.min(3.5,value));sync();requestDraw();}
  input.addEventListener('input',()=>{time=Number(input.value);sync();requestDraw();});
  initial.addEventListener('click',()=>{time=time===0?Number(input.value):0;sync();requestDraw();});
  rays.addEventListener('click',()=>{showRays=!showRays;sync();requestDraw();});
  controls.querySelector('[data-view-action=in]').addEventListener('click',()=>setZoom(zoom*1.25));
  controls.querySelector('[data-view-action=out]').addEventListener('click',()=>setZoom(zoom/1.25));
  controls.querySelector('[data-view-action=reset]').addEventListener('click',()=>{time=1;zoom=1;showRays=true;input.value='1';sync();requestDraw();});
  canvas.addEventListener('keydown',e=>{if(['+','=','-'].includes(e.key)){e.preventDefault();setZoom(zoom*(e.key==='-'?.8:1.25));}});
  canvas.addEventListener('wheel',e=>{if(document.activeElement!==canvas)return;e.preventDefault();setZoom(zoom*Math.exp(-e.deltaY*.0015));},{passive:false});
  figure.querySelector('img').hidden=true;canvas.hidden=false;controls.hidden=false;help.hidden=false;
  new ResizeObserver(requestDraw).observe(stage);sync();requestDraw();
}
