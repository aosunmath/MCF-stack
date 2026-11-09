// Original numerical Scherk patch, repeated only by its vertical half-turns.
import {nguyenNormals} from './nguyen-viewer.mjs';
export function scherkTiles(mode){
  if(mode==='patch')return [[0,0]];
  if(mode!=='periodic')throw new Error('Unknown Scherk view');
  const tiles=[];
  for(let i=-2;i<=2;i++)for(let j=-2;j<=2;j++)if((i-j)%2===0)tiles.push([i,j]);
  return tiles;
}
export function initScherkFigure(figure,data){
  const canvas=figure.querySelector('canvas'),gl=canvas.getContext('webgl',{antialias:true,alpha:false});
  if(!gl)throw new Error('WebGL unavailable');
  const vertex=`attribute vec3 position, normal; uniform mat3 rotation; uniform vec2 scale, offset;
    varying vec3 norm; varying float height;
    void main(){norm=rotation*normal;height=position.z;
    vec3 p=rotation*(position+vec3(offset,0.0));gl_Position=vec4(p.x*scale.x,p.y*scale.y,-p.z/30.0,1.0);}`;
  const fragment=`precision mediump float; varying vec3 norm; varying float height;
    uniform vec3 tint; uniform bool lines; uniform float crop;
    void main(){if(abs(height)>crop)discard;
    if(lines){gl_FragColor=vec4(.12,.25,.30,1.0);return;}
    vec3 n=normalize(norm); if(!gl_FrontFacing)n=-n;
    float light=.48+.50*max(0.0,dot(n,normalize(vec3(-.3,.5,.8))));
    float shine=pow(max(0.0,dot(n,normalize(vec3(-.15,.25,1.0)))),36.0);
    gl_FragColor=vec4(tint*light+vec3(.10)*shine,1.0);}`;
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Shader compilation failed');return s;}
  const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));
  gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Shader link failed');gl.useProgram(program);
  const uniforms=Object.fromEntries(['rotation','scale','offset','tint','lines','crop'].map(k=>[k,gl.getUniformLocation(program,k)]));
  if(data.vertices.length>65535)throw new Error('Mesh too large');
  for(const [name,values] of Object.entries({position:data.vertices,normal:nguyenNormals(data.vertices,data.faces)})){
    const b=gl.createBuffer(),location=gl.getAttribLocation(program,name);gl.bindBuffer(gl.ARRAY_BUFFER,b);
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(values.flat()),gl.STATIC_DRAW);gl.enableVertexAttribArray(location);gl.vertexAttribPointer(location,3,gl.FLOAT,false,0,0);
  }
  const faces=new Uint16Array(data.faces.flat()),edges=new Uint16Array(data.faces.flatMap(([a,b,c])=>[a,b,b,c,c,a]));
  const faceBuffer=gl.createBuffer(),edgeBuffer=gl.createBuffer();
  for(const [b,v] of [[faceBuffer,faces],[edgeBuffer,edges]]){gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,b);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,v,gl.STATIC_DRAW);}
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls'),status=figure.querySelector('.soliton-status');
  const defaults=()=>({yaw:data.view.yaw,pitch:data.view.pitch,zoom:1,mode:'periodic',wire:false,crop:1.5});
  let state=defaults(),scheduled=false,dragging=null;
  const badge=document.createElement('p');badge.className='scherk-view-label';stage.append(badge);
  function draw(){
    scheduled=false;const box=stage.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2),w=Math.round(box.width*dpr),h=Math.round(box.height*dpr);if(!w||!h)return;
    canvas.width=w;canvas.height=h;gl.viewport(0,0,w,h);gl.clearColor(247/255,250/255,251/255,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    const cy=Math.cos(state.yaw),sy=Math.sin(state.yaw),cp=Math.cos(state.pitch),sp=Math.sin(state.pitch);
    gl.uniformMatrix3fv(uniforms.rotation,false,new Float32Array([cy,-sy*sp,sy*cp,-sy,-cy*sp,cy*cp,0,cp,sp]));
    const scale=Math.min(w*.44/(state.mode==='patch'?1.9:7.8),h*.40/(state.mode==='patch'?2.2:4.8))*state.zoom;
    gl.uniform2f(uniforms.scale,2*scale/w,2*scale/h);gl.uniform1f(uniforms.crop,state.crop);gl.enable(gl.DEPTH_TEST);gl.frontFace(gl.CW);gl.disable(gl.CULL_FACE);
    for(const [i,j] of scherkTiles(state.mode)){
      gl.uniform2f(uniforms.offset,i*data.length,j*data.width);
      gl.uniform3f(uniforms.tint,...((i===0&&j===0)?[.78,.51,.26]:[.24,.54,.62]));
      gl.uniform1i(uniforms.lines,false);gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,faceBuffer);gl.drawElements(gl.TRIANGLES,faces.length,gl.UNSIGNED_SHORT,0);gl.disable(gl.POLYGON_OFFSET_FILL);
      if(state.wire){gl.uniform1i(uniforms.lines,true);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,edgeBuffer);gl.drawElements(gl.LINES,edges.length,gl.UNSIGNED_SHORT,0);}
    }
    canvas.dataset.view=state.mode;canvas.dataset.zoom=state.zoom.toFixed(3);canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;canvas.dataset.crop=String(state.crop);canvas.dataset.mesh=String(state.wire);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  const label=document.createElement('label');label.textContent='View ';
  const view=document.createElement('select');view.setAttribute('aria-label','Scherk surface view');
  for(const [value,title] of [['periodic','Periodic surface'],['patch','Fundamental patch']]){const o=document.createElement('option');o.value=value;o.textContent=title;view.append(o);}
  label.append(view);controls.prepend(label);
  const cropLabel=document.createElement('label'),output=document.createElement('output'),crop=document.createElement('input');
  crop.type='range';crop.min='.3';crop.max='1.5';crop.step='.05';crop.setAttribute('aria-label','Displayed height cutoff');cropLabel.append(output,crop);controls.append(cropLabel);
  const plan=document.createElement('button');plan.type='button';plan.textContent='Top view';controls.append(plan);
  const legend=document.createElement('p');legend.className='scherk-legend';legend.textContent='Orange: fundamental patch · Blue: half-turn copies · Translation direction: +z';controls.after(legend);
  function sync(){
    view.value=state.mode;crop.value=String(state.crop);output.textContent=`Height |z| ≤ ${state.crop.toFixed(2)}`;
    badge.textContent='α = π/2 · w = π/2 · numerical approximation';
    figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed',String(state.wire));
    status.textContent=`Finite boundary heights ±2.5; computed base L ≈ ${data.length.toFixed(4)}. Small corner fills are illustrative. Clipped edges are artificial; no certified error bound.`;
    canvas.setAttribute('aria-label',`Numerical Scherk translator ${state.mode==='patch'?'fundamental patch':'with repeated half-turn copies'}. Small corner fills are illustrative. Arrow keys rotate; plus and minus zoom.`);requestDraw();
  }
  view.addEventListener('change',()=>{state.mode=view.value;state.zoom=1;state.yaw=data.view.yaw;state.pitch=data.view.pitch;sync();});
  crop.addEventListener('input',()=>{state.crop=Number(crop.value);sync();});
  plan.addEventListener('click',()=>{state.yaw=0;state.pitch=Math.PI/2;requestDraw();});
  function zoom(f){state.zoom=Math.max(.5,Math.min(3.5,state.zoom*f));requestDraw();}
  for(const b of figure.querySelectorAll('[data-view-action]'))b.addEventListener('click',()=>{
    const a=b.dataset.viewAction;if(a==='in')zoom(1.2);if(a==='out')zoom(1/1.2);if(a==='wire'){state.wire=!state.wire;sync();}if(a==='reset'){state=defaults();dragging=null;sync();}
  });
  canvas.addEventListener('pointerdown',e=>{dragging={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!dragging)return;state.yaw+=(e.clientX-dragging.x)*.009;state.pitch+=(e.clientY-dragging.y)*.009;dragging={x:e.clientX,y:e.clientY};requestDraw();});
  for(const e of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(e,()=>{dragging=null;});
  canvas.addEventListener('keydown',e=>{const keys={ArrowLeft:()=>state.yaw-=.12,ArrowRight:()=>state.yaw+=.12,ArrowUp:()=>state.pitch-=.12,ArrowDown:()=>state.pitch+=.12,'+':()=>zoom(1.2),'=':()=>zoom(1.2),'-':()=>zoom(1/1.2)};if(keys[e.key]){e.preventDefault();keys[e.key]();requestDraw();}});
  canvas.addEventListener('wheel',e=>{if(document.activeElement!==canvas)return;e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();canvas.hidden=true;badge.hidden=true;legend.hidden=true;controls.hidden=true;figure.querySelector('.soliton-help').hidden=true;figure.querySelector('img').hidden=false;status.textContent='The graphics context was lost; the static drawing is shown. Reload to restore interaction.';});
  figure.querySelector('.soliton-help').textContent='Drag or use arrow keys to rotate; + / − zoom. Top view shows the checkerboard of graph domains. The height slider clips the display; it does not change the translator.';
  controls.hidden=false;figure.querySelector('.soliton-help').hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;sync();new ResizeObserver(requestDraw).observe(stage);
}
