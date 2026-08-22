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
