# Construction credits in example titles

Reviewed on 2026-11-09. This revision audits the 53 multi-paper entries whose
parenthetical titles previously included every cited paper's authors. The decisions
are recorded per example and per reference in `catalogue-history.json`, under
`credit_reviews`. The remaining single-paper names are unchanged. This is a reading
of relevant construction, existence, and attribution passages, not verification of
every proof or an exhaustive history of discovery. No source PDFs or extracted
paper text are redistributed.

A title credit needs a construction of the actual family recorded on that page.
The review records a passage locator and explains the contribution. All coauthors
of a qualifying paper are included, ordered by the reference's earliest date.
Reading an abstract or seeing a citation is insufficient. Classification papers
can qualify if they also establish existence. A paper constructing an input
shrinker does not thereby construct the translator built from it in a later paper.

Alternative constructions and independent rediscoveries are distinguished from
first discovery. Numerical constructions remain numerical candidates. Merely
recovering or reproducing a known special case in a survey or a broader theorem
does not automatically assign its authorship to the later paper. Read the authors'
own attribution and determine their contribution to this particular family.

Examples of the decisions:

| Entry | Title credit | Other cited work |
| --- | --- | --- |
| Rotational shrinking torus | Angenent | Drugan–Lee–Nguyen survey; Colding–Minicozzi stability; Berchenko-Kogan numerical entropy |
| Möbius shrinker | Yng-Ing Lee–Mu-Tao Wang | Braxton–Tang-Kai Lee–Zhu prove F-stability and explicitly credit Lee–Wang |
| Noncompact shrinkers of arbitrary genus | Buzano–Nguyen–Schulz | Chu–Sun explicitly cite that construction in Remark 1.5 |
| Pitchfork, Scherk, and helicoid translators | Hoffman–Martín–White | Later survey, entropy, and uniqueness/classification papers remain references |
| Tridents | Xuan Hien Nguyen; Hoffman–Martín–White | Both papers construct examples; the later paper extends the parameter range and identifies the small-neck overlap |
| Translating catenoids | Clutterbuck–Schnürer–Schulze | Lemma 2.3 proves existence; the translator notes survey it |
| Bowl | No new author parenthesis | CSS Lemma 2.2 attributes existence to Altschuler–Wu; Sun–Wang explicitly recover this known case; neither is assigned original bowl authorship |
| Ancient torus curves and eternal helices | Altschuler–Altschuler–Angenent–Wu; Stryker–Sun | Stryker–Sun give constructions in Section 2 and acknowledge the earlier discovery in Remark 1.3; the disclosure preserves this acknowledgement |
| Four-handled shrinking cone candidate | Chopp | The candidate is numerical; Angenent–Ilmanen–Chopp use and describe Chopp's computation in their nonuniqueness discussion |
| One-region networks with two to five rays | Chen–Guo | Chang studies stability; Chen–Guo derive closing equations and use numerical period evaluations in some cases |
| Brakke spoon | No new author parenthesis | Chang attributes it to Brakke; Chen–Guo's Figure 9 is not a construction of the one-ray spoon |
| Convex ancient free-boundary flows | Bourni–Langford, for both papers | The disc and higher-dimensional papers both contain existence arguments, as well as classification |

Two references have no readable construction passage verified in this audit:
Mantegazza's textbook scan and Nakayama–Iizuka–Wadati's restricted-access article.
Neither supplies a new title credit. The catenoid and ancient sine wave keep
descriptive titles, their existing citations, and their dates. Angenent–You's
attribution of the sine wave to Nakayama–Iizuka–Wadati remains recorded, but a
secondary attribution does not substitute for reading the original before adding
its authors to the title.

Reference chronology is independent of title credit. Removing a survey author
does not remove that reference or its date from the ordering. While reading
Abresch–Langer directly, the [MPIM archive](https://archive.mpim-bonn.mpg.de/id/eprint/1411/)
identified the dated preprint MPI/SFB 84-64, earlier than the 1986 journal article.
Its chronology now records 1984 at year precision. This is the preprint's date,
not the archive deposit date. All other dates remain unchanged. Dates stay in
metadata and the closed source disclosure, with no standalone earliest-date
announcement on example pages.

The build rejects missing decisions for multi-paper entries, missing passage or
contribution fields, and construction credits assigned to background-only sources.
Only `construction`, `alternative-construction`, and `numerical-construction`
roles generate the parenthetical names. An `unreviewed` decision never does.
The source disclosure lists all papers and explains each recorded role. Canonical
routes, permanent tags, source labels, and mathematical examples are retained.
