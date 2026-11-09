#!/usr/bin/env python3
"""Original heuristic diagrams for the 2026-11-06 author survey.

No mesh solves a soliton or evolution PDE. The remaining interactive meshes illustrate
local geometry/topology only; the other drawings are labeled construction diagrams.
Source figures and PDFs are not copied. Run with Python's standard library.
"""
import json, math
from pathlib import Path
from xml.etree import ElementTree as ET
from generate_expander_schematics import canvas, text, path, curve, line, card, el, save, ACCENT, MUTED, INK, PALE
OUT=Path(__file__).resolve().parents[1]/'site/assets/solitons'
TAU=2*math.pi

def heading(title, subtitle='Heuristic schematic · no geometric PDE is solved'):
 s=canvas(title,subtitle);text(s,24,33,title,22,weight=650);text(s,24,59,subtitle,14,fill=MUTED);return s

def finish(s,name,lines):
 for i,t in enumerate(lines):text(s,24,367+i*23,t,14,fill=MUTED)
 save(name+'.svg',s)

def mesh(name,f,nu,nv,ur,vr,description):
 vertices=[list(f(ur[0]+(ur[1]-ur[0])*i/nu,vr[0]+(vr[1]-vr[0])*j/nv)) for i in range(nu+1) for j in range(nv+1)]
 faces=[]
 for i in range(nu):
  for j in range(nv):
   k=i*(nv+1)+j;faces.extend([[k,k+nv+1,k+nv+2],[k,k+nv+2,k+1]])
 data=dict(name=name,vertices=vertices,faces=faces,paths=[],status='schematic',description=description,view={'pitch':1.1 if name=='translating-annuloids' else .48})
 (OUT/(name+'.json')).write_text(json.dumps(data,separators=(',',':'))+'\n')
 # Fixed printable view shares the exact mesh used by the generic reader viewer.
 yaw,pitch=.64,data['view']['pitch']; q=[]
 for x,y,z in vertices:
  h=x*math.cos(yaw)-y*math.sin(yaw);d=x*math.sin(yaw)+y*math.cos(yaw)
  q.append((h,z*math.cos(pitch)-d*math.sin(pitch),z*math.sin(pitch)+d*math.cos(pitch)))
 lo=[min(p[i] for p in q) for i in range(2)];hi=[max(p[i] for p in q) for i in range(2)]
 scale=min(560/(hi[0]-lo[0]),265/(hi[1]-lo[1]));xy=[(320+scale*(p[0]-(lo[0]+hi[0])/2),207-scale*(p[1]-(lo[1]+hi[1])/2)) for p in q]
 s=heading(description)
 for face in sorted(faces,key=lambda f:sum(q[i][2] for i in f)):
  a,b,c=[q[i] for i in face];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];norm=math.sqrt(sum(x*x for x in normal));shade=.45+.5*abs(sum(a*b for a,b in zip(normal,[.3,.5,.8]))/(norm or 1));rgb=tuple(int(b*shade+63*(1-shade)) for b in [67,139,169])
  el(s,'polygon',points=' '.join(f'{xy[i][0]:.2f},{xy[i][1]:.2f}' for i in face),fill='rgb'+str(rgb),stroke='#24566b',stroke_width='.3',stroke_opacity='.2')
 finish(s,name,['Rotate and zoom in the reader to inspect this illustrative mesh.','Truncation edges are display boundaries; no time evolution is asserted.'])


def mountain():
 s=heading('An expander between two stable barriers')
 card(s,24,80,592,260)
 for k,(h,label,color) in enumerate([(38,'Γ− : strictly stable',MUTED),(82,'Γ₀ : intervening expander',ACCENT),(126,'Γ+ : strictly stable','#b06a35')]):
  pts=[(x,299-.002*(x-320)**2-h*math.exp(-((x-320)/160)**2)) for x in range(55,586,3)]
  curve(s,pts,stroke=color,width=3);text(s,340,289-h,label,14,fill=color)
 finish(s,'mountain-pass-expanders',['Symbolic ordering only; all three approach the same prescribed cone.','Smooth construction: 2 ≤ n ≤ 6. Instability requires the genericity hypothesis.'])

def highgenus():
 # Maintained by generate_high_genus_expander_geometry.py (mesh + slice plate).
 # Do not overwrite the reviewed topology illustration with the old symbols.
 if not (OUT/'high-genus-expanders.svg').exists():
  raise RuntimeError('Run scripts/generate_high_genus_expander_geometry.py first')


def knot():
 # The reviewed surface model has its own generator and scientific dependencies.
 # Never replace it with the superseded one-dimensional spine-only drawing.
 for name in ['knotted-expanders.svg','knotted-expanders.json','knotted-expander-construction.svg']:
  if not (OUT/name).is_file():
   raise FileNotFoundError('Run scripts/generate_knotted_geometry.py to restore '+name)


def perturbation():
 # The reviewed Costa mesh and time plate have dedicated generators.
 for name in ['minimal-ancient-flows.svg','minimal-ancient-flows.json']:
  if not (OUT/name).is_file():
   raise FileNotFoundError('Run generate_minimal_ancient_geometry.py and generate_minimal_ancient_plate.mjs first')


def pancakes():
 from generate_stacked_pancakes import main as draw_pancakes
 draw_pancakes()

def spiral():
 # Keep the old batch entry point from overwriting the source-based time sequence.
 import subprocess
 subprocess.run(['node', str(Path(__file__).with_name('generate_ancient_spiral_geometry.mjs'))], check=True)


def chains():
 # The time-resolved numerical illustration is owned by its dedicated generator.
 # This schematic-only command does not regenerate the numerical PDE data.
 # Regeneration: python3 scripts/generate_reaper_flow.py --audit
 # Leave its SVG intact rather than restoring the obsolete hand-drawn path.
 if not (OUT/'grim-reaper-chains.svg').is_file():
  raise FileNotFoundError('Run scripts/generate_reaper_flow.py first')


def main():
 mountain();highgenus();knot();perturbation();pancakes();spiral();chains()
 # The numerical time sequence is maintained by generate_hh_ancient_ovals.py.
 if not (OUT/'hh-ancient-ovals-audit.json').is_file():
  raise FileNotFoundError('Run scripts/generate_hh_ancient_ovals.py first')
 # Preserve the numerical PDE time sequence maintained by generate_reapernoid.py.
 if not (OUT/'reapernoid.json').exists():
  raise FileNotFoundError('Run generate_reapernoid.py and generate_reapernoid_plates.mjs first')
 mesh('translating-helicoids',lambda u,v:(.4*v+u*math.sin(math.pi*v/2),v,u*math.cos(math.pi*v/2)+.15*u*u),34,70,(-2,2),(-4,4),'Helicoid-like strip arrangement')
 def annulus(u,v):
  x=1.2*math.cosh(u)*math.cos(v);q=.8*math.cosh(u)*math.sin(v);y=1.6*math.tanh(q);z=.16*x*x+2*math.log(math.cosh(q))+.55*u;return (x,y,z)
 mesh('translating-annuloids',annulus,48,60,(-1.5,1.5),(0,TAU),'Annuloid: heuristic two-sheet neck model')
 print('Generated 12 schematic figures and 4 interactive meshes.')
if __name__=='__main__':main()
