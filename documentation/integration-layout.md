# Integration layout and numbering

MCF-stack collects special solutions of mean curvature flow in five chapters: Introduction, Shrinkers, Translators, Expanders, and Other special flows. `collection.json` places 160 sections in those chapters: one introductory section and 159 illustrated catalogue entries. The active manuscript is `content/gmt-foundations/`; its source slug and retained labels remain stable for permanent tags. See [the catalogue expansion](catalogue-expansion.md) for sources, normalization, illustration conventions, and reproducible geometry. Project identity is centralized in `scripts/project.py`.

The inherited GMT chapters, formerly numbered 6 onward, have been removed from the manuscript, published routes, search, and source listings. Their former source files and development notes remain available through Git history. Older expansion documents describe that inherited edition and are not the current reading plan. Do not restore these chapters when extending the special-solution catalogue.

## Reading structure

Organize content by mathematical subject across contributing sources. Split long or mixed sections using reviewed `section_promotions` boundaries. Absorb a source heading that repeats the containing section title while preserving its introductory text and permanent tags. Chapter pages list sections and retained subsections; section pages show connected prose and complete statements and proofs.

Within the four solution categories, the build orders families by their lowest recorded ambient dimension using `catalogue-properties.json`: ℝ², ℝ³, ℝ⁴, then higher Euclidean dimensions. Curved ambient manifolds form a separate group. Within each group, families and cross-links are chronological by the earliest recorded reference discussing the example. `catalogue-history.json` records first arXiv submission dates, dated non-arXiv preprints or publication years when no earlier preprint is identified, all paper authors, and explicitly excluded background citations. The order in `collection.json` breaks date ties; year-only dates retain their precision and sort before exact dates in that year. These are dates of recorded references, not claims of original discovery. Retain dates in metadata for ordering and in expandable source details, without a standalone earliest-reference date below each example title. Multi-paper entries use descriptive names followed by reviewed construction-author groups in chronological order, with all coauthors included and initials or given names where needed to distinguish namesakes. Before adding a name, read the actual construction/existence and attribution passages for this example. Record the paper’s role, passage locator, and contribution in `credit_reviews` in `catalogue-history.json`. Surveys, citations, uniqueness, stability, entropy calculations, and constructions of input geometry do not by themselves supply title credit. Alternative constructions and numerical candidates need explicit qualifications; retain earlier-source acknowledgements. Unreviewed credits are withheld, while all references remain available. A classification paper can qualify when it actually proves existence. Chronological order uses the earliest relevant reference independently of whether that paper receives construction credit. See [the review record](construction-credit-review.md). Renaming the reading edition leaves source captions, canonical routes, labels, and tags intact. Each family has one primary section in the reading sequence; other applicable groups link directly to its dimensional cases. Chapter pages, the contents, and sidebars share this arrangement, and the resolved groups are exported in the public `collection.json`. Case links open the corresponding property disclosures. Higher-dimension groups retain the precise parameter restrictions in their linked case names and statements.

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

The shared reference page is alphabetical by author surname, followed by the remaining author names, publication year, and title. The adapter exports a `sort_key` derived from structured BibTeX names; the renderer applies it to every build, including newly added references. Sorting ignores capitalization and folds accents, including TeX-encoded accents, while preserving the displayed names. Entries without authors use editors, then organization or title. Preserve citation keys, reference anchors, and citation backlinks when changing the order. Page-local reference lists retain citation order.

## Chapter discussions

The local manuscript's `chapter-overviews.json` explicitly registers four HTML prose fragments in `content/gmt-foundations/overviews/`. They belong to the existing category chapter pages, not to new numbered sections or catalogue families. Their files are included in the manuscript SHA-256 snapshot. The common adapter exports their prose and cited bibliography entries; the shared renderer resolves their citations through the same page-local references and bibliography backlinks as section prose. Chapter text is searchable, and headings provide local navigation above the existing ambient-dimension groups. The background prose and its local navigation sit in a native “Background” disclosure, closed by default so the examples are immediately accessible. Fragment links reopen it, and printing temporarily expands it while preserving the reader’s choice afterward. Existing section routes, tags, numbering, and property records remain unchanged. Other manuscripts opt into this export only when requested by their adapter.

## Numerical references and visual credits

`/numerical-references/` is an unnumbered reference page, outside the introduction
and four mathematical categories. Its prose is in `content/numerical-references.html`;
`content/numerical-references.bib` records methods, software, and each reference's
role in an `annote` field. The build formats those entries with pybtex and the same
structured author-surname sorting used by the mathematical bibliography. No example
number, permanent mathematical tag, or source label is changed.

The page is linked from the home page, bibliography, sidebar, footer, and figure
captions. Optional `credit_anchor` values in `catalogue-visualizations.json` link
figures to a specific visual-source credit; other figures link to the methods
section. Search has one record and a stable route-tag redirect for the page.

When adding a visual reference, distinguish the paper's authors from an individually
credited illustrator, and a source's software from software used by this project.
Retain the exact figure locator and the schematic/numerical qualification. A related
gallery link alone is not evidence that its website, image, code, or mesh was used.
