# Critic "checks" (the controls): start_table.md §3.3-§3.5 and start_table/

Read-only critic, light D6 panel, 2026-10-06. Lens: the controls. Probes were
small `build/pcrec` runs under `timeout`; nothing in the tree was modified.

Method for the reach numbers: for each deny flag, compile every distinct corpus
pattern (3,595) at default and under the flag, and count artifacts whose `.c`
bytes differ. That is a byte-observable per-row reach with no source shared with
the code under refactor. All counts are on the Mac `build/pcrec` of the current
tree.

| arm | -fno-offset-skip (16) | -fno-start-set (47) | -fno-req-set-lead (45) | -fno-req-handoff (46) | -fno-start-pinned (22) | -fno-hyb-reseed (37) | -fno-vm-anchor-bound (28) | -fno-end-window (29) | -fno-req-run-fold (44) |
|---|---|---|---|---|---|---|---|---|---|
| auto/byte | 513 | 136 | 14 | 163 | 183 | 403 | 337 | 288 | 48 |
| auto/utf8 | 604 | 127 | 8 | 280 | 183 | 420 | 337 | 0 | 38 |

The vm/byte and vm/utf8 arms were NOT completed (probe stopped); no vm-arm reach numbers are claimed here.

## BLOCKER

None. Nothing found that makes the no-mover claim unprovable in principle. The
MAJORs below are each a place where the written proof would pass over a real
mover.

## MAJOR

### M1. The "6 re-aim / 47 re-run" split is wrong in at least three places, and the family list is hand-enumerated

`sabotage_anchors.family` is a hand-written list of function names
(`sabotage_anchors.family`, one line). A row is FAMILY iff its owner function
is on it. The refactor deletes or reshapes things that are not on the list, and
rows whose anchor text names those things are silently counted as "re-run" or
as outside the family.

- **S222** (`tests/mech/sabotages/S222_start_stamp_forked_from_selection.sh:69`):
  `SAB_BEFORE` is `dfa_search_start_name`'s body,
  `{ return dfa_search_start_of(cx)->c.name; }`. `dfa_search_start_of` is deleted
  at C3 (start_table.md:511) and the `->c.name` path changes with `CandRow`.
  `sabotage_anchors.tsv:64` has it as owner `dfa_search_start_name`, NOT marked
  FAMILY (that name is not on the list). So it is in neither the 6 nor the 47.
  At C3 `mech` would report APPLY-FAILED (the S43 shape from learnings §3: the
  coverage assertion and the planting both stay "honest" while the row goes dark).
- **S371** (`S371_...:24`): `SAB_BEFORE` is
  `if (rs->row && rs->row->action != VRS_A_FIXED) {` at `emit_vm.c:13329`. C5 moves
  `action` into `u.reseed` (start_table.md:105, `u.reseed (action, start column, armed)`).
  `rs->row->action` will not exist. It is listed in the 47 "re-run" rows
  (start_table.md:603 "8 in vm_emit_search_body ... S370, S371").
- **S169** (`S169_root_minw_unchecked.sh:45`): `SAB_BEFORE` ends in
  `if (v->root_minw >= PCREC_MINW_MAX)` (`emit_vm.c:13234`). That `if` IS row H1's
  predicate, and C5 says "the root-minw `if` read their slot's row"
  (start_table.md:516). Also listed in the 47.
- **S263** (`emit_vm.c:13479`, `attempt_max = search_from`): §3.5 says it stays
  only "IF the string literal moves there" and the plan "keeps each emitted
  literal in the body function" (start_table.md:609). §2.2 (BOUND table, line
  ~318) says `u.bound` IS "the emitted bound string" and "`u.bound` is the same
  string on B3 and B4". These contradict each other. If §2.2 wins, S263 moves too.

So the honest count is at least 9 re-aims (6 + S222, S371, S169), 10 if S263
follows §2.2. The "47 stay" claim is the one the plan leans on for cheapness.

The mechanism that should have caught this is missing: nothing re-checks, per
commit, that EVERY sabotage row's `SAB_BEFORE` still matches exactly once. The
census script (`sabotage_anchors.py:37`) does `txt.find(before)` at ONE tree and
never runs against the post-refactor tree. Also not covered by the 207:
- 9 rows carry `SAB_FILE2="src/gen/emit_vm.c"` (S141, S218, S108, ...); the script
  reads only `SAB_FILE`.
- C6 rewrites `axes_dump.c` and `AXIS_DESC`; no row anchored there was looked for
  (a grep of `axes_dump|AXIS_DESC` over `tests/mech/sabotages/` returns nothing,
  so probably none, but the note does not say it checked).

Fix: add to each of C3-C6 a mechanical gate "every `SAB_BEFORE` in
`tests/mech/sabotages/*.sh` (both FILE and FILE2) occurs exactly once in its
file" run on the child tree, and derive the family by call graph from the moved
symbols instead of a hand list. Then the 6/47 split is an output, not an input.

A second class: anchors that survive textually but stop REACHING their site
([MECH-REACH]). S490's own header (`S490:18-28`) is the example the note cites:
its `SAB_REACH` greps `rx_seed_state[`. Once the row walk sits between the
predicate and the emitted text, a plant inside a predicate that is only reached
via the walk is reached only if the walk still asks it. The note says S495's
REACH "must still find a name read" but gives no check that every re-run row's
`SAB_REACH` probe still passes on the child. `mech` reports REACH per row, so
this is cheap, but it is not in §3.3 item 6's list ("mech on every re-aimed
row" only, not "every re-run row's reach").

### M2. C0 has no failing direction for its own plumbing

C0 adds `--extra ARG` and says identity is required on the utf8 arm
(start_table.md:530-533). The failure mode that would make this arm vacuous is
the flag being dropped on one or both sides (or, in `compile_stream_ir`,
appended after `--pattern` and swallowed, or placed where the CLI ignores it).
Dropping `-e utf8` on both sides makes both sides byte-identical to the default
arm, `both_ok` goes UP (the utf8 arm compiles 3,229 vs 3,221 patterns, so the
byte arm compiles fewer), and the floors (`emit_sweep.py:185-187`) are floors on
`both_ok`: they cannot fail. The self-check (`emit_sweep.py:790-815`) compares
two builds of the same rev through the same argv builder, so it shares the
defect.

What would have to be true for it to fail, and who chooses the input: nothing,
as specified. Specify a per-arm witness that the arm DIFFERS from the default arm
on the same side: count patterns where `bytes(arm) != bytes(default)` and floor
it. My measured deltas are floors C0 can pin directly (above table): utf8 vs
byte is large by construction; each deny arm differs on 8 to 604 patterns
(only `-fno-end-window` at utf8 is 0, and that is the correct zero, W1's fact
declines under non-boundary encodings: it must be asserted as 0 explicitly, not
floored, or the arm reads as a dead flag).

Also unspecified: `--extra` on stream 4. `--source`/file mode with `-e utf8`
makes `compose_encoding_clash.rxtin`'s `ok` target refuse
("definition 'plain' declares `encoding byte` but this artifact is 'utf8'"), so
the composition stream's utf8 arm is a different population (37 producing files
/ 106 artifacts vs 38 / 108 at default; measured). Not a floor failure, but
the plan should say stream 4 under `-e utf8` is partial by design.

### M3. The selection trace is under-specified exactly where it matters

§3.3 item 5 calls the trace "stronger than bytes". It is, but only if:

1. it is keyed per compile AND per pattern AND ordered. "prints `slot route row`
   to stderr" (C1) says none of that. A multiset diff of lines across a whole
   corpus run cancels a swap between two patterns; a per-pattern unordered diff
   misses a reorder of two asks, which is the very thing §1.3 "No eager plan"
   promises not to change. Specify the record as `pattern-index, seq, slot,
   route, row`.
2. the print site is the walk's RETURN, not the reader's use. After C3 the body
   can ask `cand_select`, print, and then ignore the answer (an inline fallback
   left behind). Trace agrees, bytes agree on corpus, no mover, but the table is
   not what decides; that is the opposite of the refactor's purpose and the
   trace would bless it. At least the C6 and "no reader keeps an inline chain"
   check should be a structural grep, not the trace.
3. the reference is regenerated from the PARENT's trace build each commit, not
   recorded once at C1 ("Reference traces are recorded at C1", start_table.md:526).
   A reference stored at C1 goes stale on any corpus change between C1 and C6
   (the corpus grew 3,938 to 4,606 rows since the sweep's floors were pinned, see
   m4) and then every later commit "differs", teaching the reviewer to re-record,
   which is how the control comes to share a source with its subject.
4. the trace build is a DIFFERENT binary from the default build whose bytes the
   sweep compared (`-DPCREC_CAND_TRACE`). Fine for decisions; but then the claim
   "no emitted byte moves in the default build" rests only on `#ifdef` text, and
   the sweep (items 1-4) must run on the default build, which §3.3 does say.
   Make explicit that the trace build is NEVER the one the byte sweep ran on, and
   that a byte sweep of the trace build against the default build is part of C1
   (else a trace build that changes bytes is invisible).

On what could make it agree with a wrong walk: the C2 both-walks oracle runs the
old walk and `cand_select` in one process over rows whose predicates are the SAME
functions by pointer identity (start_table.md:343-346). It tests only the walk
FILTER (slot, route mask, deny order, first-match), not predicate selection.
That is a real but narrower control than the text suggests; and the old walk
being run first means a predicate with side effects (`pcrec_find_byte_rate`
records its first ask, §1.3) is evaluated by the OLD walk and cached, so the
second walk sees the cached answer. The `used` column and `RX_FINDINGS` then
cannot show a double evaluation. State this, and run the oracle with the order
swapped on a second pass.

### M4. §3.4's gap list is stale in one direction and incomplete in another

- "`set-leads` (P4) is invisible to every stamp ... its witness cells are
  run_prechecks.sh §5.11" (start_table.md:564-566). True of STAMPS, but
  set-leads is byte-visible: `-fno-req-set-lead` changes the emitted `.c` of 14
  distinct corpus artifacts at auto/byte and 8 at utf8 (table above; the row emits
  the set pick's memchr first). So the byte sweep reaches it at 14. The note
  conflates "no stamp" with "no byte", then asks for an out-of-sweep witness
  where the sweep already covers it, and, worse, relies on the trace for P4 when
  the independent control (bytes) exists. Use the deny-delta count as the per-row
  reach for every row that has a deny bit; it shares nothing with `cand_rows[]`.
- "`fixed` (R6) has population 0 at default; reached under `-fno-hyb-reseed`"
  (start_table.md:567). Measured: the arm moves 403 (byte) / 420 (utf8)
  artifacts (390+13 = R5+R4 stamps, so it checks out), but row_census.py has no
  deny arm at all (`row_census.py` ARMS list: four arms, no deny), so the note's
  "pop under the deny arm" is asserted, not counted in the census it cites. It
  should be a census arm, or cite the delta count.
- Rows with NO deny bit and a small population have only the stamp: H1 (6, from
  `VM_ROOT_MINW` literal `1099511627776ULL`, which equals 2^40 =
  `PCREC_MINW_MAX`; a census keyed on a literal value rather than the row's
  predicate shares the constant with the code it checks), B4 `gstart` (5 / 20),
  R4 `adaptive-dense` (13).
- B1 `bot`, B2 `gstart` (ATTEMPT bound, `emit_dfa.c:9333-9388`): no
  `row_census.tsv` stamp exists for them (the 293/21/74 figures come from
  `anchor_agree.py`'s literal read) and **no sabotage row anchors anywhere in
  `emit_dfa.c:9325-9395`** (checked against `sabotage_anchors.tsv` lines).
  These two rows, plus the "three inline bound strings", are the thinnest
  covered in the table: corpus-only, with the trace as the sole second control.
  C5 rewrites them. Name a witness (the `\G` / `(?m)^` shapes in
  `tests/assertions/`) and add the sabotage row before C5.
- Census rows share stamps. P4/P5 both stamp `"emitted"` (582), so the cross-check
  "hit counter vs stamp count" (start_table.md:575) can only check P4+P5 together;
  P4's own counter has no stamp control (the deny delta of 14 is the control).
  Likewise N1/N2 share bits 16|32 with N3/N4 on bit 16: the two arms must be read
  as a pair of deltas (513 for 16 includes N1-N4; 32 alone is the run-pinned pair).

## MINOR

### m1. Row-name check widened to every row will false-positive on day one

`cand_rows_check.py` (a) fails on a comparison call with a string literal equal
to a row name except `"none"` (`tests/codegen/cand_rows_check.py:5-14`).
Widened to all 37 rows, the names include `all`, `exact`, `anchored`, `window`,
`fixed`. `src/parse/enabled.c:262` has `if (!strcmp(spec, "all"))`. The author
will exempt it, and the exemption list is the same shape as the `"none"` carve-out
that the check already admits is a hole. Key the literal half on (row name AND
a `c.name`/stamp-typed receiver), or accept the exemption by name with a count.

### m2. Regex that reads the table will not read the new table

`cand_rows_check.py:130` anchors on `static const DfaPf dfa_pfs[] = {` and the
names regex is `\{\s*(?:\.c\s*=\s*)?\{\s*"([^"]+)"`: it expects a positional
`"name"` first in the inner brace. §1.1 specifies designated initializers
(`.c.name` ...). Re-aimed as designed, the regex returns zero names, which the
check's own K35 guard turns into a loud FAIL (good). But `[cand-route-walk]`
(`:177`, `static const void \*dfa_select\(`) is not mentioned in §3.5's re-aim
list; the signature `const CandRow *cand_select(` does not match, and it too fails
loud. Both fail loud rather than silent; list them so a reviewer does not read the
red as a regression.

### m3. The four new checks have no sabotage rows

§3.5 adds four checks (every (slot, route) ends in `cand_always`; `u` matches
slot; no comparison reads any row name; every `CandSel` names `.slot`/`.route`).
`tests/mech` has exactly one `candrows`-arm row today (S495; `grep -l candrows`).
Per learnings §3 every check needs a failing-direction witness; none is
promised. Add one per check (delete the last row of a slot; initialise a row with
another slot's `u` member; add a `strcmp(sel->row->c.name, "exact")`; omit `.slot`).

### m4. emit_sweep's floors are stale and sit far below current reach

`emit_sweep.py:185-187` floors are 3,480 against a 3,938-row population
(`argv_population_floor` 3,900). `--list-source` now yields 4,606 pattern rows
(3,595 distinct; 3,221 compile at default). With ~90% compile rate, current reach
is ~4,100 and the floor leaves ~600 patterns (15%) of silent loss. Composition
floors (`composition_producing_floor` 32, zero slack by its own comment) read 38
producing / 108 artifacts now, so six files/20 artifacts of slack where the file
says zero. Re-pin before using the script as a refactor gate, or the "reach at the
script's pinned floors" clause (start_table.md:529) is weaker than it reads.

### m5. Argv streams drop each pattern's own flags, encoding and engine

`list_source_patterns` keeps only column 5 (`emit_sweep.py:366-381`). Measured over
the 4,606 pattern rows: 132 carry `flags` (120 `i`, 12 `u`), 635 declare
`encoding utf8` (201 `byte`), 131 declare `engine vm`. Streams 1-3 compile all of
them as plain default patterns; only stream 4 (38 producing files) honours per-target
options. C0 fixes the utf8 half globally (`-e utf8`), which is a different
population from "the 635 that asked for it". There is no `-i` arm at all, and
caseless is its own start population (`-fno-req-run-fold` moves 48 artifacts).
Cheap to add: `--extra -i`.

### m6. `--emit-facts` as the new stream: what it can and cannot see

Measured over the 3,221 compiling patterns, the `used` column is `yes` on 100%
for `kinds`, `nullable`, `start_set`, `end_window`, `req_run`, `req_byte`
(not sensitive to ANY eager evaluation of a predicate that reads only those), and
varies for `start_anchor` (no 1,531), `req_set` (no 2,894), `req_whole_run` (no
2,664), `req_run_maxoff` (no 3,018), `kset_walk` (no 1,063), `run_pin` (no 2,621).
So `used` is a coarse per-fact bit: it catches an eagerly evaluated predicate
that reads one of those six, and nothing else (no order, no count). The
"decisions" section of the listing is "read off the emitted C" (its own header),
so it adds nothing beyond the `.c` bytes. §3.3 item 3's "the one observable of
WHICH predicates a walk evaluated" is overstated; say which six facts and name the
rows whose predicates read them (P4 -> `req_set`, N1-N4 -> `kset_walk`/`run_pin`,
B3/B4/R3/P2 -> `start_anchor`). `--emit-facts=byte,utf8` already compiles both
encodings in one invocation, so the utf8 arm of this stream needs no `--extra`.

### m7. No injection path for constructed witnesses

§3.4 says an UNPROVEN-BY-SWEEP row "needs its constructed witness run
explicitly". `emit_sweep.py` has no `--pattern`/`--patterns-file` argument
(`add_argument` list, lines 665-688); the corpus is `tests/**/*.rxt` of the
working tree only, and ref and working trees can differ in corpus. A constructed
witness not committed under `tests/` is not swept. Add the option (list of
`PATTERN` with per-line `--extra`), or require that every named witness is a
committed `.rxt` cell first so the sweep sees it.

### m8. `registry.md` §6¶4

The spec says the listing is "live off the SAME arrays `src/gen/emit_dfa.c`'s own
`dfa_select` walks". C3 deletes `dfa_select`/`dfa_pfs[]`. §3 says "no spec sentence
about an artifact moves", true, but this one is about an internal and goes stale
at C3, so the "spec hunk in the same change" rule (D80) applies earlier than C7.

## NOTE

- The reference-side independence claim in §3.3 ("PARENT binary from `git archive`,
  shares no source") holds. The weaker links are the ones above: the trace's key and
  print site (M3), the census's literal-value reads (H1), and stamp-sharing rows.
- `used`/stamp equality cannot distinguish two rows that emit the same bytes AND
  the same stamp. By inventory none do: P1/P2/P3 stamp differently, B3/B4 stamp
  `anchored`/`gstart`, R1/R3 stamp `exact`/`anchored`. So where a row is populated
  the byte sweep discriminates; the residual risk is population, not identity of
  emission. M4 is the list of where population is thin or absent.
- C0's `--extra` for `-fno-*` bits at 8 to 604 deltas gives a ready, independent
  floor per arm; recommend pinning them as exact-count manifests naming the rows
  they exercise, not as a single floor (learnings §3 "exact counts disarm
  themselves; manifest naming irreplaceable rows").
- `-fno-end-window` at utf8 reads 0 (correct: W1 declines non-boundary encodings;
  the note says so). Keep it as a asserted zero.
