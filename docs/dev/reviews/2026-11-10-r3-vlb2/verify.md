# VERIFY
## V1
HOLDS. Ran ora.py (ctypes oracle) on all six: ACCEPT ((0,3),((0,1),(1,2))); ACCEPT; REJECT 125; REJECT 125; ACCEPT; REJECT 125. `build/pcrec --features all -p rx --pattern '(a|\2)(b|\1)x'` rc=0 (compiles).

## V2
HOLDS. Oracle: ACCEPT; REJECT 125; ACCEPT. pcrec on 1st: 'every alternative of a lookbehind must have a bounded length (this one is unbounded) (pattern offset 23)'; on 3rd same text (offset 7).

## V3
HOLDS. --emit-facts `(a|bc)\1$`: `end_window ... declined ... decline:unbounded`, `RX_END_WINDOW "none"`; `(a|bc)bc$`: `derived ... 5`, `RX_END_WINDOW "5"`. Callers: endwin.c:119,251,364 and startanch.c:100 call pcrec_cwmax (grep). mrl.c ~:586-596: `case A_BREF: case A_VAR: case A_CALLOUT: return pcrec_sat_add(acc, row_cwmax(a, any), MRL_MINW_MAX);` (shared arm, comment 'UNBOUNDED').

## V4
HOLDS (text) / PARTLY (offsets vary, not asserted). All six print the one sentence 'a lookbehind containing a backreference, a variable or a consuming callout is not implemented (its length is known only when matching)' with offsets 3,4,8,0,20,3. pattern_language.md: :150 '(a backreference inside a lookbehind, §7.4; ...)'; :460 '[7.3¶6] A backreference inside a lookbehind is refused (§7.4).'; :480 7.4¶5 '...So is a lookbehind containing a backreference, a module vars variable or a consuming callout (`(a)(?<=\1)`...shape 5: libpcre2 accepts the first)'; :626 9¶2 'a lookbehind containing a backreference, a variable or a consuming callout (§7.4)'. All four present.

## V5
HOLDS (line numbers drift slightly). Oracle: all four REJECT 125. pcrec compiles `(a(?1){0})(?<=(?1))x` (rc=0); --emit-main + gcc -O0, `./v5 aax` -> 'match 1 3'. callgraph.c:944-946 `case A_BREF: case A_VAR: case A_CALLOUT: return;` inside cg_length_calls (HOLDS). pcrec_callgraph_lookbehind_recurses at :977; `if (n == 0) return false;` is at :981 (n = ntargets; claimed ~:967-977 is off by ~4-14 lines, and the 'no call' case is via ntargets==0, with callgraph build returning at :701 `if (sc.ncall == 0) return;`).

## V6
HOLDS. Oracle: ACCEPT; REJECT 125; REJECT 125. pcrec compiles `(a(?=\1)|b)x` rc=0.

## V7
HOLDS. Oracle: `(a)(?<=\1)(?|b|c)x` REJECT 125; `(?<=(?|(a)|(b)))\1x` ACCEPT.

## V8
HOLDS. Oracle: REJECT 187; ACCEPT; REJECT 200; ACCEPT; REJECT 125 (all as claimed).

## V9
PARTLY. HOLDS: check.py:244-247 `lbline = ... '#define rx_VALID_LB '`; `if lb != rs[0].mlb: bad("... libpcre2 10.46's MAXLOOKBEHIND is {rs[0].mlb}")`. HOLDS: vlb_accept.py:~125-165 `if mine is None: if theirs: pcre2only += 1; continue` (no reason recorded). REFUTED part: tests/utfcheck/CLAUDE.md does NOT say check.py is not run by make: line 1 says '`make test-utfcheck`, in TEST_SECTIONS'; Makefile:1459-1461 test-utfcheck runs run_utfcheck.sh, which line 18 runs check.py. Only `probe_pcre2.c` (the libpcre2 oracle probe, CLAUDE.md:22) is 'NOT built by make; run ONCE'; check.py compares against its stored answers (rs[0].mlb), not live libpcre2.

## V10
PARTLY. Backreference-in-lookbehind perr .rxt rows (grep -rn '^pattern .*(?<[=!]...\\N' under tests/, verified each has `perr`): lookaround/refused.rxt:165,176 (2); lookaround/gated.rxt:127 (1); lookaround/d27/refusals.rxt:186,191 (2) = TOTAL 5 perr rows. Not perr: nonatomic_behind.rxt:57 `(?<=(a)|(ba))c\2` (backref outside the lookbehind), recursion/d27/sr_captures.rxt:169, possessify/composition_d27 rows (backref outside lookbehind). Non-.rxt refusals beyond the 5: tests/reject/run_reject_tests.sh:1958 `(a)(?<=\1)x` (shape 5) and :1961-1962 `(a)(?<=a+|\1)x`, `(?<=(a)\1{2,})x` (unbounded, shape 7); gen_corpus.py:696,704,815 and d27/gen_refusals.py:79-80 generate the same rows; vlb_accept.py:77-78 population. HOLDS: run_lookaround_diff.sh:443 `VLB_ACC_EXPECT="vlb_accept: total=234 both=154 divergent=32 pcre2only=2 bad=0"`. HOLDS: pcrec_has_call DEFINED atomic.c:1000, read (called) by possessify.c:2138 and mod_lookaround.c:626. REFUTED for select_engine.c: only comments mention it (lines 306, 959); code uses `kinds & PF_KIND_LINKED_CALL` (:970), no call. callgraph.c:700-701 `if (sc.ncall == 0) return;` HOLDS.

## V11
HOLDS. `grep -n 'never fixed-width\|libpcre2 gives too' src/opt/mrl.c | wc -l` -> 0; `ls docs/design/vlb_d27_extract.md` -> No such file or directory (build tree).

## V12
HOLDS. altcls.c:131-147: 'A lookaround body is not walked ... case A_LOOK:' and 'this walk REBUILDS nodes (pcrec_spine_build, and the A_REP/A_CAP arms below allocate a fresh node when the body changes)'. compile.c order: pcrec_altcls :2878, pcrec_callgraph_build :2913, pcrec_postresolve :2968.

## V13
HOLDS. `build/pcrec --features all -p rx -o v13.c --pattern` on `(a)(?<=a(?=\1))x` and `(?<=(a)(?=\1))x`: no output, both compile.

## V14
HOLDS. `(a)(?<=\1|b+)x` -> 'pcrec: every alternative of a lookbehind must have a bounded length (this one is unbounded) (pattern offset 3)'.


VERIFY COMPLETE
