# VERIFY — covcap-r3

## Items

### V-1 — HOLDS (FI-1, RD-2, SND-2)
Commands: `kit/kp.sh P` on each pattern (byte and utf8 identical; first KITPROOF line):
- `a{4094}`, `a{4095}`, `[ab]{4095}`: `fixed-width k=0` (C4 passed, fail at C7 = KN_CAP-1 term at stage 1); `span_facts 0`.
- `a{4096}`, `a{4097}`, `[ab]{4096}`: `anchored-A k=0` (C4), `span_facts 0`, both byte and utf8.
- Extra: `a{2000}b{2090}` (4091 states) `fixed-width`; `a{3000}b{3000}` (6001 states) `anchored-A`; so the ceiling is on the PRE-scan-edge state count.
Code: `src/core/limits.def:186` `PCREC_LIMIT(PCREC_ANCHORED_MAX_STATES, 4096, ...)`; `src/core/compile.c:~400-403` `pcrec_build_min_dfa(..., PCREC_ANCHORED_MAX_STATES, ...)`, `if (cx->job->adfa.overflowed) return; /* stays anchored_ok == false */`; `known.c cc_anchored`: `if (!job->anchored_ok || job->adfa.n <= 0) return false`.
Consequence: any walk (C4 passed) is on an anchored machine of <= 4096 pre-pass states, so depth <= 4095 < 4096; design outcome 4 / `a{4097}` `4096:...` / plant (e) cannot be reached via stage-1 anchored machine (only if stage 2 changes the machine ceiling). Scan-edge virtual states (KnVs{s,c}, c < scan_span) each stand for a deleted pre-pass chain state, and a{2000}b{2090}/a{3000}b{3000} show the ceiling counts them, so virtual depth cannot exceed the pre-pass count (empirical; I did not read scanedge.c deeper).

### V-2 — HOLDS (SND-1, FI-7) on the cost numbers; allocation arithmetic is my reading
`python3 -I soundness/walkcost.py` (read first; it applies the rule over the -fno-scan-edge machine, not kn_walk):
- `[ab]*a[ab]{8}-{300}`: states 812, k=309, L=9, row-visits 198961, max rows/depth 811, x256 = 50,934,016 byte steps (py 2.9s).
- `(?:a|bb){150}x`: states 302, k=151, L=1, row-visits 11476, max 151 rows/depth, 2,937,856 byte steps.
Today (`kit/kp.sh`): both `fixed-width k=0` (C7 fails because k > KN_CAP-1=31; `src/gen/known.c:34 #define KN_CAP MF_MAX_SPAN_POS`); span_facts 0. Today's compile, `/usr/bin/time -v build/pcrec -p rx --features all --emit-main`: first 0:00.03 wall, max RSS 24304 kB; second 0:00.20, 63844 kB (today the walk stops at depth 32, so these do not include rev 3's walk).
Reading, known.c:~120-167 `kn_walk`: `cap = d->n*4+8`; `for j<=KN_CAP: lv[j] = arena_alloc(sizeof(KnVs)*cap)` allocated for EVERY depth up front, 256 `kn_step` per row, linear dedup `for x<nlv[j+1]` per live successor. With KN_CAP raised to 4096 and n=812: 3256*8 B = ~26 kB x 4097 = ~107 MB arena before any row is visited (n=4095: ~131 kB x 4097 = ~537 MB). So the cost concern holds on both counts (steps and up-front allocation); wall time of the rev-3 walk itself not measured (no prototype).

### V-3 — HOLDS (SND-3, SND-4, RD-3 reader claim)
`stated` reader (x0.py:835-866) format: `FLAGS<TAB>PATTERN<TAB>EXACT_LEN<TAB>S_0;S_1;...<TAB>label` (sets = comma-separated hex bytes). File verify/stated.tsv; ran `PCREC=<review>/build/pcrec X0PCRE=kit/x0pcre python3 -I docs/design/kit_proof/x0/x0.py stated verify/stated.tsv`:
```
## stated sets against 10.46 2025-08-27
r1  - ab|ac{10}  exact_len=2  RED  {"kind":"exact","d":1,"pcre":[98],"stated":[98,99]}
r2  - a{30}(?:b{30}c|d) exact_len=31 RED  {"kind":"exact","d":30,"node":"61..(30)","pcre":[100],"stated":[98,100]}
ctl - ab|abc|ad  exact_len=2  green
```
(r1 row = `61;62,63`; r2 row = 30 x `61` then `62,64`.) So true values read RED on exact for the two critic rows, control green. RD-3: `grep -c SPANSET x0.py` = 0; `z2/z2.py:76 elif f[0] == "SPANSET":` (also :11,:17) — the SPANSET reader is z2.py, not x0.py (x0.py `stated` reads a TSV). Whether the RED is due solely to horizon = len(S) (SND-4) is as the critic says; r2's witness for `b` is 61 bytes, consistent with the RED node at d=30.

### V-4 — PARTLY (FI-2, RD-5 field widths)
Quoted, `src/gen/known.h:23-31`: `typedef struct { uint8_t k; /* the fixed width; 0 = no fixed end */ uint8_t ctx_before[32]; ... uint8_t set[MF_MAX_SPAN_POS][32]; int x; int r0; } MkEnd;` with `memfn.h:277 #define MF_MAX_TERM 32`, `:302 MF_MAX_SPAN_POS MF_MAX_TERM` (so set is 32x32 = 1 KB, k is one byte: both too narrow for 4096). `PcrecCover` (known.h:~55-65) = `{ const char *why; MkEnd end; const MkLang *lang; MkKnown known; mf_class cls; key_ok,key_st,key_n,key_fin }`; it embeds `MkEnd` by value, holds no sets besides `end.set`, and `lang` is a POINTER to the facts-side `MkLang` (`facts.h:305-306 uint8_t exact_len; uint8_t set[PCREC_PREFIX_K_MAX][32]`).
`cc_exact` (known.c:~253-275): `cv->lang = pcrec_fact_span_stated(cx)` is assigned BEFORE the checks; `end.k = (uint8_t)k; memcpy(end.set, w.set, ...)` are the LAST two statements, reached only on success. `pcrec_cover` allocs via `pcrec_arena_alloc` ("zeroed" per internal.h:334).
So on a decline the memo has end.k = 0 and end.set zero, but NOT the KITPROOF print as proof: known.c:430 prints `cv->why ? 0 : cv->end.k` (k forced to 0 on declines by the print itself, so "KITPROOF prints k=0" does not show the memo's content). The memo's decline state: k/set zero by arena zeroing, `lang` pointer set once C8 was reached, `end.x/r0/ctx_before/absent_before` possibly filled by C6 (cc_entry writes them before C7 can fail). Claim "memo carries no k/exact_len/sets on a decline" HOLDS for k and set, PARTLY for the other end fields.

### V-5 — HOLDS (FI-3, RD-5 unasked)
`kit/kp.sh` (byte and utf8 identical): `ab$` (route rev-end, span_facts `2:97,98`), `abc\z` (rev-end, `3:97,98,99`), `^ab` (attempt, span_facts empty), `x[0-9]{30}\z` (rev-end, `24:120,[10],...`): NO KITPROOF line printed (the cover decision never asked: C1 route is not reached, pcrec_cover not called). `hello`: `KITPROOF cover k=5`, route "cover", `5:104,101,108,108,111`. So the 4 print no record, 1 does.
Callers of `pcrec_cover(` in src/cli/lib/tests (grep): src/gen/emit_dfa.c:4898 (`return pcrec_cover(s->cx)->why == NULL;`), :14477, :16315 (decl at known.h:70, def known.c:401). All in emit_dfa.c (listing/facts code does not call it).

### V-6 — HOLDS (FI-4)
Quoted `src/facts/facts.c:379-397` (inside `case PF_SPAN:`, `#ifdef PCREC_CAND_TRACE`): `why = pcrec_span_walk(cx, &cx->job->nfa, &pf->span);` then "The ONE-WALK control (ctx_span.md §3.8): the slice narrows the hull, never widens it", `pcrec_kset_walk(cx, &cx->job->nfa, &hull); for (d < pf->span.exact_len && d < hull.nwalk) ... if (span.set[d] has b && !hull.k[d].set[b]) pcrec_ctx_fail(cx, 0, "internal error: the span slice states byte 0x%02x at offset %d, outside the k-set walk's hull there ...")`. The same block (facts.c:~400-410) prints `SPANSET\t%d\t` (X0's input).
It lives inside the `PF_SPAN` case calling `pcrec_span_walk`/reading `pf->span` (MkLang) — all of which the design deletes (§3.1 WHAT IT DELETES, design line 232-236: "pcrec_span_walk ... MkLang ... the span_facts row ... accessor ... and the trace build's SPANSET record (facts.c)"). The design names SPANSET but not this hull control (grep of design for "ONE-WALK|one-walk|hull.*contain" matched nothing relevant); so the control is deleted with it and not listed as lost.

### V-7 — HOLDS (FI-5, RD-8)
`scripts/emit_sweep.py` `facts_declared_delta` (docstring ~1259 and body to ~1300): moves are `FACT:COLUMN:FROM>TO` (cell moves, `FACTS_COLUMNS`) or `FACT:row:>new` (a NEW fact: "REF has no row of it, NEW has exactly one per encoding REF lists", i.e. a new row of a fact, byte/utf8 only). Docstring: "an added or removed line ... is a problem"; code: `if len(al) != len(bl): return problems + ["line count %d -> %d" ...], 0` after only new-fact rows are filtered out; "Comment and section lines must be identical" (`if x.startswith("#") ...: if x != y: problems.append("comment line moved")`). So: it cannot express a removed fact row (span_facts) (line-count mismatch) and cannot express a new section / new comment lines (any comment/section change is a problem). Note there is no `FACT:row:>gone` form in `parse_fact_moves` (only `row:>new`).

### V-8 — HOLDS (FI-6, RD-4)
`docs/spec/cli.md` [2.6¶1]: "...one row per limit: `name`, `value`, `unit`, `kind` (`compile budget`, `runtime capacity`, `size cap`, `selection knee`, `identifier cap`), `override` ...". `src/dump/limits_dump.c:~93-100` header prints the same closed list ("kind: \"compile budget\" ... | \"runtime capacity\" ... | \"size cap\" ... | \"selection knee\" ... | \"identifier cap\""); `src/core/limits.def:48-54` the same definition. Design (git show 6630261a7) line 228: "one `limits.def` row, kind \"safety limit\"" and lines 384/390: "`cli.md`: none for the limit (§2.6 is generic) ... names no row: no hunk". "safety limit" is not one of the five kinds, so §2.6¶1 names a closed list the design would extend with no spec hunk (or must use an existing kind).

### V-9 — HOLDS on today's facts and on the rule's exclusion; the stage-1 mover claim is by rule application (no prototype)
`kit/kp.sh` + `build/pcrec -p rx --features all --emit-facts=byte` `width` row:
- `a{32}|a{32}b`: `KITPROOF fixed-width k=0`; width `[32,33]`; span_facts `24:97...` (24 sets).
- `x{31}(?:y|yz)`: `fixed-width`; width `[32,33]`; span_facts `24:120...`.
- `a{24}|a{24}b` (control): `KITPROOF cover k=24`; width `[24,25]`.
`kit/machine.py`: first two both `span=32 exact=32 cex=None`. Design §5.2 (lines 417-418): "`exact/producer-short`, or `fixed-width` with `width` `[w,w]`, `25 <= w <= 32` at stage 1". Their width is `[32,33]` (not `[w,w]`), their `why` is `fixed-width`, so the rule does NOT include them; and since they are today's `k=32 > KN_CAP-1` declines at C7 whose machine reads span 32/exact 32 (single-entry, the C10 shape of the cover twin `a{24}|a{24}b`), they would pass C7 at stage 1 (no KN_CAP term) and plausibly move into the cover unpredicted. I did not run the C9-C15 conjuncts for them, so "become covers" is an application of the rule, not an observation. Also confirmed: width's upper bound != k for these, so "k is read from the width fact" is not the right source for them.

### V-10 — not verified / no counter-example found (RD-1, SUSPECTED)
Read first: `src/core/internal.h:2475-2501` (`Nfa.erased`, NFA_ERASED_LOOK/ATOMIC/COUNT/CALLOUT; `island` at :2484-2488); `src/ir/nfa.c:622-640` `frag_row` records `erased` for lookaround/callout kinds, `:888-894` count erasure only `if (b->collapse ...)` (the prefilter lowering), `:1013` atomic; `src/facts/kset.c:858-861` `pcrec_span_walk` declines on `nfa->erased`, `nfa->island`, accept with `dist`.
Ran the TRACE compiler (`PCREC_KIT_PROOF_TRACE=1 ... -e byte|utf8 --emit-main`, last KITPROOF record) on 48 shapes (lookahead/lookbehind pos/neg, atomic groups, counted repeats, \K, callouts, verbs, UCP/\p{..} classes, \B \b, conditionals, backrefs, \X, \R, branch reset), files verify/shapes.txt/.out and shapes2.out. 72 KITPROOF records printed (the rest are refused/out-of-scope constructs with no record: callouts, verbs, backref, \X, \R, conditionals, ACCEPT). Distribution of `why`: cover 30, finisher-dfa 24, end-at-k 11, exact/machine-inexact 4, anchored-A 3, `exact/producer-unstated` 0.
Notably `ab(?=c)`, `a(?<=a)b`, `a\Bb`, `a(?!x)b` are covers today with span_facts stated (`2:97,98`), i.e. the slice does not see an erased NFA for them. So in ~48 shapes no compile has `producer-unstated` at all: RD-1 not demonstrated; the guards look subsumed by C1/C4/C5 or by `erased` being set on a different NFA than the one the slice walks (I did not trace that build path). Did not need the libpcre2 language comparison (no candidate). Count: 0 of 72.

### V-11 — PARTLY (RD-3 spot checks)
- `docs/design/memfn/span_runs_sheet.md` and `docs/design/patfacts/inventory.md` both exist; `grep -c 'span_facts\|KN_CAP\|PCREC_SPAN_WALK_SUBSETS\|MkLang'` = 0 and 0 on them. So neither mentions those names (they are not readers; if RD-3 listed them, REFUTED for those two files; the critic's own list at readiness.md:23 does not name them).
- `src/facts/facts_derive.h:208: PfWhyCode pcrec_span_walk(Ctx *cx, const Nfa *nfa, MkLang *o);` — declared there: HOLDS.
- `src/core/limits.def:393 PCREC_LIMIT(PCREC_SPAN_WALK_SUBSETS, 512, "count", "compile budget", NONE, "", "...", INTERNAL_H)` (section "home: INTERNAL_H (10) — src/core/internal.h's own compile-side caps", :390): X-macro home is INTERNAL_H — HOLDS.

### V-12 — HOLDS (RD-6)
Design §5.3 `facts` rows (design lines 434-439): `a{40}(?:b|cc)`, `a[xy]c|b[xy]d`, `a{30}(?:b{30}c|d)`, `a{4097}`, `ab|abc|ad`, `a*?a`, `(?:\bab|\Bac\z)` — no `a(?:b|c\z\W)`; it appears only in §5.4 plant (c) (design line 454). `grep -c 'a(?:b|c' tests/kitproof/cases.tsv` = 0; `grep -F 'c\z\W' tests/kitproof/cases.tsv` prints nothing (lines 33-38 shown above are the existing 6 facts rows).

### V-13 — HOLDS on the anchors; "the design rewrites cc_eol/set" per the design's §3.1 text (RD-7)
Anchors quoted (`tests/mech/sabotages/`):
- S1139_cover_c9_dropped.sh: `SAB_BEFORE='static bool cc_eol(CoverSt *st)\n{\n    for (int j = 0; j <= st->w.k; j++)'`.
- S1136_cover_c9_depth_k_only.sh: `SAB_BEFORE='    for (int j = 0; j <= st->w.k; j++)\n        for (int i = 0; i < st->w.nlv[j]; i++) {\n            int e = st->d->st[st->w.lv[j][i].s].eolvar;'` (depends on `w.nlv[j]`/`w.lv[j][i]` retained rows at every depth).
- S1131_cover_c8_skipped.sh: `SAB_AFTER` text contains `memcpy(st->cv->end.set, st->w.set, sizeof st->cv->end.set)` (a `w.set` copy into `end.set`); BEFORE anchors `int k = st->w.k;\n if (!st->w.exact) { ...machine-inexact }`.
Design: lines 458-459 name S1131 (keeps witness `ac|bd`) and S1149 (retires with the slice) but not S1136/S1139. §3.1 MEMORY text (design "two row arrays ... C9 checked as the walk passes each depth instead of from retained rows") — grep output above for the exact lines. So S1136/S1139's retained-rows anchor text disappears under that design: HOLDS (reading). S1149: `tests/ci/cloud_mech_shards.tsv:1047: S1149 73 15.5 runner measured` and `tests/ci/measured_mech.tsv:129: S1149 31.0 3 18.0 35.0 measured` — both still list it (HOLDS, grep).

### V-14 — HOLDS (SND-6), as a reading claim (nothing built with C15 removed)
`src/gen/known.c:455-482` `cover_window`: `pcrec_memfn_wspan(&sp[0], 0, e->k, MF_VERIFY_YES); for (int d = 0; d < e->k; d++) pcrec_memfn_wpos_bits(&sp[0], d, e->set[d]);` ... and only at the end `pcrec_memfn_window_stated(cx, s, a, 1, MF_WFLOOR_SUBJECT);`. `src/gen/memfn_sites.c:559-562` `pcrec_memfn_wpos_bits(mf_wspan *w, int j, const uint8_t bits[32]) { memcpy(w->set[j], bits, 32); }` — no bound check. `window_bounds_check` (:578-598, `w->len < 1 || w->len > MF_WSPAN_POS ...` -> `pcrec_ctx_fail`) is called only from `pcrec_memfn_window_stated` (:603) and `pcrec_memfn_part_window_stated` (:612), i.e. after the positions were written. `memfn.h:~682 uint8_t set[MF_WSPAN_POS][32]; uint32_t table_ref[MF_WSPAN_POS];` with `:653 MF_WSPAN_POS = MF_MAX_SPAN_POS = MF_MAX_TERM = 32`. So with k > 32 reaching cover_window, positions >= 32 write 32 bytes each past `set[]` (first into table_ref, then beyond the span) before the check; today k <= KN_CAP-1 = 31 prevents it. Also `MkEnd.set` is `[MF_MAX_SPAN_POS][32]` (known.h:27) so cc_exact's `memcpy(end.set, w.set, sizeof end.set)` is bounded by the destination size, not k.

VERIFY COMPLETE
