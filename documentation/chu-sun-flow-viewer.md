# Chu–Sun numerical flow viewer

The existing Chu–Sun example includes Ao Sun's supplied interactive webpage as a supplementary numerical experiment. It remains attached to the canonical example, with an embedded viewer and a full-page link at `visualizations/chu-sun-flow/index.html`. The original construction diagram, permanent tags, reading number, theorem statement, and property records are retained.

## Supplied artifact

- Archive: `Chu-Sun-shrinker-pages.zip`, supplied for publication by Ao Sun.
- Archive SHA-256: `5b841a52acd8c9da071c3676359572fa4da60aa56e8c970ff40ef678fd27c996`.
- Original `Chu-Sun-shrinker/index.html` SHA-256: `782b3bef0cf05e00237836b6e4a4dce93d821cb76a36d1caaa33101fc9f3c024`.
- Embedded `DATA` JSON SHA-256: `9f224dd004ec33f54d157b2014eb855c0888d54ec10162ff9a8355cc7f279881`; this payload is unchanged.

The supplied viewer credits the Chu–Sun numerical note and companion archive at commit `aa66772`. It contains 129 rescaled frames over eight spatial zoom stages, a stationary candidate overlay, an unperturbed torus overlay, and distance, residual, and Gaussian-density diagnostics. Its provenance and caveats remain on the page. The integration does not independently reproduce or certify the underlying numerical experiment. Neither the numerical note nor private solver archives are exported.

The caption distinguishes this numerical interpolation experiment from the existence theorem. In particular, truncated Gaussian-density measurements do not establish entropy, and the candidate does not establish the shape, compactness, ends, uniqueness, or stability of the theorem's shrinker. The numerical values do not enter `catalogue-properties.json` as proved properties.

## Integration changes

- The supplied HTML is hosted in `site/visualizations/chu-sun-flow/`. Archive deployment instructions are not part of the website.
- The two existing dependencies are pinned and served locally: three.js 0.128.0 and pako 2.1.0, with their MIT licenses. Their original URLs were `https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js` and `https://cdnjs.cloudflare.com/ajax/libs/pako/2.1.0/pako.min.js`.
- Playback controls sit immediately below the surface; narrow-screen controls wrap within the reader. An attribution and a no-JavaScript notice are added. Library-loading error text reflects local hosting.
- The embed is lazy-loaded, has an accessible title, and permits scripts without same-origin privileges. The full-page link remains available independently of the embed, and the existing static diagram remains printable.
- The build validates the registered experiment file and checks iframe URLs alongside other local links. The viewer adds no catalogue entry, search result, theorem number, or source-PDF export.

## Second angular-mode experiment

Ao Sun subsequently supplied `chu_sun_ver2_flow_viewer.html` as an additional experiment under the same Chu–Sun example. It is hosted at `visualizations/chu-sun-second-mode/index.html`, with the section anchor `experiment-chu-sun-second-mode`. The original viewer and its `experiment-chu-sun-genus-one` anchor are retained.

- Supplied HTML SHA-256: `53f2efd16028e6199dd8a11d1f8b150af72ee5ec1720c2c25fa67fba0c218bf3`.
- Embedded `DATA` JSON SHA-256: `ac77bb5d6ec46509510520a78b943a80ef0fe1b4e6232e52eab50d4096a6be40`; this payload is unchanged.

The supplied page credits the “Chu–Sun shrinker ver 2” note and companion archive. Its 98 frames show a second angular-mode perturbation with ε = 0.4, compared with a numerical genus-one candidate having two apparent conical ends. The page describes closest approach followed by departure and explicitly makes no convergence claim. Resolution-limited frames remain marked; residual and Gaussian density remain unavailable after frame 92, when the supplied diagnostics report degeneration of the parametrization. The theorem and property records are unchanged; the numerical candidate is not promoted to a proved exact shrinker or a new catalogue entry.

Only integration changes are made to the supplied HTML: the same attribution, no-JavaScript notice, mobile layout adjustments, and placement of playback directly beneath the surface as the first viewer. It reuses the locally hosted three.js 0.128.0 library and license from the first viewer. Its data, numerical estimators, explanatory text, and caveats are retained. The underlying numerical replay and the note's accuracy claims are not independently certified by this integration.

`additional_experiments` in the visualization registry attaches the new viewer without replacing the original `experiment`. Additional experiments have explicit, unique `id` values for their permanent fragment anchors; their pages and local script links are validated by the build.
