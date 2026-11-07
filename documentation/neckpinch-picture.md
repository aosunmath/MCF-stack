# Angenent–Velázquez time sequence

The source is S. Angenent and J. J. L. Velázquez, *Degenerate neckpinches in mean curvature flow*, J. reine angew. Math. **482** (1997), 15–66, DOI [10.1515/crll.1997.482.15](https://doi.org/10.1515/crll.1997.482.15). The supplied 52-page PDF was read directly, especially Introduction items 1–5 (printed pp. 16–17), Figure 1 (p. 18), the matched profiles in Section 2 (pp. 20–25), Theorem 3.3 (p. 30), and the bowl analysis in Section 8 (pp. 58–60). Printed pages equal PDF pages plus 14. The private PDF is not exported.

The existing entry covers odd m ≥ 3. The drawing selects n = 2, m = 3, K = 1 in Euclidean three-space, with s = T − t > 0. It illustrates smooth embedded spherical slices before a one-sided cusp, not the even-m two-sided pinch or peanut. The theorem constructs a flow on a sufficiently short interval before T; the chosen illustrative units do not assert that the theorem has certified a particular finite interval or an error tolerance.

## Source-supported geometry

- The leading tip position is a = −2^(1/3)s^(1/3); the leading trace mean curvature at the tip is H = (2^(1/3)/3)s^(−2/3). Thus the tip length 1/H is smaller than the parabolic length √s asymptotically.
- Parabolic coordinates (y,ρ) = (x/√s,r/√s) give the cylinder ρ = √2. The first correction is √s (y³ − 6y)/(2√2); the source uses the monic Hermite polynomial for the weight exp(−y²/4).
- Intermediate coordinates (ξ,ρ) = (x/s^(1/3),r/√s) give ρ = √(2+ξ³) for ξ ≥ −2^(1/3). This is anisotropic, not an equal-axis magnification of the surface.
- At the moving tip, the normalization (X,R) = H(x−a,r) gives X = P(R), where P''/(1+P'^2) + P'/R = 1 and P(0)=P'(0)=0. It translates with speed one. Scaling by |A| instead would give speed √2, as the manuscript already explains.

## What the implementation actually draws

No compact MCF PDE is solved. `neckpinch-geometry.mjs` constructs an original composite **schematic** with a numerical bowl cap, an intermediate segment, the leading cylindrical Hermite correction, and an arbitrary far cap. It is not a quantitatively controlled matched-asymptotic numerical approximation.

For 0 ≤ r ≤ r₀ = 0.9√(2s), the axial position interpolates between a+P(Hr)/H and −(2s−r²)^(1/3). The blending weight is the quintic smoothstep of (r/r₀−0.3)/0.7, clipped to [0,1]. In the next segment the displayed radius squared is

`[2s + x³ − 6sx χ(x/s^(1/3))] g(x)`.

The cutoff χ is one for |x| ≤ 0.1|a| and zero for |x| ≥ 0.3|a|, with a quintic transition. The artificial closing factor g is 1 for x ≤ 0 and 1−(x/0.6)^4 for x > 0, closing at x=0.6. In the parabolic region this recovers the first Hermite correction asymptotically, whereas at the intermediate scale the cutoff term is lower order. The limiting target radius is sqrt(x³[1−(x/0.6)^4]) for 0 ≤ x ≤ 0.6. This target is an illustrative choice, not a uniquely selected limiting hypersurface from the paper.

The four sequence panels use s = 10^−3, 10^−4, 10^−6, and 0, with the same spatial scale and camera. The zero panel is explicitly a singular target, not a smooth time slice or a continuation through the singularity. The slider ranges over 10^−3 to 10^−7 and never reaches T. The profile overlay includes an equally scaled local magnification. The three blow-up panels have their own stated coordinates and show limits, not extra times of the compact flow.

The bowl alone is numerically integrated (SciPy `solve_ivp`, rtol 2e−11, max step 0.02, starting with P(r)=r²/4+r⁴/128). A tenfold tighter tolerance comparison is stored in the JSON audit. The regular-tip series is used below the table spacing; table interpolation elsewhere is for display. No numerical error bound for the complete schematic is claimed.

Regenerate with `python scripts/generate_neckpinch_picture.py` in an environment with NumPy/SciPy, then `node scripts/render_neckpinch_picture.mjs`. The old `generate_expander_schematics.py` entry point delegates the neckpinch SVG to this renderer, so it cannot restore the earlier three-icon illustration. Static SVG, interactive views, and print fallback use the same geometry code.
