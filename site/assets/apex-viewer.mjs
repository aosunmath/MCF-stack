// Three computed/formula representatives; never interpolate between surfaces.
export function apexCase(data,key){
  if(key==='wing')return data;
  if(!['grim','bowl'].includes(key)||!data.cases?.[key])throw new Error('Unknown apex case');
  return data.cases[key];
}
export function quadraticHeight(k,t){return .5*k*t*t;}

export function initApexFigure(figure,data){
  const canvas=figure.querySelector('canvas'),stage=figure.querySelector('.soliton-stage');
  const controls=figure.querySelector('.soliton-controls'),help=figure.querySelector('.soliton-help'),status=figure.querySelector('.soliton-status');
  const gl=canvas.getContext('webgl',{antialias:true,alpha:false});
  if(!gl)throw new Error('WebGL unavailable');
  const vertex=`attribute vec3 position,normal;uniform mat3 rotation;uniform vec2 scale,offset;
    uniform float center;varying vec3 norm;varying vec3 point;
    void main(){point=position;norm=rotation*normal;vec3 p=rotation*(position-vec3(0.,0.,center));
      gl_Position=vec4(p.xy*scale+offset,-p.z/40.,1.);gl_PointSize=7.;}`;
  const fragment=`precision mediump float;varying vec3 norm;varying vec3 point;
    uniform float cutoff;uniform int lines;uniform bool cutaway;
    void main(){if(point.z>cutoff+.00001||(cutaway&&point.y>.00001))discard;
      if(lines>0){gl_FragColor=lines==2?vec4(.10,.30,.44,1.):lines==3?vec4(.81,.52,.19,1.):vec4(.19,.40,.46,1.);return;}
      vec3 n=normalize(norm);if(!gl_FrontFacing)n=-n;
      float light=.57+.43*max(0.,dot(n,normalize(vec3(-.35,.5,.8))));
      gl_FragColor=vec4(vec3(.32,.61,.67)*light,1.);}`;
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Shader failed');return s;}
  const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));gl.linkProgram(program);
  if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Shader link failed');gl.useProgram(program);
  const uniforms=Object.fromEntries(['rotation','scale','offset','center','cutoff','lines','cutaway'].map(k=>[k,gl.getUniformLocation(program,k)]));
  const buffers=[];let indices;
  function indexBuffer(values){const buffer=gl.createBuffer();buffers.push(buffer);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,buffer);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array(values),gl.STATIC_DRAW);return {buffer,count:values.length};}
  const segments=paths=>paths.flatMap(p=>p.slice(1).flatMap((v,i)=>[p[i],v]));
  function upload(d){
    for(const b of buffers)gl.deleteBuffer(b);buffers.length=0;
    for(const [name,values] of [['position',d.vertices],['normal',d.normals]]){
      const buffer=gl.createBuffer(),loc=gl.getAttribLocation(program,name);buffers.push(buffer);gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
      gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(values.flat()),gl.STATIC_DRAW);gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,3,gl.FLOAT,false,0,0);
    }
    const xs=d.symmetryPaths.filter(p=>p.every(i=>Math.abs(d.vertices[i][1])<1e-6));
    const ys=d.symmetryPaths.filter(p=>p.every(i=>Math.abs(d.vertices[i][0])<1e-6));
    indices={faces:indexBuffer(d.faces.flat()),mesh:indexBuffer(d.faces.flatMap(([a,b,c])=>[a,b,b,c,c,a])),
      contours:indexBuffer(segments(d.paths)),x:indexBuffer(segments(xs)),y:indexBuffer(segments(ys)),
      apex:indexBuffer([d.vertices.findIndex(p=>Math.hypot(...p)<1e-7)])};
  }
  const plot=document.createElement('canvas');plot.hidden=true;plot.tabIndex=0;plot.setAttribute('role','img');stage.append(plot);
  const ctx=plot.getContext('2d');if(!ctx)throw new Error('Canvas unavailable');
  const badge=document.createElement('p');badge.className='apex-view-label';stage.append(badge);
  const legend=document.createElement('p');legend.className='apex-legend';controls.after(legend);
  const defaults=()=>({key:'wing',mode:'cutaway',yaw:-.48,pitch:.58,zoom:1,height:6,extent:2,wire:false});
  let state=defaults(),current=data,scheduled=false,dragging=null;
  function select(title,options){
    const label=document.createElement('label');label.textContent=title+' ';
    const input=document.createElement('select');input.setAttribute('aria-label',title);
    for(const [value,text] of options){const option=document.createElement('option');option.value=value;option.textContent=text;input.append(option);}
    label.append(input);return {label,input};
  }
  const member=select('Apex curvatures',[['grim','(0, 1) · grim reaper'],['wing','≈ (0.2443, 0.7557) · Δ-wing'],['bowl','(½, ½) · bowl']]);
  const view=select('Apex view',[['cutaway','Cutaway'],['surface','Full surface'],['sections','Principal sections']]);
  controls.prepend(member.label,view.label);
  function slider(title,min,max,step){
    const label=document.createElement('label'),output=document.createElement('output'),input=document.createElement('input');
    input.type='range';Object.assign(input,{min:String(min),max:String(max),step:String(step)});input.setAttribute('aria-label',title);
    label.append(output,input);controls.append(label);return {label,output,input};
  }
  const height=slider('Apex display height',.5,6,.25),extent=slider('Section radius',.5,3,.25);
  function sync(){
    const surface=state.mode!=='sections';member.input.value=state.key;view.input.value=state.mode;
    height.label.hidden=!surface;extent.label.hidden=surface;height.input.value=String(state.height);extent.input.value=String(state.extent);
    height.output.textContent=`Height ≤ ${state.height.toFixed(2)}`;extent.output.textContent=`Section radius: ${state.extent.toFixed(2)}`;
    canvas.hidden=!surface;plot.hidden=surface;
    const wire=figure.querySelector('[data-view-action="wire"]');wire.disabled=!surface;wire.setAttribute('aria-pressed',String(state.wire));
    badge.textContent=`ℝ³ · ${current.curvatureLabel} · ${current.method}`;
    legend.textContent=surface?'Blue: x symmetry section. Ochre: y symmetry section. Dot: chosen origin. All visible edges are display cuts.':'Blue: u(x,0). Ochre: u(0,y). Dashed: ½kᵢs², shown only for |s| ≤ 1. The two bowl sections coincide.';
    help.textContent=surface?'Drag to rotate; + / − zoom. Lower the height to inspect the apex. The selector shows three representatives; it does not interpolate between them.':'Compare the two sections at the same horizontal distance. The quadratic is only the local Taylor model. Zoom buttons change the plotted window.';
    status.textContent=`Domain: ${current.domain}. ${current.note}`;
    canvas.setAttribute('aria-label',`${current.label} in R3. ${current.curvatureLabel}. ${current.method}. ${state.mode}; height at most ${state.height}. Arrow keys rotate; plus and minus zoom.`);
    plot.setAttribute('aria-label',`Principal sections of the ${current.label}, with local quadratic comparisons.`);
    stage.dataset.view=state.mode;canvas.dataset.case=state.key;requestDraw();
  }
  function size(c){const box=stage.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2);
    if(c.width!==Math.round(box.width*dpr)||c.height!==Math.round(box.height*dpr)){c.width=Math.round(box.width*dpr);c.height=Math.round(box.height*dpr);}
    return {w:box.width,h:box.height,dpr};}
  function drawPlot(){
    const {w,h,dpr}=size(plot);ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
    const xmax=state.extent/state.zoom;
    const selected=current.profiles.map(p=>p.filter(([x])=>Math.abs(x)<=xmax));
    const ymax=Math.max(.1,...selected.flat().map(p=>p[1]))*1.08;
    const left=43,right=w-20,top=57,bottom=h-40;
    const project=([x,y])=>[(left+right)/2+x*(right-left)/(2*xmax),bottom-y*(bottom-top)/ymax];
    ctx.font='11px sans-serif';ctx.lineWidth=1;ctx.fillStyle='#526b77';
    for(let i=0;i<=4;i++){
      const y=ymax*i/4,p=project([0,y]);ctx.strokeStyle='#dce6e9';ctx.beginPath();ctx.moveTo(left,p[1]);ctx.lineTo(right,p[1]);ctx.stroke();ctx.fillText(y.toFixed(ymax<1?2:1),4,p[1]+4);
    }
    ctx.textAlign='center';for(let i=-2;i<=2;i++){const x=i*xmax/2;ctx.fillText(x.toFixed(2),project([x,0])[0],bottom+17);}
    ctx.fillText('Signed distance s from the origin',(left+right)/2,h-7);ctx.textAlign='left';ctx.fillText('Height',left,top-12);
    ctx.save();ctx.beginPath();ctx.rect(left,top,right-left,bottom-top+2);ctx.clip();
    function line(points,color,dash=[]){ctx.strokeStyle=color;ctx.lineWidth=dash.length?1.5:2.4;ctx.setLineDash(dash);ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...project(p)):ctx.moveTo(...project(p)));ctx.stroke();}
    current.profiles.forEach((p,i)=>{
      const color=i?'#bc7b32':'#21667f';line(p,color);
      const r=Math.min(1,xmax),t=Array.from({length:101},(_,j)=>-r+2*r*j/100);
      line(t.map(x=>[x,quadraticHeight(current.curvatures[i],x)]),color,[5,4]);
    });
    ctx.restore();ctx.setLineDash([]);plot.dataset.case=state.key;plot.dataset.zoom=state.zoom.toFixed(3);plot.dataset.extent=String(state.extent);
  }
  function draw(){
    scheduled=false;if(state.mode==='sections'){drawPlot();return;}
    const {w,h}=size(canvas);gl.viewport(0,0,canvas.width,canvas.height);gl.clearColor(247/255,250/255,251/255,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    const cy=Math.cos(state.yaw),sy=Math.sin(state.yaw),cp=Math.cos(state.pitch),sp=Math.sin(state.pitch);
    gl.uniformMatrix3fv(uniforms.rotation,false,new Float32Array([cy,-sy*sp,sy*cp,-sy,-cy*sp,cy*cp,0,cp,sp]));
    // Fit projected bounds, including the next mesh band at a clipping plane.
    // This keeps the long wings inside both desktop and portrait canvases.
    const patch=current.vertices.filter(p=>p[2]<=state.height+.26&&(state.mode!=='cutaway'||p[1]<1e-5));
    const px=patch.map(p=>cy*p[0]-sy*p[1]);
    const py=patch.map(p=>cp*(p[2]-state.height/2)-sp*(sy*p[0]+cy*p[1]));
    const xmin=Math.min(...px),xmax=Math.max(...px),ymin=Math.min(...py),ymax=Math.max(...py);
    const scale=Math.min((w-48)/Math.max(xmax-xmin,.1),(h-78)/Math.max(ymax-ymin,.1))*state.zoom;
    gl.uniform2f(uniforms.offset,-scale*(xmin+xmax)/w,-scale*(ymin+ymax)/h-26/h);
    gl.uniform2f(uniforms.scale,2*scale/w,2*scale/h);gl.uniform1f(uniforms.center,state.height/2);gl.uniform1f(uniforms.cutoff,state.height);gl.uniform1i(uniforms.cutaway,state.mode==='cutaway');
    gl.enable(gl.DEPTH_TEST);gl.frontFace(gl.CW);gl.disable(gl.CULL_FACE);gl.uniform1i(uniforms.lines,0);gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indices.faces.buffer);gl.drawElements(gl.TRIANGLES,indices.faces.count,gl.UNSIGNED_SHORT,0);gl.disable(gl.POLYGON_OFFSET_FILL);
    for(const [item,color] of [[state.wire?indices.mesh:indices.contours,1],[indices.x,2],[indices.y,3]]){
      gl.uniform1i(uniforms.lines,color);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,item.buffer);gl.drawElements(gl.LINES,item.count,gl.UNSIGNED_SHORT,0);
    }
    gl.uniform1i(uniforms.lines,2);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indices.apex.buffer);gl.drawElements(gl.POINTS,1,gl.UNSIGNED_SHORT,0);
    canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;canvas.dataset.zoom=state.zoom.toFixed(3);canvas.dataset.height=String(state.height);canvas.dataset.mesh=String(state.wire);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function zoom(f){state.zoom=Math.max(.65,Math.min(3,state.zoom*f));requestDraw();}
  member.input.addEventListener('change',()=>{state.key=member.input.value;current=apexCase(data,state.key);state.zoom=1;upload(current);sync();});
  view.input.addEventListener('change',()=>{state.mode=view.input.value;state.zoom=1;sync();});
  height.input.addEventListener('input',()=>{state.height=Number(height.input.value);sync();});
  extent.input.addEventListener('input',()=>{state.extent=Number(extent.input.value);sync();});
  for(const button of figure.querySelectorAll('[data-view-action]'))button.addEventListener('click',()=>{
    const action=button.dataset.viewAction;if(action==='in')zoom(1.2);if(action==='out')zoom(1/1.2);
    if(action==='wire'){state.wire=!state.wire;sync();}
    if(action==='reset'){state=defaults();current=data;dragging=null;upload(current);sync();}
  });
  canvas.addEventListener('pointerdown',e=>{dragging={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!dragging)return;state.yaw+=(e.clientX-dragging.x)*.009;state.pitch+=(e.clientY-dragging.y)*.009;dragging={x:e.clientX,y:e.clientY};requestDraw();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>dragging=null);
  for(const c of [canvas,plot]){
    c.addEventListener('keydown',e=>{
      if(['+','=','-'].includes(e.key)){e.preventDefault();zoom(e.key==='-'?1/1.2:1.2);}
      if(state.mode!=='sections'&&['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){
        e.preventDefault();if(e.key==='ArrowLeft')state.yaw-=.12;if(e.key==='ArrowRight')state.yaw+=.12;if(e.key==='ArrowUp')state.pitch-=.12;if(e.key==='ArrowDown')state.pitch+=.12;requestDraw();
      }
    });
    c.addEventListener('wheel',e=>{if(document.activeElement!==c)return;e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  }
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();canvas.hidden=true;plot.hidden=true;badge.hidden=true;legend.hidden=true;controls.hidden=true;help.hidden=true;figure.querySelector('img').hidden=false;status.textContent='The static drawing is shown. Reload to restore interactive geometry.';});
  upload(current);figure.querySelector('img').hidden=true;controls.hidden=false;help.hidden=false;sync();new ResizeObserver(requestDraw).observe(stage);
}
