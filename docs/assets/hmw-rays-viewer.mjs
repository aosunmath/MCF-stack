// Section 4 topology models, not numerical self-shrinkers.
export const HMW_CASES=Object.freeze({
  tetrahedron:'Tetrahedron · genus 3',cube:'Cube · genus 5',octahedron:'Octahedron · genus 7',
  dodecahedron:'Dodecahedron · genus 11',icosahedron:'Icosahedron · genus 19',
  'polygon-3':'Triangle · genus 2','polygon-5':'Pentagon · genus 4',
  'polygon-7':'Heptagon · genus 6','polygon-12':'12-gon · genus 11'
});
export function hmwModelUrl(base,key){
  if(!Object.hasOwn(HMW_CASES,key))throw new Error('Unsupported symmetry');
  return base.replace(/hmw-platonic-polygon\.json$/,`hmw-platonic-polygon${key==='cube'?'':'-'+key}.json`);
}

export function initHMWFigure(figure,initial){
  const canvas=figure.querySelector('canvas'),gl=canvas.getContext('webgl',{antialias:true,alpha:false});
  if(!gl)throw new Error('WebGL unavailable');
  const vertex=`attribute vec3 position, normal, color;
    uniform mat3 rotation; uniform vec2 scale;
    varying vec3 world, norm, tint;
    void main(){world=position;norm=rotation*normal;tint=color;
      vec3 p=rotation*position;gl_Position=vec4(p.x*scale.x,p.y*scale.y,-p.z/12.0,1.0);}`;
  const fragment=`precision mediump float;
    varying vec3 world, norm, tint;
    uniform bool cutaway, lines, rays;
    void main(){if(rays){gl_FragColor=vec4(.73,.20,.18,1.0);return;}
      if(cutaway && world.y>0.0)discard;
      if(lines){gl_FragColor=vec4(.12,.25,.30,1.0);return;}
      vec3 n=normalize(norm);if(!gl_FrontFacing)n=-n;
      float light=.48+.50*max(0.0,dot(n,normalize(vec3(-.35,.55,.80))));
      float shine=pow(max(0.0,dot(n,normalize(vec3(-.18,.28,1.0)))),40.0);
      gl_FragColor=vec4(tint*light+vec3(.12)*shine,1.0);}`;
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Shader compilation failed');return s;}
  const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));
  gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Shader link failed');gl.useProgram(program);
  const uniforms=Object.fromEntries(['rotation','scale','cutaway','lines','rays'].map(k=>[k,gl.getUniformLocation(program,k)]));
  const buffers=Object.fromEntries(['position','normal','color'].map(k=>[k,{buffer:gl.createBuffer(),location:gl.getAttribLocation(program,k)}]));
  const indexBuffer=gl.createBuffer(),meshBuffer=gl.createBuffer(),rayBuffer=gl.createBuffer();
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  const status=figure.querySelector('.soliton-status'),help=figure.querySelector('.soliton-help');
  let data=initial,indices,meshIndices,rayIndices,scheduled=false,dragging=null,loadId=0;
  const cache=new Map([[initial.case,initial]]);
  const defaults=()=>({yaw:initial.view.yaw,pitch:initial.view.pitch,zoom:1,cutaway:false,wire:false,rays:false});
  let state=defaults();
  const badge=document.createElement('p');badge.className='hmw-rays-view-label';stage.append(badge);
  function upload(){
    if(data.vertices.length+data.rayCount+1>65535)throw new Error('Illustration exceeds index limit');
    const vertices=[...data.vertices,[0,0,0],...data.rays.map(p=>p.map(v=>v*3.05))];
    const arrays={position:vertices,normal:[...data.normals,...Array(data.rayCount+1).fill([0,0,1])],
      color:[...data.vertexGroups.map(g=>data.palette[g].map(v=>v/255)),...Array(data.rayCount+1).fill([.73,.20,.18])]};
    for(const [name,values] of Object.entries(arrays)){
      const {buffer,location}=buffers[name];gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
      gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(values.flat()),gl.STATIC_DRAW);
      gl.enableVertexAttribArray(location);gl.vertexAttribPointer(location,3,gl.FLOAT,false,0,0);
    }
    indices=new Uint16Array(data.faces.flat());gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,indices,gl.STATIC_DRAW);
    meshIndices=new Uint16Array(data.faces.flatMap(([a,b,c])=>[a,b,b,c,c,a]));
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,meshBuffer);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,meshIndices,gl.STATIC_DRAW);
    const origin=data.vertices.length;
    rayIndices=new Uint16Array(data.rays.flatMap((_,i)=>[origin,origin+i+1]));
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,rayBuffer);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,rayIndices,gl.STATIC_DRAW);
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
    gl.uniform2f(uniforms.scale,2*scale/w,2*scale/h);gl.uniform1i(uniforms.cutaway,state.cutaway);gl.uniform1i(uniforms.lines,false);gl.uniform1i(uniforms.rays,false);
    gl.enable(gl.DEPTH_TEST);gl.frontFace(gl.CW);gl.disable(gl.CULL_FACE);gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);gl.drawElements(gl.TRIANGLES,indices.length,gl.UNSIGNED_SHORT,0);
    gl.disable(gl.POLYGON_OFFSET_FILL);
    if(state.wire){gl.uniform1i(uniforms.lines,true);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,meshBuffer);gl.drawElements(gl.LINES,meshIndices.length,gl.UNSIGNED_SHORT,0);}
    if(state.rays){gl.uniform1i(uniforms.rays,true);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,rayBuffer);gl.drawElements(gl.LINES,rayIndices.length,gl.UNSIGNED_SHORT,0);}
    canvas.dataset.case=data.case;canvas.dataset.rays=String(state.rays);canvas.dataset.genus=String(data.genus);canvas.dataset.view=state.cutaway?'cutaway':'surface';
    canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;
    canvas.dataset.zoom=state.zoom.toFixed(3);canvas.dataset.mesh=String(state.wire);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  const label=document.createElement('label');label.textContent='Symmetry ';
  const select=document.createElement('select');select.setAttribute('aria-label','Symmetry');
  for(const [key,title] of Object.entries(HMW_CASES)){const option=document.createElement('option');option.value=key;option.textContent=title;select.append(option);}
  label.append(select);controls.prepend(label);
  const cutButton=document.createElement('button');cutButton.type='button';cutButton.textContent='Cutaway';controls.append(cutButton);
  const rayButton=document.createElement('button');rayButton.type='button';rayButton.textContent='Show rays Q';controls.append(rayButton);
  const legend=document.createElement('p');legend.className='hmw-rays-legend';
  for(const [name,color] of [['Outer wall','#488ba0'],['Inner wall','#d5a969'],['Passage walls','#aa734a'],['Excluded rays Q','#ba332e']]){
    const item=document.createElement('span'),dot=document.createElement('i');dot.style.background=color;dot.setAttribute('aria-hidden','true');item.append(dot,name);legend.append(item);
  }
  controls.after(legend);
  function sync(){
    select.value=data.case;
    cutButton.setAttribute('aria-pressed',String(state.cutaway));rayButton.setAttribute('aria-pressed',String(state.rays));
    figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed',String(state.wire));
    badge.textContent=`Construction schematic · ${data.rayCount} openings · genus ${data.genus}`;
    canvas.setAttribute('aria-label',`${HMW_CASES[data.case]} construction schematic: ${data.rayCount} radial passages, genus ${data.genus}; ${state.cutaway?'front half removed':'full surface'}. Not a computed self-shrinker. Arrow keys rotate; plus and minus zoom.`);
    help.textContent='Drag to rotate; + / − zoom. Show rays Q traces the excluded rays through the openings. Cutaway reveals the cavity and inner wall; its cut edges are only part of the display.';
    status.textContent=`${HMW_CASES[data.case]}: q = ${data.rayCount}, genus q − 1 = ${data.genus}. This compact model illustrates the construction input, not a solved shrinker. Theorem 12 leaves compactness unresolved in general; sufficiently large polygonal shrinkers are noncompact.`;
    requestDraw();
  }
  select.addEventListener('change',async()=>{
    const key=select.value,id=++loadId;status.textContent=`Loading ${HMW_CASES[key]}…`;
    try{
      if(!cache.has(key)){const response=await fetch(hmwModelUrl(figure.dataset.soliton,key));if(!response.ok)throw new Error('mesh unavailable');cache.set(key,await response.json());}
      if(id!==loadId)return;
      const previous=data;data=cache.get(key);
      try{upload();}catch(error){data=previous;upload();throw error;}
      sync();
    }catch{if(id===loadId){select.value=data.case;status.textContent=`${HMW_CASES[key]} could not load; ${HMW_CASES[data.case]} remains displayed.`;}}
  });
  cutButton.addEventListener('click',()=>{state.cutaway=!state.cutaway;sync();});
  rayButton.addEventListener('click',()=>{state.rays=!state.rays;sync();});
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
