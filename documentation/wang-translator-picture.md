# Wang’s entire convex translators: reading the picture

The source is the supplied journal edition of Xu-Jia Wang, *Convex solutions to the mean curvature flow*, Annals of Mathematics 173 (2011), 1185–1239, DOI [10.4007/annals.2011.173.3.1](https://doi.org/10.4007/annals.2011.173.3.1). Checked passages: the definitions and Theorems 1.2–1.3 on printed pages 1187–1188 (PDF pages 3–4), and Section 5 on printed pages 1225–1234 (PDF pages 41–50). The supplied PDF is not redistributed.

## What the paper supplies

- The translator equation is equation (1.2) with sigma = 1, not the level-set equation with sigma = 0.
- Section 5 solves a Dirichlet problem for the Legendre transform on ellipsoids, fixes the ratio theta of the two dual level widths in (5.8), and passes to a limit after transforming back. Section 5.3 proves the limit is entire for n ≥ 3 and theta > 1. Theta is a ratio in dual space, not an axis ratio to assign to the drawn primal level.
- These examples retain O(n−1) symmetry in x′ and reflection symmetry in x_n. In Wang’s terminology, k-rotational symmetry additionally requires independence of the other coordinates. A drawing with circle symmetry in (x1,x2), but genuine x3 dependence, is therefore consistent with the word “nonrotational.”
- The bounded-sublevel estimate (5.13) survives the locally convergent construction. In dimension n = 3, horizontal sections of the graph in R4 can be represented as compact convex level surfaces in the base R3. This surface is not the whole three-dimensional translator.
- Theorem 1.3 gives quadratic blow-down models Q_k = |x′|²/[2(k−1)], 2 ≤ k ≤ n, allowing scale-dependent rotations. The figure selects the k = 2 model; it makes no assertion that every example has k = 2 or fixed-axis convergence.

## Original illustrative model

The teal picture uses the explicit function

```text
f(x1,x2,x3) = (x1²+x2²)/2 + ((1+x3²)^(3/4)−1)/6,
F_h(x) = f(sqrt(h) x)/h,    h ≥ 1.
```

This is strictly convex, even, invariant under rotations of (x1,x2), and has compact levels. The second axial derivative of F_h is

```text
(1/4) (1 + h x3²/2) / (1 + h x3²)^(5/4) > 0.
```

It is **not a translator**: at the origin, gradient zero makes the unit-speed translator operator equal to the Hessian trace, 9/4 instead of 1. Its axial exponent 3/2 is an illustration choice, not a source theorem, asymptotic approximation, numerical solve, or fitted convergence rate. No control is called Wang’s theta.

The rescaled axial term converges locally uniformly to zero. The level F_h = 1 has radial coordinate

```text
r(s) = sqrt(2 (1 − ((1+h s²)^(3/4)−1)/(6h))),
|s| ≤ b_h = sqrt(((1+6h)^(4/3)−1)/h).
```

The tips b_h tend to infinity, while the radius approaches sqrt(2) on each bounded s-window. This illustrates compact levels tending locally to an infinite cylinder without asserting that model rate for the source solutions.

The ochre cylinder is the exact level Q_2 = 1, not an exact translator. The graph-slice view fixes x2 = 0 and displays (x3,x1,x4), with x4 = F_h. The level view uses (x3,x1,x2). Labels and the axis key distinguish these spaces. The slider is rescaling, not flow time. All views use the same fixed base window |x3| ≤ 3.8; finite caps beyond it are clipped without artificial closing disks. The camera rotates and zooms independently.

## Reproduction and verification

Run `node scripts/generate_wang_picture.mjs`. The generator and viewer share `site/assets/wang-geometry.mjs`, so the static fallback, initial descriptor, and interactive geometry use the same formulas. The older translator-schematic generator preserves this figure.

The geometry tests check the level equations, slice equations, finite unit normals, index validity, strict convexity, rescaling identity, escape of the caps, and nonzero translator-equation defect. Browser checks cover desktop/mobile controls, rotation, zoom, print, missing-asset fallback, and JavaScript-disabled reading. The standard Python and JavaScript suites and a complete link-checked build are required before publication.
