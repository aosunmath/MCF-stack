# Lee–Wang expander time illustration

Source read: Yng-Ing Lee and Mu-Tao Wang, *Hamiltonian stationary cones and
self-similar solutions in higher dimension*, arXiv:0802.0359v1, especially
Theorem 1.1 (p. 3), Proposition 2.1 (p. 5), Section 2.2 and Proposition 2.2
(pp. 6–7), and the positive-time parametrization on p. 12.
The PDF is not included in the website or repository.

The catalogue's embedded unit-weight case has n = 3, k = 2, and weight sum
S = 1. Thus the real quadric at time t is x1² + x2² − x3² = −2t.
At t = 1 the normalization is H = X-perp / 2. For t > 0 the full flow is
L_t = sqrt(t) L_1, with intrinsic dimension 3 and ambient dimension 6.
There is no PDE approximation: triangle vertices sample the exact formula;
straight mesh edges and shading are only rendering approximations.

The four-panel plate and interactive comparison use t = 0, 0.25, 1, 4,
identical orthographic cameras, and one common physical scale. The fixed
cutoff r <= 3.2 is a display boundary, not a geometric boundary or a material
trajectory. The t = 0 panel is labeled as the singular cone limit, outside
the smooth time interval. Playback runs only through positive times.

The two colored surfaces are the real slice. They are not a projection of
the entire three-manifold and do not solve hypersurface MCF in R3.
The phase view shows the exact circle orbit of x = (1,0,sqrt(1+2t)) in the
orthogonal plane spanned by x and i(x1,x2,-x3). The half-circle connects x
to −x and demonstrates connectedness of the two real sheets through the
missing circle direction. Its phase parameter s is not time. No crossings
in a projection are used to infer embeddedness. The existing mapping-torus
qualification of the source's topology shorthand is retained.

Rebuild the assets with `node scripts/generate_lee_wang_expander.mjs`.
Geometry and differential checks are in `tests/lee-wang-expander.test.mjs`.
The viewer supports mouse/touch rotation, keyboard rotation and zoom,
positive-time playback, fixed-time phase tracing, and static/print fallback.
No example, property case, permanent tag, or reader route is added.
