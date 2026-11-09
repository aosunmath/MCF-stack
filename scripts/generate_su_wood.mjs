// Regenerate the exact sampled profile and its accessible, printable time panels.
import {writeFileSync} from 'node:fs';
import {profileMesh,snapshotSVG,DOMAIN} from '../site/assets/su-wood-viewer.mjs';
const root=new URL('../site/assets/solitons/',import.meta.url);
writeFileSync(new URL('su-wood-stationary.svg',root),snapshotSVG());
writeFileSync(new URL('su-wood-stationary.json',root),JSON.stringify({
  name:'Su–Wood stationary Lawlor-profile product',kind:'su-wood-exact-stationary',
  status:'exact',ambient_dimension:6,intrinsic_dimension:3,profile_dimension:2,
  source:'https://arxiv.org/html/2507.01345v1#S5.SS3',
  formula:'X=(Z cos(theta), Z sin(theta), W); Z=mu(cosh(b)+i p); a=asinh(p); W=(mu^2 cosh(a+b)-cosh(a-b))/2+i((mu^2-1)a+(mu^2+1)b)/2',
  parameters:{m:3,mu1:1,mu2:1,phi:0},domain:DOMAIN,time_interval:'all real t',
  projection:'(Im Z, Re W, Im W); sampled profile, not the full three-manifold',
  ...profileMesh()
})+'\n');
