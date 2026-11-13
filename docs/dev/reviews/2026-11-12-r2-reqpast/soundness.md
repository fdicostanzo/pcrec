# soundness findings

## Findings

None. No answer moved in any probe: BASE, SUBJECT, SUBJECT `-fno-req-handoff`, and libpcre2 (tools/p2) agree on every case. The one difference is a give-up becoming the correct NOMATCH, which is the allowed direction. The premise and the stop both held when hand-read and when probed (details below).

## PROBED-AND-HELD

Hand-read (SUBJECT bd014691):
- Premise, part (a). src/facts/req.c's walk never descends into a lookaround body. The header gives the reason: lookbehind bytes lie before the match start. A positive lookaround, `\K`, `\b`, `\G` and `$` are zero-width units, so the bytes on their two sides are adjacent in the subject. Backreferences, linked calls (`(?1)`, `(?&x)`, `(?R)`) and consuming callouts are unbounded gaps. Atomic groups and captures are transparent. So every run byte is one the anchored attempt at p consumes, at a position >= p. The proof uses no bound on K, so the unbounded row needs nothing beyond what the bounded row and the BASE gate already rely on.
- Constructs that cannot reach the row (no producer, or out of scope): `(*ACCEPT)` (module 'verbs' has no producer, even under `--features all`), conditionals (not implemented), and (*SKIP)/(*COMMIT)/(*PRUNE)/(*THEN), which are rejected outright. The only advance is the encoding's own `retry_adv`. The prefilter reseed and adaptive reseed (`retry_win`/`retry_seed`) need a prefilter, and `pcrec_artifact_has_dfa_scan` is true whenever `fit.prefilter` is set. So the row and those advances never coexist.
- What `landmark_position` is, part (b). It is the START of the WHOLE run, not a needle inside it. Checked in the emitted `rx_reqrun`: it returns `cand`, the run start; `memchr` hits the window byte at +3 and steps back. Also checked in the masked 32-position `rx_reqrun_whole`, which returns `cand -= 21` (the whole-run start). In the entry, `landmark_position = handoff_position` is assigned BEFORE `handoff_position = search_from`, so the kept hit is the real hit (emit_dfa.c:1201 then :1217).
- The re-ask, part (b). It runs after `attempt_position++` (or the utf8 char advance) and before the start-set seek. It is taken only when `landmark_position < attempt_position`, from `attempt_position`, and it only returns 0 or updates the landmark. It never moves `attempt_position`, so no UTF-8 rounding is needed and startpos>0 is untouched. A seek that jumps past a stale landmark costs at most one extra attempt before the next re-ask, which is speed-only. The bounded row has the same order ("two lower bounds, each sound alone").
- Budget direction, part (b). The surviving attempts are a prefix of BASE's attempts, in the same order, from the same run state. The re-ask spends no steps. So the row can only turn a give-up into an answer, never the reverse.
- `-fno-req-handoff`: the emitted C is byte-identical to BASE apart from the abi number and the header include name.
- The row lights only through the shared `req_handoff_vm_run` conjuncts plus `req_parts_in_whole`. A long caseless pattern whose `q` is necessary but outside the whole run stamped "none", as it should.

Probed: 21 differential cases (base / subj / p2 on one subject each, mostly `--engine=vm --features all`), all agreeing:
- plain `(a|b)\w*foobar` at sp 0 and 9; `\K` (`(a|b)\w*\Kfoobar`, sp 1)
- run joined across a lookbehind, `(a|b)\w*fo(?<=foo)obar`, at sp 3
- lookahead holding run bytes, `(a|b)(?=\w*foobar)\w*foo`; a backreference, `(\w)\w*foobar\1`, at sp 2 and under `--engine=auto`
- recursion, `(a(?1)?b)\w*foobar`, at sp 3
- `(?m)...foobar$`; `\b` after the run
- partial `\G`, `(?:\G|x)(a|b)\w*foobar`, at sp 0 and 2
- `-e utf8` with multibyte runs, `(é|b)\w*fooβar`, plain and `(?i)` at sp 3
- a 32-position masked caseless whole run, at sp 1
- the step budget: `(a|b)\w*\w*\w*foobar` over `xfoobar`+60·a+`!`
  - at --step-budget=100000, BASE gives err -2, SUBJECT gives nomatch, p2 gives nomatch (the allowed direction)
  - at 300/3000 both give err -2 (one attempt alone exceeds the budget)
  - runs ahead of the attempts: both err

Stamp survey: 26 patterns; "unbounded" on 17. No row on: `x.*\Kfoobar`, a leading lookbehind, `\G`-only, a DEFINE+call, auto-engine `\K`, and the long caseless pattern with `q` outside the whole run.

Total: about 75 compiles, all niced, before 20:00.
