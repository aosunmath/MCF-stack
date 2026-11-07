# Chen–Sun immortal annulus: time illustration

Source reviewed: Chen–Sun, [arXiv:2312.17457v3](https://arxiv.org/abs/2312.17457v3), 20 August 2025. The relevant material is Section 1.1 and Figure 1 (PDF p. 3), equation (2.5), Section 3.2 (initial interpolation), Proposition 4.6 and Remark 4.7 (pp. 23–24), Theorem 4.13 (p. 27), and Proposition A.2 (p. 28). The PDF and its figure are not redistributed.

The drawing preserves rotational and reflection symmetry, a positive finite-time neck, local two-sheet flattening, and fixed asymptotic planes at the ends. These features follow from the cited construction and convergence results. The paper supplies neither a closed evolving profile nor numerical time slices. The controls therefore use ordered schematic stages, with a separate infinite-time limit. Playback does not represent a physical clock or a measured convergence rate.

## Original model

For a schematic parameter `p ∈ [0,1]`, set `a = 0.72 exp(−3.2p)`, `h = 1.1`, and `c = 1.2`. The meridian is

```
r(v) = a cosh(v),
z(v) = h tanh(c a v / h),     −∞ < v < ∞.
```

Rotate about the z-axis. The display truncates at `r = R = 5`; all stages use the same camera scale. The formula defines the illustration, not the Chen–Sun solution. In particular the exponential formula for `a` is a display interpolation, not a claim about decay in MCF time. It is not a moving minimal catenoid: the height saturates at fixed ±h.

The parametrization is smooth and regular at `v=0`: `r=a`, `r′=0`, `z′=ca>0`. It is embedded, with strictly monotone z and two ends. The full profile has limits ±h as v tends to ±∞ for every a>0. At fixed r>0, its height tends to zero as a tends to zero because `a acosh(r/a) → 0`. Hence the model illustrates local rather than uniform convergence. The full model has annular topology; the truncated mesh has Euler characteristic zero and two boundary circles. Cutaway boundaries are only a viewing device.

The lower profile uses `r/(r+R)` horizontally and unchanged height vertically. Its rightmost endpoint denotes radial infinity, not a finite point. The shaded interval corresponds to `0≤r≤R`. The limiting view draws one plane and labels its multiplicity 2; it does not separate coincident sheets or present a pinched finite-time slice.

## Reproduction and checks

Run `node scripts/generate_immortal_annulus.mjs` (also called by the existing immortal-flow generator). The JavaScript model is shared by the static SVG, initial geometry JSON, and interactive viewer. Tests check connectedness, mesh Euler characteristic, boundary edges, symmetry, positive necks, fixed truncation, monotone profiles, and the fixed asymptotic heights. These verify the illustration only; no PDE residual or numerical approximation claim is made.
