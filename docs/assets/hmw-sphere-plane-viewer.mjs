// HMW Figures 1, 5–6: original topology schematic, not a solved shrinker.
export const HMW_GENERA = [3, 5, 11];
export function hmwModelUrl(base, genus) {
  if (genus!=='limit' && !HMW_GENERA.includes(genus)) throw new Error('Unsupported illustration genus');
  return base.replace(/hmw-one-ended\.json$/, genus==='limit'?'hmw-sphere-plane-limit.json':`hmw-one-ended${genus===5?'':`-${genus}`}.json`);
}
export function hmwAxes(genus, radius=3.8) {
  return Array.from({length:genus+1},(_,j)=>{
    const t=Math.PI*j/(genus+1),x=radius*Math.cos(t),y=radius*Math.sin(t);
    return [[-x,-y,0],[x,y,0]];
  });
}

export function initHmwFigure(figure, initial) {
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
    uniform bool cutaway, lines;
    void main(){if(cutaway && world.y>0.0001)discard;
      if(lines){gl_FragColor=vec4(.12,.25,.30,1.0);return;}
      vec3 n=normalize(norm); bool front=gl_FrontFacing;
      if(!front)n=-n;
      vec3 color=front?vec3(.86,.66,.31):vec3(.30,.53,.64);
      float light=.50+.48*max(0.0,dot(n,normalize(vec3(-.35,.55,.80))));
      float shine=pow(max(0.0,dot(n,normalize(vec3(-.18,.28,1.0)))),36.0);
      gl_FragColor=vec4(color*light+vec3(.17)*shine,1.0);}`;
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Shader compilation failed');return s;}
  const program=gl.createProgram();
  gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));
  gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Shader link failed');gl.useProgram(program);
  const loc=Object.fromEntries(['rotation','scale','cutaway','lines'].map(k=>[k,gl.getUniformLocation(program,k)]));
  const positions=gl.getAttribLocation(program,'position'),normals=gl.getAttribLocation(program,'normal');
  const vertexBuffer=gl.createBuffer(),normalBuffer=gl.createBuffer(),indexBuffer=gl.createBuffer(),meshBuffer=gl.createBuffer(),axesBuffer=gl.createBuffer();
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  const status=figure.querySelector('.soliton-status'),help=figure.querySelector('.soliton-help');
  let data=initial,indices,meshIndices,axisPoints,scheduled=false,dragging=null,loadId=0;
  const cache=new Map([[initial.genus,initial]]);
  const defaults=()=>({yaw:initial.view.yaw,pitch:initial.view.pitch,zoom:1,mode:'surface',genus:initial.genus,axes:false,wire:false});
  let state=defaults();
  const badge=document.createElement('p');badge.className='hmw-view-label';stage.append(badge);
  function upload(){
    if(data.vertices.length>65535)throw new Error('Illustration exceeds index limit');
    gl.bindBuffer(gl.ARRAY_BUFFER,vertexBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(data.vertices.flat()),gl.STATIC_DRAW);
    gl.bindBuffer(gl.ARRAY_BUFFER,normalBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(data.normals.flat()),gl.STATIC_DRAW);
    indices=new Uint16Array(data.faces.flat());
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,indices,gl.STATIC_DRAW);
    meshIndices=new Uint16Array(data.faces.flatMap(([a,b,c])=>[a,b,b,c,c,a]));
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,meshBuffer);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,meshIndices,gl.STATIC_DRAW);
    axisPoints=new Float32Array(hmwAxes(state.genus).flat(2));
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
    const s=Math.min(w*.46/data.view.radius,h*.40/(state.mode==='trace'?4:2.5))*state.zoom;
    gl.uniform2f(loc.scale,2*s/w,2*s/h);gl.uniform1i(loc.cutaway,state.mode==='cutaway');gl.uniform1i(loc.lines,false);
    gl.enable(gl.DEPTH_TEST);gl.frontFace(gl.CW);gl.disable(gl.CULL_FACE);gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
    bindVertices();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);if(state.mode!=='trace')gl.drawElements(gl.TRIANGLES,indices.length,gl.UNSIGNED_SHORT,0);
    gl.disable(gl.POLYGON_OFFSET_FILL);gl.uniform1i(loc.lines,true);
    if(state.wire&&state.mode!=='trace'){gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,meshBuffer);gl.drawElements(gl.LINES,meshIndices.length,gl.UNSIGNED_SHORT,0);}
    if((state.axes||state.mode==='trace')&&state.mode!=='limit'){
      gl.bindBuffer(gl.ARRAY_BUFFER,axesBuffer);gl.vertexAttribPointer(positions,3,gl.FLOAT,false,0,0);
      gl.disableVertexAttribArray(normals);gl.vertexAttrib3f(normals,0,0,1);gl.drawArrays(gl.LINES,0,axisPoints.length/3);
    }
    canvas.dataset.genus=String(state.genus);canvas.dataset.view=state.mode;
    canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;canvas.dataset.zoom=state.zoom.toFixed(3);
    canvas.dataset.axes=String(state.axes);canvas.dataset.mesh=String(state.wire);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  const label=document.createElement('label');label.textContent='Model genus ';
  const select=document.createElement('select');select.setAttribute('aria-label','Model genus');
  for(const g of HMW_GENERA){const option=document.createElement('option');option.value=String(g);option.textContent=String(g);select.append(option);}
  label.append(select);controls.prepend(label);
  const viewLabel=document.createElement('label');viewLabel.textContent='View ';
  const view=document.createElement('select');view.setAttribute('aria-label','HMW geometry view');
  for(const [value,title] of [['surface','Full surface'],['cutaway','Cutaway'],['trace','Horizontal trace'],['limit','Sphere–plane limit']]){
    const option=document.createElement('option');option.value=value;option.textContent=title;view.append(option);
  }
  viewLabel.append(view);controls.prepend(viewLabel);
  const axesButton=document.createElement('button');axesButton.type='button';axesButton.textContent='Show horizontal lines';
  controls.append(axesButton);
  const meshButton=figure.querySelector('[data-view-action="wire"]');
  function sync(){
    const trace=state.mode==='trace',limit=state.mode==='limit';
    select.value=String(state.genus);select.disabled=limit;view.value=state.mode;
    axesButton.disabled=trace||limit;axesButton.setAttribute('aria-pressed',String(state.axes||trace));
    meshButton.disabled=trace;meshButton.setAttribute('aria-pressed',String(state.wire));
    badge.textContent=limit?'Large-genus limit · plane ∪ sphere of radius 2':trace?`Horizontal trace Qg · ${state.genus+1} lines`:`Genus ${state.genus} model · ${state.mode==='cutaway'?'cutaway':'full surface'} · schematic`;
    canvas.setAttribute('aria-label',limit?'Limiting radius-two sphere and horizontal plane. The circle where they intersect is singular. Arrow keys rotate; plus and minus zoom.':trace?`The ${state.genus+1} horizontal lines in the shrinker. This view shows the trace, not the surface. Arrow keys rotate; plus and minus zoom.`:`Hoffman–Martín–White genus ${state.genus} topology schematic, ${state.mode==='cutaway'?'front half removed':'full surface'}. Not a computed shrinker. Arrow keys rotate; plus and minus zoom.`);
    help.textContent=trace?'The lines have angles jπ/(g+1). They lie in the surface; they are not separate sheets or singular junctions.':limit?'Drag to rotate; + / − zoom. This intersecting configuration is the limit as genus tends to infinity.':'Drag to rotate; + / − zoom. Cutaway exposes the central sheet and lower cap. Gold and blue distinguish the two sides of one surface.';
    status.textContent=limit?'Theorem 42: for fixed admissible δ, convergence is smooth with multiplicity one away from the equatorial circle. This is a separate limiting configuration, not a finite-genus shrinker.':trace?'Section 5 and Theorem 40: Σg ∩ {z = 0} = Qg. The trace is exact mathematical data; its displayed radius is arbitrary.':`Schematic with model genus ${state.genus} and one exterior sheet. HMW prove existence for every g ≥ 1, but exactly one end only for sufficiently large g; no effective threshold is supplied. Shape and cone slope are illustrative. Outer and cut edges are artificial.`;
    requestDraw();
  }
  async function change(mode,genus){
    const id=++loadId,key=mode==='limit'?'limit':genus;
    status.textContent='Loading the geometry view…';
    try{
      if(!cache.has(key)){
        const response=await fetch(hmwModelUrl(figure.dataset.soliton,key));
        if(!response.ok)throw new Error('mesh unavailable');
        const next=await response.json();
        if(key==='limit'?next.kind!=='hmw-limit':next.genus!==key)throw new Error('Wrong model');
        cache.set(key,next);
      }
      if(id!==loadId)return;
      const previous=data,previousGenus=state.genus;data=cache.get(key);state.genus=genus;
      try{upload();}catch(error){data=previous;state.genus=previousGenus;upload();throw error;}
      if(mode==='trace'){state.yaw=0;state.pitch=Math.PI/2;state.zoom=1;}
      else if(state.mode==='trace'){state.yaw=initial.view.yaw;state.pitch=initial.view.pitch;state.zoom=1;}
      if(mode==='cutaway'&&state.mode==='surface')state.pitch=.43;
      state.mode=mode;sync();
    }catch{if(id===loadId){select.value=String(state.genus);view.value=state.mode;status.textContent='This model could not load; the previous valid view remains displayed.';}}
  }
  select.addEventListener('change',()=>change(state.mode,Number(select.value)));
  view.addEventListener('change',()=>change(view.value,state.genus));
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
    e.preventDefault();canvas.hidden=true;badge.hidden=true;help.hidden=true;figure.querySelector('img').hidden=false;controls.hidden=true;
    status.textContent='The graphics context was lost; the static drawing is shown. Reload to restore interaction.';
  });
  upload();sync();controls.hidden=false;help.hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;
  new ResizeObserver(requestDraw).observe(stage);
}
