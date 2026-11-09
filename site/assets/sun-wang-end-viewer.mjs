// Slices of an auxiliary end in R^4. Neither the shrinker nor u is solved here.
import {SPHERICAL_COUNTS,sphericalModelUrl} from './spherical-doubling-viewer.mjs';

export function endSliceScale(ratio,rescaled=false){
  if(!Number.isFinite(ratio)||ratio<1||ratio>9)throw new Error('Unsupported height ratio');
  return rescaled?1:Math.sqrt(ratio);
}

export function endModelUrl(base,m){
  return sphericalModelUrl(base.replace(/sun-wang-doubled-sphere-end\.json$/,'sphere-doubling-shrinker.json'),m);
}

export function initSunWangEndFigure(figure,initial){
  const canvas=figure.querySelector('canvas'),gl=canvas.getContext('webgl',{antialias:true,alpha:false});
  if(!gl)throw new Error('WebGL unavailable');
  const vertex=`attribute vec3 position, normal, color;
    uniform mat3 rotation; uniform vec2 scale; uniform float dilation;
    varying vec3 world, norm, tint;
    void main(){world=position;norm=rotation*normal;tint=color;
      vec3 p=dilation*(rotation*position);gl_Position=vec4(p.x*scale.x,p.y*scale.y,-p.z/28.0,1.0);}`;
  const fragment=`precision mediump float;
    varying vec3 world, norm, tint; uniform bool cutaway, lines;
    void main(){if(cutaway && world.y>0.0)discard;
      if(lines){gl_FragColor=vec4(.12,.25,.30,1.0);return;}
      vec3 n=normalize(norm);if(!gl_FrontFacing)n=-n;
      float light=.48+.50*max(0.0,dot(n,normalize(vec3(-.35,.55,.80))));
      float shine=pow(max(0.0,dot(n,normalize(vec3(-.18,.28,1.0)))),40.0);
      gl_FragColor=vec4(tint*light+vec3(.12)*shine,1.0);}`;
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Shader compilation failed');return s;}
  const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));
  gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Shader link failed');gl.useProgram(program);
  const uniforms=Object.fromEntries(['rotation','scale','dilation','cutaway','lines'].map(k=>[k,gl.getUniformLocation(program,k)]));
  const buffers=Object.fromEntries(['position','normal','color'].map(k=>[k,{buffer:gl.createBuffer(),location:gl.getAttribLocation(program,k)}]));
  const indexBuffer=gl.createBuffer(),meshBuffer=gl.createBuffer();
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  const status=figure.querySelector('.soliton-status'),help=figure.querySelector('.soliton-help');
  let data=initial,indices,meshIndices,scheduled=false,dragging=null,loadId=0;
  const cache=new Map([[initial.m,initial]]);
  const defaults=()=>({yaw:.23,pitch:.27,zoom:1,cutaway:true,wire:false,ratio:9,rescaled:false});
  let state=defaults();
  figure.classList.add('sw-end-figure');
  const badge=document.createElement('p');badge.className='sw-end-label';stage.append(badge);
  const scaleNote=document.createElement('p');scaleNote.className='sw-end-scale';stage.append(scaleNote);
  function upload(){
    if(data.vertices.length>65535)throw new Error('Illustration exceeds index limit');
    const arrays={position:data.vertices,normal:data.normals,color:data.vertexGroups.map(g=>data.palette[g].map(v=>v/255))};
    for(const [name,values] of Object.entries(arrays)){
      const {buffer,location}=buffers[name];gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
      gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(values.flat()),gl.STATIC_DRAW);
      gl.enableVertexAttribArray(location);gl.vertexAttribPointer(location,3,gl.FLOAT,false,0,0);
    }
    indices=new Uint16Array(data.faces.flat());gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,indices,gl.STATIC_DRAW);
    meshIndices=new Uint16Array(data.faces.flatMap(([a,b,c])=>[a,b,b,c,c,a]));
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,meshBuffer);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,meshIndices,gl.STATIC_DRAW);
  }
  function draw(){
    scheduled=false;
    const box=stage.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2),w=Math.round(box.width*dpr),h=Math.round(box.height*dpr);
    if(!w||!h)return;
    if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}
    gl.viewport(0,0,w,h);gl.clearColor(247/255,250/255,251/255,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    const cy=Math.cos(state.yaw),sy=Math.sin(state.yaw),cp=Math.cos(state.pitch),sp=Math.sin(state.pitch);
    gl.uniformMatrix3fv(uniforms.rotation,false,new Float32Array([cy,-sy*sp,sy*cp,-sy,-cy*sp,cy*cp,0,cp,sp]));
    // A fixed camera in each mode: height changes must not trigger auto-fitting.
    const radius=state.rescaled?2.65:7.1;
    const scale=Math.min(w*.44,h*.39)/radius*state.zoom;
    gl.uniform2f(uniforms.scale,2*scale/w,2*scale/h);
    gl.uniform1f(uniforms.dilation,endSliceScale(state.ratio,state.rescaled));
    gl.uniform1i(uniforms.cutaway,state.cutaway);gl.uniform1i(uniforms.lines,false);
    gl.enable(gl.DEPTH_TEST);gl.frontFace(gl.CW);gl.disable(gl.CULL_FACE);gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);gl.drawElements(gl.TRIANGLES,indices.length,gl.UNSIGNED_SHORT,0);gl.disable(gl.POLYGON_OFFSET_FILL);
    if(state.wire){gl.uniform1i(uniforms.lines,true);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,meshBuffer);gl.drawElements(gl.LINES,meshIndices.length,gl.UNSIGNED_SHORT,0);}
    Object.assign(canvas.dataset,{m:String(data.m),genus:String(data.genus),heightRatio:String(state.ratio),rescaled:String(state.rescaled),
      sliceScale:String(endSliceScale(state.ratio,state.rescaled)),view:state.cutaway?'cutaway':'surface',zoom:state.zoom.toFixed(3),
      rotation:`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`,mesh:String(state.wire)});
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  const heightLabel=document.createElement('label');heightLabel.className='sw-height-control';heightLabel.textContent='Height z / z* ';
  const height=document.createElement('input');height.type='range';height.min='1';height.max='9';height.step='.1';height.setAttribute('aria-label','Height ratio z over z star');
  const heightValue=document.createElement('output');heightLabel.append(height,heightValue);controls.prepend(heightLabel);
  const countLabel=document.createElement('label');countLabel.textContent='Sites per latitude ';
  const count=document.createElement('select');count.setAttribute('aria-label','Sites per latitude');
  for(const m of SPHERICAL_COUNTS){const option=document.createElement('option');option.value=String(m);option.textContent=`m = ${m}`;count.append(option);}
  countLabel.append(count);controls.append(countLabel);
  const cut=document.createElement('button');cut.type='button';cut.textContent='Cutaway';controls.append(cut);
  const rescale=document.createElement('button');rescale.type='button';rescale.textContent='Rescale by 1/√z';controls.append(rescale);
  const legend=document.createElement('p');legend.className='spherical-legend';
  for(const [name,color] of [['Outer sheet','#4b8ba3'],['Inner sheet','#d3a963'],['Connecting necks','#bc744d']]){
    const item=document.createElement('span'),dot=document.createElement('i');dot.style.background=color;dot.setAttribute('aria-hidden','true');item.append(dot,name);legend.append(item);
  }
  controls.after(legend);
  const equation=document.createElement('div');equation.className='sw-end-equation';
  const formula=document.createElement('p');formula.textContent='Actual slice: X = √z [x + uₘ(x,z)ν(x)],  x ∈ Sₘ';
  const explanation=document.createElement('p');explanation.textContent='The display uses a schematic Sₘ and omits the unknown correction uₘ → 0. The compact core is not shown. z* is an unspecified large reference height.';
  equation.append(formula,explanation);legend.after(equation);
  function sync(){
    count.value=String(data.m);height.value=String(state.ratio);heightValue.textContent=state.ratio.toFixed(1);
    height.setAttribute('aria-valuetext',`${state.ratio.toFixed(1)} times the reference height`);
    cut.setAttribute('aria-pressed',String(state.cutaway));rescale.setAttribute('aria-pressed',String(state.rescaled));
    figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed',String(state.wire));
    badge.textContent=`${state.rescaled?'Rescaled horizontal slice':'Horizontal slice in ℝ³ × {z}'} · ${2*data.m} bridges · genus ${data.genus}`;
    scaleNote.textContent=state.rescaled?'X / √z: the auxiliary slices coincide; the actual slices converge to Sₘ.'
      :`z / z* = ${state.ratio.toFixed(1)} · linear size ${Math.sqrt(state.ratio).toFixed(2)}× the reference slice`;
    canvas.setAttribute('aria-label',`Schematic horizontal slice of a three-dimensional translator in R4, at ${state.ratio} times a large reference height. ${2*data.m} bridges, cross-sectional genus ${data.genus}. ${state.cutaway?'Front half removed to reveal the inner sheet.':'Full closed surface.'} ${state.rescaled?'Rescaled by inverse square root of height.':'Fixed spatial scale.'} Arrow keys rotate; plus and minus zoom.`);
    help.textContent='Drag or use arrow keys to rotate; + / − zoom. Change height to see √z growth. Rescale to compare the limiting shape. Cut edges are only for display.';
    status.textContent=`One end, Sₘ × [z₀, ∞). The genus belongs to its two-dimensional slices, not to the three-dimensional translator. m = ${data.m} is an illustration choice; existence requires sufficiently large m. Neck sizes are enlarged. No soliton equation is solved by this mesh.`;
    requestDraw();
  }
  height.addEventListener('input',()=>{state.ratio=Number(height.value);sync();});
  cut.addEventListener('click',()=>{state.cutaway=!state.cutaway;sync();});
  rescale.addEventListener('click',()=>{state.rescaled=!state.rescaled;state.zoom=1;sync();});
  count.addEventListener('change',async()=>{
    const m=Number(count.value),id=++loadId;status.textContent=`Loading m = ${m}…`;
    try{
      if(!cache.has(m)){const response=await fetch(endModelUrl(figure.dataset.soliton,m));if(!response.ok)throw new Error('mesh unavailable');cache.set(m,await response.json());}
      if(id!==loadId)return;
      const previous=data;data=cache.get(m);
      try{upload();}catch(error){data=previous;upload();throw error;}
      sync();
    }catch{if(id===loadId){count.value=String(data.m);status.textContent=`m = ${m} could not load; m = ${data.m} remains displayed.`;}}
  });
  function zoom(f){state.zoom=Math.max(.5,Math.min(3,state.zoom*f));requestDraw();}
  for(const b of figure.querySelectorAll('[data-view-action]'))b.addEventListener('click',()=>{
    const action=b.dataset.viewAction;
    if(action==='in')zoom(1.2);if(action==='out')zoom(1/1.2);
    if(action==='wire'){state.wire=!state.wire;sync();}
    if(action==='reset'){++loadId;data=initial;state=defaults();dragging=null;upload();sync();}
  });
  canvas.addEventListener('pointerdown',e=>{dragging={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!dragging)return;state.yaw+=(e.clientX-dragging.x)*.009;state.pitch+=(e.clientY-dragging.y)*.009;dragging={x:e.clientX,y:e.clientY};requestDraw();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>{dragging=null;});
  canvas.addEventListener('keydown',e=>{
    const keys={ArrowLeft:()=>state.yaw-=.12,ArrowRight:()=>state.yaw+=.12,ArrowUp:()=>state.pitch-=.12,ArrowDown:()=>state.pitch+=.12,'+':()=>zoom(1.2),'=':()=>zoom(1.2),'-':()=>zoom(1/1.2)};
    if(keys[e.key]){e.preventDefault();keys[e.key]();requestDraw();}
  });
  canvas.addEventListener('wheel',e=>{if(document.activeElement!==canvas)return;e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  canvas.addEventListener('webglcontextlost',e=>{
    e.preventDefault();canvas.hidden=true;badge.hidden=true;scaleNote.hidden=true;legend.hidden=true;equation.hidden=true;
    figure.querySelector('img').hidden=false;controls.hidden=true;help.hidden=true;
    status.textContent='The graphics context was lost; the static drawing is shown. Reload to restore interaction.';
  });
  upload();sync();controls.hidden=false;help.hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;
  new ResizeObserver(requestDraw).observe(stage);
}
