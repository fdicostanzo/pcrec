# l3feat report (span_arms L3, the FEATURE; lanes l3feat then l3feat2)

## Summary
L3 BACK is built on lane/l3feat: a required run may begin inside a positive lookbehind (`(?<=foo)bar` states
`foobar` at K -3). The first lane (l3feat) built the src half and stopped: the forward scan's `handoff`
re-entry answered wrong at K < 0 (W-L17). The second lane (l3feat2) applied ruling R-1. The forward-scan
`handoff` row is now DECLINED at K < 0 (a declared row condition, `req_k_reentry_sound`). The entry move and
the VM attempt loop's re-entry are unchanged. The lane also added the witnesses on both routes, the listing
cells, W-S4c and sabotages S3405-S3413, re-aimed six rows, bumped abi 109 -> 110, and wrote the spec hunks,
the span_arms REV 3.3 addendum and the L2 note.

Two-sided compare against the census: 119 observed movers against 57 predicted. 56 of the 57 predictions
moved; the one that did not is a sound under-approximation. All 63 extra movers fall outside the census
model's scope. No non-lookbehind text moved; every non-mover's `.c` is byte-identical apart from the abi
number. The plants: 13 of the 15 rows run are DETECTED (S3411 as a compile catch). S3407 is UNDETECTED by
measurement, because its clamp is redundant today; its row says why. R-2 (the owner's question) is answered by
measurement under "Forward-scan decline at K<0". At entry, every pattern with a K < 0 run still searches with
its lookbehind bytes (104 of 104). Only the re-entry falls back to the start byte. The cloud test run and two
box jobs are dispatched. The cloud axes run is NOT dispatched (cloudrun's push timeout; see Validation). One new
finding for the manager: 9 patterns had the forward-scan handoff at base, with K 0 or 1. They
now have K < 0, so the decline takes the handoff away from them (their answers do not change). See
"Identity and movers" and the proposed filing.

PREMISE TEST (brief). (1) With the decline, `build/pcrec` gives (6,9) on "foobar12x" and (7,9) on
"xfoobar9xfoobarx". Without it (`$PCREC_TMPDIR/scratch/l3feat/pcrec.feat`, the f7b9a25da build) the answers
are NOMATCH and (15,16). Command: `PCREC=<bin> bash tests/harness/run.sh $PCREC_TMPDIR/scratch/l3feat/prem/p.rxt`
(two cells, `ms 0 "foobar12x" 6 9`, `ms 0 "xfoobar9xfoobarx" 7 9`): "cases passed: 2" against "cases failed:
2" with exactly those two answers. (2) `grep -n "define PCREC_ARTIFACT_ABI" src/gen/emit_dfa.c` printed `55:#define
PCREC_ARTIFACT_ABI 109` before the bump.

## Census check
The census is `docs/dev/lanes/l3cen_report.md`: 57 movers (55 corpus, 2 bench) over 7,613 rows / 5,932 texts.
The observed side comes from `docs/dev/lanes/l3feat_evidence/cmp_l3.py`, run as `python3 -I cmp_l3.py
<clean base build>/pcrec <clean tip build>/pcrec <base tree> docs/dev/lanes/sae1_evidence/bench_patterns.txt
<out> --jobs 12`. It reads the same population (`census_l1.population`, 7,613 rows: 7,224 corpus, 389 bench;
5,932 distinct texts). It compares the facts `req_whole_run`, `req_landmark_maxoff`, `req_byte` and
`run_pin`, plus the stamps `REQ_WHY/HANDOFF/RUN/BYTE`, `DFA_SCAN`, `DFA_PREFILTER` and `VM_PREFILTER` on both
routes. The rows are in `l3feat_evidence/ident_movers.tsv`.
- Predicted and observed: 56. 54 have the census's run exactly. On the other two, `(?<=(?:a|bc)d)x` and
  `(?<=((a|bc)d))x`, the census predicted `dx` and the build states `[ab]dx` at -2, a strictly more
  informative run. The census did not model the union term.
- Predicted, not observed: 1, `(?<=(?<=a)b)c` (census `abc` at -2). The walk does not read a lookbehind
  nested inside a lookbehind into `lg`, so the run stays none. This is sound, an under-approximation.
- Observed, not predicted: 63 (`l3feat_evidence/observed_not_predicted.tsv`), every one outside the census
  model's scope:
  - 40 use another lookbehind spelling (`(?<*`, `(*plb:`, `(*positive_lookbehind:`, `(*naplb:`, ...). The census
    selected only texts containing `(?<=`.
  - 9 have an alternation inside the lookbehind or at the root. The census lists these as ALTROOT, outside
    its model.
  - 2 have a backreference. The census abstains on them.
  - 12 hit other limits of the model:
    - a quantified or atomic or grouped lookbehind: `(?<=a)+b`, `((?<=a)b)+`, `(?<=(?:ab){2})x`;
    - a lookahead nested in a lookbehind: `(?<=a(?=b))ab`;
    - a lookbehind longer than 32: `(?<=a{65535})x` and `(?<=(?:a{1000}){65})x`, run `a^32` at -32 with an
      empty extent;
    - a lookbehind after consumed text: `z(?<=abc)` and `y(?<=abc)z`;
    - a caseless tail: `(?<=ab)(?i:cdef)`;
    - the census's own information tie (b): `(?<=qz)x?a:`, `qz` at -2;
    - a run-choice flip: `(?<=xyz)a+xyz`, `xyza` unbounded -> `xyza` at -3 (`req_byte` 122 -> 97);
    - W-D2 `(?<=ab)(?<=cb)c`, still `dead`, now with BACK's `bc` at -1 (the census put never rows outside;
      D-4's BACK row has no never conjunct; any run is sound for a pattern that never matches).
- Bench: both predicted bench movers moved as the census said (below, "Identity and movers").
- Census note (c) is confirmed: `(?<=a)\Kb` and `(?<=\Ga)b` move (run `ab` at -1). Both are answer witnesses
  in spanarms.rxt.

## Feature commits
On main 694d91dc4, branch lane/l3feat:
- bff1a3d89 (l3feat) the BACK row (`rb_top_back`, `lb_bytes` from `pcrec_lb_max` x
  `PcrecEnc.max_char_bytes`), the consumed extent (`ReqRun.cons_lo/cons_hi`, `pcrec_run_cons`),
  `pcrec_run_omin` on the run span, the signed move (`emit_req_move_open`'s K < 0 row with the end clamp), the
  entry guard `k != 0 || round.len > 0`, the per-sign re-ask, the K < 0 comments, CONFORM-1 and the facts.h
  DOC half, and the hybrid prefilter's first ask (a deviation, below).
- 9095c489b, f7b9a25da (l3feat): the run_prechecks K < 0 arms ([5.12a] lookbehind hand pins, [5.12b], [3.1b],
  [5.12l]), vmhat_checks' signed handoff, and W-T3 in presence_deny.rxt.
- 04d64ee85 (l3feat2): R-1, the decline.
- 956cb54d5 (l3feat2): the witness blocks, facts-look cells, W-S4c, sabotages S3405-S3413, five anchors
  re-aimed and S1887's reach re-aimed.
- ba8b5b880 (l3feat2): abi 109 -> 110, the spec hunks, the span_arms addendum and L2 note, and
  gen_presence_deny's temp root.
- 84bdcdb92 (l3feat2): tests/litscan/CLAUDE.md.
- The report commit (this file, the evidence, the history index line).

## Forward-scan decline at K<0
`src/gen/emit_dfa.c` `pf_handoff_applies` (the prefilter table's `handoff-reentry` row) gains
`if (!req_k_reentry_sound(k)) return false;`. `req_k_reentry_sound(PfBound k)` returns false exactly when K
is bounded and negative, and its header carries the reason. It is one declared condition of the row's
predicate, read on the same K the admission prices (`req_landmark_k`), not a new `if` tree elsewhere.
- The witness, before and after: see Summary, the premise test.
- Counts, run with `tests/harness/run.sh` over the generated witness file
  (`$PCREC_TMPDIR/scratch/l3feat/wit2.rxt`, from `l3feat_evidence/gen_wit2.py`; the l3feat witness set plus
  bench 258, `\K`, `\G`, `(?<=foo)bar(?=baz)`, W-D2 and the K -10 row):
  - with the decline (`build/pcrec`): 1,646 passed, 0 failed;
  - without it (`pcrec.feat`): 1,631 passed, 15 failed, all `(?<=foobar)\d*x`;
  - at base (`pcrec.base`): 1,646 passed.
  The first lane's own count on its 1,232-cell file was 1,232 / 15 (`wit.log`, `wit2.log` in that scratch
  dir).
- The ENTRY move and the VM attempt loop's re-entry stay. `(?<=foobar)\d*x` reads `RX_DFA_PREFILTER "memchr"`
  with `RX_REQ_HANDOFF "-6"` (`build/pcrec --features all -p rx -o o.c --pattern '(?<=foobar)\d*x'`).
- R-2 (the owner's question: does the decline throw away the point of L3, lookbehind bytes in the search?).
  MEASURED, not argued. Command: `PCREC_TMPDIR=/var/tmp/pcrec-pcrec python3 -I
  docs/dev/lanes/l3feat_evidence/r2_measure.py l3feat_evidence/pats.txt OUT.tsv <BASE build> <L3 without the
  decline, f7b9a25da> <L3 with it, ba8b5b880>`. It reads each default-route artifact (`--features all -p rx`):
  - `DFA_PREFILTER`;
  - what `rx_prefilter` searches (the run finder `rx_reqrun`, or its `memchr` byte);
  - whether `rx_search_run` asks the run finder once before the first attempt (the ENTRY move);
  - the run finder's `memchr` byte and its run position (`REQ_RUN`'s `@idx`);
  - the bytes it verifies.
  A run position is a LOOKBEHIND byte iff K < 0 and it lies below -K. The rows are in
  `l3feat_evidence/r2_three_builds.tsv`: 120 patterns (W-L17 plus the 119 movers) x 3 builds.

  | pattern | build | DFA_PREFILTER | prefilter searches | entry ask (run finder: scan byte; verifies) |
  |---|---|---|---|---|
  | `(?<=foobar)\d*x` | BASE | memchr | `x`, match start | none (no run) |
  | | L3, no decline | handoff | run finder: `b` @3 LOOKBEHIND | yes: `b` @3 LOOKBEHIND; `foob`+`obar` |
  | | L3, decline | memchr | `x`, match start | yes: `b` @3 LOOKBEHIND; `foob`+`obar` |
  | bench 258 `(?<=item )done` | BASE | offset-set | its offset set (no run) | yes: `d` @0 consumed; `done` |
  | | L3, no decline | offset-set | the same | yes: `m` @3 LOOKBEHIND; `item don` (5 lookbehind bytes) |
  | | L3, decline | offset-set | the same | yes: `m` @3 LOOKBEHIND; `item don` |
  | bench 333 `(?<=\xc3\xa9)x` | BASE | memchr | `x`, match start | none (no run) |
  | | L3, no decline | handoff | run finder: `\xa9` @1 LOOKBEHIND | yes: `\xa9` @1 LOOKBEHIND |
  | | L3, decline | memchr | `x`, match start | yes: `\xa9` @1 LOOKBEHIND |

  - Over all 120 patterns at L3 with the decline: 104 ask the run finder at entry, and all 104 verify
    lookbehind bytes there. 18 of them SCAN for a lookbehind byte. The other 86 scan for a consumed byte and
    verify the lookbehind around it. The other 16 have no entry ask. All 16 are `DFA_SCAN "cover"` artifacts: they have no prefilter, and their run is stated but `REQ_WHY "dominated"` (checked for each pattern with `grep RX_DFA_SCAN`/`RX_REQ_WHY` on the tip build). The decline cannot touch them.
  - The decline changes `DFA_PREFILTER` on 84 of the 120. In every one, `handoff` (the run finder on every
    re-entry) becomes a start-byte row (`memchr` or `memchr-bounded` with the match-start byte, `byte-class`
    for `(?<=ab)(?i:cdef)`, `first-memchr-bounded` for `\b`/`\B(?<=bc)d`). In all 84 the entry ask is kept
    and still verifies the lookbehind. 75 of the 84 had a start-byte prefilter at BASE; 9 had `handoff`
    (below).
  - Of the census's 57 movers, the decline touches 43. Of the other 14, 13 are movers whose prefilter is not
    the handoff row either way: `none` 7, `offset-set` 3 (bench 258 among them), `run-pinned` 1 (`(?<=foo)bar`), and 2 with a backreference (`-`), and 1 does not move at all
    (`(?<=(?<=a)b)c`).
  - ANSWER: the decline does not throw L3 away. The FIRST find of every search call (the entry move) still
    looks for the whole run, lookbehind bytes included, on every pattern that has one (104 of 104). What the
    decline gives up is the lookbehind bytes on RE-ENTRY. After an attempt fails, the forward scan re-seeds
    on the match-start byte (the base behaviour) instead of re-asking the run finder. Re-asking there was
    exactly the unsound step (W-L17). The VM route's attempt loop keeps its lookbehind-aware re-entry. Which
    of the two costs more on a subject with many false start bytes is a timing question; this lane measured
    no timing (none is in its brief).
- The plant is S3405: `tests/mech/sabotages/S3405_forward_reentry_at_negative_k.sh`, detector spanarms.rxt's
  W-L17 blocks. Verdict under "Tests and witnesses".
- Recorded: span_arms §14.4 L3, the REV 3.3 addendum (premise (3) refuted; witness, cause, decline, counts),
  and §14.4 L2's one-line note (AHEAD bytes are also outside the DFA's language). `pf_emit_handoff`'s header
  (src comment) now restricts the "equal futures" argument to K >= 0 and names the decline.
  `emit_req_landmark_move`'s header says K < 0 reaches it from the VM attempt loop only.

## CONFORM-1
Both attempt-loop rows read K through the offset bound's predicate (bff1a3d89, kept unchanged here):
- `req_handoff_entry_applies`: `PfBound k = pcrec_bound_of(...whole_maxoff); return req_handoff_vm_run(s) &&
  pcrec_bound_bounded(k);`, with the `k >= 0` conjunct deleted (§5.4 A8);
- `req_handoff_unbounded_applies`: `!pcrec_bound_bounded(pcrec_bound_of(...whole_maxoff))`.
So D-8's "the rows' predicates read the same predicate" is true. The DOC half of r63 CONFORM-4/HOUSE-2 is
`src/facts/facts.h`'s `pcrec_bound_of` header. It says `off` may have EITHER SIGN and that a negative `off` is
BOUNDED (D-7), never none. Its one sentence names `PfBound`, `WidthIv` (`bmin == bmax == -1` none, `bmax ==
PCREC_W_UNBOUNDED` unbounded) and `Ast.u.call.cwmax` + `cwmax_known`, with `EndMark.width`'s -1 a weaker
fourth. S1706 and S1956, which anchored on the old raw-`whole_maxoff` tests, are re-aimed at the new lines.

## Tests and witnesses
- `tests/litscan/spanarms.rxt` gains a "Unit L3" section of 38 blocks (19 patterns x default route and
  `engine vm`), 1,646 cells at every start position, generated with `gen_handoff.py`'s libpcre2-8 10.46
  ctypes oracle. Byte blocks are cross-checked against python3 `re` (no disagreement); utf8 blocks are
  `# pcre2-only`. The blocks: W-L1, W-L3, W-L10, W-L13, W-L14, W-L15, W-L16, W-L17, W-L18, W-L19, W-T3a,
  utf8 `(?<=éa)bc`, bench 333, bench 258, `(?<=a)\Kb`, `(?<=\Ga)b`, `(?<=foo)bar(?=baz)` (stays `foobar` at
  -3), W-D2 and the K -10 row.
- Already present and kept: W-L8, S-L, W-T3 (presence_deny.rxt, run under `--memfn=no-fd-pres-pick` by
  run_presence.sh). `python3 tests/litscan/gen_presence_deny.py --check-pcrec build/pcrec` regenerated the file
  byte-identically: "14 cases; pcrec check failures 0" over the default and the three denies.
- `tests/codegen/run_facts_checks.sh` [facts-look] gains 19 L3 listing cells: S-L/W-L1 `foobar` -3 pinned
  `0:3+3` and `restore=look` giving back `bar`; W-L3 `bc` -1; S1887's `(?<=abc)x`; W-S4c `req_byte` 98; W-L17,
  W-L18 and W-L19 (empty extents: `req_byte` 120 / none / 98, pin none); W-T3's listing row `a^20 b^12` at -20;
  and `(?<=foo)bar(?=baz)` at -3. W-D2's cell moves from `none dead` to `6263 dead`. Run:
  `bash tests/codegen/run_facts_checks.sh` gave "checks passed: 16, checks failed: 0" with "REACH: 52
  [facts-look] listing cell(s)".
- W-S4c: `("ws4c", "(?<=qz)ab", ())` in `tests/codegen/reqcube_check.py`'s WIT. `python3
  tests/codegen/reqcube_check.py build/pcrec <dir> gcc` printed "reqcube_check: 110 passed, 0 failed",
  including `'(?<=qz)ab': RX_REQ_BYTE 98 is a req_set member`.
- run_prechecks' K < 0 arms and vmhat_checks' signed handoff were built by l3feat (9095c489b, f7b9a25da) and
  are re-run under "Validation".
- New sabotages (ids S3405-S3413), each with a REACH probe. `REACH_ONLY=1 bash
  tests/mech/run_sabotage_matrix.sh S3405 ... S3413` gave "rows=9 reached=9 unreached=0".
  - S3405: decline removed, red on W-L17.
  - S3406: entry guard restored to `k > 0`, W-L15.
  - S3407: end clamp removed, W-L16.
  - S3408: the scan-index accessor's empty-stretch refusal removed, W-L17..19 (the compiler's pick over an
    empty extent).
  - S3409: BACK join keeps the LAST positions (`rn_pre`), W-T3a.
  - S3410: the K < 0 move lands at the hit, W-L10/W-L13.
  - S3411: the move's sign rows merged, W-L14.
  - S3412: the run span's `omin` stays 0, W-L1.
  - S3413: the `req_byte` pick reads the whole run, W-S4c (codegen arm).
  - Not planted: W-L3's union is L1's item machinery, already planted at L1.
- Plant verdicts. Command: `bash tests/mech/run_sabotage_matrix.sh S3405 S3406 S3407 S3408 S3409 S3410 S3411
  S3412 S3413 S1706 S1956 S3075 S453 S3383 S1887`, under `scripts/boxlock run`. The trailer was "15 rows
  (unexpected: 2, undetected: 2, unreached: 0, anomalies: 1)"; the rows it flagged were then re-run (next
  bullet). All 15 REACHED.
  - DETECTED: S3405 (corpus 15 fail, the W-L17 cells), S3406 (22), S3409 (220), S3410 (73), S3412 (506),
    S3413 (codegen 2), S1706 (memfnreach 1), S1956 (1), S3075 (prechecks 4), S453 (codegen 10), S3383 (facts
    1), S1887 (corpus 11).
  - S3411 was an ANOMALY: the plant does not compile. The K >= 0 text at a negative K compares a `size_t`
    difference with a negative literal, and the harness's generated-code compile refuses it as a
    `-Wsign-compare` error. The row now declares `SAB_EXPECT=COMPILE-CATCH`. Re-run: DETECTED-BUILD.
  - S3408 was UNDETECTED on the harness (0 of 2130 answers move). Over zero positions the primitive reads its
    UNINITIALISED candidate 0 (`pcrec_find_pos_pick`) and answers the index just before the stretch, a
    lookbehind byte, but no answer moves. So the refusal is load-bearing and its detector is the listing. The
    row is now on `SAB_SUITES="facts harness"`. Re-run: DETECTED (facts 1 fail, the W-L17/18/19 cells).
  - S3407 was UNDETECTED (0 of 2130), and the cause is MEASURED. The end clamp is defence in depth today. On
    the VM route the run finder verifies the whole run, so `hit + 16` never passes the end. On the default
    route the kit verifies only `Content-`, but `rx_prefilter`, which the moved position is handed to, begins
    with `if (search_from > subject_length) return 0;`. No byte past the subject is read, so asan has nothing
    to see either. The row declares `SAB_EXPECT=UNDETECTED`, with the reason in its `SAB_DOC_FIGURE`. Re-run:
    "UNDETECTED (EXPECTED)".
  - Re-run command: `bash tests/mech/run_sabotage_matrix.sh S3407 S3408 S3411` gave "3 rows (unexpected: 0,
    undetected: 1, unreached: 0, anomalies: 0)" at 84bdcdb92 (row files at a34979abd).
- Re-aimed: S1706, S1956 (CONFORM-1 lines), S3075 (its two-line anchor is now the value line plus the per-sign
  comment; its REACH grep stays valid because `a+xyz` is unbounded), S453 (the pick over the consumed extent),
  S3383 (TOP returns the extent) and S693 (abi). S1887's REACH now expects `run+K=61626378 -3`, the correct L3
  value; its plant states `abcx` at K 0. `python3 scripts/m6read_check_sab_anchors.py`: "sabotages checked:
  1376 ... all anchors resolve". S3074, S3076 and S1702 grep `if (landmark_position < attempt_position) {` on
  patterns with K >= 0 or unbounded (`a+xyz`, `b*xx(?=q)`, `(?:xx|y)abc`), so their reach is unaffected; their
  REACH probes passed in the run above's population, and the queued full REACH run checks them again.
- The D27 blinded author is a separate later lane (brief).

## Identity and movers
- Both sides are CLEAN builds from `git archive` (r63 process ruling): base 694d91dc4 at
  `$PCREC_TMPDIR/scratch/l3feat/basetree`, tip at `.../feattree` (tip ba8b5b880; later commits are tests and
  docs). Both built with `make -j8`, rc 0, 0 warnings.
- Over the census population (`cmp_l3.py`, above): fact movers 119, stamp movers 119 (default and vm), `.c`
  text movers with the abi number masked 119. These are the SAME 119 texts, every one carrying a positive
  lookbehind (the 40 "non-`(?<=`" hits are other lookbehind spellings). Every other text of the 5,932 is
  byte-identical in its `.c` on both routes except the abi number, and identical in the four facts.
- REQ_WHY base -> tip over the movers: dominated -> emitted 79, emitted -> emitted 24, dominated -> dominated
  16.
- No mover on the default route reads `DFA_PREFILTER "handoff"` with a negative K (103 default-route movers
  carry a negative `REQ_HANDOFF`; 0 of them `handoff`).
- FINDING (a perf mover, answers unchanged): 9 movers read `DFA_PREFILTER "handoff"` at BASE with K 0 or 1.
  At the tip their K is negative, so the decline falls them to the start-byte row: `(?<=qz)x?a:` (1 ->
  -2, `memchr`), `(?<=ab)(?i:cdef)` (0 -> -2, `byte-class`), and seven `(?<=a)`/`(?<*a)` forms (0 -> -1,
  `memchr-bounded`), listed in `ident_movers.tsv`. The choice of the BACK run moves them off the forward
  re-entry they had. Proposed filing below; no fix was built (D77).
- Bench 258 `(?<=item )done`: run `done@0` -> `item done@3` (`6974656d20646f6e65`), K 0 -> -5, `req_byte` 100
  unchanged, pin none -> `0:5+4`, `REQ_WHY` emitted, `DFA_PREFILTER "offset-set"` before and after (with or
  without the decline), VM prefilter hybrid.
- Bench 333 `(?<=\xc3\xa9)x`: run none -> `c3a978@1`, K none -> -2, `REQ_WHY` dominated -> emitted (default
  route), `DFA_PREFILTER "memchr"` at base and at the tip. It is `"handoff"` only without the decline.

## abi event
109 -> 110 in ba8b5b880. Readers were found by `git grep -n -w 109 -- src tests docs/spec docs/testing.md`
plus `PCREC_ARTIFACT_ABI` (every other hit is PCRE2 error 109, a timing or a count):
- `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI`;
- `docs/spec/match_api.md` §6 (the `PCREC_RX_ABI_H` guard, its `#error` text, the define, the `rx_info.abi`
  row and §6¶17's sentence: five sites);
- `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT` and its transition message (109->110 appended);
- `tests/mech/sabotages/S693_abi_not_bumped.sh` (BEFORE 110, AFTER 109);
- `docs/dev/history/abi_changelog.md` (the head paragraph).
The identity gate's (B) pins in `tests/codegen/run_recursion_identity.sh` (FILEPIN d68a1294c, ABASEPIN
b2d73b6b1) cite abi 109 as their commits' number, which stays true; they pin commits, not the number, so they
are unchanged. The new emitted text (K < 0 only): the move's own row with its end clamp, the per-sign re-ask
test, and the "at least B bytes after" K comments. `make test-codegen` and the suites that count are under
"Validation dispatched".

## Contract
D-13's L3 row, D80, all in ba8b5b880:
- `match_api.md` §6.3.7¶5: `req_byte`'s run pick reads only the run's CONSUMED positions.
- §6.3.7¶6: a run may begin inside a positive lookbehind, by at most its declared length in bytes;
  `(?<=foo)bar`.
- ¶10: a `"-3"` example.
- ¶11: K of either sign; the candidate floor `max(0, startpos + omin)`, `omin = min(0, K)`; at K < 0 every
  match begins at least -K bytes after the landmark; NOMATCH where `that - K` passes the end; the forward
  re-entry never at K < 0.
- §6.3.4's `"handoff"` prefilter row: "Never where `K` is negative".
- `tuning.md` §2.27¶4 and §2.28¶7: the consumed-positions pick.
- §2.28¶1: the definition's BEFORE side; denied, no scan begins before the start offset.
- §2.41¶1: the signed floor and negative K.
- §2.41¶8a: the decline at K < 0, with the reason and the witness.
- §2.41¶8b: K finite of either sign.
- §2.41¶8c: the unbounded-K premise; a BACK run has a finite negative K.
- `facts_listing.md` §4.1.2¶8: the run may begin inside a lookbehind; `req_byte` and `run_pin` read the
  consumed part; "No byte of it lies inside a lookbehind" is dropped.
- §4.1.2¶8b: `req_landmark_maxoff` may be negative.
Checked unchanged: §6.3.7¶4 and ¶7 (`@idx` is the kit's), `findings.md` §4. `make test-spec-history`:
"checks passed: 11, checks failed: 0".

## Deviations from the design
- bff1a3d89 (l3feat): the hybrid prefilter's kept `landmark_position` was initialised to `search_from`. At
  K < 0 that is not a neutral hit: the move from a hit `h` lands at `h + B`, past `search_from`, so the
  first lane dropped matches with it. The init now asks the kit at `search_from` when K < 0 (a miss is
  NOMATCH). The design named no init. UNDER THE DECLINE THIS BRANCH IS UNREACHABLE: no prefilter keeps a
  re-entry site at K < 0 (`pcrec_req_site_in_prefilter` needs the forward `handoff` row). It is kept as that
  sign's stated init, its comment says so, and the abi changelog does not list it as emitted text. Removing it
  is the manager's call (it would come back with any re-entry L2 re-proves).
- Premise (3) refuted, and the decline (R-1): see "Forward-scan decline at K<0".
- W-D2's run moves (dead with `bc` at -1). D-4 has no never conjunct; the census's never class assumed none.
  Listed, sound.
- Not planted: W-L3 (L1's item), W-L14's "hang" form. S3411 merges the sign rows; whether the gate then
  reports a wrong answer or a timeout is in its verdict.

## Validation dispatched
Inline, all on lane/l3feat. A suite is red only if make prints `*** [...test-X] Error`; the grep
`-E '\*\*\* \[(Makefile:[0-9]+: )?test-'` found 0 such lines in every log below.
- `make -j16` rc 0 and `make strict` rc 0 at ba8b5b880, the last src change (later commits are tests and docs).
- `make test-codegen` (abi readers, ABI_EXPECT 110, SABANCHOR) passed: "checks passed: 1, checks failed: 0" on
  its last section, no Error line.
- `make test-prechecks`: "checks passed: 405, checks failed: 0".
- `make test-registry`: "checks passed: 44 ... 79, checks failed: 0", definitions-oracle 0 disagreements.
- `make test-rxtsource`, `make test-startset` and `make test-memfn-manifest` were first red: population pins and
  the vm mover manifests did not yet count the new L3 blocks. They were re-pinned in a34979abd:
  - CENSUS/RUNSH blocks 7224 -> 7264 and lines 99815 -> 101791;
  - C3 PASS/VERIFIABLE +1824, SKIP/pcre2-only +152;
  - 22 + 38 = 60 manifest rows, every one a new block, asserted past the base line counts.
  After the re-pin: rxtsource "checks passed: 300, checks failed: 0"; startset "35 / 0", with [vm-movers] 612 auto
  and 4543 vm rows and 0 off-diagonal; memfn-manifest "14 / 0".
- `bash tests/startset/run_vmhat_checks.sh`: run before the manifest re-pin, it had the same 2 [vm-movers] reds
  and 20 passes. Its manifests are the ones re-pinned above, and test-startset runs the same check green.
- `bash tests/harness/run.sh tests/litscan/spanarms.rxt tests/litscan/handoff.rxt tests/litscan/handoff_vm.rxt
  tests/litscan/presence_deny.rxt tests/lookaround`: "cases passed: 12742, cases failed: 0".
- `bash tests/codegen/run_facts_checks.sh`: 16 / 0. `python3 tests/codegen/reqcube_check.py`: 110 / 0. `make
  test-spec-history`: 11 / 0. `python3 scripts/m6read_check_sab_anchors.py`: "all anchors resolve".
- Mech: the plant verdicts under "Tests and witnesses".

Dispatched (verdicts reach main as CLOUD-DONE / through the queue; this lane does not wait):
- Cloud TEST: `scripts/cloudrun --owner main --kind test --ref eb95f904a58e42da56c02fdd21819bd0fe6d440f --name
  l3feat-test`, recorded in the ledger. Proof: `git ls-remote origin 'refs/heads/cloud/main/*/l3feat*'` printed
  `eb95f904a58e42da56c02fdd21819bd0fe6d440f refs/heads/cloud/main/test/l3feat-test`.
- Cloud AXES: NOT DISPATCHED. `scripts/cloudrun --owner main --kind axes --ref eb95f904a... --name l3feat-axes`
  failed three times with "push of cloud/main/axes/l3feat-axes to origin failed 1". cloudrun bounds its push at
  120 s (`"$TO" 120 git push`), and the pre-push-light hook's `make strict` alone takes about that long on this
  box at load 11-12. A `git push --dry-run` of the same ref took 1m59.6s and printed "all checks passed". The
  test push succeeded on its second try at 1m53s. The ls-remote above shows no axes branch. RUNS.md dispatches
  the axes kind after the test kind is green anyway, so this is the manager's follow-up dispatch, at the same
  sha. Proposed filing below.
- Box queue: `301-main-l3feat-reach` (`REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh`, every row's REACH
  probe) and `302-main-l3feat-sanwit` (asan and ubsan builds, then `tests/litscan/spanarms.rxt`, both axes; W-L16
  through W-L19 live there). Both passed `bash -n` and `--dry-run`, and `scripts/boxqueue add` queued them ("queued
  ... cap 3600"). Copies are in `l3feat_evidence/`.

## STATE AT HANDOFF
Branch lane/l3feat at eb95f904a (all code, tests and evidence), plus the report commit that adds this file.
Rulings applied: R-1 (the decline, the REV 3.3 addendum and L2 note, the deviation, S3405, the
gen_presence_deny temp root) and R-2 (the three-build measurement, in "Forward-scan decline at K<0"). LAST R-n
APPLIED: R-2.
Queued for main's watcher, verdicts not yet in:
- cloud run `cloud/main/test/l3feat-test` at eb95f904a;
- box jobs `301-main-l3feat-reach` and `302-main-l3feat-sanwit`.
NOT dispatched: the cloud axes run (see Validation dispatched), the manager's follow-up at eb95f904a.

Proposed filings (no numbers taken):
- Tooling: `scripts/cloudrun`'s 120 s push bound is below the pre-push-light hook's `make strict` time under load,
  so a dispatch fails at random (here 3 of 4 tries).
- Perf mover: 9 patterns had the forward-scan `handoff` at BASE (K 0 or 1) and lose it to the decline, because
  their chosen run is now the BACK run at K < 0. Examples are `(?<=a)\Kb`, `(?<=qz)x?a:` and
  `(?<=ab)(?i:cdef)`. Their answers are unchanged. A trigger to measure: a bench row of this shape.
- L2/L3 follow-up: a SOUND forward re-entry at K < 0 needs a start state that has read the lookbehind. Today
  the decline is the whole answer. The unreachable hybrid-prefilter K < 0 init (Deviations) waits on that
  design.
- Census model gaps for any later census: other lookbehind spellings (40 movers), nested lookbehind (the 1
  predicted non-mover), never rows (W-D2).
- S3407 records a redundant end clamp (UNDETECTED by measurement). S3408 showed that
  `pcrec_find_pos_pick` reads an uninitialised `cand[0]` when n is 0. Its only caller now refuses n == 0, but
  the primitive could guard `n == 0` itself.
- The D27 blinded author for L3, per the brief, as a separate lane.

OWED: none to this lane. Verdicts owed to main by the queue and the cloud: the three runs above.
