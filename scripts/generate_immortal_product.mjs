// Reproduce the static fallback using exactly the viewer's schematic geometry.
import {writeFile} from 'node:fs/promises';
import {scene,sceneSVG,surfaceMesh,STAGES} from '../site/assets/immortal-product-viewer.mjs';
const base=new URL('../site/assets/solitons/',import.meta.url);
await writeFile(new URL('immortal-product.svg',base),sceneSVG(scene()));
const mesh=surfaceMesh(STAGES[0],true,32,24);
await writeFile(new URL('immortal-product.json',base),JSON.stringify({
  kind:'immortal-product-schematic',status:'schematic',vertices:mesh.vertices,faces:mesh.faces,paths:[],
  source:'Chen–Sun, arXiv:2402.04521v2, §2.1, Definition 3.10, Theorems 3.12 and 3.17.',
  model:'Qualitative profiles; not PDE solutions or a claimed asymptotic expansion. No numerical time or decay rate.',
  drawingMap:'(p,y) ↦ (1+2y)p for n=2. Not an isometry; not Euclidean MCF.',
  stages:STAGES,
})+'\n');
console.log('Generated immortal-product.svg and immortal-product.json');
