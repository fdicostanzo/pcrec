# docs/design/m46a_impl/ — the [M4.6a] BUDGET CALIBRATION lane

[M4.6a]'s measurement: the four runtime-bound bring-up placeholders in
`src/gen/emit_vm.c` (`VM_DEFAULT_STEP_BUDGET`, `VM_DEFAULT_WORK_BUDGET`,
`VM_DEFAULT_BT_FRAMES`/`VM_DEFAULT_TRAIL_FRAMES`) against `engine_m4.md`
§4.6's stated method — extended, because §4.6 as written names only the step
budget. Kept separate from `counterk_impl/` and `k23_impl/` for the same
never-confuse-the-lanes reason those two are separate: this lane does not
design or build engine mechanism, it calibrates numbers already-built
mechanism enforces.

## The extension §4.6 needed, stated explicitly

§4.6's own text: "run the whole corpus plus the bench matrix with the counter
instrumented, take the maximum resumption count any legitimate pattern needs,
and set the default with a stated margin." That is the STEP budget's
procedure, singular ("the counter", "resumption count") — it says nothing
about work units, frame depth or trail depth. This lane's first finding is
that the procedure generalizes cleanly to all three once RX_ERR_WORK exists
(D49/settlement 4 landed it on main since §4.6 was written): the same
instrumented run, against the same generic emitted-code anchors, reads all
four counters off one call to `rx_search`. `probes/budget_calibration.py`'s
module docstring is the extended method, in one place.

## Why the corpus alone is not enough, and what fills the gap

The `.rxt` corpus is a CORRECTNESS corpus — its subjects are short by
convention, because a test author writes the smallest subject that exercises
a claim. That makes it the right source for one question (what does ordinary
combinatorial backtracking on a small, adversarial-by-construction pattern
cost?) and the wrong source for another (what does an ORDINARY LARGE
single-pass match cost, which is the scenario the WORK bound's existing
~10⁹/~1.6×10⁷ tension — `emit_vm.c`:90-100 — is actually about). The lane
therefore measures in three layers rather than one:

1. **CORPUS+BENCH** — the literal §4.6 reading. Finding: every committed
   `tests/bench` THROUGHPUT case compiles `--no-captures` (DD-9's own choice,
   to isolate the DFA prefilter), so the shipped bench matrix contributes
   **zero** VM-budget signal today — recorded, not silently patched around.
2. **SCALE** — synthetic legitimate large-subject VM-forced probes on
   representative rung shapes, including a stand-in for [M4.6b]'s
   not-yet-landed capture-bearing bench sibling
   (`([01]*)1([01]{8})`), because layer 1 structurally cannot supply this
   signal.
3. **RATIO** — re-anchors `k23_impl`'s retracted 5.24 proxy work-per-step
   ratio (`k23_design.md` §12 item 5, R26 M2/E6: "not a defensible
   calibration input... re-anchoring against the real meter costs one
   lane-hour once counter-K lands on main") against the real shipped meter,
   on the exact shape the retracted number came from. This shape is the K23
   PATHOLOGY itself (the pre-MRL exemplar) and is explicitly excluded from
   the layer 1/2 legitimate-need maxima — it is measured for the archival
   value alone.

## Files

- **`probes/budget_calibration.py`** — the whole sweep: corpus extraction
  (the same six-escape decode table `docs/testing.md` and
  `tests/harness/driver.c` define), a GENERIC instrumentation of four
  textually-uniform emitted-code anchors (`RX_PUSH`'s `w->btn++;`,
  `RX_TRAIL`'s `w->trn++;`, `rx_fail:`'s budget-decrement line, `RX_WORK`'s
  work-decrement line — matched by regex tolerant of exact-spacing drift,
  each asserted to match EXACTLY ONCE per VM artifact before anything
  downstream is trusted), the three layers above, and a SUMMARY block. A
  self-consistency check worth recording: layer 2's `([a-z]+)9` cursor shape
  reproduces `counterk_impl/probes/work_charge.sh`'s closed form
  (`n(n+1)/2` frameless-scan work on a nomatch over n bytes) EXACTLY, from
  independent code — the same shape of cross-check `work_charge.sh` itself
  used against `step_charge.sh`.

  Run: `python3 probes/budget_calibration.py [--full]`. Needs a built
  `build/pcrec` (asserted, not assumed). Env: `PCREC`, `CC`, `TIMEOUT`
  (per-subprocess, default 60s). `--full` widens the SCALE layer's size
  ladder. Exits 2 only on a broken instrument (no VM rows measured at all,
  or an anchor matching more than once); a genuine zero-need finding on a
  well-formed run is exit 0.

  The measurement uses `--backtrack-frames=20000` (not the shipped
  1024/1536), deliberately: the point is to observe the TRUE unclamped
  peak frame/trail depth legitimate subjects need, then compare that
  against the D19 128 KB stack ceiling separately — clamping the
  measurement to the candidate default would make every candidate default
  measure as "sufficient" by construction.

- **`sweep_out.txt`** — an archived run (D35's stable-name convention).
  Regenerate with `python3 probes/budget_calibration.py > sweep_out.txt`.

Maintenance: update this file when files are added/removed or their roles
change.
