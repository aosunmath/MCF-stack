// Sun–Wang auxiliary end: the translator correction is deliberately not modeled.
export function torusEndMesh(profile, mode='end', height=4, rows=48, sectors=48) {
  if(!['end','slice','normalized'].includes(mode)||!(height>=1&&height<=9))throw new Error('Invalid end view');
  const vertices=[], faces=[], levels=[], n=profile.length;
  const count=mode==='slice'?sectors:rows;
  for(let j=0;j<(mode==='slice'?sectors:rows+1);j++){
    const h=1+8*j/rows, t=2*Math.PI*j/sectors;
    for(const [r,q] of profile){
      const a=Math.sqrt(mode==='slice'?height:h),s=mode==='normalized'?1:a;
      vertices.push(mode==='slice'?[a*r*Math.cos(t),a*r*Math.sin(t),a*q]:[s*r,s*q,h]);
      levels.push(mode==='slice'?height:h);
    }
  }
  for(let j=0;j<count;j++)for(let i=0;i<n;i++){
    const jj=mode==='slice'?(j+1)%sectors:j+1;
    const a=j*n+i,b=j*n+(i+1)%n,c=jj*n+(i+1)%n,d=jj*n+i;
    faces.push([a,b,c],[a,c,d]);
  }
  return {vertices,faces,levels};
}

export function endNormals(vertices,faces) {
  const normals=vertices.map(()=>[0,0,0]);
  for(const [a,b,c] of faces){
    const u=vertices[b].map((v,k)=>v-vertices[a][k]),v=vertices[c].map((p,k)=>p-vertices[a][k]);
    const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
    for(const i of [a,b,c])for(let k=0;k<3;k++)normals[i][k]+=n[k];
  }
  return normals.map(n=>{const length=Math.hypot(...n)||1;return n.map(p=>p/length);});
}

export function initTorusEndFigure(figure,data) {
  const canvas=figure.querySelector('canvas'),gl=canvas.getContext('webgl',{antialias:true,alpha:false});
  if(!gl)throw new Error('WebGL unavailable');
  const vs=`attribute vec3 position, normal; attribute float level;
    uniform mat3 rotation; uniform vec2 scale; uniform vec3 center;
    varying vec3 norm; varying float h;
    void main(){norm=rotation*normal;h=level;vec3 p=rotation*(position-center);
      gl_Position=vec4(p.x*scale.x,p.y*scale.y,-p.z/40.0,1.0);}`;
  const fs=`precision mediump float; varying vec3 norm; varying float h;
    uniform float selected; uniform bool slice, lines;
    void main(){if(lines){gl_FragColor=vec4(.12,.30,.36,1.0);return;}
      vec3 n=normalize(norm);if(!gl_FrontFacing)n=-n;
      float light=.54+.45*max(0.0,dot(n,normalize(vec3(-.3,.6,1.0))));
      vec3 tint=mix(vec3(.17,.43,.54),vec3(.36,.68,.73),(h-1.0)/8.0);
      if(slice||abs(h-selected)<.045)tint=vec3(.83,.51,.25);
      float shine=pow(max(0.0,dot(n,normalize(vec3(-.2,.35,1.0)))),32.0);
      gl_FragColor=vec4(tint*light+vec3(.12)*shine,1.0);}`;
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Shader failed');return s;}
  const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vs));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fs));gl.linkProgram(program);
  if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Shader link failed');gl.useProgram(program);
  const uniforms=Object.fromEntries(['rotation','scale','center','selected','slice','lines'].map(k=>[k,gl.getUniformLocation(program,k)]));
  const attributes=Object.fromEntries(['position','normal','level'].map(k=>[k,{buffer:gl.createBuffer(),location:gl.getAttribLocation(program,k)}]));
  const index=gl.createBuffer(),wireIndex=gl.createBuffer();let count=0,wireCount=0,scheduled=false,drag=null;
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls'),status=figure.querySelector('.soliton-status');
  const defaults=()=>({mode:'end',height:4,yaw:.38,pitch:.28,zoom:1,wire:false});let state=defaults();
  const badge=document.createElement('p');badge.className='torus-end-label';stage.append(badge);
  const axes=document.createElement('p');axes.className='torus-end-axes';stage.append(axes);
  const viewLabel=document.createElement('label');viewLabel.textContent='View ';
  const view=document.createElement('select');view.setAttribute('aria-label','Torus end view');
  for(const [v,label] of [['end','End: rotational quotient'],['slice','Horizontal torus slice'],['normalized','Rescaled end: x / √z']]){const o=document.createElement('option');o.value=v;o.textContent=label;view.append(o);}
  viewLabel.append(view);controls.prepend(viewLabel);
  const label=document.createElement('label'),output=document.createElement('output'),slider=document.createElement('input');
  slider.type='range';slider.min='1';slider.max='9';slider.step='.1';slider.value='4';slider.setAttribute('aria-label','Relative height z divided by z0');
  label.append(output,slider);controls.append(label);
  function upload(){
    const mesh=torusEndMesh(data.profile,state.mode,state.height);
    for(const [name,array] of Object.entries({position:mesh.vertices.flat(),normal:endNormals(mesh.vertices,mesh.faces).flat(),level:mesh.levels})){
      const a=attributes[name];gl.bindBuffer(gl.ARRAY_BUFFER,a.buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(array),gl.DYNAMIC_DRAW);gl.enableVertexAttribArray(a.location);gl.vertexAttribPointer(a.location,name==='level'?1:3,gl.FLOAT,false,0,0);
    }
    const indices=new Uint16Array(mesh.faces.flat());count=indices.length;gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,index);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,indices,gl.DYNAMIC_DRAW);
    const wires=new Uint16Array(mesh.faces.flatMap(([a,b,c])=>[a,b,b,c,c,a]));wireCount=wires.length;gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,wireIndex);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,wires,gl.DYNAMIC_DRAW);
  }
  function draw(){
    scheduled=false;const box=stage.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2),w=Math.round(box.width*dpr),h=Math.round(box.height*dpr);
    if(!w||!h)return;if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}
    gl.viewport(0,0,w,h);gl.clearColor(247/255,250/255,251/255,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    const cy=Math.cos(state.yaw),sy=Math.sin(state.yaw),cp=Math.cos(state.pitch),sp=Math.sin(state.pitch);
    gl.uniformMatrix3fv(uniforms.rotation,false,new Float32Array([cy,-sy*sp,sy*cp,-sy,-cy*sp,cy*cp,0,cp,sp]));
    const isSlice=state.mode==='slice',normalized=state.mode==='normalized';
    const radius=isSlice?10:normalized?4.8:6.2;
    const scale=Math.min(w*.43/radius,h*.36/(isSlice?5.7:5.0))*state.zoom;
    gl.uniform2f(uniforms.scale,2*scale/w,2*scale/h);gl.uniform3fv(uniforms.center,isSlice?[0,0,0]:normalized?[1.875,0,5]:[5.1,0,5]);
    gl.uniform1f(uniforms.selected,state.height);gl.uniform1i(uniforms.slice,isSlice);gl.uniform1i(uniforms.lines,false);
    gl.enable(gl.DEPTH_TEST);gl.frontFace(gl.CW);gl.disable(gl.CULL_FACE);gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,index);gl.drawElements(gl.TRIANGLES,count,gl.UNSIGNED_SHORT,0);gl.disable(gl.POLYGON_OFFSET_FILL);
    if(state.wire){gl.uniform1i(uniforms.lines,true);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,wireIndex);gl.drawElements(gl.LINES,wireCount,gl.UNSIGNED_SHORT,0);}
    canvas.dataset.view=state.mode;canvas.dataset.height=String(state.height);canvas.dataset.zoom=state.zoom.toFixed(3);canvas.dataset.mesh=String(state.wire);canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function sync(){
    view.value=state.mode;slider.value=String(state.height);output.textContent=`h = z/z₀: ${state.height.toFixed(1)}`;
    badge.textContent=state.mode==='slice'?`Numerical Angenent slice · scale √h = ${Math.sqrt(state.height).toFixed(2)}`:state.mode==='normalized'?'Rescaled auxiliary end · constant meridian':'One auxiliary end · copper marks the selected height';
    axes.textContent=state.mode==='slice'?'Coordinates (x₁, x₂, x₃) / √z₀ · fixed viewing scale':state.mode==='normalized'?'Coordinates (r/√z, x₃/√z, h) · 1 ≤ h ≤ 9':'Coordinates (r/√z₀, x₃/√z₀, h) · 1 ≤ h ≤ 9';
    status.textContent=state.mode==='slice'?'A two-dimensional torus in the horizontal ℝ³ slice. The height slider changes z along one auxiliary end; it is not flow time.':state.mode==='normalized'?'Dividing all three horizontal coordinates by √z makes the u = 0 model cylindrical. For the actual translator, the unknown correction tends to zero.':'Each point of this quotient represents a rotation circle in (x₁,x₂). Restoring that angle gives the three-dimensional end in ℝ⁴. Both open rims are display cuts.';
    figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed',String(state.wire));
    canvas.setAttribute('aria-label',`${badge.textContent}. ${axes.textContent}. Auxiliary model with u equals zero, not a computed translator. Arrow keys rotate; plus and minus zoom.`);
    requestDraw();
  }
  view.addEventListener('change',()=>{state.mode=view.value;state.yaw=.38;state.pitch=state.mode==='slice'?.79:.28;state.zoom=1;upload();sync();});
  slider.addEventListener('input',()=>{state.height=Number(slider.value);if(state.mode==='slice')upload();sync();});
  function zoom(factor){state.zoom=Math.max(.5,Math.min(3,state.zoom*factor));requestDraw();}
  for(const b of figure.querySelectorAll('[data-view-action]'))b.addEventListener('click',()=>{
    const a=b.dataset.viewAction;if(a==='in')zoom(1.2);if(a==='out')zoom(1/1.2);if(a==='wire'){state.wire=!state.wire;sync();}
    if(a==='reset'){state=defaults();drag=null;upload();sync();}
  });
  canvas.addEventListener('pointerdown',e=>{drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;state.yaw+=(e.clientX-drag[0])*.009;state.pitch=Math.max(-1.45,Math.min(1.45,state.pitch+(e.clientY-drag[1])*.009));drag=[e.clientX,e.clientY];requestDraw();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>{drag=null;});
  canvas.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-'].includes(e.key))return;e.preventDefault();
    if(e.key==='ArrowLeft')state.yaw-=.12;if(e.key==='ArrowRight')state.yaw+=.12;if(e.key==='ArrowUp')state.pitch+=.12;if(e.key==='ArrowDown')state.pitch-=.12;
    state.pitch=Math.max(-1.45,Math.min(1.45,state.pitch));if(e.key==='+'||e.key==='=')zoom(1.2);if(e.key==='-')zoom(1/1.2);requestDraw();});
  figure.querySelector('.soliton-help').textContent='Drag to rotate; use the zoom buttons or arrow keys and + / −. Compare the quotient, torus slice, and rescaled end. The model sets u = 0; the compact core is omitted.';
  upload();sync();controls.hidden=false;figure.querySelector('.soliton-help').hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;
  new ResizeObserver(requestDraw).observe(stage);
}
