# verify.md — round k147fix (r64), INLINE verification by the coordinator
(Every CONFIRMED finding below is a quote claim or a one-call repro, so no verifier agent ran (skill §6.2).
SUSPECTED SABOTAGE-1/-3 were tested with three coordinator-built plants under plants/V1, V3a, V3i.)
Calls: kit/stack.sh TREE BYTES FILE; patterns built by python (O*n + core + C*n), files under .coord/v/.

## DEPTH-1  HOLDS
subject 442368 `(?:abc|abd`x250 `abe` `)*`x250 -> rc=0 hw=440176 (0.5% under budget). limits.md §3.10 ¶2 and ¶5
still state >=20% headroom over every ¶3 family / the measured worst. Quote claim checked.
## DEPTH-2  HOLDS (pre-existing)
`^(?i:` + `(?:abc|abd`x249 `abe` `)*`x249 + `)|b$`: base 442368 DIED exit=139; subject 442368 DIED exit=139;
subject 8 MB rc=0 hw=452080; with 250 inner levels: rc=-1 "parentheses are too deeply nested" (so 249+1 is legal).
## DEPTH-3  HOLDS
`(abc|abd`x250 `abe` `)*`x250 + `d`: base DIED 139; subject rc=0 hw=440560. At 131072: 64 levels rc=0 hw=131056, 65 DIED 139
(¶4 says 87 for the bare nest).
## DEPTH-4  HOLDS
`build/pcrec --list-limits` (subject): PCREC_COMPILE_STACK_BUDGET "at least 1.2x the worst measured family (1.25x today)",
"any pattern up to PCREC_MAX_GROUP_DEPTH"; contradicted by DEPTH-1/-2 figures (440,176 = 1.005x; 452,080 > budget).
## DEPTH-5  HOLDS (pre-existing)
`(?|`x250 `a` `)`x250 subject: rc=-1 hw=18552 (¶3 says 16,792).
## SABOTAGE-1  HOLDS (upgraded SUSPECTED -> CONFIRMED by plant V1)
plant V1 = SUBJECT with `widen:`'s `v = fst_leaf(q, f->a);` -> `v = f->acc;`.
Witness `(x)(\1)…(\64)x+\65` (319 chars) on x^67, --engine=vm: subject `match 0 67`; plant V1 `nomatch`; libpcre2 `M 0 67`.
grep of tests/possessify/ for \65..\99: no hits (no cell reaches the bound).
## SABOTAGE-2  HOLDS
`--list-limits` PCREC_MAX_POSS_REF_DEPTH: "...so it bounds pcrec's own C stack (D10/K20). The value is a stack bound";
possessify.c's section header at SUBJECT: "The depth bound now bounds the arena's frames rather than the C stack".
## SABOTAGE-3  PARTLY
(a) plant V3a (CAPG `F->val[f->g] = f->acc;` deleted): the call-free `(x)x+\1x+\1` is LOUD on the plant
("internal error: possessify: A1 continuation disagrees with FOLLOW", rc 1), and the existing cell `(a?)(x+\1)b(?2)x` on xbxx
answers nomatch (oracle M 0 4): the point IS covered (any corpus compile + that cell). The "no cell" half is REFUTED.
(i) plant V3i (gk_build CAT: `acc->nullable` updated before the `last` union): 8 patterns ((?:a+b?){2,2}c, (?:ab?){2}a,
(?:a+b?)+c, (?:ab?)*a, (?:b?a+)+ab, (?:a?b)+b, (?:ab*)+b, (?:a*b)+a): 0/8 emitted-C differences, answers = oracle on 4.
The critic's predicted catch is NOT confirmed; the plant is silent on every probe tried: an uncovered point, witness unknown.
(c), (g-out-of-range), (j): answer-silent by the critic's own reading; not run. (h): not run.
## FAMILIES-1  HOLDS (quoted by critic with stack.sh lines; `*+` hw 293,552 agrees with DEPTH's independent re-measure)
## HOUSE-1..6  HOLD as quote claims (spot-checked: possessify.c:848 widen, 862-866 publish, 1190-1202 CAT; HOUSE-5's
objdump claim not re-run). HOUSE-7..10 are design claims; not verified beyond the critic's greps.
VERIFY COMPLETE 17:30
