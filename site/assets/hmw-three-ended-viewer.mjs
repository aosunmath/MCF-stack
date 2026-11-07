// Original HMW Figure 7 topology model; no shrinker PDE is solved.
// Shared rendering helpers do not identify distinct mathematical constructions.
import {shaoZouNormals as meshNormals, shaoZouGap as displayGap} from './shao-zou-viewer.mjs';
export const HMW_THREE_PARAMETERS=[1,3,7];
export function hmwThreeModelUrl(base,g){
  if(g!=='limit'&&!HMW_THREE_PARAMETERS.includes(g))throw new Error('Unsupported model parameter');
  return base.replace(/hmw-three-ended\.json$/,g==='limit'?'hmw-three-plane-limit.json':`hmw-three-ended${g===3?'':`-${g}`}.json`);
}
export function hmwThreeSites(g,radius=1){
  return [0,1].map(gap=>Array.from({length:g+1},(_,j)=>{
    const t=(2*j+1.5-gap)*Math.PI/(g+1);
    return [radius*Math.cos(t),radius*Math.sin(t)];
  }));
}

export function initHmwThreeFigure(figure,initial){
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
  const cache=new Map([[initial.g,initial]]);
  const defaults=()=>({yaw:initial.view.yaw,pitch:initial.view.pitch,zoom:1,cutaway:false,limit:false,wire:false,gap:initial.view.gap});
  let state=defaults();
  const badge=document.createElement('p');badge.className='shao-zou-view-label';stage.append(badge);
  function upload(){
    if(data.vertices.length>65535)throw new Error('Illustration exceeds index limit');
    const vertices=displayGap(data.vertices,state.gap);
    const arrays={position:vertices,normal:meshNormals(vertices,data.faces),
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
    const heights=data.vertices.filter(p=>state.limit||!state.cutaway||p[1]<=0).map(([x,y,z])=>z*state.gap*cp-(x*sy+y*cy)*sp);
    const low=Math.min(...heights),high=Math.max(...heights),extent=(high-low)/2;
    const scale=Math.min(w*.46/data.view.radius,h*.40/Math.max(.5,extent))*state.zoom;
    gl.uniform1f(uniforms.offset,(high+low)/2);
    gl.uniform2f(uniforms.scale,2*scale/w,2*scale/h);gl.uniform1i(uniforms.cutaway,(state.cutaway&&!state.limit));gl.uniform1i(uniforms.lines,false);
    gl.enable(gl.DEPTH_TEST);gl.frontFace(gl.CW);gl.disable(gl.CULL_FACE);gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,indexBuffer);gl.drawElements(gl.TRIANGLES,indices.length,gl.UNSIGNED_SHORT,0);
    gl.disable(gl.POLYGON_OFFSET_FILL);
    if(state.wire){gl.uniform1i(uniforms.lines,true);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,meshBuffer);gl.drawElements(gl.LINES,meshIndices.length,gl.UNSIGNED_SHORT,0);}
    canvas.dataset.g=String(data.g??'limit');
    canvas.dataset.genus=String(data.genus);canvas.dataset.view=state.limit?'limit':state.cutaway?'cutaway':'surface';
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
  const gSelect=chooser('Model g',HMW_THREE_PARAMETERS);
  for(const option of gSelect.options)option.textContent=`${option.value} (genus ${2*Number(option.value)})`;
  const limitButton=document.createElement('button');limitButton.type='button';limitButton.textContent='Triple-plane limit';controls.append(limitButton);
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
    const svg=element('svg',{viewBox:'0 0 210 210',role:'img','aria-label':`Horizontal trace and alternating neck sites for g = ${data.g}. This is a plan, not a surface.`});
    svg.append(element('circle',{cx:108,cy:101,r:72,fill:'none',stroke:'#99adb5','stroke-dasharray':'4 4'}));
    const description=document.createElement('div');
    function line(text,color){const p=document.createElement('p');p.textContent=text;if(color)p.style.color=color;description.append(p);}
    const sites=hmwThreeSites(data.g,72);
    for(let j=0;j<=data.g;j++){
      const t=j*Math.PI/(data.g+1),x=88*Math.cos(t),y=88*Math.sin(t);
      svg.append(element('line',{x1:108-x,y1:101-y,x2:108+x,y2:101+y,stroke:'#58727e'}));
    }
    for(let group=0;group<2;group++){
      const color=group===0?'#508ba6':'#bd8c3f';
      for(const [x,y] of sites[group])svg.append(element('circle',{cx:108+x,cy:101-y,r:5,fill:color}));
      line(`${group===0?'Lower':'Upper'} gap: ${data.g+1} open necks`,color);
    }
    line(`Model genus: 2g = ${2*data.g}. Three sheets joined by ${2*(data.g+1)} necks.`);
    line(`Gray: the ${data.g+1} horizontal lines Qg. Neck sites alternate between their sectors.`);
    const note=document.createElement('p');note.className='shao-zou-plan-note';note.textContent='The trace is source-supported data; neck shapes, sites on the circle and circle radius are drawing choices.';
    plan.append(svg,description,note);
  }
  layoutButton.addEventListener('click',()=>{plan.hidden=!plan.hidden;layoutButton.setAttribute('aria-expanded',String(!plan.hidden));});
  let selectedG=initial.g;
  function sync(){
    gSelect.value=String(selectedG);gSelect.disabled=state.limit;gap.disabled=state.limit;
    gap.value=String(state.gap);output.textContent=`${state.gap.toFixed(2)}×`;
    cutButton.disabled=state.limit;layoutButton.disabled=state.limit;
    if(state.limit)plan.hidden=true;
    layoutButton.setAttribute('aria-expanded',String(!plan.hidden));
    cutButton.setAttribute('aria-pressed',String(state.cutaway));
    limitButton.setAttribute('aria-pressed',String(state.limit));
    limitButton.textContent=state.limit?'Return to surface':'Triple-plane limit';
    figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed',String(state.wire));
    badge.textContent=state.limit?'Limit: one plane, multiplicity 3':`Three ends · model genus ${data.genus} · ${state.cutaway?'cutaway':'full surface'} · schematic`;
    canvas.setAttribute('aria-label',state.limit?'Horizontal plane with multiplicity three, the large-genus limit.':`Hoffman–Martín–White topology schematic, model g ${data.g}, genus ${data.genus}, three ends; ${state.cutaway?'front half removed':'full surface'}. Arrow keys rotate; plus and minus zoom. Not a computed shrinker.`);
    help.textContent=state.limit?'Rotate the limiting plane. Multiplicity three is a weight on this one plane, not three distinct parallel planes.':'Drag to rotate; + / − zoom. Cutaway exposes the neck interiors. Gold, green and blue identify the three exterior sheets of one connected surface.';
    status.textContent=state.limit?'Theorem 43: as g → ∞, the limit is 3P; after a subsequence, convergence is smooth away from one circle. Its radius is not prescribed.':`Model g = ${data.g}, genus 2g = ${data.genus}. Theorem 43 proves three ends only for sufficiently large g; no threshold is specified. ${data.g===1?'Figure 7’s genus-two appearance is conjectural. ':''}Neck sizes, cone slopes and display separation are illustrative. Outer rims and cut edges are artificial.`;
    if(!state.limit)drawPlan();requestDraw();
  }
  async function changeModel(key){
    const id=++loadId;status.textContent='Loading the geometry view…';
    try{
      if(!cache.has(key)){
        const response=await fetch(hmwThreeModelUrl(figure.dataset.soliton,key));
        if(!response.ok)throw new Error('mesh unavailable');
        const next=await response.json();
        if(key==='limit'?next.kind!=='hmw-three-ended-limit':next.g!==key||next.kind!=='hmw-three-ended-schematic')throw new Error('Wrong model');
        cache.set(key,next);
      }
      if(id!==loadId)return;
      const previous=data;data=cache.get(key);
      try{upload();}catch(error){data=previous;upload();throw error;}
      state.limit=key==='limit';if(!state.limit)selectedG=key;
      sync();
    }catch{if(id===loadId){gSelect.value=String(selectedG);status.textContent='The requested model could not load; the previous valid view remains displayed.';}}
  }
  gSelect.addEventListener('change',()=>changeModel(Number(gSelect.value)));
  limitButton.addEventListener('click',()=>changeModel(state.limit?selectedG:'limit'));
  cutButton.addEventListener('click',()=>{state.cutaway=!state.cutaway;sync();});
  gap.addEventListener('input',()=>{state.gap=Number(gap.value);upload();sync();});
  function zoom(f){state.zoom=Math.max(.5,Math.min(3,state.zoom*f));requestDraw();}
  for(const b of figure.querySelectorAll('[data-view-action]'))b.addEventListener('click',()=>{
    const action=b.dataset.viewAction;
    if(action==='in')zoom(1.2);if(action==='out')zoom(1/1.2);
    if(action==='wire'){state.wire=!state.wire;sync();}
    if(action==='reset'){++loadId;data=initial;selectedG=initial.g;state=defaults();dragging=null;plan.hidden=true;layoutButton.setAttribute('aria-expanded','false');upload();sync();}
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
