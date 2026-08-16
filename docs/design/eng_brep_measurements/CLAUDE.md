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

## Outputs

| file | probe | what the note takes from it |
|---|---|---|
| `replication_sweep.tsv` | `probe_replication.sh` | §1.2's cost table; the D45 cell reproduced at N=4000 |
| `erased_path_cost.txt` | ad hoc, serial | §1.4: pcrec's own time is quadratic; where the count lives in the emitted tables |
| `nfa_growth.txt` | `nfastats` scratch | §1.4: NFA states = 6N+3, and that `emit_vm.c` cannot change it |
| `possess_differential.tsv` / `.summary` | `probe_possess.py` | §2.4's v3 table: 0 soundness counterexamples in BOTH preference families |
| `possess_differential_lazy_control.summary` | `probe_possess.py`, `BREP_NO_LAZY_CONJUNCT=1` | §2.4's lazy refutation: 316 counterexamples without the conjunct, matching R24's independent 316 |
| `rung_census_derived.txt` | `census_rungs.py` | §3.2's whole table and §7's distinct-pattern count |
| `cell33_motivating_cell.txt` | `probe_cell33.sh` | §3.3's table, single-sourced |
| `possess_differential_v1_REFUTED.summary` | `probe_possess.py` v1 | §2.4's refutation: 117 counterexamples to disjointness alone. Kept because the refutation shaped the analysis |
| `corpus_possess.tsv`, `realistic_possess.tsv`, `census_summaries.txt` | `probe_possess_corpus.py` | §2.6's 18% vs 82% |
| `rung_census_default.tsv`, `rung_census_forcedvm.tsv` | `probe_rungs.py` | the RAW census rows; every figure §3.2 quotes is derived from these by `census_rungs.py`, never read off by hand |
| `lastiter_capture_derivation.txt` | ad hoc | §3.4: the plan row's capture formula refuted (1,799/15,036) and repaired (0/15,036) |
| `throughput_sweep.tsv` | `probe_throughput.sh` | §4.3's knee at K ≈ 16 |
| `termination.txt` | `probe_termination.sh` | §6's guard table and its 0 divergences |

## Known limits of these instruments

- **The oracle everywhere in THIS directory is python3 `re`.** No libpcre2
  check was run by this lane. **[R24] the panel ran one from outside** and
  confirmed the note's headline soundness result against libpcre2 (0
  counterexamples, identical population) plus §6's family three ways; those
  runs are the panel's instruments, not these, and are reported in
  `../../dev/reviews/2026-08-15-r24-eng-brep.md`. The note's §5.3 specifies
  the full three-way sweep; nothing here is it.
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
- **`probe_possess.py` tests only the OUTERMOST quantifier of each generated
  pattern.** Its `info[0]` selection is correct here because no PREFIX in the
  family contains a quantifier — now asserted rather than assumed — but the
  R24 soundness critic's warning stands: an extension that adds
  quantifier-bearing prefixes or tests nested quantifiers must not inherit
  that selection. Nested LAZY quantifiers are consequently unmeasured.
- **python-possessive is not PCRE2-possessive** (`docs/dev/upstream_issues.md`
  U9). PCRE2 10.46 does not backtrack into a preceding item after a
  possessive bounded repeat of a group, so the possessive SIDE of this
  probe's comparison is python-specific in exactly the swept family.

Maintenance: update this file when probes or outputs are added, removed, or
change role.
