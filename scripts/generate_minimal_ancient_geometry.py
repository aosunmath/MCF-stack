#!/usr/bin/env python3
"""Costa surface and a numerical *linearized* ancient-time illustration.

Original implementation of Melko (2010), eq. (17), using theta series.
The normal height is a Dirichlet Jacobi eigenmode on a truncated surface.
It is NOT a nonlinear Mramor--Payne flow or a computed global eigenfunction.
Requires numpy/scipy; geometry is fixed at the square-lattice normalization.
"""
import json
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import eigsh
from scipy.spatial import Delaunay
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'site/assets/solitons'
PI=np.pi

def elliptic(z):
    z=np.asarray(z,dtype=complex)
    # Reduce to a centered square; restore zeta's exact quasi-periods.
    a=np.floor(z.real+.5); b=np.floor(z.imag+.5); w=z-a-1j*b
    v=PI*w; theta=[np.zeros_like(w) for _ in range(4)]
    for n in range(9):
        k=2*n+1; c=2*(-1)**n*np.exp(-PI*(n+.5)**2)
        theta[0]+=c*np.sin(k*v); theta[1]+=c*k*np.cos(k*v)
        theta[2]-=c*k*k*np.sin(k*v); theta[3]-=c*k*k*k*np.cos(k*v)
    s=theta[1]/theta[0]; q=theta[2]/theta[0]
    zeta=PI*w+PI*s+PI*a-1j*PI*b
    wp=-PI-PI**2*(q-s*s)
    dwp=-PI**3*(theta[3]/theta[0]-3*q*s+2*s**3)
    return zeta,wp,dwp

def costa(z):
    zz,p,dp=elliptic(z); e=float(elliptic(.5)[1].real)
    diff=elliptic(z-.5)[0]-elliptic(z-.5j)[0]
    c=PI**2*(1+1j)/(4*e)
    x=.5*(-zz+PI*(z-1j)+c)+PI/(4*e)*diff
    y=.5j*(-zz-PI*(z-1)-c)-1j*PI/(4*e)*diff
    h=np.sqrt(2*PI)/4*np.log(np.abs((p-e)/(p+e)))
    xyz=np.stack([x.real,y.real,h],axis=-1)
    invg=dp/(np.sqrt(8*PI)*e)
    norm=1+np.abs(invg)**2
    normals=np.stack([2*invg.real,-2*invg.imag,1-np.abs(invg)**2],axis=-1)/norm[...,None]
    metric=.25*(np.abs(p)+2*PI*e*e/np.abs(p*p-e*e))**2
    invgp=(6*p*p-2*e*e)/(np.sqrt(8*PI)*e)
    potential=8*np.abs(invgp)**2/norm**2
    return xyz,normals,metric,potential

def generate(n=72,radius=1.0):
    # Circular cuts in the parameter torus give smooth, geometrically honest rims.
    # radius scales how much of each end is omitted, not the surface itself.
    punctures=[(0.,0.),(.5,0.),(0.,.5)]
    cuts=np.array([.11,.033,.033])*radius
    u=(np.arange(n)+.5)/n
    rng=np.random.default_rng(1729)
    uv=np.array([(a,b) for a in u for b in u])+rng.uniform(-.02/n,.02/n,(n*n,2))
    def distance(points,c):return np.linalg.norm((points-np.array(c)+.5)%1-.5,axis=-1)
    keep=np.ones(len(uv),dtype=bool)
    for c,r in zip(punctures,cuts):keep &= distance(uv,c)>max(.15,r+.045)
    points=[uv[keep]]
    for c,r in zip(punctures,cuts):
        for rho in np.geomspace(r,max(.15,r+.045),7):
            angle=2*PI*np.arange(96)/96+rng.uniform(-.002,.002,96)
            points.append((np.array(c)+rho*np.stack([np.cos(angle),np.sin(angle)],axis=-1))%1)
    uv=np.unique(np.round(np.concatenate(points),12)%1,axis=0);N=len(uv)
    shifts=np.array([(a,b) for a in [-1,0,1] for b in [-1,0,1]])
    tiled=np.concatenate([uv+q for q in shifts]);tri=Delaunay(tiled)
    cells=tri.simplices;centers=tiled[cells].mean(axis=1)
    ok=np.all((centers>=0)&(centers<1),axis=1)
    for c,r in zip(punctures,cuts):ok &= distance(centers,c)>=r*(1-1e-8)
    cells=cells[ok];coords=tiled[cells];faces=cells%N
    # Use counterclockwise parameter orientation everywhere.
    d1=coords[:,1]-coords[:,0];d2=coords[:,2]-coords[:,0]
    cross=d1[:,0]*d2[:,1]-d1[:,1]*d2[:,0]
    flip=cross<0;faces[flip]=faces[flip][:,[0,2,1]];coords[flip]=coords[flip][:,[0,2,1]]
    area=abs(cross)/2
    xyz,nu,E,V=costa(uv[:,0]+1j*uv[:,1])
    from collections import Counter
    counts=Counter(tuple(sorted((int(f[k]),int(f[(k+1)%3])))) for f in faces for k in range(3))
    boundary=np.array(sorted({a for e,count in counts.items() if count==1 for a in e}))
    free=np.ones(N,dtype=bool);free[boundary]=False
    # Conformal P1 finite elements: Euclidean parameter stiffness, E-weighted mass.
    grad=np.stack([coords[:,1]-coords[:,2],coords[:,2]-coords[:,0],coords[:,0]-coords[:,1]],axis=1)
    stiffness=np.einsum('fik,fjk->fij',grad,grad)/(4*area[:,None,None])
    rows=np.repeat(faces,3,axis=1).ravel();cols=np.tile(faces,(1,3)).ravel()
    K=coo_matrix((stiffness.ravel(),(rows,cols)),shape=(N,N)).tocsr()
    mass=np.bincount(faces.ravel(),weights=np.repeat(area/3,3),minlength=N)
    weights=mass*E
    A=(-K+diags(mass*V))[free][:,free]
    weight=weights[free];inv=diags(1/np.sqrt(weight));B=inv@A@inv
    bound=float(np.max(V/E))+1
    ev,vec=eigsh(B,k=1,sigma=bound,which='LM',v0=np.ones(free.sum()),tol=1e-11)
    lam=float(ev[0]);phi=np.zeros(N);phi[free]=vec[:,0]/np.sqrt(weight)
    if phi.sum()<0:phi=-phi
    phi/=phi.max()
    residual=float(np.linalg.norm(A@phi[free]-lam*weight*phi[free])/np.linalg.norm(lam*weight*phi[free]))
    assert lam>0 and phi[free].min()>0
    # Mesh boundary, for strong end contours and topology checks.
    from collections import Counter,defaultdict
    edges=Counter(tuple(sorted((f[k],f[(k+1)%3]))) for f in faces for k in range(3))
    adj=defaultdict(list)
    for (a,b),count in edges.items():
        if count==1:adj[a].append(b);adj[b].append(a)
    assert all(len(v)==2 for v in adj.values()), [(k,len(v),uv[k].tolist()) for k,v in adj.items() if len(v)!=2][:12]
    unseen=set(adj);paths=[]
    while unseen:
        start=min(unseen);path=[start];prev=-1;cur=start
        while True:
            nxt=next(v for v in adj[cur] if v!=prev)
            if nxt==start:break
            path.append(nxt);prev,cur=cur,nxt
        unseen.difference_update(path);paths.append(path+[start])
    used=set(x for f in faces for x in f)
    assert len(used)==N
    chi=len(used)-len(edges)+len(faces)
    assert len(paths)==3 and chi==-3
    data=dict(kind='minimal-ancient-linearized',name='Costa: two sides of an unstable minimal surface',status='numerical-linearized',
        vertices=np.round(xyz,8).tolist(),normals=np.round(nu,8).tolist(),mode=np.round(phi,9).tolist(),
        faces=faces.tolist(),paths=paths,eigenvalue=lam,amplitude=.11,time=dict(min=-5,max=0,value=-1.5),snapshots=[-5,-3,-1.5,0],
        view=dict(yaw=.28,pitch=.60),radius=3.6,
        description='Numerical Costa surface with a positive Dirichlet Jacobi mode. X ± 0.11 exp(τ) φ ν, τ=λt. Linearized model on a truncated domain, not nonlinear ancient MCF slices.',
        source='Mramor–Payne, arXiv:1904.08439v2, Theorem 1.1 and §3; Costa parametrization: Melko (2010), equation (17).')
    audit=dict(grid=n,parameter_cut_radii=cuts.tolist(),vertices=len(used),faces=len(faces),boundary_components=len(paths),euler_characteristic=chi,genus=(2-len(paths)-chi)//2,
        eigenvalue=lam,relative_eigen_residual=residual,minimum_interior_mode=float(phi[free].min()),max_principal_curvature=float(np.sqrt(np.max(V/E)/2)),
        interpretation='Dirichlet finite-element eigenmode on the truncated Costa surface. No nonlinear PDE or global ancient limit is computed.')
    return data,audit

def coordinate_checks():
    z=np.array([.12+.23j,.38+.15j,.69+.72j,.49+.48j]);h=1e-5
    x,n,E,V=costa(z)
    xu=(costa(z+h)[0]-costa(z-h)[0])/(2*h)
    xv=(costa(z+1j*h)[0]-costa(z-1j*h)[0])/(2*h)
    checks=dict(normal_tangency=float(max(np.max(abs((n*xu).sum(axis=1))),np.max(abs((n*xv).sum(axis=1))))),
        relative_metric_error=float(max(np.max(abs((xu*xu).sum(axis=1)/E-1)),np.max(abs((xv*xv).sum(axis=1)/E-1)))),
        period_error=float(max(np.max(abs(costa(z+1)[0]-x)),np.max(abs(costa(z+1j)[0]-x)))),
        conformal_harmonicity_residual=float(np.max(abs((costa(z+h)[0]+costa(z-h)[0]+costa(z+1j*h)[0]+costa(z-1j*h)[0]-4*x)/(h*h)))))
    assert checks['normal_tangency']<1e-6 and checks['relative_metric_error']<1e-6
    assert checks['period_error']<1e-10 and checks['conformal_harmonicity_residual']<1e-3
    return checks

def main():
    data,audit=generate()
    audit['coordinate_checks']=coordinate_checks()
    audit['refinement']=[generate(n)[1] for n in [52,96]]
    audit['domain_comparison']=[generate(72,r)[1] for r in [1.15,.85]]
    (OUT/'minimal-ancient-flows.json').write_text(json.dumps(data,separators=(',',':'),default=lambda x:int(x))+'\n')
    (OUT/'minimal-ancient-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2))
if __name__=='__main__':main()
