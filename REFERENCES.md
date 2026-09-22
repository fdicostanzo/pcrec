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

### [BP24] Barrière, A. & Pit-Claudel, C. (2024)

Aurèle Barrière, Clément Pit-Claudel — "Linear Matching of JavaScript
Regular Expressions", arXiv:2311.17620 (submitted 2023, revised 2024).
Identifies a larger subset of JavaScript regex matchable in linear time,
corrects prior algorithms, and adds lookaround handling; the authors report
a prototype implementation and that some of the work was merged into the V8
engine used by Chrome and Node.js. A prioritized NFA simulation with
JavaScript's backtracking semantics — NOT a DFA — listed because JavaScript
preference order is much closer to PCRE's than POSIX is.
URL: <https://arxiv.org/abs/2311.17620>.
`(unverified: the peer-reviewed venue, if any, beyond the arXiv preprint.)`
Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.10.

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

### [BT21] Borsotti, A. & Trofimovich, U. (2021)

Angelo Borsotti, Ulya Trofimovich — "Efficient POSIX submatch extraction on
nondeterministic finite automata", *Software: Practice and Experience*
(2021). The NFA-side companion to the TDFA work below; adapts Okui and
Suzuki's POSIX disambiguation [OS10] with correctness argument.
DOI: <https://doi.org/10.1002/spe.2881>. Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.4, §2.10.

### [BT22] Borsotti, A. & Trofimovich, U. (2022)

Angelo Borsotti, Ulya Trofimovich — "A closer look at TDFA",
arXiv:2206.01398 (submitted 3 June 2022; revised later). Full pseudocode for
the TDFA construction and matching algorithm, the practical optimizations,
and both ahead-of-time and just-in-time determinization variants; benchmarks
from RE2C and an experimental Java library.
URL: <https://arxiv.org/abs/2206.01398>; HTML mirror read at
<https://ar5iv.labs.arxiv.org/html/2206.01398>.
`(unverified: the body quotations in the citing document — the constant
register-overhead sentence and the bounded-repetition sentence — were read
from the ar5iv HTML rendering, not from the typeset PDF, because this box
has no PDF text extractor. The abstract was confirmed against the arXiv
abstract page. The paper's abstract makes NO complexity claim; the citing
document says so rather than supplying one.)`
Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.4, §2.10, §2.12.

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

### [Cox07] Cox, R. (2007)

Russ Cox — "Regular Expression Matching Can Be Simple And Fast (but is slow
in Java, Perl, PHP, Python, Ruby, ...)", self-published article, January
2007. The first of the author's RE2 article series, and this repository's
citation of record for the automaton-based approach RE2 embodies, including
its treatment of UTF-8 as a **byte-level** automaton rather than a decoded
code-point one — the design pcrec's `APPROACH.md` §4 already names as the
model for its own utf8 backend.
DOI/URL: <https://swtch.com/~rsc/regexp/regexp1.html>.
`(unverified: the specific code-point-range → byte-range-sequence
decomposition cited by docs/design/utf8_design.md §2.3 is described in RE2's
own source — `re2/unicode.py` and the `UTF8Fragment`/`Rune` range walk — and
in the author's series generally, rather than being given as a named
algorithm with a proof in this article. The citation is to the approach, not
to a numbered theorem.)`
Accessed 2026-09-04.
Cited by: `docs/design/utf8_design.md` §2.3.

### [Cox10] Cox, R. (2010)

Russ Cox — "Regular Expression Matching in the Wild", self-published
article, March 2010. The third of the author's RE2 article series, and the
citation of record here for RE2's engine SELECTION — the DFA that finds
match bounds (forward for the end, a reversed program run backward for the
start) and the OnePass / BitState / NFA engines that assign captures on the
span it found.
DOI/URL: <https://swtch.com/~rsc/regexp/regexp3.html>. Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.1, §2.12.

### [Ragel] Ragel State Machine Compiler (software, not a paper)

Adrian Thurston's Ragel — a state-machine compiler that generates
byte-oriented recognisers from regular languages, and which performs the same
code-point-range → byte-range-sequence expansion for its UTF-8 alphabet mode.
Listed here on the `[AutomataLib]`/`[OTF]` precedent: not a peer-reviewed
publication, cited because it is a second independent implementation of the
construction `docs/design/utf8_design.md` §2.3 adopts, which is what makes
that construction "classic" rather than one project's trick.
DOI/URL: <https://www.colm.net/open-source/ragel/>.
`(unverified: exact version whose UTF-8 expansion was inspected — this
repository cites the construction as documented by the project generally, and
has not read a pinned release's source.)`
Accessed 2026-09-04.
Cited by: `docs/design/utf8_design.md` §2.3.

### [UCD] The Unicode Character Database (data files, not a paper)

The Unicode Consortium's machine-readable property data — `UnicodeData.txt`,
`Scripts.txt`, `ScriptExtensions.txt`, `PropList.txt`,
`DerivedCoreProperties.txt`, `CaseFolding.txt` — published per Unicode
version. Cited because `docs/design/utf8_design.md` §3.3 and §4.4 propose
vendoring these files at a pinned version as the SOURCE for pcrec's `\p{...}`
membership and case-fold closure tables, deliberately in preference to
deriving them from python's `unicodedata` (version drift, measured) or from
libpcre2 itself (which would make the differential check its own generator's
output).
DOI/URL: <https://www.unicode.org/ucd/>.
**Version relevant to this repository: 16.0.0**, which is the version
libpcre2 10.46 reports (measured — `docs/design/utf8_measurements/out/
uprops.txt` §0, derived by sweeping `pcre2_config_8`).
Accessed 2026-09-04.
Cited by: `docs/design/utf8_design.md` §3.3, §4.4, §14 ASK 2.

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

### [DotNetDeepDive] "The .NET NonBacktracking Regex Engine: A Deep Dive" (gist, not a paper)

Public gist by Dan Moseley (a .NET maintainer and a co-author of [Mos23+]),
describing the NonBacktracking engine's three match phases — a forward pass
recording the last nullable position, a reverse pass over the reversed
pattern to find the start, and a third pass over the matched span that
generates the match and its captures. **SECONDARY**: the citing document
uses it only for the per-phase detail and flags it as such in its own §2.12;
the first-hand corroboration that a third phase exists and was replaced by
an NFA simulation is [DotNetPR65129].
URL: <https://gist.github.com/danmoseley/f37136646c303602fad2bcd6d47ef7a3>.
Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.6, §2.12.

### [DotNetPR65129] dotnet/runtime PR #65129, "Captures support for NonBacktracking" (source change, not a paper)

The pull request that added capture-group support to
`RegexOptions.NonBacktracking`, by Olli Saarikivi (a co-author of
[Mos23+]). First-hand for: which phase was replaced; the "NFA simulation
with additional effects to record capture group starts and ends on
transitions" mechanism; the Antimirov-derivative variant and the prioritized
state set that reproduce backtracking match-generation semantics; the
performance cost; and the "multiple captures of a single group are not
supported, only the last one is" limitation.
URL: <https://github.com/dotnet/runtime/pull/65129>. Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.6, §2.12.

### [Gal23] Gallant, A. (2023)

Andrew Gallant ("BurntSushi") — "Regex engine internals as a library",
self-published article. The `regex`/`regex-automata` author's own design
write-up: the lazy DFA, the reverse-DFA start, and the meta engine's rule
that *"it is usually faster to run the lazy DFA first to find the bounds of
a match, and then only run the `PikeVM` or `BoundedBacktracker` to find the
capture group offsets."*
URL: <https://burntsushi.net/regex-internals/>. Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.2.

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

### [GHR14] Grathwohl, N. B. B., Henglein, F., Rasmussen, U. T. (2014)

Niels Bjørn Bugge Grathwohl, Fritz Henglein, Ulrik Terp Rasmussen —
"Optimally Streaming Greedy Regular Expression Parsing", *Theoretical
Aspects of Computing* (ICTAC 2014), Bucharest.
DOI: <https://doi.org/10.1007/978-3-319-10882-7_14>. Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.10.

### [Gra16+] Grathwohl, N. B. B., Henglein, F., Rasmussen, U. T., Søholm, K. A., Tørholm, S. P. (2016)

"Kleenex: compiling nondeterministic transducers to deterministic streaming
transducers", *POPL 2016*. The implementation of [GHR14]'s greedy
disambiguation: a transducer decomposed into an ORACLE machine that performs
streaming greedy disambiguation and an ACTION machine that performs the
output actions, with worst-case linear time and sustained high throughput.
DOI: <https://doi.org/10.1145/2837614.2837647>; preprint
<https://hjemmesider.diku.dk/~bugge/pubs/files/ghrst2016-0-paper.pdf>.
Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.10, §2.11.

### [GoOnepass] Go standard library, `src/regexp/onepass.go` (source, not a paper)

The Go `regexp` package's one-pass machine. First-hand for the definition
(*"Some regexps can be analyzed to determine that they never need
backtracking"*), the condition (*"at any `InstAlt`, there must be no
ambiguity about what branch to take"*), the `NumCap` capture count, and the
1,000-instruction abandonment threshold.
URL: <https://go.dev/src/regexp/onepass.go>. Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.7, §2.11, §3.3.

### [HSdoc] Hyperscan developer reference, "Compiling Patterns" (software documentation, not a paper)

First-hand for Hyperscan's stated non-support of capturing
sub-expressions (*"capturing is ignored"*), its default of reporting only
the end offset, the `HS_FLAG_SOM_LEFTMOST` start-of-match flag and its three
stated costs (reduced pattern support, increased stream state, performance
overhead), and the all-matches semantics that make a capture meaningless
(the `/foo.*bar/` example returning two matches where libpcre returns one).
Vectorscan is a fork and inherits the model.
URL: <https://intel.github.io/hyperscan/dev-reference/compilation.html>.
Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.8, §2.11.

### [Lau00] Laurikari, V. (2000)

Ville Laurikari — "NFAs with Tagged Transitions, their Conversion to
Deterministic Automata and Application to Regular Expressions",
*Proceedings of the Symposium on String Processing and Information
Retrieval* (SPIRE 2000), September 2000. The origin of tagged automata:
tagged NFAs, their determinization into TDFAs whose transitions carry
register operations, and the termination proof.
DOI: <https://doi.org/10.1109/SPIRE.2000.878194>; author's copy
<http://laurikari.net/ville/spire2000-tnfa.pdf>. Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.3, §2.11.

### [Lau01] Laurikari, V. (2001)

Ville Laurikari — "Efficient submatch addressing for regular expressions",
Master's thesis, Helsinki University of Technology, 2001. The thesis
treatment of [Lau00]'s construction; the algorithm TRE implements.
URL: <http://laurikari.net/ville/regex-submatch.pdf>.
`(unverified: the URL above was not fetched by the citing lane; the thesis
is identified from secondary references ([TDFAwiki], [RegexTDFA],
[TREreadme]) and from [Tro19]'s own citation of it.)`
Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.3.

### [Mos23+] Moseley, D., Nishio, M., Perez Rodriguez, J., Saarikivi, O., Toub, S., Veanes, M., Wan, T., Xu, E. (2023)

Dan Moseley, Mario Nishio, Jose Perez Rodriguez, Olli Saarikivi, Stephen
Toub, Margus Veanes, Tiki Wan, Eric Xu — "Derivative Based Nonbacktracking
Real-World Regex Matching with Backtracking Semantics", *Proceedings of the
ACM on Programming Languages* 7(PLDI), June 2023. The algorithm behind
.NET 7's `RegexOptions.NonBacktracking`: derivative-based, symbolic,
supports anchors and counting, **preserves backtracking (leftmost-first)
semantics**, extensible with lookarounds, with a formal correctness proof
the authors believe to be the first of its kind for an industrial regex
matcher.
DOI: <https://doi.org/10.1145/3591262>; publisher record
<https://www.microsoft.com/en-us/research/publication/derivative-based-nonbacktracking-real-world-regex-matching-with-backtracking-semantics/>.
Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.6, §2.11, §2.12.

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

### [OS10] Okui, S. & Suzuki, T. (2010)

Satoshi Okui, Taro Suzuki — "Disambiguation in Regular Expression Matching
via Position Automata with Augmented Transitions", *Implementation and
Application of Automata* (CIAA 2010), LNCS vol. 6482. A deterministic
position automaton that recognizes and translates input into a compact DAG
of syntax trees in linear time under the POSIX leftmost-longest rule;
upstream of the POSIX correctness work in [BT21]/[BT22].
DOI: <https://doi.org/10.1007/978-3-642-18098-9_25>. Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.4, §2.10.

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

### [PCRE2matching] PCRE2 `pcre2matching` documentation (software documentation, not a paper)

First-hand for what `pcre2_dfa_match` does and does not do: the
simultaneous-paths algorithm, all matches at one start position returned in
decreasing length order, and the stated reason captures are unavailable —
*"when dealing with multiple paths through the tree simultaneously, it is
not straightforward to keep track of captured substrings for the different
matching possibilities … PCRE2's implementation of this algorithm does not
attempt to do this."* Also the dependent restrictions (backreferences,
backreference conditionals, script runs, scan-substring assertions, `\K`,
`\C` in UTF modes, control verbs other than `(*FAIL)`,
`PCRE2_MATCH_INVALID_UTF`, JIT).
URL: <https://www.pcre.org/current/doc/html/pcre2matching.html>.
Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.9, §2.11.

### [RAhyb] Rust `regex-automata::hybrid` (software documentation, not a paper)

Crate documentation for the lazy/hybrid DFA in the Rust `regex-automata`
crate. Not a peer-reviewed publication; listed here because
`docs/dev/dfa_online_minimization_study.md` §2.3 cites it with the same
weight as the papers above.
URL: <https://docs.rs/regex-automata/latest/regex_automata/hybrid/index.html>.
Accessed 2026-09-04.
Cited by: `docs/dev/dfa_online_minimization_study.md` §2.3 (retrofitted by
lane m5paper); `docs/dev/optloop/captures_via_dfa_survey.md` §2.2.

### [RAonepass] Rust `regex-automata::dfa::onepass` (software documentation, not a paper)

Crate documentation for the one-pass DFA — *"the only DFA capable of
reporting the spans of matching capturing groups"*. First-hand for the
one-pass definition and examples (`a*b` yes, `a*a` no; `(?-u)\w*\s` yes and
`\w*\s` no, because Unicode `\w`/`\s` have overlapping UTF-8 automata), for
why unanchored searches are structurally impossible, for the documented
limits, and for the O(n)-vs-O(2^n) construction contrast against a general
DFA.
URL:
<https://docs.rs/regex-automata/latest/regex_automata/dfa/onepass/struct.DFA.html>.
Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.2, §2.11, §3.3.

### [RE2onepass] RE2 `re2/onepass.cc` (source, not a paper)

The leading comment of RE2's one-pass engine. First-hand for RE2's own
definition (*"at each input byte during an anchored match, there may be
multiple alternatives but only one can proceed for any given input byte"*),
its one-pass / not-one-pass examples, the 65,000-state and
`kMaxOnePassCapture` limits, the quarter-of-the-DFA-budget memory cap, and
the performance statement that the NFA runs at about 1/20 of backtracking
PCRE speed on a one-pass regexp while this code runs at about the same speed
— because *"repeated copying of the capture registers is the main
performance bottleneck in the NFA implementation."*
URL: <https://github.com/google/re2/blob/main/re2/onepass.cc>.
Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.1, §2.11, §3.3.

### [RegexTDFA] Haskell `regex-tdfa` package (software documentation, not a paper)

Chris Kuklewicz's pure-Haskell tagged-DFA engine for `regex-base`, now
maintained by Andreas Abel and others. First-hand for its POSIX
leftmost-longest claim with correct submatch capture, its derivation from
TRE/libtre ([Lau01]), its O(N) runtime with memory bounded by pattern size,
and its own caveat that *"regexes with large character classes combined with
{m,n} are very slow and memory-hungry"*. Historically the implementation
that answered whether a TDFA can do POSIX disambiguation correctly.
URL: <https://hackage.haskell.org/package/regex-tdfa>. Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.5, §2.11.

### [re2cman] re2c manual (software documentation, not a paper)

First-hand for re2c's two submatch-extraction policies as separate shipped
options — `--captures` / `--leftmost-captures` for *"submatch extraction
with leftmost greedy capturing groups"* and `--posix-captures` / `-P` for
POSIX — for the s-tag/m-tag distinction, and for the regular-expression
syntax section, which documents `*`, `+`, `?` and `{n,m}` and NO lazy
operator.
URL: <https://re2c.org/manual/manual_c.html>. Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.4, §2.11, §3.2.

### [re2cIssue208] re2c issue #208, "Is there a way to support Non-greedy match?" (issue tracker, not a paper)

Cited for ONE narrow fact — that non-greedy/lazy quantification (`a+?`) was
raised as a request against re2c rather than being existing syntax,
corroborating [re2cman]'s syntax section, which documents only `*`, `+`, `?`
and `{n,m}`.
`(unverified: the maintainer's resolution. The citing lane fetched the issue
page and the rendered content carried only the opening request, not the
thread's replies; the issue is closed. The citing document therefore rests
the "no lazy operator" claim on the MANUAL, and uses this issue only as
corroboration.)`
URL: <https://github.com/skvadrik/re2c/issues/208>. Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.4.

### [SL14] Sulzmann, M. & Lu, K. Z. M. (2014)

Martin Sulzmann, Kenny Zhuo Ming Lu — "POSIX Regular Expression Parsing
with Derivatives", *Functional and Logic Programming* (FLOPS 2014), LNCS
vol. 8475. Derivative-based POSIX submatching, implemented in Haskell as
`regex-pderiv`.
DOI: <https://doi.org/10.1007/978-3-319-07151-0_13>.
`(unverified, and recorded as a caveat rather than a claim: later work —
Ausaf, Dyckhoff & Urban, "POSIX Lexing with Derivatives of Regular
Expressions", ITP 2016 / JAR 2023, <https://doi.org/10.1007/978-3-319-43144-4_5>
— reports that gaps in this paper's correctness argument "cannot be filled
easily" and supplies simpler Isabelle/HOL-formalized definitions and
proofs. The citing lane read this from the later work's own abstract, not
from a line-by-line comparison.)`
Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.10.

### [TDFAwiki] Wikipedia, "Tagged Deterministic Finite Automaton" (tertiary source)

**TERTIARY**, and used only for the historical SEQUENCING of the TDFA line
(Laurikari 2000 → Kuklewicz's POSIX implementation → Trofimovich's
lookahead TDFA(1) → Borsotti & Trofimovich's formalization), every step of
which is independently cited to its own primary source in the citing
document. Listed because the citing document names it.
URL: <https://en.wikipedia.org/wiki/Tagged_Deterministic_Finite_Automaton>.
Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.4, §2.5.

### [TREreadme] TRE `lib/README` (source documentation, not a paper)

Laurikari's own description of TRE's architecture: `tre-compile.c`'s tagged
AST with *"appropriate minimized or maximized tags added to keep track of
submatches"* and its TNFA without epsilon transitions;
`tre-match-parallel.c`, which *"basically takes a string and a TNFA and
finds the leftmost longest match and submatches in one pass"* in O(l) and
*"cannot handle back references"*; `tre-match-backtrack.c`, *"a traditional
backtracking matcher"* at O(k^l) that *"can handle back references"*; and
`regexec.c`'s dispatch between them.
URL: <https://github.com/laurikari/tre/blob/master/lib/README>.
Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.3, §2.12.

### [TREsyntax] TRE `doc/tre-syntax.html` (software documentation, not a paper)

TRE's regex syntax reference. First-hand for TRE's support of MINIMAL
(non-greedy) repetition — *"Adding a `?` to a repeat operator makes the
subexpression minimal, or non-greedy"*, covering `*?`, `+?`, `??` and
`{m,n}?` — and for backreferences. **The citing document flags an
unresolved tension between this and [TREreadme]'s unqualified "leftmost
longest" description of the parallel matcher; neither source settles
whether minimal repetition is honoured by the TDFA matcher or routed to the
backtracker.**
URL: <https://github.com/laurikari/tre/blob/master/doc/tre-syntax.html>.
Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.3, §2.11, §2.12.

### [Tro19] Trofimovich, U. (2019)

Ulya Trofimovich — "Tagged Deterministic Finite Automata with Lookahead",
arXiv:1907.08837 (2019; an earlier 2017 version is distributed by re2c.org).
Extends [Lau00] with one-symbol lookahead — TDFA(1) against baseline
TDFA(0), *"by analogy with LR parsers LR(1) and LR(0)"* — which *"results
in significant reduction of tag variables and operations on them"*.
Formalizes the POSIX disambiguation algorithm Kuklewicz had described
informally, and reports lookahead TDFA *"considerably faster and usually
smaller than baseline TDFA; and … reasonably close in speed and size to
ordinary DFA used for recognition of regular languages"*. Implemented in
re2c.
URL: <https://arxiv.org/abs/1907.08837>; re2c.org copy
<https://re2c.org/2017_trofimovich_tagged_deterministic_finite_automata_with_lookahead.pdf>.
Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.4, §2.5, §2.11,
§3.2.

### [Tro20] Trofimovich, U. (2020)

Ulya Trofimovich — "RE2C: A lexer generator based on lookahead-TDFA",
*Science of Computer Programming* (2020). The engineering write-up of
[Tro19]'s algorithm as shipped in re2c.
DOI: <https://doi.org/10.1016/j.scico.2020.102510>; author's copy
<https://re2c.org/2020_trofimovich_re2c_a_lexer_generator_based_on_lookahead_tdfa.pdf>.
Accessed 2026-09-22.
Cited by: `docs/dev/optloop/captures_via_dfa_survey.md` §2.4.

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
lane m5paper); `docs/dev/optloop/captures_via_dfa_survey.md` §2.8, §2.11;
also referenced informally by name ("Hyperscan") in
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
- **[NF25] (Nicol & Frohme, 2025)** — `docs/dev/plan.md` keyed by the manager
  2026-09-04; `docs/dev/dev_journal.md` is append-only and keeps its inexact
  "(2023-24)" mention as written.
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
