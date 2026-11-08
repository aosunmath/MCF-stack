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
