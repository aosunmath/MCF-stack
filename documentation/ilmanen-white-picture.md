# Ilmanen–White two-ended illustration

The revised original illustration follows Tom Ilmanen and Brian White,
*Fattening in Mean Curvature Flow*, the published 32-page version,
[arXiv:2406.18703v3](https://arxiv.org/pdf/2406.18703v3), 4 April 2025.
The paper was read directly, including its figures and the graph, topology,
symmetry, and large-genus arguments. No source PDF, extracted paper figure,
or full text is redistributed.

## Source geometry

- Figure 1, p. 2, credited to David Chopp, illustrates genus three and two
  ends. The introduction, p. 3, describes the relation of Chopp's numerical
  examples to the constructed shrinkers cautiously. Our default has the same
  topology; it is not a reconstruction of that numerical surface.
- Theorem 1.1, p. 2: for every wheel parameter g ≥ 3, the tangent shrinker
  has genus h = g − 1 and two ends. The viewer uses **surface genus h**.
- Definition 2.1, p. 4, and preservation of symmetry: horizontal reflection,
  rotation by 2π/(h+1), and vertical reflection planes at jπ/(h+1).
- Theorem 4.8, pp. 10–11, Lemma 7.1, pp. 18–19, and Theorem 7.6,
  pp. 20–21: the upper part is a positive graph over the unbounded component
  of the horizontal complement. Its reflection is the lower part. The parts
  join along h+1 smooth simple closed curves in z=0. Each outer sheet is
  smoothly asymptotically conical; the cone links lie strictly on opposite
  sides of the equator. These are not asserted to be round cones.
- Corollary 4.9, p. 11: doubling the plane with h+1 disks removed along its
  inner boundary curves gives genus h and two ends. The bounded displayed
  mesh has Euler characteristic −2h and two outer boundary loops.
- Lemmas 9.1 and 9.3, pp. 25–26, describe angular monotonicity and the
  decrease from the axis toward an inner neck boundary and increase outward
  from the outer neck boundary on a reflection ray. These motivate the
  central cap, neck depressions, and flaring ends.
- Theorems 9.4–9.5, pp. 26–28: the large-genus limit is a double plane;
  after taking a subsequence the surface convergence is smooth away from
  one circle. The theorem supplies no measured circle radius or convergence
  rate. The flattening between selectable models is only illustrative.

All shown genera (2, 3, 5, 11) lie in the existence theorem's range. None is
claimed to satisfy a known effective threshold for fattening. The picture
does not identify this construction with Ketover's family. The existing
`catalogue-properties.json` record already has the source-supported genus,
embeddedness, end and entropy qualifications and is unchanged.

## Reproducible drawing equation

For n=h+1, r²=x²+y², set R=2 and

```text
w = min(0.92, 0.80 R sin(π/n)),  s = min(1, (4/n)^0.65),
q(x,y) = Re[((x+iy)/sqrt(r²+R²))^n],
a(x,y) = s [0.48 + 0.50 exp(−r²/1.7)
                    + 0.27(sqrt(1+r²)−1)] [1−0.12 q(x,y)],
p_j = R (cos(2πj/n), sin(2πj/n)),  j=0,…,n−1,
D(x,y) = 1.8 Σ_j exp(−|(x,y)−p_j|²/w²),
F(x,y,z) = z² − a(x,y)² [1−D(x,y)].
```

The drawing is F=0, truncated at r=4.6. Its two graphs are
z=±a sqrt(1−D) over D<1. At D=1 they join in neck waists. Horizontal
reflection is built into the equation; the regular array has the paper's
dihedral symmetries. The illustrative end slopes are
±0.27s[1−0.12 cos(nθ)], so the asymptotic links have n-fold symmetry.
All lengths, slopes, neck profiles and the flattening factor s are drawing
choices. **This equation is not from the paper and does not solve the
self-shrinker PDE.** No entropy is measured from the drawing. The underlying
analytic drawing has exact symmetries; its triangulation approximates them.

`scripts/generate_iw_geometry.py` uses marching cubes and simplification,
clips to a circular display boundary, and projects vertices back onto F=0.
This is geometric meshing, not a numerical solution of the shrinker
equation. It shares clipping and mesh topology helpers with the BNS
illustration, not the BNS drawing equation. Run with NumPy, scikit-image,
and fast-simplification installed:

```sh
python scripts/generate_iw_geometry.py
```

The generated audit records connectivity, Euler characteristic, genus and
boundary loops. Independent tests also check edge orientation, vertex
links, h+1 equatorial loops, finite unit normals and the display rims.
These checks concern the finite mesh, not a proof of the shrinker theorem.

## Reading the picture

The interactive model supports rotation, zoom, genus selection, a diagonal vertical
cutaway, top and side views, mesh edges, and an equatorial-curve overlay.
The overlay is the displayed mesh's intersection with z=0; it explicitly
shows hidden portions as well. It is not an extra component. Blue and gold
distinguish opposite sides of a single connected surface. The two outer
rims truncate the infinite ends, and cutaway edges are viewing artifacts.

The static SVG shows a full surface and a cutaway, with source attribution
and the schematic qualification. It is available without JavaScript and
when printing. The older batch generator preserves this revised figure,
including when an alternate output directory is selected.
