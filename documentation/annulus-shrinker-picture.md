# Annulus-dense shrinker: picture and flow

This revision reads Halldórsson's *Self-similar solutions to the curve shortening flow*, arXiv:1007.1617v2, Section 2 and Section 5, especially Theorem 5.1 and Lemmas 5.3–5.5 (PDF pp. 11–13). Figures 4–7 (pp. 17–18) were inspected. The PDF hash is already in `halldorsson-sources.json`; the source PDF and extracted text are not exported. The source's Figure 7 is captioned as an Abresch–Langer curve with large integer indices: it is not evidence that a particular finite numerical drawing is irrational.

The curves are smooth complete nonproper immersions of the line in the Euclidean plane. Use the left unit normal, curvature vector kN, and the time −1 normalization Hvec = −Xperp/2. In the source's notation this is A = 0, B = −1/2; its Section 5 proof uses B = −1. No rotation in time is introduced.

The generator `scripts/generate_annulus_shrinker.py` integrates

```
u' = uv, v' = 1/2 − u², theta' = u,
X = −2i exp(i theta)(u + iv),
(u,v,theta)(0) = (r_min/2,0,0).
```

The first downward zero of v is the outer contact; twice its arclength gives the phase period P. Shooting chooses r_min so that theta(P)/(2π) approaches one of two mathematically specified irrational targets:

| Profile | Target α | r_min | r_max | P |
| --- | --- | --- | --- | --- |
| Narrow annulus (initial selection) | 1/√2 − 1/100 | 0.8764333841 | 2.0333215592 | 6.4628911203 |
| Broad annulus (previous target retained) | (√5 − 1)/2 | 0.1514432308 | 3.5564212148 | 8.1283093684 |

These decimal values are numerical. Each excursion has 801 samples; subsequent excursions use rotation by 2πα. The displayed segment remains open, with no artificial closing edge. An orange excursion keeps its identity in all time slices. Increasing the number of excursions changes the finite parameter window and does not evolve the flow.

Both the static drawing and interactive viewer show t = −4, −1, −1/4, −1/16 with dilation factors 2, 1, 1/2, 1/4. The exact time law is X(s,t) = √(−t)X(s) for t < 0. The main canvas stays centered at the shrinker center and does not refit on time or excursion-count changes. Snapshot canvases share a world extent; manual zoom applies only to the main canvas. Dashed circles locate the image closure. They are not extra one-dimensional solutions or the boundary of a two-dimensional MCF. Time zero is described as a singular limit, never drawn as a regular immersed slice.

`site/assets/solitons/annulus-shrinker-audit.json` records the shooting residual, phase return, conservation of u exp(−|X|²/4), radial boundary relation, tolerance refinement, and comparison of twelve rotated excursions with a separate long integration. The largest continuation discrepancy is below 9×10⁻¹³ spatial units. These are floating-point diagnostics, not certified error bounds or a proof of irrationality. Independent tests differentiate sampled positions to compare the curvature with the normal velocity at several times.

The custom viewer is embedded inline in the existing sandboxed experiment page; it requires no network fetch, CDN, or module import. It retains the section route, permanent tags, and experiment anchor. Regenerating the broader Halldórsson figures calls this generator, preserving the improved viewer. The reader's mathematical properties are unchanged.

Reproduce the assets with `python3 scripts/generate_annulus_shrinker.py` in a NumPy/SciPy environment. Run the repository Python and JavaScript suites and complete build; inspect the full-page viewer and embedded section at desktop and mobile sizes before publication.
