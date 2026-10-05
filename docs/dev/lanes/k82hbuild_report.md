# k82hbuild — K82 (B): THE HANDOFF, built (2026-10-05, lane k82hbuild, opus)

Branch `lane/k82hbuild` from main `25319ae6` (abi 60). Design:
`docs/design/litscan_k82h.md` revision 2, its two LINEAGE paragraphs, §R and
Frank's rulings of 2026-10-05 (Q1-Q8 in the note; Q9 and Q10 built to the
design's recommendations: keep the (d') decline, DECLINE on count-collapsed
prefilters). Panel record: `docs/dev/reviews/2026-10-04-r1-k82-handoff.md`.
NOT merged.

## 0. Summary

- **The mechanism.** A new two-row first-match table, `req_uses[]` (axis
  `req-use`, `--list-axes`), decides what a search body does with an EMITTED
  run pre-check's answer. Row `handoff` (`-fno-req-handoff`, bit 46, a member
  of `strategy_denials`) keeps the gate's first window hit `c` and begins the
  body's scan at `max(search_from, c − K)`; `scan-from-startpos` is the
  fallback. K is a new CORE fact on `src/facts/req.c`'s one walk, the run
  window's maximum BYTE offset from the attempt start (`req_run_maxoff` in
  `--emit-facts`). The three bodies with a DFA scan read the kept start at ONE
  site each: the DFA unanchored scan (its position AND its seed), the DFA
  attempt loop's first start, the VM hybrid's first prefilter call. `\G`
  keeps reading `search_from`. Under a multibyte encoding the moved start is
  rounded up to a character start (uncapped, only when it moved).
- **abi 60 -> 61**, one event. `<PREFIX>_REQ_HANDOFF` (`"<K>"` or `"none"`)
  is on EVERY artifact of both engines (Q3 (a)), so every artifact gains one
  line; the readers were found by grep and re-pinned (§4).
- **Movers = the design's census, exactly.** Bench auto 47 (49 rows; 14 with
  K > 0; routes 39 unanchored / 2 attempt / 6 hybrid), corpus auto 160 (209
  rows; 27 K > 0; 121 / 6 / 33), `--no-captures` 160, forced hybrid 160;
  forced VM 0. Every cause-(B) cell moves (`mod-i`, `mod-r`,
  `cls-fold-pair`, `cls-pair-ctl` K = 0, `ci-strasse` K = 2); `union-select`
  does not. 0 off-diagonal; the deny arm is identical to BASE on every
  artifact (§3).
- **No answer moves.** The every-startpos differential over all 574 mover
  artifact-configs: 0 defects over 4,407,656 cells, plain AND under
  ASan/UBSan (§5.1). The invariant-F oracle (libpcre2 anchored attempts, no
  pcrec code in the loop) over 207 patterns: 0 violations in 1,054,207 cells
  (26,440 matches), its K − 1 control 5,519 violations (§5.2).
- **The fact has checks that do not share its source** (r1 C-C4): the hand K
  pin table (13 rows, `ci-strasse`'s K = 2 among them), the oracle, and the
  K − 1 plant over every K > 0 mover: 90 of 109 detected, the 19 misses
  explained (§5.3).
- **Sabotage S463-S477**, each with SAB_REACH/SAB_REACH_POP and an in-suite
  detector; S475 declared UNREACHED (no verb/callout node exists). Mech
  verdicts in §6.
- **Owed:** the Mac `make test` + `make test-axes` over the widened subset
  (launched as this lane's last act, §7), and the Linux alpha
  (`docs/dev/optloop/s4/alpha_k82h.sh`, written, NOT run — §8).

## 1. The fact: `req_run_maxoff`

`src/facts/req.c`'s walk carries each subtree's maximum width in BYTES
(`RbRuns.maxw`, saturating at `PCREC_W_UNBOUNDED` through `pcrec_sat_add`/
`pcrec_sat_mul`) and its run's maximum offset from the subtree's start
(`RbRun.off`): a head at 0, a tail at `maxw − n`, a right factor's best
`maxw(left)` further in, a join at the left tail's offset, a repeat's best in
its FIRST iteration; a min-0 repeat's body is walked for its width alone;
zero-width kinds are 0, `A_BREF`/`A_VAR`/`A_CALL` unbounded. A tail's and a
join's offsets are DERIVED from `maxw − n` where they are built, never carried
(the prototype carried `l.tail.off`, which an `rr_none`'s empty tail left at
0 — a latent under-statement the tie order happened to hide). The offset is an
annotation: `rn_better` is unchanged (§5.4's run-choice pin). The core half
is `ReqRun.whole_maxoff`; `pcrec_req_window` derives the window's `maxoff =
whole_maxoff + at`, published as the derived row `req_run_maxoff`
(`facts.def`, E2, depends `req_run`, no deny of its own; `unbounded` with
`decline:unbounded`).

On the design's table every value reproduces (`(?i)cat` 0, `(?i)straße` utf8
2, `x{2,5}(?i)cat` 5, `.{3}cat` 12, `é{2}cat` 4, `ab(?:cdef|xyzdef)g` 5,
`(?:a|bb)?catdog` 2, `(?:éx|ʩx)` 1, `(?:ab|c)(?i)select` 4; `\w+cat`,
`a.*?(?i)select` unbounded).

## 2. The emission

- `req_handoff_applies` (src/gen/emit_dfa.c), in order: the admission's own
  verdict, CALLED (`req_admit` emits, a run shipped); (a) a DFA scan in front
  (`pcrec_artifact_has_dfa_scan`) and not the empty machine; (b) K finite;
  Q10, not a count-collapsed prefilter; (d') not a VM hybrid with a `\G`
  start family whose prefilter span end is its ceiling
  (`pcrec_vm_prefilter_window`, now the ONE derivation `Vm.mrl_win` also
  reads). (g) has nothing to read: no AST kind exists for a verb or a
  callout (they are refused before a tree exists); the comment says the kind
  that adds one must decline here, and S475 is its tripwire.
- (c) and (d) are loud internal errors at the body (`req_handoff_assert_body`:
  the pinned search, and a `\G` start family on the unanchored machine);
  the hybrid with no prefilter is one in emit_vm.c.
- `emit_req_handoff` writes `size_t handoff_position = <p>_reqrun(...);`, its
  own `>= subject_length` NOMATCH, and — where its moving branch has a
  statement — `if (handoff_position - search_from > K) { handoff_position -=
  K; <round-up> } else handoff_position = search_from;`. Never `c − K`
  unguarded, never `search_from + K`. At K = 0 under `byte` there is no
  block.
- The round-up is `pcrec_emit_start_zero`'s new SIBLING MODE,
  `PCREC_START0_ROUNDUP`: the backend's own predicate, `while (!(START(p)))
  p++;`, bounded by the predicate's `>= n` clause and nothing else (no step
  cap), not gated on nullability (Q2).
- `pcrec_emit_req_byte_check` RETURNS the start expression; each body reads
  it once (`DfaForm.from`, which `seed_emit_seeded` now renders the forward
  seed from; `first` in `emit_attempt` and in the VM's search_run).
- The gate's leftmost-occurrence contract (§1.1a) is written into
  `ofs_test_emit_fn`'s header.

## 3. The mover manifest (`k82h_movers.py`, §4.1)

BASE `25319ae6` (abi 60) vs NEW (abi 61) vs DENY = NEW `-fno-req-handoff`,
with BASE's abi digit and NEW's `RX_REQ_HANDOFF` line normalized (and the
size-cap retry reasons, which quote a byte count that includes that line).

TBD-MANIFEST

## 4. abi 60 -> 61 and the readers (D76/D94, §2.3a by grep)

- The digit: `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI`; `match_api.md` the
  K80 `#error` text, §6's log entry ("is `61`"), §6.3's new stamp and the
  `REQ_WHY` `"emitted"` row; `run_codegen_tests.sh` `ABI_EXPECT=61` and its
  narrative; `run_recursion_identity.sh` FILEPIN self-pinned to `0f11cc3e`.
- The byte counts (the stamp line is 30 bytes at `-p rx`):
  `m5_stage1_stamps.tsv` all 12 `EMITTED_BYTES` rows re-recorded (+30 on
  ten, `\bword\b` +90 and `(?i)HeLLo` +80, the two §2.3a predicted program
  movers; each diffed); `run_resource_tests.sh`'s `a{5,25000}` pin 762574 ->
  762604 (diffed: the digits and the one line); `run_registry_tests.sh` axes
  186 -> 189 (measured); `registry.md` 126 rows / 43 axes.
- The size-cap note: the corpus's near-cap artifact
  (`tests/utf8/axis12_scripts.rxt:296`, 999,925 B) grows to 999,955 B, still
  under `PCREC_MAX_EMIT_BYTES`; the manifest found no refusal change.
- NOT re-pinned here: `docs/dev/artifact_size_log.tsv` (a refresh-commit
  artifact; every row moves +30 or more, the tripwire's 1,400,000 max is not
  near) — the chain's `make test` regenerates it; commit it or not at merge.
- Spec hunks (D80): `match_api.md` §3.1 (the scan-may-begin-later sentence
  and the step-budget sentence; the give-up clause is the Q10 decline, so the
  count-collapsed allowance sentence is NOT shipped), §6, §6.3; `tuning.md`
  §2.41 (new), §2.29's cross-reference, the flags table, the dial policy
  table (31 rows); `facts_listing.md`'s value column; `findings.md` (the
  handoff never re-picks); `cli.md`'s deny list; `registry.md`;
  `lib/CLAUDE.md` (bit 46 an ordinary `strategy_denials` member);
  `lib/pcrec.h`; `src/core/axes.def`.

## 5. The checks

### 5.1 Answer identity, every start position, per route

`k82h_answers.py` (BASE vs NEW through `tests/possessify/possdiff_driver.c`;
b1's sweep with `PREFIXES=1`, `k82h_gen.py`'s widest members, shifted /
doubled / decoyed subjects, and under utf8 1-6 stray continuation bytes
before, inside and after each subject, truncated and overlong leads). NO
allowance (Q10).

| arm | movers (unanchored / attempt / hybrid) | cells | defects |
|---|---|---|---|
| plain `-O1` | 574 (346 / 17 / 211) | 4,407,656 | 0 |
| `-fsanitize=address,undefined -fno-builtin-memcmp -DDIFF_EXACT_SUBJECT` | 574 (346 / 17 / 211) | 4,407,656 | 0 |

`tests/litscan/handoff.rxt` (§4.2 item 2): 66 blocks, 1,980 cases, green
under NEW and under BASE (the expectations are oracle-made, so BASE passing
is the check that they are not the handoff's own opinion).

### 5.2 Invariant F against libpcre2 (`k82h_oracle.py`, §4.2a (b))

libpcre2 10.48 (local; the binding borrowed from
`docs/design/eng_brep_measurements/probes/pcre2_ctypes.py`), PCRE2_ANCHORED
at every start position (utf8: with MATCH_INVALID_UTF, at character starts),
the window read off `REQ_RUN`: 207 patterns (41 with K > 0), 1,054,207
cells, 26,440 anchored matches, **0 violations**; python `re` cross-check
18,393 agreeing matches, 0 violations (1,278 cells where python's language
differs from PCRE2's — `a{,}` is a quantifier to python 3.9 — counted apart,
never scored); 892 cells where MATCH_INVALID_UTF moved an anchored attempt
past an ill-formed start, counted apart. The failing-direction control
(`KDELTA=-1`): 5,519 violations.

### 5.3 The K − 1 plant over every K > 0 mover (§4.2a (c))

`k82h_answers.py ONLY_K_POS=1` with a compiler carrying S463's plant: **90 of
109 K > 0 mover configs detected** (unanchored 64 / hybrid 26). The 19
undetected are 8 patterns, and each has a reason the sweep cannot reach:
- K is not TIGHT (the walk's bound exceeds every real offset, so K − 1 is
  still sound): `(?>a|ab)bc` (the atomic never takes `ab`),
  `(?:aa|a){8,12}+ab`, `(?:aa|a){1,3}+ab` (possessive), `(?:z|)(?:ab){3,}?`
  and `(?:z|)(?:ab){3,}?c?` (lazy), `(?:a\K){0,10}ab`;
- route masking: `(foo)?bar` (1 of its 3 configs) and `\bМосква\b` under
  utf8 (2 configs) — on the unanchored DFA route the reverse pass, bounded by
  `search_from` (Q6), re-finds the true start whenever the forward scan's
  END does not move, so a short K is visible there only when it changes the
  end. This is also why the design's S463/S470 witnesses on the unanchored
  route do not reproduce: `handoff.rxt` carries them on the attempt and
  hybrid routes. Frank's Q6 note (a reverse bound at `lo` as a free
  equivalence check) would make this route a strong K detector.

### 5.4 Structural (`run_prechecks.sh` §5.12) and encoding (DD12a(i) (v))

§5.12: the hand K pin table (fact AND stamp), the presence biconditional and
the subtraction's constant, bounded, the run choice (`ab.*xyzw` keeps
`78797a77`), the cross-table check, the start sites, the `\G` readers, the
round-up, (d'), the deny, Q10, and a population of 154 patterns with floors
(52 movers / 26 K > 0 / 27 unbounded-with-pre-check at the landing, floored at
80%). DD12a(i): the handoff region (rewrite + excise + rename + normalize,
8-line ceiling), each side held to its stamp, presence symmetric unless
`REQ_WHY`/`REQ_RUN` differ; 13 both-sides pairs at the landing (floor).
`run_encoding_checks.sh` 11 passed / 0 failed; `run_prechecks.sh` TBD;
`run_cpset_structure.sh` 28 / 0; `axes_registry_check.sh` 189 / 0.

## 6. Sabotage rows S463-S477

Highest S-id on main at branch time: S462. Every row: SAB_REACH (a probe on
the clean binary) and SAB_REACH_POP (the detector's own witness lines),
anchors copied from HEAD, detector in the suite. Validated one row at a time
with `tests/mech/run_sabotage_matrix.sh S<id>` on this branch:

TBD-MECH

## 7. Validation owed (the last act)

TBD-CHAIN

## 8. The Linux alpha (`docs/dev/optloop/s4/alpha_k82h.sh`, NOT run)

`alpha_k82.sh`'s protocol (taskset, load wait, round-robin launches, >= 50 ms
loops, absolute deltas against the floor): BASE = main before the handoff
(abi 60), NEW = this branch (abi 61), DENY = NEW `-fno-req-handoff`. `W`
cells (movers: NEW handed off and != BASE, DENY == BASE modulo the digits and
DENY's `"none"` line): the five cause-(B) cells at 64 KiB and 1 MiB,
`ci-ascii-control`, `slack`, `userpass`, `alt-shared`, `stack-frame`, and the
six outside movers (`sfx-64`, `lit-l31`, `kv-quoted`, `asr-wb`,
`anc-m-caret`, `lkb-pos`); `C` cells: `union-select` (caps and nocaps) and
`level-context`. Per-call cells on union-select's short subjects:
`union-srch` (control) and two movers (`mod-i`, `ci-ascii-control`). `norm()`
reads `(60|61)` and drops the `"none"` stamp line. TBD-ALPHA-MAC

## 9. Deviations from the design, and findings

1. **(d') declines the design's own S469 witness.** `(?:\Gab|x)(cat)dog` has
   `Vm.mrl_win` true (no atomic, no lookaround, exact), so the literal (d')
   conjunct declines it; S469's witness is `(?:\Gab|x)(cat)(?=dog)` (the
   lookahead erases the ceiling, K = 2, a `\G` hybrid that hands off), and
   the original is (d')'s control. (d') reads `mrl_win`, not "a clamp site
   exists" (`RX_VM_PRUNE_CEILING "prefilter-window"`): the conservative
   reading, population zero either way.
2. **S464's plant** models the contract violation at the handoff ("hand off
   the NEXT occurrence when there is one") rather than in the pair arm: the
   pair arm's text is shared with the prefilter's run-pinned blocks, where a
   later occurrence is already answer-visible today, so a pair-arm plant
   would not isolate the new obligation.
3. **The unanchored route hides a short K and a missing clamp** (§5.3): the
   reverse pass keeps `search_from` (Q6) and re-finds the true start.
4. **The round-up's bound is the predicate's own `>= n` clause**, not a
   second `< n` test: one spelling (DD-12 (7)); S472 strips that clause.
5. **The tail/join offset** is derived, not carried (§1).
6. **Q3 (a) costs every artifact 30 bytes**; the size-cap retry reasons
   quote it (§3's normalization).

## 10. Resume notes

TBD-RESUME
