# covcap4 report — [COVER-CAP] design rev 3 (round covcap-r2 applied; the walk choice)

Lane covcap4 (opus), 2026-11-15. Branch `lane/covcap4`, from main `4ccd97ca7`. Design only:
no edits under `src/`, `cli/`, `lib/`, `tests/` or `memfn/`.

## STATE AT HANDOFF

- DONE, committed on `lane/covcap4`:
  - `docs/design/cover_cap.md` revision 3 (PROPOSED; REVISION 3 block first; rev 2 text
    superseded in place; 37.2 KB against rev 2's 37.3 KB).
  - The review `docs/dev/reviews/2026-11-15-r5-covcap-r2.md` with a "DISPOSITIONS
    (manager, 2026-11-15)" block copied from R1, and its directory
    `docs/dev/reviews/2026-11-15-r5-covcap-r2/` (COMMON, fixind, owner, premise, ready,
    sound, verify). Indexed in `docs/dev/reviews/CLAUDE.md`. Three spec LINE cites in the
    critic texts (`facts_listing.md` one, `cli.md` one, in premise.md and verify.md) were
    rewritten as section cites so `test-spec-history` stays green; nothing else changed.
  - D198 in `docs/dev/decisions.md`: the owner's criteria, verbatim (R2, R3, the 10:45 and
    11:40 journal entries; the 02:58 points marked as the manager's record, not a quote).
  - Process edits (R1): `.claude/skills/pcrec-critic/SKILL.md` (per-lens scratch subdirs;
    the premise lens's row gains "today numbers re-run from their command" and "kept
    functions: required property"), `docs/dev/guide/critics.md` (a dated lessons entry with
    all three), `docs/dev/lanes/BRIEF_TEMPLATE.md` (a TODAY NUMBERS field).
- Rulings file: R1-R5 read at every checkpoint; last entry applied: **R5** (the owner's
  safety limit, arrived after rev 3's first commit and applied in `6630261a7`: one
  `PCREC_MAX_EXACT_SPAN`, 4096 proposed with its derivation, no cliff; D198 (g)).
- PREMISE TEST: holds. `build/pcrec -p rx --features all --emit-facts --pattern 'a{48}' |
  awk -F'\t' '$1=="byte"&&$2=="span_facts"{print $7}'` prints `24:97,...`; the same for
  `a{49}` prints `0` (C-9 reproduced). `[ab]{1000}` and `a{500}` print `0`.
- STOP RULE: did not fire. Both walks can state the stretch soundly without a budget, and
  the anchored-machine reading loses 0 of today's 1,852 covers (§WALK CHOICE).
- Probes (scratch, not committed, never the worktree): `/var/tmp/pcrec-pcrec/scratch/covcap4/`
  - `probe/` a `git archive` copy with `probe.diff` over `src/gen/known.c`: a `DFALINE`
    record (`COVCAP_PROBE=1`: the machine walk unbounded, its `L`, end kind, rows) and a
    prototype of rev 3's C8 (`COVCAP_DFA=1`: the slice's half skipped, no `KN_CAP` effect
    below 32);
  - `ps.jsonl` (the 23 baseline `exact/producer-short` compiles), `diff10.py` (the
    python-`re` differential).
  - No sweep was run: the box was held by kit queue jobs, so the census numbers are
    covcap3's (scratch `covcap3/census*.jsonl`) and my own runs were single compiles
    (about 60) plus the 20-compile differential.
- `make test-plan-lint`: green (run before lanecheck). No runs owed.
- No ids taken besides D198. No abi number named.

## FINDINGS APPLIED BY ID

All per R1. "§" is rev 3's section.

| id | applied as |
|---|---|
| C-1 dead-line termination | discharged by deletion: the machine walk terminates by depth V (every row live, an accept within V-1 bytes; §3.1 TERMINATION). The 2310-period witness has no analogue: no NFA subsets are walked |
| C-2 `sw_take` cycle rule | discharged by deletion (no cycle rule; `sw_take` deleted with the slice) |
| C-3 root liveness | discharged: a context-dependent start is C6's `entry-const/seeds` (exact machine liveness); `(?:\bab|\Bac\z)` states 0 (witness row, §5.3) |
| C-4 NFA-shape dependence | discharged: rows are compared by byte SET, never identity, so deny arms cannot move `L`/`k` (§3.1); plant (b) guards it |
| C-5 (i) opaque ends; (ii) no machine control past k | (i) `\G` is C3's decline, no opaque end exists on the machine; (ii) moot: one producer, its control is X0 at every position (§3.6 Q2) |
| C-6 outcome 3 / `past` | §3.1's outcomes: the "loop ends at H" outcome no longer exists; C7 and C8 conditions stated in §3.3 |
| C-7 eager rows, memory | §3.1 MEMORY: two grown row arrays + 32 bytes per depth; §5.1 compile-cost row reads max RSS |
| C-8 POSSIBLY-LIVE pass | deleted (no liveness passes at all); presented as simplification (§3.1 WHAT IT DELETES) |
| C-9 wrong cliff | §2 PREMISE with the commands; §9 correction 1 |
| C-10 Z2 ruling 1 | §9 correction 2 (who, when, why, the 66,243,390-cell check); under rev 3 the ruling stands, no row turns red (§5.3 floors) |
| C-11 4 compiles = 3 patterns; `(?:a{1000}){1000}`; D163 cite | §2 table says "4 compiles, 3 patterns"; the non-compiling example and the D163 cite are gone with rev 2 §3.1/§3.2 |
| C-12 `PCREC_PREFIX_K_MAX` label | §3.4: the rationale lives only in `offset_k_skip.md` §3.3; labelling is PLAN (main) |
| C-13 spec targets, regeneration list | §4.5 (cli.md and match_api.md: no hunk, said so; facts_listing.md: a retired stub + a new section); §3.6 Q3 names `limits_check.sh`'s 82→81, `limits.def`'s home count, `src/facts/CLAUDE.md`, the `limits.h` X-macro |
| C-14 stale comments | §5.5's list, with the grep that must reach 0 |
| C-15 prediction instruments | §5.2: `KITPROOF` record under `PCREC_KIT_PROOF_TRACE` on the trace build, `k` from the `width` fact, an upper bound with listed exceptions, no `k >= 25` floor; the listing half downgraded to "checked against libpcre2" (X0) |
| C-16 prefix values | §5.3: every `facts` value written whole; answer rows at n >= 33 at stage 2 |
| C-17 plants | §5.4 rebuilt: (a)'s witness is a non-cover (`a{40}(?:b|cc)`), so (d) (C15 removed) cannot reach it; values computed on the prototype; the ASan claim dropped from the plant |
| C-18 outside witnesses | §5.5: `run_offset_skip.sh`'s and `run_entry_shape_identity.sh`'s 32-hex witnesses re-pointed by the build; non-`.rxt` grep at each stage |
| C-19 hollow asan row | §5.1: a named one-off with `PCREC`/`PCREC_HARNESS` set |
| C-20 `pcrec_known_derive` | deleted at stage 1 (it reads the deleted `MkLang`; no caller) |
| C-21 goal ranking | §0: G4 is a constraint above the ranking, with the loss order |
| C-22 "branch" | §3.2: a language-level paragraph, both examples, and §2's table of what each reading loses (thread 29 / subset 4 / machine 0); no owner question (R1) |
| C-23 goals per stage | §0: G1-G6 state their stage |
| C-24 kit internals | §4.3: struck, with R3's two strikes |
| C-25 general form | §1.1 END STATE: one walk, exact up to `L`, whole = cover, fraction = rows at `L`, hull = the same walk merged; unlocks (i)-(iii) with triggers as PLAN |
| R2 | §1.1 (end state, cover first case, nothing redone for the fraction); two stages kept |
| R3 | §4.3 (capability ask + population fact only); §7 (hit-dense, near-miss, cold artifact; size beside each timing) |
| R5 | §0 G4, §3.1 outcome 4 (no cliff: `exact_len = min(L, k, MAX)`, C7 `over-max`), §3.1 derivation (binding cost = emitted matcher size; 128 B/position pcrec side; population max stretch 1000, 0 compiles reach 4096), §3.5 stage 2 seam up to MAX, §4.3 asks "up to 4096", §5.3 `a{4097}` witness, §5.4 plant (e) the cliff, §8 the added row, §9 Q2; D198 (g) |

## WALK CHOICE

**Chosen: read the exact stretch from the ANCHORED MACHINE** with `kn_walk`'s existing
multi-row product rule, unbounded; delete the NFA span slice. Not the single-row form R4
sketched ("one next state continues; a revisited state ends the line"): the multi-row rule
already exists, compares byte sets, needs no revisit rule, and keeps stretches like
`a[xy]c|b[xy]d` (2, against 1).

| | NFA-subset straight walk (rev 2, repaired) | anchored-machine walk (rev 3) |
|---|---|---|
| findings removed | none by construction; C-1..C-8 each need a repair (line-wide subset hash, a growable store, a cycle-length statement, the root rule, set comparison at the branch, the past flag, lazy rows) | C-1, C-2, C-3, C-4, C-5, C-8 by deletion; C-6, C-7 by smaller text |
| findings kept | all of C-9..C-24 | the same, adapted (§5) |
| C8's control | two readings, compared on every compile (sharing `Job.nfa`) | one reading. Its controls: libpcre2 (kitproof answers standing; X0 set check one-off over the census, both stages), the `-fno-scan-edge` arm (listing compared row for row), the engine route (`test-axes`), the kit's proof (C14). Lost: the per-compile decline on a disagreement, which has fired 0 times in the trace builds that assert it |
| covers lost (today 1,852) | 4 compiles, 3 patterns, incl. Z2 ruling 1's | **0** |
| covers gained | the long shapes | the long shapes + 18 k = 1 corpus compiles (10 patterns), each 0 differences against python `re` over 1,554 subjects |
| listing values lost | 221 shrinks (census) | 1,519 compiles where no anchored machine finishes the match (no reader today) |
| code | rewrite of `pcrec_span_walk` + 2 passes + hash; `kn_walk` bounded by the slice | delete ~430 lines (`kset.c` slice), `MkLang`, a facts row, a limits row, `KN_CAP`, C8's comparison, `pcrec_known_derive`; add growable rows and a listing section |
| general form fit (R2, C-25) | the line's subset at `L` is an NFA set; the hull is a separate NFA walk (`kset_walk`) | the walk's rows at `L` ARE the engine's resume state; the hull is the same walk merged past `L` |

R5 (4): with the safety limit the walk ends in at most `MAX` steps by construction, so the
termination argument is no longer load-bearing. The same limit would let rev 2's NFA walk
drop its cycle rule (C-1, C-2) but not its root rule, its shape dependence or its
liveness passes (C-3, C-4, C-8), so the choice stands.

Why: it is the only option that removes the round's soundness findings instead of
repairing them, it loses nothing, and it is the walk the cover already trusts (X0 checked
it against libpcre2). The choice changes what the owner was told (no covers lost, a ruling
stands, the slice and its listing go, one reading instead of two): §9 question 1.

Costs I want main to see (none blocks): (1) the fraction case for patterns WITHOUT an
anchored machine of the exact language (VM-finished routes: 1,127 listing compiles today)
has no producer after the slice goes; when [MATCH-KNOWN] un-parks, its first client says
whether its population has an anchored machine (capture-only hybrids may) or needs an NFA
producer (erased/backref routes, where the slice also declines). (2) [DD-11.5]'s part 1
product is the slice; its row needs re-scoping. (3) The listing gains a `cover` section;
it is a debug listing with advisory names, not an [IFACE-PUSH] item, but main may prefer
otherwise.

Verified on the prototype (scratch `probe.diff`, `COVCAP_PROBE=1`, both encodings unless
noted): `a{1000}` and `[ab]{1000}` L 1000; the uuid shape L 36; `a{30}(?:b{30}c|d)` L 31;
`(?:[a-z]{0,3}\z|x)[0-9]{3}` cover k 4; `(?:S(?i:ab)|(?i:sab))` cover (byte; utf8 inexact
as today); `ab|abc|ad` L 2; `a*?a` L 1; `[а-я]{4}` utf8 L 1 (lead-byte split);
`(?:\bab|\Bac\z)` and `[ab]*\z\W` stop at C6 (0); `a{40}(?:b|cc)` L 41; `a[xy]c|b[xy]d` L 2
with two rows from depth 1; `a(?:b|c\z\W)` L 2. With `COVCAP_DFA=1`, 22 of the 23 baseline
`exact/producer-short` compiles read `cover` (the bench's `wild-logparse-quotedstring-noatomic`
utf8 still declines later).

## QUESTIONS

For the owner (plain words; also cover_cap.md §9):
1. The exact stretch would be read from the compiled matching machine, with the walk the
   cover already runs, instead of from the pattern's graph. No current cover is lost (rev
   2 lost four), 18 small test covers are gained, the 2026-10-21 ruling stands, and about
   430 lines of exploring code go. Given up: two readings agreeing on every compile become
   one reading checked against PCRE2 in the tests; and the debug listing stops showing a
   span for patterns the cover cannot use. Leaning: accept.
2. The earlier ruling to cover `(?:[a-z]{0,3}\z|x)[0-9]{3}` (made by the manager on
   2026-10-21 in the Z2 build lane after a check left 175 cells undecided; then 0
   differences against PCRE2 in 66,243,390 cells): rev 2 would have reversed it without
   saying so; rev 3 keeps it. Leaning: keep.
3. The maximum span length you asked for: 4096 positions. The binding cost is the size of
   the generated matcher (the kit's code today is about 8 to 31 assembly lines per position,
   so 33,000 to 127,000 lines at 4096), not pcrec's memory (about 128 bytes per position).
   The longest exact stretch in our test and bench patterns is 1000; none reaches 4096.
   Past the limit nothing collapses: the first 4096 positions stay proven. Leaning: 4096.
4. If a long cover makes the matcher big enough to lose in the cold-cache timing: one
   bounded try, then the kit, then you. Leaning: no action until the timing shows it.
5. Build go for stage 1, after the narrow readiness re-check.

For main: the three costs above; the N row and the `PCREC_PREFIX_K_MAX` label row to file.
