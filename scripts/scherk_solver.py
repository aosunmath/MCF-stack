"""Finite-difference translator graphs on a centred rectangle.

Upward convention: (delta_ij - u_i u_j / (1+|Du|^2)) u_ij = 1.
Boundary heights are +h on horizontal sides and -h on vertical sides.
Solve for the base length L simultaneously with u(0,0)=0, following
Hoffman-Martin-White, arXiv:1903.04617v4, proof of Theorem 3.1.
This is an uncertified finite-boundary discretization, not an exact soliton.
"""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from scipy.interpolate import RegularGridInterpolator

def solve(n=65,h=2.,w=np.pi/2,initial=None):
 m=n-2; k=m*m; ids=np.arange(k).reshape(m,m)
 if initial is None:
  a=np.linspace(-1,1,n); X,Y=np.meshgrid(a,a)
  U=(np.log(np.maximum(np.cos(np.pi*X/2),1e-5))-np.log(np.maximum(np.cos(np.pi*Y/2),1e-5)))*w/np.pi
  U=np.clip(U,-h,h);L=w*1.35
 else:
  U,L=initial;U=U*h/U[0,len(U)//2];U=RegularGridInterpolator((np.linspace(-1,1,len(U)),)*2,U)(np.stack(np.meshgrid(np.linspace(-1,1,n),np.linspace(-1,1,n),indexing="ij"),axis=-1)) if len(U)!=n else U.copy()
 U[0,:]=h;U[-1,:]=h;U[:,0]=-h;U[:,-1]=-h;U[0,0]=U[0,-1]=U[-1,0]=U[-1,-1]=0
 def calc(U,L,jac=False):
  dx=L/(n-1);dy=w/(n-1)
  p=(U[1:-1,2:]-U[1:-1,:-2])/(2*dx);q=(U[2:,1:-1]-U[:-2,1:-1])/(2*dy)
  r=(U[1:-1,2:]+U[1:-1,:-2]-2*U[1:-1,1:-1])/dx**2
  t=(U[2:,1:-1]+U[:-2,1:-1]-2*U[1:-1,1:-1])/dy**2
  s=(U[2:,2:]-U[2:,:-2]-U[:-2,2:]+U[:-2,:-2])/(4*dx*dy)
  D=1+p*p+q*q; A=(1+q*q)/D; B=-2*p*q/D;C=(1+p*p)/D
  F=A*r+B*s+C*t-1
  if not jac:return np.r_[F.ravel(),U[n//2,n//2]]
  dp=(-2*p*(1+q*q)*r+(-2*q*D+4*p*p*q)*s+2*p*q*q*t)/D**2
  dq=(2*q*p*p*r+(-2*p*D+4*p*q*q)*s-2*q*(1+p*p)*t)/D**2
  coeff={(0,0):-2*A/dx**2-2*C/dy**2,(0,1):A/dx**2+dp/(2*dx),(0,-1):A/dx**2-dp/(2*dx),(1,0):C/dy**2+dq/(2*dy),(-1,0):C/dy**2-dq/(2*dy),(1,1):B/(4*dx*dy),(1,-1):-B/(4*dx*dy),(-1,1):-B/(4*dx*dy),(-1,-1):B/(4*dx*dy)}
  rows=[];cols=[];vals=[]
  Y,X=np.indices((m,m))
  for (i,j),v in coeff.items():
   ok=(Y+i>=0)&(Y+i<m)&(X+j>=0)&(X+j<m)
   rows.extend(ids[ok]);cols.extend((ids+i*m+j)[ok]);vals.extend(v[ok])
  dL=(calc(U,L+1e-5)[:-1]-F.ravel())/1e-5
  rows.extend(range(k));cols.extend([k]*k);vals.extend(dL)
  rows.append(k);cols.append(ids[m//2,m//2]);vals.append(1.)
  return np.r_[F.ravel(),U[n//2,n//2]],coo_matrix((vals,(rows,cols)),shape=(k+1,k+1)).tocsc()
 for it in range(60):
  F,J=calc(U,L,True);err=max(abs(F))
  if err<1e-8:break
  d=spsolve(J,-F);fac=1.
  for _ in range(20):
   v=U.copy();v[1:-1,1:-1]+=fac*d[:-1].reshape(m,m);ell=L+fac*d[-1]
   if ell>0 and max(abs(calc(v,ell)))<err:break
   fac*=.5
  U,L=v,ell
  if it%10==0:print(n,h,it,err,L,fac,flush=True)
 error = float(max(abs(calc(U,L))))
 if error > 1e-7:
  raise RuntimeError(f'Newton solve failed: n={n}, h={h}, residual={error}')
 print('Converged',n,h,it,error,L,flush=True)
 return U,L
