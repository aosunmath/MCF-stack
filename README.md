# MCF-stack: Special Solutions of Mean Curvature Flow

**[Read the stack → aosunmath.github.io/MCF-stack](https://aosunmath.github.io/MCF-stack/)**

[Contents](https://aosunmath.github.io/MCF-stack/chapters/) · [Search](https://aosunmath.github.io/MCF-stack/search/) · [Bibliography](https://aosunmath.github.io/MCF-stack/references/)

MCF-stack is a growing mathematical reference collecting **special solutions of mean curvature flow**, including self-shrinkers, translators, self-expanders, ancient solutions, and other geometrically meaningful examples. Following the idea of the [Stacks Project](https://stacks.math.columbia.edu/), it aims to connect definitions, constructions, properties, and classification results through permanent tags, cross-references, and precise source attribution.

For each family of solutions, the goal is to record its defining equation, dimensions and topology, geometric properties, construction or existence results, and relevant references. Explicit formulas, rigorous theorems, conjectures, and numerical evidence should be clearly distinguished.

## A quick introduction to mean curvature flow

Mean curvature flow evolves a curve, surface, or higher-dimensional submanifold by its mean curvature vector. If $X:M^n\times I\to\mathbb R^{n+1}$ describes a family of immersed hypersurfaces, the geometric equation is

$$
(\partial_t X)^\perp=\mathbf H,
$$

where $\mathbf H$ is the mean curvature vector and $\perp$ denotes projection onto the normal space. We use $H=\operatorname{div}_M\nu$ and $\mathbf H=-H\nu$; for a round sphere, $\nu$ points outward and $H>0$, so the sphere shrinks.

The flow is the gradient flow of area. For a smooth closed submanifold,

$$
\frac{d}{dt}\operatorname{Area}(M_t)=-\int_{M_t}|\mathbf H|^2\,d\mu_t.
$$

Although the flow decreases area, it can develop singularities. Special solutions provide concrete examples and geometric models for understanding singularities, rescaling limits, and long-time behavior.

## Special solutions

The following equations use the mean curvature vector convention above. The normalizations fix the center at the origin and the shrinker or expander scale.

| Family | Defining equation | Associated flow |
| --- | --- | --- |
| Self-shrinkers | $\mathbf H+X^\perp/2=0$ | $M_t=\sqrt{-t}\,\Sigma$, $t<0$ |
| Translators | $\mathbf H=V^\perp$, with constant velocity $V$ | $M_t=\Sigma+tV$ |
| Self-expanders | $\mathbf H-X^\perp/2=0$ | $M_t=\sqrt{t}\,\Sigma$, $t>0$ |
| Stationary solutions | $\mathbf H=0$ | $M_t=\Sigma$ |

The collection also includes **ancient solutions**, defined for all $t<T$ for a finite $T$; **eternal solutions**, defined for every real time; and rotating or more general self-similar solutions. Ancient and eternal describe time domains and do not imply that a solution is a soliton.

The first catalogue contains **31 entries in four categories**:

| Category | Entries | Examples |
| --- | ---: | --- |
| [Shrinkers](https://aosunmath.github.io/MCF-stack/chapters/shrinkers/) | 10 | Spheres and cylinders, Abresch–Langer curves, Angenent torus, Drugan sphere, Clifford torus, higher-genus constructions |
| [Translators](https://aosunmath.github.io/MCF-stack/chapters/translators/) | 11 | Grim reapers, bowl, translating catenoids, delta-wings, Scherkenoids, pitchforks, gluing constructions |
| [Expanders](https://aosunmath.github.io/MCF-stack/chapters/expanders/) | 6 | Corner smoothings, graphical cones, one- and two-sheeted double-cone smoothings, mean-convex cones, planar networks |
| [Other special flows](https://aosunmath.github.io/MCF-stack/chapters/other-special-flows/) | 4 | Stationary catenoid, Whitney sphere evolution, degenerate neckpinches, ancient Angenent oval |

Every entry has a figure: 17 support rotation and zoom, including a fourth-coordinate rotation for the Clifford torus and a time slider for the ancient oval. Captions distinguish **exact formulas, numerical ODE solutions, projections, and schematics**. Noncompact surfaces are truncated for display; higher-dimensional examples use profiles or diagrams. A schematic does not claim to solve the geometric PDE.

The catalogue records source-supported properties and precise theorem or page locators. It is a first selection from the supplied paper collection, not an exhaustive classification. See the [source and illustration notes](documentation/catalogue-expansion.md) for editions, normalization choices, and reproducible geometry.

## Reading and contributing

The website supports keyword and tag search, permanent links, citations, and expandable proofs. This initial edition inherits the mathematical library of [GMT-stack](https://github.com/aosunmath/GMT-stack); its GMT and variational chapters remain available as background while the special-solutions collection develops. The collection is not exhaustive, and no independent human review or formal verification is claimed.

Corrections and contributions are welcome through [issues](https://github.com/aosunmath/MCF-stack/issues) and pull requests. Include precise references, complete hypotheses, and a clear account of proof status. Preserve existing tags and source labels. See [AGENTS.md](AGENTS.md) and the [integration guide](documentation/integration-layout.md).

## Building the website

Requires Python 3.11+, Node.js/npm, and Git:

```sh
git clone https://github.com/aosunmath/MCF-stack.git
cd MCF-stack
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm ci --prefix vendor --ignore-scripts --no-audit --no-fund
.venv/bin/python scripts/build.py
python3 -m http.server 8000 --directory _site
```

Open [localhost:8000](http://localhost:8000/). The active manuscript is in `content/gmt-foundations/`; the inherited source slug is retained to preserve permanent tags. The shared project identity and website address are configured in `scripts/project.py`.

Before publishing, run:

```sh
.venv/bin/python -m unittest discover -s tests
node --test tests/*.test.mjs
.venv/bin/python scripts/build.py
```

GitHub Pages serves the prebuilt `docs/` directory from `main` at **[aosunmath.github.io/MCF-stack/](https://aosunmath.github.io/MCF-stack/)**. See the [deployment guide](documentation/deployment.md) for setup and publication checks.

## Attribution

MCF-stack is derived from [GMT-stack](https://github.com/aosunmath/GMT-stack), using [Mingchen Xia’s Pome framework](https://github.com/MingchenXia/Pome) and the Gerby renderer. The original infrastructure copyright and [MIT license](LICENSE) are preserved. Mathematical contributions must retain their source attribution and applicable licenses. MCF-stack is inspired by the Stacks Project and is an independent project.
