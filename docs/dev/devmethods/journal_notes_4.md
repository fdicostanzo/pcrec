# Journal notes, slice 4 (fifty-first session part 60 through hundred-and-nineteenth session)

Scope: dev_journal.md from 2026-09-04 (fifty-first session, part 60, the ccd2 write phase) to the
end, 2026-10-18 (session 119, the ghostty iowait hold). About 6,000 lines, ~65 sessions. Items are
cited by DATE + session number + part/title. "RECURS" marks an item seen more than once in this
slice (the recurrence count is given where it is countable). Quotes are verbatim and short.
Session numbers are the journal's own (fifty-first ... 119); the journal calls the manager
"pcrecdev1" (later "the manager"), the bench session "pcrecdev2", the kit session "pcrecdev3".

---

## (1) PRACTICES THAT WORKED

### 1a. Subagent / lane control

P1. A read-first standing-rules file (BOILERPLATE.md) replaced long briefs: a brief names only task,
tier, deliverable. Rules accrete there when a failure recurs (detached runs, /tmp, one waiter per
worktree, mech id format, corpus lanes run full make test).
- Source: 2026-09-06, session 56 part 3, "the token-economics overhaul".
- "docs/dev/lanes/BOILERPLATE.md as the read-first standing-rules file (briefs shrink to task/tier/deliverable)"

P2. Subagent prompt caches live 5 minutes, so lanes get NO keepalive crons; a run longer than ~4 min is
the lane's LAST act (DO-THEN-FINISH): commit, write the report with the OWED numbers + log path +
completion line, launch detached, END. The manager's watcher catches completion; a fresh agent reads
the verdict. (The main session's 1-hour cache is the only one with a heartbeat.)
- Source: 2026-09-06, session 56 part 3; 2026-09-08, session 57 part 1, "DO-THEN-FINISH policy".
- "a >4-min run is a lane's LAST act — commit + report (OWED numbers, log path, completion line) first, launch in background, END"

P3. The monitoring ladder: liveness by a zero-model watcher script; mechanical follow-up by a fresh
small-context agent; mid-run judgment by a concise-brief watcher agent; merge/ruling by the manager.
Chosen because the cost problem is context size, not warmth.
- Source: 2026-09-08, session 57 part 1.
- "the fix is keeping the MONITORING context small, not keeping the big context warm"

P4. Main-session heartbeat cron every 30 minutes (two off-minute marks, :13/:43), minimal-action
prompt, because hourly ticks jitter past the 1-hour TTL and re-charge the whole context each time.
Measured token waste of the old 10-minute watchdog: ~73M cache-read tokens in two sessions.
- Source: 2026-09-05, session 55 part 1 (cadence reversed to 30 min); 2026-09-06, session 56 part 3 ("THE IRONY RULED INTO THE RECORD").
- "the watchdog existed partly to stop tasks idling/wasting and became the waste"

P5. Model tiering by task: sonnet for fact-finding, triage, docs, landing, harnesses; opus for engine
code and hard design; the manager model is not used for lanes. Opus "on the table" for engine tier
once the bench review showed it was needed.
- Source: 2026-09-08, session 57 part 3 ("STAGE 4 OPENED ... lane utf8s4 (OPUS, engine tier)"); 2026-09-22, session 76 (lane model list).
- "lanes stay Sonnet/Haiku BY DEFAULT with opus on the table when needed"

P6. Closing agents is the manager's act (TaskStop), done at delivery, with a straggler check by
/proc cwd before removing a worktree. Read-only critics are closed after the review file exists.
- Source: 2026-09-06, session 56 part 3; 2026-09-04, session 52 part 68 ("All eight idle agents were stopped with TaskStop").
- "closure is the MANAGER'S act — TaskStop explicitly; caught me preaching it with two delivered lanes still alive"

P7. Design note first, then a read-only D6 critic panel, then a revision lane, then build. The panel
finds soundness blockers no implementation control can see. Panel economics: three concurrent
read-only critics + one sonnet compile-and-apply lane with a verbatim disposition table cost the
manager four short turns.
- Source: 2026-09-23, session 78, "[VAR] D6 PANEL"; 2026-10-03, session 89 part 2 lessons; 2026-10-06, session 92 ("D6 PANEL ON STAGE 3").
- "a design lane before every build lane paid three times today — two of three round-1 items were re-pointed by evidence"

P8. Light re-check after a revision: a second, narrower panel confirms the fix round, and finds that
the fix failed "on its own axis" (r57: S0 declared three line classes while S1/S3 ruled two).
- Source: 2026-09-12, session 61, "[DD-13b.W23] chartered and DESIGN-COMPLETE in one day".
- "three consecutive revisions were each caught by their own round's instrument SWEPT WIDER than the finding's section"

P9. Critics who ADD the general form and its unlocks (with triggers), not only refutations, are valued
(owner liked it; every panel now gets one such lens). Critics write their OWN findings file because
long results truncate in the idle notification.
- Source: 2026-10-09, session 102 (memory pcrec-critics-propose-unlocks); 2026-10-05, session 91 lessons ("Critics' long results truncate").
- "have them write their own findings file"

P10. A blinded test author (D27: allowlist-filtered cell, no src/, no tests/) writes the corpus from
the goal; the manager triages "corpus-wrong vs pcrec-wrong". It keeps catching what implementation-
derived greens miss.
- Source: 2026-09-05, session 54, "the D27 UTF corpus"; 2026-09-06, session 56 part 4 (utf8s3: 462 of 506 green first run, zero divergences).
- "D27's fourth catch of what the implementation's own green acceptance missed"

P11. D27 cell hygiene must be tested both directions: cells under worktrees/ were git-readable by
upward discovery for every earlier D27 cell; fixed with an empty-repo boundary and a hygiene check
that proves the leak closed.
- Source: 2026-10-05/06, session 92, "artprep's FINDING".
- "D27 cells under worktrees/ were git-readable via upward discovery ... every earlier D27 cell had that leak, guarded only by brief wording"

P12. Fact-sheet lane (read-only, sonnet) BEFORE each refactor wave; the manager rules its open
questions in the brief; the build lane starts with settled scope. Waves ran U, 1, 2, 3, 4, 5 each
byte-neutral against a pinned branch-point binary.
- Source: 2026-09-18/19, sessions 69-71 (w2facts, w3facts, w4facts, w5facts); 2026-09-19, session 71.
- "a read-only sonnet fact sheet first (w3facts — it found the third_party generate.py path sites and APPROACH.md hunks no review source priced)"

P13. Prediction table written BEFORE any build/measurement and scored afterwards, including misses
(edge1, edge2, ccdiff1, k50 nullgate, optimpl). Misses are recorded as findings.
- Source: 2026-09-06, session 56 part 4, "[K50-NULLGATE]"; 2026-09-04, session 51 part 60 (edge2).
- "Prediction table: 6 hits, 1 partial, P3 a scored MISS (class-varying accept placement IS a nullable property — the model was backwards)"

P14. Pre-check "does this premise survive" lanes: the lane re-derives instead of inheriting
(w23impl RAN the format-reader survey and found the `NF != 15` defect alive; k60meas refuted K60's
own diagnosis from three lines of the recovery point).
- Source: 2026-09-13, session 63; 2026-09-18, session 68 ("K60 MEASURED").
- "RAN §2.24's format-reader survey instead of inheriting the lesson"

P15. Rulings and HOLD/LIFT travel as FILES the lane polls (NAME_rulings.md in the lane's OWN worktree,
`.hold`/`.lift`), because a busy lane reads messages only when it idles. A fresh lane is the reliable
carrier of a scope change.
- Source: 2026-09-04, session 52/53 (rulings file in own worktree); 2026-10-04, session 90 lessons.
- "a brief widened by SendMessage mid-run can be missed entirely ...; a fresh lane is the reliable carrier of a scope change"

P16. Verify a relayed ruling in the DELIVERABLE by grep before accepting: varmvp's one-seam-entry
ruling had been sent twice and was not applied; merging would have forced a second abi bump.
- Source: 2026-09-23, session 78, "varmvp + vartriage MERGED".
- "a ruling sent mid-lane is VERIFIED IN THE TREE by grep before acceptance (the lane's report never mentioned it)"

P17. Parallel build lanes get disjoint abi numbers, deny-bit numbers and sabotage-id ranges IN THE BRIEF;
sabotage ids serialize through the manager; the kit's reserved range is named in BOILERPLATE.
- Source: 2026-10-03, session 89 part 2 lessons; 2026-10-05, session 91 lessons; 2026-10-09, session 101.
- "Ids (abi, sabotage) collide across two sessions unless one hand allocates them."

P18. Landing is delegated: a sonnet landing/doc lane does merge/strict/index/push/prune; the manager
gives the VERDICT. A landing whose content is only suite runs is a chain script, not a lane.
- Source: 2026-10-16, session 113 ("Delegation shift"); 2026-09-19 evening ("LESSON: a landing whose content is only suite runs is a CHAIN SCRIPT, not a lane").
- "merges, doc edits and searches go to sonnet landing/doc lanes; the manager gives verdicts. Eight landing lanes ran today."

P19. wtprune: gated removal of delivered worktrees (merged, clean, quiet, no cwd, no lock, not pinned),
26-check self-test with each gate sabotage-verified; later `--force` on NAMED targets only, friendly
removal first, diff and unmerged commits saved, never rm -rf. A glob-apply removed three extra
clean worktrees once: pass the name.
- Source: 2026-10-05, session 92; 2026-10-18, session 117 ("wtprune --force"); 2026-10-10, session 106 (Prune).
- "`wtprune --apply --dir X` with no NAME also applied every other removable"

P20. A lane's stacked pipeline (each lane branches from the previous PARKED tip, merges deferred) plus
ONE battery on the tip, when each step carried its own measured acceptance. Taken as a declared
deviation from "merge-per-step" for the owner to ratify.
- Source: 2026-09-15, session 65 part 2, "THE WHOLE [DD-13b.W23] DELIVERY BUILT AND MERGED".
- "one battery on the tip answers what four serial batteries would at a quarter of the box time"

### 1b. Session management

P21. wake.md (gitignored hand-off brief) is rewritten from scratch at every pause/close and
re-written EARLY ("crash-proofing"); committed docs win on disagreement. Memory dir and wake.md do
not travel by git, so a machine move copies them first.
- Source: 2026-10-06, session 92 ("wake.md rewritten early (crash-proofing)"); 2026-10-07, session 95 ("Machine move completed").
- "wake.md (gitignored) and the memory dir do not travel by git"

P22. Journal entries are append-only; a wrong entry gets a CORRECTION that rides it (never an edit).
The D105 case: the journal said "IMPLEMENTED" for a decision that was only ruled.
- Source: 2026-09-17, session 67 (the correction text) and 2026-09-18, session 68.
- "The journal is append-only, so the original wording stands below and this correction rides it."

P23. Context discipline: reset the manager at ~35% context (owner rule), "look for session reset before
starting anything" at a natural point; /close waits for a natural point, never interrupts lanes.
- Source: 2026-09-29, session 85 (standing rules: "Reset when context is >35%"); 2026-10-11, session 108 CLOSE.
- "Reset when context is >35%."

P24. Token-economics instrumentation: two measurement lanes (tokenscan, delegaudit) quantified where
tokens go, and the owner ruled from the numbers (aggressive closure, delegate operations hard, stall
watching by script).
- Source: 2026-09-06, session 56 part 3.
- "small turns were 57% of all turns and 82% of all 5-min cache-writes"

P25. Pace to the subscription: at 89% the owner asked for one lane at a time across sessions; kit held
design panels until the weekly reset; "use em or lose em" when headroom exists.
- Source: 2026-10-08, session 100 (Pacing); 2026-09-15, session 65 (token headroom).
- "Frank asked to dial back to one lane at a time across sessions"

P26. Box clock before inference: check the box's own clock and accumulated CPU before calling anything
slow or stuck (a UTC/EDT misread manufactured a 4 h phantom stall; a Mac sleep gap poisoned wall-clock
reads; a maintenance sleep of 879 s read as a code defect).
- Source: 2026-09-15, session 65 CLOSE; 2026-09-27/28, session 83 ("pf35 ... ENVIRONMENTAL").
- "A maintenance sleep reads as a code defect under GNU timeout's wall clock. The watchdog signature is wall≈sleep length with cpu≈0."

### 1c. Inter-process / inter-session communication

P27. Durable channel between peers is single-writer files: the bench's inbox_from_pcrec/outbox files
committed as a single-file [inbox] commit; the GitHub remote is read transport; live messages are
for coordination only. Ritual: fetch, commit, push together (an unpushed inbox item stranded for
hours; non-fast-forward rejections took three tries).
- Source: 2026-09-04/05, session 53 ("THE CHANNEL, rebuilt in three rounds"); 2026-09-21, session 74 (three non-fast-forward rejections); 2026-10-09, session 101 ("I-140 was stranded locally for hours").
- "always fetch, commit and push together"

P28. Executor protocol for the peer that runs pcrec's Linux jobs: exact commands, expected counts,
report-don't-diagnose, quote-not-diagnose. A flagged discrepancy (47 vs 26) was resolved by the
manager in one line because it was quoted verbatim.
- Source: 2026-09-08, session 57 part 3 (I-59); 2026-09-11, session 60 part 2 (I-65).
- "The executor's report-don't-diagnose protocol handled it exactly as designed."

P29. Never launch a peer with `claude -p` (bills API credits and lacks the cross-session tools); after
bootstrap, tmux send-keys into a Claude session is BANNED; only interprocess messages.
- Source: 2026-09-16, session 66.
- "NEVER `claude -p` — it bills API credits, not the subscription"

P30. No laundering across sessions: a peer whose permission classifier blocked a launch stopped and
escalated to the owner; the owner unblocked it himself. A peer's relayed "ruling" is confirmed with
the owner before it is recorded (done twice, both real, both gained detail).
- Source: 2026-09-11, session 59; 2026-10-08, session 99 (Lessons).
- "pcrecdev2's permission classifier blocked the wrapper launch (it correctly stopped and escalated — no laundering on either side)"

P31. Peer-to-peer deadlock check: the kit waited for main to file R-8 (requests.md is main's) while
main waited for the kit to "send" it. Fixed by naming it in the heartbeat: it fires ONLY while waiting
on a specific peer, NAMES the awaited thing, and a peer waiting on me gets a one-line ack; never
ping an idle peer.
- Source: 2026-10-08, session 98 part 2 ("R-8 FILED ... after a DEADLOCK found by Frank's check-in"); 2026-10-09, session 101/102.
- "the kit waited for main to file R-8 (requests.md is main's, D78) while main waited for the kit to 'send' it"

P32. Bench box hand-offs are explicit windows: "box free" line goes live AND durable; the bench's
quiet gate is never loosened; every timing run on the shared box is cleared through main, which
clears it with the owner; ping the owner (never kill) if his process loads a timing run.
- Source: 2026-09-04, session 52 part 68; 2026-10-18, session 116 (Frank's standing rule); 2026-10-18, session 119.
- "every timing run on this box is cleared through main, which clears it with him"

P33. Official performance verdicts come from pcrec-bench runs on each targeted box, not from the
developer's scratch numbers (D144 add. 4); scratch numbers are labelled scratch tier everywhere.
- Source: 2026-10-08, session 99 ("D144 addendum 4").
- "official SIMD verdicts are pcrec-bench runs on each form's hardware"

P34. Mirror process rulings to the peer repos under direct owner authorization and record the single
sanctioned write outside the inbox.
- Source: 2026-09-06, session 56 part 3 ("Mirrored to the BENCH under Frank's direct authorization").
- "the one sanctioned write outside the inbox"

### 1d. Testing practices

P35. Oracle-first corpora with libpcre2 10.46 as the reference; python `re` only as a transcription
tripwire (C3 three-way verdict: python-vs-PCRE2 divergence is a counted INFO bucket, never a failure;
store-uncovered cells fail safe).
- Source: 2026-09-11, session 58 part 2 ("pyrole"); 2026-09-09, session 57 part 7 (oracle trilogy).
- "python = transcription tripwire; PCRE2-confirmed divergence → counted INFO bucket, never a failure"

P36. Oracle answer STORE: committed reference answers keyed (oracle-id, version, options,
question-hash), only the ORACLE side cached (pcrec always computes fresh), self-checking TSVs; darwin
consults the 10.46 answers without owning the reference. Replaces dlopen (which silently resolved a
system 10.42 / a Miniconda 10.37).
- Source: 2026-09-09, session 57 part 7; 2026-09-10, session 58; 2026-09-05, session 54.
- "only the ORACLE side caches (pcrec computes fresh — the asymmetry is the safety property)"

P37. Differential tiers: tier-1 EXACT agreement against the reference oracle (0 code points
attributed to drift), plus oracle-free invariants (`[^\p{L}] == \P{L}`) that catch positions both
engines share a blind spot on.
- Source: 2026-09-06, session 56 part 4 (utf8s3 cursor bug); 2026-09-08, session 57 part 3 (I-59).
- "an agreement check between two engines is blind to a construct's other POSITION"

P38. Sabotage (mutation) rows with declared reach: SAB_REACH/SAB_REACH_POP verified in BOTH directions,
a runner `NOW REACHED` check, a reach-only sweep over all rows, and per-row solo re-drives with the
exact predicted count. UNDETECTED rows are tracked as EXPECTED with a named derivation.
- Source: 2026-09-04/05 (S121 declared UNREACHED); 2026-09-26, session 80 lessons; 2026-10-05, session 91 (r1mtriage).
- "a reach-only sweep over all rows is cheap and found them"

P39. Re-aim ritual for sabotage anchors: anchors copied from `git show HEAD:<path>`; re-aims reproduce
the row's own recorded counts exactly (6/14/8) so the re-aim is verifiable; derived anchor maps
regenerated, never hand-merged; `sabotage_anchors.py` derives which rows to re-run from a diff.
- Source: 2026-09-05, session 54 (S08/09/10); 2026-10-08, session 97 (stc5land); 2026-10-07, admin1008b.
- "the three caseless rows reproducing their recorded counts (6/14/8) exactly, which is what makes a re-aim verifiable"

P40. Every new check is validated in the FAILING direction (planted violation goes red, restored goes
green) and its population has a K35 floor; zero-population is a failure, but the extractor's health is
asserted independently of the honest empty tier.
- Source: 2026-09-15, session 65 part 2 (W23-S3 arm 4); 2026-09-13, session 63 close; 2026-10-08, session 98 (several).
- "an arm deriving its population from the data it checks must fail on an EMPTY population"

P41. Population pins become FLOORS (half the measured population) with exact pins kept only for
absorbed counts (D110), and a fired control; brittleness was measured (158 to 162 under two
byte-neutral refactors) before ruling.
- Source: 2026-09-18, session 69/70 ("FRANK'S RULING ON THE PINS").
- "absorbed pins stay exact, population pins become floors (K35 wants an EMPTY population caught, not a shifted one)"

P42. Byte-neutrality sweep as a committed instrument (`scripts/emit_sweep.py`): multiple streams
(.c, .c --engine=vm, --emit-ir, composition, dumps, --emit-facts), a self-check against two builds of
the same ref, REACH floors, a built-in POSITIVE control (an arm that MUST move), and per-binary CLI
grammar probing. Read the REACH figure, not the pass count.
- Source: 2026-09-19, session 70/71 (bsweep); 2026-09-18 (w2x §5).
- "the REACH figure, not the pass count, is what makes a zero-mover result evidence"

P43. Identity gates pin a reference commit (FILEPIN) re-pinned at each abi merge; one-step zero-mover
refactors use "implement beside + both-walks oracle in both orders, then replace" (start table C2/C3,
fallback B2/B3, kit migrations), with the oracle retired when its half is replaced.
- Source: 2026-10-07, session 94 (C2); 2026-10-08, session 98 part 2 (B2/B3); kit migrations R4c-R4h.
- "implement-then-replace, ZERO MOVERS"

P44. Refactor discipline: no-mover refactors never fold in movers ("two serial no-mover refactors A / B
... movers never folded in"); every selection becomes a first-match table whose rows declare their
reads; edit sets, reader lists and sabotage re-aims are DERIVED by census, not hand-listed.
- Source: 2026-10-06, session 93 (Q4 STREAMLINE); 2026-10-09, session 102 lessons ("Hand-listed reader and check lists keep missing gates").
- "derive edit sets by census"

P45. Layered validation tiers: light targeted suites per lane (STOPS on first red), a full `make test`
on the merged tree (11 min on the Linux dev box; 100 min on the Mac), a nightly/batched battery
(strict, axes, san, alloc, lint, mech) pinned to a commit, with "consumers take batteried pins only"
(D102). Late merges PARK on their branch until the trailer.
- Source: 2026-09-16, session 66 (D102); 2026-09-10, session 57 part 8; 2026-10-08, session 98 part 1.
- "no merges to main while a battery is in flight — late deliveries PARK on their branch until the trailer"

P46. Heavy runs prefer the faster box and the box is chosen by EARLIEST COMPLETION; batched axes sweep
cut 5h45m to 95 min; Mac `make test` fell 104 to 30 min as comment-free artifacts and batching landed;
perfrun rotates -j x PROCS shapes in natural runs and classifies reds (K44-ONLY / LOAD-SUSPECT / RED-REAL).
- Source: 2026-09-25/26, session 80 (rulings); 2026-09-10, session 58; 2026-10-08, session 98 part 1.
- "Linux cut the validation from ~14h (Mac) to ~7.5h"

P47. CI is part of the loop: fit measured first (4 runs to green), then sharded 3-way from a declared
table with a set-equality control, per-section timestamps for killed runs, rebalanced on runner seconds;
the manager's wake step 0b checks CI, and CI is watched after EVERY push.
- Source: 2026-09-21/22, session 75; 2026-10-13, session 111; 2026-10-17, session 115 (Memory updated: watch CI after every push).
- "make test outgrew the 90-min job (citime: 42 -> 68 sections) -> 3-shard matrix from a declared table"

P48. Verdict of a suite = make's own `*** [...Error` lines, never "sections ran" and never a grep for
FAIL. The Linux form includes a Makefile:line prefix. A gate watcher prints those lines.
- Source: 2026-09-22, session 76 CORRECTION; 2026-10-06, session 92 (the grep missed a Linux red); 2026-09-22, session 77.
- "`sections ran:` counts sections `make -k` LAUNCHED, not sections that PASSED"

P49. Null control for timing: program-identical artifacts across the pin pair give a two-sided null
band (-5.74 to +8.46%); the bar's noise model must match the comparison's span (cross-window);
nanosecond per-call timings are never percentages (absolute delta vs base/deny floor, >=50 ms loops,
pinned Linux). Report sigma; don't wait for a quiet box.
- Source: 2026-09-23, session 77 (b1ledger, O-48); 2026-10-03, session 89 part 2 (D144 add. 1); 2026-10-09, session 102 ("Timing is directional").
- "a bar's noise model must match the comparison's span (ask the bench for a null-control band)"

P50. Two-tier acceptance (D144): alpha = make test + targeted timing per optimization (own commit, own
-fno- flag); batch gate = full Linux make test + axes + mech + san + wide bench per round; regressions
become issue rows unless wrong answer or tripwire blowup.
- Source: 2026-10-03, session 89 part 2.
- "regressions become issue rows unless a wrong answer or a tripwire blowup"

### 1e. Process (plans, decisions, reviews, tables)

P51. Plan rows with grep-able states and one enforced format (`scripts/plan_lint.sh`, 17 strict rules,
planted-violation self-test, opt-in pre-commit hook); stale `started` rows audited (true started
population 26, not the grep's 43); anchored counts (81 not-started, not an unanchored 100).
- Source: 2026-09-19, session 71 ([PLAN-AUDIT]); 2026-09-22, session 76; 2026-10-13, session 111 ([PLAN-LINT]).
- "the plan row's '102' was an unanchored grep counting 'formerly STATE:not-started' prose"

P52. Decision log (D-numbers) records ruling AND reasoning ("record the REASONING, so a future dispute
weighs the argument rather than the label"), plus addenda; open question lists go to the owner as
discussion with a recommendation.
- Source: 2026-10-16, session 113 (Lesson); 2026-09-23 onward (D119..D168 addenda).
- "Record the REASONING, so a future dispute weighs the argument rather than the label."

P53. Sibling-of-a-family lens: decision logic grows dispersed until the owner asks for the unified
table; notice siblings proactively, propose unification at ~3 members; survey the codebase for
dispersed decision families (ranked, with latent inconsistencies). D152 records why decision tables.
- Source: 2026-10-06, session 92 ("Frank's meta-observation ('forest for the trees')").
- "decision logic grows dispersed until he asks for the unified table"

P54. Standing design-note questions after four panels found the same three gaps: measurement regime,
independent control, what moves when data is regenerated; state relevance first. Briefs must list the
standing rulings the design must honour (two r3 findings came from the brief, not the lane).
- Source: 2026-10-05, session 90 part 2, "Lessons".
- "Four design panels in two days found the same three gaps"

P55. Milestone close-out ritual: compliance-refresh over the whole milestone, plan row moved verbatim to
the archive with a completion stamp, milestone-close journal entry citing each stage's merge commit;
and the standing rule "milestone completes → grep plan.md for rows naming it as a trigger".
- Source: 2026-09-12, session 61 ([M5.0] CLOSED); 2026-09-22, session 76 (backtri).
- "[DD-2/M4-CALLOUTS/M4-SUBST/DD-6/DD-11] wait on milestones that shipped"

P56. Measure the cheapest generalization of an existing mechanism before chartering a new tactic: each
critic round on reverse-inner found a new unsound case; the owner supplied the existing mechanism
(bounded reach-back = the K82 handoff), which measured 109-120% of reverse-inner's win.
- Source: 2026-10-11, session 106 interim, "Frank's redirect".
- "each critic round on rev-inner found a new unsound case: the signal to step back to an existing general mechanism"

P57. Measurement-before-build triage of costly ideas: studies marked D77 (name the measurement that
would trigger it); census lanes (compile-only, counts) before design; hand-twins verified answer-
identical over exhaustive cells before any timing; "legitimate no" results merged (LIM-2 M1/M2,
dfamin, OPT-EDGE closed, A2 bake-off dropped).
- Source: 2026-09-04, session 52 part 64; 2026-09-17, session 66; 2026-10-04.
- "we theorized and tested and made the best choice" (owner reading a legitimate-no outcome)

### 1f. Safety

P58. Kill by PID only via `scripts/safekill` (kills group + tree, audit line); NEVER `pkill -f`/`pgrep -f`
(self-match, collateral kills); watchers stopped by task id; hang/allocation risks wrapped in
`scripts/watchdog`; GNU `gnutimeout` per box.
- Source: 2026-09-21, session 74 (slip: "I stopped the first watcher with a `pgrep -f` match (house rule: never)"); BOILERPLATE additions throughout.
- "watchers are stopped by task id from here on"

P59. Untrusted installers: the bench asked the owner to run `curl ... | sh` (rustup); refused, then
institutionalized as a user-level rule, a PreToolUse hook that blocks remote-exec shapes (tested both
ways), and an auto-mode hard_deny. Shared automatically with the bench since it now runs on the same box.
- Source: 2026-10-18, session 118, "Security (Frank)".
- "Now a user-level rule (`~/.claude/CLAUDE.md`), a PreToolUse hook `~/.claude/hooks/block-remote-exec.sh` (tested both ways, live), and an auto-mode hard_deny."

P60. Look before delete: inspect the target's state before removal (a worktree held a regenerated size
log; chained status+remove destroyed it). Raw `rm -rf` and `git worktree remove` never; destructive
git on a peer checkout routed through the owner.
- Source: 2026-09-12, session 61 (lesson 4); 2026-10-07, session 94 ("BLOCKED on Frank: removing our stale Linux worktrees was denied").
- "my chained status+remove saw and destroyed it in one command"

P61. Scope mandate stated in every brief; sub-agents inherit; scratch goes only in the session
scratchpad; box facts (uutils `timeout` is slow, `grep` may be an ugrep function that skips
worktrees) are recorded in BOILERPLATE so lanes stop rediscovering them.
- Source: 2026-10-07/08, sessions 95-97 (BOILERPLATE box facts); 2026-10-11, session 107 ("/tmp is outside the mandate").
- "BOILERPLATE gained: corpus-file lanes run full make test; /tmp is outside the mandate."

### 1g. Owner collaboration

P62. Ask rulings ONE AT A TIME in plain text with a recommendation; no AskUserQuestion UI; no lettered
option menus (discuss: problem, forces, leaning); use words, not ids; answer a remark with a judgment
before turning it into work; an answer-free choice (identical answers, equal measured cost) is the
manager's call.
- Source: 2026-09-06, session 56 (UI dropped); 2026-10-08, session 99 ("Frank prefers DISCUSSION to lettered (a)/(b)/(c) option menus"); 2026-10-09, session 103; 2026-10-18, session 118.
- "an answer-free choice is the manager's call; triage question lists before relaying"

P63. Discuss a direction BEFORE launching design or revision lanes on it, and no BUILD lane without an
explicit build go (an agreed ordering is not a go).
- Source: 2026-10-11, session 108 CLOSE ("The launches were premature."); 2026-10-13/14, session 112 ("don't start build yet").
- "Discuss a direction before launching design/revision lanes on it"

P64. A ratification ask must say when the design absorbed a need its source marked tentative (D99:
the collision materialized only through the bench's optional proposals); a ratification condition must
cover WHERE a change lands, not only WHETHER its premise holds.
- Source: 2026-09-13, session 62 (D99); 2026-10-18, session 116 (r1-e1 `noipa` lesson).
- "when a design absorbs a need its source marked tentative, the ratification ask must say so"

P65. Owner's general-vs-special rule: general solutions are best; a "special-case fold" or parallel
mechanism is rejected; implement-then-replace is allowed; simplification alone qualifies a change
(D168 add. 1); a build waits on a measured need (D77).
- Source: 2026-09-25/26, session 80 (rulings: "general solutions are best"); 2026-10-18, session 118 (D168 add. 1).
- "simplification alone qualifies a change"

---

## (2) FAILURES / INCIDENTS AND THE RULE EACH PRODUCED

F1. Premature merge carried a red to main: the K50 merge happened before the lane's handback because
"idle + committed evidence" was read as a handback. Rule: take-over-on-idle requires the landing bar
RE-RUN BY THE TAKER; a handback names its validation COMPLETE.
- Source: 2026-09-06, session 56 part 2b, "CORRECTION: the K50 merge was PREMATURE".
- "'Idle + committed evidence' is not a handback; a handback names its validation COMPLETE."

F2. A decision log said "IMPLEMENTED" for a ruling that was never built (D105); found a day later by an
unrelated instrument. Rule: a decision log states a RULING; only the tree states whether it SHIPPED;
read the decision's action, not its title.
- Source: 2026-09-17, session 67 (the wrong bullet) and 2026-09-18, session 68 (found by k60meas).
- "a decision log states a RULING; only the tree states whether it SHIPPED, and nothing ties the two"

F3. Manager merged to main mid-battery (oralink); mech re-archives HEAD per row and exposed six missed
build sites. Rule (skill): no merges to main while a battery is in flight.
- Source: 2026-09-10, session 57 part 8.
- "mech's 7 flags = MY mid-battery merge"

F4. The harness (and later battery.sh, K24) compiled generated code with Apple clang since the Mac move
because bare `gcc` is clang and `CC ?=` is inert in make. Rule: source `cc_resolve.sh` everywhere; the
`ifeq ($(origin CC),default)` guard at every `CC ?=` site. THIRD clang-as-gcc instance in this slice.
- Source: 2026-09-06, session 56 part 5; 2026-09-09, session 57 part 5 (battery.sh san died); 2026-09-11, session 59 ([CC-ORIGIN]).
- "EVERY harness section had compiled generated code with clang since the Mac move"

F5. An "accepted" standing red (the darwin `nm arm_a.o` probe) hid for weeks; root cause was an
unstripped Mach-O underscore in the check, so the probe had NEVER produced a darwin verdict. Rule:
an "accepted" red is a finding nobody owns; a lane's "standing red" expectation must be checked on main.
- Source: 2026-10-05/06, session 92 (~12:30); 2026-10-06, session 93 lessons.
- "an 'accepted' red is a finding nobody owns; it hid for weeks"

F6. dlopen oracle silently resolved the macOS SYSTEM libpcre2 10.42 (and Miniconda 10.37) instead of the
reference; every dlopen oracle was affected. Rule: direct link (header/runtime version match), one
resolution point, loud skip on absent lib, oracle store for the reference version.
- Source: 2026-09-06, session 56 part 5 (U15b); 2026-09-05, session 54 (Miniconda 10.37).
- "silently — never a dlopen failure — so every expectation's provenance is stamped 10.37"

F7. A battery was launched without grepping known_issues: K54 had said in plain text that san is unusable
on the Mac; 5 h of box time re-derived it. Rule: BEFORE any heavy suite, grep known_issues.md for open
INFRASTRUCTURE entries naming its stages.
- Source: 2026-09-14, session 64.
- "K54 said 'san is unusable on the Mac' in plain text and 5h of box time re-derived it"

F8. A chain logged `echo "$(date) ... rc=$?"`, which always prints rc=0; B4 merged on false rc lines with
test-axes Terminated and recursion-identity red; main carried a red. Rule: capture rc before any
substitution; read each row's own trailer.
- Source: 2026-10-13, session 111, "MANAGER ERROR".
- "`echo \"$(date -Is) ... rc=$?\"`, which always prints rc=0 ($(date) resets $?)"

F9. "sections ran: N/M" read as a pass; the ff63ebf3 gate had test-registry red. Rule: verdict = make's
`*** [` lines (Linux form with Makefile:line prefix; first Linux form missed a red).
- Source: 2026-09-22, session 76 CORRECTION; 2026-10-06, session 92 (R4a′ landing).
- "the briefed verdict grep `\\*\\*\\* \\[test-` MISSED it (GNU make on Linux prints `*** [Makefile:646: test-…]`)"

F10. A coverage guard in a DIFFERENT file than the thing it counts went stale (registry guard pinned
limits_check's PASS count at 24; a landing made it 27); the guard's message never said FAIL. Rule: a
lane's "standalone re-run was clean" must NAME the file the suite runs (BOILERPLATE).
- Source: 2026-09-22, session 76 (regred).
- "admin1 validated limits_check.sh standalone (27/0) but never ran the DIFFERENT file that guards its count"

F11. Late discovery of landing debts: the full battery caught five items the light tier could not
(C3 pins, keyword census collision, search-pinned whole-form witness, cpset needle and manifest). Rule:
"merged with gates green at the light tier is not 'the suite passes'"; every one was a READER of a
changed surface that no grep enumerated.
- Source: 2026-09-05, session 55 part 1.
- "every one was a READER of a changed surface that no grep enumerated at the change"

F12. Check-gap class "a reader whose text never cites the number still moves with it" (abi bump readers
found by grep miss byte-count manifests, coverage pins, resource pins): 8+ instances this slice.
Rule: D94 addendum "after the grep, run the suites that count"; comment-reader census done by running
the suites; manifest rows named as a reader class.
- Source: 2026-09-18 (battriage), 2026-09-19 (w4, emitverb, evtriage3 4th/5th instance), 2026-09-21 (rel1b +11 bytes), 2026-09-23 (vartriage); first stated 2026-09-05.
- "The D94 addendum's class, fourth and fifth instances" (2026-09-19 evening)

F13. Mixed class of "wrong-cause failure message": a check's FAILURE MESSAGE is a second, undeclared claim
about the space of causes (NF != 15 blaming a TAB; dialimpl arms blaming the witness while the table was
wrong; nltriage's rc arm folding a CPU kill into a spec-section claim). Rule: failure text names what
was invalidated; split by cause.
- Source: 2026-09-13, session 63 (w23impl); 2026-09-16/17 (dialimpl); 2026-09-20 (nltriage).
- "a check's FAILURE MESSAGE is a second, undeclared claim about the space of causes"

F14. Filter self-check that `continue`d invalidated every count below it; the script asserted a false
staleness claim in its own voice and a "known red" label masked it. Rule: a filter fault must say what it
invalidated; a known-red script hides every other red in it.
- Source: 2026-09-19 evening, "evtriage3".
- "a filter self-check that `continue`s is a fail-closed gate on the whole body"

F15. TaskStop kills a lane's DETACHED background runs when launched as plain background tasks (b1triage's
chain; the lane's bonus recursion run; the 10-07 memory). Rule: arm owed chains `nohup ... & disown` or
`setsid`; confirm a run survives or ends before TaskStop.
- Source: 2026-09-18 (fixnow), 2026-09-22, session 76 CORRECTION; memory pcrec-taskstop-kills-detached-runs (2026-10-07).
- "stopping a lane kills its detached background runs; re-run or setsid before closure"

F16. Two waiters on one worktree fired on one `.lift` and ran interleaved chains (decattr + decland),
contaminating every verdict. Rule: ONE waiter per worktree; find and safekill any live waiter before
arming; never rewrite a chain.sh a live waiter may run.
- Source: 2026-10-09, session 101 (incidents); 2026-10-16, session 113 (E0 chain ran twice concurrently).
- "decattr's original waiter and decland's new one both fired on one `.lift`" (BOILERPLATE text)

F17. Chain/waiter gating bugs: slot script wrote DONE on a FATAL stage and released rq3 early; an
auto-lift gate keyed on "no run_sabotage process" matched the kit's light rows; a waiter gated on a log
mtime the other run did not write; end markers matching intermediate "COMPLETE" lines; a quiet-log
heuristic read a quiet step as done. Rule: key gates to the owning worktree's artifacts / PID / the
writer's real end line, never to a process name or quiet.
- Source: 2026-09-26, session 80; 2026-10-09, session 101; 2026-10-17, session 115 (Mistakes); 2026-10-18, session 116.
- "Key a gate to the owning worktree's artifacts, never to a process name."

F18. Mech ids passed with a suffix (`S222_`, `S237-`) made FATAL / silently-never-ran rows; a 1-second
rc=2 is an invocation error not a verdict. Mech arm `${f:-1}` default scored a MISSING log as DETECTED.
The kit's matrix runner took one id and silently ignored 34. Rule: ids passed without suffix; each row's
verdict read from its own `== mech run COMPLETE` trailer; one `score_arm` renders NO-LOG as ANOMALY.
- Source: 2026-09-17 (mechfix); 2026-09-30, session 87 lessons; 2026-10-07/08 (C3 chain); 2026-10-06, session 93 (kit silent green).
- "A 1-second rc=2 is an invocation error, not a verdict."

F19. Timeout/cap sized from a stale baseline: 90-min bound vs a 104-min suite; 3600 s vs briefed 7200;
5 h cap from a 70-min reference vs ~7.5 h; a 180-min mech cap; 7200 s axes with no headroom after B4.
Rule: size a bound from the recorded baseline PLUS growth, or measure first; darwin serial make test 3h.
- Source: 2026-09-18 (mtriage); 2026-09-11, session 60 part 2 (tt4mtime); 2026-09-25/26, session 80 lessons; 2026-10-05, session 91; 2026-10-13 (b3tri).
- "size a bound from the recorded baseline plus growth, or measure first"

F20. Watcher/monitor scripts failed repeatedly: mtime tests comparing to the last COMMIT (untracked files
kept it silent), bash-3.2 `declare -A` on darwin, BSD `find -newermt` silently matching nothing,
`pgrep -f`, a single-miss liveness test, a fresh worktree's creation-time age, report-committed firing on
the first report commit, a grep that matched its own launcher (2 h stall). Rule: watch ARTIFACTS (specific
log/trailer), key on worker liveness not log mtimes, positive-output test before trust, require >=3
consecutive misses.
- Source: 2026-09-12, session 61 lesson 3; 2026-09-19 (several); 2026-09-23 (s78); 2026-09-26, session 81 (lesson 3); 2026-10-17, session 115.
- "watcher scripts need their own syntax check AND a positive-output test before trust"

F21. Lanes idle "waiting for the notification" after a background run ends (paid idle time): repeated
~20 times (emitverb2/3 3.5 h and 2.5 h at one commit, tour1-4, edgeclose, repin3, vartriage, k64land,
s1b, chkgaps, possarms21, wingame). Rule: BOILERPLATE bans Monitor on a COMPLETION; pure run-launching
belongs in a script; the nudge-with-the-verdict-line works; lanes hand back via SendMessage before END.
- Source: 2026-09-19, session 71; 2026-09-21; 2026-09-25 lessons; 2026-09-28, session 84 ("Three lanes idled on a completion Monitor in one day").
- "a 'wait for my run' lane is paid idle time; the manager stops it at launch and watches the log by script" (2026-10-03, session 89)

F22. Lanes (and the manager) missed mid-run rulings, addenda and scope changes ~12 times (starttabrev3
never applied Q3-Q5; ssrev never saw the edge-case ruling; e0build missed scope; wingame; mscomp2 cited a
withdrawn design; lfl0 ids twice; specclean numbering). Rule: settle scope before briefing; scope changes
go to a FRESH follow-up lane; verify any sent addendum in the deliverable; "no ack = NOT DELIVERED".
- Source: 2026-09-12, session 61 lesson 1; 2026-10-06, session 93; 2026-10-09, session 102; 2026-10-12, session 110; 2026-10-16, session 113.
- "SendMessage to a busy lane delivered nothing twice (no ack = NOT DELIVERED; the missing ack was visible and I read past it"

F23. Lanes wrote throwaway files outside scope (/tmp, ~/.claude, $HOME .c, main tree): 3 lanes in one
day (2026-10-10), four on 2026-10-03, again 10-08, 10-11, 10-12. Always self-reported; once a scp landed
an archive in the MAIN tree. Rule: BOILERPLATE leads with the scope line, `mktemp -p "$SCRATCH"`,
TMPDIR to the scratchpad; scp targets use the worktree path.
- Source: 2026-10-03, session 89 lessons; 2026-10-04 part 3; 2026-09-23, session 77 (g3rec scp).
- "an absolute path in a lane's scp target must be its WORKTREE path"

F24. Manager `cd` into a lane worktree moves the session cwd for in-process lanes too and starts
commands in the wrong tree: 25+ recorded slips (09-19, 09-21, 09-25 twice, 09-26, 09-29, 09-30 twice,
10-07, 10-08, 10-09 twice, 10-10, 10-11, 10-16, 10-17, 10-18...). Rule: absolute paths and `git -C`;
every remote cd gets `|| exit 1` (a guard-less remote cd launched make test in the Linux MAIN tree).
- Source: first 2026-09-19 morning; recurring to 2026-10-18; 2026-10-07, session 94 (remote cd).
- "the manager `cd`'d into a worktree or scratch dir TWICE more; every Bash call uses an absolute path"

F25. `git add -A` / `commit -a` swept unwanted material: stray generated artifacts (zzz, zzz.h, out.c,
out.h committed by a lane), a regenerated artifact_size_log.tsv, and the manager's `commit -a` swept a
landing lane's uncommitted edits. Rule: diff-stat every commit; commit named paths while a lane works
in the main tree; a pre-commit hook.
- Source: 2026-09-18, session 68; 2026-09-14, session 64; 2026-10-16, session 113.
- "My `git commit -a` swept a landing lane's uncommitted edits into my ruling commit"

F26. Pushed a red to main by chaining `git push` after a commit with `;` or without gating on the check's
verdict: test-spec-history pushed red (2026-10-10), again a plan-row cite pushed unchecked (10-11), the
red test-codegen (10-07), one more push without its `&&` (10-12). Rule: gate every push with `&&` on the
CHECK's verdict, never on the commit.
- Source: 2026-10-10, session 104; 2026-10-11, session 106 CLOSE; 2026-10-07, session 94 close; 2026-10-12, session 109 lesson (4).
- "Chain push with `&&`, never `;`. A red test-codegen got pushed today"

F27. Line-number citations of spec/plan/source files in docs/reviews/reports turned test-spec-history or
PL14 red or went stale: in lane reports, a design note, the manager's own review file, BOILERPLATE's own
example, an evidence file with grep output. Rule: cite spec by section/paragraph number, plans by [ID];
lint every committed grep output; a staged-content pre-commit hook for the conditional spec checks.
- Source: 2026-10-09 (specnum/spectri), 2026-10-10 (speclim), 2026-10-17 (CI red on a design note), 2026-10-18, sessions 116-118 (review file; PL14 via an evidence file).
- "my own lane's evidence file broke PL14 and I merged it without the lint tree scan" (2026-10-18, session 118)

F28. CI unnoticed red: gcc-13 maybe-uninitialized under strict red 10-10..10-13; a `${TIMEOUT_BIN:-gnutimeout}`
fallback existing only on our boxes red for 5 pushes; make test outgrew the job. Rule: check CI after
every push; the skill's wake step 0b; CI portability lessons (`CC ?=`, shallow clone, apt pcre2 version).
- Source: 2026-10-13, session 111; 2026-10-17, session 115 (Mistakes).
- "CI was red from the c1017 merge ... for 5 pushes, unnoticed until Frank said so"

F29. `make`-exported variable collisions: `SHARD=1/3` exported by make silently thinned a Python script's
own job subsetting in every CI shard. Rule: namespaced variables (CISHARD).
- Source: 2026-10-13, session 111 (cishard2).
- "make's exported `SHARD` silently thinning tests/startset/vmhat_diff.py's jobs in every shard"

F30. An unreached/vacuous control: ASan blind to inlined constant memcmp (needed -fno-builtin-memcmp); an
ARTREV identity harness never drove `_in` call shapes; identity twins compare answers not WORK (two
critics found a quadratic); a census reading `--emit-ir` at default engine reached only 1,754 of 3,938
rows; a reach probe asking only whether `\p{L}` compiles. Rule: positive control per instrument; REACH
figure beside every pass count; WORK-bounded cells (hostile 1 MiB, standing 10 s cell).
- Source: 2026-09-27, session 82; 2026-10-06, session 92; 2026-10-09, session 102; 2026-09-18 (w2x §5); 2026-09-06, session 56 part 4.
- "Identity twins compare answers, not WORK: two critics found a quadratic the twins could not."

F31. The `-o` basename trap: two emitted artifacts compiled to different output names differ on the
`#include` line, so a byte-identity sweep reads 100% movers (or a size pin reads off by 2). Recorded
instances across this slice: utf8design (second), k60meas (fourth), evtriage2 (fourth), dd8 (fifth), b1ledger
(fifth), more later. Rule: one shared basename; the committed sweep handles it.
- Source: 2026-09-04 (utf8design); 2026-09-18; 2026-09-19 (dd8 §3.1, evtriage2); 2026-09-23 (b1ledger).
- "the `-o`-basename trap struck a FIFTH time" (2026-09-19, early morning)

F32. Timing bugs from drift in the measurement instrument rather than pcrec: bench scoring artifact (a
correct answer scored "wrong" when no expectation row exists); a +2-row offset in the bench's prose (all
three "facts" one mechanism); sdrv.c `caps[1][2]` overran on capture patterns and zeroed the timer
(50M-iteration calibration); a bimodal result that was the CPU governor; a bake-off pack from a dirty kit
measured half its rows; a harness leak only Linux sees. Rule: reconcile a peer's claim against its raw
transcript; treat 0.0 per-call as an error; packs carry sha256s and refuse a dirty kit.
- Source: 2026-09-20 (benchcases); 2026-09-23 (axesrec); 2026-10-03/04; 2026-09-28 (O-69).
- "treat a 0.0 per-call time as an error, not a floor"

F33. A diagnosis in a defect entry was wrong though its repro was real (K60: the "stale flag" did not
exist; 0 of 148 absorptions involved it); a mechanism named in an entry and reached by none of its
witnesses is unmeasured. Rule: test the offered diagnosis, not just the symptom (also: a fact-finding
lane classified a bench claim as the wrong sibling).
- Source: 2026-09-18, session 68 ("K60 MEASURED"); 2026-09-26, session 81 lessons (4).
- "Always test the offered diagnosis, not just the symptom."

F34. Cost-model predictions refuted by measurement: instruction counts mispredicted the winner three
times (memcmp study); S1's elision cost short subjects +40%; a per-call constant unmodelled; "popcount
of cycles". Rule: cost arguments model early exit and per-call constants; "aligned arms agree" is not
"alignment is faster"; a placement twin clears a mechanism, it does not motivate one.
- Source: 2026-09-27, session 82; 2026-09-26, session 81 lesson 5; 2026-09-28, session 83 lesson 2.
- "cost arguments must model early exit and per-call constants (F1's class)"

F35. Names/ids hidden-different: 29 renamed exports vs 12 vs 34 (counting method differs); "165≈170" was a
coincidence of magnitude, not composition; "38 A_EOL refs" was a label count; the design's 513 patterns was
a latin-1 census bug; EP2's "52 sites" = 52 lines over 44 statements; unanchored plan grep 100 vs 81.
Rule: census counts the right UNIT and is validated against an independent stamp.
- Source: 2026-09-20 (w5); 2026-09-23 (varland); 2026-10-18 (s118 Mistakes); 2026-09-26 (s1step6); 2026-09-18 (w2x).
- "a census counting the right thing can still count a different UNIT than the work item citing it"

F36. Corpus adds without full suite: adding an .rxt corpus file moves pins in rxtsource, startset AND
codegen (rev2corp, k62, s157tri, quantified.rxt); a corpus move between files (K34) broke the census with
no answer-level check noticing; a corpus file with a deliberate invalid byte broke FOUR readers.
Rule: any lane that touches the corpus runs a FULL make test (BOILERPLATE); a relocation needs the
corpus-wide census re-run.
- Source: 2026-09-23 (rxtfix, recidfix); 2026-10-07, session 94 close; 2026-10-10 (rev2corp/sstri); 2026-10-13 (cishard3).
- "Adding a .rxt corpus file moves pins in rxtsource, startset AND codegen. Run a FULL make test before merging one."

F37. Plan/ledger merge conflicts silently dropped a row ([OPT-PRECHECK-ADMIT] restored later); two lanes
both re-pinned one census and conflicted every time. Rule: after a plan.md conflict diff the ROW SET,
not the hunk; combine census deltas by mechanism at merge; never hand-merge derived files, regenerate.
- Source: 2026-09-23, session 77 (rxtfix PLAN NOTE); 2026-09-28, session 84 lessons (4); 2026-10-07/08, sessions 96-97 (stc5land).
- "after a plan.md conflict, diff the ROW SET before and after, not just the hunk"

F38. Stage-3 START-SET blocker: the `T == S` assertion refused valid patterns; found only by a
COMPILE-ONLY fuzz, while every answer differential and the earlier "0 diffs over 13.58M cells" were blind
because the population never held the shape. Rule: compile-only fuzz arms for refusal; a retracted claim
is retracted in the decision log.
- Source: 2026-10-06, session 92 (~02:30).
- "every answer differential is blind to a pattern that no longer compiles"

F39. Sleeping/clock-driven phantom failures: Mac sleep, UTC read as EDT, a box sleep gap. Rule: check the
box's own clock/CPU; run detached Mac chains under `caffeinate -s`.
- Source: 2026-09-27/28 (pf35); 2026-09-15 close; 2026-09-23 (timestamp correction).
- "detached Mac chains run under `caffeinate -s`" (BOILERPLATE rule, 2026-09-28)

F40. Heavy-suite concurrency violations: a lane launched mech + recursion identity + make test at once;
the manager ran a G2 check while B1's chain ran; the kit ran a sweep during a locked make test; two full
make tests overlapped; kit sweeps lacked numeric caps. Rule: restate ONE heavy suite at a time in every
brief; kit briefs carry a numeric sweep cap; light gates must actually be light while a suite runs.
- Source: 2026-09-26, session 81 lesson 1; 2026-10-08, session 98 (slips); 2026-10-07, session 94; 2026-10-07/08.
- "the one-heavy rule has to be restated in every brief"

F41. Premature or misdirected launches: lanes launched on an agreed ordering with no build go (E0); "The
launches were premature" (kit relaunched R-17 four times as rulings arrived); I recommended [MEASURE-SET]
M0 without checking its own trigger; a misrelay attached Frank's answer to the wrong question (D161
add. 1 rewritten); Workflow tool used without opt-in. Rule: discuss first; no build without an explicit
go; check a row's own trigger before recommending; confirm relays.
- Source: 2026-10-11, session 108 CLOSE; 2026-10-13/14, session 112; 2026-10-18, session 117 Mistakes; 2026-10-16, session 113.
- "Mistake: I launched an E0 BUILD lane on an agreed ordering; Frank: 'don't start build yet.'"

F42. Triage lane edited a worktree whose validation chain was live (voided the run); a mid-run fix
committed in a lane's worktree contaminated its armed run; a kit lane changed a tree during another's
locked run. Rule: triage briefs say "never edit a worktree with a live run"; arm the waiter only after
the lane's last commit.
- Source: 2026-10-07, session 94; 2026-10-16, session 114 lesson.
- "arm the waiter only after the lane's last commit"

F43. The peer repos' tooling mismatches: the bench's checkout detached HEAD (pull blockers root-caused
over ssh); a stranded inbox commit; I-143's vocabulary relay owed a pin late broke the bench's selfcheck
gate; first copy of an inbox note lost code spans to double-quoted ssh; same-pin rebaseline with a
different toolchain (rustc) was wrong on my side. Rule: an abi event that adds stamp VALUES ships its
bench relay AT MERGE; write inbox text via stdin; same-pin re-baseline needs the same toolchain.
- Source: 2026-09-13, session 62 close; 2026-10-10, session 105 close; 2026-10-05, session 91 (I-131); 2026-10-18, session 116.
- "an abi event that adds stamp VALUES ships its bench relay at merge (REVEND's went out a pin late and broke the bench's gate)"

F44. SendMessage to a stopped agent by name RESUMES it (mscomp woke); lanes' sub-agents hand back to the
MANAGER not to the spawning lane; critics' results truncate past ~60 lines / ~4.5k chars. Rule: do not
message a stopped agent; brief helper-spawning lanes with output-file paths; ask critics for <3k chunks.
- Source: 2026-10-12, session 109/110 lessons; 2026-10-04, session 90 lesson 1; 2026-10-18, session 117.
- "a lane's sub-agents hand back to the MANAGER, not to the lane that spawned them"

F45. Shared box issues: the bench's quiet gate held by ghostty's io_uring threads (phantom iowait/load);
host-key verification failing on a bare alias; ubuntubudu root at 100% from stale bench worktrees; a
classifier denied worktree removal as irreversible. Rule: host sessions in tmux on bench nights; use the
IP; check df before heavy runs; destructive removals routed to the owner or an allow rule (wtprune).
- Source: 2026-10-18, session 119; 2026-09-04/06, sessions 53/56; 2026-09-11, session 59; 2026-10-07, session 94.
- "ghostty's 4 `io` + 4 `renderer` threads in `io_cqring_wait` (io_uring, one pair per tab), which the kernel books as iowait/load"

F46. Specialized "known" results overturned by later measurement: the pre-existing nm red; "the pre-
existing darwin noise" bucket hid real reds; "ordering preserved" claims; the K50 charter's "theoretical"
site 2 turned live; refuted design premises in 8+ designs (utf8_design x3, dd8 §4.3, edge1 "8-edge ladder",
w3 "0 anchors", L11-F6, D111's generation estimate). Rule: lanes' first act includes testing the brief's
own premises; stop rules fire (pf35 found K69 before any edit).
- Source: 2026-09-04 (utf8design), 2026-09-06 (k50), 2026-09-19 (w3, w4), 2026-09-27/28 (pf35).
- "the stop rule in a byte-identical migration earns its keep: 3.5 found a real two-copy disagreement before any edit"

---

## (3) LESSONS STATED BUT NOT YET APPLIED, OR THAT RECUR (candidates to apply now)

R1. Manager `cd` into worktrees (RECURS 25+ times from 2026-09-19 to 2026-10-18) despite a memory rule
(pcrec-manager-never-cd-worktree) and root-CLAUDE.md rows. Candidate: enforce rather than remind, e.g. a
PreToolUse hook that rejects a Bash command whose cwd would leave the main tree, or a wrapper that
always `git -C`. Each slip was caught within one command, so cost is low, but the rule has not held in
~100 sessions.
- Source: 2026-09-19 (s71) through 2026-10-18 (s117); the s93 line: "Manager `cd` into a worktree AGAIN (memory says never)".

R2. Lanes idle on completion Monitors and miss mid-run rulings (RECURS ~20 and ~12 times). The stated
fixes (BOILERPLATE ban; "fresh lane carries a scope change"; rulings file) are still slipped by briefs
the MANAGER writes ("LAST act: make test, record its verdict" invited idling, 2026-09-27). Candidate:
make the lane brief template itself launch the detached chain via a manager-owned script, so lane prose
cannot say "wait".
- Source: 2026-09-27, session 82 ("my briefs' 'LAST act ...' wording invited idling"); 2026-09-28 ("Three lanes idled on a completion Monitor in one day"); 2026-10-16/17 ("lanes do not reliably wake on their own waiters (three stalls)").

R3. Pushing red to main by chaining without gating on the check's verdict (RECURS 4 times in 8 days,
2026-10-07, 10-10, 10-11, 10-12) and CI red unnoticed (2 episodes, 10-10..13 and 10-17). Candidate: a
pre-push hook that runs the cheap spec-history/plan-lint checks (a pre-commit hook for the spec checks was
BUILT 2026-10-18 and installed; extend to push, and have the heartbeat read the CI status).
- Source: 2026-10-10 (s104), 2026-10-11 (s106 CLOSE), 2026-10-12 (s109 lesson 4), 2026-10-17 (s115).

R4. Line-number citations breaking the tree-wide scan or going stale (RECURS 7+ times, incl. the manager's
own review file, BOILERPLATE's own example, an evidence file). The pre-commit spec hook now exists but the
class was still breaking CI hours before it was built.
- Source: 2026-10-09 through 2026-10-18 (specnum, speclim, citri, s116, s117, s118 PL14).

R5. "Second reader class": a changed surface moves a reader that never cites its name or number
(RECURS 8+; D94 addendum, battriage, evtriage3, rel1b, vartriage...). Stated fix = run the suites that
count; but landing lanes keep validating with light targets and missing readers (k7980: "a lane's
light-target green, measured BEFORE a main merge, does not cover the merged tree"). Candidate: make the
landing bar mechanical (a derived reader census per abi bump, not a hand-run list); already partly
done via emit_sweep + derived edit sets.
- Source: 2026-09-05 (s55), 2026-09-19 (s71), 2026-09-30 (s88 lesson), 2026-10-09 (s102 "Hand-listed reader and check lists keep missing gates").

R6. [MECH-REACH]/vacuous controls (RECURS: seventh instance 2026-09-22; nine UNREACHED rows 2026-10-13;
S806/S807 "validated by plant" claim false 2026-10-11; S265/S267/S271 silently UNREACHED after G1; S157
and S636 detection gaps). Stated fix = SAB_REACH and failing-direction runs. Gap: full mech has not been
run for weeks at a time ("no full mech run had completed since 08-30", found 2026-10-05).
- Source: 2026-10-05, session 91 (r1mtriage: "7 of 10 had been stale since 09-20..09-29 because no full mech run had completed since 08-30"); 2026-10-13, session 111.

R7. Timeout/cap sizing from stale baselines (RECURS 5 times). Candidate: store measured per-stage walls
in the ledger (perfrun/ttune exists) and derive caps in chain scripts from it with a growth factor.
- Source: 2026-09-18, 09-11, 09-26, 10-05, 10-13.

R8. Watcher scripts that false-alarm or stay silent (RECURS 8+). Candidate: one committed, tested
watcher (positive-output test, >=3 misses, artifact keyed) used by every skill and lane instead of
bespoke scratch scripts.
- Source: 2026-09-12 (s61), 2026-09-19, 2026-09-23, 2026-09-25/26, 2026-09-26 (s81 lesson 3), 2026-10-17.

R9. Chain-script bugs (RECURS 6+: rc capture, mech id suffix, DONE on FATAL, interleaved waiters, a log-
archive glob moved a chain script, mid-chain DONE marker deadlock when superseded). Candidate: a single
committed chain runner with the stage/rc/trailer protocol (partly done: scripts/perfrun, battery.sh,
the kit's slot scripts) and a rule "supersede = write the marker".
- Source: 2026-09-30 (s86 lesson 8), 2026-10-09 (s101), 2026-10-13 (s111).

R10. Lanes write outside scope (/tmp etc.) at least 8 times; BOILERPLATE line made louder three times
(2026-10-03, 10-04, 10-10). Candidate: enforce with TMPDIR set to the scratchpad in the spawn environment
or a hook, as with remote-exec.
- Source: 2026-10-03 (s89), 2026-10-04 (s89 part 3), 2026-10-10 (BOILERPLATE: "three lanes in one day").

R11. -o basename trap (6+ recorded instances): the durable fix is "a shared fixture rather than another
entry" (stated in utf8design_report, repeated by k60meas), and emit_sweep handles it, yet hand-written
sweeps and size pins keep hitting it.
- Source: 2026-09-04 (s53, "which the report argues means the durable fix is a shared fixture"), 2026-09-19.

R12. Gate reading mistakes (sections ran; grep FAIL; log summaries cut at 300 columns; stdout-only pipe
masking rc; `| tee` masking exit codes; counting the first sub-binary's summary): RECURS 8+. The stated
rule is in root CLAUDE.md but each new script re-learns it. Candidate: one shared "read verdict" helper
used by all drivers.
- Source: 2026-09-22 CORRECTION, 2026-09-18 (waveu PIPESTATUS), 2026-09-30 lesson 3, 2026-10-11 (flagacc mech core arm scraping first sub-binary).

R13. Two lanes / two sessions taking the same abi number, deny bit or sabotage id (RECURS: S273 x2, S674/S675,
nullanch2 vs advnorm abi 67/68, c3/r1 abi 56 x3, S169 duplicate). Fixed by assignment in briefs; still
relies on manager discipline. Candidate: a reservation file the lanes must read (BOILERPLATE reserves the
kit's range; extend to abi numbers).
- Source: 2026-10-03, 2026-10-08, 2026-10-09, 2026-10-07 (S169).

R14. Heavy-suite concurrency violated 6+ times (manager G2 during B1's chain, kit sweep during a locked
test, two make tests). The rule "ONE heavy suite at a time" and the suite lock exist; sweeps and censuses
are not under the lock ("three validation chains on the Mac drove load to ~80-100 — sweeps and censuses
need throttling too").
- Source: 2026-10-03 (s89 lesson 3), 2026-10-08, 2026-10-07.

R15. Premature/ungated work: recommendations without checking the row's trigger; builds started without an
explicit go; designs launched before discussion; relayed rulings misattributed. The owner has corrected
this at least 4 times in 3 weeks (2026-10-11, 10-13/14, 10-18 x2).
- Source: 2026-10-11 (s108), 2026-10-13/14 (s112), 2026-10-18 (s117 Mistakes).

R16. Hand-kept lists/masks/pins that drift (rx_info.flags strategy mask: the 4th incident, K92; the
CC ?= idiom in six Makefiles; EP2 floors; shard weights; hand-kept sabotage populations). Stated rule:
derive from the single source (axes.def, D111). Already paying off (kit's memfn-simd masked with no hand
bits "on day one"), but the pattern still occurs wherever a table is not yet the source.
- Source: 2026-10-06, session 93 (flagbits); 2026-09-11, session 59 ([CC-ORIGIN]).

R17. Controls that share a source with what they control / instruments that confirm their own premises
(RECURS in every panel: K60's own repro, "T=S" population, FIRSTSET witness whose answer is the same
under both hypotheses, simulator of one pass of a two-pass engine, bench's quiet gate). Stated in
learnings §3 and memory pcrec-check-design-lessons; now also a standing design question. Keep applying
as a gate on new instruments.
- Source: 2026-09-22 (fsreconcile), 2026-10-05 (s91 lesson 3), 2026-10-06 (ss3 panel).

R18. Wall-time growth of the validation loop: the owner stated "as soon as we speed up testing battery we
add something to it that brings it back to where it was ... 4ish hours for awhile now" (2026-09-04);
[TT-13] mech tiering was filed "for later"; make test grew 38 to 73 sections, CI had to shard, mech rows
double per merge. Partially applied (TT-MECHPAR slot pool, batching, perfrun, sharding); the tiered mech
by cadence (per-merge touched rows, full matrix scheduled) is still unbuilt.
- Source: 2026-09-04, session 52 part 62; 2026-10-09, session 101 (TT-MECHPAR); 2026-10-13, session 111 (CI shard).

R19. "Pre-existing"/"expected"/"accepted" labels that mask other reds (nm probe for weeks; "known red"
script hides filter faults; K44-ONLY class; "standing darwin red"): RECURS. Rule stated: check the label
against main and the failing direction. Keep: every standing red has an owner row and expiry.
- Source: 2026-10-06 (s92 ~12:30), 2026-09-19 evening (evtriage3).

R20. Reading a peer's/lane's numbers without the raw artifact (bench prose offsets; lane report claiming
code comment lost the reason; a lane claiming "validated by plant" with unreached witnesses; mid-lane
"green" before a main merge). Stated: quote-not-diagnose, reconcile against transcript. Candidate: make
the lane report template require the exact command + log path + completion line for each claimed number
(partly in BOILERPLATE "OWED").
- Source: 2026-09-23 (axesrec), 2026-10-12 (a5inv), 2026-10-11 (l1tri re-aim of S806/S807).

R21. Debt created by "success breaks the fallback witnesses": REVEND and START-LANDING moved witnesses off
sabotaged sites (nine UNREACHED rows), size-rung witnesses started fitting. Stated lesson: "brief build
lanes to re-aim rung witnesses with the new deny flags" (2026-10-10). Not yet a checklist item in the
build-lane brief template.
- Source: 2026-10-10, session 105 close, lesson (3); 2026-10-13 (mechwit).

R22. The owner's recurring structural observation that decision logic disperses (start table, fallback
tables, prior-cost unify, decisions survey; "forest for the trees" 2026-10-06) means each new feature
should ship its row-table form from the start; the standing D6 lens exists but dispersal was found in
~13 families by survey, so any NEW selection written as if/else is a repeat.
- Source: 2026-10-06, session 92; 2026-09-28/29, session 85 (standing rule: "Every selection is a first-match predicate-row table, listable, with no if-then spiderweb").
