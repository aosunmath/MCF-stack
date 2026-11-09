// Nguyen tridents: an illustrative deformation of Scherk, not a solved translator.
export const TRIDENT_SCALES=[22,35,50];
export function tridentModelUrl(base,scale){
  if(!TRIDENT_SCALES.includes(scale))throw new Error('Unsupported scale');
  return base.replace(/nguyen-tridents\.json$/,`nguyen-tridents${scale===35?'':`-${scale}`}.json`);
}
export function tridentNormals(vertices,faces){
  const normals=vertices.map(()=>[0,0,0]);
  for(const [a,b,c] of faces){
    const u=vertices[b].map((v,i)=>v-vertices[a][i]),v=vertices[c].map((w,i)=>w-vertices[a][i]);
    const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
    for(const j of [a,b,c])for(let k=0;k<3;k++)normals[j][k]+=n[k];
  }
  return normals.map(n=>{const r=Math.hypot(...n)||1;return n.map(v=>v/r);});
}
export function initTridentFigure(figure,initial){
  const canvas=figure.querySelector('canvas'),gl=canvas.getContext('webgl',{antialias:true,alpha:false});
  if(!gl)throw new Error('WebGL unavailable');
  const vertex=`attribute vec3 position, normal, color;
    uniform mat3 rotation; uniform vec2 scale; uniform vec3 center;
    varying vec3 world, norm, tint;
    void main(){world=position;norm=rotation*normal;tint=color;
      vec3 p=rotation*(position-center);gl_Position=vec4(p.x*scale.x,p.y*scale.y,-p.z/20.0,1.0);}`;
  const fragment=`precision mediump float;
    varying vec3 world, norm, tint; uniform bool cutaway, lines;
    void main(){if(cutaway && world.y>0.0)discard;
      if(lines){gl_FragColor=vec4(.12,.25,.30,1.0);return;}
      vec3 n=normalize(norm);if(!gl_FrontFacing)n=-n;
      float light=.50+.48*max(0.0,dot(n,normalize(vec3(-.35,.55,.80))));
      float shine=pow(max(0.0,dot(n,normalize(vec3(-.18,.28,1.0)))),40.0);
      gl_FragColor=vec4(tint*light+vec3(.10)*shine,1.0);}`;
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Shader compilation failed');return s;}
  const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));
  gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Shader link failed');gl.useProgram(program);
  const uniforms=Object.fromEntries(['rotation','scale','center','cutaway','lines'].map(k=>[k,gl.getUniformLocation(program,k)]));
  const buffers=Object.fromEntries(['position','normal','color'].map(k=>[k,{buffer:gl.createBuffer(),location:gl.getAttribLocation(program,k)}]));
  const indexBuffer=gl.createBuffer(),meshBuffer=gl.createBuffer();
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  const status=figure.querySelector('.soliton-status'),help=figure.querySelector('.soliton-help');
  const cache=new Map([[Math.round(initial.epsilon*100),initial]]);
  let data=initial,indices,meshIndices,scheduled=false,dragging=null,loadId=0;
  const defaults=()=>({yaw:initial.view.yaw,pitch:initial.view.pitch,zoom:1,mode:'surface',wire:false,m:Math.round(initial.epsilon*100)});
  let state=defaults();
  const badge=document.createElement('p');badge.className='trident-view-label';stage.append(badge);
  function upload(){
    if(data.vertices.length>65535)throw new Error('Illustration exceeds index limit');
    const arrays={position:data.vertices,normal:tridentNormals(data.vertices,data.faces),color:data.vertexColors.map(c=>c.map(v=>v/255))};
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
    let horizontal=0,vertical=0;
    for(const p of data.vertices){
      const x=p[0]-data.view.center[0],y=p[1],z=p[2]-data.view.center[2];
      horizontal=Math.max(horizontal,Math.abs(cy*x-sy*y));
      vertical=Math.max(vertical,Math.abs(cp*z-sp*(sy*x+cy*y)));
    }
    const scale=Math.min(w*.42/horizontal,h*.37/vertical)*state.zoom;
    gl.uniform3fv(uniforms.center,new Float32Array(data.view.center));
    gl.uniform2f(uniforms.scale,2*scale/w,2*scale/h);gl.uniform1i(uniforms.cutaway,state.mode==='half');gl.uniform1i(uniforms.lines,false);
    gl.enable(gl.DEPTH_TEST);gl.frontFace(gl.CW);gl.disable(gl.CULL_FACE);gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);gl.drawElements(gl.TRIANGLES,indices.length,gl.UNSIGNED_SHORT,0);
    gl.disable(gl.POLYGON_OFFSET_FILL);
    if(state.wire){gl.uniform1i(uniforms.lines,true);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,meshBuffer);gl.drawElements(gl.LINES,meshIndices.length,gl.UNSIGNED_SHORT,0);}
    canvas.dataset.neckScale=String(state.m);canvas.dataset.view=state.mode;canvas.dataset.zoom=state.zoom.toFixed(3);
    canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;canvas.dataset.mesh=String(state.wire);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  const viewLabel=document.createElement('label');viewLabel.textContent='View ';
  const view=document.createElement('select');view.setAttribute('aria-label','Trident view');
  for(const [value,title] of [['surface','Full surface'],['half','Half surface'],['end','End view']]){const o=document.createElement('option');o.value=value;o.textContent=title;view.append(o);}
  viewLabel.append(view);controls.prepend(viewLabel);
  const countLabel=document.createElement('label');countLabel.textContent='Drawing neck scale ';
  const count=document.createElement('select');count.setAttribute('aria-label','Illustrative neck scale');
  for(const m of TRIDENT_SCALES){const o=document.createElement('option');o.value=String(m);o.textContent=`ε = ${(m/100).toFixed(2)}`;count.append(o);}
  countLabel.append(count);controls.append(countLabel);
  const legend=document.createElement('p');legend.className='trident-legend';
  for(const [name,color] of [['Grim-reaper wings','#4b8ea9'],['Saddle connections','#da954e'],['Central sheet','#58a697']]){
    const item=document.createElement('span'),dot=document.createElement('i');dot.style.background=color;dot.setAttribute('aria-hidden','true');item.append(dot,name);legend.append(item);
  }
  controls.after(legend);
  function sync(){
    view.value=state.mode;count.value=String(state.m);
    figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed',String(state.wire));
    badge.textContent='Construction schematic · three periods · upward translation';
    canvas.setAttribute('aria-label',`Connected trident construction schematic, ${state.mode==='half'?'half surface':state.mode==='end'?'end view near the periodic direction':'full surface'}, illustrative neck scale ${data.epsilon}. Not a solved translator. Arrow keys rotate; plus and minus zoom.`);
    help.textContent=state.mode==='half'?'One side is hidden to expose the saddle connections. The cut at y = 0 is artificial. Drag to rotate; + / − zoom.':state.mode==='end'?'Look nearly along the periodic x-direction: the wings rise toward two outer planes, with the central sheet between them. Drag to rotate; + / − zoom.':'Drag to rotate; + / − zoom. Half surface exposes the joining saddles; End view reveals the trident profile.';
    status.textContent=`Illustrative ε = ${data.epsilon.toFixed(2)}, period 2πε ≈ ${data.period.toFixed(2)}. The neck scale changes the drawing, not a computed family of translators. Three periods and finite heights are shown; the actual surface continues without boundary.`;
    requestDraw();
  }
  async function change(mode,m){
    const id=++loadId;
    status.textContent='Loading the construction view…';
    try{
      if(!cache.has(m)){const response=await fetch(tridentModelUrl(figure.dataset.soliton,m));if(!response.ok)throw new Error('mesh unavailable');const next=await response.json();if(Math.round(next.epsilon*100)!==m)throw new Error('Wrong neck scale');cache.set(m,next);}
      if(id!==loadId)return;
      const previous=data;data=cache.get(m);
      try{upload();}catch(error){data=previous;upload();throw error;}
      if(mode!==state.mode){state.yaw=mode==='end'?1.42:data.view.yaw;state.pitch=mode==='end'?-.08:data.view.pitch;state.zoom=1;}
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
