# rule — memfn-mcfixb

## Findings

### RULE-1 (CONFIRMED; severity: answer/measurement; effort: 2 lines; blast radius: EVERY CLI verdict of the mfcard window) — the CLI scores every run as a SECOND run, and `--second FIRST FIRSTAVX2` crashes
d197_rule.py:500 `main()` passes `"--second" in a` (a bool) as rule()'s `second`, but rule() (:263-268) now takes the first
run's (shipped, avx2) RUNDIRS and derives `is_second = second is not None`. Without `--second`, second=False, which
`is not None` -> is_second True: a first run is scored as the second (INCONCLUSIVE becomes NOT-WIN, "never a third
run"). With `--second X Y`, `zip(..., True)` -> uncaught TypeError (not InputError, no exit 2). The drill calls
rule() directly (second=None), so 45/45 ok while the shipped entry point is wrong: the control shares a source
with nothing the CLI does (learnings §3).
Repro: copy est's synth shipped record (drill SCRATCH) to p1, set its libc line to `memchr=avx2` (no tunable: the
shipped arm is no-verdict). `d197_rule.py rule p1 d197_avx2` -> all three levels `NOT-WIN (second-run-without-a-verdict)`;
`rule('p1','d197_avx2')` in python -> `INCONCLUSIVE (shipped-arm-no-verdict)` (expected). `... rule A B --second p1 B`
-> `TypeError: 'bool' object is not iterable`.
Fix: parse `--second` like `--confirm` (two rundirs, refuse otherwise) and pass the tuple/None; add a CLI-level drill
case (subprocess) for: no flag, --second pair, --confirm pair, --second + --confirm.

### RULE-2 (CONFIRMED; severity: maintenance/measurement (re-derivation); effort: small (a ruled exemption or a pin-backfill path); blast radius: every pre-r6 window: s2d1, s2d2, and memfn/data/policy.tsv's r_max_e6 derivation) — est.py now refuses EVERY record finalized before r6, and the only remedy (re-finalize) is itself refused on this box
est.py:540-545 (read_cells) refuses a cells file whose `cells_sha256_<job>` pin is absent ("the record pins none").
No record finalized before this commit carries that pin, so `est.py rows|draft` over a copy of an s2d run dir (the
workflow s2d2/rev15_rows.txt and r11_rows.txt were made with) and `rmax_drill.py RUNDIR` (span_cards/rmax_drill.py:72,
est.compute: the documented re-derivation of memfn/data/policy.tsv r_max_e6 "over both windows") are now REFUSED.
The way back, `record.py finalize` on the copy (which would compute the pin from the files as they stand, i.e. bless
whatever is there), is refused before it reaches the pin: `record.py window` on a copy of s2d1's and s2d2's
committed run_record.tsv -> `REFUSED: the record's libc is 'glibc 2.43', this box's 'glibc 2.43 memchr=evex': one
window, one box` (rc 2) — r5's memchr probe, not this diff, but together they leave no supported path.
Repro (cells are only in scratch, so the s2d case was modelled): est._synth(window='s2d') -> priced 38 rows FULL;
the same record with its cells_sha256_* lines removed (= a pre-r6 record) -> `CELLS PIN cells.J2.tsv: ... the record
pins none (... or a record finalized before r6)`. record.py window on copies: rc 2 as above (both windows).
Not broken: the committed run_record.tsv files and zen4-grid3's PROVENANCE sha (unchanged bytes); j1_rule.py on a
j1_cells.tsv (no pin read). Expected: either (a) a record without ANY cells pin is read as "pre-r6, unpinned" with
a printed note (refuse only a pin that is PRESENT and differs, which is the tamper case FIDELITY-3 targets), or (b)
the refusal is ruled deliberate and the re-derivation docs (rmax_drill.py header, s2d2/CLAUDE.md) say old windows
can no longer be re-priced. Note this is the THIRD "pin present? must equal" mechanism of the record (manifest_sha256
r11, rule pins r6, cells pins r6), each with its own absent-pin policy: manifest_check (r11) and the rule pin differ
from this one — see RULE-4.

### RULE-3 (CONFIRMED by the drill's own case; severity: design (over-refusal on another box); effort: one arm-table row + one drill case; blast radius: any mfcard window on a box whose shipped memchr is the AVX2 one, e.g. ubuntubudu's Zen 1 (AVX2, no AVX-512)) — FIDELITY-2's shipped-arm guard refuses the CORRECT shipped arm on a box without AVX-512
d197_rule.py:75-77 `memchr-variant-not-the-arms`: the shipped arm is no-verdict when it bound `avx2`. On a box with
no AVX-512 the shipped glibc memchr IS the avx2 variant with no tunable, so the shipped arm is always no-verdict ->
INCONCLUSIVE, and on the re-run NOT-WIN, for every level, without a number being read. The drill pins this as
intended ("[r6 FIDELITY-2] the shipped record bound the avx2 memchr with no tunable: INCONCLUSIVE"), which is right
on the 7700X only: the guard encodes this box's ifunc landscape, not the property it means (the shipped arm ran
with NO tunable; the AVX2 arm bound avx2). D144 add. 4 puts official SIMD verdicts on the targeted hardware, and
x86-64-v3's natural target box is AVX2-only. Expected: refuse the shipped arm on `tunables` alone; when shipped and
AVX2 arms bound the same variant, name it (one libc row, 18 comparisons, or the two arms as twins) rather than no
verdict. Trigger: the first mfcard window planned off the 7700X. Today: HOLD-able if the window is ruled 7700X-only
(then say so in the tsv header).

### RULE-4 (design/maintenance; general form + unlock; effort: small) — three "record pins a file, a reader must match" mechanisms, three absent-pin policies
manifest_sha256_<job> (r11; est.manifest_check: absent pin ALLOWED, reported "pinned?"), cells_sha256_<job> (r6;
est.read_cells: absent pin REFUSED, RULE-2), d197_rule_*_sha256 (r6; d197_rule.provenance: absent REFUSED, by
design; record.window: present-and-different REFUSED). Plus `cards_sha256`/`policy_sha256` (r9fc) and
`transcript_sha256`. Each is written and checked by its own code with its own wording. Side effect of the ad-hoc
home: record.window() writes D197's rule pins into EVERY window (s2d, j1 included), so editing d197_rule.tsv in the
middle of an unrelated s2d window refuses that window's next job ("D197's rule moved inside the window").
General form: one declared PIN table in record.py — (key, file(s), written at {window|finalize}, windows it applies
to, absent-pin policy {refuse|allow-with-note}) — and one `check_pins(rec, rundir, readers)` est and d197_rule call.
Unlocks: RULE-2's old-record policy becomes one row's column, not a code change; a window-scoped pin (rule pins only
for mfcard/mfconfirm) is a column; the next pin (e.g. j1_cells.tsv, the transcript) is a row. Trigger: the next pin
added, or RULE-2's ruling.

## PROBED-AND-HELD
- (a) Independent reading of d197_rule.tsv's tables vs the script on the drill's 31 constructed outcome cases: my
  first-match reading agrees with every expected verdict (NOT-WIN `second-run-without-a-verdict` first, before
  INCONCLUSIVE/CONFIRM: RULE-1 ordering holds; R1 re-score of CONFIRM levels only in score(); RULE-5 refused/absent
  confirmation -> INCONCLUSIVE, never CONFIRM again). The drill's 14 provenance cases hold (45/45 ok with SCRATCH).
- Valid pair ADMITTED on REAL records (not constructed): est._synth mfcard shipped (evex) + avx2 (tunable) plus a
  real mfconfirm synth (SLOT_CONFIRM_CELLS="65536.0 2.100", run id c1, both arms) -> provenance + confirm_cells_check
  pass; est.compute prices a mfconfirm (J2, JMHC) record FULL, meta() reads its JMHC cells and folds. 1 case.
- Plants REFUSED: own records as confirmation (end-to-end drill case), pre-r6 pin, other rule table, code_commit,
  plan, fold, run-id reuse, wrong JMHC cells (drill provenance, 13 cases) — held.
- RULE-7: the end-to-end check's regex `ratio [0-9]+\.[0-9]{2}` fails on "-" (unpriced scan): can fail now. Held.
- FIDELITY-2 avx2 arm requires memchr=avx2; shipped refuses tunables/avx2 (see RULE-3 for the over-refusal).
- (b) per workflow: d197_rule on old records: no mfcard/mfconfirm record exists anywhere reachable (tree: only
  s2d1/s2d2 run_record.tsv; pcrec-bench: none; scratch outside the denylist: none), so nothing earlier is in its
  population — NOT broken. est re-pricing an old s2d record: BROKEN (RULE-2). Old record re-finalized: BROKEN, but by
  r5's libc probe (record.py window on both s2d copies, rc 2), not by the new pins (they would be added None->set).
  Draft regenerated from an old window: BROKEN (same est refusal). rmax_drill.py RUNDIR: BROKEN (est.compute).
  zen4-grid3 PROVENANCE sha / committed records / measure_store / memfn/data: unchanged bytes, NOT broken.
  j1_rule.py on j1_cells.tsv: NOT broken (no pin read).
- Pin TIMING: record.window() pins the rule at every job start, so an mfcard record run at a post-r6 commit is
  pinned before its numbers; a record whose window started under a pre-r6 record.py would be pinned at finalize
  (after numbers) silently — no such record exists (mfcard has not run). Held.
