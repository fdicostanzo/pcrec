# r1 — D6 panel on the [VAR] design (variables_common.md, variables_pattern.md, replace_design.md, variables_roadmap.md)

2026-09-23, compiled by lane `varfix` from the manager's rulings. Subject:
the four-note `[VAR]` design set (lane `vardesign`, merged into `main` at
`32902104`/`811b2295`), Frank's 2026-09-23 charter (quoted verbatim at the
top of `variables_roadmap.md`). Three read-only critics, distinct lenses,
launched concurrently in the session scratchpad: **mech** (opus — engine
mechanism: `select_engine.c`, the emit arm, the analysis declines, the ABI
byte-identity claims), **spec** (sonnet — contract/spec/prior-rulings:
D18/D26/D37/D38/D41.1/D80/D85/D87/D89/D94/D120 and
`docs/spec/match_api.md`), **test** (sonnet — tests/checks/MVP-measurability
against `docs/dev/learnings.md` §3, D27, D77, D119). Nobody ran `make`;
nobody wrote anything in their own reports.

**TOTALS: 2 BLOCKERS holding a third BLOCKER-shaped finding (MECH-B2, open to
Frank), 12 MAJOR, 4 MEDIUM, 6 MINOR, 6 NOTE — 30 findings across the three
lenses, plus 2 refuted BLOCKER candidates from TEST that on inspection are
not foreclosed and become a design gap (TEST-F3) and a wrong-attribution
correction (TEST-F1 vs a names-table already half-proposed).** The
mechanism's central claim — a pattern variable is a backreference whose
span comes from the caller — survived intact: `vm_bref`'s shape, the
work-charge metering, the caseless-fold machinery, the D70/no-`default:`
safety net, `[PATFACTS]`'s eventual absorption, and the general-mechanisms
discipline (F15) all held. What fell is concentrated in three places: (1)
the note's own byte-identity and "no code in `select_engine.c`" claims,
which conflated engine selection (free) with the prefilter decline (not
free, and previously unstated); (2) citation accuracy — a stale corpus
count, a mis-attributed ABI ruling, a retired function name, a stale line
citation for a house rule; (3) the MVP's own test-measurability, where the
harness had no mechanism at all to bind a `.rxt` case's variable to a
compiled artifact by name, and no oracle design existed for the pattern-side
match semantics.

**DISPOSITION SUMMARY:** every ACCEPTed finding is applied in this same
change (lane `varfix`, branch `lane/varfix`) directly to the four notes,
verified by grep (list at the end of this file). MECH-B2 is OPEN — Frank's
ruling, boxed at the top of `variables_pattern.md` §4 rather than resolved
in text. A handful of NOTE-severity mechanism findings (MECH-F11, F15) and
one SPEC NOTE (SPEC-F3's "in every mode" tightening) needed no rebuttal,
only the citation/derivation fix already applied.

---

## BLOCKERS

**MECH-B1 (mech-F1) — "no code in `select_engine.c`" is false for the
PREFILTER decline; only engine selection is free.** `prefilter_decision`
(`select_engine.c:549`) carries two hand-written whole-tree predicates,
`has_bref`/`has_call`, each feeding a construct-named `-fprefilter` refusal
— a decision the registry-driven `forces_registry` mechanism does not
reach, since VM-only and prefilter-free are two facts with two mechanisms.
Without a third predicate, `A_VAR` reaches `src/ir/nfa.c:908`'s loud
internal error the moment the prefilter build tries to walk it — not a
missing optimization, a compiler that cannot compile the module's own
corpus. **ACCEPT.** `variables_pattern.md` §3 rewritten: the design adds a
third whole-tree predicate `has_var` (`[DD-14]`'s `has_call` is the
precedent for exactly this shape) plus the third named noun in the
`-fprefilter` refusal, with `[PATFACTS]` (D120) named as the eventual
general home for all three. §2's `prefix_k` row and §8's core-vs-derived
verdict re-attributed to the prefilter predicate rather than to engine
selection. `variables_common.md` §6's fits-arch row corrected to match.

**MECH-B2 (mech-F2) — `<prefix>_match` IS `rx_matchfn`; §4.1 changes its
signature and §4.2 argues it does not — contradiction, OPEN to Frank.**
`rx_matchfn` is a fixed-literal ABI type shared by every artifact
(`match_api.md:915-918`, emitted unconditionally at `emit_dfa.c:1013`,
composability load-bearing per `match_api.md:1238`/`lib/pcrec.h:1326`).
§4.1 gives a var-bearing artifact's `<prefix>_match` a `vars` parameter,
which makes it no longer an `rx_matchfn` — the identical harm D38 rejected
in the very sentence §4.2 quotes approvingly, narrowed to var-bearing
artifacts. **DISPOSITION: OPEN — FRANK'S RULING.** An `[OPEN-FRANK]` box
added at the top of `variables_pattern.md` §4 stating the contradiction and
the manager's recommended option (a var-bearing artifact's own
`rx_varmatchfn` typedef; declining composition as a callout/submatcher in
the MVP with a named re-open condition) plus two one-line alternatives.
Text of §4 itself is unchanged pending the ruling.

---

## MAJOR

**MECH-M1 (mech-F3)** — `PCREC_ERR_UNSET_VAR` lands in the shared ABI block
`emit_dfa.c` emits unconditionally into every artifact (`:1034`/`:1051`/
`:1073`, no gate), so "a var-free artifact is byte-identical to today" is
false as stated (the same shape `match_api.md:178-179` records for the
`abi` 24→25 move). **ACCEPT.** The VALUE is fixed in the spec; EMISSION is
gated on the var-bearing bit (the `enc_mask`/residual pattern), so a
var-free artifact is unchanged except for the `abi` digit every artifact
carries. Restated precisely in `variables_pattern.md` §5, §4.2 and §8, and
in `variables_common.md` §8.

**MECH-M2 (mech-F4)** — "Five separate files each needing the same
one-line decline" undercounts: a brace-matched census finds **44** `AKind`
switches with no `default:` across **17** files, and most are not
declines — `nfa.c` must lower, `emit_vm.c` must emit, `lower_enc.c` (3
sites) must decide encoding-lowering of the expansion template,
`definitions.c` must rule core/reducible, `rxt_compose.c` (2 sites) must
place composer leaf lists. `[PATFACTS]` absorbs the five analysis declines
only, not these. **ACCEPT.** `variables_pattern.md` §2 rewritten with the
real count and file list, separating the analysis-decline population from
the real-work population; roadmap M5 resized S→M with the reasoning
stated, and the `[PATFACTS]`-graph note in §4 corrected. *Manager's brief
named "M7's size... moves up"; M7 (the entry-point/abi-ritual item) is not
the item this finding's population maps to — M5 ("the five analysis
declines") is, and that is the item resized. Flagged here for the
manager's confirmation rather than silently resolved either way.*

**MECH-M3 (mech-F5)** — `pcrec_maxw` does not exist (retired at [M5.0]
stage 2, `pcrec_cwmax` took its BYTE role); `pcrec_cwmin` (the character-pair
sibling) is omitted from the table; and the "maxw arm is not free" claim is
refuted by the arm itself — `pcrec_cwmax`'s `A_BREF` arm already returns
`PCREC_W_UNBOUNDED`, with every downstream consumer already written for it,
including `mod_lookaround.c`'s fixed-width rule, which means `(?<=${v})x`
is refused for free by the identical mechanism that refuses a backreference
there. **ACCEPT.** `variables_pattern.md` §2's table and prose corrected:
right function names, `pcrec_cwmin = 0` stated, the free lookbehind-refusal
consequence named, the unsupported byte-unit-upper-bound claim dropped.

**MECH-M4 (mech-F6)** — §1.3's "same return protocol, byte for byte" does
not deliver §7's ill-formed-UTF-8 refusal: the seam's return space is
two-valued by sign, with no room for "refuse," and the decoder's own
truncated/ill-formed case silently turns into NOMATCH — correct for a
subject (well-formed by construction) and wrong for a caller-supplied
value. **ACCEPT.** `variables_pattern.md` §1.3 states where the check
lives: the WRAPPER, once per call before the match (`O(vlen)` once, not per
position) — the general place for a per-call precondition, alongside
`PCREC_ERR_UNSET_VAR`'s existing check. The seam entry stays two-valued and
can keep assuming well-formed input, matching the subject-side code.

**MECH-M5 (mech-F7)** — "There is no compile-time-constant `memcmp`
anywhere in the VM" stopped being true one merge before the note was
written: `[OPT-REQPOS]` tier 2b (abi 30) emits a constant-length `memcmp`
against a compile-time literal in `emit_req_run_check`. The note's
conclusion survives (that mechanism cannot take a runtime operand without
becoming §1.3), but the supporting sentence over-claims. **ACCEPT.**
Narrowed in both `variables_pattern.md` §1.1 and `variables_common.md` §0.3
to "no compile-time-literal span compare in the VM's *instruction stream*,"
with `emit_req_run_check` cited as the near miss that proves the
distinction rather than left unmentioned.

**SPEC-F1** — §4.2 reason 3's "re-homed to `[LIB]`/definitions" is a
decline dressed as a deferral, and contradicts §1.2's own reasoning for
`${name/pat/repl}`: D85/D87/D89/`[LIB]` are every one of them COMPILE-TIME
mechanisms, with no path from a match-time `rx_var.p` into the DFA/VM
tables — running the compiler again after the artifact exists, the one
thing AOT-ness forbids, exactly what §1.2 already declines. **ACCEPT.**
`variables_common.md` §4.2 rewritten: a caller-supplied, match-time pattern
is declined ARCHITECTURALLY, for the identical reason `${name/pat/repl}`
is declined, with no re-open condition; `[LIB]`/D85/D87/D89 answer only the
compile-time-composition reading, which this feature has nothing to add
to. `variables_roadmap.md` §1's parallel sentence fixed the same way.

**SPEC-F2** — the "0/4,198" corpus count does not reproduce; the critic
counts 3,954 with the stated method. The zero-match verdict stands
(re-derived structurally, SPEC-F3), but a corroborating number nobody can
reproduce is a liability. **ACCEPT.** `variables_common.md` §0.2 replaced
with 3,954 and the exact `find`/`grep`/`awk` command inline; framed as
corroboration of the structural proof, not the proof itself.

**SPEC-F6** — the design's own `limits.def` row (§1.7's nesting bound) has
no named `docs/spec/limits.md` hunk anywhere in the four notes, though D90
requires one and the note is explicit elsewhere that a caller-observable
change needs its hunk "in the same change." **ACCEPT.** `variables_common.md`
§1.7 now states the D80/D90 obligation explicitly, citing `limits.md` as
D90's own spec.

**TEST-F1** — no generic mechanism exists (or is proposed) for the harness
to turn a `.rxt` variable binding into `vars[RX_VAR_<NAME>]`: `driver.c` is
one static file, never templated per pattern, with only positional/enum
runtime inputs; a name-indexed lookup needs `rx_info`'s vars-names table,
which the MVP as scoped shipped as a COUNT only (`nvars`), deferring the
table to an open question. **ACCEPT.** `variables_pattern.md` §9 Q2
PROMOTED into the MVP (no longer conditional on "if wanted"); §4.3's stamps
paragraph and `variables_roadmap.md` M7 updated to ship the names table
unconditionally, in the same `abi` event. `.rxt` line SPELLING is left to
the manager (DD-13b, unsettled by this lane); SEMANTICS fixed in a new
`variables_common.md` §3.5: one line per variable per case, shared by both
consumers, UNSET and EMPTY both spellable, values are bytes under the
artifact's encoding reusing the existing quoted-subject escape set.

**TEST-F3** — no oracle design exists for the pattern-side MATCH semantics
at all — §0.2 proves the `${...}` SPELLING is unsatisfiable, which is a
different claim from verifying the BUILT feature's match answers. The
brief's suspected foreclosure (D87's textual-composition hazard) does not
actually apply: a quotemeta'd value carries no capturing groups, so
splicing it perturbs no group numbering. **ACCEPT.** New
`variables_common.md` §3.6: QUOTEMETA-SPLICE as the MVP's primary,
independent oracle (caseless × UTF-8 × ordinary SET values); a
BACKREF-EQUIVALENCE differential labeled explicitly as a second-order
WIRING check sharing fold code with what it checks (learnings §3); the
uncovered population (UNSET/EMPTY refusal cells, the UTF-8-validity
refusal) named as oracle-less by construction, tested as refusal-table
rows instead. Named a delivery-bar item for M10.

**TEST-F4** — no population census is chartered for the MVP's own axes
(K35 applied prospectively): caseless × UTF-8, UNSET/EMPTY/SET,
variable-under-quantifier-or-alternation, same-name-twice are all named as
open questions but never assembled into a sized target, unlike every
comparably-scoped module this house has landed. **[proposed] ACCEPT** (no
explicit manager disposition given; applied consistent with the design's
own D77 discipline). New `variables_roadmap.md` §2.5: names the cross-product
and requires a `gen_corpus.py`-style plan before M10 lands, not designed
here.

**TEST-F9** — M10's **L** sizing is justified by comparison to
`[DD-13b.W23.4]`, a pure dump-format landing that never touched `driver.c`;
M10 is the first `.rxt` production needing a caller-supplied,
name-indexed RUNTIME value threaded into the compiled artifact, a cost
category W23.4 never paid. **ACCEPT** (combined with TEST-F2 per the
manager's ruling). `variables_roadmap.md` §5's M10 justification corrected:
the comparison class named as wrong, the driver-side NAME→INDEX lookup
work and the names table stated as the real cost, `.rxt`-var-line
substitution-only framing corrected in `replace_design.md` §3.9 and
`variables_pattern.md`'s cross-reference gap closed by moving the
directive to the shared note (§3.5).

---

## MEDIUM

**MECH minor-bucket, part 1 (mech-F8, [M5-SEAM])** — the `abi`-grep ritual
does not reach `tests/codegen/run_codegen_tests.sh`'s `[M5-SEAM]` fixture
table, which asserts an artifact's residual entry set FROM THE TEST, with
EXACT per-family population pins (five backref fixtures, seven lookbehind
fixtures). Adding `var_match`/`var_match_caseless` needs its own fixture
rows and its own exact population pin or ships with no detector. **ACCEPT
— fold into the note as one sentence** (per the manager's minors-bucket
disposition). `variables_pattern.md` §4.3 gains a paragraph naming the site,
plus the two new `PCREC_ENCE_*` bits' free slots (`1u<<4`/`1u<<5`) and the
`src/enc/CLAUDE.md` update the third-encoding recipe implies.

**MECH minor-bucket, part 2 (mech-F9, strict-vs-plain-make)** — "it
*cannot* build until every site names it" is a `make strict` property
(`-Wswitch` promoted to an error), not a plain-`make` property; under
plain `make` the missing case is a warning and the code runs, with two
different failure modes by site (spin forever / silent skip). Also a stale
line citation (`mrl.c:18-24` names the wrong paragraph; the rule is at
`:39-45`). **ACCEPT — fold in, fix the citation.** `variables_pattern.md`
§2 corrected on both counts, naming CI's `make strict` run as where the
alarm is real.

**TEST-F7** — D27 blinded-writer applicability is only PARTIAL and no note
says so: libpcre2's `SUBSTITUTE_EXTENDED` is a real independent authority
for the shared operator suite, but nothing in PCRE2 exists to read for the
pattern-side matching promise, which inverts D27's premise if a cell is
chartered for it. **ACCEPT — guidance in the roadmap.** New
`variables_roadmap.md` §2.4: the operator suite/replacement half is D27-clean;
a pattern-side cell's allowlist must additionally DENY the four design
notes themselves (the implementer's-own-vocabulary hazard D27 exists to
keep out); such a cell cannot start before the `docs/spec/` hunks land
(D80).

**TEST-F10** — the global-loop empty-match rule's core is oracle-verified,
but three of six named axes (`\G`, UTF-8 mid-codepoint, newline/CRLF) are
explicitly deferred in the ruled baseline and a fourth (lookbehind-anchored
interaction) is not discussed anywhere at all; the variable layer inherits
all four silently. **ACCEPT.** `replace_design.md` §3.8 now lists all four
explicitly, with citations, and notes the variable layer makes the UTF-8
gap MORE material (caller-controlled multi-byte content spliced at exactly
the deferred step-width position) without reopening `[DD-4]`/`[DD-11]`.

---

## MINOR

**MECH minor-bucket, part 3 (mech-F10, internal.h:877 census)** — the
tree's own census of `default:`-carrying `AKind` switches names four; there
are five (`vm_isl_words`, landed after the census, missing from it).
**ACCEPT — a KNOWN-ISSUE row, not a design-note fix** (a tree fact, safe as
found). `docs/dev/known_issues.md` gains **K63**; `variables_pattern.md` §2
carries a one-sentence pointer to it.

**SPEC-F8** — "D41.1" is credited with fixing five ABI type names; D41
ruling 1 fixes exactly three (`rx_ctx`, `rx_matchfn`, `rx_callout_ref`);
`rx_info`/`rx_group_entry` are fixed later, at D43/D44. **ACCEPT.**
`variables_common.md` §3.1 and §6 corrected to cite D41.1 for the first
three and D43/D44 for the other two (verified against `decisions.md`
directly, not against the note's own restatement).

---

## NOTE

**MECH-F11** — `A_VAR` has no NFA representation, which is what makes
MECH-B1's prefilter denial mandatory rather than merely a decline. Verified
intact; incorporated into §2's `nfa.c` citation wording (the "sound arm,
not a decline" phrasing).

**MECH-F12** — the new entry's memory-safety precondition is CALLER data
(`v`/`vlen`), where `bref_match`'s is STRUCTURAL (a published capture
pair), and the note never restated it; the pair `p == NULL && len > 0` is
unspecified. **[proposed] ACCEPT.** `variables_pattern.md` §4.1 gains a
paragraph: `p == NULL` implies `len` is ignored, checked at the entry
wrapper before any use of `len`.

**MECH-F13** — §4.4's `VE_VAR` listing row is proposed for the `slots`
section family, but `A_VAR` occupies no slot — its span is external, the
note's own central claim — so the row would make the `irsb` baseline
assert a falsehood. **[proposed] ACCEPT.** §4.4 corrected: `VE_VAR` gets
its own section or joins `program`, not `slots`, with the `VE_ISLAND`/
`VE_CALLOUT` reserved-with-no-producer precedent cited.

**MECH-F14** — §3's new `${` `RegRow` does not state how it resolves
against the shipped bare `$` row, though the resolution (SR-9's tail
arbitration) already exists and answers it cleanly. **[proposed] ACCEPT.**
§3 gains one paragraph citing `registry.c:1542`/`pcrec_recognise_tail_default`
(`:1753-1764`) — the correct function name; the critic's own citation had
it wrong.

**MECH-F15** — no parallel mechanism in the note itself (the general-
mechanisms discipline held); the hazard is in the REPAIR MECH-B1 forces (a
third hand-written predicate). Verified intact — MECH-B1's fix already
names `[PATFACTS]` as the eventual general home, closing the gap the
finding warns about.

**SPEC-F3** — the `$`+`{` unsatisfiability proof holds under three named
PCRE2-option variations (newline convention, `(?m)`, `DOLLAR_ENDONLY`), but
the note's "in every mode" did not enumerate them. **ACCEPT.**
`variables_common.md` §0.2 now names all three explicitly.

**SPEC-F9** — `${!name}`'s pattern-side safety is argued by citing D38 Q5's
MEASUREMENT, which was run against the replacement/template dialect, not
the pattern dialect; the conclusion holds but the derivation was borrowed
rather than worked out. **ACCEPT.** `variables_common.md` §1.4 now derives
the pattern-side case explicitly (`{!name}` is not quantifier-shaped, so
§0.2's argument applies again) rather than implying one measurement covers
both.

---

## Claims verified intact (no finding)

- `vm_bref`'s citations (`emit_vm.c:8103-8245`), the dupnames chain, the
  `engine_callable` guard, the work-charge metering — all confirmed
  correct, structure and line numbers.
- The work charge is sound for a variable: both compare bodies exit on
  `at + i >= n`, so one call's work is bounded regardless of `vlen`.
- §1.1's literal-shape claims (`A_CLASS`, `vm_cls_shape`/`vm_cls_test`, the
  per-byte emission arm) — confirmed correct (MECH-M5 narrows the
  surrounding sentence, not these).
- §1.4's D70 claim (`Ast`'s per-kind `union u`, the "new kind adds a
  member" rule).
- §2's `reqbyte`/`startanch`/`endwin` rows (case labels, line numbers,
  arms) — confirmed correct as far as they go (MECH-M2/M3 widen the
  surrounding claims, not these three rows).
- §5's error-code space (`PCREC_ERR_FLOOR`/`_INTERNAL`/`_STARTPOS`,
  `-8` as the next value) — confirmed correct (MECH-M1 narrows the
  byte-identity claim around it, not the code-space fact).
- §6.1 in full: `bref_match_caseless` ships under both backends, the byte
  fold is arithmetic and inline, the utf8 side decodes and folds through
  `utf8_fold_pairs.inc`, the length-changing case is handled end to end and
  pinned at `axis06`/`axis07`.
- §6.2's argument that pre-folding the value cannot work.
- §8's "no new opcode family, no new dispatch" — consistent with `vm_emit`'s
  structure.
- SPEC — D38's already-ruled status for every `subst-extended` operator
  `replace_design.md` §1 tabulates (spot-checked against D38 directly).
- SPEC — D23's 26% run-time-fold-indirection figure and its use as
  precedent against a resolver callback (`variables_common.md` §3.2).
- SPEC — the "byte-identical when variable-free" claim holds for the one
  real in-tree caller checked (`examples/makefile/main.c`), positive
  evidence beyond the note's own assertion.
- TEST-F6 — two proposed checks (the DFA-decline via SR-8's `forces_registry`;
  the var-free byte-neutrality claim via `scripts/emit_sweep.py`) reuse
  well-tested generic mechanisms and are LOW risk, applying the
  check-design lessons even to the checks that pass.
- TEST-F8 — the roadmap's phase triggers (Phase 2 Frank's stated want,
  Phase 3/4 genuine milestone-state flips, Phase 5/6 genuine measurement
  triggers, Phase 7 re-homed with citations) are measurements or
  explicitly-licensed wants, not disguised wishes — checked against D77 and
  D119 directly.

---

## Grep verification

Every citation and count fix below was verified by grep against the
delivered worktree state, not merely asserted:

Every command below was actually run against the delivered worktree, not
merely asserted — including two that first caught a stale count this
compile had missed (variables_roadmap.md §1 still had the old figure after
the first editing pass, found this way) and one description corrected
after the grep's own output disagreed with the claim, both fixed in place
rather than left inaccurate:

```
$ find tests -name "*.rxt" | xargs grep -cE '^pattern ' | awk -F: '{s+=$2} END{print s}'
3954
$ grep -rn "4,198" docs/design/variables_common.md docs/design/variables_pattern.md \
    docs/design/replace_design.md docs/design/variables_roadmap.md
(no output — CAUGHT ONE STALE HIT on the first run, in variables_roadmap.md
§1's own "one measurement" paragraph; fixed, re-run clean)
$ grep -n "D41.1 fixed (\`rx_ctx" docs/design/variables_common.md
(no output — the old five-name attribution sentence is gone)
$ grep -n "pcrec_maxw" docs/design/variables_pattern.md
1 hit — line 206, inside the sentence stating the function does NOT exist
("There is no `pcrec_maxw`") — the name appears because the corrected text
explains its absence, not because the erroneous claim survived
$ grep -n "mrl.c:18-24" docs/design/variables_pattern.md
(no output — stale citation replaced with mrl.c:39-45)
$ grep -n "no code in \`src/opt/select_engine.c\`" docs/design/variables_pattern.md
1 hit — line 276, a SUBSTRING of the new, correctly narrowed sentence
("Engine selection needs no code in `src/opt/select_engine.c`") — the
narrowing itself is confirmed by reading the surrounding §3 text, not by
this grep's absence
$ grep -n "OPEN-FRANK" docs/design/variables_pattern.md
1 hit — the box is present at the top of §4
$ grep -n "^### 3.5\|^### 3.6" docs/design/variables_common.md
2 hits — the new .rxt-directive and oracle sections exist
$ grep -c "K63" docs/dev/known_issues.md
1 — the new row's own header
$ grep -n "44 .AKind. switches" docs/design/variables_pattern.md
1 hit — the corrected 44-site census is in place
```

---

## OPEN (to Frank)

- **MECH-B2**: whether a var-bearing artifact's `<prefix>_match` gets its
  own `rx_varmatchfn` fixed-literal typedef (the manager's recommendation,
  boxed in `variables_pattern.md` §4) or one of the two named alternatives
  (vars on `rx_ctx`; a separate `_match_vars` entry beside an unmodified
  `_match`).
- **MECH-M2's roadmap-item mapping**: the manager's brief named "M7" as the
  item whose size moves up from the 44-site census finding; this delivery
  resized M5 instead, since M5 ("the five analysis declines") is the item
  the finding's population maps to and M7 (the entry-point/abi-ritual item)
  does not touch `AKind` switches at all. Flagged for confirmation rather
  than silently resolved in either direction.
