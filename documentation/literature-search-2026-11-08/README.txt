MCF special solutions: bibliography and relevance-review queue
Search date: 8 November 2026 (America/New_York).
The arXiv submission-date query cutoff is 2026-11-08 23:59 UTC.
The Crossref publication-date query cutoff is 2026-11-08.

Open index.html for the searchable bibliography. bibliography.bib is an importable
BibTeX library; bibliography.json preserves identifiers, source provenance,
publication/preprint dates, topic tags, and relevance-screening status.
statistics.json gives exact counts. search-audit.json contains query strings,
retrieval URLs, pagination counts, merge decisions, and deferred/excluded records.

SCOPE
The requested scope is special solutions and the MCF theory directly supporting
them: shrinkers, translators, expanders, ancient and eternal flows, rotating and
other self-similar flows; construction, classification, rigidity, asymptotics,
compactness, stability, index, entropy, and relevant singularity/weak-flow theory.
Curve shortening, networks, Lagrangian and higher-codimension cases, and curved
ambient spaces are included when the screen detects that connection. Context
tags are only discovery aids; a tag is not a verified dimensional or geometric
hypothesis. In particular, a mention of a sphere or a higher-dimensional model
does not establish the ambient geometry of every result in a paper.

This is a bibliography, not an addition of examples or theorems to MCF-stack.
No PDFs, private research files, or private source-locator notes are redistributed.
The reading collection, its mathematical statements, permanent tags, and routes
are unchanged. No schedules, background updates, or GitHub Actions were added.

SEARCH METHOD
1. Eight arXiv API searches were retrieved to the end of their pagination, with
   requests separated by at least three seconds and a submission-date cutoff.
   These returned 3,801 distinct arXiv identifiers. Query groups cover mean
   curvature flow, shrinkers, translators, expanders, curve shortening/networks,
   special solutions and supporting terminology, soliton names, and ancient
   hypersurfaces. Exact queries and page totals are in search-audit.json.
2. Five Crossref title searches retrieved the first 1,000 ranked results each:
   "self shrinkers mean curvature flow", "translating solitons mean curvature
   flow", "self expanders mean curvature flow", "ancient solutions mean curvature
   flow", and "curve shortening homothetic solutions". Publication dates were
   restricted through 8 November 2026. These ranked searches were NOT paginated
   to exhaustion and are NOT exact phrase searches; irrelevant results are common.
3. Twenty-six targeted searches checked older foundations. Their selected records
   include Huisken, Gage-Hamilton, Grayson, Ecker-Huisken, Hamilton, White,
   Evans-Spruck, Chen-Giga-Goto, Huisken-Sinestrari, Ilmanen, Abresch-Langer,
   Altschuler-Wu, Angenent, and Chopp. Ilmanen's 1992 paper was checked directly
   against the publisher after a title search returned unrelated records.
4. The project's initial 66 and current 83 bibliography records were reconciled by bibliographic identity.
   Public publication lists of Haslhofer, Bernstein, and Ao Sun and selected
   survey/paper abstract pages were consulted as cross-checks. These author lists
   and survey reference lists were not exhaustively traversed.
5. MathSciNet's search page exposed only its JavaScript shell to the available
   web tool. Google Scholar's search page was not accessible. Neither database
   supplied a usable bibliographic export. This work does NOT claim a completed
   MathSciNet, Google Scholar, or zbMATH search.

SCREENING AND RECORD COUNTS
The main index has 894 bibliographic records: 446 direct special-solution title
matches and 448 supporting-theory records. Of these, 172 are individually
selected catalogue, foundational, or central references; 722 are automatically
screened candidates requiring further relevance review. Both kinds have source
metadata, but neither label certifies a proof audit.

Topic tags overlap: Shrinkers 206; Translators 196; Expanders 54;
Other special flows 187. Supporting papers can also carry a solution-topic tag.
745 records have an arXiv identifier and 545 have a DOI; these sets overlap.
The index includes preprints, surveys, book chapters, six books/edited books/
monographs, and corrections as well as research articles. Therefore 894 is a
record count, NOT a claim of 894 distinct peer-reviewed research papers.

Automatic screening uses titles and available arXiv abstracts, with corrections
for obvious unrelated subjects and flow variants. Matching a phrase in an
abstract does not prove that the paper's main result concerns a special solution.
The review queue may still contain tangential references and may omit relevant
papers. The audit preserves deferred/excluded titles and identifiers for rechecking.
Ricci solitons, graph expanders, language translation, modified curvature flows,
and broad MCF papers without a detected direct connection were generally deferred
or excluded. This is a scope decision, not an assessment of their quality.

DEDUPLICATION AND DATES
Versions sharing an arXiv ID or a DOI were joined. Exact normalized titles were
joined when an author surname also agreed, except for generic titles. Thirteen
additional publication/preprint correspondences were reviewed by title and author
metadata. All merges are logged. Conical and cylindrical uniqueness papers were
kept separate; corrections and separately published expositions were retained.
Different titles, absent identifiers, initials, and reprints can leave residual
duplicates; the list has not been certified as one record per intellectual work.

Publisher publication years are used when supplied, otherwise arXiv first-
submission years are used. Original and preprint years are retained separately.
Brakke's original 1978 monograph is distinguished from the 2015 reprint identified
by its DOI. arXiv journal references are author-supplied metadata; missing journal
information is not evidence that a paper remains unpublished. Current arXiv titles
can differ from older citation titles. Unavailable fields are not invented.

COMPLETENESS LIMIT
This is a substantial, reproducible search result, not a certified complete list
of the special-solution literature. Complete pagination of specified arXiv queries
only establishes retrieval completeness for those queries. It cannot capture
papers absent from arXiv, unindexed older literature, all terminology variants,
or every citation-chain connection. The bounded Crossref searches and automatic
relevance screening impose additional limits. A stronger completeness audit would
require independent mathematical-index exports, further reference/citation-chain
searches, and paper-by-paper resolution of the remaining relevance and version
ambiguities.

PUBLIC SOURCES CONSULTED
https://info.arxiv.org/help/api/user-manual.html
https://info.arxiv.org/help/api/tou.html
https://api.crossref.org/
https://www.math.utoronto.ca/roberth/
https://math.jhu.edu/~bernstein/Research.html
https://sites.google.com/view/aosun/research
https://arxiv.org/abs/1708.09113
https://arxiv.org/abs/1901.09101
https://arxiv.org/abs/2512.24524
https://arxiv.org/abs/2601.09441
https://doi.org/10.1512/iumj.1992.41.41036
Individual arXiv and publisher links are stored with each bibliography record.

VERIFICATION
All 894 BibTeX and JSON records parse; identifiers and citation keys are unique.
All eight arXiv query groups have complete pagination with matching totals.
Local artifact links and desktop/mobile search, subject filters, selected-reference
filtering, pagination, downloads, and viewport layout were checked.
The unchanged reading edition was checked in a clean checkout of 6e658ea4b:
190 Python tests and 130 JavaScript tests passed; the complete build passed its
link checks and produced only the five active chapters. Desktop/mobile chapter
checks passed for mathematics, navigation, citations, tags, and bibliography links.
Only the six files in this dated bibliography directory belong to this change.
