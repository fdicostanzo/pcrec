# verify — altcode
STATE: done
## Verdicts

Method (all sections): helper `$V/t/one.sh VARIANT NAME PATFILE SUBJFILE [flags]` (V=$R/verify) compiles with
`build/pcrec -p rx --emit-main -o $V/{base,subj}/NAME.c [flags] --pattern "$(cat PATFILE)"` (BASE = $R/base/build/pcrec,
SUBJECT = review tree), `gcc -O2`, prints the stamps, the matcher's output line, then
`taskset -c 7 perf stat -x, -e instructions:u ./NAME "$(cat SUBJFILE)"` three times. Empty-process baseline
(`int main(){return 0;}`, same counter): 112,249 x3. Counts below are raw (baseline not subtracted unless stated).

### EMIT-1 — HOLDS (with the shape boundary stated)
Subject `$V/t/hay2029.txt` = first 2029 bytes of `$R/emit/run/hay.txt` (no match); `haym.txt` = it + ` qq ufthev zz` (match).
| case | flags | stamps (ISLANDS / MERGES) | match | instructions x3 |
|---|---|---|---|---|
| w-256 BASE | --engine=vm | 1 / 0 | nomatch | 205,064 205,064 205,066 |
| w-256 SUBJ | --engine=vm | 20 / 1 | nomatch | 12,190,011 12,190,011 12,190,009 |
| w-256 SUBJ | --engine=vm -fno-altcls-merge | 1 / 0 (program 143,470 B = BASE) | nomatch | 205,066 205,066 205,064 |
| w-256 SUBJ | --engine=vm -fno-altcls-factor | 0 / 1 | nomatch | 13,198,796 x3 (NOT restored) |
| w-256 BASE | --engine=vm -fno-alt-island | 0 / 0 | nomatch | 12,732,379 12,732,380 12,732,378 |
| w-256 BASE / SUBJ, match subject | --engine=vm | 1 / 20 | `match 2033 2039` both | 206,155 vs 12,208,552 |
| `(<w-256 list>) \1` BASE | --features all (auto -> vm "selected") | 1 / 0 | `match 2033 2046` | 272,729 272,729 272,730 |
| same SUBJ | --features all | 20 / 1 | `match 2033 2046` | 13,072,741 13,072,742 13,072,743 |
| same SUBJ | --features all -fno-altcls-merge | 1 / 0 | `match 2033 2046` | 272,729 272,729 272,730 |
| months `(Jan|...|Dec) \1` BASE, 60 KB `$R/emit/run/hay2.txt` | --features all | 1 / 0 | nomatch | 1,063,824 1,063,823 1,063,823 |
| months SUBJ | --features all | 0 / 1 | nomatch | 3,247,959 3,247,958 3,247,960 |
| months SUBJ | --features all -fno-altcls-merge | 1 / 0 | nomatch | 1,063,823 ... (restored) |
After the 112K baseline: w-256 ~93K -> ~12.08M (~130x); backref form ~160K -> ~12.96M (~80x); months ~3.4x. Answers identical in every pair.

Where M LOSES vs WINS (the TRD-2 direction re-run, same helper):
| pattern / subject | flags | BASE isl -> SUBJ isl | BASE instr | SUBJ instr | |
|---|---|---|---|---|---|
| `(?:ab|ba|aa|bb){24}c` / `abbaabba`*500+`c` | --engine=vm | 8 -> 0 (MERGES 1) | 2,931,070 2,931,068 2,931,070 | 1,737,251 1,737,251 1,737,250 | WIN 1.7x, `match 3952 4001` both |
| same / `abbaabbc`*500 | --engine=vm | 8 -> 0 | 576,263 576,264 576,264 | 326,101 326,100 326,102 | WIN, nomatch both |
| `x(?:ab|ba|aa|bb)y` / `xabzxbbq`*500+`xaay` | --engine=vm | 1 -> 0 | 173,531 x3 | 170,510 170,510 170,511 | ~neutral, `match 4000 4004` |
| `x(?:cat|cot|dog)y` / `xcaqxdoqxcoz `*400+`xdogy` | --engine=vm | 1 -> 0 (MERGES 1) | 182,736 182,735 182,735 | 250,402 250,400 250,402 | LOSS ~2x after baseline, `match 5200 5205` |
| altwide w-8, w-64 | --engine=vm | 1 -> 1, MERGES 0 | 145,106 / 191,549 | 145,107 / 191,548 | unaffected (no merge fires) |
Verdict: the shape boundary is "does M's merge eliminate the alternation". When EVERY branch folds into one class
sequence (`ab|ba|aa|bb` -> `[ab][ab]`) the island is no longer needed and M wins or is neutral. When M merges SOME
branches and an alternation remains (word lists with a single-position-differing pair, months, even 3 words
`cat|cot|dog`), the residual alternation carries a multi-member class branch, the island declines, and the VM runs the
chain: ~2x on 3 words, ~3.4x months, ~80-130x on 256 words. Lists where no pair differs in exactly one equal-width
position (w-8, w-64) do not move. `-fno-altcls-merge` restores BASE exactly (program bytes and counts);
`-fno-altcls-factor` does not. The critic's numbers reproduce to within +-3 instructions.

### EMIT-2 — HOLDS
Row order (SUBJECT src/core/compile.c, `fit_rungs[]`): :1416 `drop-landmark-walk`, :1431 `drop-islands`, :1441
`drop-anchored`, :1452 `drop-premul`, :1462 `drop-handoff`, :1472 `drop-prefilter`, :1483 `refuse`. The islands row
comment (:1426-1430) says "the first VM rung after the collapse"; `fit_seq_legal[]` (:1901-1908) adds
`{FIT_DROP_ISLANDS, FIT_DROP_HANDOFF}` and `{FIT_DROP_ISLANDS, FIT_DROP_PREFILTER}` and no reverse pair. The handoff
row's own comment (:1215-1218) orders rows "by measured cost" (handoff <=2.53x before the prefilter drop's ~4x); no cost
figure is given for the islands row, which is placed before both.
Repro: pattern `$V/t/k400.rx` = `(` + first 400 of 1000 `random.seed(11)` 8-letter words + `)\d+`, DEFAULT flags (no
`--engine`), subject hay2029 (nomatch):
- BASE: one note "dropped the VM hybrid's prefilter"; ENGINE_SEL "size-cap-retry", VM_ALT_ISLANDS 1, program 239,386 B,
  C 213,473 B; instructions 259,382 259,381 259,381.
- SUBJECT: two notes, "dropped the VM's alternation islands" then "dropped the VM hybrid's prefilter"; VM_ALT_ISLANDS 0,
  program 138,245 B, C 145,708 B; instructions 20,944,139 20,944,137 20,944,140 (~140x after the 112K baseline; the
  critic's "~80x" was raw-vs-raw: 20.9M/259K).
- SUBJECT `-fno-altcls-merge`: identical double drop, 20,944,144 ... -> the row order, not rule M (MERGES 0 here).
BASE shows the prefilter drop ALONE fits this pattern with islands kept, so the islands drop is a pure loss on it.
Note the match lines agree (nomatch both); no answer effect.

### TRD-1 / EMIT-3 — HOLDS (breadth: small utf8 alternations; default routing only via a VM-forcing construct)
Stamp grid, `$V/t/stamp.sh PATTERN -e utf8 --engine=vm` (BASE isl -> SUBJ isl; m = RX_ALTCLS_MERGES at SUBJ):
- FLIP 1 -> 0: `x(?:é|à|q2|r3)y`, `x(?:[éà]|q2|r3)y` (m 0: the lowering caller's merge, bit 10), `x(?:[éà]|qq|rr)y`,
  `x(?:[éà]|foo|bar|baz)y`, `x(?:é|à|ö|q2|r3)y`, `x(?:é|à|q2)y`, `(?:é|à|q2|r3)` (no context), `x(?:ж|й|q2|r3)y`.
- HELD 1 -> 1: `x(?:[éà]|foo|bar)y`, `(?:[éà]|cat|dog)s`, `x(?:[я]|cat|dog)y`, `x(?:é|q2|r3)y` (one member),
  `x(?:é|à|q2|r3|s4)y`, `x(?:é|à|q2|r3|s4|t5)y`, `x(?:é|à|quux|rest)y`, `x(?:éa|àa|q2|r3)y`, `x(?:€|£|q2|r3)y`.
- (`x(?:ab|ac|q2|r3)y` under utf8 also flips, but that is EMIT-1's byte-class mechanism, m=1.)
So the flip is not a rare edge: it hits a 2-to-3-member 2-byte-UTF-8 class mixed with 2-3 short literal branches, and
stops once the literal side grows (5+ branches or 4-byte literals) — consistent with a per-subtree size ratio (the knee)
rather than an absolute size; Cyrillic and Latin-1 both flip, `€|£` (3-byte vs 2-byte, different lead) did not.
Default flags: without `--engine`, `x(?:é|à|q2|r3)y` and `x(?:[éà]|foo|bar|baz)y` route to DFA (no island,
unaffected). A VM-forcing construct exposes it at default flags: `(x(?:é|à|q2|r3)y)\1 -e utf8 --features all` -> vm,
isl 1 -> 0.
Cost (`$V/t/one.sh`, `x(?:[éà]|q2|r3)y`, `-e utf8 --engine=vm`):
- subject `abcdefq1xrr2xéq`*300+`xr3y` (`u1.txt`): BASE 170,452 170,454 170,453; SUBJ 236,876 236,877 236,875;
  SUBJ `-fno-altcls-merge` 170,453 170,452 170,453 (restored, isl 1, program 2301 B = BASE). After baseline 58K -> 125K
  (2.1x). `match 4800 4804` all three.
- EMIT-3's subject `xq1 xr2 xé1 xàz xq3 `*400+`xr3y` (`u2.txt`): BASE 237,333 x3; SUBJ 456,647 456,648 456,647
  (125K -> 344K, 2.7x). `match 8800 8804` both.
TRD-1's 2.6x and EMIT-3's ~2-3x reproduce. Program bytes shrink (2301 -> 1667 B), which is why a size view reads it as
a win.

### TRD-4 — HOLDS
Patterns `$V/t/c1000.rx`, `c3000.rx` = `(?:` + N `random.seed(11)` 8-letter words + `)Z`. Helper `$V/t/cc.sh`: compile
only, `taskset -c 7 perf stat -x, -e instructions:u nice build/pcrec -p rx -o .../cc.c --engine=vm [flags] --pattern ...`, 3x.
| N | build / flags | rc | instructions x3 | outcome |
|---|---|---|---|---|
| 1000 | BASE | 1 | 257,461,789 257,460,923 257,459,122 | refused, 517,915 code bytes |
| 1000 | SUBJ | 0 | 479,156,326 479,157,610 479,158,725 | islands dropped (note), ISLANDS 0 |
| 1000 | SUBJ -fno-alt-island | 0 | 212,514,403 212,501,765 212,502,113 | direct chain |
| 3000 | BASE | 1 | 748,615,694 748,629,278 748,621,037 | refused, "1473456 bytes of emitted code" |
| 3000 | SUBJ | 1 | 1,380,835,594 1,380,777,715 1,380,837,524 | refused, "950970 bytes" |
| 3000 | SUBJ -fno-alt-island | 1 | 600,292,820 600,292,813 600,290,899 | refused, "950970 bytes" |
Rescued case 2.25x the direct deny compile; hopeless refusal 2.30x the direct deny and 1.84x BASE, and the refusal now
quotes the chain's figure (950,970) not the island's (1,473,456). K139 (known_issues.md:16) states only "Retry cost on the
witnesses: ~1.6-2x the direct `-fno-alt-island` compile" for rescued witnesses; the refused-anyway cost is not stated.
(TRD's absolute numbers differ, its pattern seed differs; the ratios agree.)

### TRD-5 — HOLDS
Code: limits.def:413 `PCREC_LIMIT(PCREC_MAX_REQ_PIECES, 10, ... "over it the description is dropped (`req_pieces`
declines `over-bound`), which is sound: the single run is derived as before. MEASURED ... peaks at 10, the
bench/altwide keyword lists whose words run 4 to 13 bytes"`; desc.c `pd_norm`: `if (m > c->max_groups) return
(PdDesc){ -1, PD_OVER, NULL };` and `pd_dropped` ("A description that reached either side's drop stays dropped").
Design (SUBJECT alt_normal_form.md:591-594): "Over the bound a subtree's groups collapse to today's common head/tail
(sound, today's answer)." Code drops, design says collapse: they disagree (the code's reading is the weaker, still sound).
Probe (`build/pcrec -p rx --emit-facts --pattern P`, SUBJ): `(?:aaaa|bbbbb|...|jjjjjjjjjjjjj)` (10 widths) ->
`req_pieces ... derived ... 4:[97]...`; add `kkkkkkkkkkkkkk` (11 widths) -> `declined ... decline:over-bound`.
(A prefix-sharing list `abcd|abcde|...` declines `not-fixed-width` at both 10 and 11: the factoring leaves an empty branch.)
Bench read-only count (python over pcrec-bench/bench/altwide/patterns, distinct word lengths per plain `(?:...)` group):
21 files sit at exactly 10 (w-64..w-2048, sh1-*, srt-*, wb-*, nar4-256/512, ci-*, cnt-64), none above; others 4/7/9.
So the bound equals the bench maximum with no headroom. Low severity today: the fact has no reader.

### CHK-2 — HOLDS (pre-existing at BASE; this diff widens it with the `KEY@F` spelling)
Pure call, no sweep: `PCREC_TMPDIR=$V python3 -I $V/t/chk2.py <tree>/scripts/emit_sweep.py` (imports the module from
file and calls `dumps_declared_delta("--list-limits", A, H, d)` with REF `A\t1 B\t2 C\t3`, HEAD `A\t1 B\t9 C\t3`):
- SUBJECT: declared {B, BOGUS} -> `[]`, map after {B: True, BOGUS: False}; declared {B} -> `[]`; declared {BOGUS}
  alone -> `["--list-limits: undeclared row moved: 'B\t2'"]`; declared {B@9 (invented), B} -> `[]`.
- BASE copy ($R/base/scripts/emit_sweep.py): the same `[]` for {B, BOGUS}.
So an invented declared row rides green beside a real one (the `declared[key] = True` mark, emit_sweep.py:1543, is never
read back); the caller (:1585) then counts every declared key, invented ones included, into `declared_moves`. The
defect predates the subject; the subject's `@SECOND-FIELD` spelling (:1533-1539) adds a new way to write an
unchecked invented key.

### CHK-8 — HOLDS (regression of this diff)
`PCREC_TMPDIR=$V nice python3 -I <tree>/scripts/m6read_check_sab_anchors.py`:
- review tree: `sabotages checked: 1117 (1158 anchor sites)` / `STALE ANCHORS: 1` /
  `S238_size_drop_unstamped.sh  src/core/compile.c  ANCHOR COUNT 6, SAB_COUNT 5`.
- $R/base: `sabotages checked: 1102 (1143 anchor sites)` / `all anchors resolve`.
Cause: S238 `SAB_COUNT=5`, `SAB_BEFORE='      .cells = { { ESEL_SIZE_CAP_RETRY, ESEL_SIZE_CAP_RETRY }, PFLW_PASS, NULL },'`;
`grep -cF` of that line: BASE compile.c 5, SUBJECT 6 (the new `drop-islands` row, compile.c:1435). Read-only confirmed:
the script reads files and sources each sabotage row in `bash -c` to print its variables (script lines 50-56);
`git -C <review tree> status --porcelain` empty before and after.

### CON-1 (= SLOT-1) — HOLDS
SUBJECT docs/spec/match_api.md:210-215:
`#if defined(PCREC_RX_ABI_H) && (PCREC_RX_ABI_H + 0) != 95` /
`#error "pcrec: this artifact (abi 96) shares a translation unit with an artifact of a different abi; regenerate both with one pcrec"` /
`#endif` / `#ifndef PCREC_RX_ABI_H` / `#define PCREC_RX_ABI_H 95`.
Emitted header (`build/pcrec -p rx -o $V/subj/abi.c --pattern abc`, abi.h:8, :12): `!= 96`, `#define PCREC_RX_ABI_H 96`.
Two of the three readers in the spec block still say 95.

### TRD-2 (changelog sentence) — HOLDS
docs/dev/history/abi_changelog.md:25-41 (the 96 entry) ends "Every other artifact, every `byte` artifact included,
moves only the number. No answer moves." The entry is stage-1 only (`git log BASE..SUBJECT -- abi_changelog.md`: one
commit, f1c64f11a "altbuild stage 1: abi 95 -> 96 ..."), and names no 2b or K139 movement. Byte artifacts measured
moving above, same abi: w-256 `--engine=vm` (program 143,470 -> 109,751 B, islands 1 -> 20), `(?:ab|ba|aa|bb){24}c`
`--engine=vm` (program 15,239 -> 957 B, islands 8 -> 0), `x(?:cat|cot|dog)y`, and the K139 default-route
`(400 words)\d+` (EMIT-2: a new drop note and islands 1 -> 0). The "No answer moves" half held on every pair run here.

### TRD-3 — HOLDS
tuning.md:771 [2.33¶7] still ends "`make test-axes` records the refusal as this axis's documented limit." The diff of
tests/axes/run_axes.sh deletes `["-fno-cls-kit"]="bytes of emitted code (limit"` and `["-fno-cls-kit"]=60`; the
replacement comment (:605-616) says the entry "and its K35 floor are DELETED" and that "`-fno-cls-kit -fno-altcls-merge`
restores the boxes and the refusals". One-pattern re-check (SUBJ, `-e utf8 --engine=vm -fno-cls-kit --pattern
'\P{Unknown}'`): rc 0 (225,747 code bytes); adding `-fno-altcls-merge`: rc 1 "pattern too large: 556360 bytes of
emitted code (limit 500000)". So the claim is true, but grep of tests/ for the pair finds only the run_axes.sh:616
comment: nothing exercises it, and the spec sentence describes a record that no longer exists.

### SLOT-2 — HOLDS (by reading)
- altnf.c:474 `static int anf_flatten(Ctx *cx, const Ast *a, Ast ***out)` (via `PCREC_SPINE_EACH`) vs altcls.c:52
  `static size_t altcls_cat_flatten(Ctx *cx, Ast *a, Ast ***out)` (hand loop): same left-to-right CAT spine array.
- altnf.c:486 `anf_cat` "A left-nested `A_CAT` spine of `arr[0..n)`, p_cat's shape; EMPTY at 0" vs altcls.c:69
  `altcls_rebuild_cat` "n == 0 -> A_EMPTY": same body (int vs size_t index).
- altnf.c:500 `anf_alt` vs altcls.c:84 `altcls_rebuild_alt`: same body.
- altnf.c:444 `anf_rebuild` = the same left-nested CAT loop over `b->pos[0..w)` (no EMPTY arm) — a same-file twin of anf_cat.
- lower_enc.c:380-386 (`Ast *res = bl.br[0]; for (...) { Ast *alt = pcrec_ast_node(lc->cx, A_ALT); ...`) and
  emit_vm.c:4105-4111 (`Ast *split = box[0]; for (...) { Ast *alt = pcrec_ast_node(v->cx, A_ALT); ...`): inline copies of
  the ALT builder. Both altcls helpers remain in use (altcls.c:144, :153, :161). Accurate.

### SLOT-3 — HOLDS (by reading)
altcls.c:96 section header `/* ---- stage 1 + dispatch ---- */`; :179-186 A_BREF "Stage 1 merges an alternation run of
single-BYTE branches into one class ... Stage 2 factors a shared literal PREFIX"; :198-207 A_KRESET "Stage 2 peels a
shared leading literal, and `altcls_branch_peel` requires the flattened branch's FIRST element to be an A_CLASS ...
Neither stage can move a `\K` across a byte"; :213-218 A_LOOK and :226-231 A_CALL argue from "Stage 1"/"Stage 2";
:271 A_ATOMIC "Both stages here rewrite an ALTERNATION". `grep altcls_branch_peel` over src/opt, cpset.c, emit_vm.c:
the only hit is that comment (altcls.c:200) — the function no longer exists. cpset.c:335-338 "the interval form of the
`altcls_single_bit` popcount the two callers used to write out (`src/opt/altcls.c`'s peelable-branch test, `src/gen/
emit_vm.c`'s island literal)"; emit_vm.c:4019 "`pcrec_cls_single` with `src/opt/altcls.c`'s peelable-branch test".
The quotes are accurate; the critic's further claim that rule M now moves a branch past a `\K` branch was not
re-verified here (not verified: semantic, no probe run).

### SLOT-4 — HOLDS (by reading)
lower_enc.c:343-345 `lower_class_utf8`: `for (int i = 0; i < a->u.cls.n; i++) u8_ranges(&bl, a->u.cls.iv[i].lo,
a->u.cls.iv[i].hi);` vs :441-445 `split_utf8`: `for (int i = 0; i < n; i++) u8_ranges(bl, iv[i].lo, iv[i].hi);` —
the same loop twice; `split_utf8` is reached only through `pcrec_lower_boxes` (:486-491, `ops_for(cx)->split`), whose
header says "The splitter is this file's own, never a copy". :429-430 `split_byte`: "Unreached today: no `A_WCLASS`
exists under `byte`." — a table cell (`lower_ops[]` :450) with plausible but unreached behaviour. Accurate.

### SLOT-6 — HOLDS (by reading; consequence not measured)
altnf.c:686 `AnfRun r = { cx, rules, { &anf_pd_cls, 0, PCREC_MAX_REQ_RUN_SCAN }, 0, 0, st };` — the third PdCfg field is
`max_pos` (desc.h:32-38 "at most `max_pos` positions stored per group"). limits.def:409 `PCREC_MAX_REQ_RUN_SCAN, 32,
"bytes"`, described only as "how much of a necessary literal run the ANALYSIS tracks ... (src/opt/reqbyte.c's
RbRun)"; the row's text names no altnf reader (0 hits for "altnf"). So the owner reads a bytes-unit req-run bound as its
position bound at its own level. The "retuning silently changes merges/artifacts" consequence was not probed (needs a
rebuild); the reader omission itself is accurate.

## Summary
HOLDS: EMIT-1 (with boundary: M loses whenever it merges some branches and an alternation remains; wins/neutral when it
folds the whole alternation into a class sequence), EMIT-2, TRD-1/EMIT-3, TRD-4, TRD-5, CHK-2 (pre-existing at BASE),
CHK-8, CON-1, TRD-2 sentence, TRD-3, SLOT-2, SLOT-3, SLOT-4, SLOT-6. REFUTED: none. Not verified: SLOT-3's `\K`-move
side claim, SLOT-6's retuning consequence. No answer difference in any measured pair.
Compiles spent: about 75 (pairs counted 2), plus 18 perf'd compiles for TRD-4.

VERIFY COMPLETE
