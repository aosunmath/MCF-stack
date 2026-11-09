# Stolarski–Su finite-time neck pinch: time and scale views

Reviewed source: Maxwell Stolarski and Wei-Bo Su, *Finite-Time Singularities
of Lagrangian Mean Curvature Flow with Quantitatively Precise Dynamics*,
[arXiv:2607.03152v1](https://arxiv.org/abs/2607.03152v1). Theorem 1.1,
Remark 1, the proof outline in §1.1, equations (7)–(13) in §§2.2–2.3,
and the proof of Theorem 1.1 in §5.3 determine this illustration.
The only source figure concerns the compact immersed variant (Remark 9),
which is outside this entry. No paper or source figure is redistributed.

## Mathematical scope

The entry concerns the SO(n) subfamily: smooth properly embedded Lagrangian
n-manifolds in C^n, codimension n, topology S^(n−1) × R, regular for
0 ≤ t < T. The allowed rates are K = 2,3,4 for n = 3 and all integer
K ≥ 2 for n ≥ 4. The controls show n = 3,…,6 and K = 2,…,6 within this
range; the finite menu is not an upper bound in the theorem.

The profile in §2.2 is gamma = a sin(n theta)^(-1/n) exp(i theta),
0 < theta < pi/n. After the unitary rotation exp(−i pi/(2n)), write

    w(v) = a (1 + i sinh(v))^(1/n),  v in R,
    X(v,u) = w(v)u,  u in S^(n−1).

The root has argument in (−pi/(2n), pi/(2n)). This gives Re(w^n) = a^n,
and w^(n−1) w' is purely imaginary. The Lagrangian angle is constant,
so each fixed-a neck is exactly special Lagrangian and has H = 0.
The minimum ambient radius is a, attained at v = 0 on an S^(n−1) waist.
The two limiting planes are exp(±i pi/(2n)) R^n (with the appropriate
orientations). In the profile graph orientation used by the paper,
(x,y) = (Im w, Re w) up to reflection; y = f_a(x), and f_a(0) = a.

The true flow has profile f_(a-tilde(t)) + partial_x u-tilde. The theorem
controls a-tilde(t) comparable to (T−t)^(K/2), and proves smooth convergence
after the Type II rescaling. It does not give a closed formula for that
correction. Here q = (T−t)/(T−t0) = 1−tau and **only for the illustration**
a_model = a0 q^(K/2), a0 = 0.7 in display units. The number a0 is not
a quantitative existence threshold. t0 is a reference time near T, not
necessarily the initial time of the constructed flow.

This time-dependent family of minimal necks does not solve MCF. At the
waist its velocity is nonzero whereas H = 0. We omit the PDE correction,
do not simulate chosen initial data, and do not infer a global time-T
slice or a continuation after T. Time snapshots are tau = 0, 0.6, 0.9;
playback stops at 0.98. All finite-time drawings are labeled asymptotic.

Parabolic magnification by q^(−1/2) leaves a neck of scale
a0 q^((K−1)/2), tending to zero. The finer magnification by q^(−K/2)
leaves scale a0: the model becomes stationary. For the true flow these
correspond to the stationary multiplicity-one tangent pair of planes and
the smooth special Lagrangian Type II limit, respectively. Fixed
normalization constants have been absorbed into display units.

## What is drawn

The surface is a **two-dimensional section** obtained by taking
u = (cos phi, sin phi, 0,…), not the whole n-manifold or a flow in R^3.
Four real coordinates are (Re z1, Re z2, Im z1, Im z2). We rotate the
(Re z2, Im z2) plane by the projection slider, omit the new fourth
coordinate, then rotate the resulting 3D view. Apparent intersections
and a collapsed projected direction do not mean the full neck is
nonembedded. Blue and ochre distinguish the two v half-lines, and purple
marks the circle section of the spherical waist. By default a cutaway shows
only 0 ≤ phi ≤ pi, exposing the neck along the cut edges; Half slice
toggles the other half without changing the geometry. The planar section ±w
is also shown; it has four asymptotic rays, representing the intersections
of two n-planes with a complex coordinate line, not four topological ends.

Every panel has the same camera and spatial scale within the selected
rescaling. The display cutoff |w| ≤ 2.5 is fixed in the displayed coordinates;
it is not a moving boundary of the flow. The neck zoom therefore looks
at a progressively smaller physical neighborhood. Logarithmic radial
sampling resolves a small waist without scaling the camera to fit it.

## Reproduction and validation

Run `node scripts/generate_stolarski_su.mjs`. The general Lagrangian
generator delegates to this script. The static fallback, scale comparison,
and interactive module share the same exact profile and mesh routines.
Tests check the implicit profile identity, the Lagrangian and constant
phase identities, the stationary graphical PDE, the nonzero residual
for the moving model, the dimension/rate restrictions, scale separation,
mesh connectivity and finite coordinates. They do not certify the flow.
Publication also requires the complete Python and JavaScript suites,
build/link checks, and desktop/mobile interaction checks.
