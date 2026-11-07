import fs from 'node:fs';
import {surfacePlate,profilePlate} from '../site/assets/reapernoid-viewer.mjs';
const base=new URL('../site/assets/solitons/',import.meta.url);
const data=JSON.parse(fs.readFileSync(new URL('reapernoid.json',base),'utf8'));
fs.writeFileSync(new URL('reapernoid.svg',base),surfacePlate(data));
fs.writeFileSync(new URL('reapernoid-limits.svg',base),profilePlate(data));
console.log('Wrote the surface time sequence and dimension-dependent profile comparison.');
