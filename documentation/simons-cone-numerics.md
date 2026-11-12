# Simons-cone singularities and numerical profiles

The 12 November 2026 addition records three new examples and expands the existing
bounded-mean-curvature example without changing its route or permanent labels.
All four belong to **Other special flows**, in the higher Euclidean dimension
group. None is asserted to be ancient. Guo–Šešum's theorem is analysis of a
Velázquez construction, rather than a second copy of that same example.

## Sources and hypotheses

The exact PDF hashes, editions and checked passages are in
[simons-cone-sources.json](simons-cone-sources.json). These are selected-passage
reviews, not independent proof verification. Public PDFs were read in temporary
storage and are not exported. The scanned Velázquez theorem page was also
inspected as an image because its text layer loses formulas.

| Reading page | Result and restrictions |
| --- | --- |
| Low-mode type-II singularities | Velázquez: equal blocks in R^(2n), n ≥ 4, k = 2. Guo–Šešum: n ≥ 5 for the stated slower blow-up of H. |
| Bounded-mean-curvature singularities | Stolarski: n ≥ 4, even k ≥ 4. Euclidean products remain noncompact and their singular set gains a flat factor. |
| Compact Lawson-cone singularities | Liu's 2024 preprint: N = p+q ≥ 8, p,q ≥ 2, and p,q ≥ 3 if N = 8. Bounded H for integer ℓ ≥ 4 in N = 8 or ℓ ≥ 3 in N ≥ 9. |
| Type-II smoothing | Angenent–Daskalopoulos–Šešum, published 2026: outgoing R8 construction, integer k ≥ 4, with the stated global derivative hypotheses. Attaching the bounded-H incoming solution uses even k ≥ 4. |

The early noncompact papers' compactification discussions are not substituted for
Liu's separate preprint theorem. Conversely, the published smoothing paper's
historical discussion of an open compact problem does not erase the 2024 preprint.
The post-singularity construction is distinct from a self-expander: its inner
length is t^(k/3), smaller than the parabolic length sqrt(t).

The names and chronology are source checked in `catalogue-history.json`.
Velázquez receives construction credit for his families; Guo–Šešum and Stolarski
receive analysis credit for their stated properties. The smoothing paper credits
formal matching to Angenent–Ilmanen–Velázquez; no unpublished paper is presented
as a reviewed proof.

## Reduced equation and normalization

For F(r,ω,θ) = (rω,Q(r,t)θ), with ω in S^(p−1), θ in S^(q−1), the normal
ν = (−Q_r ω, θ)/sqrt(1+Q_r²) gives

    H = −Q_rr/(1+Q_r²)^(3/2)
        −(p−1) Q_r/(r sqrt(1+Q_r²)) + (q−1)/(Q sqrt(1+Q_r²)).

Using H = div ν and mean-curvature vector −Hν yields

    Q_t = Q_rr/(1+Q_r²) + (p−1) Q_r/r − (q−1)/Q.

Smooth even profiles have Q_r(0)=0; at the axis the right side becomes
p Q_rr − (q−1)/Q. The cone slope is sqrt((q−1)/(p−1)). A stationary minimal
profile with Q(0)=1 has

    Q(r) = 1 + a r² + b r⁴ + O(r⁶),
    a = (q−1)/(2p),   b = [8a³−(q−1)a]/[4(p+2)].

DOP853 starts at r=10^−5 with this even expansion, at relative tolerance 10^−11
and absolute tolerance 5×10^−13. A second solve with relative tolerance 2×10^−13
checks sensitivity. The saved profiles extend to r=20000; their tail is sampled
logarithmically, not replaced with an unlabelled exact cone. The numerical display
uses blocks (4,4), (5,5), (6,6), and (3,5).

The pre-singularity displays apply b(t)=0.7|t|^β, β=k/(1−α), to a numerical
minimal profile. The coefficient 0.7 is a display normalization, not a recovered
parameter of the existence proof. The physical, parabolic and inner views divide
coordinates by 1, sqrt(|t|) and b. **These changing dilations do not solve MCF.**
Every individual leaf is minimal; an actual evolving solution requires correction
terms. No |H| graph is inferred from the leading minimal leaf.

## Forward nonlinear PDE experiment

The displayed computation is an actual method-of-lines integration of the reduced
nonlinear PDE for p=q=4. The intended singular trace is

    Q0(r) = r + K r^6/(1+r^6),  K=0.2.

It has k=4 in the smoothing paper's notation, bounded nonnegative first derivative,
bounded second derivative, and |Q0''| ≤ C r^4. We replace its conical part by a
minimal leaf:

    Qepsilon(r,0) = epsilon P(r/epsilon) + K r^6/(1+r^6),  P(0)=1.

This is a smooth approximation to the singular trace, not the singular trace.
The main computation uses epsilon=0.01, 480 radial intervals on the quadratic
grid r_j=5(j/480)^2, times 0 ≤ t ≤ 0.5, the smooth-axis condition and a fixed
Dirichlet value Q(5,t)=Q(5,0). Three-point nonuniform finite differences and a
sparse BDF solve use relative tolerance 2×10^−7, absolute tolerance 4×10^−9,
and maximum time step 0.01. Forty-six times are stored. The viewer replays these
computed samples; it does not integrate a new PDE while a slider moves.

| Check | Observed absolute difference |
| --- | ---: |
| 240 versus 480 intervals, epsilon=0.02, all stored times and common grid points | 2.84×10^−4 |
| Radius 5 versus radius 7, epsilon=0.01, all stored times, r ≤ 2 | 3.51×10^−5 |
| epsilon=0.01 versus 0.005, 480 intervals, final profiles on radius 5 | 7.95×10^−7 |

The radius-7 comparison uses 672 intervals; its inner resolution is slightly
different, so this comparison includes both boundary and discretization effects.
Stationary-leaf discrete residuals at 120, 240 and 480 intervals are respectively
3.94×10^−4, 9.85×10^−5 and 2.46×10^−5, consistent with second-order spatial
accuracy. The final main-run axis radius is approximately 0.94132124. These are
observed differences, **not rigorous error bounds**. They do not certify
convergence as epsilon tends to zero, the maximal existence interval, selection
of a particular continuation, or a blow-up exponent. Time zero in this replay is
the smooth regularized initial state; it is not the theorem's singular slice.

Inner magnification of the PDE replay divides by its measured axis radius Q(0,t).
It does not divide by a fitted time power. The parabolic option is disabled at
t=0. Static and print fallbacks state the approximation class as well.

## Reproduction and verification

Run from the repository root, with NumPy, SciPy and Matplotlib installed:

```sh
python3 scripts/generate_simons_cone.py
python3 -m unittest discover -s tests -p 'test_simons_cone_geometry.py'
node --test tests/simons-cone-viewer.test.mjs
```

The generator writes the shared profiles, the audit, figure data and four SVGs.
Tests check the independent finite-difference minimal-equation residual, smooth
axis, conical asymptote, exact cylinder and sphere operators, stationary-leaf
drift, saved refinement diagnostics, and scale identities. The standard complete
Python and JavaScript suites, build with link validation, and desktop/mobile
reader checks are also required before publication. The existing cone-related
Stolarski reading route and tags are preserved; each added family has one section
page with its statement tag as an alias.
