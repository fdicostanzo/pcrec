# D6 panel r1 — [MATCH-SPLIT] 4a pin-only design note (docs/design/match_split_pinonly.md, lane msdesign 48bb533b)

Session 109, 2026-10-12. Three read-only critics, none ran make: **sem** (opus; engine semantics vs libpcre2 10.46), **chk** (sonnet; checks, tests, cost claims), **arch** (sonnet; architecture, interface, unlocks). Raw findings are appended verbatim-condensed below, from the critics' messages. Scratch drivers: worktrees/.mgr/panel-{sem,chk}/ (untracked).

## Verdict
The split ALGORITHM survives: sem simulated it with libpcre2 as the machine over 54.2M cells (492k ties) with 0 diffs, and chk found no soundness counterexample. The NOTE needs a revision before any build. It has two blockers:
1. a **miscompile** in the emitted shape (sem BLOCKER-1: the K73 SEEK overwrites `search_from`, so the tie re-entry runs with `\G` true at the wrong position);
2. a **false cost claim** carrying the admission (chk B1 = arch M1 = sem MF3: two independent reverse walks plus a forward tie; about 2-3x today on trailing whitespace before a final newline).

## Frank's rulings (this session, before/at the panel)
- Q1 (deny bit): **spend bit 55** (`-fno-match-split`). Arch S6 restates the budget: 9 free now, 8 after, against the [IFACE-PUSH] <=4 trigger; queued consumers are rev-inner, rev-end-width, [ADAPTIVE-ARM], maybe 4b.
- Q2 (K106's (?m) trim shapes): **4b.2**, agreed.
- Q3 (short-call fixed term): Frank asked "what's the concern". The manager explained: the dominance claim is false; a long trailing match costs about 2L inherent (reverse locate + forward finish) against today's 1L, and 3L with today's two-pass seeding. Manager's recommendation: single-pass two-seed walk; skip FINISH when the end is unambiguous and no captures are asked; gate against today measured on the same subject. Admit after that, with a short-call cell + K row if it shows. Frank's ruling on Q3 is OPEN, pending the revision's measured factor.

## Dispositions
| id | finding | disposition |
|---|---|---|
| sem B-1 | K73 SEEK mutates search_from -> \G true at the seeked start on the tie re-entry (witness `\Ga\n?\|a$\|a\n$\|$`, -e utf8, "\x80a\n": (1,2) expected, design gives (1,3)) | ACCEPT: seek into a separate local; witness in G1 utf8 + an MS row |
| chk B1 / arch M1 / sem MF3 | dominance "<= today + 2" false (two reverse walks + tie; G3 shapes lack a final \n) | ACCEPT: one reverse pass seeding n and n-1; end-known fast path; G3 = T <= today(-fno-match-split, same subject) + c over named shapes incl. trailing-run+\n; the true factor goes to Frank (Q3) |
| sem MF1 / chk M1 | agreement check (a) vacuous post-kill / false-fires pre-kill | ACCEPT sem's form: pre-kill NFA with only N_BOT/N_GSTART killed has no live N_BOT_M; MS row (bot_m always false; `^x\|\n(?m:^)a$`) |
| sem MF2 | floor "0"/"search_from" chosen from the AST fact; a missed \G deletes matches | ACCEPT: read P's machine (s1g gstart family) like attempt-gstart, or agreement check (c) |
| arch M2 | BOUND rows floor-bot/floor-gstart hand an UPPER they cannot honour; new BOUND->LOCATE edge ([CAND-PATH-READS] class); third floor source | ACCEPT: floor extent as the split LOCATE row's payload; BOUND untouched |
| chk M2-M5 | MS-1 plant wrong; MS-4 unreached; MS-2 mis-specified; no rows for decline conjuncts; G3 vacuous-capable; population by count | ACCEPT all (chk.md) |
| chk M6 / arch S5 | re-pin and re-aim list is prose, not a D94 grep; ~12 readers missing; ABI line cite | ACCEPT: grep recipe + sabotage_anchors.py --step list |
| sem S1 | S+LS / G+LS are NOT linear today (`\Ax\|(?m)^\s+y` x15.6 per 4x) | ACCEPT: reword; filed **K109** beside K106's LS+LE (4b.2) |
| sem S2 / arch S2 | Q in job->rdfa silently changes rdfa readers on CR_ATTEMPT; 4b needs Q's pair | ACCEPT: a separate Q container; gate that the floor-loop text is unchanged |
| arch S3 | Q built under the 32000 TABLE cap | ACCEPT: derive min(P ceiling, 4096) or a limits.def row with its measurement |
| arch S1 / S4 / unlock 1 | racing locator chosen by a fact (hidden if-chain, family of >=3); tie should be a FINISH row; **Q as a sub-artifact (a full search over Q) makes 4b an admission widening** | **DIRECTION QUESTION for Frank** (below) |
| arch S7 | pin_split = 5th position-pin family member | ACCEPT: projection check as a gate; U3 gets a dated trigger |
| chk S1-S4, sem N1-N3, arch notes | corpus breadth, overflow witnesses, MS-6 direction, interior-$ witnesses, Q exactness conjunct, wording, \z-only no-tie gating, RX_DFA_START sentence | ACCEPT for the revision |

## Direction question (for Frank, discussion)
**Problem.** 4a as designed builds pin-specific machinery: a factored end walk, a tie special case and a fact-chosen racing hat. 4b (START+FREE: concat-sqli and 21 S+F patterns, trigger MET) would add a second racing locator and likely rework all three.
**Arch unlock 1.** Emit Q as a sub-artifact, a full unanchored search over the reverse-able machine, through the existing static-engine door that the VM hybrid's prefilter already uses. Then split(P) = floor attempt + Q.search. The existing LOCATE table picks Q's locator (rev-end when Q is end-pinned, composite otherwise), with ties and verify-at already proven. 4b becomes an admission widening, not a build. The two-seed cost fix lands once, in rev-end itself, and helps rev-end's own artifacts too.
**Forces.** For: no parallel mechanism, no 4a rebuild, the house rules (general mechanisms; builds that will not be rebuilt). Against: an indirection in the emitters (they read job->dfa/rdfa directly), so a bigger first step and probably more movers. 
**Leaning:** sub-artifact, with the tie as a FINISH row (arch S4). The revision lane designs it and measures the emitter indirection's size before committing.

---
# sem critic (opus) — algorithm survived; one miscompile
BLOCKER-1: K73 SEEK overwrites search_from; tie re-entry then sees start==search_from -> \G seed at wrong position. Witness \Ga\n?|a$|a\n$|$ -e utf8, subject "\x80a\n", search_from 0: today+pcre2 (1,2); design (1,3). Fix: seek into separate local split_floor (never mutate search_from) or restore before tie goto; G1 utf8 witness + MS row (plant: walk floor on search_from itself).
MUST-FIX-1: assertion (a) vacuous post-kill / refuses legal (?m)\A^\s+|\s+\Z pre-kill. Fix: state (a) on pre-kill NFA with only N_BOT,N_GSTART killed: no live N_BOT_M. MS row: plant bot_m always false; witness ^x|\n(?m:^)a$.
MUST-FIX-2: floor rows pick "0" vs "search_from" from the AST fact; a missed \G deletes matches unchecked. Fix: read the machine (s1g gstart family) like attempt-gstart; "search_from" is safe for S too (only unsafe direction = G reported absent). (truncated)
MF2 fix cont: select floor-gstart when P's attempt machine has gstart family (s1g != plain), or agreement check (c) live N_GSTART => G in floor.
MF3: dominance false (two independent reverse walks emit_dfa.c:11697-11720 + forward tie). Trim on "x"+" "^k+"\n": today ~k+3, split ~3k+5. Measured k=4M: rev-end \s+$ 0.75ms (no \n) vs 5.90ms (final \n); attempt ^\s+|\s+$ 1.46ms both; split est ~3ms vs 1.46 (~2x). G3 shapes lack final \n. Fix: one reverse pass seeding n and n-1, or accept ratio with K row; add Q.\t^k.\n, \t^k\n to G3.
S1: S+LS/G+LS NOT linear: \Ax|(?m)^\s+y on "\n"^k.Q: 1.34/18.2/283.6 ms at k=2k/8k/32k (x15.6 per 4x) — quadratic (MLINE attempts read across \n). Census witnesses linear by accident. Reword; file beside K106 LS+LE (4b.2).
S2: Q in job->rdfa changes rdfa readers on CR_ATTEMPT (unanch_start ORs dfa/rdfa eol/end vars; 10 callers incl RX_DFA_PREFILTER stamp, cand scan, cand_ppm, locate_empty, start_landing, scan_state_written) — moves would hide among expected movers. Separate job->qdfa + gate floor-loop text unchanged.
N1: add interior-$ witnesses ^x|a$\n, ^x|a$\n?, ^x|a$(?=\n). N2: admission must check Q exactness (job->rnfa.erased==0) explicitly. N3: G+E find-all wording loose (\G\n|b$ on "b\n" -> (0,1),(1,2)).
UNREFUTED: algorithm simulated via libpcre2 (floor ANCHORED, Q = P with anchors -> (?!), seeds {n, n-1}, tie = priority match anchored at s*): 54.2M cells, 492k ties, 0 diffs. §2 witnesses agree; context at walk start ok; anchors in lookarounds route VM (declined); newline conventions refused; WINDOW clamp safe; declines conservative; no NOTEMPTY mode; N_BOT/N_GSTART kill sound, Q ⊆ P. Only deletion modes = N_BOT_M kill (MF1) + missed G floor (MF2).

# chk critic (sonnet) — match_split_pinonly.md
B1 BLOCKER: dominance claim false. rev-end walk = 2 reverse passes when s[n-1]=='\n' + forward tie attempt. Twins: \s+$ rev-end on Q+tab*4000+\n = 12,010 loads (3.0n) vs ^\s+|\s+$ attempt today 4,003; a[^x]*$ rev-end 2k+5 vs -fno-rev-end k+2. G3's 4n+8 lets it through. Fix: one reverse pass injecting the n-1 seed; resolve tie by comparing seeds' accepting ends where possible; G3 = T <= today(-fno-match-split, same subject) + c, add these cells. Q3 back to Frank with real factor.
M1: agreement assertion (a) vacuous (checked after kill). Run on P's NFA before kill: every live path through a BOT-family node must be a floor path (N_BOT_M unpinned non-leading e.g. a|\n(?m)^b$). Add P-side removed-vs-floor path count.
M2: MS-1 plant "0"->"-1" makes start_max SIZE_MAX (unbounded floor), witness won't go red. Plant first > start_max; name detector.
M3: MS-4 witness (?m)^a|b$ has empty floor -> plant unreached; use ^a|(?m:b$). MS-2: use \Ga$|b$ on "xa" startpos 0 expect no match. Kill-set omission rows detect via compile failure: mark, confirm harness counts refused compile red, add answer-level twin.
M4: no rows/witnesses for decline conjuncts (!decline, !bot_m, anchors in lookaround, \K, mid-path (?m)^). Add rows + negative controls reach-proved by stamp != split: ^a\Kb|c$, (?<=^a)b|c$, ^x|\n(?m)^b$, x^a|b$.
M5: G3 too loose/vacuous-capable: assert T <= today(-fno-match-split same subject)+c; name >=4 subject shapes (internal run, trailing run, trailing run+"\n" tie, no-match+trailing "\n"); qwork attempts=marker-in-src => assert att>=1 on floor-matching subject; population guard must be per-ID manifest of the 22 admitted IDs, not a count.
M6: re-pin list not a D94 grep list. Missing: mech S636/S637/S238 (size-rung attribution), run_fallback_table.sh + dec_fallback listing_declared_*.tsv + refactor_edit_set.tsv (fit_rungs[] row), tests/revend/* (gen_rev_end.py, window_twin*, run_rev_end.sh), mech S768/S771 (anchors in refactored code), run_prechecks.sh, run_scan_edge_census.sh, cand_oracle_witnesses.tsv, assertions/rev_end.rxt; tuning/limits/registry hunks; ABI line cite :51 vs :54. State as grep recipe.
S1: corpus: 20/22 admitted are hand idioms; add planted.txt 35 C4 witnesses as G1 controls; declined classes as stamp != split controls; cells "a\n\n", empty, startpos>0 S-only, startpos>n, utf8 mid-char startpos, hybrid floor+E tie, (?m) scoped to one arm; G2 generator over floor x racing x decline with \n \r.
S2: MS-9/MS-11 need constructed witnesses (Q overflows cap while P fits; fits only without Q).
S3: MS-6 plant only EOL->Z direction.
S4: msclass cross-read is transcription-only; independent controls = libpcre2 C2/C3 + NFA assertion after M1.
N1: §5.1 loads off by nl_last probe: split ~3 loads not 2 on internal run; Q.tab^k ~k+4 vs k+2. Linearity unaffected; recount or use "~".
N2: landing bar holds: the 5 fully-anchored artifacts are mix S, concat-sqli S+F; racing=={E} false for all IF predicate requires non-empty racing. Pin by ID (12 bench rows) in identity gate.
N3: bit 55 next free (max used 54 NO_START_LANDING); 8 remain.
UNREFUTED: K106 linear (~3 loads); wrapper strip <=1 attempt entry; find-all <=3 walks (E matches end at n-1/n); R1/R2 soundness no counterexample (guard M1 weak).

# arch critic (sonnet) — no BLOCKER
M1: dominance false for two-seed + tie (same as chk B1); ^x|\s+$ on "ab"+1e5 sp+"\n" ~3L vs L. Restate as <=3(n-s*)+O(1), add trailing-newline long-match cell to G3 + landing bar; or skip n-1 seed when seed n's walk ended at floor.
M2: BOUND rows floor-bot/floor-gstart lie (CT_UPPER "no match starts above x" with start_max 0 while matches start later; shield is only that CAND_BOUND_ONE readers test .one); need new reads BOUND->LOCATE edge ([CAND-PATH-READS] class); duplicate bot/attempt-gstart texts; third source for "floor". Fix: u.locate.floor payload on the split LOCATE row passed to a shared loop emitter; BOUND untouched (sees `all`, conservative); two rows + one edge fewer.
S1: racing sub-locator chosen by a fact = hidden if-chain; family of >=3 (rev-end 4a, composite over Q 4b, rev-inner per-branch landmarks D151 add.6 F2). Make split_racers[] first-match table now (one row end-walk).
S2: Q in job->rdfa must be rebuilt in 4b; introduce job->q.{rnfa,rdfa} container now; emit walk as file-scope static <p>_split_end so 4b swaps body.
S3: Q built under wrong cap (truncated)...
S3: Q cap = PCREC_MAX_DFA_STATES_TABLE (32000) but build_anchored_dfa uses PCREC_ANCHORED_MAX_STATES 4096; P attempt capped 10000 -> Q could cost more compile CPU than anything today (K53 lesson). Derive min(P ceiling, 4096) or limits.def row with measurement.
S4: tie-in-locator special case should be FINISH row attempt-at with take[ATTEMPT]={ENDSET}; locator hands ENDSET like rev-end; that IS U8's verify-at hat and 4c's unit. _match unchanged.
S5: derived re-aim list missing: rev-end rows S758-S781 text-anchored (emit_end_walk move), start_max/return-0 anchors S263/S269/S274/S276/S441/S492; run scripts/sabotage_anchors.py --step; state C1 trace site-key delta.
S6: bit 55 defensible; honest budget: 9 free now, 8 after, trigger <=4; queued consumers rev-inner, rev-end-width, ADAPTIVE-ARM, maybe 4b. Put in §6.2.
S7: pin_split = 5th position-pin family member; epin dupes end_pin; make projection check a gate (run_facts_checks.sh) and give U3 a dated trigger; state pin_split admits interior $ (22 corpus move at U3).
NOTES: \z-only no tie -> gate goto/label/split_walked on revend_ties predicate (-Werror unused label class); RX_DFA_START reverse-pass understates (sentence in ¶11, xref match_api.md §6.3.4¶11 (the DFA_START attempt-start row)); spec/abi readers otherwise complete; Q-overflow path correct.
UNLOCKS: (1) Q as sub-artifact via pcrec_emit_dfa_engine(name,"static ") = full ENG_UNANCH search over Q; split(P)=floor attempt + Q.search; 4a racing admission/emit_end_walk/tie collapse into existing rows; 4b = admission widening. Trigger MET (concat-sqli). DECIDE BEFORE 4a BUILD. (2) FINISH attempt-at (ENDSET now; AT = U8 trigger: match-regime cell on unanchored ATTEMPT). (3) optional-machine builder w/ kill-set+cap -> capture-erased reverse locator on CR_VM closes K108; trigger K108 population. (4) U3 pin fact unification; trigger 4a + one timed cell among 22. (5) per-branch landmark racers rows; trigger ENG-TACTICS stage 1 + census. (6) FINDALL-NEXT cache; trigger 4c/LS+LE + dense find-all cell. (7) row-name deny -fdeny=locate:split; trigger IFACE-PUSH <=4 bits. (8) U5 BOONIES.
