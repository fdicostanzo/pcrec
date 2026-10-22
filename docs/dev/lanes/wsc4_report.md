# wsc4 — D172 S2 commit 4: the two-phase ask under the lever

Lane wsc4 (kit lane of the memfn kit manager), 2026-10-22. Worktree `worktrees/wsc4`, branch
`lane/memfn-wsc4`, cut from `lane/memfn-wsc3` @ e8e79d3ba. Build go: Frank's conditional go for D172
(critics GO, main agreed; request R-29), as for wsc1-wsc3. Design: `docs/design/memfn/window_site.md`
rev 3.2 §2.4, §3.4, §3.5, §5.1 commit 4. No rulings file was named.

STATE AT HANDOFF:
- **Commits:** one pcrec-path code commit, one check commit, this report's commit (§1). No kit-path
  commit: the reply already carries every field the NEXT keys read (§2).
- **The lever** is the harness option `--harness=window-reply` (`build/pcrec-harness` only). The
  default path is unchanged; the lever's default flips at commit 5.
- **Light checks:** green at the code tip (§5).
- **Owed:** the heavy job `579-kit-wsc4-heavy` is QUEUED (§7).

## 1. The commits

| # | sha | path class | what |
|---|---|---|---|
| (a) | 9329ac05b | PCREC PATH (src/, cli/ only) | the lever; the phase-1 ask; the NEXT keys as a declared map; the RE-SEED refusal; the offset-set guard |
| (b) | 8000da2db | pcrec-side TEST (tests/memfn/ only) | `tests/memfn/run_wreply.sh`, the lever check and its plants S1412-S1414; `tests/memfn/CLAUDE.md` |
| (c) | this commit | docs (`docs/dev/lanes/`, the lane index, the kit journal) | this report |

Main reviews (a): it touches no file under `memfn/`, `tests/` or `docs/`.

## 2. What (a) does

**The lever** (`PcrecHarnessOptions.window_reply`, `pcrec_window_reply_lever`, src/core/internal.h;
cli/main.c). At art setup the art previews the kit's `"window-family"` (src/gen/memfn_sites.c, beside
kit-proof's R-26.6). An art previews one step, so the two levers together are refused loudly.

Under the preview, every site stating window facts is decided and rendered by the family: that is
PHASE 2 (pcrec states the frame its NEXT row chose, the kit writes the text). The frames are today's;
no frame code changed.

**Phase 1** (`window_reply_ask`, emit_dfa.c). `unanch_start` asks `mf_wdecide` over the DFA
prefilter's statement once per start analysis, where `kind` is not NONE and only under the lever.
- The statement is the offset-skip block's: k0 parked, the D11 bound where the machine has one.
- It now has ONE derivation, `ofs_window_of`, read by both the block's define and the ask.
- The reply and the chosen alternative's ENTRY are kept in `UnanchStart.wr` / `wr_entry`, which every
  selection of the machine reads (the body path and the stamp path alike).
- The statement's facts are read with the `_stated` accessors, after prefix_k weighed the walk, as at
  commit 2, so no fact's `used` record moves.

**What pcrec computes:** nothing new. It states R-29's facts (unchanged since wsc3) and reads the
reply's fields `alt` (through the statement's entry), `reseed`, `pinned` and `path` (the refusal
text). No rank, pick, plan or member is computed (D157).

## 3. The mapping table (reply field → NEXT predicate)

`next_keys[]` in src/gen/emit_dfa.c, read by `next_key_holds`. Off the lever each key is today's
clause (`pick`); under it, the reply's declared field values (`WR_ANY`: not read).

| key | rows | off the lever (`pick`) | under the lever: ENTRY | RE-SEED | C-pin |
|---|---|---|---|---|---|
| NK_RUN_PINNED | `run-pinned`, `run-pinned-bounded` | clauses (3)-(4): the model's scan is the pin's member; the model does not test all of R | any | 1 | 1 |
| NK_OFFSET_SET | `offset-set`, `offset-set-bounded` | `ofsk.nsel > 0` | RESEED | 1 | any |
| (none) | rows 5-13 (`handoff` … `none`) | first-match order | first-match order: reached exactly where the reply chose PARKED without C-pin | | |

What stays outside the key, as before:
- Clause (0) on every offset row: the forward scan and an offset-0 prefilter (`kind`), facts of the
  machine.
- On the run rows, clauses (1)-(2): a necessary run exists and the walk pins it. They are facts of the
  run, asked as today so the facts' `used` record is the same either side of the lever. The reply can
  carry C-pin only where they hold, since R is stated only then.
- The deny bits are unchanged (rows removed by `-fno-offset-skip` / `-fno-run-prefilter`). Under
  either deny pcrec states no R, so no reply carries C-pin (§2.4, V2): the statement's code is
  wsc2/wsc3's, unchanged.

**The RE-SEED bit (§3.5).** In `dfa_form_derive`, a reply whose RE-SEED is set that reaches a NEXT row
which does not re-seed (`u.pf.reseeds` false) is a loud internal error naming the path and the row.

**The guard for the old readers.** The tables, the block's `OfsTest` and the OFFSETS stamp still read
the planner's selection until commit 6 (`ofs_test_of`). An offset-set row reached on a machine the
planner selected no offset for is therefore a loud internal error, never a silent render over an empty
selection.

## 4. The witnesses

### 4.1 Lever ON vs OFF

`tests/memfn/run_wreply.sh` (default mode, about 10 s):
1. **Identity.** 13 witnesses × 5 flag sets (default, `--engine=vm`, `-fno-offset-skip`,
   `-fno-run-prefilter`, `-fmemfn-simd`) = 65 cases: build/pcrec against build/pcrec-harness
   `--harness=window-reply`, artifact + stderr + rc. Each witness's `DFA_PREFILTER` stamp is held to
   its row, with floors per key: offset-set 3, offset-set-bounded 2, run-pinned 3 (RESEED + C-pin and
   PARKED + C-pin), run-pinned-bounded 2 (both entries).
2. **Reach.** A copy of the tree is built with the statement PERTURBED. The perturbation moves the
   reply and never the pick: the default path does not read the statement.
   - P-a (RESEED unstated): under the lever no witness may stamp an offset-set row. 5 offset-set
     witnesses move off the offset rows. Lever OFF, every witness stamps its row.
   - P-b (R stated under `-fno-run-prefilter`): `xy.*xy(?i:z)` (PARKED + C-pin) is REFUSED for
     RE-SEED under the lever (NEXT reaches `memchr`). Lever OFF compiles it.

Identity alone could not tell "NEXT reads the reply" from "NEXT reads the pick": the two agree on
every artifact (the shadow's zero). The perturbed copy is what makes the reply load-bearing and
visible.

**The corpus-wide identity** is `run_wreply.sh --sweep ARGS`: scripts/emit_sweep.py with the lever
binary as the working side, through a two-line wrapper (emit_sweep's `--extra` would reach both
sides, and the ref build has no such option). It runs in the heavy job against 3cd809da1, beside the
plain sweep against the same ref, so lever ON = ref = lever OFF on every stream (§7). Commit 5 reruns
it. A `--limit 10` plumbing run against `--ref-bin build/pcrec` read `movers=0` on every stream.

### 4.2 The plants (`run_wreply.sh --plants`)

| id | the defect | caught by | result |
|---|---|---|---|
| S1412 | a NEXT row reads the planner's pick under the lever (`next_key_holds` ignores the reply) | P-a | RED: `uuid` stamps `offset-set` with no RESEED alternative stated |
| S1413 | the RE-SEED bit ignored where it reaches a non-re-seeding row | P-b | RED: `xy.*xy(?i:z) [-fno-run-prefilter]` compiles, stamp `memchr`, rc 0 |
| S1414 | the run-pinned key does not read C-pin | identity | RED: `in\|instanceof` differs across the lever (class A takes run-pinned) |

### 4.3 The shadow

`memfn/tests/wshadow.py --every 80` at the code tip: 73 patterns, 146 compiles, 100 window sites (8
pre-check parts). Mismatches 0 on every column (reseed, stop, plan, pin, group, arm, text). Paths:
mass 53, mass+pin 8, parked 32, parked+pin 1, reseed 6. The FULL shadow (with `--g2`) is in the heavy
job (§7). Log: `build/wsc4/light_a/wshadow.log`.

## 5. Light checks (Linux dev box, gcc 15.2; code tip 8000da2db = (a)'s product tree; logs `build/wsc4/light_a/`)

| check | result |
|---|---|
| `make strict` | clean (also before (a)'s commit) |
| sabotage anchors (`scripts/m6read_check_sab_anchors.py`) | 901 rows / 932 sites, all resolve |
| `tests/codegen/run_codegen_tests.sh` | 331 passed, 0 failed |
| `make test-core` | rc 0 |
| `make test-memfn-{link,manifest,stamps,arms,deleg,arch,forms,reach,rows,finder,rank,guarded,simdfloor,g2}` | each rc 0 (g2 quick: 71,217,801 passed, 0 failed) |
| `memfn/tests/run_g2_win.sh` | 6032 passed, 0 failed |
| `tests/memfn/run_wreply.sh` | 125 passed, 0 failed (65 identity cases; P-a moved 5; P-b refused) |
| `run_wreply.sh --plants` | 3 of 3 RED (§4.2) |
| wshadow `--every 80` | 0 on every column (§4.3) |
| hand sample before the check existed | 19 patterns × 4 flag sets = 76 triples, lever ON vs OFF: 0 differ; 38 against the pre-change build: 0 differ |

(b) adds only `tests/memfn/`; the product tree is (a)'s, so one run covers both commits. After the
light run, `run_wreply.sh` gained its box-lock wrapper (W4-3); the heavy job runs the edited script
in default mode and with `--plants`.

## 6. Findings, deviations, and notes for commits 5 and 6

**W4-1, the statement phase 1 reads (a reading, for the kit manager).** NEXT reads the reply to the
OFFSET-SKIP BLOCK's statement (k0 parked), not the PF site's.
- On the DFA hat the PF site states T parked (wsc3 D-2). The offset rows sit above the hat, and
  prefix_k weighs k0, so the k0 statement is the one whose reply chooses between them.
- The PF site's own statement is still decided by the family at phase 2, when its row renders.
- The shadow compared the k0 statement against the pick only where an offset row was taken today (the
  block is defined only then). On a hat machine whose pick is PARKED, the k0 statement's decision was
  never shadowed. The lever sweep covers it: a RESEED reply there would trip the offset-set guard (§3)
  loudly.

**W4-2, the facts' `used` record is a second reader of the old predicate.** `--emit-facts` lists which
facts a predicate ASKED. Today's run predicate asks `req_run` before any clause and `run_pin` after
clauses (0)-(1).
- Under the lever both are still asked, in the same order (clauses (1)-(2) stay outside the key; §3),
  so the `facts` stream cannot move across the lever.
- At commit 6, if those clauses retire with the pick, the record moves. That would be a `facts`-stream
  mover with its own manifest, never a silent one.

**W4-3, the lever check is over the sweep cap (a process deviation, corrected).** The default mode of
`run_wreply.sh` makes about 160 compiles plus a tree build. I ran it three times by hand (clean,
`--plants`, the light run) outside the box lock, while the queue's correctness job 578 held the box.
No timing window was in force. The script now takes the box lock itself (`scripts/boxlock run`
unless its caller holds it), and the heavy job runs it under the queue's lock.

**W4-4, the arena under the lever.** Each `unanch_start` call under the lever states a fresh
statement in the compile's arena: a handful of calls per compile, a few hundred bytes each. If
commit 5 needs it, the Job could keep one reply per machine. Not measured; no default-path cost.

**For commit 5 (the flip):**
- The mech rows that plant the planner's NEXT pick stop deciding once the reply is the default:
  S281 and S289 (their anchors sit in `nk_pick_run_pinned`, unchanged text and columns). The same
  holds for any row planting prefix_k's selection where its detector reads the NEXT row. Their
  successors are reply rows (S1412-S1414's shape), or they retire with the pick at commit 6. Each
  goes through a `REACH_ONLY=1` reading first.
- After the flip, `run_wreply.sh`'s identity half compares the lever against a binary that already
  reads the reply. Commit 5 either inverts the lever (a harness option restoring the pick) or keeps
  only the reach half and the `--sweep` against pre-S2 main.

**For commit 6 (recorded, not done):**
- `<PREFIX>_REQ_RUN`'s `@idx` reads the pre-check PART's reply, whose member equals `ReqRun.idx`
  (wsc3 W3-3).
- Main's ruling: ONE pcrec resolver function (the reply's member where a site states R, else pcrec's
  index), and every reader calls it, with no per-reader branch.
- The readers: `@idx`, `REQ_BYTE` via `pcrec_req_pick`, the `[OPT-REQPOS]` comment,
  `req_set_leads_own`, the pick shadow.
- The tables (`pf_tables_ofs`), the block's `OfsTest` (`ofs_test_of`) and the OFFSETS stamp read
  the planner's selection today. They move to the reply's plan at commit 6, and the offset-set guard
  (§3) retires with them.

**Derived sabotage list (§5.4) for (a).**
- 90 rows name a file (a) touches: emit_dfa.c 79, memfn_sites.c 7, internal.h 2, cli/main.c 2.
- `scripts/m6read_check_sab_anchors.py`: all 901 rows / 932 anchor sites resolve.
- No anchor lies inside a changed hunk.
- Two rows name a §4 identifier inside a function (a) split: S281 (clause 4) and S289 (clause 3).
  Both are anchored in `pf_run_applies_common`'s old body, now `nk_pick_run_pinned`, with the same
  text and columns.
  - Intent re-verified: both plant the lever-off pick, which still decides the default path.
  - Their SAB_DESC still names `pf_run_applies_common`, the caller.
  - `REACH_ONLY=1` over both is in the heavy job.
- No other row's reach can move: the default path is unchanged.

**Deviations from the brief:** none in the code's scope.
- The lever-ON vs lever-OFF corpus witness is the lever sweep against 3cd809da1, beside the plain
  sweep against the same ref (transitive identity), rather than a sixth sweep against `--ref-bin
  build/pcrec`. Both compare the same streams against the same ref binary.
- The lever is not a `--extra` arm: the ref build has no such option, so `--extra` would reach and
  break the ref side. The working side is a wrapper (§4.1).

## 7. The heavy job (OWED)

`579-kit-wsc4-heavy` is QUEUED at the lane tip (kit band, `idle-ok`, cap 14400 s). Its `--ready`
holds first while main's `i2build-parity` is pending or running. Job file:
`worktrees/wsc4/build/wsc4/579-kit-wsc4-heavy`.

Steps, in order:
1. `make -j16`;
2. emit_sweep `--ref 3cd809da1`: plain (streams c-default,c-vm,emit-ir,composition,facts,
   emit-ir-auto,stderr), `--arms start`, `--extra=-fno-run-prefilter`, `--extra=-fmemfn-simd`;
3. `run_wreply.sh` (default) and `run_wreply.sh --plants`;
4. the LEVER-ON sweep: `run_wreply.sh --sweep --ref 3cd809da1` (the plain streams);
5. the full shadow `wshadow.py --g2`: the job counts 7 columns at 0 and G2 clean;
6. `REACH_ONLY=1` mech S281 S289;
7. `scripts/perfrun --label wsc4` (make test).

**Completion lines:**
- five `emit_sweep: DONE rc=0` (`expect sweeps=5`), each stream `movers=0`;
- `== wsc4 wshadow: 7 of 7 columns at 0, G2 clean 1`;
- `plants: 3 of 3 red`; `checks failed: 0`;
- `== wsc4 heavy: 0 step(s) failed`;
- the make verdict: `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/wsc4/heavy/maketest.make.log`, empty
  = green (`scripts/verdict`).

**Logs:** `worktrees/wsc4/build/wsc4/heavy/*.log`, and the queue's job.log under
`worktrees/.boxqueue/done/<ts>-579-kit-wsc4-heavy/`. Keep the tree clean until the job has started.
OWED: every verdict above; a fresh agent reads them.

## 8. Checklist

| item | state |
|---|---|
| NEXT predicates read the phase-1 reply under a lever: offset-set, run-pinned, rows 5-13 by order | done (`next_keys[]`; rows 5-13 unchanged) |
| reply fields read: alternative (ENTRY), RE-SEED, C-pin; stop/plan/member for the stamps at commit 6 | read: ENTRY, RE-SEED, C-pin (+ path in the refusal text); the rest is commit 6's |
| phase 2: pcrec states the frame, the kit writes the text | done: the art previews the family; frames unchanged |
| lever named, default unchanged, flips at commit 5 | `--harness=window-reply`; default byte-identical (§5, §7) |
| no R under the two denies, so no C-pin | holds (statement unchanged since wsc3; witnessed by P-b's control) |
| declared mapping table, not an if-web | `next_keys[]` (§3) |
| kit-path commit first if a reply field was missing | not needed: no field missing |
| pcrec-path commit touches only pcrec paths | (a): src/ and cli/ only |
| exactly R-29's facts, nothing computed for a kit method (D157) | yes: the statement is wsc3's; the reply is only read |
| witness: lever ON = OFF, byte-identical, reusable for commit 5 | `run_wreply.sh` (65 cases + reach) green; `--sweep` in the heavy job |
| the shadow stays at zero | sampled 0 on every column; the full run is in the heavy job |
| plants from S1412: NEXT reading the old pick; the RE-SEED bit ignored | S1412, S1413 RED; also S1414 (C-pin not read) RED |
| light checks after each commit | green (§5) |
| heavy job `579-kit-wsc4-heavy` queued, idle-ok, main's hold line, tree clean | queued; OWED |
| commit-6 note (`@idx`, one resolver) recorded, not done | §6 |
| report, lane index entry, kit journal | this commit |
