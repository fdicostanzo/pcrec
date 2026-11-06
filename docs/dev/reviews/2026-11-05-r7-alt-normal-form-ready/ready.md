# crit-altnf3 readiness findings (lens: ready)

Subject: frozen `subject_alt_normal_form.md` rev 2 (cited `§`/`L<n>` = its line numbers).
Review tree W = worktrees/crit-altnf3 at 08eef8b4b. All probes `nice -n 19`, scratch `ready/w/`.

## Findings

### RDY-1 (CONFIRMED; severity answer-gate/design; unit 1; effort small text + model row)
**Stage 1's island census cannot be an EQUALITY: the merge itself deletes islands.**
§5 stage 1 U1 table (L865) predicts `RX_VM_ALT_ISLANDS` moves "never"; U4 (L907-910) and
§11 (L1358) call the island census an equality "by the set reading's admission predicate".
The set reading only governs an island built by an ENCLOSING alternation that descends
into the `A_WCLASS` (`vm_isl_words`'s `case A_WCLASS`, emit_vm.c:4091). A bare wide class
whose byte CHILD is itself an alternation is an island today on the VM `-fno-cls-kit`
axis; once stage 1 merges the boxes the child is a single `A_CAT` box, `vm_alt` is never
reached, and the island is gone.
Repro (W/build/pcrec, `--features all -e utf8 --engine=vm -fno-cls-kit`): `a[éÉ]b`
ISLANDS 1, `(?i)aéb` 1, `(?i)é` 1, `(?i)xé+y` 2, `(?i)привет` 5 today. Byte-spelled
control (`-e byte --engine=vm -fno-altcls-merge -fno-altcls-factor`, so altcls cannot
pre-merge the spelling): `a(?:\xc3\xa9|\xc3\x89)b` ISLANDS 1 vs merged `a\xc3[\x89\xa9]b`
0; `x(?:\xc3\xa9|\xc3\x89)+y` 2 vs `x\xc3[\x89\xa9]+y` 0 (rungs 0x4 -> 0x1 as the design
says). So a CORRECT stage-1 build turns U4's equality red, and U1 calls each of these an
unpredicted mover (a failure). The design's own `(?i)xé+y` mover (L925) is one of them.
Also on the default axis the VM count is already 0 (kit-routed), so only the
`-fno-cls-kit` VM axis moves — which U4 names explicitly.
Text fix: U1's island row: "moves iff the class is lowered to its byte tree on that axis,
its unmerged child is an alternation the island admits, and the merge leaves fewer boxes
than `VM_ISL_MIN_BRANCHES` (one box: no alternation left)"; U4: "the island census is
TWO-SIDED against U1's island row (equality on every compile U1 does not list)"; §11 row
"the island's set reading" keeps "no" for the reading but the merge row (L1359) adds
"island losses on bare merged classes (`-fno-cls-kit` VM), a choice cell per D186 with its
VM number". S-i2's census role is unaffected (its island is the enclosing one).

### RDY-2 (CONFIRMED text gap; severity doc/maintenance, can turn S-m red; units 1 and 2b; effort small)
**`<PREFIX>_ALTCLS_MERGES`'s unit is undefined for the owner, at both callers.**
Today the stamp counts alternation RUNS merged (`match_api.md` §6.3.11¶3: "counts of
alternation runs merged into one class"; probed: `x(?:a|b|c)y` MERGES 1,
`x(?:a|b|cd|e|f)y` 2). §5 2b (L1095-1096) says it "counts rule-M FOLDS"; S-m (L1147-1149)
then expects `(?:abx|aby|abz)q` → `ab[xyz]q` to stamp MERGES **1**, but that is TWO folds
(y and z into x). Under "folds" S-m's correct build reads 2 and its sabotage 0: the
witness still fails the sabotage, but its stated correct value is wrong, and `run_altcls_tests.sh`
(:62-68 pin `a(b|c)+d` at 1) is fine only by luck of one fold. `x(?:a|b|cd|e|f)y` under 2b
(e, f fold into `a` across `cd`, row 1) becomes 3 folds / 1 head / 1 alternation — three
answers. Stage 1 is silent on whether the LOWERING's merges count at all: bit 10 is
re-specified to deny them (§11 L1359), `tuning.md` §2.6¶1 names `RX_ALTCLS_MERGES` as that
lever's stamp and `src/dump/axes_dump.c:625-633` reads it as the `altcls-merge` axis's
stamp_macro. If they count, every multi-box utf8 artifact's stamp moves (`\p{Lu}` would
read ~597) and §6.3.11¶3 needs a stage-1 hunk; if not, bit 10 denies an activity no stamp
records (D46: "independently stamped").
Text fix: §5 stage 1 states one choice (recommend: the lowering's merges are NOT counted,
and §2.6¶1/§6.3.11¶3 say the stamp counts code-point-level folds only, the lowering's merge
being observable through `RX_VM_PROGRAM_BYTES`/tables); §5 2b defines MERGES as "alternations
in which rule M folded at least one branch" (keeps today's per-run reading and S-m's 1) or
re-states S-m's value; the §6.3.11¶3 hunk is listed for MERGES as well as FACTORED.

### RDY-3 (CONFIRMED by reading; severity gate-red-on-correct-build; unit 1; effort one clause)
**Gate B0 part 1 requires `dumps` identity, but stage 1 itself moves `--list-axes`.**
B0 part 1 (L831-836) runs `--streams c-default,c-vm,emit-ir,emit-ir-auto,stderr,dumps` with
"identity required". The `dumps` stream compares the seven `--list-*` surfaces whole-file,
`--list-axes` included (`scripts/emit_sweep.py:37-40`, :1462). §11 (L1375-1377) requires
every re-specified bit to carry "its `--list-axes` text ... in the stage that moves it", and
bit 10 is re-specified AT STAGE 1 (L791-793, L1359): `axes_dump.c:629-631` prints "a maximal
run of single-character alternation branches qualifies (runs before either engine is
built)", false once the lowering's merge is under the bit. A correct stage 1 either leaves
that text false (violating §11) or turns B0 red.
Text fix: B0 part 1 adds `--dumps-declared-rows` naming the `altcls-merge` row(s) of
`--list-axes` as the one declared delta (2p already uses this mechanism, L1057-1058).

### RDY-4 (CONFIRMED; severity design/sequencing; cross (1, 2p, 2b); effort text)
**span_pick 1e has NOT landed, and the design mis-describes what 1e edits.**
Fact: at the freeze (08eef8b4b) and at main HEAD 64ab880aa the last span_pick landing is
1d (`39e7b20c5` "Merge lane/memfn-sp1d"; `b04160586` "journal: span_pick 1d landed"); no
subject line names 1e; `memfn/docs/journal.md:3063` gives the order "1a, 1f, 1g, 1b, 1c,
1d, 1e" and `memfn/docs/wake.md:30` says "Cut 1e ... from main" (not started). So every
unit is blocked on an external kit unit (§4.7 L738-741; §9 U1 L1310).
What 1e is (`docs/design/memfn/span_pick.md` L365, L377): KIT tables — T-FRAME, one T-FIND
walk, renderer rows; `compose` `arms[]` and `fd_find`'s text become renderers; its readers
are `rows.tsv`, `row_floors.tsv`, `rows_check.py`, the MFTRACE names; "no MF_SITE_ABI event".
It does not rewrite `emit_dfa.c`'s window walk. §4.7's RDY-9 bullet (L741-745: "1e rewrites
the window walk in `emit_dfa.c`, where most §4.2 reader rows live (`req_handoff_*`,
`pf_window_of`, ...)") is unsupported, so the ordained re-grep at 1e's landing is aimed at
code 1e does not touch. The REAL reason to wait holds: 1e's witness is byte identity plus
REACH EQUALITY base-vs-HEAD (span_pick.md L384-388), which a run-moving pcrec landing in its
window would break; that is a scheduling fence (do not land between 1e's base and its
merge), not a code dependency.
Consequences per unit: stage 1 and 2b move `req_run`/trees → keep "after 1e" (or "not
inside 1e's window", a manager choice). 2p moves no emitted byte (L1029-1030), so the stated
reason does not bind it; it waits only through its stage-1 dependency (L1040).
Text fix: §4.7 first bullet: "1e is a kit unit (span_pick.md §Staging: T-FRAME/T-FIND
renderers, no MF_SITE_ABI event, no `emit_dfa.c` window rewrite); the fence is 1e's
REACH-EQUALITY window: no stage that moves `req_run` or emitted bytes lands between 1e's
base and its landing. The stage-1 brief re-greps §4.2/§2.3 at its OWN base commit." State in
§15's readiness paragraph that 1e had not landed at the freeze.

### RDY-5 (CONFIRMED by reading W; severity design/separability; unit 2b (+2p via the shared module); effort a paragraph)
**2b's adjacency test needs description arms §3.5 schedules for LATER rows, and the
shared module would then move RUNS.**
Row 1 reads `head(m)` "through zero-width nodes ... all present in every match of `m`"
(§3.2 L222-225); the text's own cases need a REPEAT head and a lookaround/atomic
read-through: S-h's control `(?:ab|ax+|ad)` "head `a x` of length 2, passes row 1" (L1144-1146);
row 2's holds `(?=a)ad`, `(?>ad)` (L230). But §3.5's arm table (L487-489) gives REP's head
(`body^m` as an affix) to [REPEAT-RUN] "(later)" and the positive-lookaround arm to
[REQ-LOOKAROUND] "(later)", and today's REP arm keeps NO head: `req.c:650-662` +
`rb_rep_into` (:538) — "At `rmin >= 1` the body's BEST run survives and its head and tail do
NOT". With only today's arms, `ax+`'s head is `a` (h = 1): the control REFUSES (its answer
(0,2) still holds — probed, `(?:ab|ax+|ad)`/`ad` = match 0 2 — so no answer risk, but the
text's mechanism is false). If instead 2b builds a REP head arm in the SHARED module, the
byte-level run walk (a reader of that module once 2p lands, §3.5 L511-516) gains heads
across repeats — `req_run` movers that 2b's "TREE-level, not runs" (L1105) and 2p's "the
single run is derived exactly as before" (L1029-1030) both deny.
Text fix (choose one, state it in §3.5 and §5 2b): (a) 2b's head uses today's arms only
(REP rmin≥1 contributes no head, lookarounds/atomics read as zero-width transparent for the
ADJACENCY head only); re-word S-h's control as "refused at 2b (h = 1), answer (0,2) either
way"; or (b) 2b adds a REP head half and a zero-width read-through as a HEAD-ONLY column the
run reader does not read, stated as such beside WRITES (L525-530), so no run moves.

### RDY-6 (SUSPECTED; severity design (gate unbuildable as spelled); unit 2p; effort text)
**2p does not state the domain or rendering of a piece POSITION, nor its EMPTY arm.**
§3.4 (L435-438) says each width group is "a position-set sequence (a hull per width: a
superset, O1)"; §3.5 (L508-512) calls a byte position "a 256-bit byte set ... which the run
reads as a cube through `pcrec_cube_of` until stage 3". For the 37 mixed-width classes the
independent model must reproduce WHICH: the exact union set, a cube hull, or a cut beyond
`pos_set` 2. They differ on the population (e.g. ι's width-2 group `cd 85 | ce 99 | ce b9`:
second byte {85,99,b9} is not a cube; first byte {cd,ce} hulls to 4 members). `-fno-req-run-fold`
(walk bound 1, `limits.def:411`) is silent too: does it narrow pieces? And the description's
EMPTY arm: §3.5 L484 makes EMPTY the unit (2a), while 2p "keeps today's rules for the single
run (one walk, no parallel copy)" (L1033-1034); one walk cannot both cut at `A_EMPTY` (today,
`req.c:698` → `rb_row_into` → ZERO) and treat it as the unit for the pieces without saying
which the pieces get. The `facts_listing.md` §4.1.2 hunk (L1050-1051) needs the rendering.
Text fix: §5 2p: "a piece position is the exact union SET of its group's bytes at that
offset (D187's form; inert, no member bound; rendered as §4.1.2¶2's set list per position);
bit 44 does not touch pieces (the bound is the run's); EMPTY in a piece is the unit iff 2a
has landed, else a cut, exactly as the single run" — or the cube-hull alternative, stated.

### RDY-7 (CONFIRMED by reading; severity gate missing; unit 2p; effort one line)
**2p claims zero emitted-byte movers but names no instrument that would show one.**
2p refactors the run walk into a reader of the new module (L1031-1034) and declares "the
single run is derived exactly as before, so no pcrec artifact moves" (L1029-1030, L1041-1042:
"no abi event while inert"). Its one gate (L1060-1063) is the piece list vs a model; §5's
preamble gives `make test`/`make test-axes` (ANSWER identity). A run that moves without moving
an answer (a different `RX_REQ_RUN`, pick, table) passes all of them, and would be an
unrecorded abi event. The contract-reader paragraph already presumes emit_sweep's facts and
dumps streams with declared deltas (L1056-1058).
Text fix: 2p Gate adds "B0's instrument (`scripts/emit_sweep.py`, every stream, both
encodings, corpus + the bench list) IDENTICAL except the declared facts row and
`--list-limits` row; any other mover is red".

### RDY-8 (CONFIRMED by grep; severity maintenance/completeness; units 1, 2p, 2b; effort list edits)
**Reader lists are incomplete (D80 / "every reader by grep").**
- Stage 1 re-specifies bit 10 (L791-793) but lists NO reader of it; the readers are the
  same ones 2b lists plus: `src/dump/axes_dump.c:625-633` (`altcls-merge` predicate text and
  stamp_macro — see RDY-3), `lib/pcrec.h:194-229` (bit 10/11 comment), `src/core/axes.def:128`,
  `docs/spec/tuning.md` §2.6¶1-¶4, `tests/axes/run_axes.sh:592-596` (the `-fno-altcls-merge`
  REFUSAL substring table: if U1's "fewer size-cap refusals" fires, the denied arm refuses
  where the stage default answers, with whatever substring the cap prints — a new entry or
  a red axes run), `match_api.md` §6.3.11¶3 (RDY-2), `src/opt/CLAUDE.md:71`, `lib/CLAUDE.md:12`.
- 2b's list (L1101-1104) misses: `src/dump/axes_dump.c:625-641` (both predicate texts:
  "a maximal run sharing a literal first byte qualifies" is false after 2b),
  `tests/registry/run_registry_tests.sh:447-456` (reads the activity-count shape of
  `RX_ALTCLS_MERGES`/`_FACTORED`), `tests/codegen/run_codegen_tests.sh:2893-2920` (the DD-14
  fixture `((?:a|b))(?1)` pinned at `RX_ALTCLS_MERGES 1`), `scripts/alt_census.py:36-39`
  (models "altcls stage 1 merges a run of single-byte alternatives"), `tests/altcls/altcls.rxt`,
  `tests/altcls/CLAUDE.md`, `src/opt/CLAUDE.md`, `cli/CLAUDE.md:17`, and the limits row
  `PCREC_MAX_ALTCLS_FACTOR_DEPTH` (`limits.def:173`, "[OPT-ALTCLS] stage 2: how deep prefix
  factoring may recurse") with its reader `tests/registry/limits_check.sh:114`: THE PROCEDURE
  recurses on P's rests and S's heads (L328-333) and must keep a declared depth bound
  (D10/DD-10, altcls.c:76-89); its text moves (`--list-limits`, a declared dumps row).
- 2p's mech list (L1068-1070) names only S268, but 2p moves the run walk into a module
  reader (L1031-1034); the req.c-anchored rows whose anchor text sits in the functions it
  edits: `S466_alt_width_left.sh` (anchor `RbRuns o; o.maxw = ...` in `rr_alt`, req.c:472-473,
  the same function as S268), `S451_req_hull_keeps_left.sh` and `S456_cube_stores_upper.sh`
  (`rn_common_head`'s hull, which 2p's equal-width ALT hull reuses or duplicates),
  `S1339_req_walk_values_on_stack.sh` (`rb_slots`, the walk's storage), `S465`, `S446`, `S474`
  (rb_walk_at / rep / ranking) if the walk moves files. Text fix: "every
  `SAB_FILE="src/facts/req.c"` row whose `SAB_BEFORE` lies in a function 2p edits or moves
  (grep at 2p's base), REACH re-run" — a grep rule, not a hand list (the CLAUDE.md situation
  index's own lesson).

### RDY-9 (CONFIRMED; severity doc; cross; effort trivial)
Cite drifts and homes, none load-bearing:
- `vm_det_seq` is `emit_vm.c:1883`, not `:1885` (L105). `emit_dfa.c:3214` (L1099) is a
  comment inside `stamp_kinds`' neighbourhood, not an emitter; the emitter is
  `emit_altcls_macros` (`emit_dfa.c:470-471`, called at :15699).
- `kindrow.def` is `src/core/kindrow.def` (the subject writes only `kindrow.def:61`; line holds).
- `pcrec_cube_of` takes a code-point INTERVAL list (`cpset.c:394`), not a 256-bit set; §3.5
  L510-512 ("a 256-bit byte set ... read as a cube through `pcrec_cube_of`") needs "after
  converting the set to intervals" or the right primitive.
- "flag follows caller effect" (L1342-1343) has no decisions.md row; its committed home is
  `docs/dev/reviews/2026-10-29-r3-vmtrail.md` F11 (ruled by Frank). Cite it so a lane can read it.
- `shapes2.py` (U2, L896) lives at `docs/dev/lanes/altthink_evidence/shapes2.py`; give the path.
- [VLOOKBEHIND] "design rev 1 in flight" (L1117) is rev 2 since `4a0fcc859`.

### RDY-10 (SUSPECTED; severity design (termination text); unit 2b; effort one word)
§3.3 P and S (L324-333) act on "maximal runs" without a minimum length. A run of ONE
branch makes P rewrite `K` → `K(?:)` (adds an EMPTY, removes no position occurrence) and
the re-run rule (L334-335) then loops; the termination argument (L341-342: "every rule
strictly lowers the number of position occurrences") holds only for runs of ≥ 2.
Today `altcls_extend_prefix` assumes `n >= 2` (altcls.c:206-208). Text fix: "maximal runs of
at least two branches" in P and S.

## PROBED-AND-HELD

- Base: `git diff --stat` of src/ lib/ cli/ between 7ffbd4deb, 569c57d3a, 82d95943c and
  08eef8b4b is EMPTY, so §2.3's "re-held at 569c57d3a and 82d95943c, no `src/` change" holds.
- altcls.c: `altcls_branch_peel` :180, `altcls_extend_prefix` comment :200 / def :210,
  `altcls_factor_run` :260, `altcls_walk_alt` :312, `case A_LOOK` leaf + body-not-walked
  comment :440-458 (lookahead "no producer, D77" reason as §3.3 says). Pass order
  compile.c:2819 altcls → :2854 callgraph → :2962 lower_enc. Merge counter :353, factor :290.
- lower_enc.c: `u8_box` :236, `u8_ranges` :287, `lower_class_utf8` :327, seal + its
  "REDUNDANT ... abi event" comment :369-384, `if (repl) *slot = repl;` :529, `res = seal;` :383,
  `wclass_of` the one A_WCLASS producer. Note: `u8_box`/`u8_ranges` ALLOCATE `Ast` nodes
  (`u8_seq`), so "exposed for the island predicate" means the island allocates a byte tree per
  wide class it meets; correct, but the build lane should know (no finding: arena, bounded).
- req.c: `rn_hull_mask` :344, `rr_cat` :444, `rr_alt` :470 with the D77 comment :464-469 and
  `o.all = false` :479, `rb_rep_into` :538, `rb_class_into` :549 (`pcrec_cls_cube` :554),
  `rb_row_into` :579/`.text` switch :581, `case A_EMPTY` :698 falling to `rb_row_into`
  (:711-713) with A_BREF/A_VAR/A_CALLOUT — so S-g's "dispatch sends A_BREF to the EMPTY arm"
  is a natural one-line sabotage. `kindrow.def:61` `KIND_ROW(A_EMPTY, ZERO, ...)`.
  `endwin.c:300-301` and `emit_vm.c:4093` are kind tests as stated.
- emit_vm.c: `vm_isl_single` :4011, `vm_isl_words` :4079, `case A_WCLASS: return
  vm_isl_words(v, a->l, ...)` :4091, `vm_cursor_fits` :2042, island count field :568-575.
  cpset.c: `pcrec_wcls_set` :262, `pcrec_cube_of` :394, `pcrec_cls_cube` :424.
- limits.def :410 `PCREC_MIN_REQ_RUN_BITS` 16 ("sum over its positions of popcount(K)"),
  :411 `PCREC_MAX_REQ_RUN_POS_SET` 2 with the ruled two-arm reason — both quoted correctly.
- Bits: `lib/pcrec.h` defines 0..54, 56, 57; bit 55 the kit's (:1196) → 58 used, 6 free.
  Bits 10/11 :228-229, 44 :1085 ("FACT-LEVEL deny"); axes.def :128-129, :224.
- tuning.md §2.6 :230 (¶1 "maximal run of single-character alternation branches", ¶2 K45),
  §2.7 :241 (¶1 "share a literal first byte"), §2.20¶2 first decline row "any element that is
  not a one-byte class", §2.27¶5/§2.28¶8 "Facts emptied" lines, §2.39 :872. match_api §6¶17-19
  :1802-1813, §6.3.11¶3 :2896, §11.6¶1 :3957 (fire count/order unspecified, PURE callee answer).
  facts_listing §1¶1 (row set advisory), §4.1.2. run_facts_checks.sh checks 3 (:38) and 4
  (:42, :234-260). facts.def row shape `PF_FACT(ID,name,epoch,kind,deny,owner,depends)`.
- Mech rows exist: S66, S67, S268, S302, S303, S366, S451, S1653, S1638-S1641, S-U3, S-U7,
  S-U8. All `SAB_FILE` rows on lower_enc.c (S302, S303, S-U7, S-U8) and altcls.c (S66) are
  exactly the ones stages 1/2b list.
- 2b reader test files exist (run_altcls_tests.sh, run_altdiff.sh, run_island_tests.sh,
  run_axes.sh, run_form_census.sh, run_specimen_identity.sh).
- B0 spellings: emit_sweep.py has `--ref --streams --extra-base --patterns-file --no-corpus
  --dumps-declared-rows --bases --variant --data`; STREAMS_ALL = c-default, c-vm, emit-ir,
  composition, dumps, facts, emit-ir-auto, stderr (:3004). `--facts-encodings` does not exist
  (the design says the lane adds it if needed). Runnable as spelled except RDY-3.
- U1b instrument: `--emit-ir -e utf8 -fno-cls-kit --engine=vm` compiles `\p{Lu}`, `\p{L}`,
  `\p{Nd}` (rc 0); `\p{Nd}`'s summary reads resume-frames 71 / resume-points 70 = 71 boxes,
  matching the design's 71 → so the listing is a usable box counter.
- Witness baselines (W/build/pcrec, 11 compiles + runs): S-i `x(?:[éà]1|q2|r3)y` ISLANDS 1;
  S-i2 `[éè]` 0 and `[\x{100}-\x{17f}]` 0; `(?i)xé+y` RUNGS 0x4u, 3319 B; S-d
  `(?:ab|a|ad)`, `(?:for|fo|fox)`, `(?:ac|x|xc)` FACTORED 1; S-m `(?:abx|aby|abz)q`
  MERGES 0 / FACTORED 1; S-s `(?:xyr|zr)` FACTORED 0; `(?:xing|ying)` 0/0; K123
  `(?<=[a\x{3b1}])x` on `αx` = match 2 3; S-b `(?i)k` on `e2 84 aa` = match 0 3; S-a `(?i)β`
  on `ce 90` = nomatch; S-h `(?:ab|a(?:x)?|ad)`/`ad` = 0 1; control `(?:ab|ax+|ad)`/`ad` = 0 2.
  Byte-spelled rung control: `x(?:\xc3\xa9|\xc3\x89)+y` 0x4u vs `x\xc3[\x89\xa9]+y` 0x1u.
- snd1.out P0-P4 rows read (libpcre2 and pcrec agree on every non-CERR row; verbs CERR as
  stated, `(*ACCEPT)` requires module 'verbs').
- [VLOOKBEHIND] rev 2 (4a0fcc859): it works in CHARACTERS with a per-branch back-step and a
  range branch per varying branch; it states nothing about altcls entering lookbehind bodies,
  and §3.3's "owner stays out until [VLOOKBEHIND] lands, then a row of its own (equal-width
  rests or the bounded-variable support)" is consistent with it. Nothing in rev 2 changes
  SND-5's text beyond the stale "rev 1" label (RDY-9).
- Goals: §1 ranks G1-G5, each with a comparison and margin; stage 1 serves G1 (B0/U1), G2
  (kinds per regime), G4 (766 via U2), G5 (U3); 2p serves G4's mixed-width clause (fact only);
  2b serves G3 (ledger) under G1 (answer witnesses vs libpcre2) and G2 (choice cells). Order
  respected; the only conflict found is G2's "stage 1 byte emit diff EMPTY" vs RDY-3's dumps delta.

## Per-unit verdicts

Precondition for all three: span_pick unit **1e has NOT landed** (last landed: 1d,
`39e7b20c5`; 1e not started per memfn/docs/wake.md:30). §4.7's fence holds for 1 and 2b
(its stated reason does not, RDY-4); 2p waits through stage 1.

| unit | (a) cites | (b) gates/witnesses can fail | (c) separable | (d) complete | verdict |
|---|---|---|---|---|---|
| 1 | hold (drifts RDY-9) | B0 red on a correct build via dumps (RDY-3); U1/U4 island row red on a correct build (RDY-1); U1b, U2, U3, S-a, S-b, S-i, S-i2, K123 hold | yes, after 1e; nothing from 2a/3 | bit-10 readers, MERGES stamp unit (RDY-2, RDY-8) | READY WITH TEXT FIXES RDY-1, RDY-2, RDY-3, RDY-4, RDY-8 |
| 2p | hold | piece gate unbuildable until the position domain is stated (RDY-6); no byte-identity instrument for its zero-mover claim (RDY-7); S-p a fact witness, stated | yes on stage 1 (seal) + the fence; NOT on 2a only if its EMPTY behaviour is stated (RDY-6); shares the module with 2b (RDY-5) | mech list by grep (RDY-8) | READY WITH TEXT FIXES RDY-5(b-choice), RDY-6, RDY-7, RDY-8 |
| 2b | hold | S-d, S-k, S-w, S-h answer witnesses reach and fail their sabotage; S-m's correct value depends on RDY-2; S-s holds | after 1e and the module; needs REP/lookaround head arms §3.5 defers to later rows unless RDY-5 picks (a) | readers + depth limit (RDY-8); P/S min run (RDY-10) | READY WITH TEXT FIXES RDY-2, RDY-5, RDY-8, RDY-10 |

**Overall: READY WITH LISTED TEXT FIXES** (RDY-1..RDY-10, all text; RDY-1 and RDY-3 are
the two that would otherwise turn a gate red on a correct stage-1 build, RDY-5 is a one-line
design choice for 2b). No unit can START until span_pick 1e lands.
