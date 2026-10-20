# Journal notes, slice 3 (thirty-ninth session part 10 through fifty-first session part 58)

Scope: dev_journal.md, the span from 2026-08-24 (39th session, parts 10-45, the end of the
[DD-14] `recursion` build and its close) through 2026-09-04 (51st session, parts 25-59, the
evening wave of lanes A/B/D and the merge chain). Sessions covered: 39th (08-24/25), 40th
(08-25/26), 41st (08-26/27), 42nd-43rd (08-28), 44th (08-28/29), 45th (08-29/30), 46th
(08-30/31), 47th (08-31), 48th (08-31/09-01), 49th (09-01), 50th (09-02/03), 51st (09-03/04).
Items are cited by date + session + part title. "RECURS" marks an item seen more than once in
the slice. Quotes are verbatim and short.

---

## (1) PRACTICES THAT WORKED

### 1a. Subagent / lane control

P1. Design note first, then a read-only D6 critic panel BEFORE any code, for anything touching
the emitter. The panel found a miscompile in a design before it shipped.
- Source: 2026-08-28, 43rd session part 3, "chk2p1 merged; the [OPT-K] panel: MISCOMPILE-1".
- "no gate could see it (test-axes compares two builds sharing the set; the corpus lacks the shape)"

P2. A blinded test author (D27 cell: allowlist-filtered copy, no `src/`, no `tests/`) writes the
corpus from the goal; the manager triages "corpus-wrong vs pcrec-wrong" on first contact.
- Source: 2026-08-24, 39th session part 14, "the D27 BLINDED CORPUS DELIVERED (sr27)".
- "a blinded corpus of 1,031 cells with no corpus error on first contact, against the la27 precedent's 365"
- Second instance: 2026-08-31, 47th session, "THE D27 CORPUS CAUGHT A TIER-1 MISCOMPILE ON ITS FIRST RUN" ([M4-QUOTING]): "four adversarial-grade checks (probes, reject, registry, strict) were green over a miscompile the blinded corpus found in one run".

P3. The manager reviews the blinded author's EXTRACT for leaked implementation vocabulary
before the cell is built.
- Source: 2026-08-24, 39th session part 13, "the D27 EXTRACT merged".
- "a blinded reader must not learn the implementation's vocabulary from the list of what it may not learn"

P4. Critics run read-only; their output comes back as MESSAGES (they cannot write files), one
panel file is compiled by the manager with every finding dispositioned by id.
- Source: 2026-08-28, 44th session part 2, "artsize3's note delivered and PANELED (r40)".
- "the harness refuses critics' file writes, and the final-report channel dropped every one of them, so each was asked to re-send"

P5. Fix round -> FOCUSED RE-CHECK by the same critic who found the problem. The re-check found a
blocker in the fix itself (a ladder trial cannot be discarded because `ctx_fail` longjmps).
- Source: 2026-08-29, 44th session part 4, "r40 CLOSED after three revision passes".
- "a ladder TRIAL cannot be discarded"; also 2026-08-30, 45th session part 9 "Focused re-check of revision 2" (found B1's remedy not implementable).

P6. Design-lane panels run DURING the multi-hour battery: zero box time, design work overlaps
the box's busy hours.
- Source: 2026-08-30, 45th session CLOSE.
- "The panel-during-battery pattern ... is the shape to repeat: design work overlaps the box's busy hours"

P7. Model tiering: sonnet for docs/admin/measurement lanes, opus for emitter/engine/hard design;
the manager reviews rather than writes. Observed limits are recorded (see F-sonnet).
- Source: 2026-08-31, 47th session, "queue chartered ... all sonnet per Frank's tiering" (impl, corpus, STEP 0), with opus for the engine lane.

P8. Lane signalling by FILES in the worktree root: `.hold`/`.hold_ack`, `.lift`, `.stage`,
`<lane>_rulings.md`; lanes poll their own copy. A busy agent does not read messages.
- Source: 2026-08-30, 46th session part 3, "w11's unread LIFTs".
- "a BUSY lane's inbox drains only when it goes idle"; "From now on a HOLD/LIFT and any mid-run ruling is a FILE the brief tells the lane to poll."
- Source: 2026-09-03, 51st session part 25, evening wave "LAUNCHED ... under `.hold`".

P9. HOLD messages enumerate the forbidden SHAPES (no make of any kind, no gcc, no tests/ scripts,
no sweeps/loops/background jobs) and demand an ack on the first ping.
- Source: 2026-08-29, 45th session part 3, "a HOLD breach"; 2026-08-30, 45th session part 9, "Chartered under the battery's HOLD".
- "HOLD re-relayed with the forbidden SHAPES enumerated and an ack demanded"

P10. Reproduce the symptom before ruling or briefing (measure first, then charter).
- Source: 2026-08-28, 43rd session opening: "REPRODUCED before ruling: `level-context` ... auto refuses in 0.52 s, `--engine=vm` compiles in 0.00 s". Also 2026-08-30, 46th session part 2, absprobe answering the bench's fact question with a read-only probe.

P11. Measurement lanes refute their own charter, and that is treated as the deliverable.
- Source: 2026-08-26, 41st session, "srOpt3: [OPT-3] STEP 1 measured". The charter assumed the candidate-start skip loop mattered; instrumented count showed it "skips ZERO bytes"; a 7x faster skip made all subjects slower; the real lever (pre-multiplied table) was found and later measured 1.794x.
- "STEP 1's 1.276x was a FLOOR set by a patch, not a ceiling set by the mechanism" (41st session, srPremul part 2).

P12. A PREDICTION TABLE is written before a build/measurement and scored afterwards; the
bench receives pcrec's predictions before its sample.
- Source: 2026-08-26, 41st session part 1 ("Seven predictions P1-P7 for the abi-6 re-pin filed for the interpreter's ledger"); 2026-08-30, 46th session part 6 ("prediction to the bench: letters -> VM at every rung ... no count crossover"); 2026-08-31/09-01 O-12 scored it (letters 1.76-2.00 band held).

P13. Lane takeover protocol when a lane goes unresponsive: TaskStop, commit its verified
uncommitted work with the takeover stated in the message, REBUILD and re-verify on the final
tree, then merge.
- Source: 2026-08-31, 46th session part 12, "[LIM-1] LANDED BY TAKEOVER".
- Counter-practice: 2026-08-24, 39th session part 18 CORRECTION: "a lane at its authorization boundary looks like a stalled lane from outside"; "the manager should read the WIP commit message before acting".

P14. Brief files for parked lanes are kept verbatim (`<lane>_brief.md`, stale sections marked) so
a fresh agent can be relaunched onto the branch without the dead session's context.
- Source: 2026-08-31, 48th session close, "shutdown on Frank's budget call".

P15. Make lanes record "what to do at the authorization boundary" (report and hold).
- Source: 2026-08-24, 39th session part 18 CORRECTION; sr27land "had done everything within its authorization ... and was HOLDING".

### 1b. Session / context management

P16. A wake.md reset section makes a mid-battery context reset cheap; setsid'd batteries survive
the reset.
- Source: 2026-08-30, 45th session part 9, "context reset at ~01:30; battery 3 survives it".
- "orientation took six tool rounds, and nothing on the box was disturbed"

P17. The root CLAUDE.md gains a SITUATION INDEX ("about to X -> read Y", pointers not prose) as
a pattern-memory aid for the 10%-of-context problem; each re-learned lesson adds a row.
- Source: 2026-08-25, 40th session part 1, "THE GOING-FORWARD CONVERSATION" (ruling 5).
- "'about to X -> read Y', pointers not prose"

P18. Cache-warmth economics are stated and acted on: main session keepalive cron at off-minutes
(:09/:39); a context idle > 60 min is re-charged (main). Lane self-keepalives were adopted
2026-08-31 (48th session) and later REVERSED by the 2026-09-06 ruling in BOILERPLATE (lane
caches are 5-minute TTL; DO-THEN-FINISH instead). Evolution is the lesson.
- Source: 2026-08-29, 45th session part 4 ("keepalive cron at :09/:39"); 2026-08-28, 43rd session part 5 ("a context idle > 60 min is re-charged; ping held lanes inside the hour, never message done lanes"); 2026-08-31, 48th session open ("LANES SELF-KEEPALIVE").

P19. Artifacts over process greps for liveness: the watchdog reads a run log's mtime and tail;
a stalled lane is found by log age.
- Source: 2026-08-31, 47th session, "BATTERY 7 FALSE START AND RELAUNCH" ("the watchdog caught it by reading the STAGE LOG's mtime+tail").

P20. One repo per session when the owner asks ("Be the bench though - use its journal etc.") and
the durable inbox/outbox channel keeps its shape.
- Source: 2026-08-28, 42nd session, "short; the session moves to pcrec-bench".

P21. Read `date` before labelling a journal entry; times from lane message headers are UTC.
- Source: 2026-08-30, 45th session CLOSE ("read `date` before labelling a journal entry (three labels tonight ran ~30 min fast)"); 2026-09-02, 50th session part 6 ("the ~18:xx times ... were UTC read off lane message headers; corrected to EDT").

### 1c. Inter-session / inter-process communication

P22. Durable inbox/outbox files between manager and the peer bench session (`I-n`/`O-n`, one
writer each, single-file `[inbox]` commit); live messages for coordination only.
- Source: 2026-08-25, 40th session part 1 (D78); 2026-08-26..09-04 throughout (I-5 ... I-43).
- Rule that confirms the channel: 2026-09-01/02, 49th session part 5, "plan.md briefly cited a live bench message before O-13 existed (r49cons caught it; O-13/99de28e landed the durable record with an O-14 withdrawal rule)".

P23. WINDOW OPEN / WINDOW CLOSED handshake with the peer session for timing runs; BOTH sides
verify by cwd/ps before declaring the box clear.
- Source: 2026-08-24, 39th session part 20 addendum (protocol, "WINDOW OPEN with the load reading"); 2026-08-29, 45th session part 8, "Pre-HOLD slip".
- "'nothing of mine runs' is a `ps` fact, not a belief; run the grep before the message, every time"

P24. Box-sharing with a second Claude session: five rules (idle while lanes run, reads-only on the
primary repo, PID-only kills, scratch in its own scratchpad, announce heavy runs); primary vs
exploratory is stated.
- Source: 2026-08-24, 39th session part 18, "BOX-SHARING NOTE" and its continuation.

P25. A pin commit is named for the peer (the SHA whose `git diff --stat ... src lib cli tests Makefile` is empty
against main), with the battery that was run on it.
- Source: 2026-08-24, 39th session part 20 addendum, "peer coordination with pcrecdev2".

P26. Day/night split: pcrec lanes and batteries by day (one heavy suite at a time), the bench's
blocking windows overnight; announced in the durable channel.
- Source: 2026-09-02, 50th session part 7 addendum 4.

P27. When the peer's report lands, an executive summary (findings / surprises / impact / next
steps, every number cited to a ledger section) is written as a committed doc and reviewed.
- Source: 2026-09-02, 50th session part 5; part 17 (the second summary, "each carries the measured fact, the mechanism in plain language, and what it changes").

### 1d. Testing practices

T1. Oracle chain: libpcre2 10.46 is the reference, python `re` where expressible, a Perl arm for
the divergence record; a generator's INTENT is checked against the oracle.
- Source: 2026-08-24, 39th session part 14 ("a generator whose INTENT is checked against the oracle (6 cells caught that did not test what the author thought)").

T2. The identity gate is two comparisons with two OWNERS: the program region unfiltered against
a frozen pre-module reference (the module's promise, never moves); the whole file pinned to the
abi's last src commit (the scaffolding's promise). Never filter lines until things match.
- Source: 2026-08-25, 39th session part 31, "the identity gate SPLITS (option B ruled)"; 40th session part 1, D76.
- "the scaffolding is not comparable across the abi 2->3 boundary; the program is"; the rejected route is "gate that filters its way to identity".

T3. Sabotage matrix with an explicit expected-UNDETECTED list and a witness-reach check
([MECH-REACH]): a row must prove its witness still reaches the sabotaged site; UNREACHED is a
verdict.
- Source: 2026-08-25, 40th session part 3 ([CHK-1]); 2026-08-25, 39th session part 40 addendum (S70's witness expiry).
- "a sabotage row's witness can EXPIRE silently when a later wave implements the construct it relied on"

T4. A stale-anchor tripwire is a FAILING in-tree check, not a hand-run script.
- Source: 2026-08-26, 40th session part 14, "srAnchor MERGED" ([SABANCHOR]).
- "nothing in-tree had ever FAILED on a stale anchor"

T5. Answer-identity sweep over the whole corpus for every optimization axis (`make test-axes`):
diff by exact per-case ANSWER keyed by `<file>:<line>`, never by pass counts; give-ups classified
BUDGET-BOUND, refusals REFUSED-DOCUMENTED; oracle cross-check through live libpcre2.
- Source: 2026-08-26, 41st session, "lane srAxes: [CHK-2] pieces 2 and 3" and part 11 ("the sweep's verdict").

T6. Form census: a floor for every stamp value the corpus reaches, a built-and-asserted
synthetic witness for every value it does not, and a completeness loop over the documented value
sets so an unpredicted gap is caught.
- Source: 2026-08-26, 41st session, srAxes piece 3.

T7. `make test` ends with a completion trailer (`sections ran: N/M`, missing sections named,
hard-fail on empty argv); sections run under `make -k`.
- Source: 2026-08-26, 41st session, "lane srAxes addendum" and part 7.

T8. Every new check is validated in the FAILING direction with a plant, and the validation red is
recorded in the script header with the measured count.
- Source: 2026-08-26, 41st session, srPremul part 1 ("THREE PLANTS, AND ONE OF THEM REFUTED A SENTENCE OF MY OWN DESIGN NOTE"); 2026-08-25, 40th session part 9 (tier check).
- "every ANSWER stayed green and only the escalation assertions went red - the measured proof that an answers-only check would pass on a build without the optimization" (paraphrased from the same entry; verbatim fragment: "an answers-only check would pass on a build without the optimization").

T9. Non-vacuity guards: a check states its population by COUNTING at the comparison site and
asserts the count against what was due; a zero population is its own failure.
- Source: 2026-08-26, 40th session [DD-13c] part 2; 2026-09-04, 51st session part 46 (w13: "caught only by the two non-vacuity guards").
- "a number a check DERIVES about its own coverage is not evidence of that coverage; only a number it COUNTS is"

T10. Hand-twin / patched-artifact measurement BEFORE building: transform the compiler's own
emitted text, answer-gate it, then time it (premultiplied table, scan edge, island, fold).
- Source: 2026-08-26, 41st session, srOpt3 and srPremul; 2026-09-02, 50th session part 9 ([CC-DIFF] STEP 0: "two general emitter spellings, both measured").

T11. Timing discipline: quiet-box load gate, interleaved paired medians, calibrated iteration
counts, every arm ANSWER-GATED before any time is reported, controls beside the target.
- Source: 2026-08-26, 41st session, srPremul part 2; 2026-09-03, 51st session part 35 (isl1: "a harness that refuses above the bar").

T12. Scoped axis pair (deny/force on the one changed axis, full corpus, span+slots) is the
delivered identity evidence for a narrow change; the full sweep runs only if contradicted.
- Source: 2026-08-30, 46th session part 6, ruling (1).

T13. A refusal-identity ladder is part of an axis's acceptance, not only answer identity.
- Source: 2026-09-03, 51st session part 39 (r53sem S1: the island REFUSED a pattern the chain accepted).
- "an axis's acceptance is refusal identity as well as answer identity"

T14. Delivery bar re-pins every manifest/count the change moves, found by grep AND by running
the sections that count (registry, codegen, rxtsource).
- Source: 2026-09-01, 49th session part 4 (D94, "the abi ritual's site list is every-reader-by-grep"); 2026-08-26, 40th session part 11.

T15. K35 hygiene: `LC_ALL=C` at every `sort` site plus a structural check naming any unguarded
sort, validated red in three directions.
- Source: 2026-08-25, 39th session part 44 addenda (51 sites / 24 scripts guarded; structural sweep).

T16. Bound every compiler/matcher invocation in test scripts (D45 timeouts, `scripts/watchdog`)
so a compiler hang cannot kill a battery; a firing timeout is a FINDING.
- Source: 2026-08-25, 39th session part 38 / 40th session part 3 (K37, 461 sites / 77 scripts).

### 1e. Process (plans, decisions, reviews)

Pr1. One battery serves several merges when the merges are serialized with a short chain between
them; the full battery runs once after the last merge and its commit is THE PIN.
- Source: 2026-09-03, 51st session part 31, Frank "1. agree"; 2026-09-04, 51st session part 56 ("on the last merge the battery IS the chain").

Pr2. Battery verdicts are written by diagnosis: "GREEN-BY-DIAGNOSIS" names each red, the solo
re-run that cleared it, and the number beside it; the DONE line is not the verdict.
- Source: 2026-08-30..31, 45th-46th sessions (battery 3, 4, 5, 6 closings).

Pr3. Panel files (`docs/dev/reviews/<date>-rNN-*.md`), numbered, with each finding dispositioned
by id (accepted / pushed back with measurement / deferred with a trigger).
- Source: 2026-08-29, 45th session parts 2-3 (r43, r44); 2026-08-30 r45; 2026-09-01 r49; 2026-09-03 r53.

Pr4. Plan rows carry STATE tags; ideas from the owner are FILED as rows the same day with
provenance, not folded into running work (D77 trigger recorded).
- Source: 2026-09-02, 50th session part 6 addenda ([OPT-NEG], [FEAT-VAR]); 2026-09-03, 51st session part 23 addenda ([FORM-CHAR], [OPT-CLSPACK]); part 36 ([OPT-DIAL]).

Pr5. Three-column lane model (feature / optimization / admin) with one row per column.
- Source: 2026-08-29, 45th session part 1, D86.

Pr6. Measure before building: a D77 trigger names the measurement that would justify building;
STEP 0 measurement lanes precede STEP 1 designs; builds are gated on a measured need.
- Source: 2026-08-25, 40th session part 1 (D77: "build later under measurement"); 2026-08-28, 43rd session part 4 ([ART-SIZE] attribution).

Pr7. Run `/compliance-refresh` (three-component derived/surveyed/annotated doc) after a module
lands rather than editing prose.
- Source: 2026-08-31, 47th session ([M4-QUOTING] landing).

### 1f. Safety

S1. Kill only by PID and verify it by cwd; the session-leader PID is the one with `sid == pid`
and `ppid == 1`; scrape it in a SEPARATE command after the launcher exits.
- Source: 2026-08-25, 39th session part 36 addendum ("scrape AFTER the parent exits and match the process whose sid == pid"); 2026-08-31, 47th session ("THE LAUNCHER MUST EXIT FAST").

S2. Heavy detached runs use `setsid nohup` with a PID file; a `run_in_background` Bash is capped
at 10 minutes.
- Source: 2026-08-30, 45th session part 9 ("a `run_in_background` Bash is capped at 10 min").

S3. Before `git worktree remove`, check the process table for cwds under the worktree (by PID).
- Source: 2026-09-03, 50th session part 18 addendum.
- "a delivered lane's harness workers can outlive its delivery by a minute"

S4. Delete stale scratch only with the owner's yes (36 `/tmp/pcrec-*` dirs, 788 MB, no process inside).
- Source: 2026-09-03, 50th session part 23.

S5. A writer verifies `git rev-parse --show-toplevel` prints its worktree before its first edit.
- Source: 2026-09-02, 50th session part 11 addendum.

### 1g. Owner collaboration

O1. Rulings are collected in a batch ("go through questions one at a time please"), each
explained from the record, recommended, then recorded as a numbered decision (D74-D96).
- Source: 2026-08-25, 40th session part 1 ("nine rulings"); 2026-08-30, 46th session part 4.

O2. The owner's ideas are recorded in his words and sometimes overturn the manager's
recommendation; the manager records the disagreement and builds his way.
- Source: 2026-08-29, 45th session part 4 ("Frank ... ruling r44's blockers the OTHER way from my recommendations", D87); 2026-08-31, 47th session ([OPT-5] STEP 1: "Frank's IDEA ... wrongly told that's not what DFA engines do").

O3. Budget calls from the owner are honored mid-session and revised mid-session.
- Source: 2026-08-31, 48th session close and addendum ("complete all the live stuff ... then shutdown"; then "just let the lanes complete if it isn't too late ... just don't start any more lanes").

O4. The owner can simply reframe cost: "I don't want to add performance testing vm vs dfa to every
test battery ... last I saw our test battery was 3 hours and growing" -> proposal retracted; the
battery does not grow without a ruling.
- Source: 2026-08-30, 46th session part 8 (17:3x).

---

## (2) FAILURES / INCIDENTS AND THE RULE EACH PRODUCED

F1. HOLD breaches during the peer's measurement window (twice in 5 minutes). A lane ran a
harness section, then `make test-codegen`, a few seconds after the manager's re-relay. Cost: the
bench lost an attempt. Rule: enumerate forbidden SHAPES, demand an ack, TaskStop a lane that
will not drain; memory `pcrec-box-concurrency` rule 11.
- 2026-08-29, 45th session parts 3-4, "a HOLD breach" and "the second breach and the idle hold".
- "it had not yet drained the message"

F2. Manager's setsid PID mistake: scraped PIDs two seconds after launch and matched the `setsid`
parent, so the death-watch fired falsely and a chained `make mech` started while the identity
gate was still running (two heavy runs). Recurs 4x: the srFBc double launch, this one, the
45th-session death-watch, the 47th-session launcher timeout kill.
- 2026-08-25, 39th session part 36 addendum, "the manager trips rule 7"; 2026-08-25 part 29 addendum 3 (srFBc: "a failed-LOOKING launch may have launched"); 2026-08-30, 45th session part 9; 2026-08-31, 47th session "BATTERY 7 FALSE START AND RELAUNCH".
- Rule: scrape AFTER the parent exits and match `sid == pid && ppid == 1` plus cwd; the launcher must exit fast.

F3. Editing a shell script while it was executing. Bash reads scripts incrementally by byte
offset. A lane inserted ~10 lines into the identity gate mid-run and the abort looked like a
syntax error. Recurs: srMech lost a matrix summary the same way; the w11 lane edited run.sh under
test-corpus (174/178 workers); the landing lane edited main-tree scripts during san.
- 2026-08-25, 39th session part 32 CORRECTION; part 42; 2026-08-30, 46th session part 5; 2026-09-02, 50th session part 11 addendum.
- "NEVER EDIT A SHELL SCRIPT THAT IS CURRENTLY EXECUTING"

F4. Conflict markers committed as a merge. A chained `git merge ... ; git add -A && git commit`
committed the markers (twice, 40th and 41st sessions). Rule: run `git merge` alone, read the
result, verify zero markers as its own step, then commit.
- 2026-08-25, 40th session part 6 (docs/spec/CLAUDE.md conflict, fixed c52c9d9); 2026-08-26, 41st session part 11 ("the `;`-chained command went on to COMMIT THE MERGE WITH THE MARKERS IN plan.md").
- "resolve, VERIFY zero markers as its own step, then commit - never in one chain"

F5. Persisted `cd` across compound commands. Instances: a durable-channel write landed in the
bench's decisions.md (reverted); a nested worktree; a merge run inside a lane's tree; a lane
wrote its journal paragraph into the MAIN tree's journal; a stray log in the repo root. RECURS 5x.
Rule: absolute paths and `git -C`, never `cd` in a compound command; the situation index row says so.
- 2026-08-25, 40th session part 1 (D78 write); 2026-08-28, 43rd session part 7 (merge ran on lane/sizeratchet); 2026-08-30, 46th session part 3 (nested worktree); 2026-08-26, 41st session part 6; 2026-09-03, 50th session part 17 and 51st session part 44.

F6. Self-matching patterns: a waiter counted its own command line, a safekill matched the
manager's own shell (exit 144), a grep matched its own text. RECURS 4+x. Rule: build such a
pattern from two shell variables so the literal never appears in any argv; kill by bare PID.
- 2026-08-26, 40th session part 8 ("my first safekill matched my OWN shell's command line and killed it"); 40th session part 12 ("my 'wait until ... stop' waiter counted its OWN command line"); 2026-08-24, 39th session part 33.

F7. Verdict script that does not read its own inputs. The battery verdict summed
`checks failed:` lines and never saw a coverage-guard line, then printed RED with empty san/mech
fields on a green run, then died on `set -u`. RECURS 4x (41st pt 12, 43rd pt 5, 44th pt 6, 46th pt 6).
Rule: the verdict reads guard/FATAL/make-error lines, san's rc, and requires mech's trailer.
- 2026-08-27, 41st session part 12 ("a verdict that does not read its own inputs"); 2026-08-28, 43rd session part 5.

F8. Counts without a completion trailer. A lane's `make test` died silently at 12:15 with 1,872
PASS lines and the journal recorded "1,872/0" as complete; `make -j12 test` skipped every target
not yet started after one failure so `test-premul-table` never ran in two batteries.
Rule: count + trailer; `make -k`; the trailer names the sections that ran.
- 2026-08-26, 41st session part 3a ("a count without a 'this run finished' witness is a partial") and part 7.

F9. abi bump second-site misses. Two lanes missed two of four sites in one night; the identity
gate's FILEPIN went stale; a pin moved three times inside one change; a guard's second site (the
registry wrapper's count) went unexercised. RECURS 6x+ (see L2). Rule: D94, the site list is every
reader of the number found by grep, then run the sections that count.
- 2026-08-26, 40th session part 11 ("an abi bump has FOUR sites (emitter, codegen expectation, spec §6 sentence, gate pin)"); 2026-08-29, 44th session part 8 ("the fourth-site miss recurring one lane later on the same site"); 2026-09-01, 49th session part 4 (D94).

F10. Load-sensitive cells (K31/K32/K44) red under `-j12` in nearly every battery for weeks; each
was cleared solo "by diagnosis". Real cause was two stacked parallelism layers; measured shape
`-j4`/`PROCS=3` retired it (K44 cells green, 1,115 s vs 1,674 s).
- 2026-08-24, 39th session part 12 addendum (first filing of [TT-10]); 2026-09-03, 50th session part 18.
- "the two stacked parallelism layers were the whole of K44, and the measured shape retires it"

F11. Red attributed to the known load cell without reading failures-by-file. Battery 2 "cases
failed: 2" was a real [OPT-4] regression; battery 5's red had TWO causes (counterk plus a registry
coverage-guard line the failures-by-file rule does not read).
- 2026-08-30, 45th session part 6; 46th session part 9.
- "a wrapper's guard is a CHECK-side red the rule does not cover"

F12. Sabotage witnesses expiring silently. S70 (certified nothing for two milestones), S155
(deletion changed a write not an answer), S193, S206 (probe re-pointed by a rename), S219 (probe
marks a line every candidate executes, not the decline arm). RECURS 5x.
- 2026-08-25, 39th session part 40 addendum and part 41; 2026-08-31, 47th session verdict; 2026-09-01, 49th session part 4; 2026-09-03, 50th session part 12.
- "So the row has been certifying nothing since M6.5.2"

F13. Stale sabotage anchors found only by the battery: S174 (re-spelled `rmax == 0`), S179/S183/S67
(tripwire printed "ANCHOR NOT FOUND" while the script only tailed it), S73/S74, S21/S23, S102/S165
(four re-anchorings of the same expression across the [OPT-4] family). RECURS 5x. Rules: "re-run
the tripwire after the last SOURCE edit, not after the last edit one was thinking about"; the
tripwire became a failing in-tree check ([SABANCHOR]); "a check that prints but does not gate".
- 2026-08-25, 39th session part 23 addendum; 2026-08-26, 40th session parts 13-14; 2026-08-31, 47th session; 2026-09-01, 49th session.

F14. Lane messages and reports lost: a busy lane never reads a LIFT; the K43 ruling reached a
lane only on the third send; "Message delivery to this lane lags a full tool round"; every
subagent report was dropped by the final-report channel and had to be re-sent by message;
harness refuses subagent `.md` writes; a lane died on an API 403 with 38 files uncommitted and
no WIP commit; four API 529s killed a lane. RECURS.
- 2026-08-30, 46th session part 3; 2026-09-03, 51st session part 42; 2026-08-29, 45th session part 5; 2026-08-28, 44th session part 2; 2026-08-25, 40th session part 2; 2026-09-03, 50th session part 17 addendum.
- Rules: HOLD/LIFT/rulings by file; WIP commits are the liveness signal; "idle != delivered; the artifact decided".

F15. Lanes that wait for a notification that never wakes them: a background task completion does
not re-invoke a lane; "persistent monitor" does not wake an idle agent; three lane waiters never
fired; a sonnet lane answered two explicit FINALIZE pings with "I'll wait for the notification".
- 2026-08-29, 44th session part 7; 2026-09-03, 50th session part 15; 2026-08-31, 46th session part 12.
- Rule: the run's log is the trigger; poll the artifact; the lane's last act is the long run (DO-THEN-FINISH, later in BOILERPLATE).

F16. Harness reaps background tasks / launcher kills the tree. The matrix loop died at row 19; the
sweep died a second time; a `nohup ... & disown` run stopped; the launch command combining
`setsid` with a slow /proc scan blew the tool's 2-minute timeout and the SIGKILL swept the battery.
- 2026-08-24, 39th session part 21 and part 24 addendum; 2026-08-26, 41st session part 3a; 2026-08-31, 47th session.
- "the lane's background task reaped by its harness, not a row failure"

F17. A lane's validation claim was wrong and it took a second instrument to see it. [M4-QUOTING]'s
"164/164 probes" table listed the miscompiling shapes as PASSING (an absent test axis); srMech's
"UNDETECTED without ASan" was asserted by reasoning and never run; srK38's make test never finished.
Rule: a lane's report is a claim; "a parked cell's stated CAUSE is a claim".
- 2026-08-31, 47th session ("its probe harness has a self-confirming flaw"); 2026-08-25, 39th session part 42; 2026-08-24, 39th session part 9.

F18. The first form of a fix was a second spelling of the emission. The has_push fix used a
`strstr` needle on emitted text and missed the traced spelling; replaced by a flag set in the one
primitive that writes a push.
- 2026-09-01, 49th session part 3.
- "A needle is a SECOND SPELLING of the emission"

F19. Latent accounting bug made load-bearing by an unrelated change: `npush` went negative for
`{m,}`; [CC-CLANG]'s `has_push` gate then dropped the dispatch (a miscompile: `(?:ab|b){8,}+c`
nomatch). Found by a diff test the lane did not run.
- 2026-09-01, 49th session part 2.
- "invisible to cc's own validation because the dispatch sits OUTSIDE gate (A)'s program region"

F20. Manager's factual errors: the K35 follow-up survey was wrong about all four differential
suites; "rx_ctx vs zz_ctx" claim wrong; a 10-minute mech ETA wrong by 30 (rows run in lexical
order); the srStamp "all green" reading was a grep not a read; the test-axes red attributed to the
lane's witness wrongly; [SEL-1] declared unrowed because the lane grepped plan.md only.
Rules: read the artifact; grep `plan_completed.md` too; read the run's row order before an ETA.
- 2026-08-25, 39th session part 44; 2026-09-04, 51st session part 54 addendum 2; 2026-08-29, 45th session part 7; 2026-08-25, 40th session part 7; 2026-09-02, 50th session parts 10 and 5 addendum.

F21. Recommendation flip-flop on a default. B -> A -> B on successive measurements; the battery
(the only corpus test) found the regression the measurements missed.
- 2026-08-29, 45th session part 6.
- "withhold a DEFAULT recommendation until the battery - the only corpus test - has run"

F22. The wrong quantity measured: the [ART-SIZE] cap, the abort bound, the threshold, then the
materiality ratio each acted on a different quantity than the measurement. Four corrections on one
row; one produced a REASSURING wrong answer.
- 2026-08-29, 44th session part 5 and part 9.
- "the first where the wrong quantity produced a REASSURING answer instead of an alarming one"

F23. Instruments whose population nobody counted (K35 family): ambient-locale sort dropped 1/3
of the corpus; `head -150` sample census missed every nested directory (18 vs 159); the
classifier regexes missed jump tables; the 18-interior-optima claim was a hand-picked population.
RECURS.
- 2026-08-24, 39th session part 20; 2026-08-28, 44th session part 2 (r40 F1) and part 9.
- "a bare `sort -u` under en_US.UTF-8 merged 634 of 2,002 patterns"

F24. A magic ceiling (`lines < 2000`) that three abi events reached exactly turned a battery red;
the ceiling never measured the claim.
- 2026-08-26, 40th session part 15.
- "a magic ceiling the day's three abi events reached EXACTLY"

F25. Editorial scaffolding from a lane merged into a published spec page; plan.md briefly cited a
live bench message before the durable record existed.
- 2026-08-26, 40th session [DD-13c] part 1 ("lane srStamp's editorial wrapper merged into the published spec"); 2026-09-02, 49th session part 5.

F26. Landing passes that add corpus files or test scripts without a final full test run: isl1's
r53 landing pass added cells and a pool; the lane's last `make test` was before the pass; main's
chain found two reds. Also: rxtsource census pins not moved by two lanes; registry coverage guard
not moved (59 vs 53; 83 vs 79); a lane's own `make test` stopped early.
RECURS 5x. Rule: a landing pass that adds corpus or scripts owes test-corpus plus the section
hosting the new script on the FINAL branch tip.
- 2026-09-04, 51st session part 47; 2026-08-28, 43rd session part 5; 2026-08-30, 46th session part 9; 2026-09-02, 50th session part 11.

F27. Scope violations by lanes and by the manager: writes to the main tree during a battery, a
lane writing a journal entry into main, a lane's artificial-load test contaminating another
lane's timing, a stray log in the main root, `/tmp` use. RECURS.
- 2026-09-02, 50th session part 11 addendum; 2026-08-26, 41st session part 6; 2026-08-25, 40th session part 3; 2026-09-04, 51st session part 44.

F28. A lane started code before its design note was approved (opt4 "had started prefix_k.c
first"); a lane merged with a stale reference; a lane wrote its brief's number from memory.
- 2026-08-28, 43rd session part 2.

F29. `scripts/watchdog -m` takes BYTES; a bare number killed four rows at 5-14 MB RSS.
- 2026-08-30, 45th session part 9 ("Watchdog note (own mistake)").

F30. A check reading a stamp's ABSENCE as a discriminator broke when the stamp became
unconditional (four sites: codegen x2, parse, atomic_groups).
- 2026-08-25, 40th session part 8; 2026-08-26, 40th session [DD-13c] part 2 (the sweep found all 17 value-anchored).
- Rule: discriminate by VALUE, never by presence.

F31. An optimization's measured win came from an unmeasured side effect: the forced-VM x9 came
from a portability change ([CC-CLANG]'s frameless dispatch gate), unpredicted; the bench's flat
controls made it attributable.
- 2026-09-02, 50th session part 3 and the lesson line.
- "the biggest performance movement of the pin came from a PORTABILITY change nobody measured for speed"

F32. A design premise was wrong in a way no panel with source access caught: the island predicate
input was the LANGUAGE not the branch list; the K43 fix (b) moved the analyzer false positive to
the trail rewind (two-arm measurement refuted it).
- 2026-09-03, 51st session parts 26 and 38.

F33. A dependency between sections hid a check from a loaded battery: `test-size` declared
`test-size: test-corpus` and under `make -k -j12` was "not remade because of errors".
- 2026-08-28, 43rd session part 7.
- "the tripwire built to catch blowups would never have run in a loaded battery"

---

## (3) LESSONS STATED BUT NOT YET APPLIED, OR THAT RECUR (candidates for "apply to this project now")

L1. Completion witness for every long run (RECURS: F8, F7, F16). Every verdict must require a
"this run finished" line plus a population count; apply to any ad hoc `make` chain a lane or
manager launches. Sources: 41st session parts 3a, 7, 12; 43rd session part 5; 47th session.

L2. The "second reader" of a pin/count/abi number (RECURS 6x+: 40th pt 11, 40th pt 13, 43rd pt 5,
44th pt 8, 46th pt 9, 50th pt 11, 51st pt 47). Grep finds readers that cite the number; it does
not find readers whose text never cites it (coverage guards in other files, byte-count manifests).
Apply: derive pins mechanically from a run, and require the sections that count (registry,
codegen, rxtsource) in the delivery bar, not only the lane's own scripts.

L3. Sabotage-row witnesses expire and anchors go stale (RECURS 5x each: F12, F13). The reach
check and [SABANCHOR] exist, but same-day landings still cause UNREACHED rows. Apply: when a lane's
change removes/moves a construct, run `ONLY=<rows>` solo mech on the rows naming it BEFORE merge.

L4. Read the failure list by FILE and read guard lines before attributing a red to a known load
cell (RECURS: F11). Stated twice, applied inconsistently. Apply: a triage checklist in the battery
driver itself (print failures-by-file and guard lines unconditionally).

L5. Persisted-`cd`, chained merge+commit, and self-matching-pattern shell slips (RECURS 5x/2x/4x:
F4, F5, F6). All three are in the situation index but still recur. Candidate: a wrapper script
(or hook) that refuses `cd` in a compound with `git` and refuses a pattern that appears in its own argv.

L6. Lane liveness and message delivery (RECURS: F14, F15). The durable fix (files + WIP commits +
DO-THEN-FINISH) arrived 2026-09-06 (BOILERPLATE), after the 51st session. Evidence that the
earlier "lane self-keepalive" detour (48th session) cost tokens for no gain; carry the cache-TTL
reasoning to other projects instead of the cron itself.

L7. Do not edit an executing shell script (RECURS 4x: F3), including from a different worktree if
the script is read through a shared path. Candidate: running suites copy their scripts to scratch.

L8. Timing and load: measure the parallelism SHAPE once and fix it (F10). The project carried
"green-by-diagnosis" for K31/K32/K44 across ~20 batteries over four weeks before the shape table
(`-j4`/`PROCS=3`) retired it. Apply: when a check is red only under load, schedule the shape
measurement the first time, not the twentieth.

L9. A lane's own validation claim is a claim (F17, F18, F19). Pair every lane delivery with a
check the lane did not write (blinded corpus, critic, battery). The three miscompiles caught in
this slice were caught by something outside the lane in every case.

L10. Last-edit rule: validation must postdate the final source edit (F13 S174 "after the last
SOURCE edit"; F26 isl1; 49th-session srK38 make test). Apply in the delivery bar: record the HEAD
the validation ran on and compare to branch tip at handback.

L11. The "which quantity does this act on" error (F22) and "population nobody counted" (F23) are
the same family as the control-shares-a-source-with-what-it-controls lesson. Apply: every
threshold/cap/materiality constant is pinned by a test that FAILS at one step either side
(r42 S6, isl1's §9 pool).

L12. Withhold default recommendations until the battery has run (F21). Stated once (45th pt 6);
check whether it is honoured in later rulings.

L13. Sabotage-id allocation collisions between concurrent lanes (46th session part 7: S205 minted
by two lanes; 51st: manager arbitrates). BOILERPLATE later reserves ranges; verify the reservation
is enforced by a check, not by memory.

L14. Battery growth control: owner ruled the battery stays lean (46th pt 8); the same slice shows
san at 102-111 min and the battery at 3.5-4 h. Candidate: a per-stage budget row in the plan so
additions require a ruling by construction.

L15. Check-only evidence for a narrow change (T12) vs the full sweep: the ruling exists (46th pt
6) but later lanes still launch 14-pass sweeps; apply the scoped-pair rule in briefs.

L16. Messages to a running lane about SCOPE are unreliable (F14); the follow-up rule "scope changes
go to a fresh lane" appears later (memory `pcrec-no-addenda-to-running-lanes`). Evidence from this
slice: isl1 missed several rulings until re-sent while idle (51st session part 42).

L17. Sanitizer-axis blind spots: a test driver that links the library without the sanitizer
flags aborts the whole san loop at its fourth script (46th session part 11 "[DD-11] driver's
missing `$SANFLAGS`"); `make san` hid 15+ scripts behind one `set -e`. Apply: the san runner
should continue and summarize, and a structural check should require `$SANFLAGS` on every C-check
compile line.

L18. API/harness outages are routine (403, 529s, dropped reports): every lane brief must require
WIP commits and a resume log; a lane with uncommitted work is a single point of failure
(40th session part 2).
