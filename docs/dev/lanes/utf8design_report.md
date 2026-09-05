# [M5.0] DESIGN-GATE lane — delivery report

**Lane:** `utf8design` (opus), worktree
`/Users/fdicostanzo/pcrec/worktrees/utf8design`, branch `lane/utf8design`.
**Delivered:** 2026-09-04. **Not merged, not pushed.**
`docs/dev/plan.md` untouched, as briefed.

## Deliverables

| path | state |
|---|---|
| `docs/design/utf8_design.md` | 1,496 lines. PROPOSED; unpaneled. |
| `docs/design/utf8_measurements/probes/` | 7 probes + oracle helper + remote bundler + archiver |
| `docs/design/utf8_measurements/out/` | 8 archived transcripts, all written by `archive.sh` |
| `docs/design/utf8_measurements/CLAUDE.md`, `out/CLAUDE.md` | written |
| `REFERENCES.md` | `[Cox07]`, `[Ragel]`, `[UCD]` added, cited from §2.3/§3.3/§4.4 |
| `docs/design/CLAUDE.md` | two entries added |

Nothing under `src/`, `tests/`, or `docs/spec/`. One WIP commit plus this
report's own.

## Section-by-section status against the charter

| charter item | section | status |
|---|---|---|
| (i) the lowering | §2 | **complete.** Construction cited, pipeline position fixed, all four byte-tier consumers answered, invalid-UTF ruled with a measurement, parser boundary drawn. |
| (ii) `\p{...}` | §3 | **complete.** 114 spellings measured; families staged; table sizing swept from the oracle. **The data-source question is an ASK, not an answer.** |
| (iii) DD-1 | §4 | **complete, and smaller than the charter expected** — simple folding only. |
| (iv) the seam's second instance | §5 | **complete.** All four residual entries instantiated; `\b` answered with a deliberate no-new-entry; the cross-note resolved. |
| (v) engine/selection | §6 | **complete.** Sizing measured, DFA-eligibility argued, prefilter answered with a new opportunity recorded-not-built. |
| (vi) the oracle plan | §7 | **complete.** 23 measured divergence rows against a charter minimum of 10; `.rxt` needs flagged, not written. |
| (vii) validation | §8 | **complete.** Identity gate, 8 sabotage rows, ~420-cell population, the `maxw` compatibility question answered as "the gate is the check". |
| (viii) module/staging | §9 | **complete.** Five stages, each with its own acceptance. |

## The five results that matter most

1. **The `[M5.0]` row's own CROSS-NOTE prescribes a cure that would break
   every lookbehind under UTF-8.** MEASURED: PCRE2 measures lookbehind length
   in **characters** (`(?<=[a\x{3b1}])x`, one branch, one character, one-or-two
   bytes, compiles with `MAXLOOKBEHIND` = 1). Setting `pcrec_maxw`'s `A_CLASS`
   arm to the maximum code-unit length makes `la_widths`' `minw == maxw` test
   read `1 != 4` for every class and refuses `(?<=a)x`. Resolution in §5.6:
   two quantities, two consumers.
2. **`\p{...}` does not require `PCRE2_UTF`**, so `unicode-props` is not
   encoding-gated and can land before the utf8 backend. Corollary returned to
   `[DD-11]`: its chartered second predicate is keyed on **UCP**, not UTF.
3. **10.46 does simple (1:1) folding only** — 0 of 11 one-to-many cells. This
   deletes `[FORM-CHAR]`'s object (5) `utf8-full-fold`. But the fold is a
   **closure** that **reaches outside the written range**, so it must run on
   code points before lowering.
4. **There is no state blowup.** `\p{L}` is a 283-state minimised DFA,
   `\p{L}*` is 282, UTF-8 `.*` is 9 — against 10,000/32,000 caps.
5. **`enc_byte.c`'s predicted witness for the length-returning backref
   residual is refuted; the decision is vindicated by a different cell.**
   `(?i)^(ss)\1$` on `"ss\xdf"` is no match under UTF; `^(k)\1$` on
   `k`+U+212A matches `(0,4)` — a 1:1 fold that is not length-preserving.

## The ASKs (§14) — six, none a ruling contradiction

1. **Invalid-UTF semantics.** Proposal: an ill-formed sequence matches
   nothing; no validation pass, no error return. Diverges from `PCRE2_UTF`'s
   default, which errors for the whole subject. Accept?
2. **Vendor UCD data files** at a pinned version (16.0.0) into
   `third_party/`. Both alternatives are disqualified and the disqualification
   is measured. This would be the first non-PCRE2 third-party data here.
3. **Make "simple folding only" a standing check**, or accept it as a
   re-measurement event on version bump?
4. **Is a UCP axis owed?** 8 of 28 divergence rows. Design recommends no.
5. **`ENG_ATTEMPT`'s start loop** tries mid-character starts under UTF-8 —
   harmless, wasted. Fixing it means routing a shared emitter loop through a
   residual entry, which S68 forbids. Leave (recommended) or charter?
6. **The `.rxt` third oracle value** (python-verifiable through `str` only).
   Route to `[DD-13b]` or charter a small amendment?

## Rulings received

**None.** `docs/dev/lanes/utf8design_rulings.md` was polled at each section
boundary (after the premises probe, after the oracle probes, before writing
§5's resolution, and before delivery) and never existed. Every decision in the
document is therefore the lane's own, and the six §14 ASKs are exactly the
places it declined to decide.

## Escalations and corrections owed at merge

- **`[DD-12]` is stale in two places.** It assigns the CharSet widening to
  MOD-0.6; D33 §7's own 2026-08-12 amendment reassigns it to "the first wide
  producer", which is this milestone. And its item (3) mischaracterises
  `PCRE2_MATCH_INVALID_UTF`. Both should be corrected on the row.
- **`src/gen/enc/enc_byte.c`'s backref comment** names a witness that is
  measured NOT to behave as it says. Its design conclusion is right; the
  example should be replaced with `^(k)\1$` (§12 P-6 makes this a check).
- **A note, not an escalation:** `--features unicode-props` on `\p{L}` still
  reports `\p requires module 'unicode-props'` rather than an
  enabled-but-unbuilt refusal naming the construct (`out/premises.txt` §3).
  Whether that matches the D38-consistent wording the `assertions` module
  established is a question this lane did not chase — it is D26 tier 3
  (wording) and it changes nothing in this design. Flagged so the
  implementation wave decides deliberately.

## Instrument defects (full detail in `out/CLAUDE.md`)

Four found by running this lane's own probes, plus one non-defect recorded at
the same length because the alarm was rung and did not sound (the
python-version axis does not move any of the 28 divergence rows — verified by
re-running the whole table under both pythons and diffing).

The one worth the manager's attention: **`-o /dev/null` was reproduced
verbatim** after `subroutines_measurements/CLAUDE.md` had already recorded it.
That is the second time this house has recorded that shape (R30 M6 was the
first). The durable fix is a shared probe fixture, not another entry.

## Method note: the remote oracle

This is the first lane here whose reference oracle lives on another machine.
Every libpcre2 claim was measured against **10.46 on the old box**, via a
stdin-delivered bundle that embeds the borrowed binding chain verbatim —
nothing was written on that box. `probes/bundle.py`'s docstring and
`utf8_measurements/CLAUDE.md` carry the mechanism and the argument for it.
**A local run measures a third library**: `find_library("pcre2-8")` on this
Mac resolves to miniconda's 10.37, not Homebrew's 10.48.

## DISCLOSURE — files injected at spawn

Beyond the brief itself, the following were injected into this lane's context
by the harness rather than read by choice:

1. **`/Users/fdicostanzo/pcrec/CLAUDE.md`** (session-root project
   instructions) — and separately the worktree's own richer `CLAUDE.md`,
   which carries the "Situation index" table the session-root copy lacks.
2. **`/Users/fdicostanzo/pcrec/worktrees/utf8design/docs/CLAUDE.md`** and
   **`docs/design/CLAUDE.md`** — auto-injected as a system reminder partway
   through the lane, not opened by the lane.
3. **A memory-index reminder** naming user/project memories.
4. The environment block (box facts, scratchpad path) and the available-skills
   listing.

No denied file was read. The lane read `src/`, `docs/dev/plan.md`,
`docs/dev/plan_completed.md`, `docs/dev/decisions.md`, `docs/spec/
match_api.md`, `APPROACH.md`, `REFERENCES.md` and the sibling design lanes'
probes deliberately, all within the mandated repository.

## Sub-lane

One measurement sub-lane (sonnet) built `probes/probe_sizing.py` — the
byte-automaton construction and its state counts — scoped to that one file
plus scratch, briefed with the scope mandate, and forbidden `make`/git writes.
It found and fixed a real construction bug via its own self-check (5,460
mismatches → 0) before any number left the probe. Its Unicode-version caveat
(python 3.11 = 14.0.0, PCRE2 10.46 = 16.0.0) is carried into the design as
§2.4 caveat 2 and quantified against §3.3's oracle-swept census.

## What was NOT done

- No `make test` (light testing only, per the brief): the tree was built
  (`make -j4 CC=gcc-16`, green) and probes compiled/ran; the suite was not.
- No `docs/spec/` edit. §7.4 and ASK 6 flag what `rxt_format.md` will need.
- No product code, no `tests/` corpus. The population is sized (§8.3), not
  written.
- **§12 P-5 is the measurement this design does not make**: §2.4 sizes
  classes in isolation, not the products a real pattern builds. That is the
  most likely place its comfort is misplaced, and it says so.

---

# APPENDIX — r54 REVISION ROUND (2026-09-04, second lane on `lane/utf8design`)

The original report above is the DESIGN lane's, and is not edited. This
appendix is the REVISION lane's, written against
`docs/dev/reviews/2026-09-04-r54-utf8-design.md` (5 BLOCKING, 10 MUST-FIX,
8 SHOULD, 6 NOTE) and the critics' full findings in
`docs/dev/lanes/utf8design_rulings.md`. **The design lane's author is gone;
this lane continued its branch.** Commits `c8c08e18..23d8e3f1`.

## 1. Method: every citation verified before it was built on

The brief's instruction was to verify each engine-critic citation rather than
inherit it, and **all of them held**. Verified at this tree, by reading the
file:

| citation | verdict |
|---|---|
| `compile.c:1228` hands `pcrec_emit_vm` the AST root | **CONFIRMED** |
| `emit_vm.c:1515/:3287/:4608/:7055` read `u.cls.bits` | **CONFIRMED**, all four |
| `enc.h:98-106` — `PcrecEnc` is `{id, name, entries}` | **CONFIRMED** |
| `parse.c:449`/`:898` negations, `:1115` `.` | **CONFIRMED** (`.` is at `:1115`, the critic said `:1117`; the bitmap fill is inside that case) |
| `pcrec_maxw`'s three call sites; `callgraph.c:795` the fixpoint | **CONFIRMED** by grep — and the design's own claim that MRL consumes `maxw` is FALSE, which is sharper than the critic put it |
| `emit_vm.c:6124-6141` redundancy proof, `:6335-6352` the `RX_R_INTERNAL` arm | **CONFIRMED** |
| `internal.h:934-963` `maxw_known`'s arena-zero argument | **CONFIRMED**, and it transfers verbatim to `cwmax` |
| `PREMUL_MAX_ENTRIES` = 65,535 at `emit_dfa.c:2081`, tested `:2522` | **CONFIRMED** — and `:2522` is inside `dfa_premul`, a FORM-SELECTION predicate, so exceeding it is not a refusal (below) |
| `dfa.c:934` `PCREC_MAX_SUBSET_ELEMS`, `dfa.c:173` the word refinement | **CONFIRMED** |
| `internal.h:595` — `revdet_first`'s sound all-bytes widening already exists | **CONFIRMED**, and it is what makes E5's DECLINE cheap |

**No finding was refuted.** One (E13) is accepted with a correction to its
reasoning; one prediction of the design's own (P-1) is refuted by this
revision rather than by the panel.

## 2. What changed, per finding

The design's own **§16 is the durable what-changed record** and the PANEL
OUTCOME block at its top is the finding→disposition→section map; neither is
repeated here. The three that reshaped the document:

- **E1** — §2.1 rewritten against `compile.c`'s real pass chain. The lowering
  is an AST→AST rewrite and **its position is DERIVED, not chosen**: three
  ordering constraints (`callgraph_build` must follow any node-rebuilding
  pass; `postresolve`'s width rule must precede the lowering because it counts
  characters; the NFA build and `emit_vm` must follow it) admit exactly one
  line, between `:999` and `:1018`. §2.1.4 adds `pcrec_cls_bits`, whose
  assertion turns E1's silent miscompile into a compiler assertion **at the
  site that would have committed it** — the difference between fixing a bug
  and closing a class.
- **E2** — the per-encoding complement universe, chosen over symbolic
  negation with a three-part argument (two representations; set identity vs
  the byte-identity gate; D23's ordering rule and S-U1's one constructor).
  This **retracts §5's headline**, and §5.0 says so rather than qualifying it.
- **E6** — and this one **moved a conclusion**. §2.4's "no blowup" was
  measured in states; `probe_sizing.py` now reports the binding caps' own
  units, and **`\p{L}{1,3}` is 80,465 entries against `PREMUL_MAX_ENTRIES`
  65,535 — 123%** — a row printed in §2.4's own quantified table from the
  first draft, sitting next to a state cap it clears at 2.6%.

## 3. Findings this lane made against the panel or against itself

Recorded because they are not dispositions:

1. **The UCP-SPLIT oracle is 7 of 8, not 8 of 8** (design §7.1.1). The panel
   cited one agreeing example and the family holds, but working the whole
   column found `\W` over a Greek letter, where `py/bytes` disagrees for a
   **unit** reason (it consumes one byte where PCRE2 and pcrec consume the
   character) and `py/str` disagrees for the opposite reason — **neither
   python engine gives pcrec's answer there.** So the author's rule is a
   PREDICATE, not a verdict label, and VERDICT and ORACLE are different
   partitions of the divergence table. Had this lane transcribed the panel's
   example, the corpus would have carried a wrong expectation on that cell.
2. **`[SEL-1]` is an encoding→engine mechanism** (§6.2.1), found by
   re-deriving §6.2 under the forced position. §6.2 said *"there is no
   mechanism by which an encoding could make a pattern VM-only"*;
   `forces_dfa_overflow` reads a machine SIZE and size is what the encoding
   changes.
3. **`pcrec_maxw`'s chain can be RE-AIMED, not retired-and-replaced**
   (§5.6.2) — the `maxw` fixpoint becomes `cwmax`, so the net is one new
   fixpoint and one new memo field, against the panel's "two more fixpoints +
   two more memo fields". S171 keeps its row with a re-pointed `SAB_FILE`.
4. **`PREMUL_MAX_ENTRIES` is not a refusal.** `emit_dfa.c:2522` sits in
   `dfa_premul`, an `[ENG-FORM]`/D82 form-selection predicate; exceeding it
   costs `[OPT-3]`'s 1.27×. The probe's first draft printed `REFUSES` and it
   was corrected to `premul`/`PLAIN` **before** the transcript was archived —
   a confidently wrong label is what this directory's own defect catalogue is
   about.
5. **The ASCII-corpus population is 3,319, not 3,349** (§8.5). The obvious
   byte scan over the `.rxt` files misses **30 blocks whose subjects contain
   high bytes written as escapes** — and those 30 are precisely the ones the
   encoding differential must exclude. R13's lesson (*counting a population by
   an instrument that cannot express it counts the instrument*), reproduced in
   this lane after being cited in it.
6. **E2's blast radius is small and its consequence is total**: 198 of 3,350
   corpus patterns (5.9%) contain a negation-producing construct, and against
   a 100%-byte-identity bar that is not 5.9% of the failure but all of it.

## 4. Measurements: re-run, with real provenance

**All eight transcripts re-archived** at a commit that tracks the probes.
Three tooling fixes landed first (`c8c08e18`), then the runs:

- **meas-1** — `bundle.py` computed `_BUNDLED_SHA` and **nothing read it**;
  `u8_oracle.source_shas()` + a header block now print it in two labelled
  modes, `bundled` (authoritative) and `local` (weaker, and it says so).
  Verified agreeing across the ssh boundary on `probe_width.py`.
- **meas-3** — `archive.sh`'s `|| echo uncommitted` never fired (`git log` on
  an untracked path exits 0 with empty stdout); emptiness test now.
- **meas-5** — `probe_uprops.py`'s dead ternary removed.
- **meas-2** — `sizing.txt`'s blank `RUN DATE` **cause found**: an earlier
  `archive.sh` used GNU `date -Is`, which fails on BSD `date`. Already fixed
  in the script; only a re-run could show it.
- **E6** — `probe_sizing.py` gained sections (h)-(k) and a cap-units table.
  The minimization is computed once and shared, so the addition costs nothing
  on the two slow rows.

Five probes ran **remotely against libpcre2 10.46** over
`ssh duxevents@192.168.1.100` (host/version/mode in every header; `libpcre2
10.46 2025-08-27`, `Linux 7.0.0-29-generic`, python 3.14.4); three ran
`--local` (`probe_sizing.py` needs no oracle, `probe_premises.sh` measures
pcrec, and `divergence_local_py311.txt` is the deliberate python-version
comparison). **Nothing was written on the reference box.**

## 5. What was NOT done

- **No merge, no push** — the brief's instruction.
- **No `src/`, `tests/`, `cli/` or `lib/` file touched.** Verified:
  `git diff --name-only 16d5adc2..HEAD` is 13 files, all under
  `docs/design/`.
- **`docs/dev/plan.md` untouched**, per the brief.
- **No `make test`.** The tree was built (`make -j4 CC=gcc-16`, clean) and the
  probes ran; the suite was not, per the light-testing instruction.
- **The §14 ASKs are NOT resolved.** ASK 7 was ADDED (the D58 seam-field
  record, which E2's repair forces), and ASK 4 was **re-priced** rather than
  answered — §5.4.1 finds a UCP axis costs `upc_of_class`'s mechanism
  replaced, a DFA state-identity change, where the first version priced it at
  one seam entry. An ASK priced wrong is an ASK answered wrong; the ruling
  stays Frank's.
- **The design is not verified against a build**, because nothing in it is
  built. §15 is this lane's own ranking of where it is still weakest, headed
  by §2.1.2's three constraints — two of which are read off comments rather
  than off checks, and whose failure would be the largest simplification
  available (P-12 invites it).

## 6. DISCLOSURE — files injected at spawn

The session-root `CLAUDE.md` (the worktree's own copy, identical in the
mandated content), `docs/CLAUDE.md`, `docs/dev/CLAUDE.md`,
`docs/design/CLAUDE.md`, `docs/dev/reviews/CLAUDE.md`,
`docs/dev/lanes/CLAUDE.md`, `docs/design/utf8_measurements/CLAUDE.md`, and the
memory index. No denied file was read. This lane read `src/core/compile.c`,
`src/core/internal.h`, `src/core/limits.def`, `src/parse/parse.c`,
`src/parse/mod_lookaround.c`, `src/ir/dfa.c`, `src/opt/mrl.c`,
`src/opt/callgraph.c`, `src/opt/revdet.c`, `src/opt/select_engine.c`,
`src/gen/emit_dfa.c`, `src/gen/emit_vm.c`, `src/gen/enc/enc.h`,
`src/gen/enc/enc_byte.c`, `tests/mech/CLAUDE.md`, `tests/harness/verify_rxt.py`
and the `.rxt` corpus **read-only, to verify the panel's citations and to count
populations** — all within the mandated repository, none modified.
