// Genus-labelled level-set schematics. These meshes do not solve the shrinker PDE.
export function modelRotation(yaw,pitch) {
  const c=Math.cos(yaw),s=Math.sin(yaw),a=Math.cos(pitch),b=Math.sin(pitch);
  return [c,-s*b,s*a,-s,-c*b,c*a,0,a,b];
}

export function initMollerGenusFigure(figure,initial) {
  const canvas=figure.querySelector('canvas');
  const gl=canvas.getContext('webgl',{antialias:true,alpha:false});
  if(!gl)throw new Error('WebGL unavailable');
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Shader unavailable');return s;}
  const program=gl.createProgram();
  gl.attachShader(program,shader(gl.VERTEX_SHADER,`
    attribute vec3 position; attribute vec3 normal;
    uniform mat3 rotation; uniform vec2 scale;
    varying vec3 vNormal;
    void main(){vec3 p=rotation*position;vNormal=rotation*normal;gl_Position=vec4(p.x*scale.x,p.y*scale.y-.02,-p.z/10.0,1.0);}
  `));
  gl.attachShader(program,shader(gl.FRAGMENT_SHADER,`
    precision mediump float; varying vec3 vNormal; uniform bool wire;
    void main(){vec3 n=normalize(vNormal);if(n.z<0.0)n=-n;
      float light=.30+.70*max(dot(n,normalize(vec3(-.35,.6,.8))),0.0);
      vec3 color=wire?vec3(.12,.28,.32):vec3(.35,.65,.73)*light+vec3(.06);
      gl_FragColor=vec4(color,1.0);}
  `));
  gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Shader unavailable');
  gl.useProgram(program);gl.enable(gl.DEPTH_TEST);
  const vertexBuffer=gl.createBuffer(),normalBuffer=gl.createBuffer(),faceBuffer=gl.createBuffer(),edgeBuffer=gl.createBuffer();
  const rotation=gl.getUniformLocation(program,'rotation'),scale=gl.getUniformLocation(program,'scale'),wireUniform=gl.getUniformLocation(program,'wire');
  for(const [name,buffer] of [['position',vertexBuffer],['normal',normalBuffer]]){
    gl.bindBuffer(gl.ARRAY_BUFFER,buffer);const index=gl.getAttribLocation(program,name);gl.enableVertexAttribArray(index);gl.vertexAttribPointer(index,3,gl.FLOAT,false,0,0);
  }
  const defaults=()=>({yaw:initial.view.yaw,pitch:initial.view.pitch,zoom:1,wire:false});
  let state=defaults(),data=initial,faceCount=0,edgeCount=0,dragging=null,scheduled=false,request=0;
  const cache=new Map([[initial.genus,initial]]);
  const heading=document.createElement('div');heading.className='moller-genus-heading';
  Object.assign(heading.style,{position:'absolute',top:'12px',left:'14px',right:'10px',fontSize:'14px',color:'#183f52',pointerEvents:'none'});stage.append(heading);
  const label=document.createElement('label');label.textContent='Model genus ';
  const select=document.createElement('select');select.setAttribute('aria-label','Gluing model genus');select.style.minHeight='36px';
  for(const variant of initial.variants){const option=document.createElement('option');option.value=String(variant.genus);option.textContent=String(variant.genus);select.append(option);}
  label.append(select);controls.prepend(label);
  const status=figure.querySelector('.soliton-status');
  const caption=figure.querySelector('figcaption');
  const drawing=caption.querySelector('a');
  const image=figure.querySelector('img');
  const initialImage=image.getAttribute('src');
  function upload(next){
    if(next.kind!=='moller-genus-model'||next.vertices.length>=65536||next.status!=='schematic')throw new Error('Invalid model');
    data=next;
    for(const [buffer,values] of [[vertexBuffer,data.vertices],[normalBuffer,data.normals]]){gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(values.flat()),gl.STATIC_DRAW);}
    const faces=data.faces.flat();faceCount=faces.length;
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,faceBuffer);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array(faces),gl.STATIC_DRAW);
    const edges=data.faces.flatMap(([a,b,c])=>[a,b,b,c,c,a]);edgeCount=edges.length;
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,edgeBuffer);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array(edges),gl.STATIC_DRAW);
    select.value=String(data.genus);
    heading.textContent=`Genus ${data.genus} · handle schematic`;
    canvas.setAttribute('aria-label',`Genus ${data.genus} gluing schematic with handles around two circles. Not a computed self-shrinker. Drag or use arrow keys to rotate; plus and minus zoom.`);
    const svg=initialImage.replace(/moller-genus\.svg$/,`${data.name}.svg`);
    image.src=svg;image.alt=data.description;drawing.href=svg;
    status.textContent='';requestDraw();
  }
  function draw(){
    scheduled=false;const {width,height}=stage.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2);
    if(canvas.width!==Math.round(width*dpr)||canvas.height!==Math.round(height*dpr)){canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);}gl.viewport(0,0,canvas.width,canvas.height);
    gl.clearColor(247/255,250/255,251/255,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    const pixels=Math.min(width*.44/3.5,height*.39/2.2)*state.zoom;
    gl.uniformMatrix3fv(rotation,false,new Float32Array(modelRotation(state.yaw,state.pitch)));
    gl.uniform2f(scale,2*pixels/width,2*pixels/height);
    gl.uniform1i(wireUniform,false);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,faceBuffer);
    if(state.wire){gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);}
    gl.drawElements(gl.TRIANGLES,faceCount,gl.UNSIGNED_SHORT,0);
    if(state.wire){gl.disable(gl.POLYGON_OFFSET_FILL);gl.uniform1i(wireUniform,true);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,edgeBuffer);gl.drawElements(gl.LINES,edgeCount,gl.UNSIGNED_SHORT,0);}
    canvas.dataset.genus=String(data.genus);canvas.dataset.zoom=state.zoom.toFixed(3);canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;canvas.dataset.wire=String(state.wire);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function zoom(f){state.zoom=Math.max(.5,Math.min(3.5,state.zoom*f));requestDraw();}
  async function choose(genus){
    const id=++request;select.disabled=true;status.textContent='Loading genus '+genus+'…';
    try{
      if(!cache.has(genus)){
        const variant=initial.variants.find(v=>v.genus===genus);
        if(!variant)throw new Error('Unknown genus');
        const url=new URL(figure.dataset.soliton,document.baseURI);url.pathname=url.pathname.replace(/[^/]+$/,variant.model+'.json');
        const response=await fetch(url);if(!response.ok)throw new Error('Model unavailable');const next=await response.json();
        if(next.genus!==genus)throw new Error('Wrong genus');cache.set(genus,next);
      }
      if(id===request)upload(cache.get(genus));
    }catch{if(id===request){select.value=String(data.genus);status.textContent='That model could not load. The current genus remains displayed; the drawing links below are also available.';}}
    finally{if(id===request)select.disabled=false;}
  }
  select.addEventListener('change',()=>choose(Number(select.value)));
  for(const b of figure.querySelectorAll('[data-view-action]'))b.addEventListener('click',()=>{
    const action=b.dataset.viewAction;
    if(action==='in')zoom(1.2);if(action==='out')zoom(1/1.2);
    if(action==='wire'){state.wire=!state.wire;b.setAttribute('aria-pressed',String(state.wire));requestDraw();}
    if(action==='reset'){state=defaults();dragging=null;figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed','false');choose(initial.genus);}
  });
  canvas.addEventListener('pointerdown',e=>{dragging={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!dragging)return;state.yaw+=(e.clientX-dragging.x)*.009;state.pitch+=(e.clientY-dragging.y)*.009;dragging={x:e.clientX,y:e.clientY};requestDraw();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>{dragging=null;});
  canvas.addEventListener('keydown',e=>{
    const keys={ArrowLeft:()=>state.yaw-=.12,ArrowRight:()=>state.yaw+=.12,ArrowUp:()=>state.pitch-=.12,ArrowDown:()=>state.pitch+=.12,'+':()=>zoom(1.2),'=':()=>zoom(1.2),'-':()=>zoom(1/1.2)};
    if(keys[e.key]){e.preventDefault();keys[e.key]();requestDraw();}
  });
  canvas.addEventListener('wheel',e=>{if(document.activeElement!==canvas)return;e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();image.hidden=false;canvas.hidden=true;controls.hidden=true;heading.hidden=true;status.textContent='The static drawing is shown because 3D rendering is unavailable.';});
  upload(initial);controls.hidden=false;figure.querySelector('.soliton-help').hidden=false;
  figure.querySelector('.soliton-help').textContent='Choose genus 8, 16, or 24. Drag to rotate and inspect both rows of handles; + / − zoom. These are topology-checked gluing schematics, not computed shrinkers.';
  image.hidden=true;canvas.hidden=false;new ResizeObserver(requestDraw).observe(stage);
}
