# Ketover doubled-plane illustration

The original interactive picture is based on Daniel Ketover,
*Self-shrinkers whose asymptotic cones fatten*,
[arXiv:2407.01240v2](https://arxiv.org/pdf/2407.01240v2), 21 November 2024.
The relevant source passages were read directly, including the introduction,
the symmetry definition, the sweepout geometry, and the limit and end arguments.
The paper contains no surface figure or mesh to reproduce. No supplied PDF,
paper image, or extracted full text is redistributed.

## What the source supports

- Theorem 1.1, pp. 2–3: embedded genus-g shrinkers in Euclidean three-space,
  prismatic symmetry, convergence to the multiplicity-two horizontal plane,
  and two graphical asymptotically conical ends for sufficiently large genus.
- Section 2.1, p. 7: rotation by 2π/(g+1), horizontal reflection, and g+1
  vertical reflection planes. These are prismatic, not antiprismatic, symmetries.
- Section 4, Step 5, pp. 19–20: the sweepout contains two nearly parallel
  sheets joined by g+1 vertical tubes. These are comparison surfaces, not
  formulas for the min-max limit.
- Proposition 7.4, pp. 36–37: along the further subsequence in the proposition,
  for each fixed R greater than the limiting circle radius and all sufficiently
  late genera, the intersection with the horizontal plane inside B_R consists
  of g+1 embedded closed curves. The curves need not be geometric round circles.
- Section 8, pp. 37–42, especially Propositions 8.1, 8.2 and 8.6: the two
  outer components lie on opposite sides of the horizontal plane and are
  graphical conical ends for sufficiently large genus.

The picture consequently shows two perforated sheets joined along g+1 necks
near a circle. It improves the former two-annulus diagram by displaying an
actual connected triangulated surface and the topology of its necks. Joining
two disks with n holes each along their n inner boundary circles gives Euler
characteristic 2(1−n), two outer boundary circles, and genus n−1. Extending the
two outer circles to infinity gives the two-ended model.

The selectable genera 1, 3, 5 and 11 are **drawing choices**, not a claimed
threshold for the end theorem. The low-genus two-ended models reflect the
conjectural picture mentioned in Remark 1.2. The actual surfaces are not
identified with this mesh, and their entropy is not computed from it.
`catalogue-properties.json` retains separate all-genus and large-genus cases.

## Reproducible schematic

Set n=g+1, r²=x²+y², R=2.2, and

```text
w = min(0.64, 0.84 R sin(π/n)),  s = min(1, (6/n)^0.55),
h(r) = s [0.48 + 0.35 exp(−r²/1.7) + 0.19 (sqrt(1+r²)−1)],
p_j = R (cos(2πj/n), sin(2πj/n)),  j=0,…,n−1,
F(x,y,z) = z² − h(r)² [1 − 1.8 Σ_j exp(−|(x,y)−p_j|²/w²)].
```

The drawing is the level set F=0, truncated at r=4.6. This equation is an
independently chosen illustration, **not an equation from Ketover's paper**
and **not a solution of the shrinker PDE**. Local depressions form smooth
waists through z=0; away from them the two sheets approach the illustrative
cones z=±0.19 s r. The round neck arrangement, scale, waist size, central
height and cone slopes are arbitrary. No length is a measured shrinker length,
and R is not a determined value of the theorem's subsequential limiting radius.

`scripts/generate_ketover_geometry.py` uses marching cubes, simplifies the
triangulation, clips at the display radius, and projects vertices back to F=0.
It reuses the mesh clipping and topology helpers from the BNS generator;
the BNS drawing equation is not used. Required packages are NumPy,
scikit-image and fast-simplification:

```sh
python scripts/generate_ketover_geometry.py
```

The generated audit records one component, two boundary loops and Euler
characteristic −2g for every mesh. Independent tests also check orientability,
vertex links, g+1 waist loops, finite unit normals and circular display rims.
These are finite-mesh checks, not an existence proof or a certified PDE solve.

The viewer provides rotation, zoom, mesh, genus selection, top and side views,
a vertical cutaway, and a guide through the neck centers. Blue and gold mark
opposite sides of the same surface, not separate components. The cut is a
viewing aid, and the two outer rims are truncations rather than physical
boundaries. The SVG preserves the full-surface and cutaway views for printing
and use without JavaScript. The older batch schematic generator preserves it.
