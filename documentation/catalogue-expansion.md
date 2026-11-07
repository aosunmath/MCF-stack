# Special-solution catalogue

The current catalogue has 52 example families: 25 shrinkers, 13 translators, 6 expanders, and 8 other special flows. The initial 31-entry addition is recorded in the original evidence map; [the research expansion](research-expansion.md) adds 11 families from Ao Sun’s papers and their references. The [prescribed-tangent-flow reference expansion](prescribed-tangent-shrinkers.md) adds another ten shrinker construction families. Each has its own stable source label and a picture. The four `catalogue-*.tex` manuscripts in `content/gmt-foundations/` are the mathematical source; `collection.json` groups their sections. The introduction and these four categories are the complete reading collection. Catalogue tags are retained; the inherited GMT background chapters have been removed.

## Sources and scope

The supplied collection contains 101 PDF files, representing 100 distinct file hashes. Selected passages were read to identify examples and check their stated properties. The [evidence map](catalogue-source-audit.json) records files, hashes, entry-level locators, and normalization notes. The manuscript's `source-inventory.json` records supplied editions and review status. Inventory status does not imply a complete reading. Original PDFs, extracted text, and private absolute paths are excluded from exports.

Formulas specify normalization, dimension, parameters, domain, and time where available. Other entries collect the properties established in the cited sources, with qualifications on uniqueness, stability, asymptotics, and existence ranges. These lists are limited to those sources. Construction proofs remain in the cited papers; selected elementary calculations are given directly in the entries. No formal verification is claimed.

The normal convention is H = div(nu), mean curvature vector = −H nu. Shrinkers satisfy Hvec = −Xperp/2, expanders Hvec = Xperp/2, and translator diagrams move upward at unit speed. Smoczyk's shrinkers and the network-flow expanders require a sqrt(2) spatial conversion. The supplied translator papers often use downward velocity. The width ratio in the supplied Graphical Translators Theorem 2.4 is corrected using its defining formula. Neckpinch tip mean curvature and the norm of the second fundamental form differ by sqrt(n). Exact editions and details are recorded in the evidence map.

## Pictures

The [Abresch–Langer index controls](abresch-langer-controls.md) let readers compute other admissible coprime pairs, with numerical period and closure checks. The fixed SVG and print view retain the (2,3) reference.

`catalogue-visualizations.json` binds each mathematical entry to an original illustration. Interactive figures support keyboard rotation and zoom; static diagrams show topology, domains, asymptotics, or gluing inputs. Every entry also has an SVG for printing and use without JavaScript. The Møller entry additionally has a separate interactive handle schematic with three genus choices. “Open drawing” shows the larger SVG. The ancient oval, ancient torus curve, and eternal helix have time sliders at fixed spatial scales; the Clifford torus and torus curve have a fourth-coordinate rotation before projection.

The Angenent torus, Drugan sphere, Abresch–Langer curve, bowl, translating catenoid, and graphical/neck expanders use numerical ODE integration. They are not substituted by generic tori, paraboloids, or arbitrary connecting surfaces. Closure residuals in `site/assets/solitons/geometry-audit.json` describe integration before rounding the exported coordinates; they are numerical diagnostics, not error bounds or existence proofs. Displayed finite pieces of noncompact solutions have artificial truncation boundaries. The Whitney figure pairs the exact initial geometry with numerical PDE snapshots of its n=2 equivariant evolution; its surface is shown only by a labeled projection from R4. See [the numerical construction and diagnostics](whitney-flow-picture.md).

Committed assets make the ordinary site build independent of numerical libraries. To regenerate figures, use a Python environment with NumPy and SciPy; the Drugan generator also uses Matplotlib:

```sh
python3 scripts/generate_soliton_geometry.py
python3 scripts/generate_drugan_geometry.py
python3 scripts/generate_shrinker_schematics.py
python3 scripts/generate_moller_geometry.py
# Additional numerical meshing dependencies are listed in moller-picture.md:
python3 scripts/generate_moller_genus_models.py
python3 scripts/generate_kkm_geometry.py
python3 scripts/generate_nguyen_geometry.py
python3 scripts/generate_translator_schematics.py
python3 scripts/generate_expander_schematics.py
python3 scripts/generate_ancient_curve_geometry.py
python3 scripts/generate_immortal_flow_schematics.py
python3 scripts/generate_new_shrinker_schematics.py
python3 scripts/generate_referenced_shrinker_schematics.py
python3 scripts/generate_torus_cylinder_slices.py
python3 scripts/generate_spherical_doubling_geometry.py
python3 scripts/generate_prescribed_end_schematics.py
```

The schematic generators use only the standard library; the shrinker script also reads the generated numerical profiles. Regenerate geometry first. All illustrations are original mathematical drawings, not copied paper figures.

The [Drugan numerical picture](drugan-numerical-picture.md) documents the pole expansion, reflection shooting, convergence checks, and cutaway convention. Its separate `drugan-audit.json` records the numerical settings and residuals.

The permanent contribution rules are in `AGENTS.md`. Completed modifications are committed and pushed after verification by default, following the user's standing preference; a later request for local-only work takes precedence.

The [Møller picture](moller-picture.md) records the sphere–torus cutaway, numerical intersection checks, and the distinction between the singular gluing input and a smooth finite-genus surface.

The [KKM construction picture](kkm-picture.md) uses the paper’s Scherk ingredient to show a connected joining belt, with a cutaway, illustrative period counts, and adjustable end waviness. Its generator additionally requires scikit-image and fast-simplification. It does not solve the shrinker equation.

The [spherical-doubling picture](spherical-doubling-picture.md) shows connected inner and outer sheets, radial necks, and a cutaway. A numerical balanced linearized latitude guide informs the site placement; the mesh is a construction schematic, not a solved shrinker. Its generator additionally uses Pillow to render compact static mesh views.

The [Nguyen construction picture](nguyen-picture.md) shows the connected Scherk saddle belt, a cutaway, and a separately rotatable unwrapped Scherk minimal ingredient. The global mesh and end profile are explicitly schematic. Regeneration uses NumPy, scikit-image, fast-simplification, and Pillow.

The [Δ-wing picture](delta-wing-picture.md) now uses a numerical solution of the rectangular translator Dirichlet problem, with a height cut and two interactive profile views. Its exact tilted grim-reaper comparison is kept distinct from the computed surface.

The [Scherk translator picture](scherk-picture.md) computes a finite-boundary rectangular translator graph and displays its vertical half-turn extensions. It distinguishes numerical PDE data from small interpolated corner fills, records refinement checks, and offers rotation, zoom, a fundamental-patch view and height clipping. Regeneration requires NumPy, SciPy, contourpy and Pillow.
