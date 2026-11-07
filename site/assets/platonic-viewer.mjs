// Ketover, arXiv:1602.07271v1, pp. 2–3 and 9–10. Sweepout schematics only.
import {initSphericalDoublingFigure} from './spherical-doubling-viewer.mjs';

export const PLATONIC_SOLIDS=[
  ['tetrahedron','Tetrahedron',4],['cube','Cube',6],['octahedron','Octahedron',8],
  ['dodecahedron','Dodecahedron',12],['icosahedron','Icosahedron',20],
];

export function platonicModelUrl(base,solid){
  if(!PLATONIC_SOLIDS.some(([key])=>key===solid))throw new Error('Unsupported Platonic solid');
  return base.replace(/ketover-platonic\.json$/,`ketover-platonic${solid==='cube'?'':'-'+solid}.json`);
}

export function initPlatonicFigure(figure,initial){
  initSphericalDoublingFigure(figure,initial,{
    key:data=>data.solid,
    choices:PLATONIC_SOLIDS.map(([key,name,n])=>[key,`${name} · genus ${n-1}`]),
    selectLabel:'Platonic solid',
    modelUrl:platonicModelUrl,
    badge:data=>`${data.necks} necks · genus ${data.genus}`,
    aria:data=>`Ketover ${data.solid} sweepout schematic: two spherical sheets joined through ${data.necks} face-center necks, genus ${data.genus}`,
    status:data=>`${data.necks} face-center necks join two punctured spheres: genus ${data.necks} − 1 = ${data.genus}. This is a compact sweepout model. The paper does not determine compactness or ends of the limiting shrinker.`,
  });
}
