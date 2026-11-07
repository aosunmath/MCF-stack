# Three-ended finite-genus translator picture

The original source was read for this revision: Juan Dávila, Manuel del Pino,
and Xuan Hien Nguyen, *Finite topology self-translating surfaces for the mean
curvature flow in R3*, Advances in Mathematics 320 (2017), 674–729,
[DOI](https://doi.org/10.1016/j.aim.2017.09.014).
The [accepted manuscript](https://purehost.bath.ac.uk/ws/portalfiles/portal/228322441/self_translating_aug28_2017b.pdf)
was consulted at Theorem 1.1, Figure 2, and Section 2, especially (2.1), (2.3),
(2.6), Definition 2.6, Figures 5–6, and Sections 2.4–2.5. Its cover sheet adds
one to printed page numbers. No PDF or source image is exported.

The geometry is an orientable embedded surface in Euclidean three-space,
with unit upward translation velocity. The source constructs the completed
surface near the union of a bowl and a winglike translator. Near their
intersection circle a small, bent Scherk surface provides the joining region;
the nonlinear correction is essential. The genus grows as the gluing scale
shrinks. A selected illustrative count does not establish a theorem at that
genus.

## Numerical input

The bowl profile solves

    f' = p,  p' = (1+p²)(1-p/r),  f(0)=p(0)=0.

Integration starts at r=10^-5 with f=r²/4 and p=r/2. The catenoid meridians
use arclength coordinates, avoiding an infinite graph slope at the waist:

    r' = cos a,  z' = sin a,  a' = cos a - sin a/r.

The initial conditions are (r,z,a)=(1,0,+pi/2) and (1,0,-pi/2). One common
vertical translation places the lower-wing/bowl crossing at rho=1.4. Both
axes of the static meridian use the same scale. All three ends are cut at
z=4.4, producing three artificial display rims. The JSON retains the raw
meridians as well as a simplified surface mesh. The curves are numerical
ODE solutions, not parabolas or exact closed formulas.

## Connected schematic

The drawing is a separate implicit interpolation. Let B be the vertical
bowl defining function divided by sqrt(1+f'^2). Let C be

    ((z - (W+ + W-)/2)² - ((W+ - W-)/2)²) / A,

where A>0 normalizes its gradient at the crossing. The squared wing gap is
extended as 2R(r-R) below the neck radius, so it has no zero there. The model
is the level set

    sinh(B/h) sinh(C/h) = cutoff(r) cos(m theta),
    h = 0.78 rho/m.

The smooth radial cutoff vanishes near the axis. This is a bent Scherk-type
interpolation in oblique defining functions. It is **not** equation (2.6)
in Euclidean Scherk coordinates, the authors' matched approximate solution,
or a numerical solution of the translator PDE. It has no certified geometric
error relative to their completed surfaces. Blue/green color identifies the
nearer ingredient; gold highlights the joining belt, not an additional sheet.

The displayed m=8,12,16 meshes are checked for connectivity, manifold edge
incidence, three boundary loops, and Euler characteristic. Their *model*
genera are respectively 7,11,15. These are drawing choices, not newly added
catalogue cases. The period control changes the tunnel pattern and size;
rotation, zoom, full view, cutaway, and enlarged tunnel view expose the geometry.
The numerical input mode remains distinct from the connected schematic.

## Reproduction and verification

Run `python scripts/generate_dpn_geometry.py` with NumPy, SciPy, scikit-image,
fast-simplification and Pillow available. It regenerates the model assets and
both original drawings. No additional dependency is needed for site builds.
The older translator schematic generator delegates to this drawing routine.

`tests/test_dpn_geometry.py` checks the committed mesh topology, end rims,
normalization, the unique numerical crossing, and the ODE profiles. Viewer
unit tests cover the model selection. Browser QA covers desktop and mobile,
all modes and counts, keyboard and pointer rotation, zoom, mesh, reset,
failed loading, and the no-JavaScript fallback.
