// Reproduce the exact-coordinate fallback and the initial interactive mesh.
import {writeFileSync} from 'node:fs';
import {realSlice,snapshotSVG,SHRINK_TIMES,CUT_RADIUS} from '../site/assets/lee-wang-viewer.mjs';
const out=new URL('../site/assets/solitons/',import.meta.url);
writeFileSync(new URL('lw-quadric-shrinkers.svg',out),snapshotSVG());
writeFileSync(new URL('lw-quadric-shrinkers.json',out),JSON.stringify({
  name:'lw-quadric-shrinkers',kind:'lee-wang-exact-flow',status:'exact-slice',
  source:'Lee–Wang, arXiv:0802.0359v1, Theorem 1.1 and Propositions 2.1–2.2',
  ambientDimension:6,intrinsicDimension:3,sliceDimension:2,weights:[1,1,-1],
  snapshots:SHRINK_TIMES,cutRadius:CUT_RADIUS,...realSlice(-1)
})+'\n');
