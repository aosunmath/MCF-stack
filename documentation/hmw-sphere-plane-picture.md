# HMW sphere–plane picture

The figure for `ex:catalogue-hmw-one-ended` shows an original connected topology model, a cutaway, the prescribed horizontal trace, and a separate limiting configuration. It is **not a numerical self-shrinker**, an approximation with an error bound, or the initial surface flowing in the paper. No entropy is calculated from the drawing.

## Source review

Hoffman–Martín–White, *Generating Shrinkers by Mean Curvature Flow*, [arXiv:2502.20340v3](https://arxiv.org/abs/2502.20340v3), revised January 20, 2026, was checked in the supplied 50-page edition:

- Figure 1, p. 3: numerical illustrations of genera 1–6, credited to Francisco Torralbo. These motivate the geometry but are not reproduced or used as mesh data.
- Section 5, pp. 16–17: the Costa–Hoffman–Meeks symmetry group and the union `Qg` of `g+1` horizontal lines at angles `jπ/(g+1)`. The surface meets `{z=0}` in exactly those lines.
- Figure 5, p. 26: Mario Schulz's numerical genus-five illustration, including a cutaway showing the central sheet and lower cap. Our colors distinguish the two sides of one surface.
- Theorem 40, pp. 26–27: genus `g` for every positive integer, the horizontal trace, genus zero off the horizontal plane, and the entropy bound. One end is asserted only for sufficiently large genus.
- Figure 6 and the proof of Theorem 40, pp. 27–29: alternate planar sectors join an upper hemisphere, reflect by a horizontal half-turn, then complete the compact initial surface in `S²×R`. The local sphere–disk surgery has Euler characteristic `1−2g`; the compact initial surface has genus `2g`. The tangent shrinker is Euclidean and has genus `g`. The viewer does not simulate this flow or represent the whole initial surface.
- Theorems 41–42, pp. 29–31: strict entropy bound and the radius-two sphere plus plane limit. Convergence has multiplicity one and is smooth away from the equatorial intersection circle.
- Section 9, p. 40, and Lemma 64, pp. 45–46: the limit hypotheses and control of ends. No effective genus threshold or explicit cone profile is supplied.

The supplied PDF, rendered paper pages, and extracted text remain private. The existing source edition and audit hash are unchanged.

## Drawing equation and qualifications

For `n=g+1`, `r²=x²+y²`, and `a=1.35/n^1.65`, use the illustrative level set

```text
z (r²+z²−4) − a Im((x+iy)^n) (r²+1)^((3−n)/2) = 0.
```

This smooth implicit expression is reused from the catalogue's BNS topology picture. It encodes common topology and symmetry only; it neither identifies the constructed families nor imports BNS numerical data. At `z=0` its zero set is precisely `Qg`. It is invariant under vertical reflections at `(2j+1)π/(2n)`, vertical-axis rotations through `2π/n`, and half-turns about each line in `Qg`. The sampled mesh retains these features only approximately.

The coefficient and radial profile are drawing choices. At large radius the model has leading height `z≈r u(θ)`, where `u(1+u²)=a sin(nθ)`. This illustrative cone is not the unknown asymptotic cone of an HMW shrinker. The one exterior sheet is a feature of the model. Displayed genera 3, 5 and 11 are not claimed to exceed the theorem's unknown one-end threshold. The model does not solve `Hvec+Xperp/2=0`, and its spherical caps are only qualitatively motivated by the large-genus limit.

The generator uses the BNS illustration mesher (222×222×160 sampling grid, simplification, projection onto the drawing equation), clips the result at `r=3.8`, and recomputes normals. Mesh audits require one connected component, an orientable manifold with one circular truncation boundary, and Euler characteristic `1−2g`. These are checks of the displayed topology, not numerical PDE validation. The cutaway removes `y>0` without deforming the remaining geometry; its edges are artificial.

The separate limit view triangulates `S²(2) ∪ {z=0}`. The two pieces intersect along the equator; they are not a finite-genus embedded surface. The horizontal-trace view displays the exact lines `Qg`, truncated at the same arbitrary display radius. Multiple lines meeting at the origin do not imply a singular surface there.

## Interaction and regeneration

Rotation, keyboard controls, zoom, mesh display, a genus selector, and full/cutaway/trace/limit views are available. Horizontal lines can be overlaid on the schematic. Reset restores genus 5 and the initial camera. Failed model requests preserve the last valid drawing; missing or lost WebGL retains the static plate. Printing uses the SVG plate, with full and cutaway views and a separate limit inset.

Run `python3 scripts/generate_hmw_sphere_plane_geometry.py` with NumPy, scikit-image, fast-simplification and Pillow. Committed JSON/SVG files keep the normal build independent of these optional dependencies. `hmw-sphere-plane-audit.json` records the mesh counts and topology. The generic referenced-shrinker generator preserves this dedicated plate, including with `--output`.
