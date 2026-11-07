#!/usr/bin/env python3
"""Original heuristic diagrams for the 2026-11-06 author survey.

No mesh solves a soliton or evolution PDE. The four interactive meshes illustrate
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

def scherk():
 s=heading('Scherk translators: a reflected graph')
 pts=[(145,270),(420,270),(505,115),(230,115)];el(s,'polygon',points=' '.join(f'{x},{y}' for x,y in pts),fill=PALE,stroke=ACCENT,stroke_width=3)
 for x,y in pts:line(s,x,y-26,x,y+26,stroke='#c48043',width=4)
 text(s,315,102,'−∞',22,anchor='middle');text(s,280,302,'−∞',22,anchor='middle');text(s,160,192,'+∞',22);text(s,495,205,'+∞',22)
 text(s,315,195,'translator graph u',19,anchor='middle');text(s,315,223,'0 < w < π,  0 < α < π',15,anchor='middle')
 finish(s,'scherk-translators',['Downward source convention; reflect height for upward translation.','Orange lines are reflection axes. Repeating pieces gives infinite genus.'])

def mountain():
 s=heading('An expander between two stable barriers')
 card(s,24,80,592,260)
 for k,(h,label,color) in enumerate([(38,'Γ− : strictly stable',MUTED),(82,'Γ₀ : intervening expander',ACCENT),(126,'Γ+ : strictly stable','#b06a35')]):
  pts=[(x,299-.002*(x-320)**2-h*math.exp(-((x-320)/160)**2)) for x in range(55,586,3)]
  curve(s,pts,stroke=color,width=3);text(s,340,289-h,label,14,fill=color)
 finish(s,'mountain-pass-expanders',['Symbolic ordering only; all three approach the same prescribed cone.','Smooth construction: 2 ≤ n ≤ 6. Instability requires the genericity hypothesis.'])

def highgenus():
 s=heading('One cone, outgoing surfaces of large genus')
 for x in [160,320,480]:
  path(s,f'M{x-24},92 L{x-14},160 L{x+14},160 L{x+24},92',fill=PALE,width=2)
  text(s,x,85,'conical end',14,anchor='middle')
 path(s,'M110,160 Q100,305 320,320 Q540,305 530,160 Z',fill=PALE,width=2)
 for x,y in [(170,205),(235,240),(315,205),(395,240),(470,205)]:
  el(s,'ellipse',cx=x,cy=y,rx=21,ry=11,fill='white',stroke=ACCENT,stroke_width=2)
 text(s,320,292,'handle symbols:  g = pᵃ k − 1',17,anchor='middle')
 finish(s,'high-genus-expanders',['The same cone has three link components; p is odd prime and a ≥ 0.','Handles are schematic symbols. The actual surfaces have no closed formula.'])

def knot():
 s=heading('A trefoil core with three end attachments')
 # Projection of an original standard trefoil; white under-strokes show overpasses.
 points=[]
 for i in range(421):
  t=TAU*i/420;points.append((320+64*(math.sin(t)+2*math.sin(2*t)),210+40*(math.cos(t)-2*math.cos(2*t)),math.sin(3*t)))
 curve(s,[p[:2] for p in points],width=5)
 # Redraw only actual overcrossings, leaving the rest of the knot continuous.
 for i in range(420):
  a,b=points[i:i+2];u=(b[0]-a[0],b[1]-a[1])
  for j in range(i+30,420):
   if min(j-i,420-(j-i))<30:continue
   c,d=points[j:j+2];v=(d[0]-c[0],d[1]-c[1]);det=u[0]*v[1]-u[1]*v[0]
   if abs(det)<1e-8:continue
   delta=(c[0]-a[0],c[1]-a[1]);t=(delta[0]*v[1]-delta[1]*v[0])/det;h=(delta[0]*u[1]-delta[1]*u[0])/det
   if 0<t<1 and 0<h<1:
    k=i if a[2]+t*(b[2]-a[2])>c[2]+h*(d[2]-c[2]) else j
    arc=[points[q%420][:2] for q in range(k-5,k+7)]
    curve(s,arc,stroke='white',width=12);curve(s,arc,width=5)
 for x,y,tx,ty,label in [(320,150,320,86,'end 1'),(169,240,78,285,'end 2'),(471,240,567,285,'end 3')]:
  line(s,x,y,tx,ty,stroke='#b06a35',width=2,stroke_dasharray='5 4');text(s,tx,ty-6,label,15,anchor='middle')
 finish(s,'knotted-expanders',['The curve is a knot spine, not the two-dimensional expander.','Thicken the core, puncture three disks, and attach annular ends.'])

def perturbation():
 s=heading('Ancient flows on either side of a minimal M')
 for shift,label,color in [(-37,'Mₜ⁺', '#b06a35'),(0,'M',MUTED),(37,'Mₜ⁻',ACCENT)]:
  pts=[(x,205+shift+31*math.sin((x-120)/85)) for x in range(75,566,2)];curve(s,pts,stroke=color,width=3);text(s,569,pts[-1][1],label,18,fill=color)
 for x in [160,320,480]:line(s,x,163,x,205,stroke=MUTED,width=1,marker_end='url(#arrow)');line(s,x,249,x,211,stroke=MUTED,width=1,marker_end='url(#arrow)')
 text(s,320,120,'t → −∞: opposite-side convergence',18,anchor='middle')
 finish(s,'minimal-ancient-flows',['Local normal-graph diagram only: the Costa example has genus 1 and 3 ends.','No global minimal-surface profile or finite-time ancient slice is computed.'])

def pancakes():
 from generate_stacked_pancakes import main as draw_pancakes
 draw_pancakes()

def spiral():
 s=heading('Compact ancient spiral: curve and cap')
 # A thin tubular ribbon around a finite spiral, closed by semicircular end caps.
 n=560;ts=[.4+4.6*math.pi*i/n for i in range(n+1)];centers=[(320+31*math.sqrt(t)*math.cos(t),207+31*math.sqrt(t)*math.sin(t)) for t in ts];width=4
 normals=[]
 for t in ts:
  dx=31*(math.cos(t)/(2*math.sqrt(t))-math.sqrt(t)*math.sin(t));dy=31*(math.sin(t)/(2*math.sqrt(t))+math.sqrt(t)*math.cos(t));norm=math.hypot(dx,dy);normals.append((-dy/norm,dx/norm))
 upper=[(p[0]+width*v[0],p[1]+width*v[1]) for p,v in zip(centers,normals)];lower=[(p[0]-width*v[0],p[1]-width*v[1]) for p,v in zip(centers,normals)]
 curve(s,upper+lower[::-1]+[upper[0]],width=2)
 p=centers[-1];el(s,'circle',cx=p[0],cy=p[1],r=6,fill='#b06a35');text(s,482,125,'closing cap',15);line(s,480,130,p[0]+5,p[1],stroke='#b06a35',width=1)
 finish(s,'ancient-spiral-curves',['A closed embedded spiral cartoon; the true cap is grim-reaper-shaped.','The √θ spiral used to draw this diagram is not the exact rotating soliton.'])

def chains():
 s=heading('Three grim-reaper turns: an eternal curve')
 for i,y in enumerate([98,169,240,311]):
  line(s,45,y,595,y,stroke=MUTED,width=1,stroke_dasharray='6 5');text(s,55,y-7,'a'+str(3-i),14)
 path(s,'M575,307 C360,307 130,300 130,274 C130,247 355,242 452,221 C510,208 510,190 452,179 C355,158 130,161 130,134 C130,107 360,102 575,102',width=3)
 text(s,320,135,'G₃',18,anchor='middle');text(s,320,206,'G₂',18,anchor='middle');text(s,320,277,'G₁',18,anchor='middle')
 finish(s,'grim-reaper-chains',['Monotone asymptote heights give the embedded graphical subfamily.','The joins are heuristic; the full glued solution is not an explicit formula.'])

def main():
 scherk();mountain();highgenus();knot();perturbation();pancakes();spiral();chains()
 mesh('hh-ancient-ovals',lambda u,v:(3*math.cos(u),math.sin(u)*math.cos(v),math.sin(u)*math.sin(v)),38,54,(0,math.pi),(0,TAU),'Ancient oval: a heuristic elongated slice')
 mesh('reapernoid',lambda u,v:((1+.6*u*u)*math.cos(v),(1+.6*u*u)*math.sin(v),u+.2*math.tanh(u)),50,54,(-2,2),(0,TAU),'Reapernoid: heuristic annular slice in R3')
 mesh('translating-helicoids',lambda u,v:(.4*v+u*math.sin(math.pi*v/2),v,u*math.cos(math.pi*v/2)+.15*u*u),34,70,(-2,2),(-4,4),'Helicoid-like strip arrangement')
 def annulus(u,v):
  x=1.2*math.cosh(u)*math.cos(v);q=.8*math.cosh(u)*math.sin(v);y=1.6*math.tanh(q);z=.16*x*x+2*math.log(math.cosh(q))+.55*u;return (x,y,z)
 mesh('translating-annuloids',annulus,48,60,(-1.5,1.5),(0,TAU),'Annuloid: heuristic two-sheet neck model')
 print('Generated 12 schematic figures and 4 interactive meshes.')
if __name__=='__main__':main()
