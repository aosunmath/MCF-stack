"""Solve only the AV97 limiting bowl ODE; the compact time slices are schematics.

Run with numpy/scipy, then `node scripts/render_neckpinch_picture.mjs`.
The private source PDF is never copied into the edition.
"""
import json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]


def bowl_solution(tolerance=2e-11):
    eps = 1e-5
    return solve_ivp(lambda r, y: [y[1], (1+y[1]**2)*(1-y[1]/r)],
                     [eps, 40], [eps**2/4+eps**4/128, eps/2+eps**3/32],
                     rtol=tolerance, atol=tolerance/100, dense_output=True,
                     max_step=.02)


def main():
    sol = bowl_solution()
    finer = bowl_solution(2e-12)
    if not sol.success or not finer.success:
        raise RuntimeError('Bowl integration failed')
    r = np.linspace(0, 40, 8001)
    values = sol.sol(r)[0]
    values[0] = 0
    error = float(np.max(np.abs(sol.sol(r[1:])-finer.sol(r[1:]))))
    data = {
        'kind': 'av-neckpinch', 'status': 'asymptotic-schematic',
        'description': 'n=2, m=3, K=1. Compact time slices are a designed asymptotic schematic, not a numerical MCF solution. Only the speed-one limiting bowl is integrated from its ODE.',
        'vertices': [[0, 0, 0], [1, 0, 0]], 'faces': [], 'paths': [[0, 1]],
        'bowl': {'step': .005, 'height': [round(float(v), 12) for v in values]},
        'source': {'doi': '10.1515/crll.1997.482.15',
                   'locators': ['Introduction items 1–5, pp. 16–17', 'Figure 1, p. 18',
                                'Section 2, pp. 20–25, equations (2.6), (2.9), (2.24)–(2.26)',
                                'Theorem 3.3, p. 30', 'Section 8, pp. 58–60']},
        'audit': {'bowl_equation': "P''=(1+P'^2)(1-P'/r); P(0)=P'(0)=0",
                  'tip_series': 'P=r^2/4+r^4/128+O(r^6)',
                  'speed': 1, 'tip_mean_curvature': 1,
                  'refined_max_difference': error, 'rtol': 2e-11,
                  'full_flow_solved': False, 'finite_time_error_bound': None}
    }
    path = ROOT/'site/assets/solitons/neckpinch-scales.json'
    path.write_text(json.dumps(data, separators=(',', ':'))+'\n')
    print(f'Bowl refinement difference: {error:.3g}; wrote {path.name}')


if __name__ == '__main__':
    main()
