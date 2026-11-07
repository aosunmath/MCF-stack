// Source-informed drawing only. This formula does not solve the translator PDE.
export function pitchforkX(y,z){return .5*Math.sin(y)*Math.exp(z)+y*z-Math.tan(y/2);}
export function pitchforkSlice(z,limit=6,count=1600){
  const segments=[];
  let previous=null;
  for(let i=0;i<=count;i++){
    const y=Math.PI*.998*(-1+2*i/count),x=pitchforkX(y,z),p=[x,y,z];
    if(previous){
      let a=previous,b=p;
      if(Math.min(a[0],b[0])<=limit&&Math.max(a[0],b[0])>=-limit){
        const clipped=q=>{if(Math.abs(q[0])<=limit)return q;const edge=Math.sign(q[0])*limit,t=(edge-a[0])/(b[0]-a[0]);return a.map((v,k)=>v+t*(b[k]-v));};
        const ca=clipped(a),cb=clipped(b);segments.push(ca,cb);
      }
    }
    previous=p;
  }
  return segments;
}

export function initPitchforkFigure(figure,data){
  const canvas=figure.querySelector('canvas'),stage=figure.querySelector('.soliton-stage');
  const gl=canvas.getContext('webgl',{antialias:true,alpha:false});
  if(!gl)throw new Error('WebGL unavailable');
  const vertex=`attribute vec3 position,normal,color;uniform mat3 rotation;uniform vec2 scale;
    varying vec3 point,norm,tint;void main(){point=position;norm=rotation*normal;tint=color;
    vec3 p=rotation*position;gl_Position=vec4(p.x*scale.x,p.y*scale.y,-p.z/40.0,1.0);}`;
  const fragment=`precision mediump float;varying vec3 point,norm,tint;uniform bool halfOnly,lines;
    void main(){if(halfOnly&&point.y<-.00001)discard;if(lines){gl_FragColor=vec4(tint,1.0);return;}
    vec3 n=normalize(norm);if(n.z<0.0)n=-n;
    float light=.5+.48*max(0.0,dot(n,normalize(vec3(-.35,.55,.8))));
    float grid=abs(fract((point.z+3.5)*2.0+.5)-.5);
    float ink=mix(.78,1.0,smoothstep(.008,.025,grid));
    gl_FragColor=vec4(tint*light*ink,1.0);}`;
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Shader compilation failed: '+gl.getShaderInfoLog(s));return s;}
  const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));gl.linkProgram(program);
  if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Shader link failed');gl.useProgram(program);
  const uniform=Object.fromEntries(['rotation','scale','halfOnly','lines'].map(k=>[k,gl.getUniformLocation(program,k)]));
  const locations=Object.fromEntries(['position','normal','color'].map(k=>[k,gl.getAttribLocation(program,k)]));
  function buffer(values){const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(values.flat()),gl.STATIC_DRAW);return b;}
  const surface={position:buffer(data.vertices),normal:buffer(data.normals),color:buffer(data.vertexColors.map(c=>c.map(v=>v/255)))};
  const axisPoints=[[0,0,data.bounds.zMin],[0,0,data.bounds.zMax]];
  const axis={position:buffer(axisPoints),normal:buffer([[1,0,0],[1,0,0]]),color:buffer([[.13,.22,.27],[.13,.22,.27]])};
  const indices=new Uint16Array(data.faces.flat()),indexBuffer=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,indices,gl.STATIC_DRAW);
  const edges=new Uint16Array(data.faces.flatMap(([a,b,c])=>[a,b,b,c,c,a])),edgeBuffer=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,edgeBuffer);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,edges,gl.STATIC_DRAW);
  function bind(buffers){for(const [k,b] of Object.entries(buffers)){gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.enableVertexAttribArray(locations[k]);gl.vertexAttribPointer(locations[k],3,gl.FLOAT,false,0,0);}}
  const controls=figure.querySelector('.soliton-controls'),help=figure.querySelector('.soliton-help'),status=figure.querySelector('.soliton-status');
  const badge=document.createElement('p');badge.className='pitchfork-view-label';stage.append(badge);
  const modeLabel=document.createElement('label');modeLabel.textContent='View ';
  const mode=document.createElement('select');mode.setAttribute('aria-label','Pitchfork view');
  for(const [value,title] of [['surface','Complete surface'],['half','One graphical half'],['slice','Horizontal section']]){const o=document.createElement('option');o.value=value;o.textContent=title;mode.append(o);}
  modeLabel.append(mode);controls.prepend(modeLabel);
  const heightLabel=document.createElement('label');heightLabel.textContent='Height z ';
  const height=document.createElement('input');height.type='range';height.min='-5';height.max='7';height.step='.05';height.value='0';height.setAttribute('aria-label','Horizontal section height');
  const value=document.createElement('output');heightLabel.append(height,value);controls.append(heightLabel);
  const legend=document.createElement('p');legend.className='pitchfork-legend';legend.innerHTML='<span><i style="background:#42919e"></i>0 &lt; y &lt; π</span><span><i style="background:#d3934f"></i>Half-turn about the z-axis</span><span>One connected surface · w = π</span>';controls.after(legend);
  const defaults=()=>({yaw:data.view.yaw,pitch:data.view.pitch,zoom:1,mode:'surface',wire:false,z:0});
  let state=defaults(),scheduled=false,drag=null,sliceBuffers=null,sliceCount=0;
  function updateSlice(){
    const points=pitchforkSlice(state.z),colors=points.map(p=>p[1]>=0?[.18,.46,.51]:[.68,.38,.13]);
    // Include the three limiting lines as muted comparison guides.
    const guides=[-Math.PI,0,Math.PI].flatMap(y=>[[-6,y,0],[6,y,0]]);
    const p=[...guides,...points.map(([x,y])=>[x,y,0])];
    if(sliceBuffers)for(const b of Object.values(sliceBuffers))gl.deleteBuffer(b);
    sliceBuffers={position:buffer(p),normal:buffer(p.map(()=>[0,0,1])),color:buffer([...guides.map(()=>[.74,.79,.81]),...colors])};sliceCount=p.length;
  }
  function draw(){
    scheduled=false;
    const box=stage.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2),w=Math.round(box.width*dpr),h=Math.round(box.height*dpr);
    if(!w||!h)return;canvas.width=w;canvas.height=h;gl.viewport(0,0,w,h);
    gl.clearColor(247/255,250/255,251/255,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    const slice=state.mode==='slice',yaw=slice?0:state.yaw,pitch=slice?-Math.PI/2:state.pitch;
    const cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);
    gl.uniformMatrix3fv(uniform.rotation,false,new Float32Array([cy,-sy*sp,sy*cp,-sy,-cy*sp,cy*cp,0,cp,sp]));
    const scale=Math.min(w*.43/7,h*.38/(slice?Math.PI:4.7))*state.zoom;
    gl.uniform2f(uniform.scale,2*scale/w,2*scale/h);gl.uniform1i(uniform.halfOnly,state.mode==='half');
    gl.disable(gl.CULL_FACE);
    if(slice){gl.disable(gl.DEPTH_TEST);gl.uniform1i(uniform.lines,true);bind(sliceBuffers);gl.drawArrays(gl.LINES,0,sliceCount);}
    else{
      gl.enable(gl.DEPTH_TEST);gl.uniform1i(uniform.lines,false);bind(surface);gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);gl.drawElements(gl.TRIANGLES,indices.length,gl.UNSIGNED_SHORT,0);gl.disable(gl.POLYGON_OFFSET_FILL);
      if(state.wire){gl.uniform1i(uniform.lines,true);gl.disableVertexAttribArray(locations.color);gl.vertexAttrib3f(locations.color,.15,.31,.34);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,edgeBuffer);gl.drawElements(gl.LINES,edges.length,gl.UNSIGNED_SHORT,0);}
      gl.uniform1i(uniform.lines,true);bind(axis);gl.drawArrays(gl.LINES,0,2);
    }
    canvas.dataset.view=state.mode;canvas.dataset.height=String(state.z);canvas.dataset.zoom=state.zoom.toFixed(3);canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;canvas.dataset.mesh=String(state.wire);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function sync(){
    const slice=state.mode==='slice';mode.value=state.mode;height.value=String(state.z);heightLabel.hidden=!slice;value.textContent=state.z.toFixed(2);
    figure.querySelector('[data-view-action="wire"]').disabled=slice;figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed',String(state.wire));
    badge.textContent=slice?`Horizontal section · z = ${state.z.toFixed(2)} · x horizontal, y vertical`:'w = π · upward translation · schematic';
    help.textContent=slice?'Move the height slider: negative heights approach y = 0; positive heights approach y = −π, 0, π. Gray lines mark those limiting positions.':'Drag to rotate; + / − zoom. The colors identify the two graphical halves joined along the vertical z-axis. All outer edges are display cuts.';
    status.textContent=slice?'These are slices of the schematic, not computed slices of the translator. Three limiting sheets do not mean three topological ends.':'Original qualitative reconstruction after Hoffman–Martín–White, Figures 6 and 14 and Theorem 12.1. The drawing preserves the joining line and half-turn symmetry; it is not a numerical solution of the translator equation.';
    canvas.setAttribute('aria-label',slice?`Schematic horizontal pitchfork section at height ${state.z.toFixed(2)}. Use the height slider to compare the limiting planes.`:`Pitchfork schematic, ${state.mode==='half'?'one graphical half':'complete connected surface'}. Drag or use arrow keys to rotate; plus and minus zoom.`);
    requestDraw();
  }
  mode.addEventListener('change',()=>{state.mode=mode.value;state.zoom=1;drag=null;sync();});
  height.addEventListener('input',()=>{state.z=Number(height.value);updateSlice();sync();});
  function zoom(f){state.zoom=Math.max(.5,Math.min(3,state.zoom*f));requestDraw();}
  for(const b of figure.querySelectorAll('[data-view-action]'))b.addEventListener('click',()=>{
    const a=b.dataset.viewAction;if(a==='in')zoom(1.2);if(a==='out')zoom(1/1.2);if(a==='wire'){state.wire=!state.wire;sync();}if(a==='reset'){state=defaults();drag=null;updateSlice();sync();}
  });
  canvas.addEventListener('pointerdown',e=>{if(state.mode==='slice')return;drag={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;state.yaw+=(e.clientX-drag.x)*.009;state.pitch+=(e.clientY-drag.y)*.009;drag={x:e.clientX,y:e.clientY};requestDraw();});
  for(const e of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(e,()=>{drag=null;});
  canvas.addEventListener('keydown',e=>{const keys={ArrowLeft:()=>state.yaw-=.12,ArrowRight:()=>state.yaw+=.12,ArrowUp:()=>state.pitch-=.12,ArrowDown:()=>state.pitch+=.12,'+':()=>zoom(1.2),'=':()=>zoom(1.2),'-':()=>zoom(1/1.2)};if(keys[e.key]&&!(state.mode==='slice'&&e.key.startsWith('Arrow'))){e.preventDefault();keys[e.key]();requestDraw();}});
  canvas.addEventListener('wheel',e=>{if(document.activeElement!==canvas)return;e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();canvas.hidden=true;badge.hidden=true;legend.hidden=true;controls.hidden=true;help.hidden=true;figure.querySelector('img').hidden=false;status.textContent='The graphics context was lost; the static schematic is shown. Reload to restore interaction.';});
  updateSlice();sync();canvas.hidden=false;figure.querySelector('img').hidden=true;controls.hidden=false;help.hidden=false;new ResizeObserver(requestDraw).observe(stage);
}
