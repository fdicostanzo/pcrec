# REFERENCES.md — the repository's reference list

Documents in this repository cite external publications by a stable key of
the form `[Author##]` (two-author keys use both authors' initials;
three-plus-author keys use the first author's initials followed by `+`).
When a document first cites a paper, that paper gets its entry HERE in the
**same change** — never a bare inline mention with no entry. Keys never
change once used; if a later document needs a second paper by the same
first author in the same year, disambiguate with a letter suffix (`[XY24a]`,
`[XY24b]`) rather than renumbering anything already cited.

Entries are alphabetical by first author's surname. Each carries: authors
(full names where known), title, venue, year, a DOI or URL (plus a
version-pinned URL when a specific preprint version was read), date this
repository first cited it (or the date the citing document itself carries,
where earlier), and a "cited by" list of the documents that use it. A field
this lane could not confirm is marked `(unverified: ...)` rather than
guessed.

---

## Papers

### [Alm14+] Almeida, M., Moreira, N., Reis, R. (2014)

Marco Almeida, Nelma Moreira, Rogério Reis — "Incremental DFA minimisation",
*RAIRO — Theoretical Informatics and Applications* 48(2):173-186 (2014).
DOI/URL: <http://www.numdam.org/item/ITA_2014__48_2_173_0/>.
Accessed 2026-09-04.
Cited by: `docs/dev/dfa_online_minimization_study.md` §2.1 (retrofitted by
lane m5paper, which owns that document).

### [AutomataLib] AutomataLib (software documentation, not a paper)

Java library for automata, graphs and transition systems, developed at TU
Dortmund University as the automaton framework for LearnLib; Apache
Licence 2.0. Not a peer-reviewed publication; listed here because
`docs/dev/dfa_online_minimization_study.md` §6.7 cites it as the framework
[NF25]'s reference implementation is built on (`net.automatalib` 0.12.1,
per that library's `pom.xml`).
URL: <https://github.com/LearnLib/automatalib>. Accessed 2026-09-04.
Cited by: `docs/dev/dfa_online_minimization_study.md` §6.7 (retrofitted by
lane m5paper).

### [BC24] Baburin, I. & Cotterell, R. (2024)

Ivan Baburin, Ryan Cotterell — "A Close Analysis of the Subset
Construction", arXiv:2407.09891 (2024); DCFS 2025.
URL: <https://arxiv.org/abs/2407.09891>. Accessed 2026-09-04.
Cited by: `docs/dev/dfa_online_minimization_study.md` §2.4 (retrofitted by
lane m5paper).

### [Ber13+] Berglund, M., Björklund, H., Drewes, F., van der Merwe, B., Watson, B. (2013)

Martin Berglund, Henrik Björklund, Frank Drewes, Brink van der Merwe, Bruce
Watson — "Cuts in Regular Expressions", *Developments in Language Theory*
(DLT 2013), LNCS vol. 7907, pp. 70-81.
DOI: <https://doi.org/10.1007/978-3-642-38771-5_8>; also
<https://people.cs.umu.se/mbe/cutre.pdf>. Accessed 2026-09-04.
Cited by: `docs/design/atomic_groups_design.md` (retrofitted, this change);
also referenced informally (no key, out of this lane's scope — see "To
retrofit" below) in `docs/dev/plan.md`, `docs/dev/dev_journal.md` and
`docs/dev/plan_completed.md`.

### [Bro14+] Broda, S., Machiavelo, A., Moreira, N., Reis, R. (2014)

Sabine Broda, António Machiavelo, Nelma Moreira, Rogério Reis — "Partial
Derivative and Position Bisimilarity Automata", *Implementation and
Application of Automata* (CIAA 2014).
DOI/URL: <https://link.springer.com/chapter/10.1007/978-3-319-08846-4_20>.
Accessed 2026-09-04.
Cited by: `docs/dev/dfa_online_minimization_study.md` §2.2 (retrofitted by
lane m5paper).

### [CC04] Champarnaud, J-M. & Coulon, F. (2004)

Jean-Marc Champarnaud, Fabien Coulon — "NFA reduction algorithms by means of
regular inequalities", *Theoretical Computer Science* (2004). Surveys the
Ilie/Navarro/Yu NFA-reduction family (right- and left-invariant preorders);
no standalone entry exists here for that family's own paper(s)
`(unverified: exact title/venue for a dedicated Ilie, Navarro & Yu paper —
cited in this repo only via this survey)`.
DOI/URL: <https://www.sciencedirect.com/science/article/pii/S0304397504004803>.
Accessed 2026-09-04.
Cited by: `docs/dev/dfa_online_minimization_study.md` §2.2 (retrofitted by
lane m5paper).

### [DV18] D'Antoni, L. & Veanes, M. (2018)

Loris D'Antoni, Margus Veanes — "Simulation Algorithms for Symbolic
Automata", *Automated Technology for Verification and Analysis* (ATVA
2018); also the technical report version.
DOI/URL: <https://link.springer.com/chapter/10.1007/978-3-030-01090-4_7>,
technical report <https://arxiv.org/pdf/1807.08487>. Accessed 2026-09-04.
Cited by: `docs/dev/dfa_online_minimization_study.md` §2.2 (retrofitted by
lane m5paper).

### [Dus23+] Dusi, N. et al. (2023)

N. Dusi et al. `(unverified: full author list — the citing study read only
the title and venue)` — "Quick Subset Construction", *Software: Practice
and Experience* (2023).
DOI/URL: <https://onlinelibrary.wiley.com/doi/full/10.1002/spe.3246>.
Accessed 2026-09-04.
Cited by: `docs/dev/dfa_online_minimization_study.md` §2.4 (retrofitted by
lane m5paper).

### [Gar13+] García, P., López, D., Vázquez de Parga, M. (2013)

Pedro García, Damián López, Manuel Vázquez de Parga — "DFA minimization:
from Brzozowski to Hopcroft", Technical report, Universidad Politécnica de
Valencia (2013). `(unverified: whether this also appeared in a
peer-reviewed proceedings beyond the UPV technical report — search results
returned only the TR, handle http://hdl.handle.net/10251/27623)`.
URL: <https://files01.core.ac.uk/download/pdf/14028276.pdf> (the URL this
repository's citing document reads from), also
<http://hdl.handle.net/10251/27623>. Accessed 2026-09-04.
Cited by: `docs/dev/dfa_online_minimization_study.md` §2.3 (retrofitted by
lane m5paper).

### [Myt09+] Mytkowicz, T., Diwan, A., Hauswirth, M., Sweeney, P. (2009)

Todd Mytkowicz, Amer Diwan, Matthias Hauswirth, Peter F. Sweeney —
"Producing Wrong Data Without Doing Anything Obviously Wrong!", *ASPLOS
2009* (14th International Conference on Architectural Support for
Programming Languages and Operating Systems).
DOI: <https://doi.org/10.1145/1508244.1508275>. Accessed 2026-09-04.
Cited by: `docs/design/k24bisect_impl/k24_bisect_note.md` (retrofitted,
this change).

### [NF25] Nicol, J. & Frohme, M. (2025)

J. Nicol, M. Frohme — "Deconstructing Subset Construction: Reducing While
Determinizing", arXiv:2505.10319 (v1 submitted May 2025; v2, dated 10 Apr
2026, CC BY 4.0, is the version the citing study read in full); to appear
in TACAS 2026, LNCS, DOI: 10.1007/978-3-032-22749-2_20.
URL: <https://arxiv.org/abs/2505.10319>, version-pinned
<https://arxiv.org/html/2505.10319v2> (supplied by Frank), also
<https://link.springer.com/chapter/10.1007/978-3-032-22749-2_20>.
Accessed 2026-09-04.
Cited by: `docs/dev/dfa_online_minimization_study.md` §2.3 (retrofitted by
lane m5paper); also referenced informally in `docs/dev/plan.md` (out of
this lane's scope — see "To retrofit" below).

### [OTF] `jn1z/OTF` — Nicol & Frohme's reference implementation (software, not a paper)

John Nicol, Markus Frohme — the reference implementation of the OTF
determinization/minimization algorithm from [NF25] ("Deconstructing Subset
Construction: Reducing While Determinizing"). Java, built on AutomataLib
0.12.1 ([AutomataLib]), MIT licence ("Copyright © 2025 John Nicol and
Markus Frohme"). Not a peer-reviewed publication; listed here because
`docs/dev/dfa_online_minimization_study.md` §6 cites it with the same
weight as the papers above.
URL: <https://github.com/jn1z/OTF> (default branch `main`, last push
2026-05-29, read at that state). Also cited: the Zenodo artifact archiving
the benchmark systems, full results and a Docker image, given alongside
the repository in the paper's Data-Availability Statement — DOI:
<https://doi.org/10.5281/zenodo.18163403> (not downloaded or run by the
citing study).
Accessed 2026-09-04.
Cited by: `docs/dev/dfa_online_minimization_study.md` §6 (retrofitted by
lane m5paper).

### [RAhyb] Rust `regex-automata::hybrid` (software documentation, not a paper)

Crate documentation for the lazy/hybrid DFA in the Rust `regex-automata`
crate. Not a peer-reviewed publication; listed here because
`docs/dev/dfa_online_minimization_study.md` §2.3 cites it with the same
weight as the papers above.
URL: <https://docs.rs/regex-automata/latest/regex_automata/hybrid/index.html>.
Accessed 2026-09-04.
Cited by: `docs/dev/dfa_online_minimization_study.md` §2.3 (retrofitted by
lane m5paper).

### [Walnut] Walnut theorem prover (software documentation, not a paper)

Automated theorem prover for automatic words/sequences (first-order logic
over sets of natural numbers with addition, various numeration systems);
Java, GPL. Not a peer-reviewed publication; listed here because
`docs/dev/dfa_online_minimization_study.md` §6.7 cites it — [NF25] states
[OTF] is included in Walnut since version 7, and §6.4's Use Case 1
benchmark family is drawn from Walnut's automatic-sequence systems.
URL: <https://github.com/Walnut-Theorem-Prover/Walnut>. `(unverified:
whether this specific repository/version is the exact one the paper's
"since version 7" claim refers to — not independently confirmed beyond
the paper's own statement)`.
Accessed 2026-09-04.
Cited by: `docs/dev/dfa_online_minimization_study.md` §6.7, informally also
via its systems in §6.4's Use Case 1 (retrofitted by lane m5paper).

### [Wan19+] Wang, X., Hong, Y., Chang, H., Park, K., Langdale, G., Hu, J., Zhu, H. (2019)

Xiang Wang, Yang Hong, Harry Chang, KyoungSoo Park, Geoff Langdale, Jiayu
Hu, Heqing Zhu — "Hyperscan: A Fast Multi-pattern Regex Matcher for Modern
CPUs", *16th USENIX Symposium on Networked Systems Design and
Implementation* (NSDI 2019).
URL: <https://www.usenix.org/system/files/nsdi19-wang-xiang.pdf>. Accessed
2026-09-04.
Cited by: `docs/dev/dfa_online_minimization_study.md` §2.2 (retrofitted by
lane m5paper); also referenced informally by name ("Hyperscan") in
`docs/dev/decisions.md`, `docs/dev/plan.md` and `docs/dev/dev_journal.md`
without a specific-paper citation — see "To retrofit" below.

### [Wat01] Watson, B. W. (2001)

Bruce W. Watson — "An incremental DFA minimization algorithm", *Finite-State
Methods and Natural Language Processing* (FSMNLP 2001), Helsinki.
`(unverified: a stable DOI/URL for this specific 2001 paper, distinct from
the 2003 journal version below — not found independently of the citing
study's own secondary description)`. Accessed 2026-09-04.
Cited by: `docs/dev/dfa_online_minimization_study.md` §2.1 (retrofitted by
lane m5paper).

### [WD03] Watson, B. W. & Daciuk, J. (2003)

Bruce W. Watson, Jan Daciuk — "An efficient incremental DFA minimization
algorithm", *Natural Language Engineering* 9(1) (2003).
DOI: <https://dl.acm.org/doi/10.1017/S1351324903003127>. Accessed
2026-09-04.
Cited by: `docs/dev/dfa_online_minimization_study.md` §2.1 (retrofitted by
lane m5paper).

---

## To retrofit

Papers already cited by name somewhere in the repository, where this lane
did **not** append the bracket key inline, and why:

- **[Ber13+] (Berglund et al., "Cuts in Regular Expressions")** — cited in
  `docs/dev/plan.md` and `docs/dev/dev_journal.md` (both explicitly
  off-limits to this lane's edits) and in `docs/dev/plan_completed.md`
  (an archive whose own CLAUDE.md states its text is "preserved verbatim").
  Retrofit those three only if/when their own conventions change.
- **[NF25] (Nicol & Frohme, 2025)** — cited informally (with an inexact
  "(2023-24)" date) in `docs/dev/plan.md`, off-limits to this lane.
- **[Wan19+] (Wang et al., Hyperscan)** — named repeatedly
  ("Hyperscan", "ripgrep/Hyperscan") in `docs/dev/decisions.md`,
  `docs/dev/plan.md` and `docs/dev/dev_journal.md` as a system/technique
  reference rather than as a formal citation with author/year; the last two
  files are off-limits, and `decisions.md`'s mentions are informal enough
  (no "(Author Year)" form) that inserting a bracket key would read as
  rewording rather than a minimal append. Left as a naming-only reference.

Not treated as citations needing entries: generic algorithm/construction
names used as ordinary technical vocabulary rather than as citations of a
specific paper — "Hopcroft minimization", "Hopcroft's algorithm", "Glushkov
automaton", "priority Thompson NFA" (Thompson construction) — appear
throughout `docs/dev/` and `docs/design/` and `src/` with no "(Author Year)"
or title attached. `docs/dev/dfa_online_minimization_study.md` §2 already
carries the specific papers that connect to these names (e.g. [Gar13+]
connects Brzozowski's construction to Hopcroft's).

## Retrofit status: `dfa_online_minimization_study.md`

`docs/dev/dfa_online_minimization_study.md` is the densest source of
citations in the repository: §2's survey (11 papers plus [NF25]) and,
for its M5 paper reading, the software §6.7 cites by URL. Lane `m5paper`
inserted the `[Key]` bracket for each of those twelve directly into the
document; this lane (`refs2`) does not touch the study document and
maintains only the entries here — including the three added in this
change ([AutomataLib], [OTF], [Walnut]) for the software §6.7 cites.
