import {wangMesh,wangRotation,axialTip,WANG_WINDOW} from './wang-geometry.mjs';

export function initWangFigure(figure,data){
  const canvas=figure.querySelector('canvas'),stage=figure.querySelector('.soliton-stage');
  const controls=figure.querySelector('.soliton-controls'),help=figure.querySelector('.soliton-help'),status=figure.querySelector('.soliton-status');
  const gl=canvas.getContext('webgl',{antialias:true,alpha:false});
  if(!gl)throw new Error('WebGL unavailable');
  const vertex=`attribute vec3 position,normal;uniform mat3 rotation;uniform vec2 scale,offset;uniform float center;
    varying vec3 norm;void main(){norm=rotation*normal;vec3 p=rotation*(position-vec3(0.,0.,center));
    gl_Position=vec4(p.xy*scale+offset,-p.z/30.,1.);}`;
  const fragment=`precision mediump float;varying vec3 norm;uniform bool wire;uniform vec3 tint;
    void main(){if(wire){gl_FragColor=vec4(tint*.59,1.);return;}
    vec3 n=normalize(norm);if(n.z<0.)n=-n;
    float light=.50+.50*max(0.,dot(n,normalize(vec3(-.35,.55,.85))));
    gl_FragColor=vec4(tint*light,1.);}`;
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Shader compilation failed');return s;}
  const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));gl.linkProgram(program);
  if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Shader link failed');gl.useProgram(program);
  const uniforms=Object.fromEntries(['rotation','scale','offset','center','wire','tint'].map(k=>[k,gl.getUniformLocation(program,k)]));
  let buffers=[],indices,mesh,current;
  const defaults=()=>({mode:'level',h:1,yaw:.34,pitch:.48,zoom:1,wire:true});
  let state=defaults(),drag=null,scheduled=false;
  function indexBuffer(values){const b=gl.createBuffer();buffers.push(b);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,b);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array(values),gl.STATIC_DRAW);return {buffer:b,count:values.length};}
  function upload(){
    current=wangMesh(state.mode,state.h);
    for(const b of buffers)gl.deleteBuffer(b);buffers=[];
    for(const name of ['position','normal']){
      const b=gl.createBuffer();buffers.push(b);gl.bindBuffer(gl.ARRAY_BUFFER,b);
      gl.bufferData(gl.ARRAY_BUFFER,new Float32Array((name==='position'?current.vertices:current.normals).flat()),gl.STATIC_DRAW);
      const loc=gl.getAttribLocation(program,name);gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,3,gl.FLOAT,false,0,0);
    }
    indices=indexBuffer(current.faces.flat());mesh=indexBuffer(current.paths.flatMap(p=>p.slice(1).flatMap((v,i)=>[p[i],v])));
  }
  const badge=document.createElement('p');badge.className='wang-view-label';stage.append(badge);
  const axisCanvas=document.createElement('canvas');axisCanvas.className='wang-axes';axisCanvas.setAttribute('aria-hidden','true');stage.append(axisCanvas);
  const ctx=axisCanvas.getContext('2d');if(!ctx)throw new Error('Canvas unavailable');
  const label=document.createElement('label');label.textContent='View ';
  const mode=document.createElement('select');mode.setAttribute('aria-label','Wang illustration view');
  for(const [value,title] of [['level','Level surface in ℝ³'],['slice','Graph slice in ℝ⁴'],['limit','k = 2 blow-down cylinder']]){
    const o=document.createElement('option');o.value=value;o.textContent=title;mode.append(o);
  }
  label.append(mode);controls.prepend(label);
  const scaleLabel=document.createElement('label'),output=document.createElement('output'),scaleInput=document.createElement('input');
  Object.assign(scaleInput,{type:'range',min:'0',max:'8',step:'.25',value:'0'});scaleInput.setAttribute('aria-label','Illustration rescaling');
  scaleLabel.append(output,scaleInput);controls.append(scaleLabel);
  const front=document.createElement('button');front.type='button';front.textContent='Side view';controls.append(front);
  const details=document.createElement('details');details.className='wang-model-note';
  details.innerHTML='<summary>How to read this picture</summary><p>The actual translator is a hypersurface in ℝ⁴: x₄ = u(x₁,x₂,x₃). Its horizontal section x₄ = h is a surface in the three base coordinates. The graph-slice view instead fixes x₂ = 0 and plots height x₄ vertically.</p><p>Teal uses the illustrative convex function f(x) = (x₁² + x₂²)/2 + ((1 + x₃²)^(3/4) − 1)/6, with Fₕ(x) = f(√h x)/h. It does not solve the translator equation and its growth rate is not asserted for Wang’s solutions. The slider changes this model’s rescaling, not flow time or a proved family parameter.</p><p>Ochre shows the exact level set Q = 1 of Q = (x₁² + x₂²)/2, a k = 2 quadratic model permitted by Theorem 1.3. It is not itself a translator. The theorem allows 2 ≤ k ≤ n and scale-dependent rotations; this fixed-axis illustration is not a classification of every example.</p>';
  figure.querySelector('figcaption').after(details);
  function sync(){
    const slice=state.mode==='slice',limit=state.mode==='limit';
    mode.value=state.mode;scaleInput.value=String(Math.log2(state.h));scaleInput.disabled=limit;
    output.textContent=limit?'h → ∞':`Rescaling h = ${Number(state.h.toFixed(1))}`;
    badge.textContent=slice?'Graph slice · x₂ = 0 · height x₄ · schematic':limit?'Quadratic limit · Q = 1 · exact cylinder':'Horizontal section · Fₕ = 1 in the base ℝ³ · schematic';
    help.textContent='Drag or use arrow keys to rotate; + / − zoom. Side view shows the long axis. The fixed spatial window is the same at every rescaling.';
    status.textContent=limit?'Q = (x₁² + x₂²)/2. The x₃-direction is free; both ends continue beyond the drawing.':slice?'A two-dimensional slice of a three-dimensional graph in ℝ⁴, not a translator surface in ℝ³. Rim edges are display cuts.':current.clipped?'The model’s caps have moved beyond the fixed window |x₃| ≤ 3.8. Open rims are display cuts; finite-height model levels remain compact.':`Closed convex model level; axial tips at x₃ = ±${axialTip(state.h).toFixed(2)}. Circle symmetry in (x₁,x₂) does not make the level a sphere or a round cylinder.`;
    canvas.setAttribute('aria-label',`${badge.textContent}. Rescaling ${state.h}. Drag or use arrow keys to rotate; plus and minus zoom.`);
    figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed',String(state.wire));
    requestDraw();
  }
  function draw(){
    scheduled=false;
    const box=stage.getBoundingClientRect(),w=box.width,h=box.height,dpr=Math.min(devicePixelRatio||1,2);
    for(const c of [canvas,axisCanvas]){if(c.width!==Math.round(w*dpr)||c.height!==Math.round(h*dpr)){c.width=Math.round(w*dpr);c.height=Math.round(h*dpr);}}
    gl.viewport(0,0,canvas.width,canvas.height);gl.clearColor(247/255,250/255,251/255,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    const rot=wangRotation(state.yaw,state.pitch),center=state.mode==='slice'?1.5:0;
    // Fixed bounding sphere: rescaling never auto-fits the escaping caps.
    const bounds=state.mode==='slice'?[WANG_WINDOW,1.7,2.3]:[WANG_WINDOW,1.6,1.6];
    const span=i=>2*bounds.reduce((sum,b,j)=>sum+b*Math.abs(rot[i+3*j]),0);
    const scale=Math.min((w-48)/span(0),(h-100)/span(1))*state.zoom;
    gl.uniformMatrix3fv(uniforms.rotation,false,new Float32Array(rot));gl.uniform2f(uniforms.scale,2*scale/w,2*scale/h);
    gl.uniform2f(uniforms.offset,0,-10/h);gl.uniform1f(uniforms.center,center);
    gl.uniform3fv(uniforms.tint,state.mode==='limit'?[.78,.54,.27]:[.28,.62,.67]);
    gl.enable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.uniform1i(uniforms.wire,0);gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indices.buffer);gl.drawElements(gl.TRIANGLES,indices.count,gl.UNSIGNED_SHORT,0);gl.disable(gl.POLYGON_OFFSET_FILL);
    if(state.wire){gl.uniform1i(uniforms.wire,1);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,mesh.buffer);gl.drawElements(gl.LINES,mesh.count,gl.UNSIGNED_SHORT,0);}
    ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
    // A separate labeled axis key stays readable under every rotation.
    const origin=[w-53,h-47],axisScale=25;
    ctx.font='12px sans-serif';ctx.lineWidth=1.5;
    for(const [i,name,color] of [[0,'x₃','#476170'],[1,'x₁','#21667f'],[2,state.mode==='slice'?'x₄':'x₂','#a56a2d']]){
      const x=origin[0]+axisScale*rot[3*i],y=origin[1]-axisScale*rot[3*i+1];
      ctx.strokeStyle=color;ctx.beginPath();ctx.moveTo(...origin);ctx.lineTo(x,y);ctx.stroke();ctx.fillStyle=color;ctx.fillText(name,x+3,y-3);
    }
    ctx.fillStyle='#476170';ctx.fillText(state.mode==='slice'?'Height x₄ = Fₕ(x₁,0,x₃)':state.mode==='limit'?'x₁² + x₂² = 2':'Fₕ(x₁,x₂,x₃) = 1',14,h-18);
    Object.assign(canvas.dataset,{mode:state.mode,h:String(state.h),zoom:state.zoom.toFixed(3),rotation:`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`,clipped:String(current.clipped)});
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function zoom(f){state.zoom=Math.max(.5,Math.min(3,state.zoom*f));requestDraw();}
  mode.addEventListener('change',()=>{state.mode=mode.value;state.zoom=1;upload();sync();});
  scaleInput.addEventListener('input',()=>{state.h=2**Number(scaleInput.value);upload();sync();});
  front.addEventListener('click',()=>{state.yaw=0;state.pitch=0;requestDraw();});
  for(const button of figure.querySelectorAll('[data-view-action]'))button.addEventListener('click',()=>{
    const a=button.dataset.viewAction;if(a==='in')zoom(1.2);if(a==='out')zoom(1/1.2);
    if(a==='wire'){state.wire=!state.wire;sync();}
    if(a==='reset'){state=defaults();drag=null;upload();sync();}
  });
  canvas.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;state.yaw+=(e.clientX-drag.x)*.009;state.pitch+=(e.clientY-drag.y)*.009;drag={x:e.clientX,y:e.clientY};requestDraw();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>drag=null);
  canvas.addEventListener('wheel',e=>{if(document.activeElement!==canvas)return;e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  canvas.addEventListener('keydown',e=>{const keys={ArrowLeft:()=>state.yaw-=.12,ArrowRight:()=>state.yaw+=.12,ArrowUp:()=>state.pitch-=.12,ArrowDown:()=>state.pitch+=.12,'+':()=>zoom(1.15),'=':()=>zoom(1.15),'-':()=>zoom(1/1.15)};if(keys[e.key]){e.preventDefault();keys[e.key]();requestDraw();}});
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();canvas.hidden=true;axisCanvas.hidden=true;badge.hidden=true;controls.hidden=true;help.hidden=true;figure.querySelector('img').hidden=false;status.textContent='The static drawing is shown; interactive geometry is unavailable.';});
  upload();sync();figure.querySelector('img').hidden=true;canvas.hidden=false;controls.hidden=false;help.hidden=false;
  new ResizeObserver(requestDraw).observe(stage);
}
