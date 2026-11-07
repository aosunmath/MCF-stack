# Scherkenoid illustration

The revised picture is an original connected construction schematic, not a numerical translator. It replaces the detached limiting planes with one sheet that opens into alternating wings. The browser can rotate and zoom it, isolate a fundamental piece, change the width, and show one to three horizontal periods. A second drawing records exact boundary data.

## Source reviewed

David Hoffman, Francisco Martín, and Brian White, *Scherk-like Translators for Mean Curvature Flow*, [arXiv:1903.04617v4](https://arxiv.org/abs/1903.04617v4), February 2020. Read the introduction and Theorem 2.3 (pp. 2–9), semi-infinite-strip asymptotics in Section 8 (pp. 23–26), and the construction and uniqueness argument in Section 9 (pp. 26–30). Visually checked Figure 5 (p. 7) and Figure 11 (p. 27). No source figure or PDF is included in the published assets.

The source translates downward. Every new drawing and formula on this page uses the reflected height, with velocity +e₃. The two-parameter construction has 0 < α < π and w ≥ π. The drawing fixes α = π/2; varying width is not uniform scaling at fixed translator speed. The corners (0,0) and (0,w) lift to vertical lines. Half-turns about them generate a horizontal period (0,2w,0), without a vertical component.

The wing statement uses smooth convergence after translating the base point and subtracting its height, as in Theorem 8.4 and the proof of Theorem 9.2(2), p. 29: subtract u(a,w/2). The theorem display on p. 26 prints u(a,y), which cannot give the stated nonconstant y-profile at x=0. The page avoids that typographical inconsistency. We do not assert a uniform global error to a fixed grim-reaper graph.

## Deliberately schematic interpolation

Let r = w/π, A = r², and b = sqrt(r²−1). On 0 < y < w, x > 0, the display uses

```
Z(x,y) = A log[x / (r sin(πy/w))] + b (sqrt(1+x²) − 1).
```

This is **our drawing formula**, not a formula from the paper. At w=π it reduces to Z=log(x/sin y). It has the correct infinite boundary signs. The even function sqrt(1+x²) gives a smooth odd inverse graph across each vertical reflection line; simply inserting b|x| would create a second-derivative discontinuity there. The factor r normalizes the tangent at the origin to the bisector of the right angle. On reflected pieces use the absolute values inside the logarithm.

The mesh is parametrized as (X(y,z),y,z). Solve the strictly increasing equation

```
log q + (b/A)(sqrt(1+q²) − 1) = z/A + log(r |sin(πy/w)|)
X(y,z) = sign(sin(πy/w)) q.
```

At y=nw, X=0 exactly. Forty-five bisection steps evaluate this chosen formula; this is not a PDE solver. The global graph X is smooth at those lines because q is an odd smooth function of its signed small argument. The drawing is one connected sheet with period 2w and half-turn symmetry about each line. As z tends to negative infinity, X tends to zero. In bounded spatial windows at large positive height, the branches approach y=nw.

For a→∞, subtracting Z(a,w/2) from Z(a+x,y) gives

```
−A log sin(πy/w) + bx + o(1),
```

locally smoothly on R×(0,w). This matches the source's *local recentered* wing limit in the upward convention. It does not make Z a translator. For example, at w=π the inverse graph is X=eᶻ sin y; its upward translator residual

```
(1+X_z²) X_yy − 2 X_y X_z X_yz + (1+X_y²) X_zz
  + (1+X_y²+X_z²) X_z
```

equals X, rather than zero. Thus neither a computed scherkenoid nor a quantitative approximation is claimed. The finite mesh is cut at |x|=5.5 and −3.5≤z≤4.5; it is also cut after the selected number of periods. Those boundaries are display cuts, not boundaries or counts of ends of the actual complete surface.

## Reproduction and checks

Run `node scripts/generate_scherkenoid_geometry.mjs` to regenerate the initial JSON and both SVGs without external dependencies. The browser uses the same geometry module for parameter changes. Tests check the source-driven constraints (periodicity, half-turns, boundary signs, and recentered grim limits), the nonzero translator residual, and connected manifold mesh topology. This audits the drawing's claims; it does not verify the existence theorem.

The original entry's tags and section route are unchanged. Other examples retain their figures. The old general translator schematic generator no longer overwrites this asset. The source review remains a cited mathematical construction with no formal verification badge.
