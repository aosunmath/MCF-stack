// A finite-domain numerical translator; the exact grim profile is only a limit.
export function grimHeight(y,b){
  if(!(b>Math.PI/2)||Math.abs(y)>=b)throw new Error('Point outside the open strip');
  const c=Math.PI/(2*b);return -Math.log(Math.cos(c*y))/(c*c);
}
export function sectionAt(data,x){
  const stations=data.sectionStations;
  if(x<stations[0]||x>stations.at(-1))throw new Error('Section outside the computed window');
  const j=Math.min(stations.length-2,stations.findIndex(v=>v>=x)-1);
  const i=Math.max(0,j),t=(x-stations[i])/(stations[i+1]-stations[i]);
  return data.sections[i].map(([y,z],k)=>[y,z*(1-t)+data.sections[i+1][k][1]*t]);
}

export function initDeltaWingFigure(figure,data){
  const canvas=figure.querySelector('canvas'),stage=figure.querySelector('.soliton-stage');
  const controls=figure.querySelector('.soliton-controls'),help=figure.querySelector('.soliton-help');
  const status=figure.querySelector('.soliton-status');
  const gl=canvas.getContext('webgl',{antialias:true,alpha:false});
  if(!gl)throw new Error('WebGL unavailable');
  const vertex=`attribute vec3 position,normal;uniform mat3 rotation;uniform vec2 scale;
    uniform float center;varying vec3 norm;varying float height;varying float across;
    void main(){height=position.z;across=position.y;norm=rotation*normal;
    vec3 p=rotation*(position-vec3(0.,0.,center));
    gl_Position=vec4(p.x*scale.x,p.y*scale.y,-p.z/30.,1.);}`;
  const fragment=`precision mediump float;varying vec3 norm;varying float height;varying float across;
    uniform float cutoff;uniform int lines;uniform bool cutaway;
    void main(){if(height>cutoff+.00001||(cutaway&&across>.00001))discard;
      if(lines>0){gl_FragColor=lines==2?vec4(.82,.52,.20,1.):vec4(.16,.36,.44,1.);return;}
      vec3 n=normalize(norm);if(!gl_FrontFacing)n=-n;
      float light=.57+.43*max(0.,dot(n,normalize(vec3(-.35,.5,.8))));
      gl_FragColor=vec4(vec3(.32,.61,.67)*light,1.);}`;
  function shader(type,source){
    const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);
    if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Shader failed');return s;
  }
  const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));
  gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Shader link failed');gl.useProgram(program);
  for(const [name,values] of [['position',data.vertices],['normal',data.normals]]){
    const buffer=gl.createBuffer(),loc=gl.getAttribLocation(program,name);gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(values.flat()),gl.STATIC_DRAW);gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,3,gl.FLOAT,false,0,0);
  }
  function indexBuffer(values){const buffer=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,buffer);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array(values),gl.STATIC_DRAW);return {buffer,count:values.length};}
  const faces=indexBuffer(data.faces.flat());
  const mesh=indexBuffer(data.faces.flatMap(([a,b,c])=>[a,b,b,c,c,a]));
  const contours=indexBuffer(data.paths.flatMap(p=>p.slice(1).flatMap((v,i)=>[p[i],v])));
  const profileLines=[];
  for(const a of [0,48,96,144]){
    const path=[0,...Array.from({length:48},(_,i)=>1+i*192+a)];
    path.slice(1).forEach((v,i)=>profileLines.push(path[i],v));
  }
  const symmetry=indexBuffer(profileLines);
  const uniforms=Object.fromEntries(['rotation','scale','center','cutoff','lines','cutaway'].map(k=>[k,gl.getUniformLocation(program,k)]));
  const plot=document.createElement('canvas');plot.hidden=true;plot.tabIndex=0;plot.setAttribute('role','img');stage.append(plot);
  const ctx=plot.getContext('2d');if(!ctx)throw new Error('Canvas unavailable');
  const badge=document.createElement('p');badge.className='delta-view-label';stage.append(badge);
  const defaults=()=>({yaw:data.view.yaw,pitch:data.view.pitch,zoom:1,mode:'surface',height:6,section:0,wire:false});
  let state=defaults(),scheduled=false,dragging=null;
  const viewLabel=document.createElement('label');viewLabel.textContent='View ';
  const view=document.createElement('select');view.setAttribute('aria-label','Delta-wing view');
  for(const [value,title] of [['surface','Full surface'],['cutaway','Cutaway'],['along','Along the strip'],['across','Across the strip']]){
    const option=document.createElement('option');option.value=value;option.textContent=title;view.append(option);
  }
  viewLabel.append(view);controls.prepend(viewLabel);
  function slider(name,min,max,step,value){
    const label=document.createElement('label'),output=document.createElement('output'),input=document.createElement('input');
    input.type='range';Object.assign(input,{min:String(min),max:String(max),step:String(step),value:String(value)});
    input.setAttribute('aria-label',name);label.append(output,input);controls.append(label);return {label,output,input};
  }
  const height=slider('Displayed height',3,6,.25,6),section=slider('Transverse section x',0,6,.25,0);
  const legend=document.createElement('p');legend.className='delta-legend';controls.after(legend);
  function sync(){
    const surface=['surface','cutaway'].includes(state.mode);view.value=state.mode;height.label.hidden=!surface;section.label.hidden=state.mode!=='across';
    height.input.value=String(state.height);height.output.textContent=`Height ≤ ${state.height.toFixed(2)}`;
    section.input.value=String(state.section);section.output.textContent=`x = ${state.section.toFixed(2)}`;
    canvas.hidden=!surface;plot.hidden=surface;
    const wire=figure.querySelector('[data-view-action="wire"]');wire.disabled=!surface;wire.setAttribute('aria-pressed',String(state.wire));
    badge.textContent=surface?`2b = √2 π · numerical PDE ${state.mode==='cutaway'?'cutaway':'surface'} · upward speed 1`:state.mode==='along'?'Longitudinal profile · y = 0':'Transverse profiles · recentered to height zero';
    legend.textContent=surface?'Teal: numerical surface. Gold: the two symmetry sections. Lines: unit-height contours.':state.mode==='along'?'Blue: numerical profile. Dashed ochre: reference slopes ±1, aligned at x = ±8.':'Blue: numerical section. Dashed ochre: the exact limiting tilted grim profile.';
    help.textContent=surface?(state.mode==='cutaway'?'The y > 0 half is hidden to expose the rounded center. Drag to rotate; + / − zoom.':'Drag to rotate; use + / − to zoom. Cutaway reveals the center. The height control trims the displayed patch.'):'Use the view selector to compare the profiles. Across the strip, move x outward to see the approach to the grim-reaper limit.';
    status.textContent='Strip width 2b ≈ 4.44288; limiting tilt angles ±45°. The complete surface has no boundary.';
    canvas.setAttribute('aria-label',`Numerical Delta-wing on a strip of width square root of 2 times pi, truncated at height ${state.height}${state.mode==='cutaway'?', with the y positive half hidden':''}. Arrow keys rotate; plus and minus zoom.`);
    plot.setAttribute('aria-label',state.mode==='along'?'Longitudinal numerical profile with limiting slopes minus one and plus one.':`Numerical transverse profile at x=${state.section}, recentered, compared with the limiting tilted grim reaper.`);
    stage.dataset.view=state.mode;requestDraw();
  }
  function size(c){
    const box=stage.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2);
    if(c.width!==Math.round(box.width*dpr)||c.height!==Math.round(box.height*dpr)){c.width=Math.round(box.width*dpr);c.height=Math.round(box.height*dpr);}
    return {w:box.width,h:box.height,dpr};
  }
  function drawPlot(){
    const {w,h,dpr}=size(plot);ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
    const along=state.mode==='along',xmax=along?8:data.halfWidth,ymax=along?6:5.5;
    const left=48,right=w-18,top=52,bottom=h-40;
    const project=([x,y])=>[(left+right)/2+x*(right-left)/(2*xmax)*state.zoom,bottom-y*(bottom-top)/ymax*state.zoom];
    ctx.font='11px sans-serif';ctx.lineWidth=1;
    for(let y=0;y<=5;y++){
      const p=project([0,y]);ctx.strokeStyle='#dce6e9';ctx.beginPath();ctx.moveTo(left,p[1]);ctx.lineTo(right,p[1]);ctx.stroke();
      ctx.fillStyle='#526b77';ctx.fillText(String(y),left-18,p[1]+4);
    }
    const ticks=along?[-8,-4,0,4,8]:[-2,-1,0,1,2];ctx.textAlign='center';
    for(const x of ticks){const p=project([x,0]);if(p[0]>=left&&p[0]<=right)ctx.fillText(String(x),p[0],bottom+17);}
    ctx.fillText(along?'x · along the strip':'y · across the strip',(left+right)/2,h-7);ctx.textAlign='left';
    ctx.fillText(along?'z':'u(x,y) − u(x,0)',left,top-12);
    ctx.save();ctx.beginPath();ctx.rect(left,top,right-left,bottom-top);ctx.clip();
    function line(points,color,dash=[]){ctx.strokeStyle=color;ctx.lineWidth=2;ctx.setLineDash(dash);ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...project(p)):ctx.moveTo(...project(p)));ctx.stroke();}
    if(along){
      line(data.longitudinal,'#21667f');
      const z8=data.longitudinal.find(p=>Math.abs(p[0]-8)<1e-6)[1];
      for(const sign of [-1,1])line([[sign*2,z8-6],[sign*8,z8]],'#b17336',[6,4]);
    }else{line(data.grimSection,'#b17336',[6,4]);line(sectionAt(data,state.section),'#21667f');}
    ctx.restore();ctx.setLineDash([]);plot.dataset.zoom=state.zoom.toFixed(3);plot.dataset.section=String(state.section);
  }
  function draw(){
    scheduled=false;
    if(!['surface','cutaway'].includes(state.mode)){drawPlot();return;}
    const {w,h,dpr}=size(canvas);gl.viewport(0,0,canvas.width,canvas.height);
    gl.clearColor(247/255,250/255,251/255,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    const cy=Math.cos(state.yaw),sy=Math.sin(state.yaw),cp=Math.cos(state.pitch),sp=Math.sin(state.pitch);
    gl.uniformMatrix3fv(uniforms.rotation,false,new Float32Array([cy,-sy*sp,sy*cp,-sy,-cy*sp,cy*cp,0,cp,sp]));
    const scale=Math.min(w*.44/8.8,h*.39/4.7)*state.zoom;
    gl.uniform2f(uniforms.scale,2*scale/w,2*scale/h);gl.uniform1f(uniforms.center,2.8);gl.uniform1f(uniforms.cutoff,state.height);gl.uniform1i(uniforms.cutaway,state.mode==='cutaway');
    gl.enable(gl.DEPTH_TEST);gl.frontFace(gl.CW);gl.disable(gl.CULL_FACE);gl.uniform1i(uniforms.lines,0);
    gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,faces.buffer);gl.drawElements(gl.TRIANGLES,faces.count,gl.UNSIGNED_SHORT,0);gl.disable(gl.POLYGON_OFFSET_FILL);
    for(const [item,color] of [[state.wire?mesh:contours,1],[symmetry,2]]){
      gl.uniform1i(uniforms.lines,color);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,item.buffer);gl.drawElements(gl.LINES,item.count,gl.UNSIGNED_SHORT,0);
    }
    canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;canvas.dataset.zoom=state.zoom.toFixed(3);canvas.dataset.height=String(state.height);canvas.dataset.mesh=String(state.wire);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function zoom(f){state.zoom=Math.max(.65,Math.min(3,state.zoom*f));requestDraw();}
  view.addEventListener('change',()=>{state.mode=view.value;state.zoom=1;sync();});
  height.input.addEventListener('input',()=>{state.height=Number(height.input.value);sync();});
  section.input.addEventListener('input',()=>{state.section=Number(section.input.value);sync();});
  for(const button of figure.querySelectorAll('[data-view-action]'))button.addEventListener('click',()=>{
    const action=button.dataset.viewAction;
    if(action==='in')zoom(1.2);if(action==='out')zoom(1/1.2);
    if(action==='wire'){state.wire=!state.wire;sync();}
    if(action==='reset'){state=defaults();dragging=null;sync();}
  });
  canvas.addEventListener('pointerdown',e=>{dragging={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!dragging)return;state.yaw+=(e.clientX-dragging.x)*.009;state.pitch+=(e.clientY-dragging.y)*.009;dragging={x:e.clientX,y:e.clientY};requestDraw();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>dragging=null);
  for(const c of [canvas,plot]){
    c.addEventListener('keydown',e=>{
      if(['+','=','-'].includes(e.key)){e.preventDefault();zoom(e.key==='-'?1/1.2:1.2);}
      if(['surface','cutaway'].includes(state.mode)&&e.key.startsWith('Arrow')){e.preventDefault();if(e.key==='ArrowLeft')state.yaw-=.12;if(e.key==='ArrowRight')state.yaw+=.12;if(e.key==='ArrowUp')state.pitch-=.12;if(e.key==='ArrowDown')state.pitch+=.12;requestDraw();}
    });
    c.addEventListener('wheel',e=>{if(document.activeElement!==c)return;e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  }
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();canvas.hidden=true;plot.hidden=true;badge.hidden=true;legend.hidden=true;controls.hidden=true;help.hidden=true;figure.querySelector('img').hidden=false;status.textContent='The static drawing is shown. Reload to restore interactive geometry.';});
  figure.querySelector('img').hidden=true;controls.hidden=false;help.hidden=false;sync();new ResizeObserver(requestDraw).observe(stage);
}
