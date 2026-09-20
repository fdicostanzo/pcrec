# [TOUR-1] lane report — pcrec_emit_vm reads at three altitudes at once

Branch `lane/tour1` (worktree `worktrees/tour1`), branched from main
`c37d7338`; the CODE branch point is `78058db7` (same tree — `git diff` over
`src cli lib tests scripts` between the two is empty, verified before the
first edit). Design record: `docs/dev/reviews/2026-09-20-frank-tour.md`
[TOUR-1]. Prior art in the same file: `docs/dev/lanes/tour2_report.md`.

Six commits, one per step, each independently `make`/`make strict` clean with
anchors at 285/285:

| commit | step |
|---|---|
| `af436a4f` | step 1 — `vm_init` |
| `5c026a91` | step 2 — `vm_plan` + `vm_plan_entry`, and the seams |
| `6153fc51` | step 3a — `vm_emit_stamps` |
| `84307935` | step 3b — `vm_emit_storage` |
| `af4d41c6` | step 3c — `vm_emit_search_body` |
| `56b1ad7e` | step 3d/3e — `vm_emit_entries`, `vm_emit_epilogue`, and the top level |

`pcrec_emit_vm` is now its four declarations and NINE CALLS:

    vm_init(&v, cx, root, &g);
    vm_plan(&v, root, &pl);
    vm_plan_entry(&v, &pl, &en);

    pcrec_emit_prologue(cx, &g, v.ncaps, &pl.bufs);
    vm_emit_stamps(&v, &pl, &en);
    vm_emit_storage(&v, &pl);
    vm_emit_search_body(&v, &g, &pl, &en);
    vm_emit_entries(&v, &g, &pl, &en);
    vm_emit_epilogue(&v, &g, &pl, root);

Three that DECIDE and emit nothing, six that WRITE and decide nothing. That
split is stated in the rewritten `pcrec_emit_vm` header and is the property
that makes "a stamp cannot disagree with the code it describes" structural
rather than a habit each stamp's own comment has to restate.

## 1. The function list, with line counts

Measured with a brace-depth walk and a comment/string-aware line classifier
(`code` = a line with any token outside a comment; a line inside a string
literal counts as code). `hdr` is the function's own header comment.

| function | span | code | comment | blank | hdr |
|---|---:|---:|---:|---:|---:|
| `vm_init` | 211 | 48 | 156 | 7 | 16 |
| `vm_plan` | 312 | 124 | 178 | 10 | 19 |
| `vm_plan_entry` | 165 | 31 | 132 | 2 | 12 |
| `vm_emit_stamps` | 516 | 135 | 377 | 4 | 20 |
| `vm_emit_storage` | 483 | 274 | 198 | 11 | 19 |
| `vm_emit_search_body` | 780 | 358 | 405 | 17 | 21 |
| `vm_emit_entries` | 251 | 144 | 97 | 10 | 19 |
| `vm_emit_epilogue` | 86 | 44 | 36 | 6 | 14 |
| `pcrec_emit_vm` | 17 | 15 | 0 | 2 | 26 |
| **before, `pcrec_emit_vm`** | **2,808** | **1,106** | **1,643** | **59** | **15** |

**A number the brief's framing did not predict, and it is worth stating
plainly: the FILE got longer, not shorter.** 12,467 -> 12,728 lines; code
4,917 -> 5,016 (+99: nine signatures, nine preambles, the publication block
and the nine call lines) and comment 7,168 -> 7,310 (+142). The essay pruning
removed 73 comment lines; the nine [HDR-2] headers cost 166 against the one
15-line header they replace, so +151. The brief says the pruning "is what
actually shortens the file"; measured, it does not, and the headers are why.

What DID shorten is the READ, which is the thing `2026-09-20-readability-
experiments.md` §3 measured: the term that put `pcrec_emit_vm` in the read
closure of 122 of 182 historical commits is 2,808 lines -> 17, and the
largest function in the file is now 780. A reader landing on the stamps no
longer has the plan and the entries in scope.

## 2. THE DESIGN QUESTION: which locals cross the seams

Answered by MEASUREMENT before any edit, tour5's method: every one of
`pcrec_emit_vm`'s 44 top-level declarations was located by a brace-depth
parse, and its reads counted per candidate section with comments and string
literals stripped (so a name appearing in emitted text or in an essay does
not count as a read). The table that decided every row below is reproduced
at the end of this section.

**Into `Vm` (4 fields).** The rule applied: `Vm` carries what the WALK reads
and writes, and what the emitted program turned out to CONTAIN. A local
qualifies only if it is that kind of fact AND crosses a seam.

| local | reads, by section | where it went | why |
|---|---|---|---|
| `root_minw` | init 1 (decl), stamps 2, search 1, epilogue 2 | `Vm.root_minw` | a planned fact three phases apart read; `pcrec_minw(root)` is a property of the pattern, settled in `vm_init` |
| `ncaps` | init 1 (decl), prologue 1, epilogue 2 | `Vm.ncaps` | same shape; it is the artifact's REPORTED capture count, a sibling of `ngroups` which `Vm` already holds |
| `has_push` | stamps 4, search 4 | `Vm.has_push` | it is what the emitted program turned out to contain — the family of `emitted_push`/`emitted_set`, which already live there. Its own comment's whole argument is ONE bool for three readers, so a per-phase struct that only two phases saw would have re-opened exactly what it closed |
| `prefn != NULL` | search 7, epilogue 1 | `Vm.emitted_prefilter` | same family: "a `<prefix>_prefilter` pair was written". Deliberately NOT re-derived from `job->fit.prefilter` — the listing's own neighbouring comment records those as different questions |

**Into `VmPlan` (13 members), returned by `vm_plan`.** The `VmCaps`
precedent, which it CARRIES WHOLE rather than duplicating: `caps`,
`nstate`, `bufs`, `frame_fields[8]`/`trail_fields[4]` with their two counts,
`fast_frames`/`fast_trail`, `tiered`, and three built-once spellings
(`frames_sentinel`, `mrl_param`, `gst_param`).

**Into `VmEntry` (4 members), returned by `vm_plan_entry`:** `shape`, `ai`,
`ai_body`, `fwd_entries`.

**Why TWO structs and not one.** They are decided from different inputs. The
plan is a function of the pattern's measured `Cost` and the caller's knobs;
the entry rung is a function of what the emitted program turned out to be —
its own byte count and whether it touches storage. Folding them would make a
reader asking "what shape are the entries" read the capacity policy to find
out, and would have put `VmPlan` at 17 members, which is the bag the brief
rules out.

**`VmPlan` is a TRANSPORT, not a namespace,** and this is the one place the
design deferred to an existing ruling rather than deciding fresh. The file
already records, over `vm_plan_capacities`, that `bt_frames`/`ceiling` and
their four siblings are read at ~60 sites and that spelling them `caps.x`
"would buy a reader nothing while rewriting text sabotage rows sit on". So
each phase unpacks the two or three members it uses into the local names its
body already spells, and no phase body's arithmetic changed. That decision is
also why the diff is as small as it is and why only 17 sabotage rows moved.

**Read off `Vm` instead of carried (4).** `nguard_total`, `nlow_total`,
`nmark_total` and `nrev_total` were locals that `pcrec_emit_vm` ALREADY
mirrored into `v` ten lines after computing them. The later readers now read
`v->`, which removes four seam crossings for nothing: the local was a second
spelling of a field, not a second value.

**Stayed local, measured single-section (13).** `caps` (plan), `snap_before`/
`snap_after` (plan), `nctr_total`/`nlookmark_total`/`nlookpos_total`/
`nsplice_total` (plan), `touches_storage`/`may_attr`/`may_fwd` (the rung
decision), `sentw` (storage), `reset_call_top`/`prefn`/`accept_tr`/`fail_tr`/
`exhaust_tr`/`retry_adv`/`retry_win` (search), `mguard` (entries).

**The measured seam table** (reads per section, comment- and string-stripped,
at the branch point; sections as extracted):

```
local            decl  init  plan  prolog stamps storage search entries epilog
root_minw           0     1     0      0      2      0      1      0      2
ncaps               0     1     0      1      0      0      0      0      2
nstate              0     0     4      0      4      0      0      0      2
caps                0     0     7      0      0      0      0      0      0
bt_frames           0     0     6      2      0      0      0      0      4
trail_frames        0     0     7      0      0      0      0      0      2
ceiling             0     0     2      0      0      0      0      0      4
budget              0     0     2      1      1      0      0      0      3
work_budget         0     0     2      0      2      2      1      0      1
has_budget          0     0     2      1      1      1      2      0      3
frame_fields        0     0     3      0      0      1      0      0      0
trail_fields        0     0     3      0      0      1      0      0      0
nframe_fields       0     0     2      0      0      1      0      0      0
ntrail_fields       0     0     2      0      0      1      0      0      0
bufs                0     0     8      1      0      0      0      0      1
fast_frames         0     0     2      0      1      0      0      0      0
fast_trail          0     0     2      0      1      0      0      0      0
tiered              0     0     2      0      1      2      0      3      0
frames_sentinel     0     0     1      0      0      0      0      2      0
has_push            0     0     0      0      4      0      4      0      0
touches_storage     0     0     0      0      2      0      0      0      0
may_attr            0     0     0      0      2      0      0      0      0
may_fwd             0     0     0      0      5      0      0      0      0
shape               0     0     0      0     15      0      0      0      0
ai                  0     0     0      0      1      0      5      2      0
ai_body             0     0     0      0      1      0      1      0      0
fwd_entries         0     0     0      0      1      0      0      4      0
sentw               0     0     0      0      0      6      0      0      0
mrl_param           0     0     0      0      0      1      1      0      0
gst_param           0     0     0      0      0      1      1      0      0
reset_call_top      0     0     0      0      0      0      2      0      0
prefn               0     0     0      0      0      0      7      0      1
accept_tr           0     0     0      0      0      0      4      0      0
fail_tr             0     0     0      0      0      0      3      0      0
exhaust_tr          0     0     0      0      0      0      3      0      0
retry_adv           0     0     0      0      0      0      4      0      0
retry_win           0     0     0      0      0      0      3      0      0
mguard              0     0     0      0      0      0      0      5      0
snap_before/after   0     0     5      0      0      0      0      0      0
nctr_total          0     0     4      0      0      0      0      0      0
nlookmark_total     0     0     4      0      0      0      0      0      0
nlookpos_total      0     0     4      0      0      0      0      0      0
nsplice_total       0     0     4      0      0      0      0      0      0
nguard/nlow/nmark   0     0     4      0      0      0      0      0      1  (each)
nrev_total          0     0     4      0      0      0      3      0      0
```

### 2.1 Two findings the table produced that the brief's candidate list did not

**(a) The entry-rung decision was in the middle of the stamps and emits
nothing.** `has_push`, `touches_storage`, `may_attr`, `may_fwd`, `shape`,
`ai`, `ai_body` and `fwd_entries` were all declared BETWEEN stamps — 148
lines of pure decision with stamp emission on both sides of it. Left there,
`vm_emit_stamps` would have had to RETURN four values to the two phases
downstream, which is a stamping function that also decides the entry shape:
the exact altitude mixture this row exists to remove. It moved wholesale into
`vm_plan_entry`, which now runs before the first stamp. Byte-neutral by
construction (it emits nothing) and verified so.

**(b) `mrl_param`/`gst_param` were a seam the brief's candidate list did not
name, and the build found them.** They are the MRL-ceiling and `\G` parameter
SPELLINGS, built in the storage section and read by the matcher's own
signature one section on. Their own comment says the declaration, the
definition and the three call sites read ONE string so that a rename cannot
leave one behind — which rules out re-deriving them in the search body. They
joined `frames_sentinel` in `VmPlan` under a named group ("three spellings
built once, because several phases write each of them"), which is the
justification `frames_sentinel` already carried alone.

## 3. The essays

Pruned per `coding_guide.md` §4.2 — invariant and why-not-the-alternative
stay, HISTORY goes to docs with a pointer, every MEASURED cell kept verbatim.
Only essays in code this lane MOVED were touched.

| essay | before | after | what went, and where |
|---|---:|---:|---|
| `[DD-14.EMPTY]` root minimum width | 53 | 26 | the pass-order narrative and a retracted premise — **MOVED to `docs/dev/plan_completed.md`'s [DD-14.EMPTY] row** as a marked `[TOUR-1] ADDENDUM`, since neither lived anywhere else in `docs/` |
| RULE H3's three prefilter conjuncts (`[M6.4.2]` / `[M6.6.2]` wave E / `[OPT-4]`) | 102 | 74 | nothing deleted: the shared mechanism (the prefilter answers for a SUPERSET language, so H1/H2 survive and the span END does not) was stated three times and is now stated once, with the three conjuncts as a list under it |
| the entry-rung rationale (`[CC-DIFF]` STEP 1(a) + STEP 2) | 82 | 67 | two blocks that each stated the frameless gate, gcc's computed-goto refusal and the SAME three measured FRAMED cells; now one |
| `has_push`'s derivation (`[CC-CLANG fix]`) | 27 | 24 | the "THE DERIVATION MOVED UP HERE" paragraph, whose content is now the function's own header |

**Every measured cell survives**, and they are the reason the pruning stopped
where it did: `(?>a|ab)c|abcd` on `"abcd"` = (0,4) against the uncut twin's
(0,3); 122 refuting cells over 17,640 and 114 cells across 42 patterns;
`((?:a(?!q)|aq)(?:xy){0,4}q)` on `"aqq"` = (0,3) against 2, with 8 of 45 and
16 of 30; 221 of 244 counted-repeat hybrids; 1,1,0 against
PCREC_MINW_MAX = 2^40 on leftrec.rxt + mrl.rxt's three cells; 4 of 2,568
tests/ pattern lines at the ceiling, all call-bearing; isl1's x2.58 -> x6.51
replication pricing; the 0.611 `dig-upto-16` cell, the 0.599 bench median and
the three FRAMED cells 0.990 / 0.954 / 1.032.

**THE FACT RELOCATED, precisely.** `docs/dev/plan_completed.md`'s
[DD-14.EMPTY] row gains one marked addendum carrying (a) that
`pcrec_callgraph_build` now runs BEFORE `pcrec_select_engine` since
[DD-14 wave G], with the who-reads-the-memo-and-when enumeration that makes
the reorder sound, and (b) the retracted premise — the emitter's comment once
defended the move by claiming `pcrec_possessify` calls `pcrec_minw`, and
`src/opt/possessify.c` never calls it at all. The second is recorded rather
than deleted precisely so it is not re-derived.

**What was NOT pruned, deliberately.** `vm_emit_stamps` still reads 377
comment lines under 135 code lines, the worst ratio left in the function. Its
blocks were read and they are not history: each says what a stamp's value set
is, why it is family (a) or (b), where it is placed and what a consumer may
bucket on. Pruning them to hit a ratio would be the perversion
`coding_guide.md` §4 warns about by name. Named here as a deliberate
non-action, not an oversight.

## 4. Sabotage anchors

285/285 resolve at every commit, including the final tree. **17 rows / 20
anchor sites were re-aimed**, all in `src/gen/emit_vm.c`: S41, S63, S85, S88,
S140, S141 (both sites), S144, S155, S164, S169, S179, S182 (site 2), S183,
S217 (site 1), S224, S225, S226.

**One decision removed most of the churn.** A phase function takes `Vm *v`,
so every `v.field` in the moved text becomes `v->field` — and the tripwire
matches anchor TEXT, so every anchor containing `v.` breaks. Rather than pay
that once per extraction (S169 alone would have moved twice), step 1 gave
`pcrec_emit_vm` `Vm vm; Vm *v = &vm;` so the whole remaining body was already
spelled `v->` from the first commit onward. Each row was therefore re-aimed
ONCE for the whole wave. Step 3's five extractions moved code at the same
indentation (function-body top level to function-body top level) and broke
NOTHING; the only later re-aims were S179/S183 for `g.` -> `g->` when
`vm_emit_entries` took its `GenNames` by pointer.

**Intent re-verified in two ways.**

*(i) Mechanically, for all 17.* Every re-aim is one member-access
substitution applied identically to SAB_BEFORE and SAB_AFTER. A script
applies the CURRENT plant to a `git archive HEAD` tree and the OLD plant to a
`git archive 78058db7` tree, diffs each against its own clean tree, and
compares the two plant-diffs modulo that substitution. **16 of 17 are
IDENTICAL.** The exception is S217 site 1 and the difference is exactly this
lane's seam decision: the old plant edits a line that DECLARES
`const bool has_push = …` and the new one edits a line that ASSIGNS
`v->has_push = …`. What the plant does — make the gate read the pre-pass
estimate `v->npush` instead of the emitted-text flag — is unchanged.

*(ii) LIVE, on three rows chosen to cover each substitution class,* each
built as a full sabotaged compiler from a `git archive HEAD` scratch tree and
run against the clean one:

| row | class | clean | sabotaged |
|---|---|---|---|
| S217 | a local that became a `Vm` field (the one non-identical re-aim) | `(?:ab|b){8,}+c` compiles with **1** `goto *` site; `bbbbbbbbc` -> `match 0 9`, `abbbbbbbbc` -> `match 0 10` | **0** `goto *` sites; both -> `nomatch` (`ababababababababc`, which needs no backtrack into the second alternative, still matches) |
| S169 | `root_minw` -> `v->root_minw`, anchor text that moved into a new function | `^((?1)a)$` carries 3 `RX_VM_ROOT_MINW` mentions; `"aaa"` -> `nomatch` | 1 mention; `"aaa"` -> `frames` |
| S41 | `&v` -> `v` (the argument form) | `a(b|c)+d` listing carries 7 labels incl. `L1 label … the pattern is complete`, 18 events | 6 labels, 17 events — the listing describes a program one label short of the emitted one, the exact drift the row names |

Each reproduces its row's own documented failure mode. The scratch trees were
removed afterwards.

## 5. Validation

- `make -j4 CC=gcc-16` — clean, zero warnings, after every commit.
- `make strict CC=gcc-16` — clean (`-Werror -Wshadow`), after every commit.
- `python3 scripts/m6read_check_sab_anchors.py` — **285/285 resolve**, after
  every commit.
- `make test-vm CC=gcc-16` — **48 checks passed, 0 failed; 3/3 scripts**
  (the brief's expected figure exactly).
- `make test-codegen CC=gcc-16` — **9/10 scripts, 301 individual checks, 0
  failures.** The sole red is `run_inline_capability.sh`
  (`FAIL: nm could not read arm_a.o (no rx_search symbol) — no verdict is
  evidence here`), which is the standing darwin red the brief names as the
  known state and which every recent lane records at its own branch point.
  No other red appeared, so no A/B against a scratch build of `78058db7` was
  needed. Log: `build/tour1/test_codegen.log`.
- `python3 scripts/emit_sweep.py --ref 78058db7` at FULL reach — **OWED**,
  see §5.1.
- A 300-row `--limit` smoke of the same sweep was run after EVERY commit (six
  of them) and read **0 movers / 0 asymmetric on all five streams** each
  time; the floor violations a `--limit` run prints are expected and are not
  movers. Logs: `build/tour1/smoke1.log` .. `smoke6.log`.
- `make test` — NOT run, per the brief.

**NOT an abi event.** No emitted byte moves, so no `abi` bump and no
identity-gate re-pin. The one edit that could have moved a byte — hoisting
the entry-rung decision out of the stamps — was checked for exactly that and
is inert because the block emits nothing; the `<PREFIX>_VM_PROGRAM_BYTES`
stamp still reads the same `pcrec_sb_len_uncut(&job->vmsb)` at the same point
in the emission.

**No `docs/spec/` hunk is owed.** Nothing a caller can observe changed: no
entry, flag, stamp, limit, diagnostic tier or module behaviour moves. The one
documentation change outside this report is the `plan_completed.md` addendum
in §3, which records a fact, not a contract.

## 5.1 Owed at hand-off

**One item: the FULL-reach `scripts/emit_sweep.py --ref 78058db7`.** It runs
~5-6 minutes, so per BOILERPLATE's DO-THEN-FINISH it was launched in the
background as this lane's LAST act and its result is owed.

- log: `worktrees/tour1/build/tour1/emit_sweep_full.log`
- completion line to look for: `elapsed: <N>s` as the file's last line, with
  the five `-- stream: … --` blocks above it.
- PASS criteria: `movers=0 asymmetric=0` on all five streams
  (`c-default`, `c-vm`, `emit-ir-vm`, `composition`, `dumps`), in BOTH the
  self-check block and the real-run block, and no `FLOOR VIOLATION` line.
- What already stands behind it: six 300-row `--limit` smokes of the same
  instrument, one after each commit, all `0 movers / 0 asymmetric` on all
  five streams. This run is the full-reach confirmation, not the first
  evidence.

## 6. Notes for whoever picks this up

- **`docs/dev/reviews/lens_reports/emitvm_second_pass.md:388` and
  `lens_reports/CLAUDE.md:238` both say "`Vm` is 364 lines of file-private
  state".** `Vm` gained four fields here, so the number is stale. They are
  historical review records and this lane did not edit them; the rewritten
  `pcrec_emit_vm` header deliberately states the fact without the count.
- **[ORG-3] (splitting emit_vm.c by its banner sections) is now cheaper than
  its own charter priced it.** That row's "price of a split" is 285 sabotage
  anchors and many doc citations; this lane moved 17 of those anchors for
  free by keeping every relocation at the same indent, which is the same
  property a file split would have. The 780-line `vm_emit_search_body` is now
  the biggest single unit a split would have to move.
- The brief asked for one commit per step and got one per extracted function
  in step 3 (five instead of one), on the grounds that commit age is the
  liveness signal and each is independently green.
