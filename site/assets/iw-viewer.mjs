// Original Ilmanen–White graph-and-neck schematic, not a computed self-shrinker.
export const IW_GENERA = [2, 3, 5, 11];
export function iwModelUrl(base, genus) {
  if (!IW_GENERA.includes(genus)) throw new Error('Unsupported illustration genus');
  return base.replace(/iw-two-ended\.json$/, `iw-two-ended${genus===3?'':`-${genus}`}.json`);
}
export function initIWFigure(figure, initial) {
  const canvas=figure.querySelector('canvas');
  const gl=canvas.getContext('webgl',{antialias:true,alpha:false});
  if(!gl)throw new Error('WebGL unavailable');
  const vertex=`attribute vec3 position, normal;
    uniform mat3 rotation; uniform vec2 scale;
    varying vec3 world, norm;
    void main(){world=position; norm=rotation*normal;
      vec3 p=rotation*position;
      gl_Position=vec4(p.x*scale.x,p.y*scale.y,-p.z/30.0,1.0);}`;
  const fragment=`precision mediump float;
    varying vec3 world, norm;
    uniform bool cutaway, lines, equator;
    void main(){if(cutaway && !equator && world.x+world.y>0.0001)discard;
      if(equator){gl_FragColor=vec4(.78,.32,.09,1.0);return;}
      if(lines){gl_FragColor=vec4(.12,.25,.30,1.0);return;}
      vec3 n=normalize(norm); bool front=gl_FrontFacing;
      if(!front)n=-n;
      vec3 color=front?vec3(.27,.54,.62):vec3(.82,.60,.32);
      float light=.43+.53*max(0.0,dot(n,normalize(vec3(-.35,.55,.80))));
      float shine=pow(max(0.0,dot(n,normalize(vec3(-.18,.28,1.0)))),36.0);
      gl_FragColor=vec4(color*light+vec3(.17)*shine,1.0);}`;
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Shader compilation failed');return s;}
  const program=gl.createProgram();
  gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));
  gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Shader link failed');gl.useProgram(program);
  const loc=Object.fromEntries(['rotation','scale','cutaway','lines','equator'].map(k=>[k,gl.getUniformLocation(program,k)]));
  const positions=gl.getAttribLocation(program,'position'),normals=gl.getAttribLocation(program,'normal');
  const vertexBuffer=gl.createBuffer(),normalBuffer=gl.createBuffer(),indexBuffer=gl.createBuffer(),meshBuffer=gl.createBuffer(),axesBuffer=gl.createBuffer();
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  const status=figure.querySelector('.soliton-status'),help=figure.querySelector('.soliton-help');
  let data=initial,indices,meshIndices,axisPoints,verticalRadius,scheduled=false,dragging=null,loadId=0;
  const cache=new Map([[initial.genus,initial]]);
  const defaults=()=>({yaw:initial.view.yaw,pitch:initial.view.pitch,zoom:1,cutaway:false,axes:false,wire:false});
  let state=defaults();
  const badge=document.createElement('p');badge.className='bns-view-label iw-view-label';stage.append(badge);
  function upload(){
    if(data.vertices.length>65535)throw new Error('Illustration exceeds index limit');
    const {yaw,pitch}=data.view;
    verticalRadius=Math.max(...data.vertices.map(([x,y,z])=>Math.abs(z*Math.cos(pitch)-(x*Math.sin(yaw)+y*Math.cos(yaw))*Math.sin(pitch))));
    gl.bindBuffer(gl.ARRAY_BUFFER,vertexBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(data.vertices.flat()),gl.STATIC_DRAW);
    gl.bindBuffer(gl.ARRAY_BUFFER,normalBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(data.normals.flat()),gl.STATIC_DRAW);
    indices=new Uint16Array(data.faces.flat());
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,indices,gl.STATIC_DRAW);
    meshIndices=new Uint16Array(data.faces.flatMap(([a,b,c])=>[a,b,b,c,c,a]));
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,meshBuffer);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,meshIndices,gl.STATIC_DRAW);
    axisPoints=new Float32Array(data.equator.flat(2));
    gl.bindBuffer(gl.ARRAY_BUFFER,axesBuffer);gl.bufferData(gl.ARRAY_BUFFER,axisPoints,gl.STATIC_DRAW);
  }
  function bindVertices(){
    gl.bindBuffer(gl.ARRAY_BUFFER,vertexBuffer);gl.enableVertexAttribArray(positions);gl.vertexAttribPointer(positions,3,gl.FLOAT,false,0,0);
    gl.bindBuffer(gl.ARRAY_BUFFER,normalBuffer);gl.enableVertexAttribArray(normals);gl.vertexAttribPointer(normals,3,gl.FLOAT,false,0,0);
  }
  function draw(){
    scheduled=false;
    const box=stage.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2),w=Math.round(box.width*dpr),h=Math.round(box.height*dpr);
    if(!w||!h)return;
    if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}
    gl.viewport(0,0,w,h);gl.clearColor(247/255,250/255,251/255,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    const cy=Math.cos(state.yaw),sy=Math.sin(state.yaw),cp=Math.cos(state.pitch),sp=Math.sin(state.pitch);
    // Column-major rotation, matching the shared viewer's camera convention.
    gl.uniformMatrix3fv(loc.rotation,false,new Float32Array([cy,-sy*sp,sy*cp,-sy,-cy*sp,cy*cp,0,cp,sp]));
    const currentHeight=Math.max(...data.vertices.map(([x,y,z])=>Math.abs(z*cp-(x*sy+y*cy)*sp)));
    const s=Math.min(w*.46/data.view.radius,h*.40/Math.max(verticalRadius,currentHeight))*state.zoom;
    gl.uniform2f(loc.scale,2*s/w,2*s/h);gl.uniform1i(loc.cutaway,state.cutaway);gl.uniform1i(loc.lines,false);gl.uniform1i(loc.equator,false);
    gl.enable(gl.DEPTH_TEST);gl.frontFace(gl.CW);gl.disable(gl.CULL_FACE);gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
    bindVertices();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);gl.drawElements(gl.TRIANGLES,indices.length,gl.UNSIGNED_SHORT,0);
    gl.disable(gl.POLYGON_OFFSET_FILL);gl.uniform1i(loc.lines,true);
    if(state.wire){gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,meshBuffer);gl.drawElements(gl.LINES,meshIndices.length,gl.UNSIGNED_SHORT,0);}
    // Overlay includes hidden neck curves, as stated in the visible help.
    if(state.axes){
      gl.disable(gl.DEPTH_TEST);gl.uniform1i(loc.equator,true);
      gl.bindBuffer(gl.ARRAY_BUFFER,axesBuffer);gl.vertexAttribPointer(positions,3,gl.FLOAT,false,0,0);
      gl.disableVertexAttribArray(normals);gl.vertexAttrib3f(normals,0,0,1);gl.drawArrays(gl.LINES,0,axisPoints.length/3);
    }
    canvas.dataset.genus=String(data.genus);canvas.dataset.view=state.cutaway?'cutaway':'surface';
    canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;canvas.dataset.zoom=state.zoom.toFixed(3);
    canvas.dataset.equator=String(state.axes);canvas.dataset.mesh=String(state.wire);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  const label=document.createElement('label');label.textContent='Illustrated genus ';
  const select=document.createElement('select');select.setAttribute('aria-label','Illustrated genus');
  for(const g of IW_GENERA){const option=document.createElement('option');option.value=String(g);option.textContent=String(g);select.append(option);}
  select.value=String(initial.genus);label.append(select);controls.prepend(label);
  const cutButton=document.createElement('button');cutButton.type='button';cutButton.textContent='Cutaway';cutButton.dataset.iwAction='cutaway';
  const axesButton=document.createElement('button');axesButton.type='button';axesButton.textContent='Equator z = 0';axesButton.dataset.iwAction='axes';
  controls.append(cutButton,axesButton);
  for(const [name,pitch] of [['Top view',Math.PI/2],['Side view',0]]){
    const button=document.createElement('button');button.type='button';button.textContent=name;
    button.addEventListener('click',()=>{state.yaw=0;state.pitch=pitch;state.cutaway=false;sync();});
    controls.append(button);
  }
  function sync(){
    select.value=String(data.genus);
    cutButton.setAttribute('aria-pressed',String(state.cutaway));axesButton.setAttribute('aria-pressed',String(state.axes));
    figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed',String(state.wire));
    badge.textContent=`Genus h = ${data.genus} · ${data.genus+1} necks · 2 ends · ${state.cutaway?'cutaway schematic':'schematic'}`;
    canvas.setAttribute('aria-label',`Genus ${data.genus} Ilmanen–White two-ended topology schematic, ${state.cutaway?'front half removed':'full surface'}. Not a computed shrinker. Arrow keys rotate; plus and minus zoom.`);
    help.textContent=state.axes?'Orange curves mark the equatorial necks (z = 0), including hidden portions. Top view shows their arrangement. Drag to rotate; + / − zoom.':'Drag to rotate; + / − zoom. Cutaway exposes the neck walls. Blue and gold distinguish opposite sides of one surface. Outer rims are display truncations.';
    status.textContent=`Theorem: genus h = ${data.genus}, ${data.genus+1} equatorial curves and two conical ends (wheel parameter g = ${data.genus+1}). Drawing: illustrative neck shapes and cone slopes; no shrinker equation has been solved.`;
    requestDraw();
  }
  select.addEventListener('change',async()=>{
    const g=Number(select.value),id=++loadId;status.textContent=`Loading genus ${g}…`;
    try{
      if(!cache.has(g)){const response=await fetch(iwModelUrl(figure.dataset.soliton,g));if(!response.ok)throw new Error('mesh unavailable');cache.set(g,await response.json());}
      if(id!==loadId)return;
      data=cache.get(g);upload();sync();
    }catch{if(id===loadId){select.value=String(data.genus);status.textContent=`Genus ${g} could not load; genus ${data.genus} remains displayed.`;}}
  });
  cutButton.addEventListener('click',()=>{state.cutaway=!state.cutaway;if(state.cutaway){state.yaw=Math.PI/4;state.pitch=.38;}sync();});
  axesButton.addEventListener('click',()=>{state.axes=!state.axes;sync();});
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
    e.preventDefault();canvas.hidden=true;badge.hidden=true;figure.querySelector('img').hidden=false;controls.hidden=true;
    status.textContent='The graphics context was lost; the static drawing is shown. Reload to restore interaction.';
  });
  upload();sync();controls.hidden=false;help.hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;
  new ResizeObserver(requestDraw).observe(stage);
}
