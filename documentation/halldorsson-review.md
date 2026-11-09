# Halldórsson source review

Reviewed on 8 November 2026. Both requested papers were read from their final arXiv editions. Exact hashes, pages, and checked passages are in [the source register](halldorsson-sources.json). Neither PDFs nor extracted source text are exported. The supplied name refers to one author, Höskuldur P. Halldórsson.

| Source family | Catalogue treatment |
| --- | --- |
| Stationary line and shrinking circle | Retain the canonical plane and sphere entries. |
| Grim reaper | Retain the existing translator entry; link from the planar classification. |
| Homothetic planar expanders | Retain the corner-smoothing entry; add the classification reference, including the line endpoint. |
| Closed Abresch–Langer curves | Retain the existing entry and tag; link to the nonclosed branch. |
| Nonclosed homothetic shrinkers | New Shrinkers entry, restricted to irrational turning, with nonproperness and Gaussian divergence explicit. |
| Pure rotators, including Yin–Yang | Expand the existing purely rotating curve-soliton entry with the planar classification and a separate ℝ³ product surface case. |
| Rotating expanders | Expand the existing rotating-expanding curve-soliton entry with the planar classification; nonzero rotation prevents classification as a homothetic expander. |
| Rotating shrinking curves | Expand the existing rotating-shrinking curve-soliton entry with bounded planar and comet cases. Existence does not imply comet uniqueness. |
| Finite-pitch helicoidal rotators/translators | New Translators entry: rotation is equivalent to vertical translation of the images. |
| Helicoidal minimal surfaces | New stationary-flow entry, separating the embedded helicoid from the nonembedded nonzero-offset immersions. |
| Nonzero constant-mean-curvature helicoidal surfaces | Comparison in the minimal entry only. Section 6 does not make this general family a self-similar MCF family. The round cylinder is already recorded. |
| Zero-pitch circular and logarithmic-spiral limits | Explain in the associated entry. The surface parametrization degenerates at zero pitch; the limiting profile is not an additional regular MCF soliton. |

## Conventions and mathematical checks

For planar arclength profiles, use left normal N=iT, curvature vector kN, and the source's rates A (rotation) and B (dilation). The reconstruction from u′=uv+A, v′=−u²−B, θ′=u is X=e^(iθ)(u+iv)/(A−iB). Differentiating gives X′=e^(iθ), and taking the normal component gives k=A〈X,T〉+B〈X,N〉. The time interval is 1+2Bt>0; for B=0 rotation exists eternally. Homothetic shrinkers are converted to B=−1/2, consistent with MCF-stack's time −1 slice. The dense example's viewer reports that canonical time.

The infinite Gaussian values for the annulus-dense and circular-end immersions are direct deductions, not claims quoted from the papers: the parameter domain contributes infinite arclength inside a bounded region, on which any fixed positive Gaussian weight has a positive lower bound. The domain remains noncompact even when the image is bounded. No proper-shrinker Gaussian-area/entropy identity is invoked.

For the helicoidal surface F(s,φ)=(e^(iφ)X(s),hφ), the pitch h is per radian. Its mean-curvature equation gives H=−hτ/√(τ²+h²), and 〈−he₃,n〉=hτ/√(τ²+h²), so the translating velocity is −he₃. Height identifies φ and radial escape identifies bounded s-preimages; hence these immersions are proper. Their parameter planes have one end, although their planar generating curves have two arms. The pure-rotation products X×ℝ are kept with the planar rotators, not treated as finite-pitch translators.

The helicoidal minimal formula is exact. At a=0 it is the classical helicoid. At a≠0 the profile crossings recorded in Section 5 are genuine same-height surface crossings. Properness follows from the formula, and a proper immersion into Euclidean space has complete induced metric. Genus and ends refer to the full domain, not a periodic quotient.

The rotating-shrinker source captions explicitly ask embeddedness questions; those questions remain unresolved in the entry metadata. For finite-pitch translators, the symmetric axis-crossing profile is embedded, while nonzero-distance cases can have arm crossings. No unsupported threshold is assigned. Phase-plane stability in the planar paper is not rebranded as stability for unrestricted MCF perturbations.

## Figures and verification

[The generator](../scripts/generate_halldorsson_geometry.py) creates original SVGs and sampled geometry. Planar and helicoidal moving profiles use SciPy DOP853; the minimal family uses its exact formula. The dense-curve illustration targets the irrational number (√5−1)/2 by scalar shooting, without claiming numerical certification of irrationality. The comet preset starts at finite large radius using an asymptotic expansion, and is labeled as an approximate shooting orbit rather than a certified complete comet.

The interactive viewers retain equal spatial scales and show finite windows. Similarity time evolution is applied analytically; helicoidal translators move at their actual vertical velocity. The dashed circle on the shrinking profiles is an asymptotic set, never an added component. The new 3D viewers allow rotation, zoom, pitch and profile choices. The numerical audit contains refinement diagnostics, not rigorous error bounds. Figure design is credited to the source equations and figures on the numerical references page.

## Integration with the concurrent AAAW expansion

Before publication, the main branch acquired the higher-dimensional AAAW curve-soliton entries. The planar ODE is exactly their dimension-two specialization: take the skew matrix to be A times the planar quarter-turn and identify the AAAW dilation coefficient with B. The vector equation then reduces to k=A〈X,T〉+B〈X,N〉, with identical initial-value solutions and time laws. These reviewed overlaps therefore extend the existing purely rotating, rotating-expanding, and rotating-shrinking family pages; their permanent tags, routes, spatial cases and original figures are retained. Halldórsson supplies sharper planar properties and additional interactive viewers on those pages. The dense homothetic shrinker and two helicoidal families are three new entries. No canonical source fingerprint is fabricated: unpublished draft entries are folded into the already-published statements before export.
