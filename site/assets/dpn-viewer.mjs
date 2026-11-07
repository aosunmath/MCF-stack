// Three-ended translator construction schematic and numerical ODE ingredients.
import {nguyenNormals as meshNormals} from './nguyen-viewer.mjs';
export const DPN_COUNTS=[8,12,16];
export function dpnModelUrl(base,model){
  if(model!=='input'&&!DPN_COUNTS.includes(model))throw new Error('Unsupported model');
  return base.replace(/bowl-catenoid-gluing\.json$/,model==='input'?'dpn-bowl-catenoid-input.json':`bowl-catenoid-gluing${model===12?'':`-${model}`}.json`);
}
export function initDpnFigure(figure,initial){
  const canvas=figure.querySelector('canvas'),gl=canvas.getContext('webgl',{antialias:true,alpha:false});
  if(!gl)throw new Error('WebGL unavailable');
  const vertex=`attribute vec3 position, normal, color;
    uniform mat3 rotation; uniform vec2 scale; uniform float centerShift;
    varying vec3 world, norm, tint;
    void main(){world=position;norm=rotation*normal;tint=color;
      vec3 p=rotation*(position+vec3(0.,0.,centerShift));gl_Position=vec4(p.x*scale.x,p.y*scale.y,-p.z/20.0,1.0);}`;
  const fragment=`precision mediump float;
    varying vec3 world, norm, tint; uniform bool cutaway, lines;
    void main(){if(cutaway && world.y>.35*abs(world.x))discard;
      if(lines){gl_FragColor=vec4(.12,.25,.30,1.0);return;}
      vec3 n=normalize(norm);if(!gl_FrontFacing)n=-n;
      float light=.50+.48*max(0.0,dot(n,normalize(vec3(-.35,.55,.80))));
      float shine=pow(max(0.0,dot(n,normalize(vec3(-.18,.28,1.0)))),40.0);
      gl_FragColor=vec4(tint*light+vec3(.10)*shine,1.0);}`;
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Shader compilation failed');return s;}
  const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));
  gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Shader link failed');gl.useProgram(program);
  const uniforms=Object.fromEntries(['rotation','scale','cutaway','lines','centerShift'].map(k=>[k,gl.getUniformLocation(program,k)]));
  const buffers=Object.fromEntries(['position','normal','color'].map(k=>[k,{buffer:gl.createBuffer(),location:gl.getAttribLocation(program,k)}]));
  const indexBuffer=gl.createBuffer(),meshBuffer=gl.createBuffer();
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  const status=figure.querySelector('.soliton-status'),help=figure.querySelector('.soliton-help');
  const cache=new Map([[initial.m,initial]]);
  let data=initial,indices,meshIndices,scheduled=false,dragging=null,loadId=0;
  const defaults=()=>({yaw:initial.view.yaw,pitch:initial.view.pitch,zoom:1,mode:'cutaway',wire:false,m:initial.m});
  let state=defaults();
  const badge=document.createElement('p');badge.className='dpn-view-label';stage.append(badge);
  function upload(){
    if(data.vertices.length>65535)throw new Error('Illustration exceeds index limit');
    const arrays={position:data.vertices.map(p=>[p[0],p[1],p[2]-data.view.centerZ]),normal:meshNormals(data.vertices,data.faces),color:data.vertexColors.map(c=>c.map(v=>v/255))};
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
    const radius=state.mode==='belt'?2.1:data.view.radius,vertical=state.mode==='belt'?1.55:3.6;
    const scale=Math.min(w*.44/radius,h*.39/vertical)*state.zoom;
    gl.uniform1f(uniforms.centerShift,state.mode==='belt'?1.2:-.8);
    gl.uniform2f(uniforms.scale,2*scale/w,2*scale/h);gl.uniform1i(uniforms.cutaway,state.mode!=='surface');gl.uniform1i(uniforms.lines,false);
    gl.enable(gl.DEPTH_TEST);gl.frontFace(gl.CW);gl.disable(gl.CULL_FACE);gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);gl.drawElements(gl.TRIANGLES,indices.length,gl.UNSIGNED_SHORT,0);
    gl.disable(gl.POLYGON_OFFSET_FILL);
    if(state.wire){gl.uniform1i(uniforms.lines,true);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,meshBuffer);gl.drawElements(gl.LINES,meshIndices.length,gl.UNSIGNED_SHORT,0);}
    canvas.dataset.m=String(state.m);canvas.dataset.view=state.mode;canvas.dataset.zoom=state.zoom.toFixed(3);
    canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;canvas.dataset.mesh=String(state.wire);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  const viewLabel=document.createElement('label');viewLabel.textContent='View ';
  const view=document.createElement('select');view.setAttribute('aria-label','Construction view');
  for(const [value,title] of [['cutaway','Cutaway'],['surface','Full surface'],['belt','Tunnel detail'],['input','Numerical input']]){const o=document.createElement('option');o.value=value;o.textContent=title;view.append(o);}
  viewLabel.append(view);controls.prepend(viewLabel);
  const countLabel=document.createElement('label');countLabel.textContent='Illustrative periods ';
  const count=document.createElement('select');count.setAttribute('aria-label','Illustrative Scherk period count');
  for(const m of DPN_COUNTS){const o=document.createElement('option');o.value=String(m);o.textContent=`m = ${m}`;count.append(o);}
  countLabel.append(count);controls.append(countLabel);
  const legend=document.createElement('p');legend.className='dpn-legend';
  for(const [name,color] of [['Bowl sheet','#4d8fae'],['Catenoid sheets','#61a697'],['Tunnel belt','#dc994f']]){
    const item=document.createElement('span'),dot=document.createElement('i');dot.style.background=color;dot.setAttribute('aria-hidden','true');item.append(dot,name);legend.append(item);
  }
  controls.after(legend);
  function sync(){
    const input=state.mode==='input';legend.lastElementChild.hidden=input;view.value=state.mode;count.value=String(state.m);count.disabled=input;
    figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed',String(state.wire));
    badge.textContent=input?'Numerical ODE input · sheets intersect':`Construction schematic · ${state.m} periods · three ends`;
    canvas.setAttribute('aria-label',input?'Numerically integrated bowl and translating catenoid, with a front wedge removed. The two surfaces intersect. Arrow keys rotate; plus and minus zoom.':`Three-ended translator construction schematic with ${state.m} periods. ${state.mode==='surface'?'Full surface':'Cutaway'}. Not a solved translator. Arrow keys rotate; plus and minus zoom.`);
    help.textContent='Drag to rotate; + / − zoom. Cutaway opens the front; Tunnel detail enlarges the joining region. Numerical input shows the intersecting ODE surfaces before smoothing.';
    status.textContent=input?'Unit upward speed; neck radius R = 1, intersection radius ρ = 1.4. Numerical ODE solutions, truncated at z = 4.4. This singular input is not the completed translator.':`Schematic with ${state.m} periods and model genus ${data.modelGenus}. The theorem requires sufficiently small gluing scale (large genus); these counts are illustrative. The gold tunnel belt has not been corrected to solve the translator equation. Rim and cut edges are display boundaries.`;
    requestDraw();
  }
  async function change(mode,m){
    const id=++loadId,key=mode==='input'?'input':m;
    status.textContent='Loading the construction view…';
    try{
      if(!cache.has(key)){const response=await fetch(dpnModelUrl(figure.dataset.soliton,key));if(!response.ok)throw new Error('mesh unavailable');const next=await response.json();if(key!=='input'&&next.m!==key)throw new Error('Wrong period count');cache.set(key,next);}
      if(id!==loadId)return;
      const previous=data;data=cache.get(key);
      try{upload();}catch(error){data=previous;upload();throw error;}
      if((state.mode==='input')!==(mode==='input')){state.yaw=data.view.yaw;state.pitch=data.view.pitch;state.zoom=1;}
      if(mode==='belt'){state.yaw=0;state.pitch=.18;state.zoom=1;} else if(state.mode==='belt'){state.yaw=data.view.yaw;state.pitch=data.view.pitch;state.zoom=1;}
      state.mode=mode;state.m=m;sync();
    }catch{if(id===loadId){view.value=state.mode;count.value=String(state.m);status.textContent='This model could not load; the previous valid view remains displayed.';}}
  }
  view.addEventListener('change',()=>change(view.value,state.m));
  count.addEventListener('change',()=>change(state.mode,Number(count.value)));
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
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();canvas.hidden=true;badge.hidden=true;legend.hidden=true;figure.querySelector('img').hidden=false;controls.hidden=true;help.hidden=true;status.textContent='The graphics context was lost; the static drawing is shown. Reload to restore interaction.';});
  upload();sync();controls.hidden=false;help.hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;
  new ResizeObserver(requestDraw).observe(stage);
}
