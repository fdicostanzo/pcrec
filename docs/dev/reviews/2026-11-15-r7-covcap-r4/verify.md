# VERIFY — covcap-r4

## Verdicts

### FI-3 — HOLDS (as written; not built)
Commands: `kit/kp.sh 'a(?:b|c)(?:$|q(?<=x))'` -> byte+utf8 `KITPROOF no-eol-view k=0` (today declines). `kit/machine.py` same -> `span=2 exact=2 S: 61,62-63`. `fixinduced/eolprobe.py` -> `acc [F,F,T,F]`, `views {'eol_view': [None,None,None,2]}` (the only non-identity view sits on the row reached at depth 2 = k). Oracle (`kit/oracle`, subject `ab\n`): `0:2,-,-,-|0:2` i.e. PCRE2 matches (0,2).
known.c (review tree) lines 281-290: `/* C9: no row on the walk at depth 0..k carries a non-identity eol view */ ... for (int j = 0; j <= st->w.k; j++)` -> inclusive of k.
Rev 4 text: rule 2 (line 160) "Some row accepts in any form: the walk ends, k = j (C10/C11 then read the rows at k)" — no C9; C9 appears only in rule 3 (line 162), which runs only when no row accepts, i.e. j<k. Other C9 mentions (lines 344, 455, 500-501) restate "per-depth C9 check" / "C9-C11"; none adds the depth-k check. grep -n C9 over rev 4 shows no restoring sentence (§3.3, §5.4 do not). So the rule as written skips C9 at k; no refutation.

### READY-1 — HOLDS (derivation; plant not run, no make)
Quoted: tests/kitproof/cases.tsv:25 `verdict - ac|bd decline S1131: C8 machine-inexact`; run_cover.sh:76-78 compare only `[ "$s" = cover ]` / `[ "$s" != cover ]` (decline = "anything else"). known.c cc_end (C10, ~l.294-303): `if (!kn_acc_any(st->d, q.s)) return false;` over rows at `w.k`. Rev 4 §3.1 rules 1-3: accept test (rule 2) precedes set comparison (rule 3), so rows at L (branch stop) are non-accepting; `ac|bd` has rows {c-row},{d-row} at depth 1 with different sets, none accepting -> C10 declines even with C8 skipped. The verdict row cannot flip. Caveat: the rule's `k` value on a branch stop is "not known", so C10's read there is itself unspecified in the text (reinforces, not refutes).

### READY-3 — PARTLY
Holds: ordering. known.c:276-277 (today, inside C8 `cc_exact`): `st->cv->end.k = (uint8_t)k; memcpy(st->cv->end.set, st->w.set, sizeof st->cv->end.set);` (fixed sizeof = 32x32, cannot overrun). C13 `cc_served` (known.c:342-345) calls `pcrec_cover_site(...)` (known.c:485-499) which calls `cover_window(cx, s, e)` (known.c:462-478) reading `e->k` and `e->set[d]` for d<k and writing `pcrec_memfn_wpos_bits(&sp[0], d, ...)` before `pcrec_memfn_window_stated`. So `cv->end` must be filled before C13; rev 4 §3.3 (line 272-274) says it is "filled from the record when the decision is `cover`" with no stated bound, and R-13 (§3.5 line 316) bounds only `cover_window`.
Not shown: the overrun. Rev 4 does not say the fill is a counted k x 32 copy (the critic infers it from S1131's re-anchor); if the build keeps today's fixed-size memcpy in C8 the fill is safe and `a{40}(?:b|cc)` fails C10 before any fill under "when the decision is cover". So the finding is a valid hardening note (name the fill's bound), SUSPECTED not CONFIRMED, as the critic itself labelled it.

### READY-5 — HOLDS
`kit/kp.sh 'a\z\W|b{32}'`: byte+utf8 `KITPROOF fixed-width k=0`, `RX_DFA_SCAN "unanchored"`, today's span_facts `24:98...` (not a cover today). `build/pcrec -p rx --features all --emit-facts --pattern 'a\z\W|b{32}'`: `width [2,32]`. `kit/machine.py`: `span=32 exact=32`, `S: 62 x32`. Rev 4 §5.2 (line 453) predicts INTO only for `fixed-width` with `wmin` in 25..32; this compile has wmin 2 yet first-accept depth 32 (a-arm dead), so C7 (k=32 <= 31+1 per critic's reading of KN_CAP) would admit it as a candidate the prediction omits. Synthetic witness; population presence unknown. (Whether it finally moves also needs C9-C15; the claim is only that the prediction rule can miss it.)

### FI-1 — HOLDS
`kit/kp.sh` (byte+utf8): `a{2047}b{2048}` -> `fixed-width`; `a{2048}b{2048}` -> `anchored-A`; `[ab]*a[ab]{12}` -> `anchored-A`; `[ab]*a[ab]{11}` -> `exact/producer-short`. So the 4095-position boundary sits exactly where rev 4's straight-line witnesses do (both are single lines; `a{3000}b{3000}` is 6000 positions), while the genuinely many-paths shape flips at 13 positions. Rev 4's "many paths meets it sooner (`a{3000}b{3000}` does)" is an example of length, not of path count. Text-only.

### FI-2 — HOLDS (by reading)
src/ir/dfa.c:1911-1914: `const int ncell = d->ncls + (d->island ? d->nchr : 0); d->maxstates = maxstates; if (d->maxstates > PCREC_MAX_TABLE_ENTRIES / ncell) d->maxstates = PCREC_MAX_TABLE_ENTRIES / ncell;`. limits.def:164 `PCREC_MAX_TABLE_ENTRIES 2000000`; limits.def:417 `PCREC_MAX_CHAR_STEP_ATOMS 32`; ncls built by `refine_by` over byte classes (<=256). ncell <= 256+32 = 288; 2000000/288 = 6944 > 4096 (PCREC_ANCHORED_MAX_STATES, limits.def:186, passed at compile.c:406). Narrowing cannot bind for the anchored machine. Rev 4 mentions it at §3.1 line 196 and §8 line 564.

### FI-6 — HOLDS (by reading)
kset.c:860-861 `if (nfa->st[i].k == N_ACCEPT && nfa->st[i].dist) return PF_WHY_MARKED;` is the same test as dfa.c:1850-1852 `d->tagged = false; for ... if (nfa->st[i].k == N_ACCEPT && nfa->st[i].dist) d->tagged = true;`; C5 `cc_unmarked` (known.c:204-206) is `return !st->d->tagged;`. Rev 4 line 237 keeps the three guards "at the top of `cc_anchored`" (C4, known.c:194, which precedes C5), so a `marked` guard there fires on exactly C5's population and C5 can no longer be the `why` — a parallel mechanism. Population point also correct: V-10's 72 decisions are compiles that reached C8; guard lines at C4 see compiles that today stop at C5-C7. (Assumes the DFA is built from the same NFA the slice read; critic cites compile.c build_anchored_dfa; not re-traced.)

### READY-2 — HOLDS (text)
Rev 4 line 479: "The loader in `run_cover.sh` selects the new section by `$2 == "cover"` and reads the §3.3 columns". The existing loader (run_cover.sh:84) keys `awk -F'\t' '$2 == "span_facts" { print $7 }'`, i.e. $1 = encoding, $2 = fact name; facts_listing.md [3¶2] "Every table is a NAMED `#section`" (rows carry no section name). The new section's columns per §3.3 are `encoding | why | k | exact_len | sets`, so `$2` is `why`; `$2 == "cover"` would select only cover-decision rows. And the VALUE spelling is inconsistent within §5.3 (lines 472-478: `exact_len:sets` for most rows, "`why` `anchored-A`, `0`" for a{4096}). Text defect, red not vacuous.

### READY-4 — PARTLY
Holds: `memfn/window_site.md` does not exist (`ls` fails); it is `docs/design/memfn/window_site.md`. `build_anchored_dfa` is compile.c:382, `cc_anchored` is known.c:194 (C4), so rev 4's "`compile.c`'s anchored build, `cc_anchored`" conflates them. `grep -l span_facts` over the review tree finds live mentions in docs/design/kit_proof/conj.py, kit_proof/witnesses.txt, scripts/NOTES.md, docs/design/memfn/CLAUDE.md, scripts/tests/emit_sweep.py.test, which rev 4's §5.5 list (lines 520-526) does not name.
Softened: rev 4 does exempt LIVING design notes (ctx_span.md etc.) via a dated "superseded" note (lines 528-531), and HISTORY includes journal/decisions/reviews/lanes; the critic's "cannot reach 0" is true as to the enumerated tooling files (conj.py, witnesses.txt, studies data, kit ledgers), not as to design notes. Did not re-grep all ~12 files individually.

### FI-4 — HOLDS (text)
Rev 4 line 269-270: "`k` and `exact_len` (`uint16_t`; 0 where not reached)"; line 283 "Where C1-C6 fail: the `why`, `exact_len` 0"; lines 286-287 "Other rows read `exact_len` `-`" (rows neither cover nor width-bounded); line 417 "states `exact_len` 0". An unbounded-width C1-C6 decline is thus 0 by line 283 and `-` by line 287. `k` has no stated/unstated rule beyond `unasked` (line 281). Direct reading; sentences coexist.

### FI-5 — HOLDS
x0.py:835-866 `stated()` splits `fl, pat, ex, sets, label` (five columns, no wmax) and calls `explore(O, contexts(...), len(S), 64, rnd, ...)` with no `horizon`; x0.py:242 `hz = depth if horizon is None else horizon`. Rerun (`X0PCRE=kit/x0pcre python3 -I fixinduced/x0h.py <tree>/docs/design/kit_proof/x0 fixinduced/x0rows.tsv`, cwd verify/): `ab|ac{10} hz None RED` / `hz 11 green`; `a{30}(?:b{30}c|d) hz None RED` / `hz 61 green`; `ab|abc|ad` and `a[xy]c|b[xy]d` green both ways. (Extra row `(?:ab|cd)e{3}|ab` red both — not a critic claim; probably an input row whose stated sets are not true.) Rev 4 §3.3 line 286 says X0 "is given wmax as its horizon" without naming the x0.py edit.

VERIFY COMPLETE
