# vlbbuild — [VLOOKBEHIND] stage 1 build (2026-11-06, lane vlbbuild, opus)

Design: `docs/design/vlookbehind.md` rev 4 (with erratum r3-1106 and this lane's
`[vlbbuild R2 erratum]`). Branch `lane/vlbbuild` over main `fb22c62a6`. Build go
covered STAGE 1 only: backreferences in a lookbehind (stage 2) and the reverse DFA
stay out. No `docs/dev/lanes/vlbbuild_deliver.txt` exists (the brief said so), so
there is no lanecheck DELIVER block to run against.

## STATE AT HANDOFF

- **Code and docs: COMPLETE and committed.** Last commit is this report's.
- **Rulings applied:** R1 (the 15 D27-owned rows) and R2 (gate 4 gives up with
  STEPS). R2 is the last entry in `vlbbuild_rulings.md`.
- **Validation run in the lane, all on the clean rebuild:**
  - `test-encoding-checks` GREEN;
  - `test-partlayout` GREEN;
  - `test-codegen` GREEN (this includes the SABANCHOR check over every new and
    re-anchored row);
  - `test-lookaround` GREEN (re-run after the oracle fix below);
  - `test-backrefs` GREEN (re-run after the oracle fix; log
    `$PCREC_TMPDIR/scratch/vlbbuild/chk2_test-backrefs.log`).
- **OWED:** nine box-queue jobs, `200-vlbbuild-*` .. `208-vlbbuild-*`, all queued
  detached. Logs and completion lines are in "OWED runs" below.

## Commits (in order)

| commit | unit | what |
|---|---|---|
| ea4fcbbac | U1-U5 | the exact width pair; the 255 cap and the 65535 ceiling (`limits.def`); the range candidate loop; the LO slot sub-block; `VSK_STEP_CHAR` / `VL_LB_COUNT`; the `$_fwd_step` seam entry |
| 6f6d27975 | U6 | gate 1: oracle modes (UTF-8 patterns, `MATCH_INVALID_UTF`, a compile context); `bref_oracle` MODE column; `run_lookaround_diff.sh` §5 |
| e013203ee | U6 | gate 3 (accept set and classification, §6) and gate 4 (the budget cell, §7) |
| 3b9754edf | U6 | `tests/codegen/enc_entry_list.c` (the seam reader); DD12a(i) region (1), twins, keys, rules (a) and (b) derived; DD12a(ii) names derived, plus the witness; K49 (b) boundary members read from the seam |
| 786312130 | K137 + abi | **K137 FIXED.** abi 95 -> 96. U6 fixtures (`residlbrange` plus its utf8 twin), guards, W-low's codegen detector |
| 142dcb4ff | U7 | the 17 non-D27 corpus flips; the reject row re-aimed; the call sweep's refusal regex; K37 bounds on two new sites |
| 7dc2c4183 | U7 (R1) | the 15 D27-owned flips; the generators moved in the same commit |
| b195cf80e | U7 | the NPO guard 69 -> 85; `tests/lookaround/CLAUDE.md` |
| cba188ead | U9 | spec hunks (`pattern_language.md`, `limits.md`, `match_api.md`); `limits_check` 78 -> 80; the comment readers for INTERNAL |
| 63250b5cb | R2 | the design erratum: §5.5's give-up is STEPS |
| b589d1710 | readers | `mrl.c` and `internal.h` width headers; `VMREC.md` body and plan refs; `arev.md`; `src/enc/CLAUDE.md`; **D189** |
| 7521c7163 | readers | the D27 extracts and `lookaround_design.md` §2.5 marked SUPERSEDED IN PART |
| 97eadaca4 | U8 | the witness corpus (W1-W16, W-low); NPO 85 -> 115; the `emit_vm` LO comment corrected. **Last src commit.** |
| 7c87559a6 | U8 | sabotage rows S1960-S1980; S133/S134/S170/S-U6 re-anchored; S136 and S-U4 re-aimed; S136's two witness cells; NPO 117 |
| b3c045e78 | FIXIND-6 | plan row `[ENC-SIDE-EMIT]` (Backlog, trigger: a second side emission) |
| 57bed924a | finding | `bref_oracle.py` byte mode passes the pattern's UTF-8 bytes (see Findings) |
| 713282fc1 | gate 2 | `run_recursion_identity.sh` self-pin: FILEPIN = ABASEPIN = 97eadaca4 |

## What was built, per unit

- **U1 (width rule, `mod_lookaround.c` `la_widths`).**
  - The per-branch `[lo, hi]` is stored in written order.
  - Branches are refused when unbounded (err 125 class), above the 65,535 ceiling,
    or above the 255 cap once any branch varies.
  - Both rows are in `limits.def`: `LA_LOOKBEHIND_BRANCH_MAX` and
    `LA_LOOKBEHIND_VAR_MAX`.
  - The verdict is an `LbVerdict` plus a figure. The parse hook and the deferred
    (call-bearing) re-check share it.
- **U2 (exact ends).** The `pcrec_cwmin`/`pcrec_cwmax` headers are rewritten as
  EXACT for the lookbehind consumer (`mrl.c`, `internal.h` call table).
- **U3-U5 (the emitter, `emit_vm.c` `vm_look_behind*`, `vm_stmt.c`).**
  - A one-length branch is unchanged.
  - A varying branch is the cursor-rung loop:
    - LO_i is written once per evaluation as a TRAILED slot (`RX_SLOT_LB_LO<j>`,
      sub-block sized by the count pass's `vm_lb_varies`);
    - the far count `K = min(hi - lo, LO)` is a local (`VL_LB_COUNT`);
    - the far step is the seam's `back_step` with a local count (the byloc
      operand), with retry-one-shorter on the sentinel;
    - candidates run farthest first;
    - each candidate steps one character with `$_fwd_step` bounded by the cursor
      in POS (`VSK_STEP_CHAR`);
    - the exhaustion test is `scan_position == LO_i`, then `L_n_i` restores the
      cursor.
  - On a varying branch the end-check DECLINES on both polarities; the INTERNAL
    return stays for one-length negative branches only.
  - The trail term is `2 + (varying branches)`.
  - The non-atomic `(?<*` keeps its candidate frames live.
- **U6 (checks).** The seam reader `tests/codegen/enc_entry_list.c`. DD12a(i)
  region (1), K49's boundary members and the fwd_step guard are derived from the
  seam. `residlbrange` fixtures (byte and utf8). W-low's codegen detector. Gates 1,
  3 and 4 live in `run_lookaround_diff.sh` §5-§7.
- **U7 (corpus).** 32 rows flip (24 distinct patterns); the full table is below.
  The reject row is re-aimed at the 255 cap reached through a call:
  `^(?:(?<g>a{1,300})){0}b(?<=(?&g))$`, err 200 at offset 23, which libpcre2 also
  gives. The call sweep's refusal regex is widened. The NPO guard went
  69 -> 85 -> 115 -> 117.
- **U8 (witnesses and sabotage).** The `lookbehind_variable_witness.rxt` corpus
  (libpcre2-generated from `lookbehind_variable_witness.gen.py`: 36 blocks, S136's
  two cells included, 4 of them `perr`). 21 new rows and 6 re-cut legacy rows (table
  below).
- **U9 (spec, D80).**
  - `pattern_language.md`:
    - §7.4¶5: the bounded rule, 65535/255, and the zero-width divergence;
    - new ¶5b: written order, farthest first, the non-atomic retry, with examples
      verified on libpcre2 and the harness;
    - §2.4: shapes 5 and 7;
    - §9¶2 trimmed, plus a new indented ¶2a for the accepted divergence;
    - §7.11¶3.
  - `limits.md`: new §3.1¶5 (the charge; the STEPS give-up class, R2) and new §3.11
    (the two rows); TOC regenerated.
  - `match_api.md`: §3¶2 (`<prefix>_fwd_step`) and §4¶6 (two INTERNAL producers).
  - Re-read with no change needed: `match_api.md` §9.4¶2 and ¶8.

## abi event (95 -> 96, D76/D94) and K137

K137 is **FIXED in 786312130**: the utf8 retry advance's prose is now a D112 doc
half (`advance_doc`) behind the comment gate, so `-e utf8 -fno-comments` no longer
emits it.

The abi readers were found by grep for the number:
- `emit_dfa.c`;
- `match_api.md` §1¶7, the §6 table and §6¶17;
- `ABI_EXPECT`;
- S693;
- `docs/dev/history/abi_changelog.md`.

`test-codegen` is green. Registry and rxtsource run inside the owed `make test`.

The (B) pin moves with the abi: see gate 2.

## Gates (design §6)

| gate | status |
|---|---|
| 1. 0 diffs vs libpcre2 (byte, utf8, utf8-invalid) | GREEN: §5 covers 661 patterns (byte=48,863, utf8=15,145, utf8-clip=2,064, utf8-invalid=252 cells), 0 disagreements. The 49 utf8-clip cells are D142's stated divergence. §1's `# pcre2-only` sweep: 117 blocks / 11,349 cells, 0 disagreements |
| 2. byte identity except the K137 flag pair | OWED: jobs id1, abisweep, id2 (below) |
| 3. accept set inside PCRE2's; width judgment exact | GREEN: 234 cells; 32 zero-width-repeat cells are the stated divergence; 2 backreference rows only libpcre2 accepts (stage 2); 154 shared accepts judged equal to libpcre2 at `max_varlookbehind = 0` |
| 4. budget cell | GREEN: the common path answers at 60,000 bytes. The worst case answers at 4,000 and gives up with STEPS at 20,000. The measured boundary is 7,890 bytes. Never FRAMES |
| sabotage RED planted / GREEN without | OWED: jobs mech1-3 |
| encoding checks | GREEN (`test-encoding-checks`) |
| 32 corpus rows flip with oracle-verified expectations | DONE (table below). The harness passes over all flipped files (697/697 at U7) |

### R2: when gate 4's give-up starts, and how it scales with the cap

For `(?<=a{1,K}b)` on an all-`a` subject, the cost is about K² steps per cursor
position. The first give-up length (PCREC_ERR_STEPS, default step budget) was
measured as:

| K | first give-up length (bytes) |
|---|---|
| 32 | 473,507 |
| 64 | 120,236 |
| 127 | 30,843 |
| 254 | 7,890 |

Each doubling of K divides the length by about 4. libpcre2 answers all of these.
The pinned margins (4,000 answers, 20,000 gives up) are unchanged. The spec states
this class in `limits.md` §3.1¶5.

## The flipped rows (R1: file:line in HEAD, libpcre2 10.46 answers)

The 15 D27-owned rows are refusals.rxt ×7, spellings.rxt ×7 and
sr_interactions.rxt ×1. Their expectations come from libpcre2 only; the
generators moved in 7dc2c4183.

| HEAD location (was) | pattern | answers |
|---|---|---|
| tests/lookaround/alpha_spellings.rxt:368 (was :369) | `(*plb:(a\|bc))x` | m "ax" 1 2; g 1 0 1; m "bcx" 2 3; g 1 0 2; n "cx" |
| tests/lookaround/d27/refusals.rxt:14 (was :13) | `(?<=(a\|bc))x` | n "x"; m "ax" 1 2; g 1 0 1; m "aax" 2 3; g 1 1 2; m "aaax" 3 4; g 1 2 3; m "bcx" 2 3; g 1 0 2; m "abcx" 3 4; g 1 1 3; n "adx"; n "bcdx"; n "cdx"; n "aabx"; n "abx"; n "zx" |
| tests/lookaround/d27/refusals.rxt:36 (was :18) | `(?<=a{2,3})x` | n "x"; n "ax"; m "aax" 2 3; m "aaax" 3 4; n on the other eight |
| tests/lookaround/d27/refusals.rxt:53 (was :23) | `(?<=a?)x` | m on all twelve subjects, at the x |
| tests/lookaround/d27/refusals.rxt:100 (was :58) | `(?<=(?:a\|bc)d)x` | m "adx" 2 3; m "bcdx" 3 4; n on the other ten |
| tests/lookaround/d27/refusals.rxt:117 (was :63) | `(?<=((a\|bc)d))x` | m "adx" 2 3; g 1 0 2; g 2 0 1; m "bcdx" 3 4; g 1 0 3; g 2 0 2; n on the rest |
| tests/lookaround/d27/refusals.rxt:138 (was :68) | `(?<=a{1,255})x` | m "ax" 1 2; m "aax" 2 3; m "aaax" 3 4; n on the rest |
| tests/lookaround/d27/refusals.rxt:170 (was :88) | `(?<=a{2}b{0,1})x` | m "aax" 2 3; m "aaax" 3 4; m "aabx" 3 4; n on the rest |
| tests/lookaround/d27/spellings.rxt:140 (was :139) | `(?<*(a\|ba))c` | n "ba"; n "xa" |
| tests/lookaround/d27/spellings.rxt:151 (was :148) | `(*naplb:(a\|ba))c` | n "ba"; n "xa" |
| tests/lookaround/d27/spellings.rxt:162 (was :157) | `(*non_atomic_positive_lookbehind:(a\|ba))c` | n "ba"; n "xa" |
| tests/lookaround/d27/spellings.rxt:218 (was :211) | `(?<=(a\|ba))c` | m "bac" 2 3; g 1 0 2; m "xac" 2 3; g 1 1 2; m "aac" 2 3; g 1 1 2 |
| tests/lookaround/d27/spellings.rxt:233 (was :220) | `(?<*(a\|ba))c` | same as above |
| tests/lookaround/d27/spellings.rxt:248 (was :229) | `(*naplb:(a\|ba))c` | same as above |
| tests/lookaround/d27/spellings.rxt:263 (was :238) | `(*plb:(a\|ba))c` | same as above |
| tests/lookaround/gated.rxt:105 (was :109) | `(?<=(a\|bc))x` | m "ax" 1 2; g 1 0 1; m "bcx" 2 3; g 1 0 2; n "cx" |
| tests/lookaround/lookbehind_group_alt.rxt:99 | `(?<=(?:a\|bc))x` | m "ax" 1 2; m "bcx" 2 3; n "cx"; n "x" |
| tests/lookaround/lookbehind_group_alt.rxt:108 (was :104) | `(?<=(?i:a\|bc))x` | m "Ax" 1 2; m "bCx" 2 3; n "cx" |
| tests/lookaround/lookbehind_group_alt.rxt:117 (was :110) | `(?<=(?:a\|bc)\|d)x` | m "ax" 1 2; m "bcx" 2 3; m "dx" 1 2; n "cx" |
| tests/lookaround/lookbehind_group_alt.rxt:126 (was :116) | `(?<!(?:a\|bc))x` | n "ax"; n "bcx"; m "cx" 1 2; m "x" 0 1 |
| tests/lookaround/lookbehind_variable.rxt:38 (was refused.rxt:104) | `(?<=(a\|bc))x` | m "ax" 1 2; g 1 0 1; m "bcx" 2 3; g 1 0 2; n "cx"; n "x"; m "abcx" 3 4; g 1 1 3; ms 1 "zbcx" 3 4; g 1 1 3 |
| tests/lookaround/lookbehind_variable.rxt:56 (was refused.rxt:115) | `(?<=a{2,3})x` | m "aax" 2 3; m "aaax" 3 4; n "ax"; m "baax" 3 4; m "aaaax" 4 5 |
| tests/lookaround/lookbehind_variable.rxt:70 (was refused.rxt:124) | `(?<=a?)x` | m "x" 0 1; m "ax" 1 2; m "bx" 1 2; ms 1 "aax" 2 3 |
| tests/lookaround/lookbehind_variable.rxt:81 (was refused.rxt:132) | `(?<=a{0,3})x` | m "x" 0 1; m "aaax" 3 4; ms 2 "aaaax" 4 5; m "bx" 1 2 |
| tests/lookaround/lookbehind_variable.rxt:94 (was refused.rxt:189) | `(?<=(?:a\|bc)d)x` | m "adx" 2 3; m "bcdx" 3 4; n "cdx"; n "dx" |
| tests/lookaround/lookbehind_variable.rxt:105 (was refused.rxt:197) | `(?<=((a\|bc)d))x` | m "adx" 2 3; g 1 0 2; g 2 0 1; m "bcdx" 3 4; g 1 0 3; g 2 0 2; n "cdx" |
| tests/lookaround/lookbehind_variable.rxt:121 (was refused.rxt:220) | `(?<!(a\|bc))x` | n "ax"; n "bcx"; m "cx" 1 2; g 1 -1 -1; m "x" 0 1; g 1 -1 -1; m "zzx" 2 3; g 1 -1 -1 |
| tests/lookaround/lookbehind_variable.rxt:137 (was refused.rxt:228) | `(?<*(a\|bc))x` | m "ax" 1 2; g 1 0 1; m "bcx" 2 3; g 1 0 2; n "cx" |
| tests/lookaround/lookbehind_variable.rxt:152 (was refused.rxt:284) | `(?<=\n?\z)x` | n "x"; n "\nx"; n "a" |
| tests/lookaround/lookbehind_variable.rxt:163 (was refused.rxt:294) | `(?<=\w?)x` | m "x" 0 1; m "ax" 1 2; m "-x" 1 2; ms 1 "aax" 2 3 |
| tests/recursion/d27/sr_interactions.rxt:244 (was :245) | `^(?(DEFINE)(?<g>a\|ab))ab(?<=(?&g))$` | m "ab" 0 2; g 1 -1 -1; n "b"; n "aab" |
| tests/recursion/inlookaround.rxt:119 (was :121) | `^(?:(?<g>a\|ab)){0}ab(?<=(?&g))$` | m "ab" 0 2; n "b"; n "a" |

Outside the corpus, three things moved:
- **The reject row.** It is re-aimed rather than flipped (U7 above).
- **`gated.rxt`'s new capability cell.** `(a)(?<=\1)x` is a `perr` on module
  `backrefs`; libpcre2 accepts it, and it is stage 2.
- **Generator moves.** `sr_check.py`'s `PCREC_ONLY_PERR` is emptied, and the
  `sr_gen.py` spec is moved. `checker.py`: 342 ok, plus 2 "no features line"
  failures that predate this lane (a control on the base shows them).

## Sabotage rows (ids S1960-S1989; S1981-S1989 unused)

The plant verdicts are OWED from jobs mech1-3. Predictions are in each row's
`SAB_DOC_FIGURE`. Every row passed `VALIDATE_ONLY`, and the anchors pass codegen's
SABANCHOR check.

| row | design witness | plant | predicted detector |
|---|---|---|---|
| S1960 | W1 | far count 0 (nearest candidate only) | W1's group span |
| S1961 | W2 | the range end-check never fires | W2, W3 |
| S1962 | W4 | INTERNAL on a varying negative branch | W4 (PCREC_ERR_INTERNAL) |
| S1963 | W5 | every lookaround cuts (the `(?<*` retry lost) | W5, W16 |
| S1964 | S134 twin (READY-1) | the far sentinel test always passes | W6 utf8 |
| S1965 | W6 (a) | a far sentinel ends the branch | W6 utf8 |
| S1966 | W6 (b), W15 | a far sentinel jumps to the try at LO | W6, W15 utf8 |
| S1967 | W8 | the cap applies only to varying branches | W8 (`perr`), gate 3 |
| S1968 | W9 | the cap admits 256 | W9 |
| S1969 | W9b | the ceiling admits 65,536 | W9b |
| S1970 | W11 (a) | exhaustion skips the restore | W11 (a) |
| S1971 | W11 (b) | LO's sentinel skips `L_n_i` | W11 (b) utf8 |
| S1972 | W12 (b) | the trail term loses `+ varying` | W12 (b) (FRAMES) |
| S1973 | W13 | the step is bounded by `subject_length` | W13 utf8 |
| S1974 | W14 | the byte `fwd_step` moves 2 | W14, W16 |
| S1975 | W16 | the exhaustion test fires one early | W16, W3b |
| S1976 | W-low (FIXIND-5) | LO is written untrailed | codegen W-low detector; harness W-low |
| S1977 | fwd_step (i) | the step is inlined (`+= 1`) | codegen fwd_step per-site count |
| S1978 | fwd_step (ii) | the utf8 `fwd_step` steps one byte | K49 boundary tie (encoding checks) |
| S1979 | S133 twin (READY-1) | the far back_step is inlined | codegen back_step per-site count |
| S1980 | W12 (a) | LO is written per candidate (a second write at `L_try_i`) | W12 (a); depends on K134's compaction trigger, as noted in the row |

Legacy rows re-cut:
- **S133 and S134 (READY-1)** are re-anchored on the shared builder line and the
  `k_none` sentinel branch.
- **S170** is re-anchored on the `LbVerdict` call.
- **S-U6** is re-anchored with its signature, because the utf8 `fwd_step` has the
  same body (READY-10).
- **S136** is re-aimed. Every one-length pair is stored one too wide at both ends
  (r3 F9 / r6 V8). Its two new witness cells are `(?<=bc|d)x` on `abcx` and
  `(?<!bc|d)x` on `bcax`.
- **S-U4** is re-aimed at gate 3's classification control. Its old detector (a
  class-bearing lookbehind refuses) is gone by construction.
- **S172** is unchanged: its two moving rows are unbounded and still refused.

NOT PLANTED. Their witnesses are in the corpus; no clean one-edit plant exists:
- **W3 / W3b** (no backtracking into the body at the end-check). The cut is the
  body's frame structure, not one emitter line. A plant means possessifying or
  atomic-wrapping the body across several sites.
- **W10** (branch order lost). The order is the walk that builds the branch
  table. Reversing it touches the branch split and every label that
  `vm_look_behind` derives from it.

## OWED runs (box queue, detached, owner `vlbbuild`)

All jobs live under `$PCREC_TMPDIR/scratch/vlbbuild/` (`jobs/` holds the scripts).
Read each verdict with `scripts/boxqueue state vlbbuild-<name>`.

| job | what | log / completion line |
|---|---|---|
| 200 id1 | gate 2 RUN 1: subject built from 3b9754edf (abi 95, pre-K137) vs the pre-landing pins f5de088bf / 4bd002e20 | `id1.log`, judged into `id1_judge.out`. Completion line: `id1: VERDICT GREEN` |
| 201 abisweep | every distinct corpus pattern, 3b9754edf vs HEAD, byte/utf8 × comments on/off, abi digits masked | `abisweep.tsv`; `abisweep: patterns=N unexpected=0` |
| 202 id2 | gate 2 RUN 2: HEAD vs the self-pin 97eadaca4 | the job log; the script's own ok lines |
| 203 maketest | `make strict` + `make test` | `maketest.log`; no `*** [...test-` line |
| 204-206 mech1-3 | the 30 rows above plus S135/S169/S693, real plants | `mech/{1,2,3}/mech.log`; `== mech run COMPLETE: 10 rows (unexpected: 0, ...` |
| 207 reach | `REACH_ONLY=1` over the whole matrix (the delivery bar for a widened admission) | `mech/reach/reach.log`; `mech-reach-only: DONE rc=0` |
| 208 axes | `make test-axes` | `axes.log` |

Predictions:
- **id1.** (B) and (A) both show `differing=0` on every axis. Every refusal
  mismatch is subject=compiled reference=refused, on a pattern libpcre2 accepts at
  `max_varlookbehind` 255 and refuses at 0. The set is the manifest's call-free
  patterns (`vlbinv_evidence/population.tsv`; 22 distinct expected) plus this
  lane's added witness patterns. The judge prints both list differences for the
  reader. The identity script's own rc is RED by construction, so it is not the
  verdict.
- **abisweep.** Differences appear only under utf8 `-fno-comments` (K137). The
  identity gate is byte-only and runs with `-fcomments`, so it cannot see K137;
  this sweep is the check.

Two gaps remain:
- **The identity run is byte-only.** Gate 2's G2 claim for utf8 artifacts is
  covered by the abisweep's utf8 classes. That sweep is pcrec vs pcrec, so a byte
  move it does not predict is the signal.
- **The STOP RULE stays live.** An unpredicted identity mover in id1 or abisweep
  is the STOP case. A fresh agent reads the judge output before landing.

## Findings

1. **`bref_oracle.py`'s byte mode handed libpcre2 a latin-1 `str` (fixed in
   57bed924a).**
   - pcre2_ctypes encodes a non-UTF `str` as latin-1, so `é` was one byte for
     libpcre2 and two for pcrec.
   - The first non-ASCII `# pcre2-only` blocks (the witness file's utf8 cells,
     swept byte-mode by §1) disagreed: `(?<=(é{0,2}))x`, 9 cells, and
     `(?<=(é{0,2}))b`, 41 cells.
   - After the fix, §1 shows 117 blocks / 11,349 cells with 0 disagreements.
   - Other users: backrefs, dupnames, expansion and recursion diffs. Only
     non-ASCII byte-mode patterns move, and those were previously mis-posed.
     `test-backrefs` was re-run GREEN; the rest ride the owed `make test`.
2. **The Makefile has no header-dependency tracking.**
   - After the `enc.h` struct change, the stale `nfa.o` read garbage `start_cls`,
     and every utf8 compile failed with `[K50-NULLGATE]` (18 codegen FAILs).
   - `make clean` cured it.
   - Any lane that changes a struct in a header must `make clean`. Not filed as a
     row (D2's plain make); the manager decides.
3. **The spec-history checker only recognises paragraph labels at column 0.** An
   indented `- <a id>` sub-bullet (`§9¶2a`) is not citable, so D189 cites §9.
4. **D189 numbering.** main already has D188. D189 was free at the base; renumber
   at landing if taken.
5. **`src/gen/CLAUDE.md` is NOT edited.** It is at 12,284 of 12,288 bytes, and no
   file changed role.
6. **`docs/testing.md` has no edit.** No passage there describes DD12a(i), K49 or
   gate 1's harness (grep), so it has no reader to update.
7. **`docs/pcre2_compliance.md` is OWED after landing**, via the
   `compliance-refresh` skill: variable lookbehind moves from refused to compiled.
8. **FIXIND-6.** The shared predicate is in; the general hook is filed as
   `[ENC-SIDE-EMIT]` (trigger: a second side emission).

## For the manager at landing

- Re-pin FILEPIN and ABASEPIN to the merge commit (the self-pin convention).
- Check D189's number.
- Run the compliance refresh.
- The tree's `docs/dev/artifact_size_log.tsv` is written by `make test`, as always.

## 2026-11-06 lane vlbfix: code review r4 fixes

The fixes ruled in `docs/dev/reviews/2026-11-06-r4-vlookbehind-code.md`, on this
branch, base 48606e036. Rulings file re-read at every finding boundary (last
entry R3). Sabotage ids S1981-S1989 (the unused top of S1960-S1989).
No answer moved and no artifact byte moved: abi stays 96, nothing in emitted
scaffolding changed (F15's guard is compile-time only: 138 compiles, the 69
corpus lookbehind patterns x byte/utf8, byte-identical to the base).

### Per finding

- **F1** (5bdc95759, 937bed801). `pcrec_cwmax_static` (mrl.c) counts each
  match-time length as one character. A branch unbounded under
  `pcrec_cwmax` but bounded under it is `LBW_NOTBUILT`, the shape-5 refusal
  "a lookbehind containing a backreference, a variable or a consuming
  callout is not implemented (its length is known only when matching)". It
  is reported after the 255 cap, so `(a)(?<=\1|a{300}|b?)x` still gets
  libpcre2's err 200 sentence. Reject rows (gated 112 -> 117):
  `(a)(?<=\1)x` at offset 3, `(?<=${x})a` at offset 0, and
  `(?<=a(?C"c,consume"))x` at offset 0 (libpcre2 accepts the first and the
  third). The controls `(a)(?<=a+|\1)x` and `(?<=(a)\1{2,})x` keep err 125's
  "(this one is unbounded)", as libpcre2 does. test-reject: 667 pass / 0 fail.
  Spec: pattern_language.md §7.4¶5 and §9¶2, and the refusal table in
  vars.md §6. Premise reproduced first: "unbounded" for `(a)(?<=\1)x`.
  Sabotage S1981 plants the old rule (the not-built test always true).
- **F3** (5ba90d36a). `run_lookbehind_call_sweep.py` counts PCREC-REFUSES (an
  over-refusal) as a failure; `PCREC=` overrides the compiler. Queue job
  210-vlbfix-lbsweep was GREEN. At HEAD: "lbsweep: OK (0 disqualifying
  findings)". The control used a copy of main's pre-stage-1 compiler: "FAILED
  (220 disqualifying findings)", 40 of them over-refusal lines. The
  compliance page was refreshed per the compliance-refresh skill: the
  `(?<=...)` annotation record, the survey row and the intro prose, and every
  compliance check passes. The "compliance refresh OWED after landing" item
  above is now DONE on this branch.
- **F6-F9** (98be8bb01). Each row now fails for the right reason, measured
  with tools/review/plant.sh plus the harness:
  - S1963 (two sites: the atomic flag and the cut emission): 47 pass / 7 fail.
  - S1964 re-aimed to the far retry's `- 1`: 51 pass / 3 fail. The old
    sentinel plant is visible only under a sanitizer, a stated residual.
  - S133: site 1 widened to the whole one-length back-step, site 2 keyed on
    `vm_lb_nvaries`. 0 gcc failures (it had 40, scored ANOMALY); 5 utf8
    witness cells move.
  - S1980: 36 pass / 18 fail, every one GAVE UP (frames).
- **F10** (b7d71b08c, c7eaaa779). All three plants sit at the parse hook,
  where the count pass and the emitter read one AST, so there is no slot
  drift. vlbbuild had found no one-edit emitter plant.
  - S1985 makes a one-branch body atomic: 49 pass / 5 fail (W3, W3b, W1).
  - S1986 possessifies a branch's tail quantifier: 53 pass / 1 fail (W3b
    alone, [1-2] -> [2-3], the design's predicted sabotage).
  - S1987 swaps a two-branch body so the longer branch runs first: 52 pass /
    2 fail (W10).
  - S1975's figure claimed W3b. The r4 checks lens measured that cell green,
    so the figure is corrected and points to S1986.
- **F11** (e8cc59b33). run_lookaround_diff.sh §5 floors moved from
  30000/9000/2000/150/1 to 48374/14993/2043/249/48. That is vlbbuild's
  measured 48,863/15,145/2,064/252/49 less 1%; the comment says why. Confirmed
  by the owed make test (test-lookaround).
- **F15** (481b0d73b). `vm_take_lblow` refuses at compile when the low
  sub-block would overflow, by branch index or slot range. After emission
  `nlblow == nlblow_total` is checked, the nsplice sibling's shape. Premise
  reproduced with the review's plant PA: it compiled silently and
  `(?<=a{1,2})x` on "abxa" SIGSEGVed. Sabotage S1982 (slot formula +1),
  S1983 (count pass short) and S1984 (count pass long): under each, the
  varying cells refuse at compile with the internal error. No plant hangs.
- **F16** (72d39992c). DD12a(i)'s SYM2KEY, SIG_RE and TWINNED are keyed by
  backend, so a symbol is excised only from an artifact whose own backend
  lists it. S1989 unlists byte's side-table symbol (enc.c's
  `enc_row_side_table` arm). At the default slice it gives 13 pass / 2 fail:
  "4 of 241 strict-identity pairs differ OUTSIDE the named encoding-owned
  regions" and the K50 exception-list mismatch. The review measured the
  same plant (PB) GREEN before the fix.
- **F17** (72d39992c). `(?<=a{1,2}|b)x` and `(?<!a{1,2}|b)x` join the
  explicit witnesses. S1988 splices a utf8-only work charge into `L_n_i`.
  It gives 13 pass / 1 fail: "2 pair(s) entered the gate-refinement class
  WITHOUT a manifest row". The review measured the same plant (PC) GREEN
  before. The red comes through the K50 no-unlisted-members guard, not the
  strict bar, because the splice moves RX_VM_PROGRAM_BYTES, a FORM stamp.
  That is the review's pre-existing VM_PROGRAM_BYTES note; it is not fixed
  here and not filed (manager's call). The clean run at the default slice:
  14 pass / 0 fail, all 15 seam rows reached.
- **plant.sh** (f5fc48880). The r4 round's plant helper is committed as
  `tools/review/plant.sh ROW OUTDIR [REV]`, with a line in
  tools/review/CLAUDE.md. It derives the tree from its own location, applies
  the row with the matrix's replace.py, rebuilds only the planted object and
  refuses /tmp.

### PLAN, for the manager (nothing filed)

- SEAM-5 (F19): the boundary rule is spelled four times per backend
  (next_pos, advance, start_guard, fwd_step). General form: one boundary
  datum per backend, rendered by the seam. Trigger: a third encoding or a
  fifth spelling.
- SEAM-6 (F20): stands-for and the side table are code in enc.c, not row
  fields; fold into [ENC-SIDE-EMIT].
- SEAM-7 (F21): symbol facts are parsed from C text, with silent 63-char
  truncation and no #define symbols.
- Also unfiled: F4a and F18 stay PLAN per the ruling. The VM_PROGRAM_BYTES
  form stamp lets a hot-path splice read as a declared form move (see F17).

### Residuals

- A backreference reached through a CALL
  (`^(?:(?<g>(b)\2)){0}(?<=(?&g))x`, which libpcre2 accepts) still reads
  "unbounded": the static walk does not follow calls. Rule 0's comment in
  mod_lookaround.c says so.
- `(a+)(?<=\1)x` gets not-built; libpcre2 gives err 125. A capability
  refusal for a construct libpcre2 refuses anyway is the right tier under D26.
- S1964's original mechanism (the sentinel taken as a candidate) shows only
  under a sanitizer.

### OWED runs (box queue, detached, owner `vlbfix`)

Scripts are in `$PCREC_TMPDIR/scratch/vlbfix/jobs/`; S below is
`/var/tmp/pcrec-pcrec/scratch/vlbfix`. Each job's own log is
`worktrees/.boxqueue/{done,failed}/*-KEY/job.log`.

| job | log | completion line / predicted |
|---|---|---|
| 210-vlbfix-lbsweep | S/lbsweep_{head,base}.log | DONE GREEN: `lbsweep: VERDICT GREEN` |
| 200-vlbbuild-id1 (vlbbuild's, kept) | /var/tmp/pcrec-pcrec/scratch/vlbbuild/id1_judge.out | `id1: VERDICT GREEN` |
| 211-vlbfix-abisweep (waits for 200's old3b build) | S/abisweep.tsv + job.log | rc 0: movers only under utf8 -fno-comments (K137) |
| 212-vlbfix-maketest (make, make strict, make test via perfrun) | S/strict.log, S/maketest.log (+ .perfrun) | no `*** [...test-X] Error` line; `scripts/verdict S/maketest.log` |
| 213-216-vlbfix-mech1..4 (S1960-S1989; S133 S134 S135 S136 S169 S170 S693 S-U4 S-U6) | S/mech/{1,2,3,4}/mech.log | `== mech run COMPLETE: N rows (unexpected: 0, ... anomalies: 0` |
| 217-vlbfix-reach | S/mech/reach/reach.log | `mech-reach-only: DONE` |
| 218-vlbfix-axes | S/axes.log | no `*** [...test-X] Error` line |

At queue time 212 had started at 10:51 on the tree as of 937bed801. That is
the code HEAD; only this report followed it.

## 2026-11-06 lane mttri: triage of vlbfix's red make test

Subject: vlbfix's job 212 make test at e9ede562a
(`/var/tmp/pcrec-pcrec/scratch/vlbfix/maketest.log`, perfrun `class=RED-REAL
contaminated=YES`; the contamination was the box at load1 29 with another
tree running). Branch HEAD at start d7aaa3bc1. Rulings file re-read; last
entry R4, nothing in it touches these sections. PREMISE TEST: the log's five
red sections were test-registry, test-vars, test-rxtsource, test-memfn-arch,
test-startset. Each was re-run SOLO (`nice make -C <worktree> test-X`, one at
a time). All five reds were real and owned by the branch; none was
contamination, and none was pre-existing on main (main has moved no .rxt file,
no rxtsource/registry script and no manifest since the merge base
fb22c62a6). No answer regression vs libpcre2 and no check weakened.

### Per section

- **test-vars**: solo RED, now GREEN at dc9283a80. Fixed in d378202ac.
  - Real regression in the test harness. vlbbuild U6 (6f6d27975) changed
    the shared binding `docs/design/eng_brep_measurements/probes/pcre2_ctypes.py`
    so a `str` is encoded UTF-8 whenever `PCRE2_UTF` is set.
  - `tests/vars/verify_vars.py` already passed `PCRE2_UTF` with latin-1
    byte-strings. Its three non-ASCII caseless subjects
    (`tests/vars/caseless.rxt` lines 76/86/96: the Kelvin sign and sharp s)
    were double-encoded, so libpcre2 answered nomatch (69 agree, 3 disagree).
  - Fix: restore the binding's contract, a `str` is always latin-1 (one
    character per byte), and a caller wanting UTF-8 hands bytes. Every UTF
    caller the branch added (bref_oracle.py, vlb_accept.py) and
    utfcheck_arm.py already pass bytes. U6's other additions stay:
    `PCRE2_MATCH_INVALID_UTF`, the `max_varlookbehind` compile context and
    `Pcre2Error.code`.
  - Solo: `verify_vars.py` 72 agree / 0 disagree; `make test-vars` green.
- **test-registry**: solo RED, now GREEN at dc9283a80. Fixed in 4f1667414.
  - Stale pin the stage legitimately moves. U1 added the limits.def rows
    LA_LOOKBEHIND_BRANCH_MAX and LA_LOOKBEHIND_VAR_MAX, each with a
    limits.md §3.11 anchor, so `limits_check.sh` gains two `[doc]` PASS
    lines (41 PASS, 0 failed, read from a run).
  - cba188ead moved that script's own manifest (78 -> 80). The second
    reader of the same fact, run_registry_tests.sh's coverage guard, stayed
    at 39.
  - Re-pinned 39 -> 41, with the cause in the guard's history comment.
    `make test-registry` green.
- **test-rxtsource**: solo RED, now GREEN at d7125694f. Fixed in d7125694f.
  - Stale pins. The stage added two .rxt files and edited eight more, and
    no lane moved the census. Measured per changed file, base vs HEAD,
    with the check's own awk and `verify_rxt.py`, not re-derived from the
    corpus. Census and RUNSH both move 312/6304/75730 -> 314/6341/75962:
    - lookbehind_variable.rxt: +1 file, 10 blocks, 54 lines.
    - lookbehind_variable_witness.rxt: +1 file, 36 blocks, 54 lines.
    - refused.rxt: -10 blocks, -10 lines.
    - gated.rxt: +1 block, +5 lines.
    - Lines only: d27/refusals +86, d27/spellings +23,
      lookbehind_group_alt +11, alpha_spellings +4,
      recursion/d27/sr_interactions +3, recursion/inlookaround +2.
  - C3 moves:
    - PASS -25 (22650 -> 22625). These are perr refusal lines python could
      check, for shapes stage 1 now ACCEPTS: refused -10, d27/refusals -7,
      lookbehind_group_alt -4, and one each in alpha_spellings, gated,
      sr_interactions and inlookaround.
    - SKIP +257 = pcre2-only +250 (python `re` has no variable-width
      lookbehind) + no-python-expression +7 (the recursion files).
    - Verifiable -18.
  - `make test-rxtsource` 300 passed / 0 failed.
- **test-memfn-arch**: solo GREEN at d7aaa3bc1. Already fixed by reachtri's C4
  allowlist rows (docs/dev/lanes/reachtri_report.md); nothing changed here.
- **test-startset**: solo RED, now GREEN at dc9283a80. Fixed in dc9283a80.
  - Stale manifests. `manifest_s2_vm_{auto,forced}.tsv` key rows by
    file:line, and the stage's .rxt edits moved them.
  - Every off-diagonal row was listed IN FULL (vmhat_checks.py's own
    `one()`/`corpus_blocks` in a scratch driver; the check prints six) and
    classified against the base text.
  - auto +3/-1:
    - 2 new-file blocks.
    - 1 line shift, sr_interactions :361 -> :363.
  - forced +74/-25:
    - 24 line shifts, same text and options.
    - +33 blocks of the two new files.
    - +17 blocks that were `perr` at the base and that stage 1 now accepts.
    - -1: lookbehind_widths.rxt:91 `(?<=(a)|(aa))c` yields its id to its
      dedup twin lookbehind_variable_witness.rxt:114, which sorts first (the
      ssbuild3 precedent).
  - No other row in an unchanged file moved; the bench rows are untouched.
    Rows follow the upropb2 precedent: the hat's own mover rule. A fresh
    `census_s1.py` would not reproduce today's manifests byte for byte
    (s3fix600 and others pinned measured rows), so it was not the control.
  - `make test-startset` green: vm-movers 491/3808, 0 off-diagonal.

### OWED runs (box queue, owner `mttri`, detached; scripts in /var/tmp/pcrec-pcrec/scratch/mttri/jobs/)

All at the branch HEAD current when each job starts (dc9283a80 or this
report's commit, which adds no code). Read verdicts with `scripts/verdict`
on each job's `done/*/job.log`.

| job | what | log | completion line |
|---|---|---|---|
| 220-mttri-maketest | make, make strict, make test via perfrun | scratch/mttri/strict.log, scratch/mttri/maketest.log (+ .perfrun) | perfrun `DONE rc=0`; no `*** [...test-` line |
| 221-mttri-abisweep | vlbfix's abi sweep (3b9754edf abi 95 vs HEAD) | scratch/mttri/abisweep.tsv; job.log | **DONE, GREEN**: patterns=5048, only utf8 -fno-comments differs (2244, K137), unexpected=0 |
| 222..225-mttri-mech1..4 | vlbfix's rows: S1960-S1989, S133 S134 S135 S136 S169 S170 S693 S-U4 S-U6 | scratch/mttri/mech/{1,2,3,4}/mech.log | `== mech run COMPLETE: N rows (unexpected: 0, ... anomalies: 0` |
| 226-mttri-reach6 | REACH_ONLY S518-S523 (reachtri's owed check) | scratch/mttri/mech/reach6/reach.log | `mech-reach-only: DONE rc=0 rows=6 reached=6 unreached=0` |
| 227-mttri-reach | REACH_ONLY, the whole matrix | scratch/mttri/mech/reach/reach.log | `mech-reach-only: DONE rc=0` (vlbfix's run read unreached=6, the six above) |
| 228-mttri-axes | make test-axes | scratch/mttri/axes.log | no `*** [...test-` line |

### Commits

d378202ac (pcre2_ctypes str = latin-1), 4f1667414 (registry 39 -> 41),
d7125694f (rxtsource pins), dc9283a80 (start-set manifests), then this report.

### For the manager

- The binding fix restores a shared contract that 30+ probe and test callers
  rely on. If a later stage wants a UTF-8 `str` convenience, it should be an
  explicit parameter, not keyed on the option bit.
- History index lines for reachtri and mttri are placed in
  docs/dev/history/claude_md/docs__dev__lanes.md.
