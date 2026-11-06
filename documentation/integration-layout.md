# Integration layout and numbering

MCF-stack collects special solutions of mean curvature flow in five chapters: Introduction, Shrinkers, Translators, Expanders, and Other special flows. `collection.json` places 53 sections in those chapters: one introductory section and 52 illustrated catalogue entries. The active manuscript is `content/gmt-foundations/`; its source slug and retained labels remain stable for permanent tags. See [the catalogue expansion](catalogue-expansion.md) for sources, normalization, illustration conventions, and reproducible geometry. Project identity is centralized in `scripts/project.py`.

The inherited GMT chapters, formerly numbered 6 onward, have been removed from the manuscript, published routes, search, and source listings. Their former source files and development notes remain available through Git history. Older expansion documents describe that inherited edition and are not the current reading plan. Do not restore these chapters when extending the special-solution catalogue.

## Reading structure

Organize content by mathematical subject across contributing sources. Split long or mixed sections using reviewed `section_promotions` boundaries. Absorb a source heading that repeats the containing section title while preserving its introductory text and permanent tags. Chapter pages list sections and retained subsections; section pages show connected prose and complete statements and proofs.

Within the four solution categories, the build orders families by their lowest recorded ambient dimension using `catalogue-properties.json`: ℝ², ℝ³, ℝ⁴, then higher Euclidean dimensions. Curved ambient manifolds form a separate group. The order in `collection.json` breaks ties within each group. Each family has one primary section in the reading sequence; other applicable groups link directly to its dimensional cases. Chapter pages, the contents, and sidebars share this arrangement, and the resolved groups are exported in the public `collection.json`. Case links open the corresponding property disclosures. Higher-dimension groups retain the precise parameter restrictions in their linked case names and statements.

Reader locators belong to the current collection structure: chapters use `C`, and each catalogue example uses its containing section's `C.S` number. The example is the section's primary content, not a second reading stop numbered `C.S.1`. Its statement tag redirects to the complete section page, with source, property, citation, and other retained fragment targets preserved. Search combines the section introduction and primary example into one result while retaining both sets of tag and label aliases. A repeated inline example heading is absorbed into the page heading; a different descriptive caption remains unnumbered. This is a reading-page consolidation, not a mathematical merge of distinct source entries. The public entry metadata identifies such primary examples with `section_example: true`.

Genuinely separate subordinate statements, equations, and other blocks still share the `C.S.N` counter. Source numbers remain provenance. `scripts/structure.py` places sections, `scripts/numbering.py` assigns locators, and `scripts/collection.py` applies them to headings, equations, references, navigation, and search. Do not globally replace digits in mathematical text.

Section page headings use the standard section sign, for example `§ 2.1 Round shrinking spheres`. Introductory and primary-example tag markers carry `data-section-marker`: they remain available through Show tags, but do not receive formal-proof status badges. Independent statements retain the proof-review machinery.

## Tags, sources, and review

Global tags derive from source slugs and stable labels. A canonical merge requires explicit source bindings and reviewed statement fingerprints. Changed hypotheses or missing reviewed members must fail the build. Different hypotheses remain distinct. Numbered clauses retain anchors inside their parent statement; formalization badges describe complete statements.

Preserve tags for retained entries when reorganizing. Removed inherited GMT and Pome content has no reading routes or redirects into unrelated catalogue entries.

`books.json` registers source repositories or an explicit project-relative `local_path`. Local manuscripts use an exact SHA-256 file manifest; remote manuscripts retain Git commit provenance. Optional `proof_expansions`, `reading_edits`, and `historical_exposition` paths in `collection.json` activate the retained review machinery. These fields are currently absent. Do not carry over old prose replacements, historical summaries, dependency records, or source fingerprints. If source-coordinate citation conversion is needed, a reading registry must explicitly provide `locator_source` and `locator_bibliography_key`; no source is assumed by default.

Record source licenses, exact revisions, attribution, and unresolved proof dependencies. A prose edit is not mathematical or formal verification. The public Sources pages retain provenance without confusing source numbering with current reader numbering.

## Reader checks

Show tags reveals chapter, section, statement, equation, and clause identifiers. Cite this page must open on repeated clicks and direct `#cite` links, and its BibTeX must identify MCF-stack: Special Solutions of Mean Curvature Flow and the current page. Footnotes retain paired references and return links. Long equations scroll within the reading column on narrow screens.

Before publication, run the commands in the README and inspect desktop and mobile layouts. The build must contain only the five active chapters, all registered catalogue figures, and no removed background routes or links. Check that retained tags are unchanged and that citations and search resolve within the current edition.

Proofs use native closed `details.proof` panels. Fragment links reopen a containing proof, and print events temporarily expand proofs. Citations retain their canonical bibliography identifiers and also receive page-local reference targets with unique return links. Bibliography backlinks point to the exact local reference list; source catalogues distinguish cited sources from files awaiting review.

Reader citation labels omit the internal `Cat` prefix from catalogue bibliography keys (for example, `CatAngenent1992` displays as `Angenent1992`). Inline citations, page reference lists, the bibliography, and search excerpts use these display labels. Source keys, provenance records, canonical bibliography identifiers, and legacy bibliography redirects remain unchanged.

## Chapter discussions

The local manuscript's `chapter-overviews.json` explicitly registers four HTML prose fragments in `content/gmt-foundations/overviews/`. They belong to the existing category chapter pages, not to new numbered sections or catalogue families. Their files are included in the manuscript SHA-256 snapshot. The common adapter exports their prose and cited bibliography entries; the shared renderer resolves their citations through the same page-local references and bibliography backlinks as section prose. Chapter text is searchable, and headings provide local navigation above the existing ambient-dimension groups. Existing section routes, tags, numbering, and property records remain unchanged. Other manuscripts opt into this export only when requested by their adapter.
