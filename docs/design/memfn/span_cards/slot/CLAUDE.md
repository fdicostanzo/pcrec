# docs/design/memfn/span_cards/slot/ — the stage-2 SLOT HARNESS (span_cards.md §3.2-§3.7, unit S2c)

The producer of `zen4-grid3`'s cells: one window's timing jobs (J1-J5, J2p), their dry runs, the slot's own
estimator and the RUN RECORD. Evidence for one run, never built or run by pcrec's make; retired when M3's driver
implements `docs/spec/measures.md` §3.4-§3.5. Writes only under a RUNDIR the caller names (scratch).
Timing (`run.py run`, `run.py screen`) only in a window main clears with Frank, never 19:00-01:00.
Review r9 (`docs/dev/reviews/2026-11-06-r9-memfn-s2c.md`) rules the shape: the thing TIMED is the thing GATED,
KEYED and RECORDED (span_cards §R1.3's r9 table).

## Files

- `plan.py` — the plan: every job's arms (keys, groups, lengths, events, bases), the floor's clauses and the
  unreached pairs, from `../../span_pick/census0.out`, `vcls.out`, `enter/fixtures.tsv`, the ver-3 and ver-4 cards
  (`memfn/data/cards/kit-grid.tsv`) and the kit policy table (`memfn/data/policy.tsv`); `key_form`, `base_of`,
  `shape_majority`; `plan.py report | groups JOB | freeze OUT`. `[K38-3]` The producer plans a SET of card vers (`METHOD_VERS` 3, 4), each
  card read at its own ver; kit-grid@4's `enter_back` (dim `back`, t in `BACK_STEPS`) is its OWN job and group `J5B` `[k383 F1]` (not J5's: `dry J5` keeps its 16 arms), UNMEASURED and UNSCHEDULED (no window job runs it; `record.JOBS`/`common.sh` omit it; est.py's selftest skips jobs outside `record.JOBS`); `check_card_dims`
  (build time) refuses a planned-ver card dim with no `DIM_FIELD` line. Env `SLOT_TREE`: the tree when slot/ runs from a copy.
  [lane slotx] ver 6 planned too: `card_of` (a key's card: its quantity's card whose deps name its form token;
  find_byte/find_hit have cards at 3 and 6), jobs JMB (find_byte@6) and JMH (find_hit@6's sweep `GAPS6` x reject
  percent, dim `reject`), mfind-w64 listed OWED (`UNPLANNED6`); every row key held to its card's dims at build time.
- `vcls.py`, `vcls.out` — the verify-class census (T-CMP / T-SETTEST classes of the S2b corpus's row-1 sites):
  settest c1/c2/cn by compare count, rc-words w1/w2/w3 by word count, rc-memcmp l1; c2's `shape`
  lines by gcc's lowering (`alu1`: one ALU op + one compare, a single-bit pair, an inner range or `[^x]` (S2e, FIX-5); `cmp2`:
  two compares); the header stamps the sweep's sha-256 and commit. R-38 Part D D3: cn is 3-7 compares, cn+ above
  (UNMEASURED: plan.py's `UNPLANNED` lists it and never schedules it, nor `every-pos`); derived run parts' records
  join the population through census0's parser (`runpart_pop`).
- `slot.h`, `gen.c`, `drv.c` — the arm table, the seeded subject generator (hits, candidates, [slotx] a find site's
  check run after each hit and `reject` percent of hits failing it; the gate's
  expected count/position sum/FNV-1a-64, the sentinel subject) and the driver (`gate`: `_gate` and `_time` on
  every subject and sentinel, the population line, [slotx] a `reject` line per landed find arm read off the
  bytes; `addr`; `round R NFILE`, its ACC checked against the planted
  counts; `check`: the round's loop over every subject once, the dry run's, r9fc FIX-6). `-DCAND_STRIDE`/`-DPOOL_BYTES`
  come from plan.py.
- `link.py` — renders each arm's TU (`[rev1.4 R14-1]` a null base from its class arm's own text, the compare
  removed; the NULL-BASE check) from `arm_fixtures --site-parts` for the (form, cls) its KEY names
  (KEY-ARM MISMATCH otherwise), the cell-text check against that instance's hash, `cell_text.tsv` (instance
  and fold hashes, the EMIT-3 shape tag), arm and twin, seven launches with seeded pads, the placement
  constraints with the bounded re-draw, linked-text equality, and the fixed `ctl` (refuses other inputs).
  [lane slotx] THE ARM'S TARGET REGION: a TU whose instance's kit target opens a region is compiled inside it as
  pcrec places one (`arm_fixtures --frame`: the family guard first, header lines ahead, region around the TU's
  functions); the target and the features its code uses go to cell_text.tsv (`target`, `target_isa`), and the ISA
  check refuses an object needing a feature outside floor + target, or none of what its target adds. Review
  2026-11-15 r1: the ISA table classifies by ENCODING (the bytes: EVEX = AVX-512, also the mask-register and
  high-register rows; an unpriced VEX/EVEX instruction refuses), and `isa_table_check` holds the table to every
  planned target's `--target-facts` (a feature above the floor with no row refuses). Review r5 (mcfixa): ONE TEXT,
  TWO OBJECTS (`_time` alone; `_gate` from the same file under `-DSLOT_GATE_TU`, linked after the arms), and
  TIMED-SHAPE refuses a `_time` calling a function its own object defines (the site out of line); cell_text's
  `text_bytes` (the timed function's size, reported beside the timing). Review r6 (mcfixb): TIMED-SHAPE's per-form
  callee table `TIMED_CALLEES` (mfind-*: none, fn-memchr: memchr; [j4fix] J4's cell-less null bases keyed `null` by `timed_form`, none), and it refuses any branch through a section
  symbol (`section`/`cold` sites, `_time`'s own cold split) and indirect call/jmp; `link.py shape-selftest SCRATCH`
  holds it to three controls and the critic's plants (S3210-S3213; j4fix's null-base plant S3220).
- `art.py` — whole-artifact arms for J5 (`enter`; refuses a step-back arm, `no_back`, until t's artifact is specified) and J1 (PAIR width substitution): pcrec artifact + one
  wrapper, symbol localization, subjects, python `re` expectations, all cached by their inputs' sha;
  `art.py check RUNDIR`.
- `enter/fixtures.tsv` — J5's fixture per (kind, entry), or `-` with the reason it is unreached.
- `j1/patterns.tsv`, `j1/subjects.py` — J1's two bench patterns (path + sha-256 pin, read at run time) and its
  seeded subject generators (shapes mixed, qs; regimes throughput, short).
- `run.py` — `dry JOB RUNDIR RUN_ID` (frozen plan, ctl, links, placement, the gate and the round check on ctl
  and every launch,
  the job's manifest; no clock), `run JOB RUNDIR RUN_ID` (manifest first, the window facts, quiet-gated with
  the total wait bounded, 7 launches x 7 rounds on the plan's CPU; cells.JOB.tsv under `#run_id`, or J1's
  j1_cells.tsv), `screen RUNDIR RUN_ID` (quiet-gated; J2's unit noise vs the half gate, on J2's manifest; queue
  job `480-kit-s2d-screen`); `[rev1.4 R14-3]` every quiet check logs load1 and the top co-runners (`[r10-REV14-6]` CPU over 0.5 s from /proc), the dry
  run one ungated sample (QUIET-LOG refuses a line without them); [slotx] the gate's REJECT-RATE check (the
  realized rejects against the key's percent). Env: `BQ_JOB`,
  `CODE_COMMIT`, `SLOT_TREE`; art.py also reads `PCREC_BENCH` (the bench checkout, else the sibling).
- `est.py` — the slot's estimator and gates (§3.4-§3.5) over the FINALIZED record and its cells, the card and
  policy values read from the record's pinned rows only (r9fc FIX-1), the format-2 draft writer (SPLIT BY VER: one set per method, ver 3 `zen4-grid3`, ver 4 `zen4-grid4` to `<path>.v4`, [slotx] ver 6
  `zen4-grid6` to `.v6`, each set's rows held to its own cards by `draft_split`; only the WINDOW's jobs' rows priced; none for a ver
  with no timed row; no draft on
  REFUSED; one set per ISA level, [r5] the level from the kit's target facts (`Levels`: floor level or the
  target's own; suffix/class by rule), the guard on link's RECORDED needs (DRAFT-ISA-LEVEL MIXED), the unit row
  repeated in every set (its one exemption), bases and ctl by their rows' sets; every ran job's manifest
  (`cell_text`, `placement` pins), a duplicate cell or cell_text line refused; `rows` prints each row's size;
  the self-test loads every draft with build/pcrec; the cards as declared, r9fc FIX-8), `selftest SCRATCH` (the input cross-checks, a live table edit,
  rev 1.4's sub-resolution branches); `[rev1.4]` delta rows printed `ungated`, the sub-resolution branch
  (measures.md §3.5¶3a; `[r10]` the all-negative rule, r capped at the pinned policy's `r_max_e6`
  (`r_max`: the live row, named, for a record planned before it), the A/A in the branch), `notes` (box-state split, bimodal delta rows); the primitives' one home.
  `[rev1.5 R15-1]` the FUSED-COMPARE fact from every launch executable's timed code (`fused_text` over objdump's
  mnemonics, checked by `fused_bytes` over the bytes; the stems from `obj/tab.c`) and the bound row; `[R15-2]` the
  draft's `# note est_commit` (refused from an uncommitted est or when `TIMED_PATHS` moved since `code_commit`);
  the self-test compiles real timed code for its synthetic J4. `[rev1.5 r11]` (review r11): the executables checked against
  the job's manifest and the record's pin of it (`manifest_check`), the stems from the pinned plan (`plan_stems`, tab.c
  cross-checked), the symbol's range only, EXACTLY ONE subject read and it the compare (`fact_of`; a subject read is
  any operand through a register derived from `%rdi`), VEX/EVEX decoded, a fused null base refused, the bound's value
  max(0, med); the draft's inputs blob-identical at HEAD (`est_inputs`, `est_commit`, `draft_gate`), timed paths by the
  exclusion table `NON_TIMED`; self-test READING_CASES (assembled functions) and GATE_CASES (a scratch git tree).
  [r13 JF-4] the outcome's 4th field: its refusals as data, (cause, the keys it names); a gate FAIL row's `gate_why`.
- `d197_rule.tsv`, `d197_rule.py` — [r5 FIDELITY-4 + R1] D197's DECLARED decision rule for the mfcard window, ONE
  VERDICT PER ISA LEVEL (first-match tables: deciding cells, levels (form each level emits, every differing axis),
  libc_variant, cell/arm/verdict with triggers and the one re-run) and its reader (`rule RUNDIR AVX2RUNDIR [--second
  FIRST FIRSTAVX2] [--confirm C CAVX2]`, `drill [SCRATCH]`: constructed outcomes, constructed provenance, plus end to
  end on est's synth). Review r6: every record must pin both files (record.py), and `provenance` refuses records
  that are not one experiment (windows, run ids, code_commit, plan, kit fold; a confirmation's JMHC cells).
  [r13 JF-4] the `refusal` table reads est's REFUSALS (cause, keys): a refusal naming only find_byte@6 scan rows
  never vetoes a level's verdict (the scan line prints the row `scan unpriced (<est's reason>)`); any other refuses.
- `j1_rule.py` — J1's verdict (a)/(b)/(c) from its cells (m 0.5, k 5), on est.py's primitives.
- `record.py` — the run record's one writer: per-ver `SETS`/`RULES` (ver 3 keeps the `rules` key, others `rules.<ver>`); [slotx]
  `WINDOWS` (a window's job set: `s2d`, `mfcard` = J2 J2p JMB JMH; finalize records `window`), `libc` names any
  GLIBC_TUNABLES and [r5] the memchr variant the process bound (`memchr_variant`, a probe); `window`, `j1`, `ready-j2p`, `finalize` (the CAUSE table; plan,
  floor, cards and policy pinned from the frozen plan with the tables' sha-256; [r6] `window` pins D197's rule
  (`d197_rule_tsv_sha256`, `d197_rule_py_sha256`, `rule_pins`), finalize each ran job's cells file
  (`cells_sha256_<job>`, `cells_pins`; est's read_cells refuses a differing file); `[rev1.4 R14-3]` the `quiet`
  section from the transcript and est's two note keys; `[rev1.5 r11-REV15-1]` `manifest_sha256_<job>` per ran job).
- `sabotage.sh SCRATCH [ROW..]` — the slot-local sabotage rows, planted in scratch copies (each row, its S-id and
  lane in the script's header; jobs: a dry run, `est` self-test, `d197`/`d197e2e` drill, `shape`); DETECTED/MISSED
  per row; the control runs every job the selected rows score on first (review r1 F3).
- `movers.py` — S2e's data-mover census (m0build's method, normalization EMPTY, plus the head-vs-itself pass
  across the two sets); written by S2c, run by S2e.
- `run_record.tsv` (S2d, later) — the run record zen4-grid3's PROVENANCE.md cites by sha-256.

## Subdirectories

- `jobs/` — the S2d window's boxqueue job scripts (own CLAUDE.md).
- `enter/`, `j1/` — fixture data (above).

Maintenance: update this file when files are added/removed or change roles.
