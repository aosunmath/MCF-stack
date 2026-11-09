# Ancient spiral time sequence

The drawing for `ex:catalogue-ancient-spiral-curves` follows Zhang–Olson–Khan–Angenent, [Nonconvex ancient solutions to Curve Shortening Flow, arXiv:2204.05253v3](https://arxiv.org/abs/2204.05253v3). The introduction, Figures 1–2, Section 2 (especially (2.19)–(2.23)), and Appendix A were checked against the paper. The source PDF is not exported.

This is a numerical drawing of the **asymptotic construction**, not a numerical solution of the ancient curve-shortening PDE. The picture replaces a tubular Fermat-spiral cartoon, including its artificial inner cap, with the Yin–Yang curve passing through the origin and one outer closing cap. No late-time or extinction behavior is inferred from the model.

## Geometry and conventions

All coordinates are in the Euclidean plane. The equation is normal velocity equal to signed curvature, with left normal `JT` and `J(x,y)=(-y,x)`. The noncompact rotating model has counterclockwise angular speed one. On its positive arm, arclength satisfies

```
x_s = cos((x²+y²)/2), y_s = sin((x²+y²)/2), (x,y)(0)=(0,0).
```

Indeed, `κ=<X,T>` implies `φ=|X|²/2` with initial tangent `(1,0)`. The negative arm is its image under `X -> -X`. Unwrapping the positive arm's polar angle `ψ` gives the paper's radial function `ℛ(q)` with `q=ψ+π/2`; this avoids the singular radial initial condition at `q=π/2`. It also gives the first-integral check `r²/2 - ψ - arctan(r/r_q)=0` away from the origin.

The generator uses fourth-order Runge–Kutta with arclength step 0.002, retaining samples every 0.05. The viewer interpolates only within that table. It rotates the arms by `t` and truncates them near polar angle `-t`. There is one common physical spatial scale for all four snapshots (`-24, -18, -12, -8`), and for the main animation. The cap inset has its own explicitly labeled moving coordinates.

Write `τ=-4t`, `R=ℛ(-2t)` and `X=exp(-tJ)((R,0)+Z/R)`. The cap is `Z=G+(F/τ)JG'`, where `G=(-asin(tanh p),-log cosh p)` and `F` is the odd solution of

```
F' = 2 G₂ - |G|²/2 - 1 - tanh(p) F, F(0)=0.
```

This is a numerically convenient differentiated form of (2.21), with the paper's constants `A=0, B=-1`. The generator tabulates it with the same RK4 step, retaining samples every 0.02. The uncorrected grim reaper appears dashed only in the inset.

For each cap point below `v=-0.5 log τ`, the viewer finds the relevant Yin–Yang arm at the same `v` by bracketed bisection and blends the two **u coordinates** using a smooth cutoff. The cutoff is zero at `-v/log τ <= 0.5` and one at `>=2`. This implements the convex-combination expression `k=ηU+(1-η)h` in Section 2.8. The second displayed equality in (2.23) is algebraically inconsistent with that expression; the implementation uses the first expression, also used later in the text. The arms are cut at `v=-2 log τ`. Their endpoints and the cap endpoints are identical.

The finite interval is selected for legibility, not asserted to exceed an effective threshold in the existence proof. The paper's symmetric-difference area estimate concerns the proved ancient solution, not an error bound for this finite drawing. In particular, the model does not certify pointwise closeness, uniqueness, or embeddedness of the theorem's solution.

## Reproduction and verification

```
node scripts/generate_ancient_spiral_geometry.mjs
node --test tests/ancient-spiral.test.mjs
```

No third-party numerical library is required. The JSON table, interactive view, and printable SVG all use the same computed geometry. The legacy author-schematics generator delegates this example to the new generator, so it cannot restore the old cartoon.

Checks cover refinement of the ODE integration; the rotating-soliton first integral; smooth passage through the origin; closure, absence of polygon crossings, and cap joins at sample times; the clockwise/inward cap motion; and approximate area loss. These are numerical diagnostics of the illustration, not an existence proof or certified PDE error estimate. Full Python/JavaScript suites, the link-checking build, and desktop/mobile reader checks are required before publication.
