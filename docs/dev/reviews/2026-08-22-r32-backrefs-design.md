# R32 — D6 panel on the [M6.5.1] backrefs module design

**Subject:** `docs/design/backrefs_design.md` + `backrefs_measurements/` on
branch `lane/brdesign` at **4cd461f** (2026-08-22, thirty-sixth session).
**Panel:** `r32eng` (opus, engine semantics vs libpcre2), `r32chk` (opus,
checks/tests/probe validity), `r32doc` (sonnet, citations/provenance).
Critics read-only, never ran `make`. Status: IN PROGRESS — appended as
reports arrive; verdict last.

## Manager findings (pre-panel) and rulings

### M-1 — §6.1 `forces_backref` + §11.5's tripwire arithmetic (HIGH, REFUTED by the lane itself)
The lane measured the tripwire population against its own design: backrefs
owns TWELVE qualifying rows, so `forces_backref` would be a third (twelve-
row) exception to a check whose text says the SECOND construct builds SR-8.
**Ruling (shared with R31 M-1, to be D67):** SR-8 is built in [M6.4.2];
`A_BREF` nodes are stamped from their rows and consumed by the generic
analysis; §6.1 and §11.5 rewritten in the revision round (qualifying stays
48, wired moves by 12). The lane's three contract notes are recorded in R31.

### Rulings on §15's ASKs
ASK-1 attribution of `(?J)` moves to `backrefs`, split noted (keyed
annotation via compliance-refresh). ASK-2 inline `(?J)` only. ASK-3 the
`--engine=dfa` branch-ordering fix lands in [M6.4.2]'s engine slice; §6.2
stays as the defect record with a pointer. ASK-4 one-shot commit-pinned
identity sweep (same reason as R31/atomic §11.2).

## r32doc — citations, marking, provenance (received 09:2x)

| ID | Sev | Location | Evidence | Verdict | Disposition |
|---|---|---|---|---|---|
| D1 | MED | `probes/archive.sh:26` stamps "module `assertions`" into every out/ header | copy-paste leftover from assertions_measurements' archiver; all 8 headers wrong; commit refs/dirty lists/content independently correct | REFUTED | FIX: re-scope the stamp, re-archive all eight in one batch |
| D2 | LOW-MED | §11.5 "33 built / 61 unbuilt" uncited | correct (registry_built_status_memo.md:382-384) but violates §0.1's own rule | WEAKENED | FIX: cite |
| D3/D4 | LOW | two citation-locality nits (mod_modifiers.c upper bound; internal.h:664-665 quote offset) | content not disputed | — | FIX: ranges |

SURVIVED: all other 69 citations verbatim (incl. the corrected revdet
no-default-arm claim, the run_codegen_tests.sh allowlist text, the RK_ESC
`\N{` precedent, all compliance.md lines post-DOC-DRV); provenance mechanics
exact (dirty lists out/-only, per-probe commits match, no orphans,
__pycache__ ignored); lane touched only its three charter paths; D26 clean
(§14 disclaims error numbers; numbers used only as discriminators); the nine
charter items map 1:1 onto §3-§12; §8 implements the ruled dupnames
semantics rather than re-deciding; §13 complete against the one BELIEVED
claim; stale figures none; the [M6.4]-lands-first framing consistently
conditional.

## r32eng — engine semantics vs the oracle (received 09:4x)

Instrument: `scratchpad/r32eng/simvm.py`, a faithful simulator of §3.2's
emitted model (slots, trailed writes, exact restore, A_CAP write-on-open /
write-on-close, frame-free A_BREF read). Replaying the design's own 37
archived cells: 36 agree, 1 diverges — and that one is E1.

| ID | Sev | Claim / location | Counter-evidence | Verdict | Disposition |
|---|---|---|---|---|---|
| E1 | HIGH | §3.2 props 1-2 + §3.5: "a slot is UNSET iff no live path wrote it", the two-slot UNSET test is total; self-reference needs no parser rejection | `emit_vm.c:3823-3833`: A_CAP writes slot[2k] at the OPEN position and slot[2k+1] at CLOSE. While a group is re-entered on iteration n>1, start holds iteration n's start and end holds n-1's end — neither UNSET — so the compare runs on a span that is no capture. libpcre2 publishes the pair at CLOSE (reference sees the last COMPLETED capture). The design's OWN cell S3 `(a\|b\1)+` on "ab": model (0,2) g1=(1,2); libpcre2 (0,1) g1=(0,1) (out/br_semantics.txt:39). 1,444-cell sweep: 36 divergences, ALL this class (`^(?:(a\|b\1))+$` on "ab" spurious MATCH). MEMORY SAFETY: `^(?:(a\|b\1)y)+` on "aybay" gives ref_s=2 > ref_e=1 → `size_t` length underflows to SIZE_MAX — an OOB read in EMITTED code. selfref.rxt takes only the agreeing S/F cells; no sabotage row | REFUTED | FIX (design): PUBLISH-AT-CLOSE — the open position goes to a per-group PENDING slot (or the existing start slot is treated as pending) and the (start,end) PAIR is published together at close, both trailed; A_BREF reads only published pairs; the signature asserts `ref_s <= ref_e` structurally. Cost the extra slot/write; re-run the 1,444-cell sweep on the corrected model; add the re-entry class to selfref.rxt and a sabotage row (publish-at-open) |
| E2 | HIGH | §7.2/§13 P-7: "the erasure is a genuine SUPERSET — the captured text is always in the group's language" | a group containing a POSITION PREDICATE is not a pure language: `(\ba)\1` on "aa" = (0,2), erasure `(\ba)\ba` = None; same for `^(^a)\1$`, `^(\Ga)\1$`, `^x((?<=x)a)\1$` — 6 of 10 cells FALSE NEGATIVE with constructs shipping today; none of the seven families has an assertion INSIDE the group | REFUTED (§7.1's no-prefilter ruling unaffected — safe direction; §7.4's nomatch-only charter premise false) | FIX: §7.2 restated as "superset iff the referenced group is assertion-free"; §7.4's charter inherits that condition; P-7 corrected |
| E3 | MED-HIGH | §5 rule 3/4: "two+ digits: backref if that many groups SO FAR, else octal; 8 and 9 terminate" | a multi-digit run BEGINNING with 8 or 9 is ALWAYS a backref to the whole decimal number: `\81` err 115 at 0/1/8/9/10/12 groups, OK at 81+; `\812` reads 812; the design's rule leaves an EMPTY octal run. No `\8N`/`\9N` cell in the archive. Rider: `\100` with 100 groups is a backref — references above \99 exist, §2 stops at \99 | REFUTED | FIX: rule 3' — a digit run starting with 8/9 is a decimal backref; re-measure; §2 table says "\N for any N" |
| E4 | MED | §3.8 "charge `took` on success and the compared prefix on failure" vs §4.2's `-1` sentinel | a single sentinel carries no prefix length; the failure charge — the case `(a*)\1` over a long subject needs — is inexpressible | REFUTED (recommendation); need real | FIX: return protocol carries the compared length on failure (e.g. negative-encoded), or charge `min(ref_len, remaining)` before the call |
| E5 | MED | §6.2's fix "the loop already records the first DFA-excluding why" | it records ONLY the first, and `analyses[]` is captures-FIRST DELIBERATELY (:168-175 rationale); `(a)\Kb` stamps "capture group at offset 0" — the construct's why is never computed. Reordering the BRANCHES alone regresses plain-captures (loses the --no-captures advice) | defect SURVIVED; fix REFUTED | RULING (travels to [M6.4.2] with ASK-3): record a SECOND why — the first NODE-derived exclusion — and take the captures branch only when it is absent; RX_ENGINE_WHY's first-row rule unchanged (no identity re-baseline) |
| E6 | MED | §6.3/§10: "the expansion's customer set is --no-captures builds" | `parse.c:704-708`: under --no-captures NO A_CAP node is created (tree identical to the non-capturing one); a --no-captures artifact has ZERO RX_SLOT_*. §3.2 has nothing to read; §10's matrix has no --no-captures row | REFUTED (framing) | RULING: a backref pattern under --no-captures KEEPS internal slots for REFERENCED groups and reports none (the \K precedent: the flag drops reported group slots); §10 gains the row; §6.3's customer-set sentence corrected — the expansion's deferral conclusion stands |
| E7 | MED | §4.4's proposed engine_callable COMPLEMENT check | its population is derived from the artifact's OWN declarations (the emitter's mask); `run_codegen_tests.sh:1013`'s empty-population guard is global and next_pos is unconditional, so an inlined compare that also drops the entry from the mask leaves the check nothing to assert while the guard stays green — control shares a source; also existential (one of two sites inlined passes); fixture table has no backref rows | REFUTED (proposal); reading of the shipped check SURVIVED | FIX: the fixture rows DECLARE which artifacts must carry a bref residual (test-authored truth, independent of the emitter); per-site counting (number of A_BREF sites = number of calls, from the pattern); module adds fixture rows |
| E8 | MED | §4.1 "shared-definition rule follows \b's precedent exactly" | `\b` reads `pcrec_cls_word_esc`, a shared bitmap; `cls_casefold` (parse.c:224-231) is `static` and widens a 32-byte BITMAP — not a byte→byte fold; nothing in src/gen/enc/ can call it; the entry would carry a SECOND spelling of A-Z↔a-z with no agreement test | WEAKENED | FIX: one shared fold TABLE object (or an agreement check over all 256 bytes at test time) |
| E9 | LOW-MED | §3.6's revdet bullet | rd_shape declines A_BREF in the body (SURVIVED); but the rung is NOT declined for the group-in-body/reference-outside shape (`(?:(a\|bb)x)+y` emits 16 revdet mentions); per-iteration capture writes are suppressed and reconstructed by the backward walk — traced as correct, but unnamed and uncovered | SURVIVED as stated; incomplete | FIX: name the interaction; a differential/sabotage row |
| E10 | LOW | "compile error THERE" (mrl.c), revdet alarms | -Wswitch is a warning; `make strict` promotes; `vm_nullable` has no default and falls to `return true` — S-BR3 requires actively adding a wrong arm | WEAKENED (wording) | FIX |
| E11 | LOW | §4.5's cost list | `pcrec_enc_ready` (enc.h:54) reads `e->decls`, which the `entries` array removes; every decls/defs caller moves | WEAKENED | FIX: cost list |

SURVIVED (evidence): the fold SET — 256×256 pairs against a caseless
backref compare: exactly 52 bytes fold, one partner each, no non-ASCII
(0xB5/0xDF/0xFF do not); length claim holds in byte mode; §4.4's reading of
the shipped check verbatim + S68; all 8 U cells and 5 E cells; PCREC_UNSET
= -1 cannot collide with (0,0); §3.6/§3.7 mechanism (vm_det_seq default,
rd_shape fall-out, RX_SET/TRAIL/PUSH/fail-label as cited); the CUT
paragraph (`^(?:(a|b)x)++\1$` on "axbxb" = (0,5) g1=(2,3)); §5 rules 1, 2,
4, 5 and all 12 class cells; §6.3's expansion numbers reproduce EXACTLY
(boundary 10,525/10,526, gcc 2.05 s); §7.3's axis is the real one (hybrid
vs vm on the identical erased pattern with a skip control) — two caveats:
ratios understate the real cost (the shipped pattern also pays the compare)
and the filler is the prefilter's best case; §8.1's 17 rows + 6 new cells
("checked at each declaration against the scoped state"); §8.2's NAMETABLE
bytes read for 10 patterns incl. mixed case and `_`/digit names — (name asc
by byte, number asc) on all; rx_group_entry unchanged; §8.3 under a harder
battery (first-set-EMPTY three-way runs; declaration inside a reset
quantifier; repeated alternation runs; all five spellings) — and
DECISIVELY PCRE2 does NOT retry later run members when the first-set one's
compare fails, so the frame-free else-if chain is the right shape; §10's
matrix incl. (?J)'s two refusal sites; §9/P-5's `\N{` precedent real.

## r32chk — checks, tests, sabotage rows, probe validity (received 09:4x)

All eight probes re-run into scratch: six byte-identical to out/; the
expansion boundary reproduces for a THIRD time from a third tree
(10,525/10,526, 7,116,509 B); the prefilter ratios inside §7.3's ranges
(rows swap between runs exactly as §7.3 predicts).

| ID | Sev | Claim / location | Evidence | Verdict | Disposition |
|---|---|---|---|---|---|
| C1 | HIGH | §11.5 "qualifying drops by the rows this module builds (51→48's movement)"; §6.1 declines SR-8 | named-groups' rows LEFT the population by reclassification; §6.1 keeps VM_ONLY, so `qualifying` stays 48 and `wired` goes 1→13 — twelve `bad(...)` hits; registry_check.c:1424-1427 forecloses a second exception; the 48 is hand-typed at :1473-1477 | REFUTED | = M-1 (SR-8 built in [M6.4.2]); §11.5 rewritten; the hand-typed 48 named as a pin this module's change must move |
| C2 | HIGH | §4.4's complement check "the same discipline, one field wider" | `calls_in_bodies()` (:986-1004) is a single `inbody` boolean — no loop/label awareness exists; the violation rule is raw `index($0, want)` with NO comment filtering, so a comment naming `rx_bref_match` (which §3.2's emitted shape places beside the call) satisfies the complement — S-BR5 goes green by construction | REFUTED (mechanism) | FIX with r32eng E7: fixture-declared expectations, comment-stripped call-site counting per A_BREF site; the "not in a scan loop" clause DROPPED (no mechanism) — S68's anchor survives the refactor (verified) |
| C3 | HIGH | §11.1 oracle markings: caseless.rxt and octal_class.rxt "python-verifiable" | python refuses 4/9 caseless cells (`^(?i)(a)(?-i)\1$`, `^((?i)a)\1$` — the load-bearing §3.1(c)/F7 cells) and 4/12 class cells (`[\8]` `[\k]` `[\g]` literal in PCRE2/pcrec, errors in python; `[\400]`) | REFUTED | FIX: mark pcre2-only per cell; upstream_issues.md entries; §12 states these divergences |
| C4 | HIGH | §11.4 completeness | no row plants a PREFILTER on a backref pattern (§7.2's measured wrong-answer mode); none for §5.3's deferred validity (nonexistent group silently accepted), §8.2's qsort tiebreak (silent non-reproducibility), §6.1's registration | REFUTED (completeness) | FIX: four rows added (prefilter-on-bref is the first) |
| C5 | HIGH | §11.5 "check_built_status_defects gains this module's rows for free" | the check (registry_check.c:1694-1744) asserts `defects == 0` only; built/unbuilt tallies are INTERPOLATED INTO THE ok() STRING and compared to nothing; PC-3 never reads the column — "33/61" is pinned by no test; §9's seven-row table has no check behind it | REFUTED | CROSS-PANEL FIX (lands in [M6.4.2], first module to flip rows): registry_check asserts the built/unbuilt/na tallies EXACT, moved by each module's landing; R31 C8's pins join it |
| C6 | MED | §9's built predictions | `built_status_probe` drives the row's syntax ALONE (`\1`, `\k<name>`, `(?P=n)` are err 115 standalone in PCRE2); they derive `built` ONLY because §5.3 defers validity to end-of-parse — uncited; `[\1]` compiles everywhere while `\1` reads unbuilt (atom-position-only granularity) | WEAKENED | FIX: §9 cites §5.3 as the reason; the granularity note |
| C7 | MED | §10's after-table: bare `\k<n>` under backrefs,named-groups "compiles" | PCRE2: err 115 (no group `n`); gated.rxt would pin a tier-1 divergence | REFUTED (cell) | FIX: the cell is a refusal; gated.rxt's accept cells oracle-verified |
| C8 | MED | §7.2/P-7 "28,160 subject-family pairs" | sampling with replacement: 11,042 distinct (letter/finite/star 127 each, 31.5x inflated); `letter` and `finite` are the same language pair over the same list — seven families is six | WEAKENED | FIX: distinct counts; dedupe; FALSE-NEG denominator = true-hit rows |
| C9 | MED | §7.3 "filler whose 7-letter words all differ" | each word is seven IDENTICAL letters; `(\w)\1` matches at (0,2) in the filler — the `letter` row is noise anyway | WEAKENED | FIX: wording + filler |
| C10 | MED | §11.2 cites run_kreset_diff.sh's shape | that driver has six sections (entries vs libpcre2; the find-all loop; --no-captures) and THREE population guards (nwrite==NK, ent_nz, fa_empty floor); §11.2 describes one section and no guard; §11.3's citation is to the wrong file | WEAKENED | FIX: drivers specified with the entries + find-all sections and asserted-exact floors |
| C11 | MED | §12 goal facts | omits the caseless divergence (`^((?i)a)\1$`) and the class-position divergences; points the blinded author at tests/ paths the cell allowlist denies | WEAKENED | FIX: add the divergences; pointers only to docs/design/eng_brep_measurements/probes/pcre2_ctypes.py (+ br_oracle.py under docs/) |
| C12 | MED | probe_erasure_hazard's FALSE-NEG column | VACUOUS guard sound; but no positive control proves FALSE-NEG can be non-zero — (E2's assertion-in-group cells ARE that control now) | WEAKENED | FIX: add E2's cells as the positive control |
| C13 | MED | probe_prefilter_cost's guard | compares stamps not engines (a DFA artifact's empty stamp passes); fact right, control doesn't establish it | WEAKENED | FIX: assert RX_ENGINE equal on both arms |
| C14 | LOW | archiver stamps "module `assertions`"; §0.3 "nine files from archive.sh" | out/CLAUDE.md is hand-written and claims the same of itself | = r32doc D1 | FIX |
| C15-C19 | LOW | §6.3's table "pasted" (a reordered faithful subset); dead `states` and missing cls26x2 baseline in probe_expand_cost; dead `nrows` in probe_prefilter_cost; hand-typed "seven" (nine cells/eight patterns); P-5's rank answerable now (higher wins, `\g` rank 0); axis A measures 255 bytes (`.` excludes 0x0a) | — | FIX: wording/probes |
| C20 | — | §13/§14 gaps | the tripwire collision; the complement check; `\0`'s gating split undecided; families lack nested backrefs/`\K`; `star` has 88 negatives | — | FIX: §13 lists them; `\0` decided (stays refused naming backrefs — not a regression) |

SURVIVED (evidence): every probe reproduces; the corrected `_body()` filter
is discriminating (four positive controls DIFFER, the probe's cell SAME);
br_oracle's import self-check is two-directional and the `c_void_p`
restype makes the compile-error path safe; the printf/read -r fixes
load-bearing; §2's subroutine-vs-backref discriminator is a real
measurement; §9's RK_ESC-tail argument now MEASURED (higher rank wins, no
kind branch, disjoint tails cannot tie); §10's three "today" rows and the
(?J) two-source refusal reproduce; S68 survives the refactor; S-BR3's hang
is caught by the harness's derived timeout.

## Verdict in one paragraph

The backrefs design's MEASURED facts held almost everywhere — the fold set,
the octal matrix bar one rule, the dupnames resolution rule under a harder
battery, the NAMETABLE order, the expansion boundary (three independent
reproductions), the no-prefilter ruling — and its reading of the shipped
seam check (P14) is correct. What fell: (E1) the VM lowering's central
premise, "a non-UNSET slot pair is a capture", is false while a group is
re-entered — the design's own archived cell S3 refutes it, 36 divergences in
a 1,444-cell sweep, and two shapes underflow a `size_t` in emitted code —
the fix is PUBLISH-AT-CLOSE; (E2) the erasure is not a superset once the
group holds an assertion, so the chartered nomatch-only prefilter's premise
is false (§7.1 unaffected); (E3) `\8N`/`\9N` are decimal backrefs; (M-1/C1)
the tripwire rule, SR-8 built upstream; (E7/C2) the proposed complement
check shares a source with its subject; (C3) two corpus files mis-marked in
the direction that loses the oracle; (C4) no row for the wrong-answer
failure mode; (C5) the `built` column is asserted by nothing — a cross-
module fix; (E6) `--no-captures` creates no A_CAP node. HIGH count: M-1,
E1, E2, C1, C2, C3, C4, C5. NOT approved at 4cd461f; revision round with
focused re-check.

## Triage — the revision brief (lane/brdesign, same author)

MUST: E1 (publish-at-close design, cost, re-run the 1,444 sweep on the
corrected model, re-entry cells into selfref.rxt + a sabotage row, `ref_s <=
ref_e` structural); E2 (assertion-free condition; P-7; §7.4's charter
premise); E3 (rule 3'; `\N` any N; re-measure `\8N`/`\9N`); M-1/C1 (§6.1 →
stamping; §11.5 rewritten; the 48 named); E7+C2 (fixture-declared
expectations; per-site comment-stripped counting; drop the scan-loop
clause); C3 (markings; upstream_issues rows; §12); C4 (four rows, prefilter-
on-bref first); C5 (state the tally assertion as [M6.4.2]'s cross-module
obligation and this module's movement of it); E5 (the second-why ruling,
pointer to [M6.4.2]); E6 (the --no-captures ruling; §10 row). SHOULD: E4
(return protocol carries the failure prefix); E8 (shared fold table or
256-byte agreement check); E9 (name the group-in-body revdet interaction;
a row); C6, C7, C8, C9, C10, C11, C12, C13; E10, E11, C14-C20 (wording,
probes, archiver re-scope + one-batch re-archive). Rulings from §15 as
sent (ASK-1..4). Focused re-check: r32eng on E1/E2/E3 as revised; r32chk on
C2/C3/C4/C5.

## Revision round — lane/brdesign 4cd461f → b3d0b32 (27 commits since main; doc 1,708 → 2,341 lines; ten probes)

E1 verified by the lane before adoption (hand-traced `^(?:(a|b\1)y)+` on
"aybay" to ref_s=2 > ref_e=1; libpcre2 (0,5) g1=(2,4) = publish-at-close's
answer). The critic's simvm.py ADOPTED with one `publish` parameter
("a lane that re-implements the instrument that refuted it cannot detect
that it has softened it"); probe_publish_discipline.py, 5,808 cells in
three populations — re-entry 2,178 (open: 138 divergences / 40 reversed
spans; close: 0/0), ordinary 1,452 (0/0 both), backref-free CONTROL 2,178
(0/0 both). The control arm is what SCOPES the fix: publish-at-close for
REFERENCED groups only (per-group pending slot; pair published together at
close, both trailed; +1 slot, +1 trailed write per marked group per
traverse; A_BREF's emitted code unchanged), so §11.3's byte-identity holds
by construction. Oracle-side padding only (the probe's first run reported
a shape mismatch in the CONTROL column and was fixed on that side).

All ten MUSTs and every SHOULD done (table in the lane's report): E2 the
assertion-free gate with 6/10 false negatives as the POSITIVE control; E3
rule 3' (8/9-led runs decimal, four ordered questions, `\N` any N); M-1
stamping + §11.5 (48 stays, wired 1→13, the hand-typed 48 named); E7+C2
fixture-declared, comment-stripped per-site counting; C3 per-cell
markings + four upstream_issues entries; C4 eighteen rows led by S-BR14
prefilter-on-backref; C5 the cross-module tally obligation with +12/-12 +
(?J); E4 negative-encoded failure prefix; E8 shared fold table + 256-byte
agreement (S-BR11); E9 S-BR13; C7 bare `\k<n>` a refusal; C8 12,786
distinct pairs, the `finite` family removed; archiver re-scoped, nine
outputs re-archived in one batch, dirty lists out/-only. No disagreements;
two refinements (C15 "pasted" → "selection"; §13 P-11: the +12/-12 depends
on the `\g<`/`\g'` split landing).

**The lane's lesson, recorded in three places:** E1's counterexample was
already in the archive — cell S3 disagreed with §3.2's model from the day
both were written; nothing compared the archive to the claim.

Focused re-check dispatched: r32eng on E1 (incl. the simulator diff, P-1's
named gap, the scoping's observability), E2, E3; r32chk on C2 (P-10), C3,
C4, C5 (+ closures, re-runs).

## Focused re-check, r32chk on b3d0b32 — 17/20 CLOSED; C2 narrowed (3 residuals); six NEW

Re-runs: publish_discipline, erasure_hazard, caseless_fold byte-identical;
expand_cost boundary reproduced a FOURTH time (10,525/10,526, 7,116,509
B); prefilter_cost timing-only variation (N6). C9's new filler verified:
all five TRUE patterns no-match against the exact 256 KB subject. C12's
positive control "refuted the lane's own superset claim" — strong closure.
C3/C4/C5 and C6-C20 closed with evidence (C16's new baseline: cls26x2
VM-only 27,609 B vs the expansion's 321,302 B — 11.6x, strengthening the
decline).

| ID | Sev | Claim | Evidence | Disposition |
|---|---|---|---|---|
| C2 (a) | MED | §4.4 per-site count "the test knows because it wrote the pattern" | provenance unspecified: a `\<digit>` text scan is a SECOND implementation of §5's octal rule (`(a)\10` octal → count 0; `(a)\18` → 0 — S-BR8's own fixtures); a hand-typed integer collides with the no-hand-typed-counts rule unless DECLARED | REVISION 2: declared integer column; octal-ambiguous fixtures excluded or explicitly counted |
| C2 (b) | MED | the complement check's population | all six existing fixtures expect 0 / get 0; deleting the new rows leaves the check green over nothing — the diagnosed shape relocated to the fixture table | REVISION 2: scoped guard "≥ N fixtures declare ≥ 1 bref", N asserted |
| C2 (c) | LOW | comment stripping | the call spans two lines; a trailing comment on the call line survives a line strip; one pass or two unspecified | REVISION 2: token-level; S68 still fires |
| N1 | MED | S-BR17 (qsort tiebreak removed) | MEASURED: 8 rows / 4 dup pairs sorted name-only with glibc qsort -O2 → insertion order preserved (stable merge sort unless memory-starved) — undetectable or flaky | REVISION 2: structural detector (emitted (name, number) order / comparator totality) |
| N2 | MED | §13 P-11 "+12/-12 plus (?J)" | `\0` (ANY_ENGINE, outside the tripwire twelve) ALSO flips built per §9/§14 → 14 flips; the two new `\g<`/`\g'` rows are UNBUILT; correct: built 33→47, unbuilt 61→49, na 6, total 102 — tripwire population ≠ built-tally population | REVISION 2 |
| N3-N6 | LOW | §7.3 stale figures (40%/2%, 157x, five vs six runs); §0.3's erasure row still "superset (sound)"; S-BR14's detector names a nonexistent §7.2 driver section; a seventh run puts `tag` at 172.9x above the stated ceiling; C18 residue ("all seven" = 9 cells / 8 patterns); S-BR12 observable only after [M6.4.2] | — | REVISION 2 |

Revision 2 dispatched to lane/brdesign (r32eng's re-check still running on
b3d0b32; §3.2/§5/§7.2 held).
