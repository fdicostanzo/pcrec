# cover_cap.md — the `cover` route's exact span: a straight line, no length bound, no budget ([COVER-CAP])

Status: PROPOSED, revision 2 (lane `covcap3`, 2026-11-15). DESIGN ONLY: no build go.
Plan row: [COVER-CAP] (set S3), from [EARNED-SKIP]'s measurement (lane skipmeas,
2026-11-11). Built on: `kit_proof.md` §1.1 (the `cover_conj[]` table), `ctx_span.md`
§11 N-1, `offset_k_skip.md` §3.3. Compiler read: worktree at main `75d365a0b` (no `src/`
change since rev 1's `1b75dba61`; cites below are at that tree).

**REVISION 2 (owner's span model, Frank 2026-11-15).** Rev 1 removed the length limits
but KEPT the subset-exploring walk as the proof of exactness, with its 512-subset budget
and its cliff, and answered the kit's per-position text growth by offering run facts.
Frank rejected that model and stated his own: "there are two kinds of spans. exact spans
that can prove each position is exactly as the rx requires and the engine does not need
to retest, and hull positions that show the position is possibly matching but not
proven. the purpose of the hull positions is to get better candidates but the work is
thrown out. how far to go to get these is a judgement call. i would say that if the span
exceeds N positions, the hull is not needed. the hull positions can be used to extend a
short span and get something to filter candidates." Also recorded (journal 2026-11-15):
a span is an array of byte classes, a branch ends it, the walk is straight-line with no
budget (R-b); the kit is not told about repeated positions, it can loop and detect them
from the span it is passed (R-c); no bound on the exact span, and any constant left is
labelled and measured (R-d); pcrec states facts and never the kit's method (R-e, D157).

Rev 2 therefore:
- REPLACES the subset-exploring walk by a STRAIGHT walk that holds ONE thread subset per
  depth and ends at the first branch (§3.1). It has no budget and no length bound. It
  deletes the 2 x 24 horizon, the 24-deep exact loop and the `PCREC_SPAN_WALK_SUBSETS`
  limits row.
- RAN THE CENSUS FIRST (§2). Over 11,738 compiles (corpus + bench, both encodings),
  1,852 take the cover route today. The straight walk keeps 1,848 of them. The 4 it loses
  are 2 corpus test patterns, k <= 4, and none is a bench pattern. Every long fixed shape
  the cover is waiting for (the bench's l31/l40/hex32/uuid set, corpus `a{500}`,
  `[ab]{1000}`, `(?:ab|ba|aa|bb){24}c`, `(?:abc){20}`) is a straight line to its accept.
- TAKES THE HULL OFF the cover path (§3.3). A cover is exact by definition. The hull
  producer already exists (`kset_walk`), and its N is not built here.
- RE-SPELLS the kit request (§4.3) as capability: a counted span of any length, and
  compact text for repeated positions. No run facts, no form.

Rev 1's text is superseded in place. What survives from it is listed in §10.

## 0. Goals

Ranked; the higher goal wins a conflict.

1. **G1, answer identity (every caller).** No search, match or group answer moves on any
   corpus pattern, encoding or deny-flag arm. Form: `make test`, `make test-axes`
   (`--memfn=no-window-search` against default) and the new `test-kitproof` rows
   (libpcre2 10.46 answers, §5.3): all green, 0 answer differences.
2. **G2, only the predicted artifacts move (reviewers).** Every artifact outside the
   PREDICTED mover list (§6, built from the baseline, both directions, the 4 cover losses
   included) is byte-identical except for the `abi` stamp. Form: `scripts/emit_sweep.py`
   main-before against the candidate, predicted == observed.
3. **G3, no slower cell (bench users).** No mover cell is slower beyond the bench's A/A
   noise floor, in any regime or encoding. Form: §7. A loss gets the one-pass rule
   (memory `pcrec-one-pass-loss-chasing`), then an owner ruling, never a length cut-over.
4. **G4, no bound on the exact span (maintainers; R-b, R-d).** The exact-span producer has
   no length bound, no budget and no constant of its own. Its only limits are the
   machine's size and the pattern's own branches. Form: the §8 inventory has no pcrec-side
   row on the exact path marked INHERITED or BUDGET, and `limits.def` loses
   `PCREC_SPAN_WALK_SUBSETS`.
5. **G5, the long fixed shapes leave the engine (bench users with literals, hashes, ids
   and uuids of 25 or more positions).** The `lit-l31`, `lit-l40`, `hex32`, `dig-exact-32`,
   `hex32-id`, `uuid` and `wild-validator-uuid-grok` match cells get faster beyond noise,
   in both encodings. The expected size of the gain is the 24-position twin's
   cover/engine ratio, measured in §7 as one variable (UNMEASURED today).
6. **G6, size reported (reviewers, users with size budgets).** Each mover's C bytes and
   `gcc -O2` `.text`, before and after. How the text is made compact on repeated
   positions is the kit's call (R-c). Holds if no mover grows, or if the owner accepts
   each growth once the kit has answered §4.3 ask 2.

Non-goals: the hull and its N (§3.3); lookaround as a run ([REQ-LOOKAROUND], S4); a
trailing `$`/`\z` as a length compare; captures in a cover body (C1/C5 decline them, so
`wild-secrets-github-pat` (93) and `(ab){300}` stay on the engine); earned skip and
[MATCH-KNOWN] (PARKED); `PCREC_PREFIX_K_MAX` itself (§3.3).

## 1. The owner's model, mapped to the code

| the model | in pcrec today | rev 2 |
|---|---|---|
| EXACT span: every position proven, the engine does not retest | `span_facts` (`MkLang`, `pcrec_span_walk`, `src/facts/kset.c:853`). Its only decision reader is C8 of the cover table (`known.c` `cc_exact`). The listing and the trace build's SPANSET/X0 also read it | produced by the straight walk (§3.1), counted, with no bound |
| HULL positions: possibly matching, not proven, used for candidates, the work thrown out | `kset_walk` (`pcrec_kset_walk`, `kset.c:226`): the union of next bytes over every thread, assertions passed as if they held, out to `PCREC_PREFIX_K_MAX` (24) offsets. Read by the offset-k skip, `run_pin`, the reseed statement | unchanged. Not on the cover path (§3.3) |
| "a branch ends it" | no such rule. The subset walk proves branching prefixes exact by exploring them, up to 512 subsets and depth 48 | the definition of the straight walk's end (§3.1) |
| "how far to go [for the hull] is a judgement call"; "if the span exceeds N positions, the hull is not needed" | the hull's reach is 24, chosen in 2026-08 with headroom over a measured corpus maximum of 13 (`offset_k_skip.md` §3.3). No N exists | N is not built (no reader measures a need, D77). Filed with a trigger (§3.3) |
| the kit loops over repeated positions and finds them itself (R-c) | the kit renders one test per position (spanfacts report §4) | asked as a capability in §4.3. pcrec states no runs |

**The manager's reading, tested.** "Exactness needs no subset exploration, so no budget and
no cliff": confirmed by the census (§2). "The bounded walk that exists today survives, if
at all, only as the HULL producer": not so. The subset walk produces exact sets with
liveness, which is not a hull. The hull producer is `kset_walk`, which already exists. So
the subset walk has no remaining role and retires whole. "N is a constant to label and
measure": N belongs to the hull. With no consumer reading both the exact span and the hull
today, there is nothing to label yet (§3.3, §9 Q2).

## 2. Census (premise and classification)

PREMISE, at `75d365a0b`, `-p rx --features all`: `a{20}` lists `span_facts 20:...` and
`RX_DFA_SCAN "cover"`. `[0-9a-f]{32}` lists `24:...` and is not a cover (`why`
`fixed-width`, the M2 sentinel). Holds.

Method: a scratch copy of the tree with read-only probes in `pcrec_span_walk` and
`pcrec_cover` (not committed; the diff and the census script are in scratch, report §CENSUS).
The population is `bench_pop()` + `corpus_pop()` of `docs/dev/optloop/artrev/gen/census.py`.
Each distinct (pattern, encoding, icase) compiles under BOTH encodings at
`--features all`: 11,738 compiles, 10,795 of them ok. Wall time was 31-48 s per pass
(8 workers), so the census is not a heavy sweep.

| population | ok compiles | cover today | one THREAD per depth | one SUBSET per depth, exact liveness | one SUBSET per depth, rev 2's liveness (§3.1) |
|---|---|---|---|---|---|
| bench byte | 331 | 84 | 84 | 84 | 84 |
| bench utf8 | 335 | 62 | 62 | 62 | 62 |
| corpus byte | 5,029 | 1,025 | 1,009 | 1,023 | 1,022 |
| corpus utf8 | 5,100 | 681 | 668 | 681 | 680 |
| **total** | 10,795 | **1,852** | 1,823 (29 lost, 1.6%) | 1,850 (2 lost) | **1,848 (4 lost, 0.2%)** |

- **STRAIGHT vs BRANCHING.** Read as one NFA thread per depth, 29 cover compiles (16
  distinct corpus patterns, k = 1..4) are BRANCHING. All 16 are lazy or zero-width test
  shapes (`a*?a`, `ab|abc|ad`, `(?:(?!a)z|w)`, `a??(?:\b|)a`, ...). None is a bench
  pattern. That is under the 10% STOP threshold. Read as one SUBSET of threads per depth,
  only 2 remain BRANCHING: `tests/litscan/reqcube.rxt:29` and `:48`,
  `(?:S(?i:ab)|(?i:sab))` (byte, k 3). There, after `S` and after `s`, two different
  subsets have equal languages. Rev 2's liveness rule (§3.1) adds one more pattern,
  `tests/assertions/view_edge.rxt:2607` `(?:[a-z]{0,3}\z|x)[0-9]{3}` (both encodings,
  k 4). Its side branch is dead only through `\z`, which the rule leaves undecided.
- **`(?:ab|ba|aa|bb){11}c` is a straight line today**, even one thread per depth.
  altcls's sibling MERGE (`alt_normal_form.md`) rewrites it to `[ab][ab]`. The morning's
  spanfacts report inferred the prefix-factored `a[ab]|b[ab]`, but that is what
  `-fno-altcls-merge` builds: then the cover still holds by the subset walk, and the
  straight walk declines it (one deny arm's mover, §6).
- **The anchored DFA is one row per depth on all 1,852 covers.** So the machine reading
  (C7) is itself a straight line on every cover today.
- **Every long fixed shape is a straight line to its accept** (straight length = width):
  bench `lit-l31` 31, `lit-l40` 40, `hex32`/`dig-exact-32`/`hex32-id` 32, `uuid` and
  `wild-validator-uuid-grok` 36, `wild-secrets-github-pat` 93 (capture: C1). Corpus:
  `litrun.rxt:1204` 31, `:1320` 32, `spanarms.rxt:96` `(?:abc){20}` 60,
  `counterk.rxt:1919` 49, `d27_large_counts.rxt:6` `a{500}` 500, `:37` `[ab]{1000}` 1000,
  `:29` `(ab){300}` 600 (capture). All of them, under both encodings.
- **The listing (`span_facts` values)** moves on 297 of 5,680 compiles that list it: 76 grow
  (the long shapes, now unbounded) and 221 shrink (branching prefixes the subset walk proved
  exact). Of the shrinks, 109 end at an undecided side branch, 75 have an undecided line and
  37 differ by one position. No decision reads a shrunk value except C8, whose losses are
  the 4 above.
- **The subset budget was a length cap in disguise.** A straight line uses one subset per
  position, so 512 subsets capped a literal near 511. `[ab]{1000}` lists 24 today, and its
  straight length is 1000.

## 3. The design

### 3.1 The exact span: one subset per depth, ending at the first branch

**FORM.** The walk reads `Job.nfa`, the wrapped forward NFA from `anch_start`: the same
machine today's slice and `kset_walk` read (E3, after altcls and the other tree passes;
spanfacts report §2). Its state at a depth is ONE thread subset: today's `SwSub` (entries
of node, restriction R and the end-after flag), closed by today's `sw_close`, which
decides every zero-width item exactly from the previous byte's class. The walk keeps
`sw_partition`, `sw_push`, `sw_close` and `sw_take`. It deletes the breadth-first
exploration, the liveness pass and the budget.

Why this form, against the alternatives the census priced:
- **One thread per depth** (the literal reading of "a branch ends it"): it loses 29 covers
  to branches that are not real. In `a*?a` the two threads move together. In
  `ab|abc|ad` the prefix `ab` is one deterministic path. A SUBSET is "where the pattern
  can be" after the bytes so far, so one subset per depth is exactly "no branch" in the
  sense of the language. It is determinization applied along the one path the line
  takes, which is the general rewrite the brief asks about, with no special case.
- **The anchored DFA** (straight on all 1,852): it would lose nothing, but the exact span
  would stop being a pattern fact (it would need a DFA route and the machine's views), and
  C8 would lose its second machine (§3.6 Q2).
- **The AST after rewrites**: priority, laziness and the items are lowered by the NFA
  build. Reading them again from the tree states them twice (the D163 rule for one
  source per fact).

**THE WALK.** Write U_d for the line's subset at depth d.

1. Roots: the origin's closure under every context before it (each byte class, and the
   subject start), as today. The live roots must be ONE subset. Otherwise the start
   depends on the context, and `exact_len` is 0 (111 listing compiles, 0 covers).
2. At depth d: if U_d accepts, the line ENDS (`accept`) and `exact_len = d`. If U_d is
   opaque (`\G`, `N_CSTART`), it ends with `exact_len = d`.
3. Otherwise take U_d's successor per byte class (`sw_close` + `sw_take`) and drop the
   SURELY DEAD ones (liveness below).
   - No successor: the line is dead and `exact_len` is 0.
   - One successor: `S_d` is the bytes that lead to it, and the walk goes on to d + 1. If
     that successor is a subset already on the line, the line is a cycle with no exit:
     dead, `exact_len` 0.
   - Two or more (THE BRANCH): if every one is decided SURELY LIVE, `S_d` is their union
     and `exact_len = d + 1`. If some are undecided and one is surely live,
     `exact_len = d`. If none is surely live, the line's own liveness is undecided, and
     `exact_len` is 0.

**LIVENESS, with no exploration.** Two backward passes over the NFA, each linear, once
per compile:
- POSSIBLY LIVE: the state reaches `N_ACCEPT` with every item passed as though it held.
  Failing this proves the state dead.
- SURELY LIVE: the state reaches `N_ACCEPT` through no item state (`N_EOL`, `N_CTX`,
  `N_GSTART`, `N_CSTART`), only through non-empty classes and epsilons. Such a path can
  always be spelled.

A side subset is SURELY LIVE if it accepts, or if some entry whose class meets its R has
a surely-live target. It is SURELY DEAD if no such entry has a possibly-live target.
Otherwise it is undecided. An end-after entry (the final `\n` of a `$`) counts as
undecided. The line's own subsets need no decision: the line's end decides them.

**SOUNDNESS** (the facts contract: an under-statement is sound, `facts.h:296`). Suppose
the line is live: it reaches its accept, or it reaches a decided branch with at least
one live successor. Then every byte that leads to the one continuing subset is a byte of
some match's prefix, and no byte that leads to a surely-dead subset is one. So `S_d` is
the true set for every d on the line. At a decided branch, every successor is live, so
the union is the true set. Every uncertain case ends the statement before the position
it would decide. The items are decided by `sw_close`, unchanged (`kit_proof.md` §R2.2's
true sets, the view-gated `\n` included). The census confirms it from the other side:
the rev 2 length never exceeds the exact-liveness length except where the subset walk's
budget left that length unknown (26 compiles, all budget-unknown). C8 compares the sets
with the DFA's on every cover, and the trace build asserts that they agree.

**TERMINATION AND COST.** Each step is one closure. The line holds distinct subsets (a
repeat ends it), so its length is at most the number of distinct subsets on one path.
That is the problem's own bound: for a whole cover it is the width, and in general it
can never pass the anchored machine's own state count for the same path. No constant is
introduced. Work is O(L x subset size), against today's O(512 x subset size) cap.
The cost is UNMEASURED as a comparison. The census passes (11,738 compiles each, the probes
included) took 31-48 s of wall time on 8 workers, so no compile was slow enough to show,
but no pass compared an old and a new binary. The build measures that with
`scripts/compile_time_census.py` (§5.1).

**WHAT IT DELETES:** P1, P2 and P4 (§8). The P4 row comes out of `limits.def`. `MkLang`
becomes a counted arena list (P3). Liveness ("decided by walking up to twice
`PCREC_PREFIX_K_MAX` levels within `PCREC_SPAN_WALK_SUBSETS` subsets", `kset.c:578`) is
replaced by the two passes. This is a simplification, and the census is its price list:
4 cover compiles (two corpus test patterns) and 221 listing values.

### 3.2 The machine reading walks as far as the slice (rev 1 §3.2, kept)

`kn_walk` (`known.c:126`) takes its horizon H from the slice's `exact_len`. C8 cannot
admit `k > exact_len`, so walking deeper could not change an admission. This bounds the
work on huge widths (`(?:a{1000}){1000}`). Its rows and sets become counted arena arrays
(M1, M4). Rows per depth are sized from the machine (M3). Rev 1's three explicit outcomes
replace the `KN_CAP` sentinel. At each depth `j <= H`: (1) no rows, or `ended` at `j-1`:
`k = j`. (2) A row accepts in any form: `k = j`. (3) The loop ends at `H` with neither:
`k = H + 1`, and C8 declines it `exact/producer-short`. `kn_walk` keeps its general
multi-row form. It is C8's second machine, and on every cover today it holds one row per
depth (§2).

### 3.3 The hull: not on the cover path

A cover is REPORT: every position is proven, and the engine never retests. The hull has
nothing to add there. So rev 2 changes nothing on the hull side:
- `kset_walk` stays the hull producer, with its reach `PCREC_PREFIX_K_MAX` (24), and that
  limits row keeps its label ("chosen with headroom over a measured corpus maximum of
  13"). Its other borrowers (`run_pin`'s `0:0+24` clip, the reseed statement,
  `MF_WMAX_SPAN`'s derivation) are rev 1's PREMISE-7 family. They stay a plan row for
  main, at BOONIES unless a measurement names one.
- **N is not built.** No consumer today reads both the exact span and the hull, so "do
  not compute the hull past an exact span of N" has no reader. Filed (for main) as a row
  with a TRIGGER: the first FIND-site statement that offers the kit an exact span
  extended by hull positions (verify-NO positions after verify-YES ones, the form
  `memfn.h`'s window site already has). At that point N is a labelled UNMEASURED
  constant, with a measurement that compares candidate rate and find cost against the
  exact length (§9 Q2).
- Under UTF-8, a multi-byte class branches on its lead byte. `[а-я]{4}` lists `1:` under
  both walks, while `асд{3}x` is a straight line (11). Whether such classes are where the
  hull "extends a short span" is §9 Q3.

### 3.4 Two stages (rev 1 §3.5, kept)

- **Stage 1 (pcrec only, today's seam).** §3.1-§3.2, plus the conjunct
  `C15 statement-fits` (kind `seam`, read right after C7): `k <= MF_WSPAN_POS`,
  `k + 1 <= MF_WREACH`, `k < MF_MAX_FWD`, all read from the kit's own constants. It exists
  so that `cover_window` (`known.c:462`) never writes past `mf_wspan.set[]` (K7).
  pcrec has no bound of its own. Movers: shapes of 25..32 positions.
- **Stage 2 (with the kit's delivery of §4.3).** A counted seam. C15 is RETIRED, the way
  C2 was: its id stays, absent. `cover_window` and `pcrec_cover_proof_diff`
  (`known.c:510`) read the counted lists. Movers: every straight line.

Each stage is one pcrec `abi` event (§4.4).

### 3.5 The standing questions

1. **Measurement regime: RELEVANT** for G3, G5 and G6 (§7). No decision here depends on
   the regime: the cover is answer-identical by proof. The census counts compiles and
   reads no clock.
2. **Independent control: RELEVANT.** The selection widens, and the producer is replaced.
   The checks, and what each is checked against: libpcre2 10.46 (kitproof answers, X0);
   the engine route of the same compiler (the axes deny arm); the anchored DFA against
   the NFA straight walk (C8, two machines with two constructions: the DFA by full
   subset construction and minimization, the line by one path's subsets). The mover
   prediction comes from the BASELINE build's records (§5.2). This census used a probe in
   the same functions it measures. It is a classification, not a control, and §5's checks
   do not reuse it. K35: the sweep counts the whole population, and the kitproof floors
   rise by the rows added. [MECH-REACH]: each plant names its witness, and the build
   checks the witness's reach on the clean tree.
3. **What moves on regeneration: RELEVANT.** `limits.def` LOSES the
   `PCREC_SPAN_WALK_SUBSETS` row. So the `--list-limits` text, `internal.h`'s generated
   block and `tests/registry/limits_check.sh`'s name manifest all move, by grep, in the
   same change. Regenerated by the build: `tests/kitproof/answers.tsv`
   (`gen_answers.sh`), the start-set mover manifest (`manifest_s3_dfa.tsv`) and the
   recursion identity gate's pins (§4.4). Not regenerated:
   `docs/dev/artifact_size_log.tsv` (a separate gate commit), and kvcensus's committed
   tables (their `span` column is capped at 32 and is already stale, per its CLAUDE.md).

## 4. The seam, and the kit request draft

### 4.1 What pcrec needs across the seam (facts)

- pcrec STATES one window span of `k` positions, for any `k >= 1`, plus one context
  position before it (offset -1) and one after it (offset `k`).
- pcrec READS, for every offset in `[-1, k]`, the set the kit's text tests there, and
  checks that it EQUALS the statement (C14, `pcrec_cover_proof_diff`). Today that range
  ends at `MF_MAX_FWD` (33).
- pcrec READS the reply's `stop` (`req_run_at`). It reads nothing else in `mf_wreply` on
  the cover path.

### 4.2 pcrec's side (stage 2)

`cover_window` states the span in the counted form the kit chooses, taking its sets from
`MkEnd`'s counted array. `pcrec_cover_proof_diff` loops over the reply's counted proof
range. `window_bounds_check` mirrors the kit's new statement check. C15 is retired. M6
(`pcrec_known_derive`, no caller) is either bounded by the counted range or deleted; the
build picks, and either is two lines. The other window sites (OFS, reseed, the run
pre-check) state what they state today, and the sweep proves them byte-identical.

### 4.3 KIT REQUEST DRAFT (for main to file; facts only, D157; no build go)

> **R-n (DRAFT, pcrec manager) — a window span of any length ([COVER-CAP] rev 2)**
> - GO: none yet. File on main's call. The kit-side build waits on the owner's go for
>   stage 2 (§9 Q4).
> - FACT 1. pcrec will state the cover's REPORT window site with span 0 of `k` exact
>   positions. `k` is the length of the pattern's exact straight prefix, which has NO
>   upper bound on pcrec's side. Population today (census, both encodings): 31 and 32
>   (`lit-l31`, `hex32`, `dig-exact-32`, `hex32-id`, two corpus literals), 36 (two
>   uuids), 40 (`lit-l40`), 49, 60, 500, 1000 (corpus). Each has one context position at
>   -1 and, where stated, one at offset `k`.
> - FACT 2. pcrec reads the per-offset proof at every offset in `[-1, k]` and checks that
>   it EQUALS its statement. Today the proof range ends at `MF_MAX_FWD` = 33, and the
>   statement is refused past `MF_WSPAN_POS` = 32 and past `MF_WREACH` = 64.
> - FACT 3. On these spans many consecutive positions carry one set. The measured cover
>   text grows by about 8 (`[0-9a-f]`, byte), 25 (utf8) and 20-31 (`\b`-bounded)
>   `gcc -O2 -S` lines per position, against a flat engine (`cover_cap.md` rev 1 §3.4's
>   table, same pattern, cover vs `--memfn=no-window-search`).
> - THE BOUNDS ON THIS PATH, as pcrec reads them (yours to keep, move or label): the
>   statement's `MF_WSPAN_POS` (= `MF_MAX_TERM`, from emit_vm's `VM_MAX_STRIDE`; a REPORT
>   site is never translated to terms), its `uint8_t` lengths and fixed arrays, `MF_WREACH`,
>   the reply's `MF_MAX_FWD` and `MF_WPLAN_MAX`, and window.c's `WF_NPOS`, `uint8_t` shift
>   and `run_bytes` buffer (`cover_cap.md` §8).
> - ASK 1. Can the statement and the reply carry a span of any length? Reply in
>   responses.md with the form you choose. It is an `MF_SITE_ABI` event, and an
>   `MF_CLASS_V` event where the reply moves.
> - ASK 2. Can your text for a span stay compact where consecutive positions repeat a
>   set? pcrec does not mark repeats: they are in the span you are passed. Say the
>   run-time cost of the form you choose, and confirm or correct FACT 3.
> - ASK 3. G2 cases past 32 positions, at lengths you choose.
> - pcrec's side (ours): counted `MkEnd`/`MkLang`, C15 retired, the proof check over the
>   counted range, one pcrec `abi` event in the same landing.
> - Deliver: a kit branch for merge review, for one landing with pcrec's stage 2.

### 4.4 The `abi` events (rev 1 §4.4, kept)

Both stages are pcrec `abi` events. Each needs a bump, a re-pin of the recursion
identity gate's pins, a `docs/dev/history/abi_changelog.md` entry, D94's grep of every
reader of the current number, and the suites that count (registry, codegen, rxtsource).
The gate's D76 block says that (B)'s pin "IS, by definition, the commit that introduced
the CURRENT `abi`". (B) compares whole files over every call-free corpus pattern, and the
corpus movers of §6 are in that population, in both directions now (the 4 losses
included). Stage 2 also moves kit bytes, which D146/D147 make a pcrec abi event in the
same commit. (A), the program region, is empty on DFA artifacts.

### 4.5 Spec (D80), in the same change

- `facts_listing.md` §4.1.2¶7c: `L` is the length of the straight prefix. The walk ends at
  the first depth where the pattern's possible continuations are not one, where a
  continuation's liveness is not decided, or at a match end. It has no length bound. The
  sentence about the walk's budget goes. The product definition ("the matches'
  length-(d+1) prefixes are exactly the product") is unchanged: rev 2 states less or
  more of it, never something else.
- `cli.md` §2.6 (`--list-limits`): the `PCREC_SPAN_WALK_SUBSETS` row is removed.
- `match_api.md` §6.3.4¶2's `"cover"` row names no bound, and stays as it is.
- The abi changelog entry is §4.4's.

## 5. Answer-identity plan

### 5.1 The checks, and what each is checked against (rev 1 §5.1, adapted)

| check | against | proves |
|---|---|---|
| `make test` (both encodings) | oracle-verified expectations | every mover's cases answer as before, through the cover or the engine |
| `make test-axes` | the same compiler under `--memfn=no-window-search` (`tuning.md` §2.43¶3d) | cover against engine on every corpus subject |
| `test-kitproof`, new rows (§5.3) | libpcre2 10.46 (`answers.tsv`) | the boundaries at every startoffset, and find-all |
| `pcrec_cover_proof_diff` (an internal error on any difference) | the kit's proof against the statement | the kit proves exactly what pcrec states, at every `k` |
| trace build: C8 `producers-disagree` assert; X0 on the movers' SPANSET records | the anchored DFA; libpcre2's sets | the straight walk's sets where the DFA reads them, and past 24 positions, where the hull control M8 stops |
| `make asan` over the kitproof and litscan sections | AddressSanitizer | the counted arrays (P3, M1, M4, K1-K5) |
| `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh` | the clean tree | every kitproof witness still reaches its site |
| `scripts/compile_time_census.py`, old binary against new | child CPU time | §3.1's cost claim, over its population |

### 5.2 Byte identity and the mover list (G2)

`scripts/emit_sweep.py --trace`, main-before as baseline against the candidate, over the
committed population. Everything is byte-identical except the `abi` stamp (normalized on
both sides, named in the deliverable) and the movers. The PREDICTED list comes from the
baseline's trace records, in both directions: INTO the cover, every decision whose `why`
is `fixed-width` or `exact/producer-short` with `width` `[k,k]`, `k >= 25` (kept to
`k <= 32` at stage 1), whose straight length reaches `k`; OUT of it, the 4 of §2. The check
is predicted == observed. Every exception is listed with the candidate's `why`. The listing
movers (§2: 76 grow, 221 shrink) are predicted the same way, from the baseline's
`span_facts` and the census's classification, and checked as predicted == observed.

### 5.3 New witnesses (`tests/kitproof/cases.tsv`)

- `verdict`: a literal and `[0-9a-f]{n}` at 24, 25, 32, 33, 40, 100 and 1000;
  `\b[0-9a-f]{n}\b` at 32, 40 and 100; `\d{32}` under `u`. Stage 1: cover through 32,
  decline from 33 (C15). Stage 2: cover at every length. `ab|abc|ad` stays a cover (the
  one-subset witness). `(?:S(?i:ab)|(?i:sab))` declines `exact/producer-short` (a
  recorded loss). A body ending in a view-gated final newline (the `ended` path) is
  recorded with its observed `why`.
- `facts` (`span_facts`): 40-literal `40:`, 100-literal `100:`, 1000-literal `1000:`,
  `a{30}(?:b{30}c|d)` `31:`, `ab|abc|ad` `2:97,[2]`, `a*?a` `1:97`,
  `(?:[a-z]{0,3}\z|x)[0-9]{3}` `0` (undecided liveness), `[ab]*\z\W` `0` (the line's
  cycle).
- `answer`: at each length `n`, subjects of `n-1`, `n` and `n+1` bytes; a near miss at
  the last position; a match at the subject end; two adjacent matches; every
  startoffset. Expectations from libpcre2 via `gen_answers.sh`.
- The floors (24 verdict / 6 facts / 55 answer rows) rise by the rows added.

### 5.4 Sabotage rows (mech arm `kitproof`), each with a unique witness

| plant | what it restores or breaks | unique witness | why only it flips |
|---|---|---|---|
| (a) a length bound back on the walk (`d < 32`) | P1 | `facts` 40-literal `40:` → `32:` | (b)-(e) leave every literal intact |
| (b) one THREAD per depth instead of one subset | the census's 29 | `facts` `ab\|abc\|ad` `2:97,[2]` → `1:97` | (a) and (c)-(e) agree with the subset reading there |
| (c) an undecided successor treated as live | §3.1's liveness | `facts` `(?:[a-z]{0,3}\z\|x)[0-9]{3}` `0` → a nonzero value (PREDICTED `1:[27]`; the build records the observed one) | nothing else states a position past an undecided branch |
| (d) the machine walk stops one depth short (`j < H`) | rev 1's M2 off-by-one | `verdict` 25-literal cover → decline | (a)-(c) leave a 25-literal's statement whole |
| (e) stage 1 only: C15 removed | K7 | the 40-literal compile goes red (`window_bounds_check`'s internal error; under ASAN, the overflow) | nothing else reaches a 40-position statement at stage 1 |

A plant that drops the cycle rule hangs the walk. The suite's timeout catches it, and
`[ab]*\z\W` is its witness row, not a matrix row. The sabotage ids are the build's to take.

## 6. Movers (census, both encodings; the sweep's count is the count of record)

| population | stage 1 (k <= 32) | stage 2 (any k) |
|---|---|---|
| bench, into the cover | `lit-l31`, `hex32`, `dig-exact-32`, `hex32-id`: 4 x 2 | + `lit-l40`, `loglines/uuid`, `wild-validator-uuid-grok`: 7 x 2 |
| corpus, into the cover | `litrun.rxt:1204` (31), `:1320` (32): 2 x 2 | + `counterk.rxt:1919` (49), `spanarms.rxt:96` (60), `d27_large_counts.rxt:6` (500), `:37` (1000): 6 x 2 |
| out of the cover (answers unchanged) | `reqcube.rxt:29`, `:48` (byte); `view_edge.rxt:2607` (both): 4 compiles | same |
| not moving | `wild-secrets-github-pat`, `(ab){300}` (captures, C1/C5); `uuid-near-miss` (attempt route); variable widths | same |
| deny arm `-fno-altcls-merge` | `(?:ab\|ba\|aa\|bb){11}c` leaves the cover on that arm only (answers unchanged; `test-axes` compares answers) | same |
| outside the population | `(?i)permission is hereby granted` (28), byte only (PREMISE-3) | + `req-<uuid>` (40) |
| listing only | the 221 shrinks, and the grows up to 32 | all 76 grows |

## 7. Re-timing plan (rev 1 §7, kept; not run)

Cells are generated from §5.2's OBSERVED movers x the bench's regimes x both encodings x
each cell's subject families, and confirmed with the bench dev. Before and after differ
in one variable: main at the build's base against main with the stage, on the same box,
pin, toolchain and night. A/A controls: `lit-l16` and one non-mover engine cell, on
hit-dense and hit-sparse subjects. G5's expectation is the 24-position twins, default
against `--memfn=no-window-search`, on the before compiler. Read `fbf` and
`short-subject-search` first, because class covers grow with `k` until the kit answers
ask 2. Size (G6) is read from the same build. The window is at night, cleared with Frank,
outside 20:00-01:00, after each stage lands.

## 8. The bounds on the cover path (rev 1 §1, condensed; rev 2 verdicts)

Rev 1 §1's end-to-end inventory (in git at `75d365a0b`) stands for its sites and cites. Rev 2 changes only the
verdicts on pcrec's side:
- GONE: P1, the exact loop `d < PCREC_PREFIX_K_MAX` (`kset.c:911`, INHERITED); P2, the
  horizon `2 * PCREC_PREFIX_K_MAX` (`kset.c:891`, INHERITED); P4,
  `PCREC_SPAN_WALK_SUBSETS` (`limits.def:393`, a BUDGET and a length cliff near 511, the
  row deleted); M1, `KN_CAP` (`known.c:34`, INHERITED from the kit's term bound).
- COUNTED: P3, `MkLang.set[24][32]` and `uint8_t exact_len` (`facts.h:305-306`); M4, `MkEnd`
  (`known.h:24`, `:28`). M3, the rows per depth (`known.c:129`), is sized from the machine.
- REPLACED: M2, the sentinel (`known.c:132`, `:250`), becomes the three outcomes of §3.2.
- At stage 2: M5, the proof loop (`known.c:510`), and M6 (`pcrec_known_derive`, no
  caller) read the reply's counted range.
- Unchanged: P5 (256 byte values, OWN), M7-M9 (length-driven; M8 is the hull's reach).
  The seam's K1-K7 (`MF_WSPAN_POS` 32, the `uint8_t` lengths, `MF_WREACH` 64,
  `MF_MAX_FWD` 33, `MF_WPLAN_MAX` 72, `MF_WMAX_SPAN`, pcrec's mirror) are read by C15 at
  stage 1 and are the kit's call at stage 2. The kit's own W1-W5 are the kit's (D157).
- Adjacent, not on this path: `PCREC_PREFIX_K_MAX` (the hull's reach, §3.3),
  `PCREC_MAX_REQ_RUN_SCAN` (32, which maps into a cover of any length) and `MF_MAX_BACK` (8).

## 9. Questions for the owner (plain words)

1. **Losing four tiny covers for the simpler walk.** The straight walk keeps 1,848 of
   today's 1,852 covers. It loses four compiles of two test patterns,
   `(?:S(?i:ab)|(?i:sab))` (three letters, where two branches meet without the walk
   seeing it) and `(?:[a-z]{0,3}\z|x)[0-9]{3}` (four positions, where proving one branch
   dead would need the exploration being removed). Those go back to the engine with the
   same answers. In exchange, the 512-step budget, its hidden length limit near 511, and
   the exploration code are all deleted. Leaning: accept.
2. **The hull and its N stay out of this change.** A cover is fully proven, so hull
   positions add nothing to it. The hull code that exists (the k-set walk, 24 positions)
   stays as it is, and "skip the hull past N exact positions" waits until something
   offers the kit an exact span extended by hull positions. Then N gets a label and a
   measurement. Leaning: yes, filed with that trigger.
3. **What you meant by "hull only for UTF-8, later".** My reading: under UTF-8, a
   multi-byte character class (Cyrillic `[а-я]`, say) is a branch on its first byte, so
   the exact span stops there, and hull positions are what could carry the filter on past
   it. A Cyrillic LITERAL is still a straight line and covers today. Is that the case you
   meant, as a later item? Leaning: yes, a separate row after this one.
4. **One step or two** (from revision 1, not yet answered). Step one changes only pcrec and
   covers up to 32 positions, which is what the kit's interface carries today. That moves
   `lit-l31`, the 32-character hex and digit shapes, and `hex32-id`. Step two needs the
   kit to accept a span of any length, and then the uuids, `lit-l40` and the long corpus
   shapes move too. Leaning: two steps. The first gain comes sooner, and its timing is
   the evidence for the kit's work.
5. **Build go** for stage 1 (§3.1-§3.2 plus C15, with §5 as the delivery bar), at opus
   tier (facts and engine code). Stage 2 gets its own go once the kit replies.

For main, not the owner: [DD-11.5] (STARTED) adds a producer into the same `MkLang`, and
its next step should rebase on the counted form. [DEC-LIMITS]'s trigger ("the next new
limit") does not fire, because a row is removed, not added. The N row (§3.3) and
PREMISE-7's family row are for main to file.

## 10. What rev 1 parts survive

- KEPT: the bounds inventory (§8, condensed), the premise (§2, re-tested), the machine
  reading (§3.2), the two stages and C15 (§3.4), the abi events (§4.4), the spec hunk
  (§4.5, which now also removes a `--list-limits` row), the checks and the sweep (§5.1-5.2),
  the re-timing (§7).
- REPLACED: rev 1 §3.1 and §3.3 (the slice explores up to the budget; the budget and its
  cliff), by §3.1 (the owner's model).
- ADAPTED: the witnesses and plants (§5.3-5.4: plants (b) and (c) are new, and the horizon
  plant goes with the horizon); the movers (§6, from the census, both directions).
- DROPPED: rev 1 §3.4's answer to size ("pcrec states runs") and the request's FACT 3/FACT 4
  (run and table offers), by R-c and R-e. The size measurements are kept as FACT 3. Rev 1
  owner questions 2 (size) and 3 (budget) are answered by R-c and R-d.
- Rev 0's critic dispositions stand as recorded in `docs/dev/reviews/2026-11-15-r2-covcap0.md`.
  SOUND-1 and SOUND-2 (the horizon) are moot, since there is no horizon.
