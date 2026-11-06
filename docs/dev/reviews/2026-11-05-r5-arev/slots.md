# crit-arev lens: slots — every slot of arev's operand record traced to its home

Subject: R/subject_arev.md (arev.md rev 0) and R/subject_roadmap.md (A-REV, §2 hubs, §4, §5), read
against the review tree worktrees/crit-arev (main f15f30f25). Rulings read from
`git show f15f30f25:docs/dev/{decisions,plan}.md` and vlookbehind.md rev 1 at f15f30f25.
Code citations are review-tree paths and line numbers.

## Slot map (the trace this lens was asked for)

| arev §2.1 slot | home the design names | where the fact lives TODAY | verdict |
|---|---|---|---|
| `machine` | per-artifact machine table keyed (site, role) (§2.4) | `Job.rdfa`/`lmdfa` (+ `Job.dfa`/`adfa` for W3's verify), membership bits `CAND_M*` via `cand_path_members` (emit_dfa.c:4916-4925), `DfaForm.d`; lowering = artifact-level swap `revend_choose_form` (compile.c:585-590) | duplicated + misread (SLOT-3, SLOT-4) |
| `repr` | `table`/`structural`; later D161 add.17 tiers | `DfaForm.repr` (axis A object) for table forms; revdet.c admission for W4 | widened against D161 add.17 (SLOT-11) |
| `seed` | RevWalk.seed; §5 also "a POSITION STREAM" | `DfaForm.from` (forward walks; "NULL on the reverse walk", emit_dfa.c:5883-5888); `DfaDir.seed_cond/seed_byte`; the caller's C text (`rewind_position = match_end_position`, :13621-13624, :14315-14316, :14485-14487); `Rev.cur` | second home (SLOT-1); defined twice in arev (SLOT-12) |
| `floor` | RevWalk.floor | `DfaDir.at_bound`, `DfaDir.scan_more`, AND literal `search_from` in `dir_rev_bound_accept` (S74's site) and the stay site's bound (`stay_advance(f, K, f->dir->scan_more)`, kit fact); `Rev.floor` | partly unseen by arev (SLOT-2) |
| `exit` | RevWalk.exit (`farthest`/`first`) + §2.2 hand table | roadmap §4 admission table's kind/exit column (`AUTO GATE/COMMIT/ENUM/TAGGED/EXISTS`); hands = `CT_*` / `CAND_HAND_*` (emit_dfa.c:9881-9906) | second home + new vocabulary (SLOT-6, SLOT-7) |
| `tags` | RevWalk.tags | `DfaForm.accv` + `entry_set/head/dead` — also on FORWARD and ANCHORED forms (`forward_dist` :14158, `anchored_dist` :14658); `Rev.ga/gs/ns/grp/ngrp` | second home (SLOT-1) |
| `dead` | RevWalk.dead | `DfaForm.dead` (+ `emit_reverse_block`'s `dead_skip`); the fact "seed may be dead" = the RECOVER hand WINDOW vs EXISTS (D156 add.4 Q3) | duplicated twice (SLOT-1, SLOT-7) |
| `names` | RevWalk.names | `DfaDir` strings (statev/posv/recv/ind/bind/tbl_hdr/acc_meaning), `DfaForm.lbl`, literal `rewind_position` in `dir_rev_skip`; `Rev.loop` | third home (SLOT-1, SLOT-2) |
| `host` | `inline` / `vm-record` | placement of the caller; W4's records `VK_CONSUME_BACK` etc. | two meanings of `vm-record` (SLOT-8) |
| `charge` | RevWalk.charge on VK_AUTO | `VK_WORK` records (`vm_charge`, emit_vm.c:932); vlookbehind rev 1 §5.5 charges per candidate through `VK_WORK` | second home (SLOT-8) |
| exactness (`erased`, §2.4/§3.1) | recorded with the table entry | `Nfa.erased` (internal.h:2427); A-FACTS end state = THREE P1 facts (superset, START PIN, report shift) | narrowed: start pin missing (SLOT-5) |
| size cap (not a slot) | "own cap; overflow is the row's decline" | own state cap AND a size-cap ladder rung per optional machine (`drop-end-mark`, `drop-landmark-walk`, compile.c:1113-1127, :1402) | unreachable rung (SLOT-9) |

## Findings

### SLOT-1 — RevWalk is a second home for operands `DfaForm` already carries (CONFIRMED; design; M; every reverse walk + forward walks)
- Design §2.1, §3.3 (a), §4.1 S1 ("`emit_reverse_block(RevWalk *)`").
- Today `emit_reverse_block` (emit_dfa.c:13409-13416) takes a `DfaForm` and overrides two of its
  fields: `f.lbl = label; if (dead_skip) f.dead = dead_skip;`. `DfaForm` (emit_dfa.c:5862-5975)
  already holds, per walk: the machine (`d`), the representation (`repr`), the start expression
  (`from`: "the expression the walk STARTS at ... NULL on the reverse walk"), the label stem
  (`lbl`: "the stem its edge labels are named from"), the dead-entry hand (`dead`), the distance tag
  (`accv`, `entry_set`). These are arev's `machine`, `repr`, `seed`, `names`, `dead`, `tags`.
- `accv` is NOT reverse-only: `fwd->accv = "forward_dist"` (:14158) and `tf.accv = "anchored_dist"`
  (:14658). `from` is set on the lmverify form (`av.from = "lmwalk_start"`, :14439).
- So a reverse-only `RevWalk` beside `DfaForm` gives `seed`/`names`/`dead`/`tags` two homes (three
  for names, with `DfaDir`'s strings), split by direction. After S2 the tree would hold `DfaForm`
  (all DFA walks) + `RevWalk` (reverse walks) — still two walk-descriptor records, which is the
  parallel G2 says S1/S2 remove.
- Expected: the operand record IS `DfaForm`, made direction-neutral (add the reverse `seed` and
  `floor`, move the name strings out of `DfaDir` into a `names` operand), with W4's `Rev` fields as
  the `structural` representation's. S1 then also folds `dfa_dir_lmverify` (SLOT-10) and no new
  struct is born.
- Effort: same as S1. Blast radius: S1, S2, R28's meaning.

### SLOT-2 — the floor and the names are also literal C text inside emitter functions, not only `DfaDir` strings (CONFIRMED; maintenance/doc; S; S1, S74)
- Design §1 "The floor and the seed context are frozen strings"; §3.3 "the one sabotage site that
  (a) moves from a string constant into an operand".
- `dir_rev_bound_accept` (emit_dfa.c:9297) prints the
  floor as literal C: `"search_from ? %s_%s_accepts_class(..., %s_%s_byte_class[subject[search_from - 1]]) : ..."`
  (twice, tagged and untagged arms). This is S74's anchor
  (tests/mech/sabotages/S74_reverse_termination_blind.sh: "`subject[search_from - 1]` in the
  emitted reverse loop"). `dir_rev_skip` prints `rewind_position` literally (`" && rewind_position + 1 < subject_length"`).
  The forward/anchored bound uses `range_guard`/`at_bound` strings, so the reverse direction's floor
  has two spellings (strings + function literal).
- For L's floor `max(0, cursor − W)` the context-indexed accept must read `subject[floor − 1]`;
  a floor operand that reaches `at_bound`/`scan_more` but not `dir_rev_bound_accept` reads the
  context below `search_from` instead (WD6's class). arev's §3.3 floor cells and S74 are listed as
  witnesses, so the gate exists; the claim that one string moves is what is wrong: S1 must move
  the floor out of two function bodies too, and S74's anchor re-aims.
- Expected: §1/§3.3 list `dir_rev_bound_accept` and `dir_rev_skip` as sites of `floor`/`names`.

### SLOT-3 — the `machine` slot misreads W2, and a (site, role)-keyed table has no home for D164 add. 4's artifact-level lowering (CONFIRMED; design; M; W1, W2, S3's table)
- Design §1 table W2 "`Job.rdfa`, or the lowered `Job.xrdfa`"; §2.4 "`Job.rdfa`, `Job.xrdfa`,
  `Job.lmdfa` become entries of one per-artifact machine table keyed by (site, role) ... The BUILD
  REQUEST is part of the operand".
- compile.c:585-590 (`revend_choose_form`): on `tagged` the lowered set is SWAPPED into the Job:
  `td = job->dfa; job->dfa = job->xdfa; ...; td = job->rdfa; job->rdfa = job->xrdfa; ...` and adfa
  likewise. `emit_rev_end` reads only `job->rdfa` (emit_dfa.c:14266
  `dfa_form_derive(cx, &job->rdfa, &rus, &dfa_dir_reverse, &rev)`). At emit time `Job.xrdfa` holds
  the UNLOWERED machine and is no walk's machine. `dfa_member_machines` has no `xrdfa` arm.
- D164 add. 4 (decisions.md "one lowering per artifact: where the mark is used by one machine,
  every machine of that artifact uses it"; add. 5 Q3 scopes it to forward, reverse, anchored DFA).
  The lowering is a fact about the whole SET of end-answering machines. A per-entry build request
  (exact / collapsed / lowered) lets W1's and W2's entries differ, which is the mixed artifact the
  B3 panel blocked (r3-b3 S1). It has to be a table-level fact (or the swap stays as a second
  mechanism beside the table).
- §2.4 "`dfa_member_machines` reads the table instead of four bits": the bits name F and A too
  (`CAND_MF`, `CAND_MA`, emit_dfa.c:4920-4923), which a table holding only reverse machines
  cannot serve; and membership is a path fact (`cand_path_members`), not a build fact. Unreachable as written.

### SLOT-4 — a reverse-only machine table is a second machine-identity mechanism beside H-FLAGS's "one builder" (CONFIRMED; design; M; H-FLAGS, R14)
- Design §2.4 ("H-FLAGS's end state ... applied to reverse machines; the step that lands it
  declares H-FLAGS's extension shape for machines"); §4.1 S3 ratchet column "H-FLAGS (R14) declares
  its machine shape here".
- roadmap §2 H-FLAGS already writes the owner (machine building is P5's) and the interim shape "a
  new machine is requested by a row and built by the one builder (r3-B2's X-6, named here)". R14's
  recipe is "0 once its owner and shape are written (§2), else 1"; the hub step is the declaration,
  not S3. S3 declaring a reverse-machine shape is a second declaration of one hub.
- The Job's machines are many: mandatory `dfa`, `rdfa`, `nedfa` (`build_notempty_dfa`,
  compile.c:438), optional `adfa`, the lowered `x*` set, `xprio`, `lmdfa`. W3 itself reads `Job.adfa`
  (the verify, emit_dfa.c:14437-14438). `revend_build_one` builds optional machines only; W1's `rdfa` is
  mandatory and is not built by it. A table for reverse optional machines leaves forward and
  mandatory machines as Job fields: two identity mechanisms, and W3 reads both.
- Expected: either S3 uses H-FLAGS's (all machines) table and the S3 row says R14 is the hub's,
  or §2.4 is deferred to the H-FLAGS step and S3 adds one `Job` field per the interim shape (a
  lookbehind needs an array per site; that is the measured need that would trigger the general
  table, and it should be argued as H-FLAGS's trigger, not A-REV's).

### SLOT-5 — the exactness slot is narrowed to `Nfa.erased`; the START PIN (`\G`) has no slot and no conjunct in `exist` (SUSPECTED; answer; S; S3's `exist`/`gate` rows)
- Design §2.4 ("The realized `Nfa.erased` is recorded with the entry, because the exit rows read
  it"), §3.1 row 1 `exist` "machine built `exact` and `erased == 0`; the branch has no capturing
  group".
- `A_GSTART`'s kind row records no erasure: `KIND_ROW(A_GSTART, ZERO, TRANSPARENT, NONE, 0)`
  (src/core/kindrow.def:64); the NFA keeps an `N_GSTART` node (src/ir/nfa.c:704). dfa.c:789-800:
  `\G`'s truth "is not a fact about the SUBJECT at all ... decided by an argument" (`startpos`),
  closed only on the START pre-set. nfa.c:1330-1347 (`pcrec_nfa_has_bot`): "the reverse machine
  would need it at its termination boundary" — BOT-family nodes route away from reverse machines
  today. roadmap A-FACTS end state and §4 "two superset facts" (open r3-A5): three facts, the START
  PIN split from the superset.
- Oracle (libpcre2 10.46, R/tools/oracle_probe): `(?<=\Ga{1,3})b` ACCEPT maxlookbehind=3;
  on `aab` [2-3], on `caab` nomatch; `(?<!\Ga{1,3})b` on `aab` nomatch, on `caab` [3-4].
- This body varies (lo 1 < hi 3), has no capture, no backreference/variable, and `erased == 0`, so
  §3.1's `exist` admits it. A reverse table machine has no operand for `startpos`, so it either
  passes `N_GSTART` unconditionally (a superset that `exist` treats as exact: false match on `caab`)
  or never passes it (a SUBSET machine: `gate`'s "no accept ⇒ decided" is then UNSOUND — `aab`
  loses (2,3)). Either way the record lacks the fact. §3.1's "a superset machine's NO accept is
  always sound" holds only if the machine is a superset, which `erased` does not record for `\G`.
- To confirm: a reverse build of `\Ga{1,3}` (pcrec_build_min_dfa reverse, the lookbehind body) and
  its accept on `caab`/`aab` at cursor 3/2 (needs the build; the client is refused today).
- Expected: the exit rows read A-FACTS' three facts (or decline on `pcrec_nfa_has_bot`-family
  nodes: `\G`, `^`/`\A`, absent-prev contexts) and the record carries the start pin as an operand
  or a decline. Roadmap §4 row 12 (captureless regular lookaround) carries r3-A5 open for exactly this.

### SLOT-6 — the exit slot already has a home: roadmap §4's admission table kind/exit column, row 12 (CONFIRMED; design/doc; S; S3, A-ISL)
- Design §2.1 `exit`, §2.2, §3.1 (three lookbehind-specific EXIT ROWS `exist`/`gate`/`commit`).
- roadmap §4 (subject_roadmap.md :641-647) spells the manifesto's exits as record-kind SUFFIXES:
  `AUTO GATE` (rows G, 7), `AUTO COMMIT` (2, 3, 4), `AUTO ENUM` (8, 9; A-ISL's end state),
  `AUTO TAGGED`/`AUTO EXISTS` (row 12, "captureless regular lookaround as a predicate", "BUILT at
  the edge (D164); NEW elsewhere", open r3-A5). The lookbehind `exist` row IS row 12 in a new
  context; `gate` is `AUTO GATE`; `commit` is `AUTO COMMIT`.
- arev moves the exit to an operand and says enumerate is "the HOST's loop" (§2.2), while A-ISL's
  end state is a RECORD `AUTO ENUM`. Two homes for one fact across two areas, and arev cites
  neither §4 nor row 12, so row 12's admission rule (D27 witnesses + sweep + its open r3-A5) is not
  attached to `exist`.
- Expected: arev states the mapping (operand `exit` ⇔ §4's suffix), rules which spelling is the
  home (one), admits `exist` as row 12 with its open findings, and says how A-ISL's `AUTO ENUM`
  relates to "enumerate is a host loop".

### SLOT-7 — §2.2's hand types respell the existing hand vocabulary; `exist` collides with `CAND_HAND_EXISTS`; `dead` restates the RECOVER hand (CONFIRMED; maintenance; S; R12)
- Design §2.2 hands "exact point", "candidate, re-enterable", "candidate or no match", "exact yes /
  no", "exact point plus the tag value"; §5 "FINISH's hand types (AT, LOWER, NOMATCH, SPAN) are the
  kind's hand types; no new vocabulary" — the two sections disagree.
- Home today: emit_dfa.c:9881-9906, the `CT_*` masks and their aliases `AT`, `NOMATCH`, `SPAN`,
  `ENDSET`, `LOWER`, `WINDOW`, `EXISTS`. §5's list omits `ENDSET` (W2's tie hand today is the
  `tags` exit arev describes), `WINDOW` (W2's speculative seed) and `EXISTS` (W1's live seed; "an
  end some match has"). arev's `exist` exit row name is a different meaning under the same word.
- `dead` (§2.1: NULL for W1, `continue;` for W2) is decided by whether the seed may be dead, which
  is the RECOVER hand the walk receives (WINDOW vs EXISTS; D156 add. 4 Q3 "RECOVER asks carry a
  HAND"). The ACTION is the host's; the FACT already has a home.
- Ratchet: R12 counts "vocabularies among the `CT_*` masks and the asker enum, minus 1"; a built §2.2
  vocabulary is a third, R12 +1 at S3, which S3's "ratchet 0" does not count.
- Expected: §2.2's column re-spelled in `CT_*` terms (adding a mask only where none fits, e.g. a
  yes/no verdict that is not a search NOMATCH), and the `exist` row renamed or tied to row 12.

### SLOT-8 — `host = vm-record` has two meanings, and `charge` duplicates `VK_WORK` (CONFIRMED; design; S; W4, S3, G4)
- Design §2.1 `host`, `charge`; §2.3 `VK_AUTO`; §3.2 S2 ("only their describing struct changes");
  G4 ("every instance prints its operands in `--emit-ir`").
- W4's walk is MANY records (`VK_CONSUME_BACK`, `VK_BRANCH`, `VK_LSET`) built by `vm_rev_emit`
  from `Rev` (emit_vm.c:5490-5500, 5521); after S2 a `RevWalk` is a builder-side argument and
  never a record field. L's walk is ONE `VK_AUTO` record whose operand is the `RevWalk`. So the
  seam document (principle 9; D182 (c) ruling 3: "every analysed operand is printed by its renderer
  or carried as a record field") exists only for L; W1-W3 (inline) and W4 never serialize it, and
  G4 is unmeasurable for four of five instance kinds as written.
- The VM's work charge is a record kind, `VK_WORK` (vm_stmt.h:57), written by `vm_charge`
  (emit_vm.c:932); vlookbehind rev 1 §5.5 charges `range`'s candidates through `VK_WORK` with a
  slot amount. A `charge` operand rendered by `VK_AUTO` is a second home for the charge; composing
  `VK_WORK` + `VK_AUTO` keeps one.
- Expected: `host` split into placement (inline / file-scope function) and container (a record or
  not), and `charge` dropped from the record in favour of a `VK_WORK` record beside it.

### SLOT-9 — the size cap has two homes per optional machine today; the design names one, so S3's rung is unreachable or undeclared (CONFIRMED; design; S; H-LADDER, R11, R13)
- Design §2.4 "own cap; overflow and subset budget restored; an overflow is the row's decline".
- Each optional machine row today has its state cap (`revend_build_one`) AND a size-cap ladder
  rung: `drop-end-mark` (`fit_end_mark_applies`, compile.c:1113-1117), `drop-landmark-walk`
  (`fit_lmwalk_applies`, :1120-1127; `fit_rungs[]` :1402; D184 "It is also a size-cap rung").
- S3 adds per-site table machines (tables and accessors at file scope) to VM artifacts. Under an
  emitted-size cap (`--max-emit-code-bytes`) either (a) a new `drop-lookbehind-dfa` rung appears:
  H-LADDER's interim shape (rung, `FitAct`, verb, legal pairs, `COMPILE_MAX_ATTEMPTS` term, driver
  case, note) and a `*_dropped` spelling (R11), none in §4.1 S3; or (b) no rung, and an artifact
  `range` would fit is REFUSED because of an optional optimization (D158: optimizations never reduce
  a pattern's ability to complete).
- Expected: the machine-table entry carries H-LADDER's end-state `droppable` field, and S3's
  ratchet column counts the rung.

### SLOT-10 — R28's population is narrowed: `dfa_dir_lmverify` is the forward copy of the same kind; the inventory baseline omits R28 (CONFIRMED; maintenance; S; R28, §5 totals)
- Design §4.3 R28 "`static const DfaDir` objects ... whose `reverse` member is `true`, minus 1".
- emit_dfa.c:9433-9476: the comment over both says `landmark` is the reverse object's strings
  "character for character under its own name" and `lmverify` is "the anchored object's strings,
  its own name ... no range guard ... its dead entry leaving the verify's one-pass block". Diffing
  `dfa_dir_lmverify` against `dfa_dir_anchored` (:9412): names, indentation, `tbl_hdr`,
  `acc_meaning`, `range_guard` NULL, `dead_entry` `"break;"` — i.e. exactly arev's `names` and
  `dead` operands. Same p1build, same cause (W3 opens its own C block). R28 counts 1 (reverse,
  landmark); the found member lmverify is not counted, and S1 (which opens W3, where lmverify is
  used) would leave it.
- Per roadmap §8 item 2 "a new parallel mechanism not in the list is a review finding that adds a
  row". Proposed recipe: "`static const DfaDir` objects in `src/gen/emit_dfa.c` minus the number of
  distinct directions (forward, reverse, anchored = 3)": 2 at base, 0 after an S1 that folds both.
- Baseline: R28's member existed at p1build's merge, so §5's "At p1build's merge as it stands: 29"
  and the ratchet log's total 44 (2026-11-03) under-count by 1 (by 2 with lmverify). arev §4.3 gives
  the row's count but restates no total; the manager's §5 restatement needs the new totals.

### SLOT-11 — `repr` widened against D161 add. 17: the tiers are ADMISSION rows, not representations (CONFIRMED; design; S; §5 "Representation rows")
- Design §5 "Representation rows, three candidates (table, structural, [LANDWALK-FOLD]'s constant
  walks) ... unification proposed as one representation axis of the kind; D161 add. 17's tiers
  (fixed k, one class run, a chain of runs, general reverse DFA) are its rows by prefix shape".
- D161 add. 17 (decisions.md:9578-9584), the manager's consequences recorded with the ruling:
  "revwalk's tiers T1-T3 are an ADMISSION table (when a landmark-seeded walk is exact ...), not
  mechanisms"; "the REVERSE DFA seeded at the landmark is the SCAFFOLDING, the one general
  mechanism; SCAN EDGES are the optimization inside it"; "Today's cases where a specialised method
  REPLACES the reverse DFA are candidates to fold under it". The walk's fast runs are the kit's
  (D146/D157: pcrec states facts, the kit chooses forms).
- Making "one class run" / "fixed k" pcrec-side representation rows re-creates the specialised
  replacements the ruling folds UNDER the DFA, and has pcrec choose what is the kit's method.
  `structural` (W4) stands as a representation (a different construction, hosted as VM records);
  the constant walks and the tiers do not.
- Expected: §5 drops the tiers from `repr` and lists them as admission facts; [LANDWALK-FOLD]'s
  constant walks are "fold under the table walk" candidates per the ruling.

### SLOT-12 — the `seed` slot is defined twice in arev, and enumeration has two proposed homes (CONFIRMED; doc; S)
- §2.1: `seed` = "the position expression the walk starts at". §2.2: enumeration by a moving seed
  is "the HOST's loop". §5: "the `seed` operand is a POSITION STREAM (a list, a FIND record's
  output, or the previous walk's result)".
- If the seed is a stream, the host loop over seeds moves INTO the record (W2's seed loop, W3's
  LMHIT loop); if it is an expression, §5's unification is the host's. These are different
  records (one serializes a stream source, the other a position). Pick one; SLOT-6's `AUTO ENUM`
  question is the same choice for the exit.

### SLOT-13 — §2.1/§2.2 put a `distance` tag on W1's reverse walk; the tag is on W1's FORWARD form (CONFIRMED; doc; S)
- §2.1 `tags` W1 "none / distance"; §2.2 "W1/W2 under D164 B3 (`distance`)".
- emit_dfa.c:13621-13629: RECOVER's reverse walk is emitted with no `accv`; after it,
  `if (fwd->accv) ... match_end_position -= (size_t)__builtin_ctz(%s);` reads the FORWARD form's
  tag. `rev->accv = "revend_dist"` is set only in `emit_rev_end_tagged` (:14090). W1's reverse walk
  carries no tag; the W1 cell is "none". (It reinforces SLOT-1: the tag is a form fact of forward
  walks.)

### SLOT-14 — the L column differs from the client in force (vlookbehind rev 1), and [LB-EXIST] is filed (CONFIRMED; doc/design; S; S3)
- arev §3.1 splits `reverse-dfa` into `exist` / `gate` / `commit` (HELD). vlookbehind rev 1 §5.4
  (f15f30f25) has ONE row whose non-exact exit is "candidates farthest first, each confirmed by
  §5.1's step" — arev's HELD `commit`, not `gate`. Rev 1's admission also carries "no
  side-effecting construct" (kept as a fact, `[r3 F14]`), absent from arev's §3.1 conjuncts. Rev 1
  §3 (row "start of subject") floors the walk at 0; arev floors at `max(0, cursor − W)`.
- arev §5: "The HELD row is NOT yet filed"; plan.md at f15f30f25 has `- [LB-EXIST] STATE:not-started`
  (filed 2026-11-05 by lane vlbrev1), naming "reverse-dfa's existence exit" as one form.
- Expected: arev re-reads rev 1 and either adopts its exit/floor/conjuncts or says why it differs
  (a client-row change is vlookbehind's to make).

### SLOT-15 — ratchet rows R03 (restated) and R10 count NAMES, the defect the ratchet log already fixed in R21/R22/R24 (CONFIRMED; maintenance; S; §5)
- Design §4.3: R03 restated "`} Rev;` ... in `src/gen/emit_vm.c` present: 1, else 0" (present at
  emit_vm.c:5500, so 1 at base: countable); R10 unchanged "`emit_landmark_walk` present: 1".
- roadmap §5 restated R21 because the old recipe "counted the two choosers' definitions, which 1d
  keeps ... so it read 1 forever", R22 because it "could not see a renamed survivor such as
  `kit_mass`", R24 likewise. Same defect here: S2 can rename `Rev` to anything (0 without deleting
  a parallel description), and S4 (the walk's body as records) may keep a function named
  `emit_landmark_walk` as the record builder (1 forever) or rename it (0 with the hand-written
  loop intact).
- R03's MEMBER also narrows: it was "X3 revdet's own reverse walk" (a mechanism); restated it
  counts the record while `vm_rev_emit` stays (§3.2: "It does NOT delete a renderer"). If the end
  state keeps two representations, the member was never parallel and R03 should be RETIRED by
  owner ruling (owner question 2), not restated so that S2 can be credited with its deletion.
- Expected recipes by what the member DOES: R03 = struct types in `src/gen/` whose fields describe
  a reverse walk's cursor/floor/fail target other than the one operand record, minus 0; R10 = raw
  C-text writes (`pcrec_sb_puts`/`printf` of loop control) in the landmark walk's body, 1 while any.

### SLOT-16 — S3's "ratchet 0 (an instance)" does not count the rows it can raise (SUSPECTED; maintenance; S; §5)
- Design §4.1 S3 ratchet "0 (an instance)"; §3.1 "Its ratchet movement is ZERO by construction".
- Rows S3 plausibly raises, none counted: R12 (SLOT-7's vocabulary), R11/R13 (SLOT-9's rung and
  its `*_dropped`), R19 (the exit rows' admission is a first-match conjunct table; every such table
  so far has its own private conjunct struct: `lmwalk_conj[]`, `RevendFormRow`, `CoverConj`,
  `CompConj` — R19 counts them; a lookbehind exit-row struct is the fifth unless built on
  [ROWCONJ]'s one type), and an H-HEADER growth (SLOT-17). The §0 RATCHET rule rejects a step that
  adds a member without deleting one.
- To confirm: S3's lane re-counts R11, R12, R19 at its head; the design should state which shape
  it uses for each.

### SLOT-17 — the shared record needs a header the design does not name (CONFIRMED; doc; S; H-HEADER)
- `DfaForm`/`DfaDir` are file-local to emit_dfa.c (:5787, :5862); `Rev` is file-local to emit_vm.c
  (:5490). A `RevWalk` read by both, and a machine table in `Job`, land in `internal.h` by default;
  roadmap H-HEADER says each area's migration moves its own types OUT of the 9,342-line header.
  arev §8 leaves "the record's C names and field layout" to the build lane but not its header;
  naming the part header (P3 back end / P6 seam) is the H-HEADER ride-along.

## D-rows arev relies on: what they say, and the consequence here

| D-row | what it says (f15f30f25) | arev's use | holds? consequence |
|---|---|---|---|
| D142 | item 3: under PCRE2_UTF libpcre2 clips backward reads at startpos − LB; pcrec reads real bytes; a STATED divergence, 4 pinned cells/config | G1 "0 differences outside D142's ruled class" | holds. Consequence: L's floor `max(0, cursor − W)` reads `subject[floor − 1]` (S74) below startpos − LB; the differential's expected-divergent subset must include lookbehind-at-cursor cells under UTF, not only `\b`. |
| D151 (+add. 4-7) | rev-inner = one reverse-walk candidate row; HELD; floor = previous verified occurrence + 1 (add. 6 F3) | §5 "rev-inner ... S1 removes the naming obstacle" | holds (emit_reverse_block's comment names it). Consequence: rev-inner's floor is a moving floor (add. 6 F3) — a third member of §5's moving-floor family, which reaches arev's "unify at the third" threshold. |
| D153 | remodel before optimization rounds | S1/S2 ride-alongs | holds. |
| D156 (+add. 1-4) | LOCATE hands a TYPED result (exact span / end undecided / lower bound / nomatch) to a FINISH first-match table; RECOVER asks carry a HAND (add. 4 Q3); revisit when a locator's output is not one of the typed results | §2.3 finisher contract; §5 "no new vocabulary" | partly: §2.2's yes/no "exist" hand is not a D156 type (the lookbehind walk is an assertion, not a search locator). Either it is D156's "revisit when" event (say so) or the hand is a new `CT_*` mask (SLOT-7). |
| D157 | pcrec→kit carries FACTS only, never presumes the kit's method | §2.1 "Nothing in it names a method of the kit" | holds for the record; strained by §5's tier rows (SLOT-11). |
| D161 add. 17 | reverse DFA = the one scaffolding; scan edges the kit's optimization inside it; tiers are ADMISSION, not mechanisms; the walk's owner perhaps the kit, both directions | §2.1, §5 | §2.1 holds; §5's representation rows contradict (SLOT-11). Owner remark "memfn would implement perhaps both directions" makes the walk's renderer a candidate for the back-end face (manifesto 2026-11-04): `repr` should not be pcrec's only. |
| D164 (+add. 2, 4, 5) | END_MARK; B3 tagged reverse; add. 4 one lowering per artifact; add. 5 Q3 VM keeps `$`; add. 2 client 8 lookahead-as-check = anchored yes/no DFA question | `tags: distance`; W2 machine | add. 4 binds the machine table (SLOT-3); the distance tag is a forward/anchored form fact too (SLOT-1, SLOT-13). add. 2's client 8 is the forward twin of `exist` (Standing Q2). |
| D182 | VM body only by typed records (29 kinds, `vm_kind_rows[]`); (c) rulings: kit windows opaque with declared effects; operands printed or carried as record fields | §2.3 `VK_AUTO` with declared effects | holds for L; W4's `RevWalk` is never a record field (SLOT-8). A new kind is a `vm_kind_rows[]` row: fine. |
| D184 | landmark walk LOCATE row; floored at `search_from`; `lmwalk_conj[]` ten rows; size-cap rung `drop-landmark-walk`; public deny bit 57 | §1 W3 | holds; its rung is the H-LADDER precedent S3 ignores (SLOT-9). |
| D185 | one stream, derived stamps; ratchet; ride-along; per-step go | throughout | holds. |
| D186 | unit vs choice changes; choice = a row with per-regime evidence; losing regime narrows the row | §3.1 "each a D186 choice row with its own evidence" | partly: `exist` vs `gate` is decided by a FACT (recorded exactness), not by regime; only "reverse-dfa vs range" is a choice. Treating `exist`/`gate` as separate choice rows multiplies evidence and test levers (flag follows caller effect) for a fact-determined exit. |
| D27/D76/D77/D80/D94 | spec-first author; abi ritual; build under measurement; spec in same change; readers by grep | §4 | hold. S3's abi event is H-ABI's declared shape. |

## Questions for a pcre2-reader
- None needed: the `\G`-in-lookbehind cells above were answered by the installed library.

## PROBED-AND-HELD
- Every §1 symbol exists in the review tree at the cited role: `struct DfaDir` :5787, `dfa_dir_reverse` :9360, `dfa_dir_landmark` :9442, `dfa_dir_lmverify` :9460, `emit_scan_loop` :13244, `emit_reverse_block` :13409, `emit_landmark_walk` :14398, `emit_rev_end` :14229, `dfa_member_machines` :4916 (four machines), `revend_build_one` compile.c:454, `lmwalk_build` :547 (built only where `lmnfa.erased == 0`, :554), `CAND_ML` internal.h:9285, `NFA_ERASED_*` :2434-2440, `} Rev;` emit_vm.c:5500, `VK_CONSUME_BACK` vm_stmt.h:59 (13 symbols checked).
- W1-W3 share one renderer body: `emit_reverse_block` has exactly three callers (:13625 RECOVER, :14317 rev-end, :14489 landmark), each through `emit_scan_loop`. Held.
- `dfa_dir_landmark` vs `dfa_dir_reverse`: differ only in names, indentation, `tbl_hdr`, `acc_meaning` (field-by-field read of the two initializers). R28's base count 1 is right under its own recipe (2 objects with `reverse == true`).
- R03 restated recipe is countable as written (`} Rev;` present once, 1). R10 countable (function present, 1). Their defect is what they count (SLOT-15), not whether they count.
- H-SITES: the reverse walk's kit sites (STAY via `dir_rev_skip` → `pcrec_memfn_advance_site(DELEG_STAY)`, EDGE via `emit_scan_edge`) are keyed in tests/memfn/site_manifest.tsv by pcrec EMITTER function (`stay_advance,dir_fwd_skip,dir_rev_skip`), so a per-instance emitted function for `VK_AUTO` adds no site row; the floor reaches the kit as a fact (`stay_advance(f, K, f->dir->scan_more)`). No H-SITES event in S1-S3. Held.
- A-KIND: consumer kinds (`site_kinds[]`, emit_dfa.c:1418-1429) are keyed on the search entry's PRE/PF/HAT sites; walk-internal STAY/EDGE sites carry none, so a VM-hosted reverse walk raises no R06 question. Held.
- H-ABI: S1, S2, S4 claim 0 movers and no bump; S3 states an abi event with readers by grep (D76/D94). Consistent with H-ABI's declared shape. Held.
- D142, D151, D153, D157 (record level), D182 (new kind as a row), D184, D185 say what arev cites them for (table above; 7 of 12 rows hold fully).
- Oracle: 4 cells on `(?<=\Ga{1,3})b` / `(?<!\Ga{1,3})b` (SLOT-5); the atomic cell in COMMON (`(?<=(?>a|ab)b)x` on `abbx` nomatch) not re-run.

## Standing questions

### (1) Sibling of a family — is the operand record / exit set the third member of something?
Yes, twice, and both should be unified rather than paralleled:
- **Walk descriptors: `DfaForm` (+ `DfaDir`) — `Rev` — proposed `RevWalk`.** `DfaForm` already
  describes every DFA walk (forward search, anchored, lmverify, reverse, landmark) with machine,
  repr, start, label stem, dead hand and tag; `Rev` describes W4. `RevWalk` would be the third
  member and covers only reverse walks. Unify by making `DfaForm` direction-neutral (SLOT-1) and
  giving it a `structural` representation that holds `Rev`'s group sinks. That also folds
  `dfa_dir_lmverify` (SLOT-10).
- **Exits/hands: `CT_*` hand masks (D156) — roadmap §4's `AUTO <exit>` suffixes — arev §2.2's
  hand column.** Three spellings of "what a locator hands on". The `CT_*` masks are the built one
  (start-table and FINISH rows read them); the §4 suffixes are the planned record kinds; arev's is
  the third. Unify on `CT_*` plus the suffix as the rendered kind (SLOT-6, SLOT-7).
- Checked and NOT siblings: LOCATE/FINISH rows (arev correctly makes the walk a LOCATE and the
  finisher a FINISH row; the exit rows `exist`/`gate` are FINISH-like selections and could be
  `cand_rows[]` rows in a lookbehind slot instead of a new table — cheaper than a fifth conjunct
  table, SLOT-16); kit consumer kinds (keyed on search entries, not walks); VM island records
  (A-ISL's `AUTO ENUM` IS a sibling for the enumerate exit: SLOT-6); the skip family (a reverse
  stay is a SKIP inside the walk, already shared through `dir_rev_skip`; not the record).

### (2) General form + unlocks
- **General form: a DIRECTION-NEUTRAL AUTOMATON RUN record** — machine (from H-FLAGS's one table,
  with the artifact's lowering as a table-level fact), direction, seed (a position received with
  its `CT_*` hand), floor/bound, exit (which accept(s), handed on as a `CT_*` hand), tags,
  placement; plus the facts that decide exit soundness (A-FACTS' three: superset, start pin,
  report shift). Reverse is one direction, not the kind.
- Unlocks, each with its trigger:
  - **Forward existence in a VM body** ([LB-EXIST], [ENG-LOOK]'s `Σ*·L`): trigger [LB-EXIST]'s own
    (a real pattern needing unbounded or over-255 lookbehind from [UTF-RW] or a user).
  - **Lookahead-as-check** (D164 add. 2's compound client 8: an anchored yes/no "does Y match from
    e"): the forward twin of `exist`; trigger: client 8 opens (a trailing unbounded lookahead
    pattern reaching the bench).
  - **The anchored verify inside a VM body** ([LANDWALK-VM]/[LANDWALK-FWD]): trigger: [LANDWALK-VM]
    opens (stage 2 of D184).
  - **P-b's reverse `AUTO` record** (roadmap §6): the DFA artifact's top level as records reuses
    the same record; trigger: P-c lands.
  - **A-ISL's `AUTO ENUM`** as the same record with an enumerate exit: trigger: P-g's new example
    (r1-C12).
  - **The machine table for all machines** (H-FLAGS end state): retires per-client `Job` fields and
    the `x*` swap; trigger: the first client needing a variable number of machines — the
    lookbehind (one per branch per site) is that client, so it should be argued at S3 as
    H-FLAGS's trigger (SLOT-4).
