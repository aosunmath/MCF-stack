# Reapernoid time illustration

The example keeps its canonical section, permanent tags, two geometric cases,
and distinction from the ancient Costa perturbations. The former arbitrary
annulus is replaced by numerical solutions of the rotational MCF equation.

## Paper and conventions

Read: Mramor–Payne, *Ancient and Eternal Solutions to Mean Curvature Flow from
Minimal Surfaces*, [arXiv:1904.08439v2](https://arxiv.org/abs/1904.08439v2),
Theorem 1.3 (pp. 4–5), §2.2 and equation (2.7) (pp. 9–10), the outward-offset
construction in §3 (pp. 11–14), and §4 (pp. 14–20), especially equation (4.5).
The source is used as mathematical evidence, not redistributed.

The theorem constructs an embedded eternal flow on the outside of a catenoid.
Its rotational graph moves outward and its neck radius tends to infinity.
The recentered meridian tends to a line for n=2 and to a grim reaper for n≥3.
A convex meridian does not imply a convex hypersurface: its meridional and
rotational principal curvatures have opposite signs.

Our convention is H=div ν and mean curvature vector −Hν. When ν points away
from the axis, the outward-moving slices have H<0. The paper writes the
vector as Hν and uses the opposite scalar sign. The graph PDE is unchanged:

    u_t = u_xx/(1+u_x²) − (n−1)/u.

The limiting catenoid has neck radius 1; this fixes the spatial and time units.
For n=2, w(x)=cosh(x). For n=3, solve the stationary ODE
w''=(n−1)(1+w'²)/w, w(0)=1, w'(0)=0.
To avoid ambiguity in the paper's width notation W_n in (2.6), use the actual
coordinate half-width a3 = integral_1^infinity (r^4−1)^(-1/2) dr ≈ 1.311028777,
derived directly from this stationary equation. The limiting recentered grim
reaper is G(x)=−log(cos(cx))/c, c=π/(2a3), |x|<a3.

## Finite-start numerical construction

Start from a normal offset δ=10^−4 on the outward side. For a stationary
profile (s,w(s)), the initial graph is obtained by inverting

    x = s − δ w'(s)/sqrt(1+w'(s)²),
    r = w(s) + δ/sqrt(1+w'(s)²).

In three-space this gives the explicit cosh/sech formula in the reader.
Solve on the positive half-domain, using even reflection at x=0 and fixed
initial radius at the artificial outer boundary. The base mesh has 600
intervals on [0,7] for n=2 and 700 intervals on [0,a3−0.005] for n=3.
These are computational boundaries, distinct from the smaller display windows.

For stability near the stationary surface, evolve v=u−w, differentiating w
analytically (n=2) or with the stationary ODE (n=3). The algebraically equivalent
right-hand side is

    [w'' v + (w+v) v'' − (n−1)(2w'v' + v'²)]
    / [(1+(w'+v')²)(w+v)].

This preserves v=0 exactly and avoids exciting instability through the
finite-difference error of the reference catenoid. Centered second-order
space differences and SciPy's BDF solver are used, with relative tolerance
2e−8, absolute tolerance 2e−10 and maximum time step 0.2. The n=3 stationary
ODE has tighter tolerances. Time is shifted to the first slice with u(0)=2;
this is a regular time, not a singular or distinguished geometric event.
The computational start times in this convention are approximately −16.995
for n=2 and −7.093 for n=3.

These computations approximate the finite-start flows used in the source's
limiting construction. They are not exact eternal slices, a certified ancient
limit, or a uniqueness claim. The displayed finite intervals do not represent
the maximal existence interval. The reader interpolates saved numerical frames.

## Evidence and numerical limits

`site/assets/solitons/reapernoid-audit.json` records:

- Positive outward speed and meridian curvature in the audited display windows;
  the profile remains above the reference catenoid.
- Neck speed, radius and meridian curvature. At the neck,
  speed = meridian curvature − (n−1)/radius, an independent scalar sign check.
- Time-differencing residuals below 4e−6 at the sampled interior times.
- Separate changes of space mesh (twice as many intervals), initial offset
  (10^−5), end truncation (longer domains), and time tolerance (ten times tighter).

After matching the u(0,0)=2 time origins, maximum profile differences on
|x|≤2 for n=2 and |x|≤1 for n=3, over the listed checkpoints, are:

| Comparison | n=2 | n=3 |
| --- | ---: | ---: |
| Double space resolution | 0.000173 | 0.005873 |
| Smaller initial offset | 0.001039 | 0.003774 |
| Longer computational domain | 0.000082 | 0.002612 |
| Tighter time tolerance | 0.000000029 | 0.000000013 |

These are numerical sensitivity comparisons, not rigorous error bounds.
The exported profile extends a little beyond the audited comparison windows:
|x|≤2.2 and |x|≤1.17 respectively. Artificial outer boundaries lie farther away.
The finite-time n=2 meridian is still curved at t=100. Its line guide denotes
the theorem's infinite-time limit, not an attained finite-time shape. The n=3
meridian is near its grim-reaper guide at t=40, without being identified with it.

## Display contract

The default four surface views are genuine revolutions of the computed n=2
profiles over |x|≤2, on a common spatial scale and with one camera. They have
two open rims and annular topology. A time slider, playback, rotation, zoom,
mesh and stationary-catenoid reference are available. The default times are
−8, −4, 0, 10, with neck radii about 1.034, 1.251, 2 and 5.327.

The meridian views extend to t=100 (n=2) and t=40 (n=3). Recentered coordinates
subtract u(0,t) without dilation; the alternative coordinates show the original
radius. n=3 is always labeled as a meridian of a hypersurface in R4 and is never
presented as a surface of revolution in R3. The theorem covers all n≥2; only
n=2 and n=3 are computed. A supplementary static plate compares the profiles
with their distinct line/grim-reaper limits, including when JavaScript is off.

## Reproduction

With NumPy and SciPy installed:

```sh
python scripts/generate_reapernoid.py
node scripts/generate_reapernoid_plates.mjs
```

The normal site build has no new dependencies. The static plates and interactive
views use the same data and frame functions. The legacy batch generator cannot
overwrite these assets with its former arbitrary polynomial annulus.
