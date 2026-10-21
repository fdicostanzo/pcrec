# i1build — [FINDALL-NEXT] I0 + I1: the find-all iterator (lane report)

Lane i1build (opus), 2026-10-21, branch `lane/i1build` from main `e05050a48`
(abi 82). Design: docs/design/findall_iter.md revision 3, as cut by the two
manager rulings in docs/dev/lanes/i1build_rulings.md (last entry applied: 2).
The build's departures from revision 3 are the design's §12 addendum. The
contract is docs/spec/match_api.md §3.8.

## 1. What landed

**I0 (commit `ac4021692`, no abi event, no emitted byte):**
- `reports_empty`, an E1 fact (src/facts/widths.c): the minimum REPORTED
  width is 0. `a*` yes, `ab\K` yes, `a\Kb` NO, `ab\Kc?` yes, `(a|)\Kb` no,
  `(?1)(\K)` yes. Listed by `--emit-facts` (facts_listing.md §4.1.2¶5a);
  `pf_check_e1` holds it to the lowered tree and `nullable => reports_empty`.
- `Dfa.notempty` (src/ir/dfa.c, memo key in src/opt/dfamemo.c): the notempty
  START ROOT as a construction parameter.
- The `mg` line (rxt_format.md §1.7.1) in the schema, `--list-source`,
  run.sh's arms and verify_rxt.py (`re.finditer`); the rxtsource census awks
  count it.

**I1 (abi 82 -> 83), on every artifact:**
- `<prefix>_next(rx_iter *, caps)`, the `iterate` row of `entry_rows[]`
  (src/gen/emit_iter.c): bind once (`__enter`: the FRESH/BOUND/ENDED state
  machine, the setters' normalization IT1, the caller-position prologue
  `__bind_checks` run once), one STEP per call (`__step`: the retry, the
  search at `lo`, PCRE2's advance; commits only on a match), ENDED sticky
  (IT2), no owner check (IT5, stated in §3.8¶8).
- The shared ABI block: `rx_iter` (fixed type, every prefix), `rx_nextfn`,
  `PCREC_ITER_*`, `rx_iter_init`/`RX_ITER_INIT`, `rx_iter_at`,
  `rx_iter_vars`, `PCREC_ERR_ITER` (-10); `struct rx_info` appends `next`
  (ruling 2). The header: `<prefix>_next`, `<prefix>_iter_buffers`.
- `<PREFIX>_ITER_RETRY` (`none` / `dfa-root` / `vm-guard`, §6.3.13).
- The split: DFA `<prefix>_search` = head + prologue over `<p>__find`
  (`always_inline`; `noinline` on the attempt route's label-table body); VM
  `_search_run` = range test + guard over `<p>__find`.
- The retry, on `reports_empty` artifacts only: DFA `<p>__retry` over the
  notempty-rooted machine `Job.nedfa` (a compound's shell included); VM
  `<p>__retry` + the accept label's guard. One meter per search (D165 add. 4).
- The residual twins `<p>__<name>`; the exported entries are forwarders.
- Hoisted out of every BOUND call: the startpos guard / alignment and the
  `-futf-check` range check (bind). Variable resolution stays per search
  (§12 of the design says why).
- NO batch ABI (ruling): **I2 appends**, at `PCREC_ITER_LAYOUT` 4, `rc_next`
  (int32, the padding at offset 12), then `batch`, `nbatch`, `bhead`,
  `bcount`, `st` after `bufs`; `PCREC_ITER_OPT_BATCH` takes `0x80`; `struct
  rx_info` appends `next_n` (`rx_nextnfn`) after `next`. `rx_iter` is 72 B
  on LP64 today; no I1 field moves.

**Neutral to length decisions (§6.4).** The scaffold bracket
(`pcrec_sb_scaffold_open/_close/_putc`, src/core/sb.c) holds every new byte,
including the twins' second `_` at every call site. Measured on 29 artifacts
(DFA, VM, hybrid, utf8, `-futf-check`, align, vars, `\K`, compound), I0 vs
I1 counted size (`--warn-emit-bytes=1`): identical everywhere except (a) a
`reports_empty` DFA artifact, where the notempty machine is counted like any
machine (`x*|y` 15,678 -> 17,667 code bytes, `a*`, `(?=a)`, `x*|.` utf8,
`^\s*|\s*$` the shell), and (b) one byte on a compound shell (its controller's
`__next_pos` reference, `^\s+|\s+$` 19,819 -> 19,820). The raw files grow by
~6.4-7.5 KB (cpset manifest, below). The full-corpus census is queued (§4).

## 2. Spec and docs (D80)

match_api.md §1¶2/¶5/¶6/¶8, §1¶7 (guard 83), §2 (the block regenerated from
`'a(b|c)+d'`), §2¶8a, §3¶1 (table row), §3.1.3¶1/¶9/¶11 (the loop's
differences from PCRE2 restated: not always an omission, `a??b?`, the CSV
idiom, `x*|y`; `ab\K` three times under the iterator), NEW §3.8, §4 (row +
¶9a), §6 (row 30 `next`, ¶14b, abi 83), §6.3.2 inventory + §6.3.12 kind +
NEW §6.3.13, §10.2¶5. rxt_format.md §1.7.1, facts_listing.md ¶5a, vars.md
§4. TOCs regenerated; `tests/spec_history` green. abi_changelog.md entry.
Directory CLAUDE.md files: src/gen, src/facts, src/ir, tests, tests/findall
(new), tests/codegen, tests/harness, docs/dev/lanes. plan.md row STATE:started.

## 3. Checks

- **tests/findall/** (`make test-findall`, in TEST_SECTIONS, shard 1):
  `run_iter_diff.sh` over `cells.tsv` (62 byte patterns x 18 subjects, 8 utf8
  patterns x 9 subjects x 3 flag sets), auto / vm / dfa. Measured green:
  `groups=242 ok=3619 giveup=92 skip=0 illformed=24 retry-cells=621
  dfa-root=110 vm-guard=81`. The 92 GIVEUPs are all `-futf-check` refusals
  of ill-formed subjects (documented, §9.4); the 24 ILLFORMED cells are the
  ill-formed-UTF-8 boundary difference the §3.1.3 loop already has (the
  iterator equals the loop; libpcre2 under MATCH_INVALID_UTF answers
  otherwise). Zero DIFF. The ASan cells: 12 groups, 190 OK, 28 retry cells.
  `global.rxt` (62 blocks, 1,116 `mg` + 288 `mc`): run.sh 1,404/0; python
  verify all pass (216 pcre2-only skips).
- **tests/codegen/run_residual_twins.sh** (test-codegen): 9/0 incl. the plant.
- **The state-machine arms** in iter_drv.c on every subject: sticky, endset,
  nullcaps, poison (setter on BOUND, zeroed header), dirty-init (0xA5 fill),
  info (`rx_info.next`), at1.
- Re-pinned by measurement: rxtsource census (+1 file / +62 blocks / +1,404
  lines; C3 PASS +1,188, SKIP +216), the K59-PREMUL rung (762,954 -> 765,616
  raw; its code bytes 15,143 unchanged), the cpset EMITTED_BYTES manifest
  (+6,429 DFA, +6,417 `^foo$`, +7,137 VM, +7,549 tiered; other stamps
  identical), `ABI_EXPECT` 83 + ledger, S693 (82). Six sabotage anchors
  re-anchored (S504, S701, S891, S902, S1126, S1151); `m6read_check_sab_anchors`
  all resolve.
- `make strict` clean; spec_history green; test-rxtsource green; clang -O2
  and gcc -O0/-O2/-O3 `-Werror` compile of DFA/VM/compound artifacts with the
  driver (clang found a `-Wtautological-compare` in the first VM guard; fixed).
- **Sabotage rows S1297-S1308** (mech arms `findall`, `twins`, registered):
  VM guard removed, DFA retry gate off, `\K` reports_empty wrong, K75 end
  advance, ENDED not sticky, setter-on-BOUND not poisoned, bind `lo` not
  normalized, the utf-check calling the exported residual, the stamp
  swapped, `rx_info.next` NULL, the notempty root keeping accepts, the VM
  retry not arming. All expect DETECTED; none run yet (§4).
- **Parity post-build mode**: `PARITY_POST=1 PCREC_OLD=<parent pcrec>
  parity.sh` (arms L_old = loop over the parent's artifact, L_new, A, I = the
  built `_next`; the verdict marks cells 1, 3, 4 GATE and 2, 5, 6, 7 REPORT,
  D171). Smoke green: 96 answers against L_old and python `re`, PLT
  structure 16/16.

## 4. STATE AT HANDOFF

Branch `lane/i1build`: I0 `ac4021692`, I1 `38a439e25`, the FILEPIN self-pin
`6834bc26c` (`tests/codegen/run_recursion_identity.sh` -> `38a439e25`), then
this report's commit. Rulings read: entries 1-2 (last applied: 2). Built and
committed; **nothing below has run**. Queued at 2026-10-21 ~17:30 behind
`560-kit-e8-window` as boxqueue jobs (owner `i1build`; the job scripts and
`i0ref.sh`, which builds the I0 commit's pcrec into `build/i0ref`, are in
`worktrees/i1build/build/i1jobs/`, uncommitted scratch). Each job is capped at
8 cores; 640 waits for 600-630 to end and for the quiet gate (load1 < 2.0
twice a minute apart), pinned to cpu7:

| job | what | read |
|---|---|---|
| `600-i1build-i0sweep` | emit_sweep, `e05050a48` vs the I0 commit, streams c-default, c-vm, emit-ir, composition: I0's zero-mover claim | identity on all four |
| `610-i1build-maketest` | `make test` on the I1 head | make's `*** [...test-X] Error` lines |
| `620-i1build-mech` | mech S1297-S1308 + the re-anchored S504 S701 S891 S902 S1126 S1151 + S693 | each row's verdict |
| `630-i1build-census` | tests/findall/mover_census.py, I0 vs I1, the whole corpus | CLEAN, or the UNEXPLAINED list |
| `640-i1build-parity` | the post-build parity timing (quiet gate, idle-ok), 5 launches | VERDICT rows: cells 1, 3, 4 `GATE I PASS` (stop rule) |

Expected reds in `make test`, named so a reader does not mistake them:
suites that pin per-entry structure the iterator changed and that this lane
could not run under the box rules: `test-compound` (entry_ranks.tsv's
derived edges gained FIND/NEXT rows; compound_drive.c's suffix table gained
`next`), `test-partlayout` (its attribute census meets `__find`'s
`always_inline`/`noinline` and the twins' `noclone`), any byte-count pin not
listed in §3 (size tripwire, `run_anchored_match.sh` §5's caps,
emit_sweep VARIANT_PINS), and `test-encoding-checks` (DD12a(i) compares the
engine text, where `__find` and the twins are new names). A red there is a
re-pin or a new excision to make, not a wrong answer: the answer suites
(corpus, findall, the differentials) are the ones that must be green.

## 5. Deviations, findings, owed

- Design §12 lists the deviations (no batch ABI; `reports_empty` precise;
  separate notempty machine; split as two entries; twins `__<name>`; var
  resolution per search; second bracket; `find` part-layout class empty;
  tests/findall at I1; `mg` = §1.7.1).
- **I0's tests/findall/ landed at I1** (ruling 1 listed it in I0): the
  harness drives `<prefix>_next`, which I0 does not have. I0's mg parse and
  the fact landed first.
- **Not migrated** (design §6.7 table): tests/assertions/gstart_findall.c,
  tests/encseam/findall_driver.c, tests/codegen/entry_shape_driver.c gaining
  an iterator arm. tests/findall covers the iterator's answers; the three
  arms are owed.
- **Box rule breach, mine:** before reading BOILERPLATE's 50-compile cap I
  ran `run_iter_diff.sh` (~726 compiles, ~15 s each run) four times and a
  20-pattern size sample outside the box lock, at PROCS=8. Afterwards I
  killed a direct `boxlock run` waiter of my own (it would have jumped the
  queue ahead of `560-kit-e8-window`) and moved every heavy run to the queue.
- **Unification candidate:** the scaffold bracket is the SIMD bracket's
  twin (same rules, own counters). With a third "excluded from length
  decisions" member, one bracket with a kind is the general form.
- **The compound shell's one byte** (`__next_pos` in the controller text,
  passed as a fragment to `callsite_emit`) is the one scaffold byte counted.
- **Size**: every artifact's file grows ~6.4-7.5 KB (the ABI block's
  iterator text and doc comment, `_next`'s parts). No decision reads it.
