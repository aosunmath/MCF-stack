# Nguyen translating tridents: picture review

The replacement picture is an original connected construction schematic in R³, not a numerical translator or an approximation with a proved error bound. It does not compute Gaussian area or entropy. The original intersecting-input drawing remains an unlinked asset for reproducibility of the earlier generator.

## Sources and conventions

- X. H. Nguyen, *Translating Tridents* (2009), DOI [10.1080/03605300902768685](https://doi.org/10.1080/03605300902768685). The [author-posted manuscript text](https://www.researchgate.net/publication/243046956_Translating_Tridents) was reviewed: Theorem 1 (p. 2), Sections 1.2–1.4 (pp. 3–4), Section 2 and Definitions 4–5 (pp. 5–7), and the nonlinear correction in Section 5 (pp. 18–19). The source uses translation in the first coordinate and the exact minimal ingredient `sin(v) = sinh(u) sinh(w)`. Its construction unbalances the wings, matches grim-reaper ends with cutoffs, and then solves a nonlinear perturbation problem. Its four wings are not an assertion of four topological ends of the full periodic surface.
- Hoffman–Martín–White, *Nguyen's Tridents and the Classification of Semigraphical Translators for Mean Curvature Flow*, [arXiv:1909.09241v2](https://arxiv.org/abs/1909.09241v2), 26-page edition. Theorem 1 and Figures 1–2 (pp. 1–3) were read and the two figures inspected. Their downward convention is reflected vertically here. Their period is `2a`; the half-width `b(a)` is in `(π/2,π)`. The small-period limit is a bisecting plane and grim cylinder. These tridents coincide with Nguyen's small-period family. Proper embeddedness and entropy 3 in the metadata come from this source, not the mesh.

PDFs, extracted text, and source figures are not included in the repository or website.

## Drawing map

For an illustrative positive scale ε, apply the following diffeomorphism to the exact Scherk surface `sin(v) = sinh(u) sinh(w)`:

```text
x = ε v,
y = atan(sinh(ε w)),
z = ε u + log(cosh(ε w)).
```

The target domain is `x,z ∈ R`, `|y|<π/2`. The map is one-to-one with positive nonzero Jacobian (up to coordinate order), and has a smooth inverse. Thus it preserves the embeddedness and topology of Scherk. Its period is `2πε` in x. The asymptotic input `u=0` maps to `z=-log(cos y)` and `w=0` maps to `y=0`. The two bent wings rise toward `y=±π/2`, while the central sheet extends both upward and downward. Half-turn symmetry about each vertical line at `x=nπε,y=0` and reflection in `x=πε/2+nπε` are retained by the smooth drawing model. Triangulation retains these only approximately.

Equivalently, the drawing is the regular level surface

```text
U = (z + log(cos y))/ε,
W = asinh(tan y)/ε,
tanh(U) tanh(W) - sin(x/ε) sech(U) sech(W) = 0.
```

The map is our drawing choice, not Nguyen's matched initial surface. In particular it fixes half-width π/2 at positive period, whereas actual tridents have larger half-width. The choices ε = 0.22, 0.35, 0.50 are illustrative scales, not certified solutions or an effective existence range. No translator residual or accuracy is asserted. The ε-dependent Scherk period is a geometric feature of this model, not a numerical calculation of the actual width-versus-period relation.

## Meshing and interaction

`scripts/generate_trident_geometry.py` samples the implicit surface on a 290×152×194 grid, simplifies to 28,000 triangles, and projects vertices back to the illustrative level set, constraining boundary coordinates. The bounds are `(-3π+0.13)ε ≤ x ≤ (3π+0.13)ε`, `|y|≤1.565`, and `-1.8≤z≤2.8`. The slight phase offset avoids placing an entire mesh boundary on a symmetry axis. These are artificial display cuts.

Each mesh has one connected component, two boundary loops, Euler characteristic −4 and genus 2. This is the topology of this three-period crop, not a claim of finite genus for a complete trident. Edge orientation and vertex links are also tested. The bounded implicit residual is only a check of the chosen drawing equation, not of the translator equation.

The viewer supports drag and keyboard rotation, zoom, mesh display, three illustrative neck scales, a half-surface view, and an end view near the periodic direction. WebGL depth testing makes the sheet occlusion correct. The static fallback and printable SVG are original renderings of the same default mesh. The input surfaces and the new connected drawing are not overlaid as if they were separate components.

Regenerate with NumPy, scikit-image, fast-simplification, and Pillow installed:

```sh
python scripts/generate_trident_geometry.py
```
