// Original construction schematic, not a numerical Kapouleas–McGrath shrinker.
export const SPHERICAL_COUNTS=[6,10,14];
export function sphericalModelUrl(base,m){
  if(!SPHERICAL_COUNTS.includes(m))throw new Error('Unsupported bridge count');
  return base.replace(/sphere-doubling-shrinker\.json$/,`sphere-doubling-shrinker${m===10?'':`-${m}`}.json`);
}

export function sphericalGap(vertices,factor){
  if(!(factor>=.6&&factor<=1.8))throw new Error('Unsupported display separation');
  return vertices.map(p=>{const r=Math.hypot(...p),scale=(2+factor*(r-2))/r;return p.map(v=>v*scale);});
}

export function sphericalNormals(vertices,faces){
  const normals=vertices.map(()=>[0,0,0]);
  for(const [a,b,c] of faces){
    const u=vertices[b].map((v,i)=>v-vertices[a][i]),v=vertices[c].map((w,i)=>w-vertices[a][i]);
    const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
    for(const j of [a,b,c])for(let k=0;k<3;k++)normals[j][k]+=n[k];
  }
  return normals.map(n=>{const r=Math.hypot(...n)||1;return n.map(v=>v/r);});
}

export function initSphericalDoublingFigure(figure,initial){
  const canvas=figure.querySelector('canvas'),gl=canvas.getContext('webgl',{antialias:true,alpha:false});
  if(!gl)throw new Error('WebGL unavailable');
  const vertex=`attribute vec3 position, normal, color;
    uniform mat3 rotation; uniform vec2 scale;
    varying vec3 world, norm, tint;
    void main(){world=position;norm=rotation*normal;tint=color;
      vec3 p=rotation*position;gl_Position=vec4(p.x*scale.x,p.y*scale.y,-p.z/12.0,1.0);}`;
  const fragment=`precision mediump float;
    varying vec3 world, norm, tint;
    uniform bool cutaway, lines;
    void main(){if(cutaway && world.y>0.0)discard;
      if(lines){gl_FragColor=vec4(.12,.25,.30,1.0);return;}
      vec3 n=normalize(norm);if(!gl_FrontFacing)n=-n;
      float light=.48+.50*max(0.0,dot(n,normalize(vec3(-.35,.55,.80))));
      float shine=pow(max(0.0,dot(n,normalize(vec3(-.18,.28,1.0)))),40.0);
      gl_FragColor=vec4(tint*light+vec3(.12)*shine,1.0);}`;
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Shader compilation failed');return s;}
  const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));
  gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Shader link failed');gl.useProgram(program);
  const uniforms=Object.fromEntries(['rotation','scale','cutaway','lines'].map(k=>[k,gl.getUniformLocation(program,k)]));
  const buffers=Object.fromEntries(['position','normal','color'].map(k=>[k,{buffer:gl.createBuffer(),location:gl.getAttribLocation(program,k)}]));
  const indexBuffer=gl.createBuffer(),meshBuffer=gl.createBuffer();
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  const status=figure.querySelector('.soliton-status'),help=figure.querySelector('.soliton-help');
  let data=initial,indices,meshIndices,scheduled=false,dragging=null,loadId=0;
  const cache=new Map([[initial.m,initial]]);
  const defaults=()=>({yaw:initial.view.yaw,pitch:initial.view.pitch,zoom:1,cutaway:false,wire:false,gap:1});
  let state=defaults();
  const badge=document.createElement('p');badge.className='spherical-view-label';stage.append(badge);
  function upload(){
    if(data.vertices.length>65535)throw new Error('Illustration exceeds index limit');
    const vertices=sphericalGap(data.vertices,state.gap);
    const arrays={position:vertices,normal:sphericalNormals(vertices,data.faces),
      color:data.vertexGroups.map(g=>data.palette[g].map(v=>v/255))};
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
    const scale=Math.min(w*.44,h*.43)/data.view.radius*state.zoom;
    gl.uniform2f(uniforms.scale,2*scale/w,2*scale/h);gl.uniform1i(uniforms.cutaway,state.cutaway);gl.uniform1i(uniforms.lines,false);
    gl.enable(gl.DEPTH_TEST);gl.frontFace(gl.CW);gl.disable(gl.CULL_FACE);gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);gl.drawElements(gl.TRIANGLES,indices.length,gl.UNSIGNED_SHORT,0);
    gl.disable(gl.POLYGON_OFFSET_FILL);
    if(state.wire){gl.uniform1i(uniforms.lines,true);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,meshBuffer);gl.drawElements(gl.LINES,meshIndices.length,gl.UNSIGNED_SHORT,0);}
    canvas.dataset.m=String(data.m);canvas.dataset.genus=String(data.genus);canvas.dataset.view=state.cutaway?'cutaway':'surface';
    canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;
    canvas.dataset.zoom=state.zoom.toFixed(3);canvas.dataset.gap=String(state.gap);canvas.dataset.mesh=String(state.wire);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  const label=document.createElement('label');label.textContent='Sites per latitude ';
  const select=document.createElement('select');select.setAttribute('aria-label','Sites per latitude');
  for(const m of SPHERICAL_COUNTS){const option=document.createElement('option');option.value=String(m);option.textContent=`m = ${m}`;select.append(option);}
  label.append(select);controls.prepend(label);
  const cutButton=document.createElement('button');cutButton.type='button';cutButton.textContent='Cutaway';controls.append(cutButton);
  const gapLabel=document.createElement('label');gapLabel.textContent='Display separation ';
  const gap=document.createElement('input');gap.type='range';gap.min='.6';gap.max='1.8';gap.step='.1';gap.value='1';gap.setAttribute('aria-label','Display separation');
  const output=document.createElement('output');gapLabel.append(gap,output);controls.append(gapLabel);
  const legend=document.createElement('p');legend.className='spherical-legend';
  for(const [name,color] of [['Outer sheet','#4b8ba3'],['Inner sheet','#d3a963'],['Connecting necks','#bc744d']]){
    const item=document.createElement('span'),dot=document.createElement('i');dot.style.background=color;dot.setAttribute('aria-hidden','true');item.append(dot,name);legend.append(item);
  }
  controls.after(legend);
  function sync(){
    select.value=String(data.m);gap.value=String(state.gap);output.textContent=`${state.gap.toFixed(1)}×`;
    cutButton.setAttribute('aria-pressed',String(state.cutaway));figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed',String(state.wire));
    badge.textContent=`${2*data.m} bridges · model genus ${data.genus} · ${state.cutaway?'cutaway':'full surface'}`;
    canvas.setAttribute('aria-label',`Spherical doubling construction schematic: ${2*data.m} radial bridges, model genus ${data.genus}; ${state.cutaway?'front half removed':'full surface'}. Not a computed self-shrinker. Arrow keys rotate; plus and minus zoom.`);
    help.textContent='Drag to rotate; + / − zoom. Cutaway exposes the inner sheet. Display separation enlarges the gap; it is an illustration control. Cut edges are not boundaries of the closed surface.';
    status.textContent=`Schematic: m = ${data.m} sites on each of two aligned latitude circles; genus 2m − 1 = ${data.genus}. The theorem requires sufficiently large m, with no effective threshold stated here. Neck sizes and sheet separation are illustrative.`;
    requestDraw();
  }
  select.addEventListener('change',async()=>{
    const m=Number(select.value),id=++loadId;status.textContent=`Loading m = ${m}…`;
    try{
      if(!cache.has(m)){const response=await fetch(sphericalModelUrl(figure.dataset.soliton,m));if(!response.ok)throw new Error('mesh unavailable');cache.set(m,await response.json());}
      if(id!==loadId)return;
      const previous=data;data=cache.get(m);
      try{upload();}catch(error){data=previous;upload();throw error;}
      sync();
    }catch{if(id===loadId){select.value=String(data.m);status.textContent=`m = ${m} could not load; m = ${data.m} remains displayed.`;}}
  });
  cutButton.addEventListener('click',()=>{state.cutaway=!state.cutaway;sync();});
  gap.addEventListener('input',()=>{state.gap=Number(gap.value);upload();sync();});
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
    e.preventDefault();canvas.hidden=true;badge.hidden=true;legend.hidden=true;figure.querySelector('img').hidden=false;controls.hidden=true;help.hidden=true;
    status.textContent='The graphics context was lost; the static drawing is shown. Reload to restore interaction.';
  });
  upload();sync();controls.hidden=false;help.hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;
  new ResizeObserver(requestDraw).observe(stage);
}
