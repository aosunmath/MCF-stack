import fs from 'node:fs';
import {snapshotSVG} from '../site/assets/minimal-ancient-viewer.mjs';
const base=new URL('../site/assets/solitons/',import.meta.url);
const data=JSON.parse(fs.readFileSync(new URL('minimal-ancient-flows.json',base),'utf8'));
fs.writeFileSync(new URL('minimal-ancient-flows.svg',base),snapshotSVG(data));
console.log('Wrote four Costa time views from the same model as the reader.');
