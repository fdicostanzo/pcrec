# [ENG-PGO] — full plan.md row text

Moved out of docs/dev/plan.md on 2026-10-12 ([PLAN-LINT] step 2, lane plclean): a plan row over ~5 KB is a design document in disguise (docs/dev/reviews/plan_triage_2026-10-12.md, canonical-format rule 4). The row in plan.md keeps a compact charter and the current status and points here; the text below is the row VERBATIM as it stood at the move (indentation removed). The plan.md row is the status of record from the move on; this file is the long-form charter and history.

- [ENG-PGO] STATE:not-started (under [OPTLOOP] candidates per D137) — (CROSS-NOTE 2026-08-29 19:4x, Frank on [OPT-4]'s default: the count-collapse decision "sounds like the kind of thing that analyzing the exemplar file with a profiling version of the pattern would answer" — a second PGO-informed selection point beside [OPT-A]'s rarest byte: the findings file's subject profile (candidate-start density, run lengths at the repeat) decides exact vs collapsed per pattern; the static knee-128 stays the profile-less default.) (CROSS-NOTE 2026-08-29, Frank: the FINDINGS FILE is an .rxt — a `freq <name>` DATA block (a byte-frequency table) that a target's config references; docs/design/dd13_format/frank_inputs.md 2026-08-29, usecases_and_outline.md §6.5; blocks on [DD-13b] wave 2/3.) D83 (2026-08-28) RULES THE SHAPE: exemplar analysis runs OUTSIDE pcrec, once per file, delivering a FINDINGS FILE pcrec accepts; FILE-GENERAL findings (byte frequencies etc., pattern-independent, one exemplar serves many patterns) and PATTERN-SPECIFIC findings (a statistics-recording special compilation, built only for a specific question, later) are two result files and two builds. The bench's [B11.1] presence counts are the first exhibit. FIRST CONCRETE QUESTION for the profile attachment (Frank, 2026-08-25 ~21:2x, at the [OPT-1] two-tier ruling): the tier design is a BET that the fast tier holds the overwhelming majority of real calls; a `--profile` variant run over an EXEMPLAR subject file would put a number on it — the escalation count (FRAMES → deep tier) per call, per pattern, per subject class — and is the trigger D79 names, made concrete: build the profiler when the loop needs this number, and this is the number. CHEAP FIRST STEP (srTier, 2026-08-25): the `-DRX_TEST_TIER_HOOK` build of a tiered artifact already counts escalations per call — a driver over an exemplar subject file yields the escalation rate WITHOUT the profiler; charter that as [OPT-1]'s follow-up measurement before any profiler design. (Cross-note continues.) — CROSS-NOTE (Frank, 2026-08-24, thirty-ninth session, direction not decision): the `--profile` emission mode below gains a SECOND CUSTOMER — the post-spine pcrec-bench OPTIMIZATION LOOP (journal 2026-08-24 direction note): a PROFILE ATTACHMENT on a compiled pattern that says where the matcher spends its time BY SECTION (prefilter scan, skip loop, VM attempt, per rung) and, where possible, in smaller increments, run over a variety of scenarios, to guide optimization PRIORITY — `--trace` is the debugging tool, the profile is the optimization tool. Design starting points (manager, same day): time attribution needs cycle deltas (`rdtsc`/`clock_gettime`) at the section boundaries the emitter already names, not counts alone; the computed-goto labels are natural fine increments (count + cycles per label = a per-construct profile with no `perf`/symbolizer), and can carry the pattern offset the [V-H] trace-enrichment note wants; the profile struct is read through an `rx_info`-shaped accessor; the artifact stamps that it is the profile variant (identity gate: the default artifact is byte-identical across the axis). Same [V-H] namespace as D71.1's counter axis — a second diagnostic axis is the trigger D71 names for designing the GROUP rather than the flag. PROFILE-GUIDED GENERATION (Frank,
  2026-08-16, twenty-seventh session — promoted from the parenthetical
  inside [SIMD-META] to its own row at his ask; the SIMD-META exemplar-axis
  mention now points here). TWO NAMED CUSTOMERS as of 2026-08-17 (D53
  addendum): (1) [ENG-THIN]'s clamp-cost tuning; (2) HYBRID-VS-VM-ONLY
  ENGINE SELECTION per pattern — D53 killed the runtime length branch
  (the deciding variable is match OFFSET, unknowable pre-search), but
  the offset DISTRIBUTION is a static workload fact an exemplar file
  exposes; preferred form is pure PGO (build both variants, run the
  exemplars, keep the measured winner — absorbing per-attempt-cost
  effects no distribution model sees), with OS-0 named entry points
  for mixed/unknown workloads. The idea: compile a pattern exactly as today,
  but with an opt-in `--profile` emission mode whose matcher TRACKS HOW IT
  RAN on the user's exemplar inputs — a PROFILE, not a trace: counters at
  the observation points the emitter already names (D46 stamp points,
  DD-8's tracer sites; same structural constraint — derived from the
  structure the emitter walks, never a parallel description). Stats out
  (candidate-start density, prefilter hit/miss, per-arm hit distribution,
  iteration-count histograms per quantifier, match/fail mix, subject byte
  frequencies), then a RECOMPILE-WITH-STATS channel feeds them back as
  generation inputs. SCALAR CUSTOMERS EXIST — this row is not
  SIMD-contingent: alternation/trie arm ordering by hit frequency;
  prefilter literal choice by measured-rarest byte (scalar memchr benefits
  identically to any SIMD scanner); the §8.1 capture-walk sink knob
  (eager/n-step/accept-time is a match/fail-mix question); [M4.6] engine
  selection; step-budget sizing near K23-style boundaries. RELATION TO
  F-1/D18, stated so the tension is on record as a resolution: per-pattern
  adaptive choices keep getting deferred because an axis must earn itself
  with a measurement — PGO is the EARNING MECHANISM, the standing vehicle
  for every deferred adaptivity question ([ENG-CLAMP], adaptive K, arm
  order), so those rows cite this one instead of re-inventing a
  measurement channel. SEQUENCING: design sketch is panel-eligible any
  time (thinking is cheap); implementation AFTER the M4 spine closes and
  WITH [BENCH-1] (the profile without the bench is a dial with no meter —
  BENCH-1's prioritizer is also this row's proving ground), BEFORE the OPT
  waves it would guide. (gate re-pointed 2026-09-22: [BENCH-1] folded
  into [OPTLOOP]; the proving ground is now an [OPTLOOP] cycle's own
  analysis, e.g. docs/dev/optloop/cycle1_analysis.md, rather than a
  standing BENCH-1 prioritizer) The stats interface is designed scalar-first;
  later SIMD backend variants ([SIMD-META] hypothesis 2's density/
  statistics dependence) consume the SAME channel — which is exactly the
  "best non-SIMD approach, then backend variants on top" architecture
  Frank ruled.
