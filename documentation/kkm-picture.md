# KKM construction picture

The illustration for `ex:catalogue-kkm-one-end` is an original, rotatable construction schematic. It shows a connected surface with the topology of the sphere–plane desingularization, rather than just the intersecting input surfaces. It is **not a numerical solution of the self-shrinker equation**, a reproduction of the paper's initial surface, or an approximation with an error bound.

## Source review

Kapouleas–Kleene–Møller, *Mean curvature self-shrinkers of high genus: Non-compact examples*, [arXiv:1106.5454v3](https://arxiv.org/pdf/1106.5454v3), was checked at these locators:

- Theorem 1.1, PDF p. 2: complete embedded surfaces in R³, every sufficiently large genus, one end, symmetry and sphere–plane limit.
- Figure 1, p. 3: Ilmanen's picture is explicitly captioned as conjectural, with genus eight.
- Equation (1.2), p. 4: the end height is `r sigma(theta) + O(1/r)`, with nonzero angular profile; the paper does not provide a closed formula for that profile.
- Section 2, pp. 5–6: distinguish the initial surfaces from the final normal graph obtained by solving the nonlinear equation.
- Definitions 5.1–5.2 and equation (5.1), p. 9: the Scherk surface `sinh(u) sinh(v) = sin(w)`, period `2 pi`, with half-period translation combined with reflection.
- Definitions 5.7 and 5.10, pp. 11–12: curling, cap matching and attachment of four wings. Remark 5.12 gives `k = g+1`. We use “periods” to avoid confusing the remark's `2k` Scherk-handle terminology with the wording of Figure 1.

The supplied PDF remains private and is not exported. Its existing inventory hash and edition are unchanged.

## Drawing geometry

For `k = 6, 9, 12`, put `w = k theta` in the Scherk equation and use the illustrative map

```text
r = 2 exp(u/k) sech(v/k),   z = 2 tanh(v/k),
(x,y,z) = (r cos(theta), r sin(theta), z).
```

The asymptotic planes `u=0` and `v=0` map respectively to the radius-two sphere and the horizontal plane. The four wings approach the two caps, the central disk, and the exterior sheet. This map agrees with the local radius-two scaling at the joining circle; it is our drawing map, not KKM's cutoff and cap-matching map. Its image does not satisfy the self-shrinker equation. The smooth model inherits the rotation by `2 pi/k`, the rotation by `pi/k` followed by vertical reflection, and the vertical reflection plane at angle `pi/(2k)`; discretization does not preserve these symmetries exactly.

The mesh is extracted from the bounded implicit equation

```text
tanh(u) tanh(v) - sin(k theta) sech(u) sech(v) = 0,
v = k atanh(z/2),
u = k log(r / (2 sqrt(1-z²/4))).
```

Marching cubes on a `181 × 181 × 108` Cartesian grid, followed by mesh simplification and clipping to `r ≤ 3.65`, gives the finite drawing. The sphere poles and central disk are included. The mesh audit checks connectedness, edge incidence, one boundary loop and Euler characteristic: `-9, -15, -21`, respectively, giving model genera `5, 8, 11`. These are mesh topology checks, not a proof about an individual KKM surface or a guarantee that these low genera fall in its existence range.

An optional vertical shear gives the exterior a visible cone:

```text
z -> z + a r sin(k theta) h(r),
h(r) = 0 (r ≤ 2.35), h(r) = 1 (r ≥ 3.20),
h(r) = 6t^5 - 15t^4 + 10t^3, t=(r-2.35)/0.85, between these radii.
```

The default amplitude is `a=0.075`. The shear preserves the smooth model's topology and the stated discrete symmetries. This freely chosen sine profile represents the qualitative end behavior only; it is not the source's `sigma`, and its amplitude is not a modulus proved to occur among shrinkers. Setting it to zero displays the plane-asymptotic construction model, explicitly distinguished in the viewer from the theorem's nonplanar end. No Gaussian area or entropy is calculated from this mesh.

Colors identify sphere-like caps, the joining belt, and the disk/exterior region. They are region labels, not curvature values. Cutaway removes a fixed angular wedge without changing the other vertices. Dragging, keyboard rotation, zoom, mesh display, three period counts and the end-waviness slider work on the finite model. Reset restores the default nine-period model and camera. Failed model loads retain the previous valid drawing. The SVG supplies a full view and a cutaway for printing and readers without JavaScript.

## Regeneration

Run `python3 scripts/generate_kkm_geometry.py` in an environment with NumPy, scikit-image and fast-simplification. Committed meshes and SVGs keep the normal site build independent of these libraries. The older generic schematic generator no longer writes the KKM asset. The topology audit is in `site/assets/solitons/kkm-audit.json`.
