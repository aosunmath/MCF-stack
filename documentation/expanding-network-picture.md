# Numerical picture of expanding planar trees

The figure for `ex:catalogue-expanding-networks` now shows an original numerical
four-ended example, replacing the former unsolved Bézier sketch. Its permanent
section and statement tags are unchanged.

## Sources read

- Ilmanen–Neves–Schulze, *On short time existence for the planar network flow*,
  JDG 111 (2019), supplied published PDF: Section 4, Lemmas 4.1 and 4.3,
  Theorem 4.4, printed pp. 49–51 (PDF pp. 11–13), and Section 7, printed p. 70
  (PDF p. 32). These give the geodesic formulation, Gaussian end decay,
  uniqueness with asymptotic ends and topological class fixed, and the
  attribution of existence results.
- Mazzeo–Saez, *Self-similar expanding solutions for the planar network flow*,
  [arXiv:0704.3113v1](https://arxiv.org/pdf/0704.3113v1), Sections 1–4:
  the Main Theorem on p. 3; the profile equation and Proposition 2.3 on
  pp. 5–8; geodesic trees in Section 3; the four-ended blowup illustration
  in Figure 2 on p. 13. No source figure or supplied PDF is redistributed.

Both sources use curvature vector equal to normal position at time 1/2.
Dilating that profile by sqrt(2) gives the catalogue's time-one equation
`k_vec = X_perp/2`, with `Sigma_t = sqrt(t) Sigma_1` for `t > 0`.
The corresponding metric is `exp(|X|^2/2) (dx^2 + dy^2)`.

## Construction of the plotted example

Work in the Euclidean plane with one-dimensional branches and regular triple
junctions. Parameterize one branch by Euclidean arclength, with tangent
`T=(cos(theta), sin(theta))` and left normal `N=(-sin(theta), cos(theta))`.
The curvature vector is `theta' N`. Consequently the profile equation is

```
x' = cos(theta)
y' = sin(theta)
theta' = (-x sin(theta) + y cos(theta))/2.
```

Start at `(a,0,pi/3)` and shoot toward the asymptotic direction `pi/4`.
Reflection in the x-axis supplies the second outgoing end at `(a,0)`.
The central edge points to the left, so the three outward tangent angles are
`pi/3`, `pi`, `5pi/3`: all pairwise junction angles are exactly 120 degrees.
Reflect in the y-axis for the other junction, and join by the straight segment
`[-a,a] x {0}`. This segment solves the equation since its curvature and normal
position both vanish. Monotone coordinates in each quadrant prevent crossings.
This is an embedded network with two triple junctions, one finite edge, four
unbounded ends and no cycles; it is not a smooth curve at the junctions.

Numerically `a = 0.385404860209...`. The shooting uses classical RK4 with
arclength step 0.005 and 43 bisections on `[0,1]`, imposing `theta(12)=pi/4`.
The initial slope and positive junction distance are essential: these are
curved arms, not a stationary Y or arbitrary interpolating curves. The ends
approach the rays of angles `pi/4 + j*pi/2`.

Rotate the entire tree by pi/2 for the other panel. The two drawings are
congruent by a rotation, but distinct when the asymptotic ends are fixed
individually. Labels 1,2,3,4 remain northeast, northwest, southwest, southeast
in both panels. The junction pairs change from 1–4 / 2–3 to 1–2 / 3–4.
This comparison does not claim noncongruence or classify all expanders.

## Reproduction and numerical limits

Run `python3 scripts/generate_expanding_network.py` (standard library only).
The old `generate_expander_schematics.py` entry point delegates to it, so it
cannot restore the unsolved network. The JSON carries points and paths usable
by the common figure validator; a specialized planar viewer compares both
connections at the same physical scale. The original SVG is the no-JavaScript,
print and download version of the same computed geometry.

The audit JSON records step halving and extension of the shooting interval to
16. The junction changes by less than 1e-11 in these checks, and the tangent
angle and distance to the prescribed ray at the shooting endpoint are below
1e-10. These are floating-point consistency checks, not certified bounds.
The independent geometry tests estimate curvature directly from exported
positions, check the soliton sign and factor, and verify junction angles,
end directions and the nonintersecting tree structure.

The display continues the solved ODE to arclength 24 and samples it every
0.01; paths are clipped to the viewing window. The viewer permits
`0.05 <= t <= 4`, applies the exact homothety to this numerical profile and
keeps the plot scale fixed as time varies. At the separate `t=0` setting it
draws the limiting four rays, not collapsed finite samples. This cone is
nonregular, while the positive-time networks have two distinct junctions.
Angle arcs refer to the exact junction tangents; short dashed tangent guides
distinguish angles from chords of the curved branches.

The family property records remain unchanged: the new computation does not
establish Gaussian area, entropy or new classification results.
