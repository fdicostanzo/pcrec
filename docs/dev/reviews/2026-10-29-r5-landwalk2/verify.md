# VERIFY (opus) — critic round landwalk2

Verifier: independent re-check of the CONFIRMED findings in sound.md and slots.md.
Subject: `git show 99447aa2a:docs/dev/lanes/p1dsg2_report.md` (copy: verify/subject.md; line
numbers below are that copy's). Code: worktrees/crit-landwalk2 (main 02a054851). My probe dir:
verify/. My own twin `verify/ph.py` shares no code with pcrec or with the critics' drivers: truth
= libpcre2 10.46 find-all via ctypes; per-hit = hits of L ascending from search_from, s*(j) = the
smallest s in [sf, j] where `(?:P)L` matches exactly subject[s:j+|L|] (pcre2 ANCHORED|ENDANCHORED
with the length cut at j+|L|), then ONE anchored pcre2 attempt of R at s*.

## SOUND-1

**HOLDS.**
- Answer (my twin, `python3 -I verify/ph.py '((?:xy)?ab)=\1' '((?:xy)?ab)' '=' 'xyab=aba'`):
  `pcre2 [(2, 7)] perhit []`. With starts(4) = {0, 2}, s* = 0 and the one attempt at 0 fails
  (`\1` = "xyab" vs "aba"); there is no later `=`. Control "ab=ab": both (0,5).
- The table: I read pcrec's emitted reverse table myself (`sound/w/u-xyab/m.c:79-104`). Classes:
  1 `=`, 2 `a`, 3 `b`, 4 `x`, 5 `y`. Row 0 -`=`-> row 2 -`b`-> row 3 -`a`-> row 4 (accepting on
  every class, `is_accepting[24..29]=1`) -`y`(idx 29)-> row 5 (`is_accepting[30..35]=0`)
  -`x`(idx 34)-> row 6 (accepting). So accept → NON-accept → accept. Under the one-step reading
  step(row4, y) = row5 has no accepting pair, so the rule says UNIQUE; the brute count is 2. Their
  script agrees (`unique_tables.py`: "DIRECT UNIQUE TRANSITIVE NOT brute max|starts| 2 DIRECT WRONG").
- Does §A1 admit the DIRECT reading? Yes. subject.md:146-147: "for no reachable state `s` and byte
  class `c` with `accepts(s, c)` does `step(s, c)` reach a state `s'` that has ANY accepting pair".
  "reachable" is used for `s` but `step(s, c)` "reach[es]" `s'` is unqualified; the next sentence
  (:150-152) argues only about the single step reading the same byte, and the line "Rev 0's
  state-level wording ('no accepting state reachable from another') could not see that" reads as
  if the rewrite replaced the reachability wording. A builder can read it as one step.
- Scope as the critic says: R has `\1` so it is VM-routed; stage 1 reads no UNIQUE (:141-143).
  Severity doc now / answer at stage 2.

## SOUND-2

**HOLDS** on the answer and on L1/L6/L7; L8 (rarity) and the choice rule's pick of the run
`aa` over the single byte `a` are NOT verified (no build to evaluate them).
- Answer (my twin, `python3 -I verify/ph.py '[0-9]*aa[bc]' '[0-9]*' 'aa' '00000aaabb'`):
  `pcre2 [(6, 9)] perhit [(6, 9)] perhit-nonoverlap []`. The non-overlapping stream sees `aa`
  at 5, s* = 5 (`[0-9]*` empty), the attempt at 5 fails (`aaa`), and resumes at 7, skipping the
  overlapping hit at 6 that owns the match.
- Admission, my own compile (`pcrec -p rx --emit-main -o verify/s2.c --pattern '[0-9]*aa[bc]'`):
  `RX_ENGINE "dfa"` (L1 passes: CR_DFA), `RX_DFA_PREFILTER "memchr"` (not in L6's list,
  subject.md:359), `RX_DFA_MATCH "unwrapped"` (A built, L10 passes), `RX_REQ_RUN
  "616162@2/fffffe"`. L7: bytes(`aa`) = {a} ⊄ digits. L2: `aa` is an inner run at a top-level
  concat position with non-empty P (subject.md:241-242 allows "one byte, or a run").
- Caveat for the ruling: the choice rule could also offer the single byte `a` at position 1
  (same P); there overlapping and non-overlapping streams coincide. The rule ranks by rarity
  margin (subject.md:248), which should favour the run, but that is unbuilt. The mechanism
  (a periodic L, P not covering L) is general, so the fact wording fix stands regardless.
- The subject's wording (subject.md:495-496) "the positions of L from `search_from`,
  ascending" does not say "overlapping"; the D157 fact is the only carrier, as the critic says.

## SOUND-3

**HOLDS.**
- `sound/w/csv5b/m.c` (pcrec's own rev-end of `[^,\n]{0,2},`): `m_reverse_is_stop(s)` is
  `s >= 9u` (:62); `m_reverse_next_state[12]` (:98-99) has ONE live cell, row 0 on `,` → 9; rows 2
  and 3 (states 6, 9) are accepting (:101-102) with every transition dead. The `[^,\n]` run is
  only in `m_reverse_scan3` and the bounded loop at :143-157 (`scan_run_length < 2ULL`, then
  `reverse_state = 6`). Applied to `next_state[]`/`is_accepting[]` alone, the rule sees one
  accept with no live successor: UNIQUE, one start; the true starts(j) has up to 3 members.
- Why: `pcrec_scanedge_dfa` mutates the Dfa in place: "Finds every maximal SCAN CHAIN in `d`
  ... and DELETES the chain, leaving one edge the emitter turns into a bounded loop"
  (src/opt/scanedge.c:555-559; emit_dfa.c:9106-9109 "rewrites exactly one transition cell
  (`tr[head][C] = -1`) ... drops only states ..."). So a rule read off ML after the pass reads
  the edited machine.
- The subject builds ML with "then `pcrec_scanedge_dfa` over it" (subject.md:430-431, :634) and §A1
  never says the rule reads the pre-edge form. Severity doc (stage 1 reads no UNIQUE).

## SLOT-1

**HOLDS** (both halves), with one correction to which trace check fires first.
Each hop, quoted from the review tree's src/gen/emit_dfa.c:
- LOCATE → NEXT: the design's L6, `CAND_READ(LOCATE, NEXT)` (subject.md:359).
- NEXT → FIRST: `pf_handoff_applies` (:9040) "`u = req_use_read(cx, CAND_SLOT_NEXT);`" (:9045),
  and `req_use_read` (:8944-8951) selects FIRST via `CAND_READ(reader, CAND_SLOT_FIRST, ...)`.
- FIRST → PRESENCE (and → path): `req_handoff_applies` (:8790) "`if
  (!req_admit_emits(req_admit_read(cx, CAND_SLOT_FIRST)))`" (:8794) then "`if
  (!(cand_path_members(cx) & (CAND_MF | CAND_MATT)))`" (:8796); `req_admit_read` (:8665-8672)
  selects PRESENCE.
- PRESENCE → LOCATE: `req_dominated_applies` "`if (CAND_READ(CAND_SLOT_PRESENCE,
  CAND_SLOT_LOCATE, &ls, "req-whole")->u.locate.whole) return true;`" (:8589-8590).
  `cand_path_members` → `cand_path_of` also selects LOCATE (:11957-11960).
Guards that could break it: none at run time in a release build.
- `cand_read` (:11638-11643): "`cand_select(slot, s, s->cx->opt->flags |
  cand_nodes[reader].under[slot])`": `under` is the direct reader's only. `req_use_read` /
  `req_admit_read` build a fresh `CandSel` and select with the compile's flags, so a deny never
  rides down the chain. `cand_select` (:10712-10724) has no memo and no visited set.
- Trace build only: `cand_applies` traps depth ≥ `CAND_EVAL_MAX` 64 as `table-read-recursion`
  (:10705-10709). But `cand_nested_read` (:10690-10697) traps an UNDECLARED read first:
  `cand_nodes[CAND_SLOT_LOCATE]` (:9936-9938) has only name/accepts/asks/succ, so `reads` is
  zero and L6's read fails `undeclared-read` on its first evaluation. If the build declares it,
  the static `table-read-cycle` walk (:11287) sees LOCATE→NEXT→FIRST→PRESENCE→LOCATE unless an
  `under` breaks it. So the trace build would catch it; the critic's "trips
  `table-read-recursion`" names the wrong (later) check. The release-build recursion claim holds.
- Could the existing `under` be reused? Only in a form that defeats L6: `under[NEXT] =
  PCREC_NO_REQ_HANDOFF` on LOCATE's read would skip `handoff-reentry` (the row whose predicate
  reads FIRST) and end the recursion at one level, but then L6 can never see `handoff`, which is
  the value it exists to decline on. Making the WALK transparent needs `PCREC_NO_LANDMARK_WALK`
  to reach the LOCATE selection three reads down, which `cand_read` cannot carry.
Two fixed points: confirmed.
- `dominated` sets verdict `REQ_ADMIT_DOMINATED` (:8744), and `req_admit_emits` (:295-298) is true
  only for EMITTED / SET_LEADS, so FIRST's `handoff` fails its first conjunct (:8794), so
  `u->use != REQ_USE_HANDOFF` and NEXT's `handoff-reentry` declines (:9047).
- My compiles of kv-quoted (`--features all`): default `RX_DFA_PREFILTER "handoff"`,
  `RX_REQ_HANDOFF "32"`; with `-fno-req-handoff` `RX_DFA_PREFILTER "first-class-bounded"`, which is
  not in L6's list. (`-fno-req-handoff` keeps `RX_REQ_WHY "emitted"`, so it is a proxy for the
  dominated state, not the same state; NEXT's remaining rows read no PRESENCE verdict that I
  found, so the proxy is fair.) Walk off → NEXT handoff → L6 declines; walk on → NEXT
  first-class-bounded → L6 passes. Both self-consistent; subject.md:266-267 asserts the first.

## SLOT-2

**HOLDS.**
- The check (emit_dfa.c:11376-11392): for each FIN_SEARCH row's take hand on a non-VM route,
  "`if (r->take[rt][k] != CAND_HAND_AT && !(r->take[rt][k] & ~fb->hands))
  cand_oracle_fail("table-progress-rank", ...)`", with `fb = cand_fallback(LOCATE, rt)` and
  "`if (!fb || rt == CAND_ROUTE_VM) continue;`". The comment (:11372-11375) states the meaning:
  a relocating row "must take no hand its relocation target ... hands it back".
- `fb` on DFA is the last LOCATE row routed there, `composite` (`.routes = CAND_ALL_ROUTES`,
  `.hands = CT_LOWER`, :10217-10218); `CAND_HAND_LOWER` is `CT_LOWER` (:9812). For a LOWER take
  cell on `search-from` (FIN_SEARCH, :10608) on DFA: `CT_LOWER & ~CT_LOWER == 0`, so the check
  FAILS. Today's DFA cells AT (exempt) and ENDSET (`CT_START|CT_ENDSET`, :9811, not ⊆ CT_LOWER)
  pass; the VM LOWER cell passes only by the `rt == CAND_ROUTE_VM` skip.
- The subject (subject.md:216-218) gives "`table-progress-rank`: LOWER ⊆ `composite.hands`
  (`CT_LOWER`)" as a reason it PASSES "unchanged in kind"; that inclusion is the failure
  condition.

## SLOT-3

**HOLDS.**
- AT's single producer today: docs/design/locate_finish.md:254 (table row `AT` ... "the `caller`
  locator of the match-here entry") and :258 ("`caller` always asks a point").
- The four places, quoted from emit_dfa.c:
  1. `cand_takes` (:10647-10652): "`(r->slot != CAND_SLOT_FINISH || s->hand != CAND_HAND_AT ||
     s->point)`".
  2. The rank inequality comment (:11373-11375): "`AT` is the match-here entry's E-FC (`entry`,
     once per call), not a relocate", and the code exempts `CAND_HAND_AT` (:11388).
  3. `cand_nodes[FINISH]` (:10036-10040): "`.rank = CN(CAND_SLOT_LOCATE), .entry =
     CN(CAND_SLOT_LOCATE)`"; the acyclicity walk drops `entry` edges (:11359-11362 "an `entry`
     edge runs once per call, so neither can spin").
  4. `point = false` asks: `cand_finish_ask` (:10779-10780), `cand_path_of`'s LOCATE-hands loop
     (:11943, the 5th argument of `cand_path_finish(..., h[k], false, ...)`, signature :11894),
     and `dfa_search_calls_match` (:13600-13601).
- `cand_path_finish` (:11894-11907) relocates only `hand != CAND_HAND_AT`; an AT follows its row
  even when that row is FIN_SEARCH, which is the run-time self-loop the subject itself names
  (subject.md:207, the AT row's last cell).
- Placement: the subject puts `locate-at-recursion` "trace build, beside
  `table-finish-not-total`" (subject.md:226-228). `table-finish-not-total` is raised at :11428
  inside `static void cand_path_selfcheck(void)` (:11349), which has no Ctx, so it cannot read
  `anchored_ok`/`finish_available`. Yet the subject requires it to "fire on a pattern with
  `-fno-anchored-dfa`" (:228, :665): a per-compile property. Statically the check either
  assumes `verify-at` declines (search-from is then the AT taker: always fires) or assumes it
  applies (never fires). The per-compile home would be `cand_path_of`, beside
  `path-needs-unbuilt` (:11950). Holds as stated.

## SLOT-4

**HOLDS** (latent on stage 1, as the critic grades it).
- Route: `cand_route_of` (emit_dfa.c:3835-3838) is "`cx->job->engine == PCREC_ENG_ATTEMPT ?
  CAND_ROUTE_ATTEMPT : CAND_ROUTE_DFA`"; its comment (:3830-3831) names "the VM hybrid's inlined
  prefilter" as a DFA-shaped body. `cover` has its own C1 for this: `cc_finisher` returns
  `pcrec_cand_finisher_dfa` (src/gen/known.c:181-184).
- My compiles (`--features all`; without it both refuse "requires module 'lookaround'"):
  - `(?![a-z]*b)[a-z]+@x`: `RX_ENGINE "vm"`, `RX_VM_PREFILTER "hybrid"`, `RX_DFA_SCAN
    "unanchored"`, `RX_DFA_PREFILTER "byte-class"` (not in L6's list), no `RX_DFA_MATCH` line.
  - `(?=[a-z]*b)[a-z]+@x$`: `RX_ENGINE "vm"`, `RX_VM_PREFILTER "hybrid"`, `RX_DFA_SCAN
    "rev-end"`: a LOCATE row other than `composite` IS selected on a hybrid's CR_DFA body today.
  So L1 as worded (subject.md:355, "the body is CR_DFA, i.e. ENG_UNANCH") passes hybrids; L3
  (:356) leans on "VM-routed, so L1 catches them first", so it does not decline the erased
  lookaround either; L7 passes (`@` ∉ [a-z]).
- Answer (my twin, P as the prefilter body sees it, lookahead erased: `python3 -I verify/ph.py
  '(?![a-z]*b)[a-z]+@x' '[a-z]+' '@' 'ba@x'`): `pcre2 [(1, 4)] perhit []`. With the real P (the
  lookahead kept) the twin gives (1,4), so the wrong answer comes exactly from walking the
  erased body.
- L10: `build_anchored_dfa` (src/core/compile.c:378-386) returns at "`if
  (!pcrec_cand_finish_needs(cx, CAND_MA)) return;`" — the VM finisher's route declares no
  `CAND_MA` — so `anchored_ok` stays false (consistent with no `RX_DFA_MATCH` stamp), and the
  POST row L10 declines after the PRE rows pass and ML is built (subject.md:342-346: "ML is
  BUILT only where every PRE row passes, and the POST rows read the built machines"). On stage
  1 the cost is a wasted ML build and a listing that names `anchored-A`, not `route`.

## SLOT-5

**HOLDS**, with one refinement on the "falls under SLOT-1" sub-claim.
- `req_landmark_admits(const CandSel *s, long long k)` (emit_dfa.c:9016-9027) takes no landmark:
  "`landmark_ppm = req_landmark_hit_ppm(cx, rate)`", and `req_landmark_hit_ppm` (:8956-8971)
  reads "`pcrec_fact_req_run(cx)`" and "`set[pcrec_fact_req_byte(cx)] = 1`": the FACTS'
  landmark. The subject's L8 is "`req_landmark_admits(s, ŵ + k_hit)`" (subject.md:361) and
  calls the rarity row "the handoff's own admission ... with another K" (:40-41, :83, :118); the
  choice rule ranks candidates by its margin (:248). With no landmark parameter, every candidate
  gets the same `h`, so the per-candidate margin cannot be computed; where the chosen L is not
  the fact's landmark (subject.md's own dup-param, `RX_REQ_BYTE "38"` = `&` vs the pick `=`,
  :256-260) it prices the wrong byte.
- `m`: `req_start_set` (:8979-9000) does "`cand_select(CAND_SLOT_NEXT, s, cx->opt->flags |
  PCREC_NO_REQ_HANDOFF)`" then "`cand_row_scan(cx, CAND_SLOT_NEXT, s->us, start_row, &cs)`".
  `cand_locate_sel` (:11696-11700) builds `.us = NULL`, and `ofs_test_of` (reached from
  `cand_row_scan`) dereferences it unconditionally ("`const mf_wreply *w = &us->wr;`"). So the
  LOCATE predicate must supply NEXT's `UnanchStart`: confirmed.
- Refinement: this NEXT selection is made under `PCREC_NO_REQ_HANDOFF`, so it skips
  `handoff-reentry` and does NOT itself close SLOT-1's recursion; it is an undeclared
  LOCATE→NEXT read edge (a trace-build `undeclared-read`), not a second cycle.

## SLOT-6

**HOLDS.**
- `CoverConj` (src/gen/known.c:367-372): "`const char *cid; const char *id; const char *kind;
  bool (*holds)(CoverSt *st);`" — no phase, no desc.
- `CompConj` (src/core/internal.h:8730-8737): "`id; name; CompPhase phase; holds; const CompRead
  *reads; int nreads;`" — phase and a declared `reads` column; `split_conj[]` uses it
  (src/core/compound.c:248-258).
- The subject's shape (subject.md:342-343) "`cover_conj[]`'s shape (`{ cid, id, phase, kind,
  holds, desc }`)" matches neither: it is cover's plus phase and desc.
- `.c.deny` exists and is read: `cand_select` "`if (pcrec_flags_has(flags, r->c.deny))
  continue;`" (emit_dfa.c:10727); `rev-end` declares it twice, ".c = { "rev-end",
  PCREC_NO_REV_END, ... }" (:10186) and the listing's 4th field "`{ "locate", 1, "rev-end",
  PCREC_NO_REV_END }`" (:10189).
- The cited F0 precedent (subject.md:353) is `revend_forms[]`'s "denied" FORM row, whose
  predicate is `rf_denied` on `PCREC_NO_REV_END_ONEWALK` (emit_dfa.c:13491-13493, :13510): a
  form-choice deny inside a row that is already selected, not a row deny. The row deny
  precedent in the same family is `.c.deny`.

## SLOT-7

**HOLDS** (the code claims; the "nothing moves" survey over MR/A/Q/4c/rev-end-relaxed I did not
re-run).
- `compound_place[]` is a table over `const CompPart *` (src/core/compound.c:279-301:
  `bool (*holds)(const CompPart *p)`; rows `different-tree`, `different-options`,
  `erasure-only`), and its one code caller is `pcrec_compound_rows_check` over each
  `row->parts[i]` of `compound_rows[]` (:348-349). "Review asks it of every in-Job candidate"
  (:277) is comment text, not code.
- The predicates read only `p->derive`, `p->flags_set/clear`, `p->engine`, `p->bound`
  (:283-291). Every part HAS an entry, typed by `bound` (`part_type`, :313-316). The subject's
  row 0 (subject.md:456) conditions (b) "no entry and no FINISH of its own" and (c) "hands a
  POSITION ... never a span" are not functions of these fields, and ML is not a `CompPart`, so
  no `CompPart` can reach row 0 and compound.md's "a reach witness per row" (compound.md:321-322)
  cannot be supplied for it.

## SLOT-8

**PARTLY.** The collision is real only for a rung that takes an SDR ordinal, the subject does
not say which shape it means, and the critic's named "working shape" is misattributed.
- Holds: the ordinal's meaning, "A RUNG MEANS "EVERY CONTRIBUTOR UP TO AND INCLUDING THIS ONE IS
  DROPPED"" (src/core/internal.h:3109-3110), and the ruled order, "APPEND. `SDR_NO_ANCHORED`
  stays rung 1" (:3119-3121; `SDR_NONE = 0`, `SDR_NO_ANCHORED = 1`, `SDR_MAX = 3`,
  :3145-3179). `fit_anchored_applies` (src/core/compile.c:1091-1098) requires "`s->size_drop_rung
  == SDR_NONE`". So a `drop-landmark-walk` rung placed before `drop-anchored` (subject.md:612-613)
  that set any SDR value would stop `drop-anchored` from firing, or force a renumbering
  against the ruling.
- Not quite: "The working shape is drop-premul's: `FIT_SDR_KEEP` plus the row's deny bit". In
  the code `drop-premul` sets `FIT_SDR_TO_PREMUL` (compile.c:1371, an SDR rung after anchored;
  `fit_premul_applies` reads `size_drop_rung < SDR_NO_PREMUL`, :1151). The shape that leaves
  `drop-anchored` live is `FIT_SDR_KEEP` (as `drop-handoff`, :1381, or `drop-compound`, :1311)
  WITH the row's deny in the `sets` flags field (as `drop-premul` OR's `PCREC_NO_PREMUL_TABLE`,
  :1371): a combination of two rows, not drop-premul's.
- Holds: `COMPILE_MAX_ATTEMPTS`' hand formula (compile.c:672-673) is held to the table by
  `fit_check(cx, fit_attempt_bound() == COMPILE_MAX_ATTEMPTS, ...)` (:1769-1770), so a new
  retrying row moves it. The subject's ladder reader list (subject.md:655-656) names
  `fit_rungs[]`, `axes_dump.c`, `run_fallback_table.sh`, `limits_check.sh` and not this formula.

## SLOT-9

**HOLDS.**
- docs/spec/tuning.md:125, the §2.15 table row: "`-fno-anchored-dfa` | 17 | on | answer-identical
  | masked | `<PREFIX>_DFA_MATCH`" — one stamp. §2.15¶1 (:337): "**Denies** the ANCHORED MACHINE
  behind `<prefix>_match` and `<prefix>_match_caps`". §2.15¶3 names only `<PREFIX>_DFA_MATCH`.
  The §5.4 dial row (:1316) excludes the flag on "its worst measured population".
- Under L10 (subject.md:363, POST: A built) the same flag also declines `landmark-walk`, so on 5b
  it moves `RX_DFA_SCAN` back to `unanchored` and gives up the walk's measured x44 cycles
  (subject.md:38, :307). The `drop-anchored` note (src/core/compile.c:1364-1368: "loses the
  [OPT-2] fast path -- <prefix>_match falls back to search-and-filter") would understate it.
- Build plan step 7's tuning entry (subject.md:650) is "tuning.md (a new section, and the
  `<PREFIX>_DFA_SCAN` table)"; §2.15 ¶1/¶3/¶4, its line-125 row, the §5.4 exclusion and the
  note text are not named.

VERIFY COMPLETE
