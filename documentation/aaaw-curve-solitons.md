# AAAW13 curve-soliton expansion

Five additional families from Dylan J. Altschuler, Steven J. Altschuler, Sigurd B. Angenent, and Lani F. Wu, *The Zoo of Solitons for Curve Shortening in Rⁿ*, Nonlinearity 26 (2013), 1189–1226, join the existing compact ancient torus curves and eternal shrinking helices. They belong to **Other special flows**: nonzero normal rotation generally prevents a mixed soliton from satisfying the pure shrinker, translator, or expander equation.

The complete 39-page [arXiv v1 preprint](https://arxiv.org/abs/1207.4051v1) was read, including the proofs and the unresolved scenarios on its last pages. Locators below are PDF/preprint pages, not journal pages. The reviewed local PDF has SHA-256 `052f77d9247a90a49fa15a12490e8de885b9a14b24e09b5a6ed86ea67813cf10`; its title page has the later typesetting date January 26, 2018. The PDF and extracted source text remain private and are not exported. This is source comparison and direct calculation, without independent human or formal verification.

| Added family | Evidence | Recorded distinction |
| --- | --- | --- |
| Ancient dense torus curves with irrational frequencies | §3, (11)–(14), pp. 8–10 | Rationally independent frequencies give an injective, recurrent, nonproper immersion of R, not an embedded compact torus curve. |
| Purely rotating curve-shortening solitons | §4.1, (27), Lemmas 5.4 and 6.3, pp. 11–20; §7.1, p. 23 | Includes planar Yin–Yang and spatial rotators; nonconstant kernel projection supplies an embedding. |
| Rotating and translating curve solitons | §4.1, Lemmas 5.2 and 6.4, pp. 11–15, 20–22 | The axial height is monotone or has a unique minimum; two graph branches alone do not prove a global embedding. |
| Rotating and expanding curve solitons | §4.2, Lemmas 6.3 and 7.6–7.7, pp. 12–13, 19–20, 28–30 | The two proper ends approach generalized logarithmic spirals; those are asymptotes, not exact profiles. |
| Rotating and shrinking curve solitons | §4.2, Lemma 6.5, Lemmas 7.7–7.8 and 8.1–8.5, pp. 12–13, 22, 28–39 | Includes spherical profiles, conditional circle limits, and the proved shooting construction of spiral ends; unresolved kernel limits are not added as existence claims. |

## Formula and hypothesis checks

- In §3, integrating (13) with (14) gives `t = |v|²τ − (1/2)Σ|Cj|² exp(−2ωj²τ) + constant`. The displayed frequency coefficient in preprint (15), and consequent frequency-dependent limiting radii, are inconsistent with (12)–(14) and Lemma 3.1. The new dense-curve entry uses the directly differentiated time relation, not those coefficients. The existing torus and helix entries already use independently checked Stryker–Sun formulas.
- With `C_s=T`, `T_s=P_T((αI+A)C+v)`, unit speed is preserved. A unit tangent and the bound `|C(s)| ≤ |C(0)|+|s|` give complete global initial-value solutions; these are not uniqueness theorems for prescribed ends.
- For `v=0`, set `r(t)=sqrt(1+2αt)` and `R(t)=exp(A log(1+2αt)/(2α))`. Then `r'=α/r`, `R'=AR/r²`, and both the normal velocity and curvature of `rRC` equal `R P_T((αI+A)C)/r`. The interval is `t>−1/(2α)` for α>0 and `t<−1/(2α)` for α<0. For α=0, `exp(tA)C+tv` is valid when `Av=0`.
- The sign is `V_s ≥ 0` in (76). The word “decreasing” in Lemma 8.3 conflicts with (76) and with §8.5's `V_- ≤ V_+`; the entry follows the differentiated identity. Also, a rotation-frequency space is `ker(A²+Ω²I)`, as follows from `A²=−Ω²I`, despite the sign in the displayed definition in §8.1. We avoid importing either typo.
- A nonzero limit of V forces a bounded circle limit set (Lemma 8.4). Convergence to one circle is stated only when the relevant frequency space is two-dimensional. Strict monotonicity gives a nonzero limit at at least one end for genuinely rotating shrinking profiles, hence a bounded infinite-length tail. Gaussian length and entropy are then infinite by a positive lower bound on the Gaussian weight. This deduction does not identify finite centered Gaussian area with entropy.
- Lemma 6.4's `±∞` means either sign is possible at each end. Its proof allows a unique minimum and two upward ends. No unjustified opposite-sign requirement is copied. We retain its range-of-A projection rather than replacing it with distance to a line in a higher-dimensional kernel.
- Lemma 7.8 is used through its invariant-region conclusion. We do not quote its overly strong displayed estimate on `|T+â|`: the region's bound on `1−μ²` gives an angular estimate of order `|a|⁻²`, not `|a|⁻⁴`. The topological shooting conclusion, not a guessed numerical tangent, supplies the spiral end.
- A bounded immersed image need not have compact domain, and an injective immersion need not be an embedding. The metadata records the two ends of the domain R and distinguishes proper escaping ends from bounded accumulation.

## Original illustrations and validation

`python3 scripts/generate_aaaw_geometry.py` generates seven original figures: a dense R4 curve, spatial and planar rotators, a screw soliton, a rotating expander, and nonspherical and spherical rotating shrinkers. NumPy and SciPy are required for regeneration. Every figure has an SVG fallback and interactive rotation and zoom; all have a physical-time slider, and the R4 curve has a fourth-coordinate rotation control.

The six profile figures solve equation (27) with DOP853, `rtol=2e-11`, `atol=2e-12`, and maximum step 0.04. Their sample spacing is 0.02. Profiles use arclength windows [−24,24], or [−18,18] for shrinking examples. A tighter solve and independent fourth-order differences provide numerical diagnostics in `site/assets/solitons/aaaw-audit.json`; no certified error, global embeddedness, or infinite-end computation is implied. The spherical sample satisfies `|C|²=2` to numerical precision. The dense curve uses its exact physical-time formula on `−12π ≤ θ ≤ 12π`, never joining its endpoints.

Python checks independently differentiate stored positions and tangents and test the spherical and monotonicity identities. JavaScript checks compare time derivatives of the exact motion against the scaled curvature and check the dense curve's vector flow equation. Full Python/JavaScript suites, the complete build and link checker, and desktop/mobile reader checks apply before publication. The collection retains five chapters, one reading page per family, permanent tags for earlier entries, and no inherited GMT routes.
