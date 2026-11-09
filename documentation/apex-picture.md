# Prescribed apex curvatures: surface comparison

The original ellipse diagram is replaced by three representatives in Euclidean
three-space, with rotation, zoom, a half-cut, a height cut, and principal sections.
The theorem also concerns higher dimensions; these surfaces do not represent a
slice or projection of an unspecified higher-dimensional member.

## Source checked

The supplied 28-page July 5, 2018 edition of Hoffman–Ilmanen–Martín–White,
*Graphical Translators for Mean Curvature Flow*,
[arXiv:1805.10860v2](https://arxiv.org/abs/1805.10860v2), was read at equations
(1.2)–(1.4), Figure 3, Sections 3–4, Theorem 7.1, Theorem 8.1 and its proof,
Corollary 8.2, Section 9, and the final discussion of Section 11. The PDF is not
redistributed. The paper's downward convention is reflected vertically: all
three pictures satisfy the upward unit-speed equation

```text
Q(u) = [(1+u_y²)u_xx − 2u_x u_y u_xy + (1+u_x²)u_yy]
       / (1+u_x²+u_y²) = 1,
u(0)=0,  M_t=graph(u)+t e₃,  −∞<t<∞.
```

At a horizontal tangent, the nonnegative apex curvature data here are the
eigenvalues of D²u(0). Hence k₁+k₂=1. This is the convex-curvature convention;
with the site's H=div(ν) convention the upward graph normal has negative scalar
mean curvature. The positive values must not be mistaken for its signed H.

Section 8 constructs solutions by solving zero-Dirichlet problems on ellipsoids,
tuning their aspect ratios to the desired Hessian, and taking a centered limit
as the apex height diverges. It supplies no closed formula for the general
translator. The illustration does not identify ellipsoid coefficients with
apex curvatures or use an anisotropic paraboloid as a global surface.

## Three representatives

- **Grim-reaper cylinder:** k=(0,1), exact u(x,y)=−log cos y on
  ℝ×(−π/2,π/2). A zero eigenvalue gives translation invariance. The minimum
  is a whole line, not an isolated point. Display cuts are |x|≤8 and u≤6.
- **Δ-wing:** the committed numerical PDE solution from
  [the Δ-wing computation](delta-wing-picture.md), on the strip of width √2π.
  It uses the rectangular Dirichlet exhaustion from Sections 3–4, rather than
  rerunning the ellipsoid construction. Its measured apex Hessian is
  (0.2442666335, 0.7557334962). These are finite-domain numerical values, not
  an exactly prescribed pair or an exact formula relating width and curvature.
- **Bowl:** k=(½,½), sampled by integrating f′=p,
  p′=(1+p²)(1−p/r), starting with f=r²/4+r⁴/128+O(r⁶).
  Equal apex curvatures give rotation invariance by Theorem 8.1(5).
  The numerical mesh ends at height 6; the complete graph is entire.

No interpolation of meshes is used to invent intermediate family members.
In R³, Theorem 7.1 identifies the unequal positive cases with Δ-wings. The
higher-dimensional existence statement and its qualifications remain unchanged.
No property metadata is inferred from the meshes.

## Diagnostics and reproducibility

Run `python scripts/generate_apex_translators.py` with NumPy, SciPy and
Matplotlib. The generator reuses the committed Δ-wing mesh and audit, recording
the input mesh's SHA-256 in `site/assets/solitons/apex-audit.json`.
Its sampled interpolant residual is 0.000604; its reported domain and transverse
grid comparisons change displayed heights by 0.00623 and 0.00817 respectively.
The bowl uses DOP853 with ε=10⁻⁵, rtol=2×10⁻¹¹ and atol=2×10⁻¹²;
halving ε and tightening tolerances changes the sampled profile height by
about 1.2×10⁻¹⁰. These are floating-point checks, not certified error estimates.
PDE, finite-domain, interpolation and mesh errors remain as documented in the
Δ-wing audit. The normal website build uses only the committed assets.

The static plate uses a common spatial scale for its three surface views and
common axes for the section plots. Interactive surface views fit the selected
patch to the window. In the principal-section view, blue is u(s,0), ochre is
u(0,s), and dashed curves are ½kᵢs², restricted to |s|≤1. The two bowl
sections coincide. These Taylor curves have no claimed approximation radius
or certified remainder. The dot marks the chosen origin even when the minimum
is not isolated. All rims and the cutaway plane are display devices.

Python tests check oriented disk topology, unit normals, formula samples,
curvature normalization, the recorded input hash, and preservation by the old
schematic generator. JavaScript tests check selection of distinct cases and
the Taylor formula. Desktop/mobile checks exercise every case, sections,
height cuts, rotation, zoom, reset, printing, no-JavaScript and failed-load fallback.
