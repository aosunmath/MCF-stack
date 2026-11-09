"""Numerical Delta-wing from HIMW's rectangular Dirichlet construction.

Requires NumPy, SciPy and Matplotlib. The source translates downward; here
z is reflected so Q(u)=1 and the velocity is +e3. This is an unvalidated
finite-difference illustration, not a computer-assisted existence proof.
Run with --cache /tmp/mcf-delta-cache to reuse numerical solves.
"""
import argparse
import json
import os
from pathlib import Path
import numpy as np
from scipy import sparse as sp
from scipy.sparse.linalg import spsolve
from scipy.interpolate import RectBivariateSpline
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
B = np.pi / np.sqrt(2)

def operators(x):
    """Three-point derivatives, even reflection at 0, zero outer Dirichlet data."""
    h,k=np.diff(x)[:-1],np.diff(x)[1:]
    n=len(x)-2
    rows=np.repeat(np.arange(n),3)
    cols=np.array([np.arange(n),np.arange(n)+1,np.arange(n)+2]).T.ravel()
    d=np.array([-k/(h*(h+k)),(k-h)/(h*k),h/(k*(h+k))]).T.ravel()
    dd=np.array([2/(h*(h+k)),-2/(h*k),2/(k*(h+k))]).T.ravel()
    out=[]
    for v,first in [(d,[0,0]),(dd,[-2/(x[1]**2),2/(x[1]**2)])]:
        interior=sp.csr_matrix((v,(rows+1,cols)),shape=(n+1,n+2))
        boundary=sp.csr_matrix((first,([0,0],[0,1])),shape=(n+1,n+2))
        out.append((interior+boundary)[:,:-1])
    return out

def solve(b,L,nx,ny,initial=None):
    """Damped Newton on a quadrant; nx, ny count intervals in the full rectangle."""
    x=np.linspace(0,L,nx//2+1);y=b*np.sin(np.linspace(0,np.pi/2,ny//2+1));nx//=2;ny//=2
    dx,dxx=operators(x);dy,dyy=operators(y)
    ix,iy=sp.eye(nx),sp.eye(ny)
    DX=sp.kron(dx,iy,format='csr');DY=sp.kron(ix,dy,format='csr')
    DXX=sp.kron(dxx,iy,format='csr');DYY=sp.kron(ix,dyy,format='csr');DXY=sp.kron(dx,dy,format='csr')
    def calc(u,speed,jac=False):
        p,q=DX@u,DY@u;r,s,t=DXX@u,DXY@u,DYY@u
        D=1+p*p+q*q;A=(1+q*q)/D;B=-2*p*q/D;C=(1+p*p)/D
        f=A*r+B*s+C*t-speed
        if not jac:return f
        P=(-2*p*A*r+(-2*q+4*p*p*q/D)*s+2*p*q*q/D*t)/D
        Q=(2*q*p*p/D*r+(-2*p+4*p*q*q/D)*s-2*q*C*t)/D
        J=sum(sp.diags(v)@mat for v,mat in [(A,DXX),(B,DXY),(C,DYY),(P,DX),(Q,DY)])
        return f,J
    u=np.zeros(nx*ny) if initial is None else initial(x[:-1],y[:-1]).ravel()
    for speed in (np.linspace(.1,1,10) if initial is None else [1.]):
        for it in range(45):
            f,J=calc(u,speed,True);err=np.max(np.abs(f))
            if err<1e-8:break
            step=spsolve(J,-f);a=1
            while a>1e-8:
                v=u+a*step
                if np.max(np.abs(calc(v,speed))) < err:break
                a*=.5
            if a<=1e-8:raise RuntimeError('Newton line search failed')
            u=v
        else:raise RuntimeError((L,speed,err))
    U=np.zeros((nx+1,ny+1));U[:-1,:-1]=u.reshape(nx,ny)
    x=np.r_[-x[:0:-1],x];y=np.r_[-y[:0:-1],y]
    U=np.concatenate([U[:0:-1],U],axis=0);U=np.concatenate([U[:,:0:-1],U],axis=1);nx*=2;ny*=2
    print('SOLVED',b,L,nx,ny,'tip',U[nx//2,ny//2],'res',err,flush=True)
    return x,y,U,RectBivariateSpline(x,y,U),err

def centered_spline(x,y,u):
    return RectBivariateSpline(x,y,u-u[len(x)//2,len(y)//2])


def make_geometry(s):
    # Height contours give a smooth, closed display boundary instead of the
    # misleading vertical cut walls of a rectangular plotting window.
    angles=np.arange(192)*2*np.pi/192
    heights=np.linspace(0,6,49)[1:]
    theta,z=np.meshgrid(angles,heights)
    c,d=np.cos(theta),np.sin(theta)
    lo=np.zeros_like(z)
    hi=np.minimum(12/np.maximum(abs(c),1e-12),.997*B/np.maximum(abs(d),1e-12))
    if np.any(s.ev(hi*c,hi*d)<z):raise ValueError('Display contour exceeds solved window')
    for _ in range(45):
        mid=(lo+hi)/2
        below=s.ev(mid*c,mid*d)<z
        lo=np.where(below,mid,lo);hi=np.where(below,hi,mid)
    r=(lo+hi)/2
    vertices=np.vstack([[0,0,0],np.column_stack([(r*c).ravel(),(r*d).ravel(),z.ravel()])])
    faces=[]
    for j in range(192):faces.append([0,1+j,1+(j+1)%192])
    for i in range(47):
        for j in range(192):
            a=1+i*192+j;d0=1+i*192+(j+1)%192
            faces.extend([[a,a+192,d0+192],[a,d0+192,d0]])
    # Orient the disk with the upward graph normal.
    faces=np.array(faces)
    cross=np.cross(vertices[faces[:,1]]-vertices[faces[:,0]],vertices[faces[:,2]]-vertices[faces[:,0]])
    faces[cross[:,2]<0]=faces[cross[:,2]<0][:,[0,2,1]]
    p=s.ev(vertices[:,0],vertices[:,1],dx=1);q=s.ev(vertices[:,0],vertices[:,1],dy=1)
    normals=np.column_stack([-p,-q,np.ones(len(p))]);normals/=np.linalg.norm(normals,axis=1)[:,None]
    contours=[list(range(1+i*192,1+(i+1)*192))+[1+i*192] for i in range(7,48,8)]
    ys=np.linspace(-.95*B,.95*B,161)
    stations=np.linspace(0,6,25)
    sections=[np.column_stack([ys,s(x,ys)[0]-float(s(x,0)[0,0])]).tolist() for x in stations]
    xs=np.linspace(-10,10,401)
    return dict(name='delta-wing',kind='delta-wing-pde',status='numerical-pde',
        description='Numerical upward unit-speed Delta-wing, strip width sqrt(2) pi; height-truncated finite-domain approximation.',
        vertices=np.round(vertices,8).tolist(),faces=faces.tolist(),normals=np.round(normals,8).tolist(),paths=contours,
        halfWidth=float(B),angle=float(np.pi/4),maxHeight=6,
        view=dict(yaw=-.48,pitch=.62,radius=9.5),
        longitudinal=np.round(np.column_stack([xs,s(xs,0)[:,0]]),8).tolist(),
        sectionStations=stations.tolist(),sections=np.round(sections,8).tolist(),
        grimSection=np.round(np.column_stack([ys,-2*np.log(np.cos(ys/np.sqrt(2)))]),8).tolist())


def audit(s,domain_comparison,grid_comparison):
    x,y=np.meshgrid(np.linspace(-10,10,201),np.linspace(-.99*B,.99*B,199),indexing='ij')
    z=s.ev(x,y);mask=z<=6
    p,q,r,t,h=[s.ev(x,y,dx=i,dy=j) for i,j in [(1,0),(0,1),(2,0),(0,2),(1,1)]]
    residual=((1+q*q)*r-2*p*q*h+(1+p*p)*t)/(1+p*p+q*q)-1
    eigen=(r+t-np.sqrt((r-t)**2+4*h*h))/2
    def change(other):return float(np.max(abs((other.ev(x,y)-z)[mask])))
    sx,sy=np.meshgrid(np.linspace(0,6,25),np.linspace(-.95*B,.95*B,161),indexing='ij')
    profiles=s.ev(sx,sy)-s.ev(sx,np.zeros_like(sx))
    profile_change=(domain_comparison.ev(sx,sy)-domain_comparison.ev(sx,np.zeros_like(sx)))-profiles
    return dict(status='numerical-pde; no certified error bounds',
        source='https://arxiv.org/abs/1805.10860v2',source_locations='Equation (1.3), Figure 3, Theorem 2.4, Sections 3–4 and Theorem 5.7',
        normalization='Hvec = e3 perpendicular; reflect the source vertical coordinate; u(0,0)=0',
        half_width=float(B),width=float(2*B),tilt_angle=float(np.pi/4),
        equation='((1+u_y^2)u_xx - 2u_x u_y u_xy + (1+u_x^2)u_yy)/(1+u_x^2+u_y^2) = 1',
        method='Second-order finite differences on a quadrant; even reflection on axes; zero Dirichlet data on rectangle edges; damped Newton; subtract apex height; bicubic sampling',
        rectangle_half_length=24,grid_intervals=[480,960],display_height=[0,6],
        residual_sample_count=int(mask.sum()),max_sampled_interpolant_pde_residual=float(max(abs(residual[mask]))),
        min_sampled_hessian_eigenvalue=float(min(eigen[mask])),
        domain_comparison=dict(half_lengths=[22,24],y_intervals=960,x_spacing=.1,max_display_height_change=change(domain_comparison),max_recentered_profile_change=float(np.max(abs(profile_change)))),
        grid_comparison=dict(half_length=24,y_intervals=[720,960],x_spacing=.1,max_display_height_change=change(grid_comparison)),
        apex_hessian=[float(s(0,0,dx=2)[0,0]),float(s(0,0,dy=2)[0,0])],
        limitations='Residuals and mesh/domain comparisons are numerical diagnostics, not rigorous bounds. The finite rectangle is not the complete translator; only a compact centered portion is shown. No boundary of the complete surface is implied.')


def drawing(data):
    os.environ.setdefault('MPLCONFIGDIR','/tmp/mcf-delta-matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    plt.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'mcf-delta-wing','font.family':'DejaVu Sans','font.size':10,'text.color':'#183f52','axes.labelcolor':'#183f52'})
    fig=plt.figure(figsize=(11,6.5),facecolor='#f7fafb')
    fig.text(.045,.94,'The Δ-wing translator',fontsize=23,weight='bold')
    fig.text(.045,.89,r'Strip width $2b=\sqrt{2}\,\pi$  ·  upward speed 1  ·  numerical PDE approximation',fontsize=12)
    ax=fig.add_axes([.005,.17,.64,.66],projection='3d',facecolor='#f7fafb')
    v=np.array(data['vertices']);f=np.array(data['faces'])
    colors=np.tile(np.array([87,155,171])/255,(len(f),1))
    # Paint thin bands into the surface triangles, so the contour marks obey
    # the same visibility as the surface (mplot3d sorts whole line objects).
    centers=v[f].mean(axis=1)
    bands=np.mod(centers[:,2],1)>.88
    colors[bands]*=.73
    colors[(abs(centers[:,1])<.035)|(abs(centers[:,0])<.035)]=np.array([210,138,61])/255
    poly=Poly3DCollection(v[f],facecolors=colors,linewidths=0,antialiased=False,shade=True)
    ax.add_collection3d(poly)
    for path in data['paths']:ax.plot(*v[path].T,color='#2a6679',lw=.65,alpha=.6)
    for a in [0,48,96,144]:
        path=[0]+[1+i*192+a for i in range(48)]
        ax.plot(*v[path].T,color='#d28a3d',lw=1.7)
    ax.set(xlim=(-9,9),ylim=(-3,3),zlim=(-.5,6.8))
    ax.set_box_aspect([18,6,7.3]);ax.view_init(elev=48,azim=-64);ax.set_axis_off()
    fig.text(.06,.17,'Height contours expose the rounded center and rising wings.',fontsize=10)
    ax1=fig.add_axes([.68,.56,.275,.235],facecolor='#f7fafb')
    line=np.array(data['longitudinal']);keep=np.abs(line[:,0])<=8
    ax1.plot(*line[keep].T,color='#21667f',lw=2.2)
    intercept=np.interp(8,line[:,0],line[:,1])-8
    for sign in [-1,1]:
        t=np.linspace(3,8,60);ax1.plot(sign*t,t+intercept,'--',color='#b17336',lw=1.3)
    ax1.set(xlabel='x (along the strip)',ylabel='z',title='Longitudinal profile: y = 0',ylim=(-.2,6.2))
    ax2=fig.add_axes([.68,.22,.275,.235],facecolor='#f7fafb')
    for i,color in [(0,'#21667f'),(24,'#64a291')]:
        a=np.array(data['sections'][i]);ax2.plot(*a.T,color=color,lw=1.8,label=f'x = {data["sectionStations"][i]:g}')
    a=np.array(data['grimSection']);ax2.plot(*a.T,'--',color='#b17336',lw=1.5,label='Grim limit')
    ax2.set(xlabel='y (across the strip)',ylabel='u(x,y) − u(x,0)',title='Recentered transverse profiles')
    ax2.legend(fontsize=8,frameon=False,loc='upper center')
    for a in [ax1,ax2]:
        a.spines[['top','right']].set_visible(False);a.spines[['bottom','left']].set_color('#a7bbc4');a.tick_params(colors='#526b77',labelsize=8);a.grid(alpha=.13)
    fig.text(.045,.09,'A compact patch of a complete surface: all visible rim edges are height cuts.',fontsize=11)
    fig.text(.045,.045,'Hoffman–Ilmanen–Martín–White, §§3–4. Finite-domain computation; no certified error bound.',fontsize=10,color='#526b77')
    fig.savefig(OUT/'delta-wing.svg',metadata={'Date':None})
    svg_path=OUT/'delta-wing.svg'
    svg_path.write_text('\n'.join(line.rstrip() for line in svg_path.read_text().splitlines())+'\n')
    fig.savefig(OUT/'delta-wing.png',dpi=160)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache',type=Path,default=Path('/tmp/mcf-delta-cache'))
    args=parser.parse_args();args.cache.mkdir(parents=True,exist_ok=True)
    results={};previous=None;oldL=None
    for L,ny in [(14,240),(14,480),(18,480),(20,480),(22,720),(24,960),(22,960),(24,720)]:
        path=args.cache/f'L{L}-Y{ny}.npz'
        if path.exists():
            cached=np.load(path);x,y,u=[cached[k] for k in ['x','y','u']]
        else:
            init=None if previous is None else lambda x,y: previous(x*oldL/L,y)*L/oldL
            x,y,u,_,_=solve(B,L,20*L,ny,initial=init)
            np.savez(path,x=x,y=y,u=u)
        results[L,ny]=centered_spline(x,y,u)
        previous=RectBivariateSpline(x,y,u,kx=1,ky=1);oldL=L
    s=results[24,960];data=make_geometry(s);report=audit(s,results[22,960],results[24,720])
    assert report['max_sampled_interpolant_pde_residual']<.005
    assert report['min_sampled_hessian_eigenvalue']>0
    assert report['domain_comparison']['max_display_height_change']<.04
    assert report['grid_comparison']['max_display_height_change']<.04
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'delta-wing.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    (OUT/'delta-wing-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    drawing(data);print(json.dumps(report,indent=2))


if __name__=='__main__':main()
