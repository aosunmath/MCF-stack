// Original topology model informed by HMW, arXiv:2605.09657v1. No PDE is solved.
export const EXPANDER_COUNTS=[4,12,20];
export function expanderModelUrl(base,m){
  if(!EXPANDER_COUNTS.includes(m))throw new Error('Unsupported model count');
  return base.replace(/high-genus-expanders\.json$/,`high-genus-expanders${m===4?'':`-${m}`}.json`);
}
export function expanderSurface(data,type){
  if(type!==1&&type!==2)throw new Error('Unknown reflection-slice type');
  return {...data,vertices:data.vertices.map(([x,y,z],i)=>[x,y,(type===1?z:-z)+data.endShear[i]]),
    faces:type===1?data.faces:data.faces.map(([a,b,c])=>[a,c,b]),
    vertexColors:type===1?data.vertexColors:data.vertices.map(([x,y,z])=>{
      const level=Math.max(-1,Math.min(1,-z/(.72*Math.sqrt(.15)*Math.max(Math.hypot(x,y),.01))));
      const end=level>=0?[76,142,173]:[90,166,147],middle=[218,155,87];
      return middle.map((c,i)=>Math.round(c*(1-Math.abs(level))+end[i]*Math.abs(level)));
    })};
}
export function expanderNormals(vertices,faces){
  const normals=vertices.map(()=>[0,0,0]);
  for(const [a,b,c] of faces){
    const u=vertices[b].map((v,i)=>v-vertices[a][i]),v=vertices[c].map((w,i)=>w-vertices[a][i]);
    const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
    for(const j of [a,b,c])for(let k=0;k<3;k++)normals[j][k]+=n[k];
  }
  return normals.map(n=>{const r=Math.hypot(...n)||1;return n.map(v=>v/r);});
}
export function initHighGenusExpanderFigure(figure,initial){
  const canvas=figure.querySelector('canvas'),gl=canvas.getContext('webgl',{antialias:true,alpha:false});
  if(!gl)throw new Error('WebGL unavailable');
  const vertex=`attribute vec3 position, normal, color;
    uniform mat3 rotation; uniform vec2 scale;
    varying vec3 world, norm, tint;
    void main(){world=position;norm=rotation*normal;tint=color;
      vec3 p=rotation*position;gl_Position=vec4(p.x*scale.x,p.y*scale.y,-p.z/20.0,1.0);}`;
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
  const uniforms=Object.fromEntries(['rotation','scale','cutaway','lines'].map(k=>[k,gl.getUniformLocation(program,k)]));
  const buffers=Object.fromEntries(['position','normal','color'].map(k=>[k,{buffer:gl.createBuffer(),location:gl.getAttribLocation(program,k)}]));
  const indexBuffer=gl.createBuffer(),meshBuffer=gl.createBuffer();
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  const status=figure.querySelector('.soliton-status'),help=figure.querySelector('.soliton-help');
  const cache=new Map([[initial.m,initial]]);
  let data=initial,indices,meshIndices,scheduled=false,dragging=null,loadId=0;
  const defaults=()=>({yaw:initial.view.yaw,pitch:initial.view.pitch,zoom:1,mode:'surface',wire:false,m:initial.m,type:1});
  let state=defaults();
  const badge=document.createElement('p');badge.className='expander-view-label';stage.append(badge);
  function upload(){
    const shown=state.mode==='cone'?initial.coneMesh:expanderSurface(data,state.type);
    if(shown.vertices.length>65535)throw new Error('Illustration exceeds index limit');
    const arrays={position:shown.vertices,normal:expanderNormals(shown.vertices,shown.faces),color:shown.vertexColors.map(c=>c.map(v=>v/255))};
    for(const [name,values] of Object.entries(arrays)){
      const {buffer,location}=buffers[name];gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
      gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(values.flat()),gl.STATIC_DRAW);
      gl.enableVertexAttribArray(location);gl.vertexAttribPointer(location,3,gl.FLOAT,false,0,0);
    }
    indices=new Uint16Array(shown.faces.flat());gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,indices,gl.STATIC_DRAW);
    meshIndices=new Uint16Array(shown.faces.flatMap(([a,b,c])=>[a,b,b,c,c,a]));
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
    const radius=initial.view.radius,vertical=Math.max(1.6,3.5*Math.abs(sp)+1.1*Math.abs(cp));
    const scale=Math.min(w*.44/radius,h*.44/vertical)*state.zoom;
    gl.uniform2f(uniforms.scale,2*scale/w,2*scale/h);gl.uniform1i(uniforms.cutaway,state.mode==='cutaway');gl.uniform1i(uniforms.lines,false);
    gl.enable(gl.DEPTH_TEST);gl.frontFace(gl.CW);gl.disable(gl.CULL_FACE);gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);gl.drawElements(gl.TRIANGLES,indices.length,gl.UNSIGNED_SHORT,0);
    gl.disable(gl.POLYGON_OFFSET_FILL);
    if(state.wire){gl.uniform1i(uniforms.lines,true);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,meshBuffer);gl.drawElements(gl.LINES,meshIndices.length,gl.UNSIGNED_SHORT,0);}
    canvas.dataset.m=String(state.m);canvas.dataset.genus=String(state.m-1);canvas.dataset.type=String(state.type);canvas.dataset.view=state.mode;canvas.dataset.zoom=state.zoom.toFixed(3);
    canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;canvas.dataset.mesh=String(state.wire);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  const makeSelect=(title,aria,options)=>{
    const label=document.createElement('label');label.textContent=title+' ';
    const select=document.createElement('select');select.setAttribute('aria-label',aria);
    for(const [value,title] of options){const o=document.createElement('option');o.value=value;o.textContent=title;select.append(o);}
    label.append(select);controls.append(label);return select;
  };
  const view=makeSelect('View','Expander model view',[['surface','Full surface'],['cutaway','Cutaway'],['cone','Fixed cone']]);
  const count=makeSelect('Model genus','Illustrative genus',EXPANDER_COUNTS.map(m=>[String(m),`${m-1} (q = ${m/4})`]));
  const type=makeSelect('Slice pairing','Reflection-slice type',[['1','Type 1: middle to upper'],['2','Type 2: middle to lower']]);
  const legend=document.createElement('p');legend.className='expander-legend';
  legend.textContent='Three ends encircle the z-axis. The end colors blend through the connected core; they are not separate components.';
  controls.after(legend);
  function sync(){
    const cone=state.mode==='cone';view.value=state.mode;count.value=String(state.m);type.value=String(state.type);
    count.disabled=cone;type.disabled=cone;
    figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed',String(state.wire));
    badge.textContent=cone?'Fixed illustrative cone · three sheets':'Topology model · genus '+(state.m-1)+' · three ends';
    canvas.setAttribute('aria-label',cone?'Illustrative fixed cone with three nonrotational sheets, not the cone of a computed shrinker. Arrow keys rotate; plus and minus zoom.':`Connected schematic with genus ${state.m-1} and three ends, type ${state.type} slice pairing. Not a solved self-expander. Arrow keys rotate; plus and minus zoom.`);
    help.textContent='Drag to rotate; + / − zoom. Cutaway exposes the core. Fixed cone shows the same three sheets for every genus and both slice types.';
    status.textContent=cone?'The cone is chosen for this drawing; its opening is not a verified admissible bound from the theorem. The vertex is singular.':`Illustrative k = 4, q = ${state.m/4}, genus qk − 1 = ${state.m-1}. The theorem requires a suitable cone and sufficiently large k; these small display counts are not existence claims. No expander equation is solved. The mesh does not model the big/small distinction. Outer and cut edges are artificial.`;
    requestDraw();
  }
  async function changeCount(m){
    const id=++loadId;status.textContent='Loading the topology model…';
    try{
      if(!cache.has(m)){const response=await fetch(expanderModelUrl(figure.dataset.soliton,m));if(!response.ok)throw new Error('mesh unavailable');const next=await response.json();if(next.m!==m)throw new Error('Wrong genus model');cache.set(m,next);}
      if(id!==loadId)return;
      const previous=data,oldM=state.m;data=cache.get(m);state.m=m;
      try{upload();}catch(error){data=previous;state.m=oldM;upload();throw error;}
      sync();
    }catch{if(id===loadId){count.value=String(state.m);status.textContent='This model could not load; the previous valid view remains displayed.';}}
  }
  view.addEventListener('change',()=>{state.mode=view.value;if(state.mode==='cutaway')state.pitch=.43;upload();sync();});
  count.addEventListener('change',()=>changeCount(Number(count.value)));
  type.addEventListener('change',()=>{state.type=Number(type.value);upload();sync();});
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
