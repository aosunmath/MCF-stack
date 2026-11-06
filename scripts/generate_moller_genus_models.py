"""Genus-labelled gluing schematics, NOT numerical shrinker solutions.

Requires numpy, scipy, scikit-image, trimesh, fast-simplification. The ordinary
site build uses committed assets and does not need these numerical packages.
See documentation/moller-picture.md for the defining illustrative level set.
"""
from pathlib import Path
import json
import math
import numpy as np
from scipy.interpolate import CubicSpline
from skimage.measure import marching_cubes
import trimesh
from generate_moller_geometry import profile_and_intersections, project

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/assets/solitons'
GENERA = [8, 16, 24]


def torus_data():
    profile, intersections = profile_and_intersections()
    z, r = np.array(profile)[:-1].T
    center = (r.min()+r.max())/2
    angle = np.arctan2(z, r-center)
    order = np.argsort(angle)
    angle, rho = angle[order], np.hypot(z, r-center)[order]
    angle = np.r_[angle, angle[0]+2*np.pi]
    rho = np.r_[rho, rho[0]]
    return center, angle[0], CubicSpline(angle, rho, bc_type='periodic'), intersections[1]


def field_grid(resolution):
    center, start, profile_radius, (z0, r0) = torus_data()
    x = np.linspace(-3.6, 3.6, resolution)
    z = np.linspace(-2.3, 2.3, int(resolution*4.6/7.2))
    xx, yy = np.meshgrid(x, x, indexing='ij')
    r, zz = np.hypot(xx, yy)[..., None], z[None, None, :]
    sphere = np.hypot(r, zz)-2
    angle = (np.arctan2(zz, r-center)-start) % (2*np.pi)+start
    torus = np.hypot(r-center, zz)-profile_radius(angle)
    bump = np.maximum(1-((r-r0)**2+(np.abs(zz)-z0)**2)/.7**2, 0)**3
    return x, z, sphere*torus, bump, np.arctan2(yy, xx)[..., None]


def audit(mesh, genus):
    components = len(mesh.split(only_watertight=False))
    result = dict(vertices=len(mesh.vertices), faces=len(mesh.faces),
                  edges=len(mesh.edges_unique), euler=int(mesh.euler_number),
                  components=components, watertight=bool(mesh.is_watertight),
                  orientable=bool(mesh.is_winding_consistent), genus=genus)
    assert result['euler'] == 2-2*genus, result
    assert components == 1 and result['watertight'] and result['orientable'], result
    return result


def extract(grid, genus):
    x, z, product, bump, theta = grid
    periods = genus//2
    epsilon = 1.25/periods
    field = product-epsilon**2*np.cos(periods*theta)*bump
    vertices, faces, _, _ = marching_cubes(field.astype(np.float32), 0,
        spacing=(x[1]-x[0], x[1]-x[0], z[1]-z[0]), allow_degenerate=False)
    vertices += np.array([x[0], x[0], z[0]])
    return trimesh.Trimesh(vertices, faces, process=True)


def export(mesh, genus):
    name = 'moller-genus' if genus == 8 else f'moller-genus-{genus}'
    return dict(name=name, kind='moller-genus-model', status='schematic', genus=genus,
        description=f'Genus {genus} sphere–torus handle schematic; not a computed self-shrinker.',
        vertices=np.round(mesh.vertices, 6).tolist(), faces=mesh.faces.tolist(), paths=[],
        normals=np.round(mesh.vertex_normals, 6).tolist(),
        variants=[{'genus': g, 'model': 'moller-genus' if g == 8 else f'moller-genus-{g}'} for g in GENERA],
        view=dict(yaw=.35, pitch=.36, radius=3.5),
        topology=audit(mesh, genus),
        model=dict(periods_per_circle=genus//2, epsilon=1.25/(genus//2), support_radius=.7,
                   equation='S(r,z) T(r,z) = epsilon^2 cos((g/2) theta) B(r,z)'),
        limitations='Illustrative smoothing of the sphere–torus intersection, not a shrinker-PDE solution or a certified approximation to one. The theorem does not give an explicit genus threshold. The selected genera label the meshes only.')


def svg(data):
    # Original shaded rendering of the same mesh used in the interactive view.
    points = np.array([project(p, yaw=.35, pitch=.36) for p in data['vertices']])
    xy = np.column_stack([320+75*points[:, 0], 215-75*points[:, 1]])
    faces = np.array(data['faces'])
    a, b, c = points[faces].transpose(1, 0, 2)
    normal = np.cross(b-a, c-a)
    light = .38+.57*np.abs(normal @ np.array([.3, .5, .8]))/np.maximum(np.linalg.norm(normal, axis=1), 1e-12)
    rgb = (light[:, None]*np.array([75, 151, 173])+(1-light[:, None])*38).astype(int)
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="640" height="410" viewBox="0 0 640 410" role="img" aria-labelledby="title desc">',
        f'<title id="title">Genus {data["genus"]} sphere–torus gluing schematic</title>',
        '<desc id="desc">One connected closed surface with handles along the two former intersection circles. Its mesh genus is checked. This is an illustrative level-set smoothing, not a computed self-shrinker.</desc>',
        '<rect width="640" height="410" fill="#f7fafb"/>']
    for i in np.argsort(points[faces, 2].mean(axis=1)):
        pts = ' '.join(f'{x:.2f},{y:.2f}' for x, y in xy[faces[i]])
        color = ','.join(map(str, rgb[i]))
        parts.append(f'<polygon points="{pts}" fill="rgb({color})" stroke="rgb({color})" stroke-width=".35"/>')
    parts += ['<g font-family="Arial, Helvetica, sans-serif" fill="#183f52">',
        f'<text x="22" y="29" font-size="20" font-weight="600">Genus {data["genus"]} · handle schematic</text>',
        '<text x="22" y="52" font-size="14">Illustrative desingularization, not a computed self-shrinker</text>',
        '<text x="22" y="387" font-size="14">Handles replace the two intersection circles. Rotate online to inspect them.</text>',
        '</g></svg>']
    return '\n'.join(parts)+'\n'


def main():
    checks = {'status': 'mesh topology checks, not shrinker verification', 'source': 'https://arxiv.org/abs/1111.7318v2', 'resolutions': [144, 192], 'models': {}}
    for resolution in checks['resolutions']:
        grid = field_grid(resolution)
        for genus in GENERA:
            mesh = extract(grid, genus)
            result = audit(mesh, genus)
            checks['models'].setdefault(str(genus), {})[str(resolution)] = result
            print(resolution, genus, result, flush=True)
            if resolution == checks['resolutions'][-1]:
                mesh = mesh.simplify_quadric_decimation(face_count=26000, aggression=5)
                # Audit after simplification AND after the exported rounding.
                mesh = trimesh.Trimesh(np.round(mesh.vertices, 6), mesh.faces, process=False)
                data = export(mesh, genus)
                checks['models'][str(genus)]['export'] = data['topology']
                (OUT/(data['name']+'.json')).write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':'))+'\n')
                (OUT/(data['name']+'.svg')).write_text(svg(data))
                print('Exported', data['name'], data['topology'], flush=True)
    (OUT/'moller-genus-audit.json').write_text(json.dumps(checks, indent=2)+'\n')


if __name__ == '__main__':
    main()
