# HMW three-ended picture

The source is Hoffman–Martín–White, *Generating Shrinkers by Mean Curvature Flow*, [arXiv:2502.20340v3](https://arxiv.org/abs/2502.20340v3), revised January 2026. The supplied PDF was read at pp. 31–46, including the construction in Section 8 and the limiting argument in Section 9; Figure 7 was inspected visually. No source images or PDFs are redistributed.

## Source and drawing choices

- Theorem 43 (p. 31): sufficiently large g gives an embedded Euclidean shrinker of genus 2g and three ends, with horizontal trace Qg and Costa–Hoffman–Meeks symmetries. The plane limit has multiplicity three. These are two-dimensional, codimension-one surfaces in R³, with H-vector = −X-perp/2 and flow sqrt(−t) Σ for t < 0.
- Figure 7 (p. 31): qualitative genus-two illustration credited to Matthias Weber. The authors explicitly call this conjectural and not a numerical approximation. The new mesh is an original drawing, not a digitization of that image.
- Proposition 44 (pp. 32–34): the initial-surface construction connects alternating sectors to upper and lower pieces. These compact surfaces in S² × R have genus 4g; they are not the Euclidean tangent shrinkers displayed here.
- Theorem 55 and Conjecture 56 (p. 38): small g may yield genus g or 2g. No effective threshold for the three-ended conclusion is supplied.
- Theorem 59 and Theorem 61 (pp. 39–45): convergence to 3P, smoothly away from one circle after taking a subsequence. Its radius is not a free geometric parameter of the theorem.
- Proposition 62 and Lemma 64 (pp. 45–46): three annular ends and conical asymptotics for large g.

The drawing joins three punctured graphical disks by g+1 upper necks and g+1 lower necks, alternating around one illustrative circle. Its genus is 2g: with three outer boundary curves, χ = 3 − 4(g+1) = −4g − 1 = 2 − 2(2g) − 3. The mesh has actual holes with shared-index neck attachments. No tubes have simply been placed on intact sheets. The models g = 1, 3, 7 are choices for visibility, not certified admissible parameters for the existence theorem.

The central analytic drawing graph is

    z = 0.035 A r^(g+1) (1+r²)^(-g/2) sin((g+1)θ).

It is smooth at the origin, has horizontal zero set Qg, and approaches a corrugated cone. The upper and lower drawing graphs have heights

    z = ±A [0.80 + 0.16 sqrt(1+r²) − 0.24 exp(−((r−1.65)/0.5)²)].

These formulas define illustrative geometry only. The scale A, circle radius 1.65, catenoid-shaped necks, collar interpolation, and conical slopes are not derived by solving the shrinker equation. In particular, this is not a Shao–Zou matching construction or an identification of the two families. A shared triangulation topology audit and rendering helpers are infrastructure only. The diagram of Qg is exact source-supported incidence data, while the displayed triangle mesh discretizes the analytic drawing.

All surface rims at radius 3.2 and cutaway edges are artificial. Gold, green and blue identify the three exterior sheets of a connected surface. The display-separation slider applies a vertical drawing dilation; it is not a solution modulus. The separate limit view is one planar disk representing a plane of weight three, with no necks or physical separation. The default g = 3 illustration does not represent a limiting sequence.

## Reproduction and checks

Run `python scripts/generate_hmw_three_ended_geometry.py` with NumPy, SciPy and Pillow. The output is three mesh JSON files, the separate plane-limit JSON, an SVG fallback plate, and a topology audit. The general schematic generator preserves this SVG.

Python tests independently check connectivity, edge orientations, vertex links, Euler characteristic, three outer boundary loops, and disjoint attachment disks. JavaScript tests check parameter routes, the separate limit, and the alternating neck sites relative to Qg. These checks certify properties of the illustration, not existence or approximation of a self-shrinker. Run the full repository tests and build, then inspect the live controls and desktop/mobile layouts before publication.
