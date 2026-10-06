# Lane artcollect -- report (2026-10-06, sonnet, branch `lane/artcollect`)

[ARTREV] pilot: collect the four blind reviews, harden the identity, re-verify every sealed twin, prepare
the confirmer. Nothing was run on ubuntubudu. No `make test` / heavy suite was run (only the harness's own
self-test, `studies/artrev/selftest.sh`, a few minutes of light compiles plus its timing sections).

## 1. Collected (task 1)

`docs/dev/optloop/artrev/{A01,A07a,A07b,A09}/` (verbatim from rvA01-cell, rvA07a-cell's `A07/`, rvA07b-cell's
`A07/`, rvA09-cell; A09's `tools/`, `controls/`, `edge_subjects/` included; edge subjects A01 96 KB + A09
1.2 MB, committed), the four notebook entries under `notebook/`, and `pilot_index.md` (leads table per artifact:
id, class, origin, idea, expected effect, scratch verdict; the counted A07 overlap table). Also `pilot_pins.tsv`
(pattern, flags, prefix and artifact sha256 of each pilot artifact) so the confirmer can verify a regeneration.
Overlap, counted: of a's 6 leads, 3 matched fully, 2 partially, 1 unique; of b's 6, 3 full, 3 partial, 0 unique;
7 distinct ideas in the union; only b ever timed (run 001: L1 -20%, L2 -45%, L3 -53%, L4 -72% scratch, Mac).

## 2. Harness hardening (task 2) -- `studies/artrev/`

**A finding first, bigger than the brief's:** `arm_compile_cmd` never passed `-DARTREV_HAVE_IN=1`, so the shim
exported stubs and the identity driver NEVER drove an `_in` shape (SI/MI/CI/FSI) in ANY pilot identity run, while
the summary line claimed them ("shapes: ... SI MI CI"). Fixed in `common.py` (the compile line now carries it
whenever the artifact has `_in` entries, as `gen` already recorded in GENERATION.txt); the summary now prints how
many `_in` search lines were really driven (e.g. 14,912 on A07). All the pilot's "identity PASS" rows before this
fix therefore never exercised the `_in` entries; section 3 re-verifies with it on.

Hardened `identity` (all default; the confirmer's gate):
- **Shrunken resources.** Both arms rebuilt with RX_STEP_BUDGET/RX_WORK_BUDGET shrunk (default pairs 8:64,
  64:1024, 2000:40000; `--shrunk-budgets`) and every `_in` shape driven with {0,1} frames x {0,1} trail
  (`driver_id.c ... shrunk`, `art_set_bufs` in the shim). Compared under THE GIVE-UP RULE (`identity.giveup_compare`,
  keyed by (shape, subject, from) because a twin that answers can walk a find-all further): original gives up and the
  twin answers = a REPAIR, checked against libpcre2 (new anchored mode `a` in `pcre2_ref.c` for the M/C shapes),
  counted and printed; a repair that disagrees = FAIL; twin gives up where the original answers, answers differ,
  N/V differ, lines missing = FAIL. A different give-up code on both sides is accepted. If libpcre2 is absent and
  repairs exist, FAIL (unverifiable). `--strict-giveup` additionally fails every repair.
- **Window start.** For an artifact with an internal `<p>_prefilter` (the hybrids; auto-detected), the window the
  prefilter proposes at every search_from (every from up to 3000 bytes, ~1500 spaced above; `driver_pf.c`) must be
  identical orig vs twin; n/a otherwise (printed).
- **Livelock bound.** The twin's driver runs under max(30 s, 25 x the original's wall) (`ARTREV_LIVELOCK_FLOOR`),
  failing with "LIVELOCK suspected" instead of the 900 s timeout.
- `--skip-shrunk` / `--skip-window` log PASS-PARTIAL; `time` refuses it (it wants PASS).

Also added (task 4's missing pieces, see section 4): the LAYOUT control (`time --pads/--pad-arms`), `--cell`
(the CELL row), `variants` (dense/sparse subjects), `confirm_prep.sh`, `reverify.sh`; and one bug fix in
`run_remote` (the bundle was built from the raw `--arms` string, not the computed list with `orig`/`orig2`/pad
arms, so a remote run omitting `orig2` from `--arms` would have failed on the box).

**Self-test additions (failing direction first)** -- sections 8-11 of `selftest.sh`; results in section 6 below.
Synthetic twins (`selftest_twins.py`): `giveup_wrong` (fabricated match in place of a give-up) must FAIL;
`giveup_right` (retries with the full buffers = a correct frame-dropping-style repair) must PASS with repairs
counted AND oracle-checked; `giveup_lost` (gives up where the original answers) must FAIL; `start_early` (window
start one early, answers identical) must FAIL by the window differential ALONE (the test asserts answer identity
did not see it); `start_early_loop` likewise; `hang` must FAIL FAST by the livelock bound; PASS-PARTIAL must be
refused by `time`; unit cases for `giveup_compare` and for the layout verdict (clean WIN, layout-swing NOISE,
one-pad-flip NOISE, clean LOSS). Real twins on a PINNED A09 fixture (`fixtures/a09_pin57db5152/`):
**rvA09's L4 r2 is NOT a FAIL under the give-up rule as the charter amendment states it** -- see section 5, the one
point where the brief's expectation and the rule disagree. It PASSES by default with 5,562 repairs, every one
equal to libpcre2's answer, and FAILS under `--strict-giveup`; L4 r3 is exact under `--strict-giveup`; `ctlL4e`
(start one early, the livelock) FAILS fast.

## 3. Re-verification of every sealed counted twin (task 3)

Hardened identity, plain and `--san`, on each cell's subjects (A01/A09: 12 throughput + 112 search + the cell's
edge subjects; A07: t-64k/256k/1m), battery 3000, block 16, libpcre2 10.48 sample. Pinned artifact regenerated
byte-identically in every case (sha256 equal to the cell's). Logs: `build-artrev/rv_<A>/logs/` (scratch, not
committed); `studies/artrev/reverify.sh` reproduces the table. "repairs" = answers where the ORIGINAL gives up
(shrunk budgets / 0-1 frames-trail), each checked equal to libpcre2.

| artifact | twin | plain | san | give-up repairs (checked vs libpcre2) | window start |
|---|---|---|---|---|---|
| A01 | L1 | PASS | PASS | 0 | n/a (DFA, no prefilter) |
| A01 | L2, L3, L4 | PASS | PASS | 0 | n/a |
| A07a | L1 | PASS | PASS | 0 | n/a |
| A07a | L2 | PASS | PASS | 5,380 | n/a |
| A07a | L3, L4, L5 | PASS | PASS | 294,884 (every give-up of the original: the frameless/stepless twins never give up) | n/a |
| A07a | L6 | PASS | PASS | 0 | n/a |
| A07b | L1 | PASS | PASS | 0 | n/a |
| A07b | L2 | PASS | PASS | 5,380 | n/a |
| A07b | L3, L4 (r2), L5, L6 | PASS | PASS | 294,884 | n/a |
| A09 | L1 r1, L1 r2 (final), L2, L3 | PASS | PASS | 0 | 342,690 windows, 0 differences |
| A09 | L4 r1, L4 r3 (final), L5, L6 | PASS | PASS | 0 | 342,690, 0 |
| A09 | L4 r2 (superseded) | PASS | PASS | 5,562 (all equal to libpcre2); FAILS `--strict-giveup` | 342,690, 0 |

Every counted final twin PASSES; no twin was fixed. Controls (uncounted, expected to fail) behave as their authors
said: A01 ctlat/ctldollar/ctlfrom FAIL (plain and san); A07a ctlskip FAIL, ctlclamp PASS plain / FAIL --san;
A09 ctlnb, ctlnof, ctlnb2, ctlL3, ctlL4, ctlgap FAIL, ctlbnd PASS plain / FAIL --san, ctlL4e FAIL (now by the livelock
bound within about 30 s, previously by the 900 s identity timeout). The A07 twins reading "294,884 repairs" are the
case the lead named: frame/step-dropping twins that answer correctly where the original gives up; PASS under the rule,
FAIL under `--strict-giveup`; the confirmer should print the count and say "changes the limits behaviour".

## 4. Confirmer prep (task 4) -- `docs/dev/optloop/artrev/confirm_plan.md`

The exact command block for S4: pre-gates (bench slot, one read-only ssh probe), `confirm_prep.sh` (regenerates the
three artifacts from main's build/pcrec at abi 62 -- verified byte-identical to the pin for all three, 22 final twins
import cleanly), hardened identity per arm, dense/sparse variants, a TWO-pass timing scheme per artifact via
`time --remote ubuntubudu` (pass 1 plain to find candidates, pass 2 with `--pads 16,32,48,64,80,96,112 --pad-arms
orig,<candidates>` and `--cell`), >=11 interleaved rounds, load gate 0.5, `gnutimeout`+watchdog inside the remote
wrapper, expected wall about 1 h 15 min of box time in all, and the WIN/LOSS/NOISE rule on the CELL row of pass 2.

What the harness LACKED and this lane added (each with self-test cases): the pad-shift control (arms `X@pK` = the arm's
artifact.c behind a file-scope `.skip K`, timed in the same interleaved rounds; verdict needs the pad-median win to
exceed both arms' spread across pads, the null deviation and the IQRs, with every paired pad agreeing in sign;
verified to move the entry point on this box: 4 distinct addresses), the CELL row (per round, per arm, median over the
named subjects = the bench's cell number), the dense/sparse variants (`artrev.py variants`), `confirm_prep.sh`.
Not done, by instruction: no `--dry-run` against ubuntubudu (the harness refuses it outside 08:00-19:00 and the hour
override is self-test only); the first real action of the confirmer is the dry run.

## 5. Needs a ruling

1. **rvA09's wrong L4 r2 does not FAIL under the give-up rule as amended (497f8bda).** It answers a correct match
   where the original gives up with FRAMES/TRAIL=0 (5,562 such calls, all equal to libpcre2), which the rule calls
   the permitted repair direction. The brief asked that it FAIL; the rule says PASS. The harness does both: default =
   the rule (PASS, repairs counted and checked), `--strict-giveup` = FAIL. If the intent is that a twin must never
   change which calls give up (limits observable as a contract), the confirmer should use `--strict-giveup` always and
   most A07 twins fail it; if limits are cost bounds only, as the charter sentence says, the default stands. The spec
   reads that way: `docs/spec/limits.md` section 1 promises only that "a give-up is never a false answer" (an honest
   "I don't know"), and section 8 item 2 treats the OPPOSITE direction, a compiler-chosen K that turns a match into a
   give-up, as the answer change ("would be an answer change no flag asked for"); nothing there forbids a build that
   answers correctly where another would have given up. My recommendation: keep the default, print the repair count in
   every report, and let S5 state the emitter-side consequence (an optimization that stops giving up changes the
   `_in`/`PCREC_ERR_FRAMES` escalation behaviour documented in limits.md section 7, which callers who escalate on
   FRAMES would simply never trigger).
2. The identity HAVE_IN bug (section 2) means the pilot's earlier PASS rows are void for the `_in` entries; section 3 is
   the replacement. If the manager has quoted "A07/A09 identity zero differences" anywhere, re-cite this table.

## 6. Validation

SELFTEST_PLACEHOLDER

Commits: see `git log lane/artcollect`. Files added/changed: `studies/artrev/{identity.py,common.py,timing.py,artrev.py,
shim.c,artrev_abi.h,driver_id.c,pcre2_ref.c,selftest.sh,selftest_twins.py,README.md,CLAUDE.md}`, new `driver_pf.c`,
`driver_spans.c`, `variants.py`, `confirm_prep.sh`, `reverify.sh`, `fixtures/`; `docs/dev/optloop/artrev/{A01,A07a,A07b,
A09,notebook,pilot_index.md,pilot_pins.tsv,confirm_plan.md}`; `docs/dev/optloop/CLAUDE.md`.
