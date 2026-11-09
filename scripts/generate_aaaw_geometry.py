"""Original AAAW illustrations: exact dense curve and numerical soliton profiles.

Run with Python + NumPy/SciPy. No source figures or PDFs are redistributed.
The diagnostics are numerical checks, never existence or asymptotic proofs.
"""
import json
import math
import numpy as np
from scipy.integrate import solve_ivp
from generate_soliton_geometry import OUT, save


def rhs(alpha, omega, velocity):
    def equation(s, state):
        c, tangent = state[:3], state[3:]
        # Unit projection also prevents roundoff amplification in long tails.
        tangent = tangent / np.linalg.norm(tangent)
        a = alpha*c + omega*np.array([-c[1], c[0], 0.]) + np.array([0., 0., velocity])
        return np.r_[tangent, a-np.dot(a, tangent)*tangent]
    return equation


def profile(alpha, omega, velocity, position, tangent, length, tolerance=2e-11):
    equation = rhs(alpha, omega, velocity)
    state = np.array([*position, *tangent], dtype=float)
    samples = []
    count = round(length/.02)
    for sign in (-1, 1):
        arc = np.linspace(0, sign*length, count+1)
        sol = solve_ivp(equation, (0, sign*length), state, t_eval=arc,
                        method='DOP853', rtol=tolerance, atol=tolerance/10,
                        max_step=.04)
        if not sol.success:
            raise RuntimeError(sol.message)
        samples.append(sol.y.T[::-1] if sign < 0 else sol.y.T[1:])
    return np.linspace(-length, length, 2*count+1), np.concatenate(samples)


def main():
    audit = {'source': 'AAAW13, arXiv:1207.4051v1, equations (11)-(14), (27)',
             'status': 'Numerical diagnostics, not certified error bounds', 'profiles': {}}
    configurations = [
        ('aaaw-rotator', 0, 1, 0, [1,0,0], [0,0,1], 24),
        ('aaaw-yin-yang', 0, 1, 0, [0,0,0], [1,0,0], 24),
        ('aaaw-screw', 0, 1, 1, [1,0,0], [0,1,0], 24),
        ('aaaw-expanding', .5, 1, 0, [1,0,0], [0,0,1], 24),
        ('aaaw-shrinking', -.5, 1, 0, [2,0,0], [0,0,1], 18),
        ('aaaw-spherical', -.5, 1, 0, [math.sqrt(2),0,0], [0,0,1], 18),
    ]
    for name, alpha, omega, velocity, position, tangent, length in configurations:
        arc, states = profile(alpha, omega, velocity, position, tangent, length)
        _, refined = profile(alpha, omega, velocity, position, tangent, length, 2e-12)
        vertices = states[:, :3]
        times = (-3, 3) if alpha == 0 else ((-.8, 2) if alpha > 0 else (-2, .8))
        parameters = dict(alpha=alpha, omega=omega, velocity=velocity)
        data = save(name, vertices, paths=[list(range(len(vertices)))], status='numerical-ode',
                    description=f'Numerical AAAW curve: alpha={alpha}, omega={omega}, vertical velocity={velocity}; arclength window [-{length}, {length}].',
                    flat=name == 'aaaw-yin-yang',
                    dynamic=dict(kind='rotating-soliton', min=times[0], max=times[1], value=0, **parameters),
                    view={'radius': float(max(np.linalg.norm(vertices, axis=1))*math.sqrt(max(1+2*alpha*t for t in times))+abs(velocity)*max(map(abs,times))), 'center': [0,0,0]},
                    integration={'arc': arc.tolist(), 'states': np.round(states, 12).tolist(), **parameters})
        # Differentiation of the stored samples, independent of solver estimates.
        h = arc[1]-arc[0]
        derivative = (states[:-4]-8*states[1:-3]+8*states[3:-1]-states[4:])/(12*h)
        residual = derivative-np.array([rhs(alpha,omega,velocity)(s,y) for s,y in zip(arc[2:-2],states[2:-2])])
        audit['profiles'][name] = {
            **parameters, 'position': position, 'tangent': tangent, 'arc_window': [-length,length],
            'max_unit_speed_error': float(max(abs(np.linalg.norm(states[:,3:],axis=1)-1))),
            'refinement_max_component_change': float(np.max(abs(states-refined))),
            'fourth_order_difference_residual': float(np.max(abs(residual))),
        }
        if name == 'aaaw-spherical':
            audit['profiles'][name]['max_sphere_equation_error'] = float(max(abs(np.sum(vertices**2,axis=1)-2)))
    theta = np.linspace(-12*math.pi, 12*math.pi, 2401)
    vertices = np.column_stack([np.cos(theta), np.sin(theta), np.cos(math.sqrt(2)*theta), np.sin(math.sqrt(2)*theta)])
    save('aaaw-dense-torus', vertices, paths=[list(range(len(vertices)))], status='formula',
         description='Exact irrational-frequency curve in R4 at t=-1, projected to R3; only -12 pi <= theta <= 12 pi is sampled.',
         view={'radius': math.sqrt(12), 'center': [0,0,0]},
         dynamic={'kind':'dense-torus', 'min':-6, 'max':-.05, 'value':-1})
    (OUT/'aaaw-audit.json').write_text(json.dumps(audit, indent=2)+'\n')
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    main()
