# Lane p1dsg — P1 build design: the landmark-seeded reverse DFA (D161 add. 17 "Structure")

Lane p1dsg, opus, 2026-10-29, worktree `worktrees/p1dsg` at main 8fcc15669. Design and
measurement only. No build: no edit under `src/`, `cli/`, `lib/` or `memfn/`. The twins live in
scratch, and their diffs and drivers are in `p1dsg_evidence/` (its CLAUDE.md lists every file).
All numbers come from `p1dsg_evidence/results.txt`, `population*.txt`, `size.txt`,
`crossover.txt` and `unique_model.txt`. Instruction counts (instructions:u) are the evidence,
because the box was loaded by queue job 622-kit-s3m-heavy. Cycles are reported as a ratio only.

## Summary

- **The mechanism is ONE new LOCATE row of the existing start table `cand_rows[]`. There is no
  new table (ruling R1).** I name it `landmark-walk`, after what it does (D174); it is the row
  locate_finish.md §4.6 filed as `rev-inner[-bounded]`. It finds each hit `j` of the landmark
  `L`. From there it runs rev(P·L) backwards, seeded at `j+|L|` and floored at `search_from`.
  The smallest accepting position is `s*(j)`, and the row hands it to FINISH:
  - On the DFA route: `verify-at` on the anchored machine.
  - On the VM route: one anchored attempt, or LOWER.

  The kit's EDGE ADVANCE runs inside the walk machine as the optimization. p48's priced
  one-state relaxation is a row of that edge table.
- **The 5b mask-email twin keeps the win.** It is built exactly this way: rev DFA of
  `[A-Za-z0-9._%+-]+@` seeded at `@`, plus its scan edge. On acc-main (362 MB) it measures
  5,477.6M → 77.8M instructions (**x70.4**) and 2.37G → 58M cycles (x40). Its spans are
  identical to shipped. subtri's hand walk was 73.1M (x75). The scaffolding carries the win:
  denying the edge costs only 2.4% (79.7M).
- **dup-param twin (VM route).** Its starts are unique because of the `\b`, so it hands CAND
  per occurrence. Measured per line:
  - acc-main: x1.45 instructions / x1.29 cycles;
  - synthetic query strings: x1.33 / x1.19;
  - answers identical on both.

  The bench cells do NOT move, because their subjects hold no `&` (revtwin's NOT MET stands).
  After the twin, the VM's own backtracking attempts are the cost.
- **Rarity is load-bearing, and pricing beats a factor.** Where landmarks are dense, the twin
  is SLOWER:
  - fz-me (about 1 '@' in 10 bytes): x1.25 worse;
  - crossover sweep: break-even near one hit per 19 bytes, about 294 instructions per hit
    against 15.4 instructions per byte for the shipped DFA.

  The admission's rarity row should be priced from a measurement card, not set by the
  unmeasured factor F = 2.
- **Every recorded rev-inner unsound case is excluded by a named admission row** (table below).
  The STOP RULE did not fire.
- **A new soundness refinement, verified against libpcre2.** Where `S` reads `P`'s groups, CAND
  per occurrence is still exact if each hit has ONE start candidate (fixed width; `\b` before a
  word-only P; `(?m)^` before a P that cannot consume `\n`).
  - `unique_model.py`: 7 unique rows, 0 wrong over about 115k checks (two seeds).
  - The 3 NEGATIVE rows (bak-1, LF-E1's `(a+)X\1`, dup-param without `\b`) go wrong
    13-1013 times each.
- **Stage 1 is the DFA hat.** It moves 5b and up to 9 other bench DFA rows (count depends on
  the priced rarity row). Stage 2, the VM hat, waits on locate_finish L3 and [GIVEUP-DIFF].
  All of it waits on the one-optimization-build-at-a-time rule until [INLINE-C] closes.

## Premise test

The premise is that today's artifacts do NOT already do this. Confirmed at HEAD
(build/pcrec, main 8fcc15669):

| pattern | today's stamps | what it means |
|---|---|---|
| 5b mask-email `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}` | `RX_ENGINE "dfa"`, `RX_DFA_PREFILTER "byte-class"`, `RX_DFA_SCAN_EDGE "bitmap"`, `RX_DFA_START "reverse-pass"`, `RX_REQ_BYTE "64"` | the forward DFA walks every byte of every local-part class run, and RECOVER reverse-walks from a match end. The landmark `@` is used only as a PRESENCE pre-check |
| dup-param `\b(\w+)=[^&]*&(?:[^&]*&)*\1=` | `RX_ENGINE "vm"`, `RX_VM_START_SCAN "first-class"`, `RX_VM_PREFILTER "none"`, `RX_REQ_BYTE "38"` | a VM attempt at every `\w` start; `&` is only a PRESENCE pre-check |

On both, the landmark is known, and the search does not start from it. The family's premise
holds.

## Admission table

These are first-match rows. The first row that applies decides, and only `excl-cand` and
`excl-lower` select the LOCATE row. Every other row DECLINES: `landmark-walk` does not apply,
and the table falls through to `composite` as today.

At build time the rows are the conjuncts of `locate_landmark_walk_applies`. They are listed
in the same order, so `--list` can print the deciding row per compile; that is the declined
reason [LIST-TABLES] asks for. Each row has a population (next section) and a reason.

| # | row | applies when | verdict | reason (rule / unsound case it excludes) |
|---|---|---|---|---|
| 1 | `no-split` | no inner landmark `L` with a non-empty prefix `P`, or `R` start-anchored | decline | nothing to seed from |
| 2 | `g1` | `P` not regular-faithful: backreference, call, atomic/possessive, or a lookaround the DFA cannot view | decline | G1; `erase_atomic` (where_to_start §2.6) |
| 3 | `fixed` | `P` has one fixed width `k` | decline to the EXACT-k NEXT rows (`run-pinned*`, `offset-set*`) | those rows are the walk's constant-width case and stay (fold trigger, Build plan) |
| 4 | `branches` | more than one top-level branch | decline | D151 add. 6/7 composition; per-branch P_i F1 (where_to_start §2.6). Belongs to [MATCH-SPLIT] (Remodel overlap) |
| 5 | `rarity` | priced: `p(L)·H(w) ≥ c(route)` (Measurement card); until measured, the labelled UNMEASURED default `ratio < F`, F = 2 | decline | negative control: fz-me x1.25 worse; crossover at ~1 hit / 19 B |
| 6 | `excl-cand` | strong arm EXCLUSION (`bytes(L) ⊄ alphabet(P)`) ∧ (G4: S reads no group of P ∨ UNIQUE starts) | **SELECT**, hand CAND per hit | D151 strong arm; LF-E1 is excluded by the G4/unique conjunct |
| 7 | `excl-lower` | EXCLUSION ∧ ¬G4 ∧ starts not unique | **SELECT** (VM hat only, stage 2), hand LOWER(s*(j₀)) | LF-E1, DUPNAMES LR-S5: the closed G4 predicate (locate_finish §4.6) |
| 8 | `factor-free` | only the third G2 arm (L no factor of P, border-free) | decline (HELD) | add. 5's arm; population 1 corpus / 2 bench |
| 9 | `plain-shared` | P one plain run that can consume L | decline (HELD) | exact but not linear without a run memo |
| 10 | `fallback` | always | decline | rust #1354 "which occurrence": no strong arm |

**UNIQUE starts.** This means `starts(j)` never holds two positions. It is decided at build
time on rev(P) by one rule: no accepting state of rev(P) is reachable from another accepting
state, by-class accepts included.

Fixed width implies it. So do `\b` with P's alphabet ⊆ `\w`, and `(?m)^` with `\n` ∉
alphabet(P). The census (`population.py`) uses only these sufficient forms, so it undercounts.

Why it is exact: LF-E1's failure needs a second, larger member of `starts(j)` that succeeds
where `s*` fails. With one member, the per-hit attempt at `s*(j)` IS every attempt the
shipped loop could make for that hit's matches. The libpcre2 model checks this
(`unique_model.py`; Summary).

**The unsound cases, each excluded:**

| recorded case (where_to_start §2.6/§2.7, locate_finish §4.6, D151 add.) | excluded by |
|---|---|
| rust #1354 / which-occurrence (a later hit's start precedes an earlier hit's) | rows 6/7 require EXCLUSION; no-arm rows hit row 10 |
| the floor at the previous hit (`[a-z]+xy`) | no floor at a previous hit: the walk floors at `search_from` only, and exclusion stops it at the previous L byte. That shape is `plain-shared` (row 9, HELD) |
| per-branch P_i F1; composition (add. 7) | row 4 |
| LF-E1 `(a+)X\1` (82 wrong / 82,903) | row 6's G4-or-unique conjunct → row 7 LOWER |
| DUPNAMES LR-S5 `(?J)(?<n>a+)X(?<n>b)?\k<n>` | G4 is locate_finish §4.6's closed switch over every `refs[]` member |
| `erase_atomic` | row 2 |
| `lo0` / slice (context at the floor) | the walk reads `subject[lo−1]` for context at the floor (the existing reverse-pass floor code), never "absent" |
| restart_s1 / skipL (find-all restart) | find-all `next` starts at the previous match end. An empty match advances `j+1` on the CALLER's side, never a hit-relative skip |
| quadratic forward verify (§2.7) | the DFA hat's reach guard → FIN4 `search-from` (Mechanism) |
| utf8 non-initial landmark byte | stage 1 admits utf8 only where `L[0]` is ASCII, so it is a character boundary |

No recorded case is unexcluded.

**The facts row.** This is revwalk's proposed `back_walk` with its value SIMPLIFIED by add. 17.
Segments, kinds and counts are gone: rev(P) is exact by construction.

    PF_FACT(BACK_WALK, "back_walk", 2, PF_DERIVED, 0, "src/facts/backwalk.c",
            "req_set req_run req_set_maxoff req_landmark_maxoff")

- **Value:**
  - the landmark (which req fact, and its offset in the run);
  - the sub-tree id of P (what rev(P·L) is built over);
  - the EXCLUSION bit;
  - the G4 bit (S reads a group of P);
  - the top-level branch count;
  - the rarity inputs.
- **The deciding row is computed by the row predicate, not stored here.** UNIQUE needs
  rev(P), which exists only at machine-build time (compile.c), so it lives with the machine,
  not in the fact.
- **Declines are spelled as the admission rows' names.**

## Mechanism

**Where rev(P·L) is built.** In compile.c, beside the other optional machines, in the
`revend_build_one` pattern (compile.c "D164 B3 ONE OPTIONAL MACHINE"):

1. `pcrec_build_min_dfa(cx, nfa_of(P·L), &job->lwdfa, prune, reverse=true, cap, root=P·L)`;
2. then `pcrec_scanedge_dfa(...)`, which is where the kit's EDGE ADVANCE comes from.

Overflow is a DECLINE (the record is saved and restored), never a refusal. Building over P·L,
not P, matters:
- the seed state needs no hand-computed end context;
- `L`'s own bytes are re-checked by the walk (|L| steps);
- a `\b` or by-class accept at P's end sees the true right-hand byte.

This is what both twins run (`extract_rw.py` wraps pcrec's own reverse-pass text of `P·L`).

**The row.** In `cand_rows[]`, the LOCATE block becomes:

    empty, rev-end, cover, landmark-walk, composite

- **After `rev-end` and `cover`.** Both answer the whole call with at most one walk and no per-hit
  loop. They are cheaper wherever they apply.
- **Before `composite`.** `composite` is the always-row.

One row, not locate_finish's `rev-inner-bounded` + `rev-inner` pair. Under the reverse DFA,
a bounded P simply reaches a dead state sooner. The views-first split was a T-tier artifact
and is deleted; the simplification counts as a benefit.

- **Routes:** `CR_DFA` (stage 1); `CR_VM` (stage 2).
- **Deny:** `PCREC_NO_LANDMARK_WALK`, one flag bit. About 8 bits remain; the [IFACE-PUSH]
  hard trigger is ≤ 4.
- **`.needs`:**
  - `[CR_DFA]` = {W (the new walk machine), A, F + the composite's slots (the fallback), PRESENCE};
  - `[CR_VM]` = {W, VM}.

  §2.7's path closure then derives the members and stamps. A new machine bit `W` joins F/R/A/ATT/VM.

**The relation to today's start rows (R1).**

| today's row (slot) | under landmark-walk | fold? |
|---|---|---|
| `rev-end` (LOCATE) | stays first; an end-seeded reverse DFA; the same scaffolding seeded at `n` | it IS the family's end-seeded member; no fold needed |
| `cover` (LOCATE) | stays before; proves the whole match without a machine | no |
| `composite` (LOCATE) | the fallback when the guard trips (FIN4 `search-from`) | no |
| `run-pinned[-bounded]`, `offset-set[-bounded]` (NEXT, EXACT-k) | the walk's constant-width case: rev(P) of width k is "step back k". Row 3 defers to them | **fold candidate**; trigger: the stage-1 card shows the walk's per-hit cost on a width-k P within noise of `offset-set`'s |
| `handoff`, `handoff-attempts*` (FIRST), `handoff-reentry` (NEXT): req-handoff | LOWER = hit − `req_landmark_maxoff` is the walk's bounded-width special case. The walk's `s*(j₀)` is never lower, so it is always at least as tight | **fold candidate at stage 2**: where `landmark-walk` is selected on `CR_VM` the handoff rows go off the path. Where it declines they stay (no exclusion → no walk) |
| `first-class` (NEXT, VM start-set) | off the path where the VM hat selects `landmark-walk`; the twin replaced exactly it | no (composite's) |
| `pinned`, `end-minus-width`, `landing`, `reverse-pass` (RECOVER) | asked only by `composite`; `landmark-walk` hands a START and asks no RECOVER | no: they are end-seeded shortcuts of R, a different seed |
| filed `rev-end-relaxed` (L4) | the same relaxed reverse machine seeded at a landmark is the "relaxed prefix" later row | **one mechanism**: the later row reuses L4's machine, not a second relaxation |

**The walk, per hit `j` ascending from `search_from`.** The kit's find of `L` supplies the
hit. The walk is `st = W.seed; for p = j+|L| down to lo: …`:

- It records the last accepting position.
- It stops at the dead state or at `lo`.
- At `lo` it reads `subject[lo−1]` for context: the existing reverse-pass floor code.

`s*(j)` is the smallest accepting position. No accept means the next hit. The EDGE ADVANCE
skips W's self-loops (5b: the local-part class loop).

**DFA hat (stage 1).** FIN3 `verify-at`: one anchored run of A from `s*(j)`. A match is a
SPAN, and the row returns it. Otherwise the next hit.

The quadratic guard: keep `reach`, the farthest byte the last verify read. If the next hit's
`j < reach`, hand `s*(j)` as LOWER to FIN4 `search-from` on `composite`, which is linear.
This is locate_finish §4.6's give-up hand-off, a measured `fallback` there. The 5b twin ran
without the guard. On acc-main the guard does not trip, because each verify reads at most to
the line's next non-class byte.

**VM hat (stage 2).**
- `excl-cand`: FIN3, one `rx_match_anchored` attempt at `s*(j)`; error codes propagate
  (the twin's splice).
- `excl-lower`: LOWER(s*(j₀)) to FIN4 `search-from`; the attempt loop runs from there.

Both are ONE_WAY (D148 Q6, D151 Q4). The attempts made are a subset of the shipped loop's,
so there is no new give-up surface. GIVEUP1 must still show that, which is [GIVEUP-DIFF]'s
job before any VM-finisher LOCATE row (locate_finish L3/L5).

**The three standing questions.**
1. **Measurement regime:** instructions:u, find-all over named subjects (results.txt), plus the
   crossover sweep for the rarity price.
2. **Independent control:** libpcre2 10.46 is the oracle (unique_model.py; revwalk's model.py
   for the strong arms). Span hashes compare against the SHIPPED artifact, which shares no
   start code with the twin.
3. **What moves on regeneration:** W's tables, and the stamps `RX_DFA_SCAN "landmark-walk"` and
   `RX_VM_START_SCAN`. This is an abi event and an identity-gate re-pin (D76/D94).

## dup-param twin

Pattern `\b(\w+)=[^&]*&(?:[^&]*&)*\1=`, VM route. The twin (`mk_vmtwin.py`, `twin_dp.diff`)
splices into `rx_search_run`, before the attempt loop:
1. memchr `=`;
2. `rw_walk` = pcrec's own reverse-pass machine of `\b\w+=`, seeded after the `=`;
3. ONE `rx_match_anchored` at `s*`, else the next `=`.

The match is CAND per occurrence: `\b` before a `\w`-only P makes the starts UNIQUE, although
`S` reads `\1`. Per line (`drv_lines.c`; whole-file runs give PCREC_ERR_FRAMES on both forms,
because `[^&]*` crosses newlines):

| subject | shipped instr | twin instr | ratio (instr / cycles) | matches, hash |
|---|---|---|---|---|
| acc-main, 1.6M lines (52,280 with `&` and `=`; 337,676 candidates) | 3,966.6M | 2,742.0M | x1.45 / x1.29 | 5542, cd1a5c10… both |
| qs-200k synthetic query strings (21 MB, 3% repeated key) | 5,275.7M | 3,978.0M | x1.33 / x1.19 | 6019, fc1953cd… both |
| bench t-1m / t-64k / t-hyb-embed-64k | 98,552 / 6,393 / 6,393 | identical | x1.00 | no `&`: both dismiss at the pre-check |
| fz-dp, 300k random lines | 682.2M | 428.0M | x1.59 | 3994, 64d953ab… both |

**Where the cost goes.** With the VM attempts stubbed out:
- acc-main: the twin's walk + find cost 0.41G of the 2.74G;
- qs-200k: 0.085G of 3.98G.

The start-finding part on qs went 1.39G → 0.085G. What remains is the VM's own backtracking
attempts, about 6.9k instructions each on `[^&]*&(?:[^&]*&)*\1=`. That is P2/P3's territory
(trail), not P1's.

**Hand class-context edge.** A hand scan edge on the `\w` reverse loop, the accept invariant
over the loop's context classes, measured 3,970.1M vs 3,978.0M: negligible. So the proposed
edge-precondition relaxation is NOT worth building (BOONIES). A stubbed-VM arm with the
edge measured 168.6M against 85.2M; that is a codegen effect, recorded and not chased
(one-pass rule).

**Verdict.** The design holds on the VM route. The twin is answer-identical, and the start
part of the cost almost disappears. It does NOT move a bench cell. The movement needs
query-string traffic.

## mask-email twin

5b, built exactly as the design says (`mk_twin.py`, `twin_5b.diff`):
1. memchr `@`;
2. `rw_walk` = pcrec's reverse-pass machine of `[A-Za-z0-9._%+-]+@` with its unbounded scan
   edge (`RX_DFA_SCAN_EDGE` on the walk's class loop), seeded after the `@`, floored at
   `search_from`;
3. the shipped anchored machine `rx_match` at `s*`, else `p = at+1`.

Find-all over acc-main (361,986,301 B; sha256 a9b0a4cc…, regenerated from a scratch copy of
bench/subst):

| form | instr | cycles | result, hash |
|---|---|---|---|
| shipped (byte-class prefilter + forward DFA + reverse-pass RECOVER) | 5,477,638,535 | 2,370M | 80123, e97ca4d6da618f68 |
| twin (rev DFA + scan edge) | 77,755,125 (**x70.4**) | 58M (x40) | same |
| twin, `-fno-scan-edge` on the walk | 79,663,522 (x68.8) | 63-67M | same |
| subtri's hand memchr walk | 73.1M (x75) | — | — |

**It keeps the x75 to within 6%.** The remainder is a table walk against subtri's hand-coded
class test. The scaffolding carries the win; the edge adds 2.4%, because local parts are
short (about 8 bytes).

**Answer identity:**
- fz-me per line (hash 9d38ff6d…) and whole file (815700d7…): identical;
- 364 bench capability + email subject files, both patterns: 0 diffs.

**NEGATIVE control, dense `@`.** With about 1 '@' in 10 bytes, the twin is SLOWER: per line
150.9M vs 120.9M (x1.25 worse), whole file 117.6M vs 97.6M.

**Crossover sweep** (`crossover.txt`, `crossover_subjects.py`). The subjects are 4 MB of
8-byte class words, with a fraction q of the words followed by a failing `@ `:

| q | ratio (twin / shipped) |
|---|---|
| 1 | 1.909 |
| 0.5 | 1.008 |
| 0.25 | 0.524 |
| 0.1 | 0.223 |
| 0.03 | 0.074 |
| 0.01 | 0.030 |
| 0.001 | 0.008 |

From these points:
- the walk with its verify costs **H ≈ 294 instructions per hit** (8-byte walk);
- the shipped DFA costs **c ≈ 15.4 instructions per byte**;
- the find floor costs ≈ 0.13 instructions per byte;
- break-even is at ≈ 1 hit per 19 bytes.

This is the rarity row's price, not a factor.

## Population

From `population.py` (parse-only, built on revwalk's `tiers.py`), with F = 2 (the labelled
default):

| row | corpus (5203) | bench (346) |
|---|---|---|
| no-split | 3307 | 247 |
| g1 | 374 | 15 |
| fixed | 105 | 14 |
| branches | 1 | 2 (waf sleep, ipv6) |
| rarity | 104 | 12 |
| **excl-cand** | **259** | **12** |
| **excl-lower** | **43** | **6** |
| factor-free | 1 | 2 |
| plain-shared | 22 | 1 (cls-s-uc) |
| fallback | 54 | 1 (email/orig) |
| uncounted (reader) | 933 | 34 |

**Admitted corpus rows, by revwalk tier.** excl-cand is T2 bounded 70 / unbounded 90, T3 9/4,
T4 bounded 81 (+1 S-reads-P unique), T4 unbounded 4. excl-lower is T2 10+26, T3 2, T4 5.
- T4 ("outer", a view inside P) rows are ADMITTED here and were HELD in revwalk. The reverse
  DFA walks them exactly: kv-quoted, stack-frame, ipv4.
- Selftest 12/12; `--sabotage unique` is detected (10/12).

**Bench admitted rows, by route** (the route is from `size.txt`'s `RX_ENGINE`):
- **DFA**, `excl-cand` (stage 1): 5b mask-email (ratio 1237), csv5 (149), kv-quoted (200),
  stack-frame (33), dotted4 (7.5), ipv4 (7.5), qnt-plus / qnt-plus-ctl (5.5),
  cls-s-nbsp / cls-s-ucp (5.5, utf8, ASCII `L`).
- **VM**, `excl-cand` (stage 2): dup-param-detect (UNIQUE by `\b`), username-password.
- **VM**, `excl-lower` (stage 2): tag-depth3-bound, tag-pair-match, bak-k-named, bak-1,
  bak-g-rel, mod-j-uc.

**Sensitivity to the rarity factor** (`population_fsweep.txt`):

| F | corpus excl-cand / excl-lower | bench excl-cand / excl-lower |
|---|---|---|
| 2 | 259 / 43 | 12 / 6 |
| 8 | 70 / 43 | 5 / 6 |
| 20 | 57 / 40 | 5 / 3 |

5b sits at 1237 and is admitted at any F. The five rows with a ratio of 5.5-7.5 are exactly
the ones whose admission the priced row must decide.

**Route split for the CORPUS rows: not measured.** It needs about 300 compiles (> 50, so it
needs boxlock), and the box was held by 622-kit-s3m-heavy. revwalk's per-tier route split
(about half VM) stands in. The build lane's first step is this census, under boxlock.

## Size and compile cost

`size.txt` (`size_run.sh`) covers 17 of the 18 bench admitted rows (bak-g-rel omitted: it has
bak-1's shape). It compiles each full pattern and each P·L with the RECOVER shortcuts denied,
so pcrec emits P·L's reverse-pass machine, which is the W machine this design builds:

| row | route | artifact (B) | W cells | W text (B) | edges |
|---|---|---|---|---|---|
| dup-param | vm | 26,594 | 9 | 3,564 | 0 |
| username-password | vm | 548,919 | 289 | 5,852 | 0 |
| tag-pair | vm | 26,161 | 30 | 4,658 | 0 |
| mask-email | dfa | 22,661 | 9 | 5,006 | 1 |
| kv-quoted | dfa | 35,874 | 396 | 8,908 | 0 |
| stack-frame | dfa | 63,350 | 90 | 4,638 | 0 |
| ipv4 | dfa | 21,608 | 64 | 3,335 | 0 |
| cls-s-ucp (utf8) | dfa | 26,543 | 247 | 4,279 (tables only) | 0 |
| others (9) | — | 16.6-33 K | 9-30 | 2.9-5.3 K | 0-1 |

**Size.**
- W is 0.6-8.9 KB of text against 16.6-549 KB artifacts: +1% (username-password) to +40%
  (the smallest artifacts, where the walk function's fixed scaffolding dominates).
- W's state counts (9-396 cells) are far below `PCREC_MAX_DFA_STATES_TABLE` (32000).
- An overflowing W is a decline, never a refusal (Mechanism).

**Compile time.** Building P·L from scratch costs 4-7 ms per whole pcrec process, against 4-32
ms for the full pattern. Inside one compile, W is one more `pcrec_build_min_dfa` over a
sub-tree, which is an upper bound well under the full compile.

**The size-cap ladder** (limits.md §8.4). Add a rung `drop-landmark-walk` (DFA and VM;
deny: the row's own flag) **before rung 3 `drop-anchored`**:
- On the DFA hat, W needs A, and §8.4¶2a's rung 3 applies only where dropping leaves a strict
  subset of the machines. Dropping A under a selected `landmark-walk` would leave `needs ⊄
  built`, which is a defect.
- W's text is small, so the rung rarely binds.

Its position within the VM rungs (before 1) is a labelled UNMEASURED order. limits.md §8.4's
"degrading: all eight" becomes nine.

## Measurement card

The card is new, because a new find/locate method needs one in the same change
(memory "new method needs measurement card"). The proposed row is for pcrec's card table
(`measure/cards.tsv` does not exist yet, and the build creates it in measure_sets.md §7.2's
column order):

    owner  quantity  ver  dims        unit   subject                 lengths                launches rounds aa_rule         gate_e6  env deps
    pcrec  lwhit     1    route;wlen  instr  landed:crossover-q      4 MiB, q in {1..0.001} 5        5      pair-per-group  30000*   -   pcrec:probe.mask-email
    pcrec  lwbyte    1    route       instr  landed:crossover-q      4 MiB, q = 0.001       5        5      pair-per-group  30000*   -   pcrec:probe.mask-email

(*) a labelled UNMEASURED default (D149).

- **`lwhit`:** the cost of one hit = walk + verify (DFA hat) or + attempt setup (VM hat, VM
  stubbed), as a function of the walk length `wlen` ∈ {2, 8, 32}. The walk length is
  generated by the word length of `crossover_subjects.py`.
- **`lwbyte`:** the find floor per byte.
- **What it prices.** It pairs with the route's existing per-byte cost (the DFA-step and
  VM-start rows the stop choice already reads). The rarity row becomes
  `p(L)·lwhit(wlen̂) < c(route) − lwbyte`. Here `p(L)` is the landmark's prior from the byte
  table F already uses, and `wlen̂` is the expected run length: P's max width when bounded,
  otherwise the class-run prior.
- **Measured values (this lane, loaded box, not a set):**
  - lwhit(dfa, 8) ≈ 294;
  - c(dfa, byte-class) ≈ 15.4;
  - lwbyte ≈ 0.13.
- **Twin cells for the build's acceptance:**
  - 5b on acc-main (x70 instructions);
  - dup-param per line on acc-main and qs-200k;
  - fz-me per line as the NEGATIVE control (it must DECLINE or not lose);
  - the crossover q-sweep.
- **Bench ask (via the manager):** a query-string subject for dup-param. Without one, stage 2
  shows nothing on the bench.

## Build plan

All stages wait for the build gate. Frank's rule is one optimization BUILD at a time until
[INLINE-C] closes. The primed ranking is P2 > P1.

**Stage 1: DFA hat, `excl-cand`, single branch.** It moves 5b. One build lane (opus), one abi
event:
1. A census under boxlock: the corpus route split per admission row (not taken here).
2. The `back_walk` fact (src/facts/backwalk.c), with the `--emit-facts` reader.
3. W in compile.c (`revend_build_one`'s pattern, an overflow declines), plus
   `pcrec_scanedge_dfa` over it. **p48's priced SCAN_SITE_ROWS sits INSIDE here.** That is
   row 4 (split-exit, the one-state relaxation priced by k* ≈ 2.3 B), held for P1. W's loops
   are its first client: 5b's walk loop (about 8 B > k*) is admitted, and the bounded-head
   entry rule applies unchanged.
4. The `landmark-walk` LOCATE row (CR_DFA) between `cover` and `composite`, with `.needs`,
   the reach guard → FIN4, the deny flag, and the listing.
5. The rarity row priced from the card. The card and its script are in the same change.
   Until a set exists, use F = 2, labelled.
6. The ladder rung.
7. Spec hunks: tuning.md (a new section), match_api.md stamps, limits.md §8.4, flags.
8. Tests:
   - the answer net: the unsound witnesses above, LF-E1 and DUPNAMES as DECLINES on the DFA
     route, `\G` (locate_finish §4.6), the utf8 ASCII `L` rows;
   - a libpcre2 differential model;
   - sabotage ids: max-start instead of min; the floor context dropped; the reach guard
     removed (an instruction-count witness); EXCLUSION dropped (the rust #1354 shape); W
     seeded at `j` instead of `j+|L|`.

Movers: bench 5b (x70) plus up to 9 DFA rows, depending on the price.

**Stage 2: VM hat.**
- **Trigger:** locate_finish L3 (VM hats) and [GIVEUP-DIFF] landed; plus a bench query-string
  cell, or Frank's go on the acc-main evidence.
- **Content:** the same row on CR_VM; `excl-cand` (incl. UNIQUE, decided on W) as CAND →
  FIN3; `excl-lower` as LOWER → FIN4; the req-handoff rows go off the path where it selects.
- **Movers:** dup-param x1.3-1.45 on query-string traffic, plus the 7 other VM rows.

**Later rows, each with its trigger:**

| row | trigger |
|---|---|
| `branches` | [MATCH-SPLIT]'s class union: each part of the compound carries its own `landmark-walk` row (no per-branch mechanism here) |
| `factor-free` | a bench mover in that row (today 2 bench rows, 1 corpus) |
| `plain-shared` | a run-memo design; 22 corpus / 1 bench |
| relaxed prefix (W over the cap, or G1 content in P) | L4 `rev-end-relaxed` built; reuse its machine |
| fold `run-pinned*` / `offset-set*` | the stage-1 card shows walk cost ≈ theirs on width-k |
| fold the req-handoff rows | stage 2 landed |
| class-context edge relaxation | measured negligible → BOONIES |

**Remodel overlap.**
- **[OPT-REVEND] / locate_finish.** The LOCATE block, `.needs` and the path closure are
  stage 1's substrate; L0 and the `rev-end` row are in the tree. Stage 2 rides L3 and needs
  [GIVEUP-DIFF]. This row replaces the filed `rev-inner` rows (§2.4, §4.6, L5).
- **[COMPOUND] / [MATCH-SPLIT].** The `branches` row belongs there. A compound's part is an
  artifact with its own start table, so no parallel per-branch walk. Stage 1 does not touch
  the compound controller.
- **[DD-11.5] / D168.** The walk's context at its floor and the UNIQUE rule's `\b` / `(?m)^`
  forms are span-context facts. Stage 1 reads them from W itself (A_CTX in the reverse
  machine), so it has no dependency and adds no parallel spelling. When D168's producer
  lands, it is the place to state the facts.
- **[INLINE-C].** No code overlap; a scheduling gate only.

## Questions for Frank

1. **The rarity threshold: price it, or a factor?** Where landmarks are dense, starting from
   them is slower than today: about 25% worse at one '@' per 10 bytes. In the crossover
   sweep, break-even is around one landmark per 19 bytes. Five bench rows sit at a rarity
   ratio of 5-7.5, where a factor-of-2 rule admits them and a factor-of-8 rule does not.
   - My leaning: stage 1 builds the priced comparison from a measured card (per-hit cost
     against the route's per-byte cost), not a constant, since a measurement card is owed
     anyway. Until the card is measured on the box, it uses factor 2, visibly labelled
     unmeasured.
   - The other way: ship factor 8 now (more conservative, 5b still admitted) and price later.
2. **Should dup-param's VM stage wait for a bench cell?** The twin is a clean 1.3-1.45x on
   real and synthetic query strings. The bench's throughput subjects have no `&`, so stage 2
   would show zero bench movement.
   - My leaning: ask the bench for a query-string subject now, and let stage 2's trigger be
     "L3 landed and that cell exists". The other way: build on the acc-main evidence alone.
3. **Fold the older special cases after stage 1?** Under the reverse-DFA scaffolding, the
   fixed-offset rows (`offset-set`, `run-pinned`) and the required-byte handoff rows are
   special cases of this walk.
   - My leaning: keep them in stage 1, and fold each once the stage-1 card shows the walk costs
     the same there. The deleted rows are then the benefit.
   - The other way: fold in the same build, which costs more and risks the answer-identity
     gate.

## STATE AT HANDOFF

- Delivered and committed on lane/p1dsg:
  - this report;
  - `p1dsg_evidence/`: twins, drivers, the population census + F sweep, unique_model.py
    (libpcre2 10.46, PASS on two seeds), the crossover sweep, the size census;
  - the history-index entry.
- OWED: none. No job is queued.
  - **Not measured:** the corpus route split per admission row (>50 compiles; the box was held
    by 622-kit-s3m-heavy). It is named as stage 1's first step.
  - **Not chased:** the 168.6M stubbed-VM codegen effect (one-pass rule).
- Rulings file `p1dsg_rulings.md`: last entry applied **R1** (the admission rows are new rows
  of `cand_rows[]`, placed and related to today's rows above; no new table).
- STOP RULE: not triggered. Every recorded unsound case is excluded by a named row, and both
  twins agree with the design.
- No edits under `src/`, `cli/`, `lib/` or `memfn/`. Nothing was merged.
