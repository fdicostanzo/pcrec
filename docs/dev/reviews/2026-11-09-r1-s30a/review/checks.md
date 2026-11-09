# checks findings

## Findings

**CHECKS-1 — three of 3.0a's twelve rows (B, C, M; ids S2983, S2984, S2988) are hosted NOWHERE**
CONFIRMED (grep). `git grep -E 'S298[2-9]|S299[0-3]' 6dc54e383` (denylist excluded) finds hosts for S2982 (A, mech),
S2985 (D, decider_census.py in-script), S2986/S2987/S2989/S2991 (K/L/N/P, run_g2_win.sh plants), S2990 (O), S2992 (Q),
S2993 (R) (mech) — and no text at all for S2983, S2984, S2988. plan_frame.md §5 lists B, C, M as 3.0a rows and §5
"Separability" lists B, C, M in commit 2's rows. B and C are said to be "DETECTED by [§R's] message", but nothing
ever plants them, so the invariant's message is never shown to fire on a B/C fault (§R only runs on a clean build;
its regex is never exercised red by any committed plant). M (LIBC admits MASK, read only by §S) likewise has no
plant: §S's cell compare is never shown red by a committed row. Expected: three committed rows (mech scripts with
SAB_SUITES naming the rows suite, or in-script plants in rows_check.py like decider_census's S2985), or the
deviation stated in the design's row list. Severity: maintenance (check coverage); effort S; blast: rows_check.py §R/§S.

**CHECKS-2 — §S keys the pin by search in a dict: a DUPLICATE pin row with wrong cells is silently dropped (green)**
CONFIRMED. tests/memfn/rows_check.py :826 `pmap = {c[0]: c for c in pin}` (and `kmap` likewise for the kit print).
Plant (copy of 6dc54e383, rows_check.py --root copy): insert `LIBC	yes	yes	no	DERIVED	wrong duplicate` ahead of the
real LIBC row in stream_support.tsv. Observed: exit 0, "checks failed: 0", "support pin: 6 rows" (7 data lines read;
the count printed is the dict's size, so the population is not counted). Expected: red ("stream_support.tsv declares
LIBC twice"), as §R already does for renderer_rows.tsv (`len(declared) != len(rr)`). Same blind spot on the kit side
(a twice-printed kit row). Deleted line (WALK) and invented line (V1) plants are red (held). Severity: maintenance
(check hole); effort XS (count keys, fail on dup, print lines read); blast: §S only.

**CHECKS-3 — a RULING row's quote may name ANY tree file, including the pin itself: the control can share its source**
CONFIRMED. rows_check.py :839-852 opens `os.path.join(root, PATH)` for whatever PATH the row names. Plant: the LIBC
and LIBC_BACK rows' `@ memfn/docs/responses.md` rewritten to `@ tests/memfn/stream_support.tsv` (the pin quotes the
sentence, so it "holds" it). Observed: exit 0, checks failed 0. Expected: red — §2.5.2 / R7 make the RULING source
"the owner's text, never the table read twice"; a self-citing pin is exactly a control sharing a source with its
subject (learnings §3). Fix: allowlist the ledger path(s) (memfn/docs/responses.md, docs/dev/decisions.md) in the
script, not in the pin. Invented-sentence plant is red (held). Severity: maintenance; effort XS; blast §S.

**CHECKS-4 — the narrowed backstop misses a true copy of the ONE accessor and a pointer-alias twin; S2985's plant spells an idiom no reader uses**
CONFIRMED. decider_census.py :62-66 LIVE adds `ren_find(` and `ren_<table>[`. But `ren_find` (window.c :1800-1808) walks
`const ren_key *k = ... rows + i * size` and every caller passes `REN_ROWS(ren_X)` — no `ren_X[` anywhere outside the
tables' own definitions. Plants (copy of 6dc54e383, appended to window.c, both pass `gcc -fsyntax-only`; census run
`--root copy --src copy --map tsv --no-plants`):
 (b1) `census_find2`, a byte copy of ren_find's loop under a new name, plus `census_twin_b1(pick){ return
      census_find2(REN_ROWS(ren_search), E_FIND, REN_PICK(pick)); }` -> exit 0, hits 50, outside a member 0 (GREEN);
 (b2) `const ren_search_row *t = ren_search; for (i < RB_N) if (t[i].k.frame == f && (t[i].k.keys & REN_PICK(pick)))`
      -> exit 0, outside 0 (GREEN).
The in-script S2985 plant (:335-351) indexes `ren_search[i]` directly — a spelling the subject never uses — so it
shows the shape list catches its own token, not that a second renderer list is caught (the plant shares its source
with the shape list; learnings §3). Row (D) asks for "a COPY of the one accessor's loop"; the script's own comment
concedes such a copy "would hold no shape". Neither twin "copies the rows under a NEW name" (the census's stated
limit, :38-41): both read the live `ren_search` table. Expected: red. Cheap shapes that would catch both without
live strays: `REN_ROWS(` (every table read goes through it; its users are the members ren_find's callers already
are) and `const ren_key *` / `->keys &`. Severity: maintenance (Goal-3 check hole on the 3.0a tables); effort S
(add shapes, re-pin HITS, re-aim S2985 at b1's text); blast decider_census.py.

**CHECKS-5 — row (B) is not LOUD: an (E-stmt, PAIR) search row with no arm is a SILENT MOVE to E-find B-pair, so §R's refusal message (its declared host) never fires**
CONFIRMED (kit plant 3 of 4; rows_check.py builds the planted kit itself). Plant in a copy of
6dc54e383 window.c: enum `RB_ST_PAIR` before `RB_N` and row `[RB_ST_PAIR] = { { E_STMT, REN_PICK(FF_PAIR), "pf_pair",
NULL }, 0, "", NULL, NULL, NULL, NULL, NULL, "..." }` (no arm). Witness `foo|bar\d` (`-p rx --features all`): clean traced
pcrec FDROUTE `row=R7w ren=pf_walk frame=E-stmt`; planted: rc 0, artifact DIFFERS from base, FDROUTE `row=PAIR ren=B-pair
frame=E-find` (trace: wfE now `chosen=E-find`, T-FIND `chosen=PAIR`). `(?:(?!a)z|w)` SAME. So select_arm's refusal is
not reached: Table E's legacy-first ask sees the composer cannot serve and falls to E-find. rows_check (planted
build/pcrec too) is red only by §R's TRIPLE check ("its witness 'foo|bar\\d' printed FDROUTE triples [('E-find',
'PAIR', 'B-pair')]") plus one unnamed refusal (`(?i)(ab)\1`: "the memfn kit's text calls <string.h> functions the
prologue did not include"); the "REFUSED naming PAIR" message never appears. plan_frame.md §5 (B) and [rev2.2 R11]
("the check asserts the refusal names row PAIR ... DETECTED by that message") is falsified, and no mech arm runs
rows_check, so in the matrix the row would read UNDETECTED (answers unchanged: B-pair is correct). Severity: design
(sabotage row mis-modelled) / maintenance; effort S (re-model B as SILENT-MOVE detected by §R's triple set; host it);
blast plan_frame §5 B, rows_check §R comment :107-110, renderer_rows.tsv :21.

**CHECKS-6 — row (C) is likewise a SILENT MOVE, not "rc != 0 AND names PAIR"; F5's false-branch witness is not what the design says**
CONFIRMED (kit plant 4 of 4). Plant: finder.c :510 `if (r->slot == FD_FIND && !wf_renders(...)) return 0;` replaced by a
comment. `foo|bar\d`: rc 0 (base 0), artifact DIFFERS, FDROUTE moves `E-stmt/R7w/pf_walk` -> `E-find/PAIR/B-pair`;
`(?:(?!a)z|w)` and `(?:(?i:abs)|(?i:ab)S)` SAME. rows_check (planted build/pcrec): exit 1, checks failed 2 — the §R
triple mismatch on `foo|bar\d` and the generic `(?i)(ab)\1` refusal (`<string.h> ... prologue did not include`, no
PAIR named). plan_frame.md §5 (C) "the same refusal as (B) ... (rc != 0 AND it names PAIR) ... stays LOUD only while
select_arm's refusal is kept" does not describe the build: with the gate gone, Table E's legacy-first ask declines
E-stmt and the stop renders as E-find B-pair (a correct, different text). Consequence: the refusal-invariant regex
(rows_check.py :306) has NO committed or measured plant that turns it red for a T-FIND row name — only R's Table S
branch was shown (CHECKS-7). Severity: design/maintenance; effort S; blast plan_frame §5 B/C, §2.4 "unreachable by
construction" reasoning, rows_check §R docstring.

**CHECKS-7 — under (R) the refusal invariant names Table S on only 6 of 19 refused witness compiles; the ask-path refusal drops the kit's text**
CONFIRMED (kit plant 2 of 4: S2993's own SAB_AFTER). rows_check with planted kit and planted build/pcrec: exit 1, 20
failed: §S red ("support row PAIR ... kit's table yes/no/yes", held), 6 lines "REFUSED naming Table S's ST-many refusal"
(incl. the B-pair witness `(?:(?!a)z|w)` and `foo|bar\d`, as §5 (R) requires: held), and 13 refusals reported only as
"does not compile" — e.g. the B-fn witness `(?:(?i:abs)|(?i:ab)S)` and fn/fn-pair `(?i)cat`, whose stderr is
"pcrec: internal error: the memfn kit refuses the start-search site a selection reads (its define would refuse it too)",
with no kit reason. So the invariant's "own message" depends on which pcrec path refuses (define vs ask), not on the
fault; a B/C-style fault surfacing at the ask would never be named. Also: with the PLAIN build/pcrec unplanted (pass 1)
every refusal is unnamed, because the regex reads `rp` (build/pcrec) stderr only (rows_check.py :305) — harmless when
both binaries come from one tree, but worth one line in the docstring. Severity: maintenance (minor); effort S (pcrec
surfaces the kit's why on the ask path too, or the invariant reads the traced binary's REFUSE record); blast §R.

**CHECKS-8 — row (Q) is hosted but measured UNDETECTED, and row (M)'s only detector (§S) is outside the mech matrix**
CONFIRMED by reading (S2992's own record) + plant (M). S2992 (tests/mech/sabotages/S2992_wf_libc_union_two_pieces.sh)
carries SAB_EXPECT=UNDETECTED: no byte moves on `--memfn=no-fd-d1 abcdef`, RX_MEMFN_LIBC `none` both sides, and
arm_fixtures --query's libc reading greps `memchr(`/`memcmp(` only — plan_frame.md §5 (Q)'s "emit_sweep is red ... the
reply-class pin moves" is falsified and the design is not amended. (Q) = SAME. Row (M), planted here (kit plant 1 of 4:
LIBC `WF_ST_RESTART | WF_ST_MASK`): SAME on all 118 traced compiles of rows_check (no "artifact differs"), red ONLY at
§S ("support row LIBC ... yes/yes/no"); with no mech arm running rows_check (S2993's header says so;
run_sabotage_matrix.sh has no rows arm), M, B, C and R's §R/§S halves can never be matrix rows — which is why CHECKS-1's
three ids have no host. Expected: either a `memfnrows` mech arm (run_rows.sh is self-contained, ~3 s here) so B/C/M/Q-
style rows can be hosted and re-run, or the design's row list amended to say which rows are by-hand only. Severity:
maintenance; effort S-M; blast mech matrix, plan_frame §5.

## PROBED-AND-HELD
- **The twelve rows, host / input / reach / class** (class = pcrec rc and bytes vs base on the row's witness):

| row | id | host | failing input / detector | witness reaches site? | class |
|---|---|---|---|---|---|
| A | S2982 | mech, memfnfinder | formhash `pair` instance stops resolving (finder_check.py) | yes (lane-measured; anchor resolves) | SILENT-MOVE (B-pair -> B-walk) |
| B | S2983 | NOWHERE | measured here: `foo|bar\d` moves E-stmt -> E-find B-pair; §R triple red | yes | SILENT-MOVE (CHECKS-5) |
| C | S2984 | NOWHERE | same as B, measured | yes | SILENT-MOVE (CHECKS-6) |
| D | S2985 | decider_census.py in-script plant | backstop stray hits 2 (clean run) | own token only (CHECKS-4) | SAME (census-only) |
| K | S2986 | run_g2_win.sh plant | G2 hors census floor 110 / dense-window control | anchor count 1 at window.c :2033 (wf_support HORS) | SILENT-MOVE (by reading) |
| L | S2987 | run_g2_win.sh plant | G2 answers vs g2_win_ref.c | anchor :2671 in resume_next, shared by both S-restart rows | SILENT-MOVE, wrong answers |
| M | S2988 | NOWHERE | §S only, measured (118 compiles SAME) | n/a | SAME (CHECKS-8) |
| N | S2989 | run_g2_win.sh plant | floor sites refused; G2 no-window-search control | anchor :1956 (RS_GENERIC_RESTART) | LOUD |
| O | S2990 | mech, memfnfinder | presence spans refused | anchor resolves (finder.c :510) | LOUD |
| P | S2991 | run_g2_win.sh plant | gcc compile of every B-pair site fails | anchor :2942 in b_pair_state | pcrec rc 0 / bytes differ; LOUD at gcc |
| Q | S2992 | mech, SAB_EXPECT=UNDETECTED | none | — | SAME (CHECKS-8) |
| R | S2993 | mech, harness | measured here: §S red + 6 named / 13 unnamed refusals | yes (B-pair witness named) | LOUD (CHECKS-7) |

- **G2 re-aims**: S1423, S1427, S1428, S1543 kept VERBATIM (no diff hunk in run_g2_win.sh); a static replay of the
  script's own apply (`s.count(FROM) == 1`) over all 26 PLANTS: every anchor count 1; the four sit in their intended
  functions — S1423 window.c :3011 `d_hors_head`, S1427 :2915 `wf_b_walk` (`wf_member` line), S1428 :2928 `wf_b_pair`
  (`two(...)`), S1543 :2967 `wf_raise` else-branch. New K/L/N/P anchors likewise count 1. (G2 plant runs are by hand,
  `--plants`; not run here — suite.)
- **m6read_check_sab_anchors.py** (review tree, PCREC_TMPDIR=checks/): rc 0, "sabotages checked: 1171 (1214 anchor
  sites) / all anchors resolve" (it reads mech scripts only, not G2's in-script table: covered by the replay above).
- **§S plants (rows_check.py --root copy)**: clean exit 0 (243 passed); DELETED pin line (WALK) red; INVENTED pin line
  (V1) red; pin cell edit (LIBC MASK yes) red; invented RULING sentence red (2 rows); kit-side M red. Duplicate pin row
  GREEN (CHECKS-2); self-cited ledger path GREEN (CHECKS-3). 6 pin plants + 1 kit plant.
- **decider_census.tsv map plants (--no-plants)**: deleted `ren_find` line red (count + stray :1800); deleted `ren_stream`
  red (count + stray :1954); deleted `table_s` red (count + stray :2077); deleted `wf_support` red by MEMBER_COUNT ONLY
  (it holds no shape: a delete + count edit would pass — the census's stated design, a declaration); invented member
  `ren_lookup2` red (count + "not defined"). Clean: hits 50/50, members 61, 83 passed, S2985 plant 2 strays. Bypasses
  (CHECKS-4) GREEN.
- **§R refusal regex** matches both kit texts (compose.c :1077-1078, window.c :2197) — shown red by plant R only.
- Plant builds used: 4 (M, R, B, C), all via rows_check's own kit build in the copy; copy restored (cmp) after each.
