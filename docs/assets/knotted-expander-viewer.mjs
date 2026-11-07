// A trefoil tube and three ends. This viewer does not solve the expander equation.
export function knottedNormals(vertices,faces){
  const normals=vertices.map(()=>[0,0,0]);
  for(const [a,b,c] of faces){
    const u=vertices[b].map((x,i)=>x-vertices[a][i]),v=vertices[c].map((x,i)=>x-vertices[a][i]);
    const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
    for(const j of [a,b,c])for(let i=0;i<3;i++)normals[j][i]+=n[i];
  }
  return normals.map(n=>{const length=Math.hypot(...n)||1;return n.map(x=>x/length);});
}

// Line segments on the actual triangle/plane intersection, not floating circles.
export function knottedRims(vertices,faces,axes,limit){
  const lines=[];
  for(const axis of axes){
    const distance=vertices.map(p=>p.reduce((sum,x,i)=>sum+x*axis[i],-limit));
    for(const face of faces){
      const hits=[];
      for(let i=0;i<3;i++){
        const a=face[i],b=face[(i+1)%3],da=distance[a],db=distance[b];
        if(Math.abs(da)<1e-6)hits.push(vertices[a]);
        if(da*db<0&&Math.abs(da)>=1e-6&&Math.abs(db)>=1e-6){
          const t=da/(da-db);hits.push(vertices[a].map((x,k)=>x+t*(vertices[b][k]-x)));
        }
      }
      if(hits.length===2)lines.push(...hits);
    }
  }
  return lines;
}

export function initKnottedFigure(figure,data){
  const canvas=figure.querySelector('canvas'),gl=canvas.getContext('webgl',{antialias:true,alpha:false});
  if(!gl)throw new Error('WebGL unavailable');
  const vertex=`attribute vec3 position,normal,color;uniform mat3 rotation;uniform vec2 scale;
    varying vec3 point,norm,tint;
    void main(){point=position;norm=rotation*normal;tint=color;vec3 p=rotation*position;
      gl_Position=vec4(p.x*scale.x,p.y*scale.y-.06,-p.z/20.0,1.0);}`;
  const fragment=`precision mediump float;varying vec3 point,norm,tint;uniform float limit;uniform bool lines,clipped;
    void main(){if(clipped&&(point.y>limit||.8660254038*point.x-.5*point.y>limit||-.8660254038*point.x-.5*point.y>limit))discard;
      if(lines){gl_FragColor=vec4(.12,.24,.30,1.0);return;}
      vec3 n=normalize(norm);if(!gl_FrontFacing)n=-n;
      float light=.48+.5*max(0.0,dot(n,normalize(vec3(-.35,.55,.80))));
      float shine=pow(max(0.0,dot(n,normalize(vec3(-.18,.28,1.0)))),40.0);
      gl_FragColor=vec4(tint*light+vec3(.08)*shine,1.0);}`;
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Shader compilation failed');return s;}
  const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));
  gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Shader link failed');gl.useProgram(program);
  const uniforms=Object.fromEntries(['rotation','scale','limit','lines','clipped'].map(k=>[k,gl.getUniformLocation(program,k)]));
  const attributes=Object.fromEntries(['position','normal','color'].map(k=>[k,gl.getAttribLocation(program,k)]));
  function buffer(array,target=gl.ARRAY_BUFFER){const b=gl.createBuffer();gl.bindBuffer(target,b);gl.bufferData(target,array,gl.STATIC_DRAW);return b;}
  function mesh(model){return {position:buffer(new Float32Array(model.vertices.flat())),normal:buffer(new Float32Array(knottedNormals(model.vertices,model.faces).flat())),color:buffer(new Float32Array(model.vertexColors.flat().map(x=>x/255))),indices:buffer(new Uint16Array(model.faces.flat()),gl.ELEMENT_ARRAY_BUFFER),count:model.faces.length*3,wire:buffer(new Uint16Array(model.faces.flatMap(([a,b,c])=>[a,b,b,c,c,a])),gl.ELEMENT_ARRAY_BUFFER)};}
  if(Math.max(data.vertices.length,data.core.vertices.length)>65535)throw new Error('Mesh too large');
  const full=mesh(data),core=mesh(data.core),rim=gl.createBuffer();
  const spinePoints=[...data.spine,data.spine[0]],spine=buffer(new Float32Array(spinePoints.flat()));
  const stage=figure.querySelector('.soliton-stage'),controls=figure.querySelector('.soliton-controls');
  const status=figure.querySelector('.soliton-status'),help=figure.querySelector('.soliton-help');
  const defaults=()=>({yaw:data.view.yaw,pitch:data.view.pitch,zoom:1,mode:'surface',length:1.8,wire:false});
  let state=defaults(),scheduled=false,dragging=null,rimCount=0;
  const badge=document.createElement('p');badge.className='knotted-view-label';stage.append(badge);
  const labels=data.endAxes.map((_,i)=>{const label=document.createElement('span');label.className='knotted-end-label';label.textContent=String(i+1);label.setAttribute('aria-hidden','true');stage.append(label);return label;});
  const viewLabel=document.createElement('label');viewLabel.textContent='View ';
  const view=document.createElement('select');view.setAttribute('aria-label','Trefoil construction view');
  for(const [value,title] of [['surface','Surface and ends'],['punctured','Three punctures'],['core','Closed trefoil tube'],['spine','Knot spine']]){const option=document.createElement('option');option.value=value;option.textContent=title;view.append(option);}
  viewLabel.append(view);controls.prepend(viewLabel);
  const lengthLabel=document.createElement('label');lengthLabel.textContent='End length shown ';
  const length=document.createElement('input');length.type='range';length.min='.4';length.max='2.2';length.step='.05';length.value=String(state.length);length.setAttribute('aria-label','End length shown');lengthLabel.append(length);controls.append(lengthLabel);
  function limit(){return state.mode==='punctured'?3.35:3+state.length;}
  function updateRim(){const points=knottedRims(data.vertices,data.faces,data.endAxes,limit());rimCount=points.length;gl.bindBuffer(gl.ARRAY_BUFFER,rim);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(points.flat()),gl.STATIC_DRAW);}
  function bindMesh(model){for(const key of ['position','normal','color']){gl.bindBuffer(gl.ARRAY_BUFFER,model[key]);gl.enableVertexAttribArray(attributes[key]);gl.vertexAttribPointer(attributes[key],3,gl.FLOAT,false,0,0);}}
  function bindLine(b){gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.enableVertexAttribArray(attributes.position);gl.vertexAttribPointer(attributes.position,3,gl.FLOAT,false,0,0);for(const key of ['normal','color']){gl.disableVertexAttribArray(attributes[key]);gl.vertexAttrib3f(attributes[key],0,0,1);}}
  function draw(){
    scheduled=false;const box=stage.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2),w=Math.round(box.width*dpr),h=Math.round(box.height*dpr);if(!w||!h)return;
    if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}
    gl.viewport(0,0,w,h);gl.clearColor(247/255,250/255,251/255,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    const cy=Math.cos(state.yaw),sy=Math.sin(state.yaw),cp=Math.cos(state.pitch),sp=Math.sin(state.pitch);
    gl.uniformMatrix3fv(uniforms.rotation,false,new Float32Array([cy,-sy*sp,sy*cp,-sy,-cy*sp,cy*cp,0,cp,sp]));
    const closed=state.mode==='core'||state.mode==='spine',radius=closed?3.7:5.7;
    const scale=Math.min(w*.46/radius,h*.42/(closed?3.7:4.9))*state.zoom;
    gl.uniform2f(uniforms.scale,2*scale/w,2*scale/h);gl.uniform1f(uniforms.limit,limit());gl.uniform1i(uniforms.clipped,!closed);
    gl.enable(gl.DEPTH_TEST);gl.frontFace(gl.CW);gl.disable(gl.CULL_FACE);
    if(state.mode==='spine'){
      gl.uniform1i(uniforms.lines,true);bindLine(spine);gl.drawArrays(gl.LINE_STRIP,0,spinePoints.length);
    }else{
      const model=closed?core:full;bindMesh(model);gl.uniform1i(uniforms.lines,false);
      gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,model.indices);gl.drawElements(gl.TRIANGLES,model.count,gl.UNSIGNED_SHORT,0);gl.disable(gl.POLYGON_OFFSET_FILL);
      gl.uniform1i(uniforms.lines,true);
      if(state.wire){gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,model.wire);gl.drawElements(gl.LINES,model.count*2,gl.UNSIGNED_SHORT,0);}
      if(!closed){gl.uniform1i(uniforms.clipped,false);bindLine(rim);gl.drawArrays(gl.LINES,0,rimCount);}
    }
    labels.forEach((label,i)=>{
      label.hidden=closed;const [x,y,z]=data.endAxes[i].map(v=>v*(limit()+.25)),a=x*cy-y*sy,b=x*sy+y*cy;
      label.style.left=`${box.width/2+scale/dpr*a}px`;label.style.top=`${box.height*.53-scale/dpr*(z*cp-b*sp)}px`;
    });
    canvas.dataset.view=state.mode;canvas.dataset.zoom=state.zoom.toFixed(3);canvas.dataset.rotation=`${state.yaw.toFixed(3)},${state.pitch.toFixed(3)}`;canvas.dataset.endLength=String(state.length);canvas.dataset.mesh=String(state.wire);
  }
  function requestDraw(){if(!scheduled){scheduled=true;requestAnimationFrame(draw);}}
  function sync(){
    view.value=state.mode;length.value=String(state.length);length.disabled=state.mode!=='surface';
    figure.querySelector('[data-view-action="wire"]').setAttribute('aria-pressed',String(state.wire));
    figure.querySelector('[data-view-action="wire"]').disabled=state.mode==='spine';
    const titles={surface:'Genus 1 · three annular ends',punctured:'Genus 1 · three boundary circles',core:'Auxiliary closed trefoil tube',spine:'Auxiliary trefoil curve'};
    badge.textContent=titles[state.mode]+' · schematic';
    canvas.setAttribute('aria-label',`${titles[state.mode]}. Topology illustration, not a computed self-expander. Arrow keys rotate; plus and minus zoom.`);
    help.textContent='Drag to rotate; + / − zoom. Change views to see the knot, its tube, the three punctures, and the attached ends.';
    status.textContent=state.mode==='surface'?'The numbered rims are display cuts, not boundaries of the complete expander. End length changes only how much of this fixed schematic is shown. The flaring profile is illustrative.':state.mode==='punctured'?'Three end collars cut near the trefoil tube expose three holes. Attaching annuli preserves genus one. These are artificial display boundaries.':state.mode==='core'?'The boundary of a tubular neighborhood of the trefoil is a knotted torus. This closed auxiliary surface is not an expander.': 'The one-dimensional trefoil records the knot type. The expander is a two-dimensional surface, not this curve.';
    updateRim();requestDraw();
  }
  view.addEventListener('change',()=>{state.mode=view.value;state.zoom=1;sync();});
  length.addEventListener('input',()=>{state.length=Number(length.value);updateRim();requestDraw();});
  function zoom(f){state.zoom=Math.max(.5,Math.min(3,state.zoom*f));requestDraw();}
  for(const b of figure.querySelectorAll('[data-view-action]'))b.addEventListener('click',()=>{
    const action=b.dataset.viewAction;if(action==='in')zoom(1.2);if(action==='out')zoom(1/1.2);
    if(action==='wire'){state.wire=!state.wire;sync();}if(action==='reset'){state=defaults();dragging=null;sync();}
  });
  canvas.addEventListener('pointerdown',e=>{dragging={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!dragging)return;state.yaw+=(e.clientX-dragging.x)*.009;state.pitch+=(e.clientY-dragging.y)*.009;dragging={x:e.clientX,y:e.clientY};requestDraw();});
  for(const name of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(name,()=>{dragging=null;});
  canvas.addEventListener('keydown',e=>{const keys={ArrowLeft:()=>state.yaw-=.12,ArrowRight:()=>state.yaw+=.12,ArrowUp:()=>state.pitch-=.12,ArrowDown:()=>state.pitch+=.12,'+':()=>zoom(1.2),'=':()=>zoom(1.2),'-':()=>zoom(1/1.2)};if(keys[e.key]){e.preventDefault();keys[e.key]();requestDraw();}});
  canvas.addEventListener('wheel',e=>{if(document.activeElement!==canvas)return;e.preventDefault();zoom(Math.exp(-e.deltaY*.0015));},{passive:false});
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();canvas.hidden=true;badge.hidden=true;labels.forEach(l=>l.hidden=true);figure.querySelector('img').hidden=false;controls.hidden=true;help.hidden=true;status.textContent='The graphics context was lost; the static drawing is shown. Reload to restore interaction.';});
  sync();controls.hidden=false;help.hidden=false;figure.querySelector('img').hidden=true;canvas.hidden=false;
  new ResizeObserver(requestDraw).observe(stage);requestDraw();
}
