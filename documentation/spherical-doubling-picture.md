# Spherical-doubling construction picture

The figure for `ex:catalogue-spherical-doubling-shrinkers` shows one connected closed surface: two nearby spherical sheets joined through radial necks on two reflected, aligned latitude circles. The original drawing is a **construction schematic**, not a solution of the shrinker equation, the paper's matched initial surface, or an approximation with an error bound. No Gaussian area or entropy is computed from it.

## Source review

Kapouleas–McGrath, *Generalizing the Linearized Doubling Approach, I: General Theory and New Minimal Surfaces and Self-Shrinkers*, [arXiv:2001.04240v4](https://arxiv.org/pdf/2001.04240v4), was read at the following relevant passages, with the spherical application also inspected in the rendered PDF:

- Introduction, pp. 1–4: the distinction between linearized doubling solutions, matched initial surfaces, and the final nonlinear correction.
- Definition 1.1 and Theorem A, p. 3: two graphical sheets, doubling holes, small catenoidal bridges, and genus `2gΣ − 1 + |L|`.
- Definitions 7.10–7.11 and Remark 7.12, p. 40: the dihedral and equatorial-reflection symmetries and the aligned configuration `L[s;(m)]` with `2m` sites.
- Equation (7.20), Definitions 7.24 and 7.29, and Lemma 7.30, pp. 41–43: the rotationally invariant linearized equation, flux balance, and the pole-regular solution.
- Theorem 9.40, pp. 65–66: closed embedded doublings, their genus, and multiplicity-two convergence.
- Equation (10.3) and Theorem 10.5, p. 66: the radius-two spherical background, potential `4 sech²s`, and existence for each fixed number of latitudes at sufficiently large `m`.

We retain the entry's two-latitude specialization, `k◦ = 2`, `m-vector = (m)`, in Euclidean three-space. The normalization is `H = <X,ν>/2`, with outward scalar convention `H = div ν`; the associated flow is `sqrt(-t) S_m` for `t < 0`. No explicit formula or effective small-`m` threshold for the constructed shrinker is claimed. The supplied PDF is not exported.

## Latitude guide

Equation (10.3) parametrizes the base sphere by

```text
X(θ,s) = 2(sech(s) cos θ, sech(s) sin θ, tanh(s)).
```

For the balanced two-circle RLD guide, integrate `φ'' + 4 sech²(s) φ = 0`. Let `E(0)=1`, `E'(0)=0` be the even solution and let `P` be regular at the north pole, normalized by `P(∞)=1`, `P'(∞)=0`. Equality of the two positive logarithmic fluxes gives

```text
−E'(s*)/E(s*) = P'(s*)/P(s*).
```

Our numerical calculation yields `s* ≈ 0.6225416993`, corresponding to geographic latitudes approximately `±33.5658653°`. The initial calculation truncates the pole at `s=15`; repeating at `s=18` with tighter tolerances changes `s*` by less than `10⁻¹¹`. This is a numerical balance check, not an interval certificate. The actual construction includes unbalancing, matching and nonlinear corrections; the displayed guide is not an exact finite-`m` neck location. At each of `±s*`, put `m` sites at longitudes `2πj/m`.

## Drawing geometry

The drawing uses spherical normal coordinates about `S²(2)`, chosen for illustration, rather than the source's Gaussian-metric Fermi coordinates. At a unit site direction `n`, choose an orthonormal tangent pair `e₁,e₂` and write

```text
q(t,θ) = cos(t/2)n + sin(t/2)(e₁ cos θ + e₂ sin θ),
X(u,θ) = (2 + h(u)) q(τ cosh u, θ).
```

Near the waist, `h(u)=τu`, so the local chart uses the catenoid meridian `t=τ cosh u`. At `t=b`, it joins the two spheres of radii `2±H`, where `H=τ acosh(b/τ)`. For `t≤0.6b` the catenoid profile is retained; between `0.6b` and `b`, the height is blended to `±H` using the quintic cutoff `w³(10−15w+6w²)`. Thus the sheet tangent and second derivative match at the outer collar. The joining formula is a drawing choice, not an exact catenoid in Euclidean space after the spherical coordinate map.

We set `b=min(0.4, 1.5 sech(s*) sin(π/m))` and `τ=0.22b`. These visibly enlarged necks do not model the source's quantitative gluing scale. Disjoint spherical patches and positive radial coordinates keep the smooth drawing model embedded. The symmetry is exact in the smooth model and the bridge-site arrangement; the background triangulation only approximates it.

A spherical convex-hull triangulation supplies two punctured sheets, and the neck annuli reuse the hole-boundary vertices. Independent mesh tests check connectedness, oriented edge incidence, circular vertex links, and Euler characteristic. The models `m=6,10,14` have `12,20,28` bridges and genera `11,19,27`. These are topology checks on illustrations, not existence assertions about shrinkers at those values of `m`.

## Interaction and regeneration

The viewer supports rotation, zoom, mesh display, three bridge counts, and a vertical half-space cutaway. A separation slider applies the positive radial deformation `r ↦ 2+a(r−2)` for `0.6≤a≤1.8`; it is an illustration control, not a proved family parameter. Normals are recomputed after deformation. Colors identify the outer sheet, inner sheet, and neck region. Cut edges occur only in the display; the intact model has no boundary. Failed model loads retain the previous valid mesh. Reset restores the default `m=10`, camera and separation. A standalone SVG shows the intact surface, cutaway and local neck section for printing and readers without WebGL.

Run `python3 scripts/generate_spherical_doubling_geometry.py` with NumPy, SciPy and Pillow. The self-contained SVG embeds supersampled mesh views and retains vector labels and a vector neck section. Committed geometry keeps the site build independent of those libraries. The audit is `site/assets/solitons/sphere-doubling-audit.json`. The older schematic generator preserves this reviewed figure.
