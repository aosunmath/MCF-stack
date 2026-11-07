# Knotted-expander picture

## Source review

Read Mramor and Shengwen Wang, *On knotted self expanders of the mean curvature flow in R3*, [arXiv:2611.02829v1](https://arxiv.org/abs/2611.02829v1), on November 6, 2026. The full eleven-page paper was read, with visual inspection of Figure 2 on page 9. Theorem 1.1 (page 2) describes the trefoil tube with three punctures and attached annuli. Section 2 constructs the annular barriers; Section 3, especially Corollary 3.2 and Figure 2 (pages 9–10), explains their use at the overpasses. This is a source review, not an independent verification of the existence proof. No source PDF or source figure is redistributed.

## What the picture represents

The main view is an original connected surface mesh, replacing the old curve with dashed attachment labels. It has genus one and three open display rims. Blue marks the knotted core; gold, terracotta, and green distinguish the three ends. Rotate to inspect over/under crossings and the open ends. The auxiliary views isolate the closed tube, the punctures, and the one-dimensional knot spine. The closed tube and spine are not examples of self-expanders.

The accompanying plate explains the topological operations in Theorem 1.1. It is not a reconstruction of the finite-ball Plateau competitors in Figure 2. In particular, the paper does not specify the drawing's attachment positions, cone openings, tube radius, or threefold geometric symmetry. These are illustrative choices. The annular barriers in the proof are not additional ends of the drawn surface.

The shown end flares suggest conical asymptotics. Neither the mesh nor its centerline solves the expander equation, and no error bound, normalization, entropy, or Gaussian-area value is inferred from it. The slider changes the truncation of one fixed model, not an existence parameter or time variable. Mathematical property records and permanent tags are unchanged.

## Reproducible geometry

Run `python3 scripts/generate_knotted_geometry.py` with NumPy, SciPy, scikit-image, fast-simplification, and Pillow. These are asset-generation dependencies; the ordinary build uses the committed JSON and SVG files. The author-survey generator preserves the new assets.

The drawing centerline is

```text
K(t) = (sin t + 2 sin 2t, -cos t + 2 cos 2t, 0.8 sin 3t),  0 <= t < 2 pi.
```

The main core uses a radius-0.27 neighborhood of the sampled polygonal knot. Three outward branches lie on the rays through its outer lobes, in directions `(0,1,0)` and `(±sqrt(3)/2,-1/2,0)`. At axial distance `s >= 3`, each branch radius is `0.26 + 0.13(s-3)`. A polynomial smooth union of width 0.18 joins the branches to the core. This is an implicit drawing function, not the self-expander equation. Marching cubes and mesh simplification generate its surface. Three planes at axial distance 5.2 truncate the ends; the browser can cut earlier along the same ends.

The closed auxiliary tube is triangulated directly using an orthonormal normal frame along `K`. Its radius is also 0.27. The static plate is rendered from the same models as the interactive viewer. Its geometry is embedded in the SVG as an original raster rendering with vector text.

## Verification

The committed audit records one connected component, three boundary loops, Euler characteristic −3, and genus one. Tests check consistent orientation, manifold vertex links, nondegenerate triangles, three distinct planar end rims, and the closed genus-one auxiliary tube. A separate projection check confirms three transverse crossings with alternating over/under order in the centerline. These checks concern the illustrative meshes, not the existence theorem or a PDE approximation.

Browser checks cover desktop and mobile layouts, rotation, zoom, all construction views, end truncation, mesh display, reset, static fallback, and print. The complete Python/JavaScript suites and build/link validation are required before publication.
