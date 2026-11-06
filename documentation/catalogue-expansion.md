# Special-solution catalogue

The first addition has 31 entries: 10 shrinkers, 11 translators, 6 expanders, and 4 other special flows. Each has its own stable source label and a picture. The four `catalogue-*.tex` manuscripts in `content/gmt-foundations/` are the mathematical source; `collection.json` groups their sections. Existing tags and background sections are retained.

## Sources and scope

The supplied collection contains 101 PDF files, representing 100 distinct file hashes. Selected passages were read to identify examples and check their stated properties. The [evidence map](catalogue-source-audit.json) records files, hashes, entry-level locators, and normalization notes. The manuscript's `source-inventory.json` records supplied editions and review status. Inventory status does not imply a complete reading. Original PDFs, extracted text, and private absolute paths are excluded from exports.

Formulas specify normalization, dimension, parameters, domain, and time where available. Other entries collect the properties established in the cited sources, with qualifications on uniqueness, stability, asymptotics, and existence ranges. These lists are limited to those sources. Construction proofs remain external unless an existing local proof is explicitly linked; no formal verification is claimed.

The normal convention is H = div(nu), mean curvature vector = −H nu. Shrinkers satisfy Hvec = −Xperp/2, expanders Hvec = Xperp/2, and translator diagrams move upward at unit speed. Smoczyk's shrinkers and the network-flow expanders require a sqrt(2) spatial conversion. The supplied translator papers often use downward velocity. The width ratio in the supplied Graphical Translators Theorem 2.4 is corrected using its defining formula. Neckpinch tip mean curvature and the norm of the second fundamental form differ by sqrt(n). Exact editions and details are recorded in the evidence map.

## Pictures

`catalogue-visualizations.json` binds each mathematical entry to an original illustration. Seventeen have an interactive canvas with keyboard rotation and zoom; the remaining fourteen use static diagrams of topology, domains, asymptotics, or gluing inputs. Every entry also has an SVG for printing and use without JavaScript. “Open drawing” shows the larger SVG. The ancient oval has a time slider at a fixed spatial scale; the Clifford torus has a fourth-coordinate rotation before projection.

The Angenent torus, Abresch–Langer curve, bowl, translating catenoid, and graphical/neck expanders use numerical ODE integration. They are not substituted by generic tori, paraboloids, or arbitrary connecting surfaces. Closure residuals in `site/assets/solitons/geometry-audit.json` describe integration before rounding the exported coordinates; they are numerical diagnostics, not error bounds or existence proofs. Displayed finite pieces of noncompact solutions have artificial truncation boundaries. The Whitney figure is the exact initial generating profile, not a formula for its later evolution.

Committed assets make the ordinary site build independent of numerical libraries. To regenerate figures, use a Python environment with NumPy and SciPy:

```sh
python3 scripts/generate_soliton_geometry.py
python3 scripts/generate_shrinker_schematics.py
python3 scripts/generate_translator_schematics.py
python3 scripts/generate_expander_schematics.py
```

The schematic generators use only the standard library; the shrinker script also reads the generated numerical profiles. Regenerate geometry first. All illustrations are original mathematical drawings, not copied paper figures.

The permanent contribution rules are in `AGENTS.md`. Keep additions local until publication is requested.
