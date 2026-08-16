# docs/design/eng_brep_measurements/ — the ENG-BREP design lane's instruments

Everything `../eng_brep_design.md` cites. Kept so the note's numbers can be
re-run rather than believed, and so the implementation lane inherits the
harnesses instead of rebuilding them.

**Nothing here is a proposed patch.** Two probes need a MODIFIED compiler (a
raised replication cap; an NFA-state `fprintf`). Both get one from
`probes/mkscratch.sh`, which builds into a SCRATCH COPY of the tree outside
the repository's build directory — so `src/`, `build/`, `make test` and the
known-fail ratchet only ever see the unmodified compiler. Every scratch patch
ASSERTS on its own anchor: a `sed` whose anchor has moved fails loudly rather
than silently building the stock compiler and reporting its numbers under a
prototype's name.

The archived outputs are **EVIDENCE, NEVER AN ORACLE** — no check reads them.

## Probes

- `mkscratch.sh NAME [FILE SED-EXPR]...` — tar the worktree (minus `.git`,
  `build*`, `worktrees`) into `$BREP_OUT/NAME`, apply the patches, `make`,
  print the built binary's path. The k18 lane's `prototypes/mkproto.sh`
  precedent. Two scratch compilers are used by the note:
  `bigcap` (`PCREC_MAX_VM_REPEAT_COPIES` raised to 100000, so the replication
  sweep can see past the cap) and `nfastats` (an `fprintf` of `nfa->n` at the
  end of `pcrec_build_nfa`, gated on `$BREP_NFASTATS`).
- `probe_replication.sh N...` — emitted lines/bytes, pcrec time and gcc time at
  −O1 and −O2, for the three strategies (VM+captures replicated, capture-erased
  DFA, choice-free cursor rung). Every compile is under `timeout`; a timeout is
  a recorded FINDING (`TIMEOUT>N` in the cell), never a reason to re-run
  longer. Note §1.4 of the design note: two `pcrec_s` cells in the archived
  sweep were taken under load from a parallel probe and were re-measured
  serially before being quoted.
- `probe_throughput.sh N...` + `tdriver.c` — the speed half of the K axis:
  full replication (K = N) against the frames-rung star (the K = 1 code
  shape), min of three trials, `-O2`. `tdriver.c` prints the span and group 1
  alongside the timing and the script refuses to compare times when the two
  artifacts disagree on the answer.
- `probe_rungs.py BINARY PATTERNS` — the RUNG CENSUS, read out of
  `--emit-ir`'s own RUNGS section (written by the emitter's own walk, so it
  cannot drift from the emitted C). Reports per-quantifier rows plus a
  summary; patterns that reach the DFA instead are counted, not dropped. Run
  twice for the note: default selection, and with `--engine=vm` forced.
- `probe_possess.py [--verbose]` — the DISJOINT-FOLLOW POSSESSIFICATION
  analysis stated as code and checked against python3 `re`'s possessive
  quantifiers in BOTH directions: soundness (possessifiable ⇒ identical) and
  non-vacuity (the "no" verdicts are where the divergences are). Generates its
  own family: 8 base counts, each spelled BOTH greedy and lazy against the
  possessive form, 8,032 pairs × 260 subjects. **This probe refuted the
  analysis the plan row states** — the header comment carries the two witness
  families that forced the unique-iteration condition.
  **[R24] the lazy half did not exist before the panel.** The old
  `possessive_form()` returned `None` for every lazy row (a lazy quantifier
  has no possessive spelling), so half the design's claim was silently absent
  from the differential; `spellings()` replaces it and derives both families
  from one base count, so omitting one now requires deleting a loop.
  `BREP_NO_LAZY_CONJUNCT=1` is the failing-direction control: it reverts the
  analysis to the refuted rule and reproduces the panel's 316 counterexamples.
  **[D47.6] `subjects()`'s alphabet excluded the discriminating character.**
  The original `ALPHA = "abcd "` never contained `z`, the byte every
  non-empty `PREFIXES` member (`"z"`, `"(?:z|)"`) is built from, so every
  z-prefixed pattern was swept without a subject that could enter its own
  loop — the lazy conjunct's reported "20 false declines" were this defect's
  visible symptom (all 20 genuinely diverge; see
  `../eng_brep_design.md` §2.4/§10.2 and `docs/dev/decisions.md` D47.6).
  Fixed: `z` joins `ALPHA`, and `subjects()` now also generates
  deterministic repetition-heavy subjects (long single-byte runs and
  two-byte cycles at lengths 6/8/10/12, each also prefixed by every pattern
  byte) instead of relying on the random tail to find depth by luck. The 20
  patterns this found are now guarded permanently at
  `../../../tests/base/possess_lazy_guard.rxt`.
- `census_rungs.py [OUTPUTS_DIR]` — **[R24 M-F1/M-F2/M-F3]** derives every
  rung-census figure the note quotes, in python, from the archived census
  files. It exists because the first version of those figures came from an
  uncommitted shell pipeline ending in `sort -u`, which under a UTF-8 locale
  merges strings differing only in punctuation (`\d+` and `[\d]+` collate
  equal) and so undercounted every "distinct" column. The script states its
  row filter and labels the (pattern, rung, detail) column as the LOWER BOUND
  it is.
- `probe_cell33.sh` — **[R24 M-F4]** the note's §3.3 table, all three rows
  from ONE serial run. The row it replaces mixed three sources and labelled a
  DFA artifact as the VM's cursor rung (`(?:ab){0,N}y` is non-capturing, so it
  requests no captures and never reaches the VM). The engine column is read
  from `--emit-ir`'s header per row, so a row cannot claim a rung the compiler
  did not take.
- `probe_possess_corpus.py PATTERNS` — the same analysis, IMPORTED not copied,
  applied to a real population. Run over the harvested `.rxt` corpus and over
  `realistic_patterns.txt`; the note reports both because either alone
  misleads.
- `realistic_patterns.txt` — 40 patterns of the kind bounded repeats actually
  appear in. Hand-written from memory of the shapes, which the file's own
  header discloses as a bias; the `.rxt` corpus is a compiler test corpus and
  is adversarial by construction, so it cannot answer "how much does this
  help".
- `probe_termination.sh` — R21 E-2's no-guard-for-bounded ruling, checked in
  the emitter's listing AND against python3 `re`.
- `archive.sh SRC NAME DESC` — copy a probe's raw output into `outputs/` with
  a D35 source-information header (date, commit, gcc, python, host). Stable
  filenames on purpose: a re-measurement lands as a git diff.

Pattern harvesting reuses `../k18_measurements/harvest_patterns.py` rather
than duplicating it.

**Added by the nested-lazy measurement lane (2026-08-16), closing the R24
NOTED residuals at §8 items 6 and 8 — see `outputs/nestedlazy_findings.txt`
for the full numbers per item:**

- `pcre2_ctypes.py` — a minimal python/ctypes binding to the installed
  libpcre2-8-0 RUNTIME (compile/match/ovector/free), the same dlopen
  precedent `tests/fuzz/pcre2_abi.h` uses for this box (runtime present, no
  `-dev` package, no `pcre2.h`). `version()` reads the live libpcre2 version
  string rather than hand-typing it. Self-check at `__main__` reproduces
  U9's own witness. Every probe below that talks to libpcre2 imports this,
  not a fresh binding.
- `probe_possess_nested.py` — the NESTED-LAZY differential (§8 item 8): a
  two-quantifier family (`PFX '(' INNER_ATOM INNER_SPELL MIDFIX ')'
  OUTER_SPELL FOLLOW`, 9,216 patterns) testing BOTH the outer's own verdict
  and the inner's, across all four preference combinations (greedy/greedy
  baseline + the three previously-unmeasured lazy combos). `info[0]`/
  `info[1]` targeting is asserted against each row's own `(lo, hi)`, not
  assumed. Two failing-direction controls, both via `probe_possess.py`
  module-level toggles (see below): `BREP_NO_LAZY_CONJUNCT` (existing) and
  the new `NO_ENCLOSING_FIRST`. Real analysis: 0/9,216×2 counterexamples.
  Both controls catch real divergences (68 and 212) when sabotaged.
- `probe_possess_pcre2.py` — Task B item 1: `probe_possess.py`'s own flat
  family (both preference families) re-run as TWO separate
  self-consistent differentials (all-python, all-libpcre2) rather than a
  cross-engine one, because U9 makes a cross-engine possessive comparison
  the wrong question. Carries a `is_u9_shape()` classifier so any
  libpcre2-only divergence is checked against U9's known trigger shape
  before it would be escalated. 10,032 pairs, 0 counterexamples either
  oracle, either preference, 0 U9-shaped.
- `probe_dollar_multiline_pcre2.py` — Task B item 3's remainder (the `$`
  MULTILINE gate, §2.5). `qualifies_except_for_follow()` filters the
  population to rows the current analysis already calls possessifiable for
  a benign follow (an unfiltered first run's 63/528 non-multiline
  divergences turned out to be almost entirely ambiguous/nullable bodies
  unrelated to `$`, disclosed in the script's own docstring and in the
  findings file). Split by which arm qualified the row: EXACT-COUNT is
  cleanly follow-independent (0/48 both prefs, both multiline settings);
  GREEDY DISJOINT reproduces "$ safe non-multiline, unsafe under (?m)"
  against BOTH oracles; LAZY DISJOINT diverges even without `(?m)`, and the
  probe's own docstring/findings explain why that is the PRE-EXISTING lazy
  conjunct (a bare `$` follow makes the remainder nullable, which the
  conjunct already declines for ordinary follows) rather than a new `$`
  defect — a note for whoever implements D47 ruling 5's live gate.
- `regen_body.py` — unparses a quantifier's own parsed BODY sequence back
  to regex source text, scoped deliberately to exactly the opcode set
  `first_and_nullable()`/`Glushkov` already model (anything else is
  declined by the analysis before reaching "possessifiable", so this
  module never needs to round-trip it — see its own docstring). Raises
  `Unsupported` (counted by the caller, never silently skipped) outside
  that set. Self-check at `__main__` round-trips 17 cases including
  ambiguous/nullable bodies, `\d`, ranges, and assertions, checking
  SEMANTIC (re-parse and match) not textual equality.
- `probe_corpus_diff_pcre2.py` — Task B item 2: extends
  `probe_possess_corpus.py`'s census (verdict COUNTS only) into a real
  DIFFERENTIAL over the .rxt corpus and `realistic_patterns.txt`. Every
  verdict=="possessifiable" row is tested as a minimal standalone
  reconstruction `(?:BODY){lo,hi}[?] FOLLOW` vs `(?:BODY){lo,hi}+ FOLLOW`,
  with BODY from `regen_body.unparse()` and FOLLOW/subjects built from the
  row's own computed `bf`/`eff` byte sets (never a fixed alphabet — the
  D47.6 lesson applied to a population this lane does not choose the bytes
  of). 306 possessifiable rows (230 corpus + 76 realistic — the realistic
  figure matches the design note's own 69+7 exactly), 0 python/libpcre2
  counterexamples; 6 cells hit libpcre2's own 65535 repeat-count limit
  (benign, not a divergence — python has no such cap); 1 body
  (`a(?i:b)*`'s inline-flag group) `regen_body.py` declines, disclosed.
- `outputs/nestedlazy_findings.txt` — the findings summary for this whole
  lane: populations, verdict splits, divergence counts, control catches,
  per Task/item, plus a closing table. Read this first for the numbers;
  the probes' own docstrings for method and rationale.

**`probe_possess.py` itself grew two things for this lane**, both additive
and backward-compatible: a second failing-direction control
`NO_ENCLOSING_FIRST` (mirrors the existing `NO_LAZY_CONJUNCT`, drops S2.2's
transitive-FOLLOW term for a nested quantifier), and an 8th element on every
`walk()` row tuple (`body`, the row's own parsed body sequence) — appended,
not inserted, so index-based consumers are unaffected; the one 7-tuple
unpacking consumer (`probe_possess_corpus.py`) was updated to match.

## Outputs

| file | probe | what the note takes from it |
|---|---|---|
| `replication_sweep.tsv` | `probe_replication.sh` | §1.2's cost table; the D45 cell reproduced at N=4000 |
| `erased_path_cost.txt` | ad hoc, serial | §1.4: pcrec's own time is quadratic; where the count lives in the emitted tables |
| `nfa_growth.txt` | `nfastats` scratch | §1.4: NFA states = 6N+3, and that `emit_vm.c` cannot change it |
| `possess_differential.tsv` / `.summary` | `probe_possess.py` | §2.4's v3 table: 0 soundness counterexamples in BOTH preference families. **[D47.6] re-archived** with the fixed `subjects()` (see the probe's own entry above) — same 0 counterexamples, but the `no` row's same/DIVERGES split moved (deeper subjects find more genuine divergence among already-declined cells); supersedes the 2026-08-16T01:41 run (reason recorded in the archive's own header) |
| `possess_differential_lazy_control.summary` | `probe_possess.py`, `BREP_NO_LAZY_CONJUNCT=1` | §2.4's lazy refutation: 316 counterexamples without the conjunct, matching R24's independent 316 |
| `rung_census_derived.txt` | `census_rungs.py` | §3.2's whole table and §7's distinct-pattern count |
| `cell33_motivating_cell.txt` | `probe_cell33.sh` | §3.3's table, single-sourced |
| `possess_differential_v1_REFUTED.summary` | `probe_possess.py` v1 | §2.4's refutation: 117 counterexamples to disjointness alone. Kept because the refutation shaped the analysis |
| `corpus_possess.tsv`, `realistic_possess.tsv`, `census_summaries.txt` | `probe_possess_corpus.py` | §2.6's 17% vs 82% |
| `rung_census_default.tsv`, `rung_census_forcedvm.tsv` | `probe_rungs.py` | the RAW census rows; every figure §3.2 quotes is derived from these by `census_rungs.py`, never read off by hand |
| `lastiter_capture_derivation.txt` | ad hoc | §3.4: the plan row's capture formula refuted (1,799/15,036) and repaired (0/15,036) |
| `throughput_sweep.tsv` | `probe_throughput.sh` | §4.3's knee at K ≈ 16 |
| `termination.txt` | `probe_termination.sh` | §6's guard table and its 0 divergences |
| `nested_possess_differential.tsv` / `.summary` | `probe_possess_nested.py` | §8 item 8: nested-lazy differential, 0/9,216×2 counterexamples, both controls catch (68, 212) |
| `possess_pcre2_differential.tsv` / `.summary` | `probe_possess_pcre2.py` | §8 item 6: flat family (both prefs) vs libpcre2, 0/10,032, 0 U9-shaped |
| `dollar_multiline_pcre2.tsv` / `.summary` | `probe_dollar_multiline_pcre2.py` | §8 item 6 / §2.5: `$`-follow safety, both oracles, split by arm and multiline |
| `corpus_diff_pcre2.tsv` / `.summary` | `probe_corpus_diff_pcre2.py` | §8 item 6: the two §2.6 censuses' possessifiable rows, differentially checked, 0/306 both oracles |
| `nestedlazy_findings.txt` | (findings summary, hand-written from the above) | per-item counts and what's closed vs still open |

## Known limits of these instruments

- **The oracle everywhere in THIS directory WAS python3 `re` only, until the
  nested-lazy lane (2026-08-16).** [R24]'s panel ran libpcre2 from OUTSIDE
  this repo (0 counterexamples, identical population, plus §6's family
  three ways — `../../dev/reviews/2026-08-15-r24-eng-brep.md`). The
  nested-lazy lane's four new probes above (`pcre2_ctypes.py` +
  `probe_possess_pcre2.py` / `probe_dollar_multiline_pcre2.py` /
  `probe_corpus_diff_pcre2.py`) bring libpcre2 INTO this directory as a
  committed, re-runnable instrument, and cover what was still python-only
  after R24: the LAZY family, both §2.6 censuses' differential-relevant
  rows, and the `$`/assertion follow sweep. The note's §5.3 full three-way
  sweep (adding pcrec itself, once possessify has an implementation) is
  still not run by anything here — there is no pcrec artifact to run yet.
- **`probe_possess.py`'s model widens `\d`/`\w` and every unmodelled construct
  to all 256 bytes.** pcrec has exact class bitmaps and would be strictly less
  conservative, so the census rates are LOWER bounds on what the shipped
  analysis can reach.
- **`probe_rungs.py` splits its TSV on tabs**, so a harvested pattern that
  itself contains a tab shifts that row's fields — **two such rows** in the
  forced-VM census, not one as this file previously said. `probe_rungs.py`'s
  own summary counts them under a nonsense rung name; `census_rungs.py` drops
  any row without exactly five fields and reports the surviving count, which
  is why its cursor stamp total is 1,402 where the probe's summary says 1,404.
- **`probe_possess.py` itself still tests only the OUTERMOST quantifier of
  each generated pattern** (`info[0]`, correct here because no PREFIX in its
  family contains a quantifier — asserted, not assumed). That limitation is
  now measured around rather than open: `probe_possess_nested.py` is the
  dedicated instrument for nested quantifiers (both `info[0]` outer and
  `info[1]` inner, structurally verified per-row), and nested LAZY
  quantifiers — the R24 soundness critic's specific worry — are covered
  there at 0/9,216×2 counterexamples with both controls catching real
  divergences when sabotaged. A future extension that adds
  quantifier-bearing PREFIXES to either probe must not inherit either
  probe's own index-based targeting without re-deriving it.
- **python-possessive is not PCRE2-possessive** (`docs/dev/upstream_issues.md`
  U9). PCRE2 10.46 does not backtrack into a preceding item after a
  possessive bounded repeat of a group, so the possessive SIDE of this
  probe's comparison is python-specific in exactly the swept family. This is
  why the libpcre2 probes above run TWO separate self-consistent
  differentials (all-python, all-libpcre2) rather than one cross-engine
  comparison — `probe_possess_pcre2.py` additionally classifies each row
  against U9's own trigger shape; 0 of the flat family's 10,032 rows
  actually diverged on it (U9's own note is that it surfaced in only 3
  cells of a much larger, captures-focused sweep elsewhere).

- **libpcre2 refuses a repeat count above 65535** (its own compiled-in
  limit; python3 `re` has none). `probe_corpus_diff_pcre2.py` hit this on 6
  cells (`a{65536}`-shaped rows harvested from the .rxt corpus, which
  exists to probe pcrec's OWN `PCREC_MAX_VM_REPEAT_COPIES`-adjacent limits)
  — reported as `pcre2_status = compile-error`, not a divergence; python's
  own differential still covers those rows at "same".
- **`regen_body.py` only round-trips the opcode set `first_and_nullable()`/
  `Glushkov` already model.** An inline-flag group (`(?i:...)`) inside a
  quantifier's body is the one construct this lane's corpus sweep actually
  hit (`a(?i:b)*`) — `regen_body.py` declines it (`Unsupported`, counted),
  which is correct because such a body is already declined by the analysis
  before reaching "possessifiable" (its opcode isn't in
  `first_and_nullable`'s modeled set either), so nothing possessifiable was
  left untested by the decline.

Maintenance: update this file when probes or outputs are added, removed, or
change role.
