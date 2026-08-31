# r48 — [OPT-5] STEP 1 (DFA scan edge) close panel + [M4-QUOTING] check movements

Panel of three read-only critics (sonnet), run DURING battery 7 per the
panel-during-battery pattern, on merge 60c85f8's tree. Lenses: engine
semantics (r48sem), checks/guards/floors (r48chk), docs/spec staleness
(r48doc). Critics ran no make and wrote nothing; r48sem compiled/ran
single probe artifacts in its scratchpad (~35 probes, every one diffed
default vs -fno-scan-edge, several cross-checked against python3 re).

## Findings and dispositions

**F1 (r48chk, REAL — accepted): no sabotage row exercises the scan-edge
CAP's true enforcer.** scanedge.c:404's `nedges < SCAN_MAX_EDGES`
conjunct is what keeps marked-dead table cells and emitted edges in
agreement; emit_dfa.c:4474's cap is redundant by construction TODAY. A
future widening of one but not the other = miscompile (dead cells, no
loop) that nothing currently detects — the same failure family
S213/S214 pin on the criterion, unpinned on the cap.
DISPOSITION: S215 (widen/remove the scanedge conjunct on a >4-chain
machine; lost-match detector), landed post-battery with its own solo
DETECTED proof. Owed THIS session.

**F2 (r48chk, PROCESS — adopted as a verdict item): every DETECTED
figure this session (S21, S23, S212, S213, S214) is author-measured.**
The independent confirmation is battery 7's full matrix; the VERDICT
must diff the matrix's per-row figures against the figures cited in the
rows, not just read the summary line.

**F3 (r48chk, MINOR — accepted): S212's coverage-gap autopsy cites
scratch evidence that has expired** (learnings §3's "a number that
cannot be re-run is not a measurement"). The DETECTOR is genuine (the
D27 corpus); only the why-nothing-caught-it-earlier narrative is
unreproducible. DISPOSITION: post-battery comment amendment to S212
dating the autopsy as scratch-measured with the lane report as
provenance.

**F4 (r48doc, REAL — FIXED in-session):** src/parse/CLAUDE.md's "No
tests/quoting/ corpus ships with this landing" went stale when the
corpus landed hours later. Fixed (commit on main, the replacement also
records the corpus's miscompile catch).

**F5 (r48doc, unresolved → corroborated by the manager):** the
"guard 83→91→88" figure the critic couldn't locate lives in
tests/registry/run_registry_tests.sh (:343 chain comment, :434
assertion). Real and current.

## No-refutation results

- r48sem: ZERO divergences across all attack surfaces — the five
  preconditions (view-adjacent shapes a{0,4}$ / \z / (?m)$ / \Z / \G
  all correctly stamp "none"), the reverse pass (multi-chain,
  startpos-straddling via a custom rx_search driver), accept-fold
  arithmetic vs the uncollapsed walk (incl. the exact-count
  chain-into-chain shape [0-9]{4}[a-z]{0,6} where both emit blocks fire
  in one iteration), boundary shapes (subject-end, empty, count-exact,
  m=2 vs refused m=1, \x00/\xFF classes, caseless, bitmap bodies), and
  the 4-edge budget under overflow (longest-first selection verified).
- r48chk: S213/S214 anchors byte-exact and unique; detector
  disjointness honestly scoped (S214 discloses classes.rxt's 1
  failure); the 91→88 guard decrease's three-duplicates-one-falsehood
  argument verified against the live check code.
- r48doc: both abi-13 sentences, FILEPIN dc2c8ef resolving, stamp
  values vs the emitter's candidate table (three of four probed live),
  registry tally 108/14/16 verified via --list-syntax, limits 45 rows,
  D91 cross-notes — all consistent; no abi-12 residue.

## Side observation (recorded, not a defect)

r48sem: `foo[a-z]{0,50}bar` overflows the DFA construction (>32,000 raw
states from unanchored threading of the counted class) and falls back
before scan-edge can run — [OPT-4.1] SIZE-rung territory, and one more
datum for the embedded-chain future work already flagged in the [OPT-5]
row (the unanchored threading is what both refuses embedded chains and
blows up the state count; a future mechanism that tames one likely
tames both).
