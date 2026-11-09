// Original Shao–Zou construction schematic; no shrinker PDE is solved here.
export const SHAO_ZOU_LAYERS=[2,3,4,5,6];
export const SHAO_ZOU_COUNTS=[6,10,14];
export function shaoZouModelUrl(base,k,m){
  if(!SHAO_ZOU_LAYERS.includes(k)||!SHAO_ZOU_COUNTS.includes(m))throw new Error('Unsupported illustration counts');
  return base.replace(/shao-zou-stacking\.json$/,`shao-zou-stacking${k===4&&m===10?'':`-${k}-${m}`}.json`);
}
export function shaoZouGap(vertices,factor){
  if(!(factor>=.6&&factor<=2))throw new Error('Unsupported display separation');
  return vertices.map(([x,y,z])=>[x,y,z*factor]);
}
export function shaoZouSites(k,m,radius=1){
  return Array.from({length:k-1},(_,gap)=>Array.from({length:m},(_,j)=>{
    const t=(2*j+gap%2)*Math.PI/m;
    return [radius*Math.cos(t),radius*Math.sin(t)];
  }));
}

export function shaoZouNormals(vertices,faces){
  const normals=vertices.map(()=>[0,0,0]);
  for(const [a,b,c] of faces){
    const u=vertices[b].map((v,i)=>v-vertices[a][i]),v=vertices[c].map((w,i)=>w-vertices[a][i]);
    const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
    for(const j of [a,b,c])for(let k=0;k<3;k++)normals[j][k]+=n[k];
  }
  return normals.map(n=>{const r=Math.hypot(...n)||1;return n.map(v=>v/r);});
}

export function initShaoZouFigure(figure,initial){
  const canvas=figure.querySelector('canvas'),gl=canvas.getContext('webgl',{antialias:true,alpha:false});
  if(!gl)throw new Error('WebGL unavailable');
  const vertex=`attribute vec3 position, normal, color;
    uniform mat3 rotation; uniform vec2 scale; uniform float offset;
    varying vec3 world, norm, tint;
    void main(){world=position;norm=rotation*normal;tint=color;
      vec3 p=rotation*position;gl_Position=vec4(p.x*scale.x,(p.y-offset)*scale.y,-p.z/12.0,1.0);}`;
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
  const uniforms=Object.fromEntries(['rotation','scale','offset','cutaway','lines'].map(k=>[k,gl.getUniformLocation(program,k)]));
  const buffers=Object.fromEntries(['position','normal','color'].map(k=>[k,{buffer:gl.createBuffer(),location:gl.getAttribLocation(program,k)}]));
  const indexBuffer=gl.createBuffer(),meshBuffer=gl.createBuffer();
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  const status=figure.querySelector('.soliton-status'),help=figure.querySelector('.soliton-help');
  let data=initial,indices,meshIndices,scheduled=false,dragging=null,loadId=0;
  const cache=new Map([[`${initial.k}-${initial.m}`,initial]]);
  const defaults=()=>({yaw:initial.view.yaw,pitch:initial.view.pitch,zoom:1,cutaway:true,wire:false,gap:initial.view.gap});
  let state=defaults();
  const badge=document.createElement('p');badge.className='shao-zou-view-label';stage.append(badge);
  function upload(){
    if(data.vertices.length>65535)throw new Error('Illustration exceeds index limit');
    const vertices=shaoZouGap(data.vertices,state.gap);
    const arrays={position:vertices,normal:shaoZouNormals(vertices,data.faces),
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
    const heights=data.vertices.filter(p=>!state.cutaway||p[1]<=0).map(([x,y,z])=>z*state.gap*cp-(x*sy+y*cy)*sp);
    const low=Math.min(...heights),high=Math.max(...heights),extent=(high-low)/2;
    const scale=Math.min(w*.46/data.view.radius,h*.40/Math.max(.5,extent))*state.zoom;
    gl.uniform1f(uniforms.offset,(high+low)/2);
    gl.uniform2f(uniforms.scale,2*scale/w,2*scale/h);gl.uniform1i(uniforms.cutaway,state.cutaway);gl.uniform1i(uniforms.lines,false);
    gl.enable(gl.DEPTH_TEST);gl.frontFace(gl.CW);gl.disable(gl.CULL_FACE);gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);gl.drawElements(gl.TRIANGLES,indices.length,gl.UNSIGNED_SHORT,0);
    gl.disable(gl.POLYGON_OFFSET_FILL);
    if(state.wire){gl.uniform1i(uniforms.lines,true);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,meshBuffer);gl.drawElements(gl.LINES,meshIndices.length,gl.UNSIGNED_SHORT,0);}
    canvas.dataset.k=String(data.k);canvas.dataset.m=String(data.m);
    canvas.dataset.genus=String(data.genus);canvas.dataset.view=state.cutaway?'cutaway':'surface';
    canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;
    canvas.dataset.zoom=state.zoom.toFixed(3);canvas.dataset.gap=String(state.gap);canvas.dataset.mesh=String(state.wire);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function chooser(text,values){
    const label=document.createElement('label');label.textContent=text+' ';
    const select=document.createElement('select');select.setAttribute('aria-label',text);
    for(const v of values){const option=document.createElement('option');option.value=String(v);option.textContent=String(v);select.append(option);}
    label.append(select);controls.prepend(label);return select;
  }
  const mSelect=chooser('Bridges per gap m',SHAO_ZOU_COUNTS);
  const kSelect=chooser('Sheets / ends k',SHAO_ZOU_LAYERS);
  const cutButton=document.createElement('button');cutButton.type='button';cutButton.textContent='Cutaway';controls.append(cutButton);
  for(const [name,yaw,pitch] of [['Top view',0,Math.PI/2],['Side view',0,0]]){
    const b=document.createElement('button');b.type='button';b.textContent=name;controls.append(b);
    b.addEventListener('click',()=>{state.yaw=yaw;state.pitch=pitch;state.zoom=1;requestDraw();});
  }
  const gapLabel=document.createElement('label');gapLabel.textContent='Display separation ';
  const gap=document.createElement('input');gap.type='range';gap.min='.6';gap.max='2';gap.step='.05';gap.setAttribute('aria-label','Display separation');
  const output=document.createElement('output');gapLabel.append(gap,output);controls.append(gapLabel);
  const layoutButton=document.createElement('button');layoutButton.type='button';layoutButton.textContent='Neck layout';layoutButton.setAttribute('aria-expanded','false');controls.append(layoutButton);
  const plan=document.createElement('div');plan.className='shao-zou-plan';plan.hidden=true;controls.after(plan);
  const svgNS='http://www.w3.org/2000/svg';
  function element(name,attributes,text){
    const node=document.createElementNS(svgNS,name);
    for(const [key,value] of Object.entries(attributes))node.setAttribute(key,String(value));
    if(text)node.textContent=text;return node;
  }
  function drawPlan(){
    plan.replaceChildren();
    const svg=element('svg',{viewBox:'0 0 210 210',role:'img','aria-label':`Projected neck sites: ${data.m} sites per gap, alternate gaps offset by pi over m.`});
    svg.append(element('circle',{cx:108,cy:101,r:72,fill:'none',stroke:'#99adb5','stroke-dasharray':'4 4'}));
    const description=document.createElement('div');
    function line(text,color){const p=document.createElement('p');p.textContent=text;if(color)p.style.color=color;description.append(p);}
    const sites=shaoZouSites(data.k,data.m,72);
    for(let group=0;group<Math.min(sites.length,2);group++){
      const color=group===0?'#21667f':'#b76c43';
      for(const [x,y] of sites[group])svg.append(element('circle',{cx:108+x,cy:101-y,r:5,fill:color}));
      line(`${group===0?'A':'B'}: ${data.m} equally spaced sites`,color);
    }
    line(`Gaps, bottom to top: ${Array.from({length:data.k-1},(_,i)=>i%2?'B':'A').join(' → ')}`);
    line(data.k===2?'Only one gap is present.':'A and B differ by π/m (half a step).');
    const note=document.createElement('p');note.className='shao-zou-plan-note';note.textContent='Plan of idealized neck sites; finite-m radii and tilts are not computed.';
    plan.append(svg,description,note);
  }
  layoutButton.addEventListener('click',()=>{plan.hidden=!plan.hidden;layoutButton.setAttribute('aria-expanded',String(!plan.hidden));});
  function sync(){
    kSelect.value=String(data.k);mSelect.value=String(data.m);gap.value=String(state.gap);output.textContent=`${state.gap.toFixed(2)}×`;
    cutButton.setAttribute('aria-pressed',String(state.cutaway));figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed',String(state.wire));
    badge.textContent=`${data.k} ends · ${(data.k-1)*data.m} bridges · model genus ${data.genus} · schematic`;
    canvas.setAttribute('aria-label',`Shao–Zou construction schematic: ${data.k} sheets, ${data.m} staggered bridges per gap, model genus ${data.genus}; ${state.cutaway?'front half removed':'full surface'}. Not a computed self-shrinker. Arrow keys rotate; plus and minus zoom.`);
    help.textContent='Drag to rotate; + / − zoom. Cutaway exposes the open necks. Neck layout shows the staggered sites. Separation is a drawing control. Outer rims and cut edges are display boundaries.';
    status.textContent=`k = ${data.k}, m = ${data.m}: ${data.k%2===0?'prism symmetry Dₘₕ':'antiprism symmetry Dₘd'}; genus (k − 1)(m − 1) = ${data.genus}. Existence requires sufficiently large m for each k; the displayed counts are illustrative. Neck dimensions and end slopes are not solved.`;
    drawPlan();requestDraw();
  }
  async function changeModel(){
    const k=Number(kSelect.value),m=Number(mSelect.value),id=++loadId,key=`${k}-${m}`;status.textContent=`Loading k = ${k}, m = ${m}…`;
    try{
      if(!cache.has(key)){const response=await fetch(shaoZouModelUrl(figure.dataset.soliton,k,m));if(!response.ok)throw new Error('mesh unavailable');cache.set(key,await response.json());}
      if(id!==loadId)return;
      const previous=data;data=cache.get(key);
      try{upload();}catch(error){data=previous;upload();throw error;}
      sync();
    }catch{if(id===loadId){kSelect.value=String(data.k);mSelect.value=String(data.m);status.textContent=`The requested model could not load; k = ${data.k}, m = ${data.m} remains displayed.`;}}
  }
  kSelect.addEventListener('change',changeModel);mSelect.addEventListener('change',changeModel);
  cutButton.addEventListener('click',()=>{state.cutaway=!state.cutaway;sync();});
  gap.addEventListener('input',()=>{state.gap=Number(gap.value);upload();sync();});
  function zoom(f){state.zoom=Math.max(.5,Math.min(3,state.zoom*f));requestDraw();}
  for(const b of figure.querySelectorAll('[data-view-action]'))b.addEventListener('click',()=>{
    const action=b.dataset.viewAction;
    if(action==='in')zoom(1.2);if(action==='out')zoom(1/1.2);
    if(action==='wire'){state.wire=!state.wire;sync();}
    if(action==='reset'){++loadId;data=initial;state=defaults();dragging=null;plan.hidden=true;layoutButton.setAttribute('aria-expanded','false');upload();sync();}
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
    e.preventDefault();canvas.hidden=true;badge.hidden=true;plan.hidden=true;figure.querySelector('img').hidden=false;controls.hidden=true;help.hidden=true;
    status.textContent='The graphics context was lost; the static drawing is shown. Reload to restore interaction.';
  });
  upload();sync();controls.hidden=false;help.hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;
  new ResizeObserver(requestDraw).observe(stage);
}
