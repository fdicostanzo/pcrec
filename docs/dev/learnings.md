# Consolidated learnings — distilled from the full dev journal

Written 2026-08-17 (twenty-eighth session) from a complete read of all
126 journal entries (sessions 1–28, 2026-08-09 onward), at Frank's
request: the durable lessons, consolidated so a future session does not
need the whole 9,000-line journal to inherit them. The journal remains
the record; this is the digest — and it replaces only the DEEP-HISTORY
read: the journal TAIL is still the mandatory session-start read for
current work and status (Frank's standing rule; the wake sequence). The check-design lessons have their own
richer home in the manager's memory file (pcrec-check-design-lessons.md)
— §3 here is the summary, not the replacement. Update this file at
session close when a NEW lesson class appears; do not re-state instances
of classes already here.

## 1. Measurement discipline

- **Measure before describing.** Every early review found claims written
  from memory that one measurement would have killed (nine registry rows
  asserting a PCRE2 semantic that does not exist; python's repeat
  ceiling copied wrong into four files; a 40% "improvement" that was a
  27% regression). If a number appears in a commit message, decision
  entry, or journal, it came from a run against the exact build being
  described — or it does not appear.
- **A single sample is not a measurement.** Interleave builds, repeat,
  judge on medians with spread printed, pin to a core, check load
  before AND after — and check PER-CORE occupancy, not just loadavg: a
  1-minute load of ~1.0 is one competitor sitting on your pinned core
  (the poisoned-core incident: a killed benchmark's orphaned pinned
  children halved every engine's throughput while the global load guard
  read "quiet"). A locale is an instrument too: `sort -u` under a UTF-8
  locale merges regexes that differ only in punctuation — `LC_ALL=C`,
  always (bitten three separate times, once by a critic checking a
  correct count).
- **Predict, then measure.** State the expected populations/floors/
  verdicts before the first run. This is the difference between a floor
  and a number copied from output, and it caught transcription bugs the
  first run would otherwise have laundered.
- **A decision-critical measurement kept in a scratchpad has expired
  before anyone asks for it.** Commit the probe, archive the output with
  a provenance header (D35: pure function of probe + ABI + oracle
  version). A number that cannot be re-run is not a measurement — and an
  ARCHIVED file can still be empty (the K24 h2h archive was header-only;
  the claim survived only because the instrument was re-runnable).
- **Negative results are results.** Record them with numbers and protect
  them with a check where possible, so they cannot be re-landed on
  plausibility (M2.10's skip-eligibility revert has a codegen check).
- **Sanity-check results against their expected functional form.** Three
  sizes returning one boundary is not what a linear law looks like; a
  bisect converging to 1 everywhere was a harness that never built. And
  a suspicious GREEN deserves the same investigation as a red: greens
  predicted red found the two-knob half-landed calibration and the
  vacuous argless probe.

## 2. Oracle strategy

- **Where python `re` and PCRE2 disagree on what a construct MEANS, a
  python-verified corpus CERTIFIES the divergence instead of catching
  it** (\v, POSIX collating, `[:alpha:]`, brace whitespace — four
  instances). The base tier oracle is the right first oracle and cannot
  be the last word on PCRE semantics.
- **Reading the spec against the parser beats running the compiler for
  flavor bugs.** Five consecutive checkpoints: ~54M oracle-checked
  comparisons found zero compiler defects while afternoons reading
  PCRE2's reference found three real errors. The registry exists
  because of this.
- **No oracle-exclusion mechanisms; three-way comparison with the
  2-1-minority rule** (D44). The planned python-vs-PCRE2 exclusion
  machinery would have HIDDEN K17: the disagreement it guarded against
  measured zero, and every real disagreement was pcrec vs both oracles.
  Point instruments at pcrec first. The rule has since earned itself
  twice more (the (|a){m,n} family where pcrec+libpcre2 agree against
  python).
- **PCRE2 facts are measured, never read from documentation** — and each
  measurement names its version (10.46 throughout). D26's tiers govern
  how much fidelity each surface is owed; tier-3/4 gold-plating is the
  recurring temptation (the LIMIT_MATCH overflow boundary reproduced to
  the digit on a row we had already ruled out of scope).

## 3. Check design (summary — the full catalogue lives in the memory file)

The single most recurring finding class in the project: every checkpoint
panel found the same defect in whatever check was just built. The
distilled forms:

- A control must not share a source with what it controls — nor a
  FAILURE MODE (empty-vs-empty compares equal), nor may the composition
  go dark while both components stay honest (the wired-check vs
  removal-caught-check split: S43 sat APPLY-FAILED for days while the
  coverage assertion truthfully passed).
- Guards written to answer a finding are reliably wrong in the way the
  finding was wrong; only positive controls catch it, and an EARLIER
  control must be re-run after a LATER change.
- Exact counts disarm themselves via their own failure message; the fix
  is a manifest naming irreplaceable rows. Floors answer "did someone
  delete a lot", never "the right ones".
- Ask of any new guard: not "does this check run" but **"what would have
  to be true for it to fail, and who chose that input"**. Liveness
  arguments are not value arguments.
- Which of the branches I just added can no test see? What does this
  code compute that nothing observes? Which suite reads this FIELD of
  the output (offsets were the blind field twice of three)?
- A corpus needs the axes of the MECHANISM under test, not of the
  exemplar that motivated it (stride/residue; the cross-product cell
  neither of two large honest sweeps generates).
- Sabotage-validate every check; prove the sabotage reached the binary;
  assert exact occurrence counts in patch harnesses; a green sabotage is
  a finding about the population OR about redundancy — run it to find
  out which.
- A REFERENCE BUILD assembled by glob or hand-enumerated list drifts
  silently from the subject's source set ([M5-SEAM], 2026-08-18: two
  suites' one-level `src/*/*.c` globs missed the new `src/gen/enc/`
  nesting — loud that day only because the symbols were missing; a
  differential whose reference quietly compiles from DIFFERENT sources
  measures nothing). Enumerate by `find`, and hard-fail on an empty or
  suspiciously short list — the source LIST is itself an input someone
  must have chosen.

- **Provenance IMITATION is worse than absent provenance** (thirty-third,
  R30 M7): a hand-written header in a mechanical archiver's output format
  defeats the reader's ability to distinguish stamped from asserted — the
  sharpest instance yet of a control sharing a source with what it
  controls. Rule: an archiver is the ONLY writer of its output directory;
  a hand edit there is a red line, and the doc table citing an archive
  must byte-match it (R30 N2 was the same failure one step removed).
- **A named defect is not a fixed defect — the fix must travel as
  committed tooling** (thirty-third, R30 M6): the locale `sort -u`
  undercount recurred verbatim AFTER being found, named, and fixed in a
  sibling lane, because the fix lived as knowledge instead of as the
  committed harvest script (LC_ALL=C) it now is.
- **Extraction helpers hard-fail on empty, never default** (thirty-third,
  [ABI-NS]): eight test sites read a constant from the wrong file after a
  relocation and `(0x$empty))` arithmetic'd to 0 silently — every
  "possessified?" answer flipped to no across four suites, caught only by
  the SUITE'S non-vacuity guard. A detection helper that returns a default
  on missing input fails in the silent direction; extract, test -n, exit 1
  naming the file and constant, THEN use.

## 4. Testing strategy

- **Behavior-preserving change is the perennial blind spot** — three
  consecutive early checkpoints, then repeatedly since. The nets that
  work: structural/codegen checks, byte-identity gates against a
  pristine `git archive HEAD` build, output-preserving differentials
  with positive controls, and the green-because-fast sweep at every
  optimization landing ("what was slow or big because of the thing I
  just removed?" — five checks found un-tested at the revdet landing
  alone, all re-pinned with denial flags).
- **D27 blinded spec-first testing pays, and the mechanism is the
  alphabet.** Tests derived from the implementation inherit the
  implementation author's alphabet (every range was `a`-based; the
  masking bug needed a lower bound below `[`). Isolation, not
  adversarialness, is the active ingredient — and the GENERATED sweep is
  what makes it pay (both D27 tier-1s were reached by generation).
  Cells (scripts/mk_d27_cell.sh, allowlist REQUIRED per invocation)
  exist because ambient CLAUDE.md injection leaks denied context;
  briefs demand disclosure of the residue.
- **An identity proof cannot see a bug both sides share.** "Did I change
  anything" and "was it right to begin with" need different instruments.
- **Every strategy-selection point observable and forceable (D46), and
  witnesses must SELECT.** A test whose pattern routes to a different
  engine than intended reports green about nothing — assert the stamp
  (RX_ENGINE, VM_RUNGS/STRATS bitmasks), report selected-counts not
  passed-counts, and give per-case expected-engine assertions to
  benchmarks (the bench engine-drift went unseen for three days because
  floors pinned numbers without pinning what the number measured).
- **Budgets and honest refusal:** every compile AND execution of
  generated code runs under a bounded clock (D45, CPU-primary with wall
  backstop — CPU is load-RESILIENT, ~2x inflation worst case, where wall
  stretches unboundedly); a timeout firing is a FINDING; "hang" is a
  diagnosis, not an observation (slow-and-correct vs looping demand
  opposite actions — read the emitted loop, fit the growth law); an
  unbounded compile reads as "still running", never as "failed".

## 5. Design process

- **Design panels are the cheapest reviews available.** R9 found
  thirteen findings in built code; R10 found comparable severity in a
  document where every fix was a paragraph edit. Design-first-then-panel
  is now the standing shape (K18, ENG-BREP, counter-K, K23 — each
  refuted parts of its own first draft before code existed).
- **Simulate a design against the real data before adopting it.** Rank
  was simulated over 176k probes and survived; the ordered-list
  alternative died on the shipped table with no edit required. Prototype
  candidate mechanisms head-to-head and let measurement pick (K18's
  A/B/C, K24's four levers, K23's three rivals priced).
- **Frank's one-line questions find what panels inherit.** "Do we really
  need this?" and "is this really constant?" each killed a mechanism
  three panels had accepted. Every panel was internally sound and built
  on the same unexamined premise — questioning premises is a distinct
  lens from finding errors.
- **The critic is also a contributor.** Settlement 4, the lattice fix,
  the prefilter-window ceiling all came from verification passes — with
  provenance recorded. And verify a critic's consequence claim the way
  you verify your own: run it (two critic claims died that way).
- **BELIEVED marks are the panel's target list.** At R21 all eleven
  STRUCTURAL citations held and everything that broke was marked
  BELIEVED. Mark claims honestly and budget probe time by the marks.
- **Apply D27 to every enumeration, not only signatures** — deriving a
  verdict vocabulary from one doorway (sample size one) recreated four
  fixed bugs; the same document stated the rule and broke it two pages
  apart.
- **A wrong description of correct code still costs** — the next reader
  reasons from the description (three separate hunts for bugs that
  committed docs said existed). Correct the document with the same
  urgency as the code, and grep a wrong number EVERYWHERE rather than
  fixing the place you remember writing it.

## 6. Orchestration (lanes, critics, sessions)

- **Critics write findings incrementally to a file, get prodded, get
  re-polled after the prod and immediately before compiling, and the
  checkpoint is not closed until every critic has idled.** Each clause
  was paid for separately: batching critics delivered nothing twice;
  three of five delivered their best material after being read; panels
  delivered after the commit three sessions running. Narrow briefs beat
  five-part briefs, measured twice (2-of-4 vs 4-of-4 delivery).
- **Lanes: worktrees for writers, WIP commits as crash insurance and
  watchdog signal, async long validation, landing bar travels with the
  brief.** The box rebooted mid-session and lost zero work because
  everything was committed; a session crash cost ~30 minutes of
  reconstruction for the same reason. A lane blocked in a foreground run
  is indistinguishable from dead — both wrong liveness calls have been
  made. An idle notification without its report means ASK FOR A RESEND
  (raced every session since adopted); message crossings get ordering
  acks; rulings land on main first and lanes verify against committed
  docs with verify-after-apply on both sides (a scripted replace once
  failed silently; a partial-apply left half an edit unlanded twice).
- **Liveness is a fact about artifacts, never process greps.**
  `pgrep -f <target>` matches its own harness wrapper (three incidents,
  including 17 mutually-deadlocked watchers); completion trailers in
  logs, commit age, and mtimes are the trust chain — but a fresh mtime
  is not an append (check the tail timestamp) and `find -newermt` needs
  ISO timestamps on this box.
- **Shell discipline, paid for repeatedly:** a pipe eats the exit code
  you were gating on; a script ending in `grep -c` exits 1 when the
  count is zero (bit the manager twice, most recently reading a green
  battery as a failed task); `$(...)` strips trailing newlines (byte
  0x0A became the empty string in a sweep); cwd is state — absolute
  paths always (three wrong-tree incidents); kill by PID, never by a
  pattern that quotes itself; `df` lies about tmpfs per-user quotas.
- **Review a lane's report as a receipt**: invariants must account for
  everything sent to it, including mid-flight messages; verify "not a
  bug, here's why" claims against the SHIPPED artifact (one-minute stamp
  checks close the gap between "the analysis declines" and "the built
  pass declines"); a commit message is a claim — grep, don't believe
  (one brief propagated a wrong fix attribution that way).
- **Model tiering and budget:** sonnet wherever the work fits, opus for
  engine code and hard design, the manager's model never in lanes.
  Budget paces at ~14%/day of a 7-day window; the tiering is what keeps
  it there. Fact-gathering delegates; architectural judgement stays in
  the main session.

- **Panel targets are FROZEN COMMITS** (thirty-third, R30): the manager
  relayed design inputs to the author mid-panel twice and the target moved
  under working critics both times. Freeze before launch; batch every
  input — including the manager's own fix items — until the round
  compiles. Corollary: pin verification is by commit id the VERIFIER
  rev-parses, never one reported in prose (a lane fabricated a plausible
  hash in a summary this session and self-corrected; the habit made it
  harmless).
- **An idle agent has no tool rounds** (thirty-third): "poll at each tool
  round" cannot wake a lane whose background run finished while it idles —
  three missed completions in one session. The manager reads the
  completion artifact and pings; the lane-side fix is to hold an active
  poll loop only when a run is expected to finish within the round.

## 7. Durable technical facts (cheap to forget, expensive to re-learn)

- **gcc:** compile time is superlinear in the FAN-OUT of a computed
  goto's address-taken labels, not file size; -O2 partial-inlining
  splits a function with same-TU wrapper callers into a layout-sensitive
  `.part.0` (K24 — `noclone` on the callee is the minimal denial;
  caller-side attributes do NOT prevent the callee split); a ~670 KB
  single function can DNF -O2 at 300s while -O1 takes 6.6s; -O1 DSE
  legally erases an unobserved heap-overflow write before ASan sees it;
  `-Wextra` missing-field-initializers turns trailing-field schema
  widening into per-row enforcement.
- **Process control:** soft-only RLIMIT_CPU yields a diagnosable SIGXCPU
  ("CPU time limit exceeded") where soft=hard escalates to SIGKILL and
  reads exactly like an OOM kill; a backgrounded job in a
  job-control-less shell gets /dev/null stdin (the watchdog swallowed a
  differential's entire subject stream — 77,725 cells → 0 with "0
  diverged" staying green); timeout-killed harnesses leave their pinned
  children running.
- **The engine:** the DFA prefilter IS the general linear check
  (set-simulation over all start positions); the VM's costs are the
  price of leftmost-greedy capture semantics and the backref roadmap
  (NP-complete); steps and work meter genuinely disjoint cost classes
  (measured at counter-K's calibration); meter output is PREDICTABLE
  FROM EMITTED STRUCTURE (closed forms verified out of sample) — which
  is what makes refusals explainable and budgets calibratable.
- **Calibration has TWO knob pairs** (VM_DEFAULT_* for the unbounded
  class, VM_MAX_AUTO_* clamping the large-bounded class) — they emit the
  same arrays under the same D19 arithmetic and move together or the
  calibration is half-landed. K (unroll) lives in limits.h because it
  decides what COMPILES; runtime budgets live in emit_vm.c — limits.h's
  inclusion rule ("changes what pcrec accepts, rejects or promises") is
  the discriminator.
- **Environment:** this box's /tmp is a per-user-quota tmpfs that `df`
  misrepresents (use the scratchpad; TMPDIR=/var/tmp for big jobs);
  timezone flipped UTC→EDT mid-project (2026-08-15) — earlier journal
  timestamps are UTC.

## 8. The meta-lesson

Stated once at R3 and confirmed ever since: **the compiler holds up
under attack; what fails is what we write ABOUT the safeguards.** Claims
about checks, budgets, coverage, and measurements need the same evidence
discipline as claims about code — and they are exactly where the
discipline lapses, because the sentence being written feels like
bookkeeping rather than a claim. The rule is easy to remember and hard
to apply to the sentence currently being written; the working
countermeasures are mechanical, not attitudinal: predict-then-measure,
positive controls, re-run-after-change, manifests, provenance headers,
and panels over everything load-bearing — including this document.

## Addendum, 2026-08-19 (thirty-fourth session) — the identity lesson class, three instances in one day

1. **Kill by identity, never by name pattern.** A command line is not an
   identity: two legitimate concurrent invocations of the same tool are
   indistinguishable under any `pkill -f`/`pgrep -f` pattern, and the
   pattern can match the caller's own wrapper shell. Kill the PROCESS
   GROUP of the shell you launched, or the recorded PID. Two incidents
   hours apart (wave B lane; then the MANAGER, after journaling the
   first). Product: `scripts/safekill` (merged db8ddde) — briefs point at
   it; the matrix runner's completion comment carries the third outcome
   (no trailer AND no FATAL = killed, not failed — the row-count guard
   counts INSIDE the script and cannot see a SIGTERM).
2. **A script with a live instance is a running program, not a file.**
   bash reads lazily by byte offset; editing a live script can execute
   garbage. Safe orders: edit before the run, after it, or in a copy the
   run does not read (git-archive scratch trees give this free). Wave C
   lane's near-miss, self-reported, while writing the comment about
   incident 1 — same class.
3. **Done working ≠ done verifying.** Removing a lane's worktree while
   its verification shell was still using it stranded its cleanup trap.
   Confirm verification is finished, not just the work.
Also distilled this session: never launch your own copy of work you just
delegated (the duplicate created the kill-cleanup); a FLOOR gate PASSING
under load is a-fortiori valid, only its FAILURES need a quiet re-run
(wave C's contaminated case-g fail vs its loaded-box 13/13 re-run);
sub-second compiler spawns are invisible to point-in-time ps — check
archive/scratch mtimes before reading absence as death; briefs must cite
the design's PER-CONSTRUCT answers, not restate milestone obligations
over them (the manager's wave B seam instruction, caught by the lane's
stop rule — which also caught wave E's finding 6 against the manager's
repair brief).
