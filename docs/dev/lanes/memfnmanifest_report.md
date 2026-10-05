# memfnmanifest — R-3 part 1 (R4a): the checked site manifest and C17

Lane `memfnmanifest`, kit session, 2026-10-05. Branch `lane/memfnmanifest`,
cut from `lane/memfn-r4a` at eb327ff5. It serves `memfn/docs/requests.md`
R-3 item 1, the site-manifest bullet. Design: integration.md rev 4.6,
§R4.3.4, §8.5, §16, §17.6 and §22, plus D147 addendum 10 (Q54).

**ZERO MOVERS.** No emitter, no `src/` file and no artifact byte changed.
The diff is `tests/memfn/` (new), one Makefile section, one mech arm, three
sabotage rows and the CLAUDE.md entries. `memfn/` is untouched.

## 1. What landed

| file | role |
|---|---|
| `tests/memfn/site_manifest.tsv` | THE MANIFEST: 13 rows, every row `pending` |
| `tests/memfn/search_vocab.tsv` | THE SEARCH-FORM VOCABULARY: 8 lines, 4 classes. C12 has none yet, so it is defined here, in ONE place, for C12 to read when it is born at R4c |
| `tests/memfn/c17_lex.py` | the emitter reader: string literals (adjacent pieces joined, emitter comments dropped), attributed to their file-scope definition |
| `tests/memfn/site_manifest_check.py` | C17: manifest shape, rules 1-4, counts |
| `tests/memfn/run_site_manifest.sh` | entry point. Holds `C17_ROW_FLOOR=13` (K35) |
| `tests/memfn/CLAUDE.md` | the directory's doc |
| `Makefile` | `test-memfn-manifest` added to TEST_SECTIONS, its target, and the phony list |
| `tests/mech/run_sabotage_matrix.sh` | arm `memfnmanifest`: the vocabulary entry and the case |
| `tests/mech/sabotages/S478…S480` | the three witnesses |
| `tests/CLAUDE.md`, `tests/mech/CLAUDE.md`, `docs/dev/lanes/CLAUDE.md` | index entries |

## 2. The manifest, row by row

| site | emitters (spell the form) | op/handoff | budget | step | status | companions |
|---|---|---|---|---|---|---|
| PF | `pf_emit_memchr`, `pf_emit_memchr_bounded`, `pf_emit_bcls`, `pf_emit_bcls_bounded` | FIND/ASSIGN | scan | M2 (R4g) | pending | `pf_comment_memchr`, `pf_emit_ofs`, `pf_emit_ofs_bounded`, `pf_block_ofs` |
| PRE | `emit_req_one_byte` | FIND/ON_MISS | scan | M1 (R4c) | pending | `pcrec_emit_req_byte_check`, `emit_req_run_check`, `emit_req_handoff`, `pcrec_emit_req_run_blocks`, `req_run_tests` |
| OFS | `ofs_test_emit_fn`, `ofs_test_emit_pair` | FIND/RETURN | scan | M1 (R4c) | pending | `ofsk_emit_verify`, `ofsk_emit_params` |
| SETREST | `emit_req_set_rest` | ALL_PRESENT/ON_MISS | scan | M1 (R4c) | pending | `pcrec_emit_req_byte_check` |
| VERIFY | `pcrec_emit_run_compare`, `rc_emit_words`, `rc_emit_bytes`, `pcrec_emit_runcmp_helpers` | VERIFY/BOOL | scan | M1b | pending | `ofsk_emit_verify`, `pcrec_runcmp_prepare` |
| VMRUN | `pcrec_emit_run_compare`, `rc_emit_words`, `rc_emit_bytes`, `pcrec_emit_runcmp_helpers` | VERIFY/BOOL | loop | M1b | pending | `vm_lit`, `vm_isl_emit` |
| STAY | `dir_fwd_skip`, `dir_rev_skip` | SKIP/ADVANCE | loop | M3 (R4h) | pending | — |
| EDGE | `emit_scan_edge` | SKIP/ADVANCE | loop | M3 (R4h) | pending | `scan_test` |
| VMSPAN | `vm_emit_span_scan` | SKIP/ADVANCE | loop | M3 (R4h) | pending | `vm_cursor_rep` |
| MLINE | `emit_attempt` | FIND/ASSIGN | scan | M4 | pending | — |
| N6 | `vm_rev_emit` | MF_VOCAB bump (backward walk, captures in flight) | loop | M6 | pending | `vm_revdet_rep` |
| VMSTRIDE | `vm_emit_span_scan` | MF_VOCAB bump (strided SKIP) | loop | M6 | pending | `vm_cursor_rep` |
| N7 | `defs_bref`, `defs_bref_ci`, `u8_defs_bref`, `u8_defs_bref_ci` | MF_VOCAB bump (run-time-operand mismatch, prefix-count return) | loop | M7 | pending | — |

**How each emitter was located.** I first built `c17_lex.py`, then dumped
every emitted-text literal under `src/gen/` and `src/enc/` with its
enclosing function (2,240 joined literals in 314 definitions). I grepped
that dump for libc search calls and `while (`/`for (` loops, and read every
hit against the function names the design gives (§15.1-§15.7, §16; rev 4.6
names functions, not lines). Per site:

- **PF**: these are the `dfa_pfs[]` rows' emit functions.
  - `memchr[-bounded]` → `pf_emit_memchr[_bounded]`.
  - `byte-class[-bounded]` → `pf_emit_bcls[_bounded]`.
  - `offset-set`/`run-pinned` → `pf_emit_ofs[_bounded]`. These only CALL
    `<p>_ofsskip`, an EXPR around OFS's function (§16), so they are
    companions along with `pf_block_ofs`.
- **PRE**: `pcrec_emit_req_byte_check`'s parts. Only `emit_req_one_byte`
  spells a form (its `memchr(`). The run gate's search is `<p>_reqrun`,
  spelled by `ofs_test_emit_fn` (OFS), and its compare is runcmp's
  (VERIFY). The rest of §16's PRE unit is companions.
- **OFS**: `ofs_test_emit_fn` and `ofs_test_emit_pair`, two `memchr(` each.
  `ofsk_emit_verify` and `ofsk_emit_params` are companions: per-candidate
  one-position tests, T4's shape.
- **SETREST**: `emit_req_set_rest`, N4's k `memchr` passes.
- **VERIFY/VMRUN**: runcmp's row texts are
  - `rc_emit_words` (`%s_w%d(`);
  - `rc_emit_bytes`;
  - `pcrec_emit_run_compare` (`!memcmp(`);
  - `pcrec_emit_runcmp_helpers` (the words row's `%s_w%d(` load helpers).

  The callers are `ofsk_emit_verify` (budget 1) and `vm_lit`/`vm_isl_emit`
  (budget 2, the two VM callers in §16).
- **STAY**: `dir_fwd_skip` and `dir_rev_skip` (§15.7).
- **EDGE**: `emit_scan_edge`'s two `while` lines. The spliced class test is
  `scan_test`.
- **VMSPAN/VMSTRIDE**: `vm_emit_span_scan`, called by `vm_cursor_rep` with
  `stride`. One function serves both rows.
- **MLINE**: `emit_attempt`'s `(?m)^` `memchr(` (§15.7).
- **N6**: `vm_rev_emit`'s backward byte step (`{ %s--; goto … }`). Its
  caller is `vm_revdet_rep`.
- **N7**: the encoding seam's TEXT CONSTANTS, not functions:
  - `enc_byte.c`'s `defs_bref` and `defs_bref_ci`;
  - `enc_utf8.c`'s `u8_defs_bref` and `u8_defs_bref_ci`.

  They are the `$_span_match[_caseless]` definitions (D58/DD-12).

The C12 reading, information only: 9 emitted-text `memchr(` calls, matching
§16's / I5's 9 at 90d396fd. Six are in M1's units, two in PF and one in
MLINE.

## 3. C17's design and its independent control

**Static half (rule 1).** A function under `src/gen/` or `src/enc/` whose
literals match a vocabulary line, with no `pending` row naming it, FAILS.
The vocabulary:

| class | line | recognises |
|---|---|---|
| libc-search | `libc-call` | `memchr`/`memcmp`/`memmem`/`strchr`/… called with the SUBJECT, a format hole, or an appended operand as the first argument. This excludes the prose `memchr()` and `vm_emit_vars_resolve`'s `memcmp(cv->name, …)`, a name lookup |
| table-walk | `walk-stmt` | `while (… T[subject[cur]]) cur++/--;` |
| table-walk | `walk-open` | a `while (` whose condition is completed by a spliced predicate (EDGE, VMSPAN) |
| table-walk | `walk-back` | `{ %s--; goto` — a backward walk's byte step. The forward VM step is `++` and is the engine |
| runcmp | `runcmp-words`, `runcmp-bytes` | word-load compares; per-position constant compares |
| span-compare | `span-index` | `s[at + i]` (Q54's line) |
| span-compare | `span-decode` | `$_decode(s,` — the utf8 caseless per-character compare |

**Dynamic half (rule 2).** It is UNREACHED (K35), and the output says so
rather than reporting 0. It is also a tripwire: once a comment-stripped
`mf_emit_site(` call appears under `src/`, rule 2 FAILS ("no longer
unreachable; build it"). So it cannot stay silently unreached past R4c.

**Rule 3** is printed as VACUOUS at 0 delegated rows and is not counted as
a pass.

**Rule 4** is applied PER EMITTER FUNCTION, not per row: every function a
pending row names must spell at least one form. That is stricter than "the
row spells something", and it is why the emitter column lists spellers only
and the `companions` column was added (§5).

**Counts.** It prints delegated / pending / total against a K35 floor. The
floor is `C17_ROW_FLOOR=13`, a literal in `run_site_manifest.sh` that is
never computed from the TSV.

**The independent controls:**
- The vocabulary names no site and no function. The manifest names no text
  shape.
- Rule 1 catches a form the manifest lacks, and rule 4 catches a listed
  emitter the vocabulary cannot see. Neither file can drift into agreement
  with the other.
- Rule 4 is also the vocabulary's and the lexer's REACH witness
  ([MECH-REACH]). If the reader broke and saw nothing, every pending row
  would go stale (22 FAILs) instead of rule 1 passing quietly.
- Every emitter and companion must still be DEFINED, so a renamed function
  is a FAIL, not a silent drop.

**Stated limit (§R4.3.4).** A search spelled in a shape no vocabulary line
knows escapes the static half.

### Clean-tree output (`bash tests/memfn/run_site_manifest.sh`, the file `make test-memfn-manifest` runs)

```
== C17: the checked site manifest (tests/memfn/site_manifest.tsv) ==
PASS: search vocabulary: 8 lines in 4 classes
static half: 9 files under src/gen/ and src/enc/; 28 forms in 22 functions (libc-search 10, runcmp 6, span-compare 4, table-walk 8)
  (C12 reading, information only until C12 is born at R4c: emitted-text memchr( calls = 9)
manifest: 13 rows -- delegated 0 / pending 13 (K35 floor 13)
PASS: manifest row count 13 >= K35 floor 13
PASS: rule 1 (static half): every one of the 22 functions that spell a form is named by a pending row
UNREACHED: rule 2 (dynamic half): no pcrec source calls mf_emit_site, so the corpus compile pass has no site call to count -- declared UNREACHED (K35), not passed. Site calls counted: 0.
VACUOUS: rule 3 (delegated emitter still spells a form): 0 delegated rows, nothing to check -- not counted as a pass.
PASS: rule 4: defs_bref (pending: N7) spells 1 form(s)
PASS: rule 4: defs_bref_ci (pending: N7) spells 1 form(s)
PASS: rule 4: dir_fwd_skip (pending: STAY) spells 1 form(s)
PASS: rule 4: dir_rev_skip (pending: STAY) spells 1 form(s)
PASS: rule 4: emit_attempt (pending: MLINE) spells 1 form(s)
PASS: rule 4: emit_req_one_byte (pending: PRE) spells 1 form(s)
PASS: rule 4: emit_req_set_rest (pending: SETREST) spells 1 form(s)
PASS: rule 4: emit_scan_edge (pending: EDGE) spells 2 form(s)
PASS: rule 4: ofs_test_emit_fn (pending: OFS) spells 2 form(s)
PASS: rule 4: ofs_test_emit_pair (pending: OFS) spells 2 form(s)
PASS: rule 4: pcrec_emit_run_compare (pending: VERIFY,VMRUN) spells 1 form(s)
PASS: rule 4: pcrec_emit_runcmp_helpers (pending: VERIFY,VMRUN) spells 1 form(s)
PASS: rule 4: pf_emit_bcls (pending: PF) spells 1 form(s)
PASS: rule 4: pf_emit_bcls_bounded (pending: PF) spells 1 form(s)
PASS: rule 4: pf_emit_memchr (pending: PF) spells 1 form(s)
PASS: rule 4: pf_emit_memchr_bounded (pending: PF) spells 1 form(s)
PASS: rule 4: rc_emit_bytes (pending: VERIFY,VMRUN) spells 2 form(s)
PASS: rule 4: rc_emit_words (pending: VERIFY,VMRUN) spells 3 form(s)
PASS: rule 4: u8_defs_bref (pending: N7) spells 1 form(s)
PASS: rule 4: u8_defs_bref_ci (pending: N7) spells 1 form(s)
PASS: rule 4: vm_emit_span_scan (pending: VMSPAN,VMSTRIDE) spells 1 form(s)
PASS: rule 4: vm_rev_emit (pending: N6) spells 1 form(s)
checks passed: 25
checks failed: 0
```

## 4. Witness transcripts

**(i) Manual: C17 on a `git archive HEAD` tree.** Each plant was applied
by `tests/mech/lib/replace.py` from the row's own fields. The `PASS: rule 4`
lines are elided. Each plant fires exactly its intended rule and nothing
else.

```
applied S478 to src/gen/emit_dfa.c
--- S478: C17 on the sabotaged tree
== C17: the checked site manifest (tests/memfn/site_manifest.tsv) ==
PASS: search vocabulary: 8 lines in 4 classes
static half: 9 files under src/gen/ and src/enc/; 29 forms in 23 functions (libc-search 11, runcmp 6, span-compare 4, table-walk 8)
  (C12 reading, information only until C12 is born at R4c: emitted-text memchr( calls = 10)
manifest: 13 rows -- delegated 0 / pending 13 (K35 floor 13)
PASS: manifest row count 13 >= K35 floor 13
FAIL: rule 1 (static half): src/gen/emit_dfa.c:1440 in emit_dead_group_fill spells a libc-call form ('memchr(subject, 0, 0);  /* SABOTAGE S478 */\\n%s ') and no pending row names it
UNREACHED: rule 2 (dynamic half): no pcrec source calls mf_emit_site, so the corpus compile pass has no site call to count -- declared UNREACHED (K35), not passed. Site calls counted: 0.
VACUOUS: rule 3 (delegated emitter still spells a form): 0 delegated rows, nothing to check -- not counted as a pass.
checks passed: 24
checks failed: 1
exit=1
applied S479 to src/gen/emit_dfa.c
--- S479: C17 on the sabotaged tree
== C17: the checked site manifest (tests/memfn/site_manifest.tsv) ==
PASS: search vocabulary: 8 lines in 4 classes
static half: 9 files under src/gen/ and src/enc/; 27 forms in 21 functions (libc-search 9, runcmp 6, span-compare 4, table-walk 8)
  (C12 reading, information only until C12 is born at R4c: emitted-text memchr( calls = 8)
manifest: 13 rows -- delegated 0 / pending 13 (K35 floor 13)
PASS: manifest row count 13 >= K35 floor 13
PASS: rule 1 (static half): every one of the 21 functions that spell a form is named by a pending row
UNREACHED: rule 2 (dynamic half): no pcrec source calls mf_emit_site, so the corpus compile pass has no site call to count -- declared UNREACHED (K35), not passed. Site calls counted: 0.
VACUOUS: rule 3 (delegated emitter still spells a form): 0 delegated rows, nothing to check -- not counted as a pass.
FAIL: rule 4: emit_req_one_byte (pending: PRE) spells no vocabulary form: the row is stale (flip it to delegated in its step's REPLACE commit, or teach search_vocab.tsv the form it now spells)
checks passed: 24
checks failed: 1
exit=1
applied S480 to tests/memfn/site_manifest.tsv
--- S480: C17 on the sabotaged tree
== C17: the checked site manifest (tests/memfn/site_manifest.tsv) ==
PASS: search vocabulary: 8 lines in 4 classes
static half: 9 files under src/gen/ and src/enc/; 28 forms in 22 functions (libc-search 10, runcmp 6, span-compare 4, table-walk 8)
  (C12 reading, information only until C12 is born at R4c: emitted-text memchr( calls = 9)
manifest: 12 rows -- delegated 0 / pending 12 (K35 floor 13)
FAIL: the manifest holds 12 rows, below its K35 floor of 13: a row was deleted without the floor being lowered in the same change
PASS: rule 1 (static half): every one of the 22 functions that spell a form is named by a pending row
UNREACHED: rule 2 (dynamic half): no pcrec source calls mf_emit_site, so the corpus compile pass has no site call to count -- declared UNREACHED (K35), not passed. Site calls counted: 0.
VACUOUS: rule 3 (delegated emitter still spells a form): 0 delegated rows, nothing to check -- not counted as a pass.
checks passed: 24
checks failed: 1
exit=1
```

**(ii) Through mech.** These are single-row runs,
`bash tests/mech/run_sabotage_matrix.sh S478` (then S479, then S480), each
on a freshly built archived tree at 1c3fadf3. All three read DETECTED, with
reach ok and the trailer `unexpected: 0, undetected: 0, unreached: 0,
anomalies: 0`:

```
S478-c17-unlisted-form	src/gen/emit_dfa.c	a memchr( search text is planted in emit_dead_group_fill, an emitter no site-manifest row names: a search site pcrec spells outside the manifest	memfnmanifest	pop:src/gen/emit_dfa.c:/^static void emit_dead_group_fill\(/=1(want>=1),reach:ok(1/1),memfnmanifest:1fail/24pass	DETECTED
S478-c17-unlisted-form  src/gen/emit_dfa.c  a memchr( search text is planted in emit_dead_group_fill, an emitter no site-manifest row names: a search site pcrec spells outside the manifest  memfnmanifest  pop:src/gen/emit_dfa.c:/^static void emit_dead_group_fill\(/=1(want>=1),reach:ok(1/1),memfnmanifest:1fail/24pass  DETECTED
S479-c17-stale-pending-row	src/gen/emit_dfa.c	emit_req_one_byte stops spelling memchr( (respelled as a kit-style call) while the PRE manifest row stays pending: a stale row	memfnmanifest	pop:tests/memfn/site_manifest.tsv:/^PRE[[:space:]]+emit_req_one_byte[[:space:]].*[[:space:]]pending[[:space:]]/=1(want>=1),memfnmanifest:1fail/24pass	DETECTED
S479-c17-stale-pending-row  src/gen/emit_dfa.c  emit_req_one_byte stops spelling memchr( (respelled as a kit-style call) while the PRE manifest row stays pending: a stale row  memfnmanifest  pop:tests/memfn/site_manifest.tsv:/^PRE[[:space:]]+emit_req_one_byte[[:space:]].*[[:space:]]pending[[:space:]]/=1(want>=1),memfnmanifest:1fail/24pass  DETECTED
S480-c17-row-below-floor	tests/memfn/site_manifest.tsv	the VMSTRIDE row is deleted from the site manifest (its emitter stays listed by VMSPAN), taking the row count below its K35 floor	memfnmanifest	pop:tests/memfn/site_manifest.tsv:/^VMSTRIDE[[:space:]]+vm_emit_span_scan[[:space:]]/=1(want>=1),pop:tests/memfn/run_site_manifest.sh:/^C17_ROW_FLOOR=13$/=1(want>=1),memfnmanifest:1fail/24pass	DETECTED
S480-c17-row-below-floor  tests/memfn/site_manifest.tsv  the VMSTRIDE row is deleted from the site manifest (its emitter stays listed by VMSPAN), taking the row count below its K35 floor  memfnmanifest  pop:tests/memfn/site_manifest.tsv:/^VMSTRIDE[[:space:]]+vm_emit_span_scan[[:space:]]/=1(want>=1),pop:tests/memfn/run_site_manifest.sh:/^C17_ROW_FLOOR=13$/=1(want>=1),memfnmanifest:1fail/24pass  DETECTED
```

**Reachability.** These rows are static, and the design marks them "—
(static)" (§17.6). Each one still declares reach, so a future edit makes it
read UNREACHED rather than an empty verdict:
- **S478**: `SAB_REACH` asserts the planted function is NOT in the
  manifest, and `SAB_REACH_POP` asserts that the function exists.
- **S479**: the PRE row is `pending` and names `emit_req_one_byte`.
- **S480**: the VMSTRIDE row exists and the floor literal is 13.

**S-ids.** Main's highest is S477, so these are S478-S480. I told lane
memfnskel, so its ids start at S481 if it takes any.

## 5. Judgement calls

1. **The vocabulary is born here.** C12 does not exist yet; it is born at
   R4c. `search_vocab.tsv` is THE one definition, and its header says C12
   reads it rather than spelling a second list. The table-walk and N6/N7
   lines are fitted to today's spellings. That is the nature of the static
   half, and it is the stated limit.
2. **Columns.** The manifest has §R4.3.4's six columns, plus `companions`
   (existence-checked only) and `ref`. The emitter column holds SPELLERS
   only, which is what rule 4 can check per function.
3. **PRE and SETREST are separate rows.** §15.5 makes them one composite
   site, but §R4.3.4's list names both. Both flip at M1.
4. **Shared emitters.** VERIFY/VMRUN share runcmp's functions, and
   VMSPAN/VMSTRIDE share `vm_emit_span_scan`. Two consequences:
   - deleting one row of a pair trips neither rule 1 nor rule 4, which is
     exactly why the K35 floor exists. S480 deletes VMSTRIDE to witness the
     floor alone;
   - when M1b flips only one of VERIFY/VMRUN, rule 3 fires on the shared
     functions. That is intended: one emitter, one spelling.
5. **`pcrec_emit_runcmp_helpers` is a VERIFY/VMRUN emitter.** The words
   row's `%s_w%d(` load helpers are runcmp row text and move with M1b.
6. **N7's emitters are text constants.** The encoding seam's code is
   `static const char` arrays (`defs_bref`, …), so the reader attributes
   literals to initializers too. The utf8 caseless form does not contain
   `s[at + i]`, so it needed a second line, `span-decode`.
7. **N6's line, `walk-back`, matches `--` only.** The forward VM
   `{ scan_position++; goto` (`vm_emit_node`, `vm_lit`) is the engine's
   per-byte step, which the design says is not a site. If the kit session
   reads N6 differently, this is the line to revisit.
8. **D91 budget for N6, VMSTRIDE and N7 is `loop`.** This is my reading:
   C10's list classifies only the ten original sites. All three run inside
   the VM's match.
9. **These are NOT listed, deliberately:**
   - `ofsk_emit_verify`'s per-candidate tests (T4's shape);
   - clskit's `emit_leaf` range binary search (one code point's
     membership);
   - `emit_scan_loop` and `emit_attempt`'s start loop (the engine);
   - the scan edge's peeled guard (stays pcrec's, §15.7; it is an `if (`,
     not a `while (`);
   - `vm_emit_vars_resolve`'s `memcmp` (a caller-name lookup).
10. **`test-memfn-manifest` has no `all` prerequisite.** It reads `src/`
    and runs no binary, so a stale build cannot make it pass. This follows
    the `test-spec` exception's argument, and the Makefile comment says so.
11. **Mech was run for my three rows only**, as single-row runs, because
    the brief requires each witness to be shown firing. This was not the
    full matrix, not `make test`, and not under the suite lock.

## 6. Validation

| run | result |
|---|---|
| `make -j4 CC=gcc-16` | exit 0 |
| `make strict CC=gcc-16` | exit 0 ("whole tree compiles clean with -Werror -Wshadow") |
| `make test-memfn-manifest` | 25 passed / 0 failed; rule 2 UNREACHED (declared); rule 3 VACUOUS (declared) |
| witnesses (manual) | S478 → rule 1, S479 → rule 4, S480 → floor; each exactly 1 FAIL |
| witnesses (mech, single rows) | S478/S479/S480 DETECTED, 0 unreached/anomalies |
| full `make test`, full mech | NOT RUN (per brief; the manager's at merge) |

## 7. Charter vs committed

| charter item | status |
|---|---|
| `tests/memfn/site_manifest.tsv`: one row per search/span-compare site, the §R4.3.4 columns, all `pending`, a header naming the source of truth and the two states | DONE (13 rows, N7 included, D58/DD-12 cited) |
| C17 rule 1, static, over `src/gen/` and `src/enc/` | DONE |
| C17 rule 2, dynamic, declared UNREACHED (K35) | DONE, plus the reachable-tripwire |
| C17 rule 3, vacuous at 0 delegated rows, said in its output | DONE |
| C17 rule 4, stale pending row | DONE (per emitter) |
| counts with a K35 floor as a literal sharing no source with the TSV | DONE (`C17_ROW_FLOOR=13`) |
| vocabulary independent of the manifest, in one place, reusing C12's if it exists | DONE. C12 did not exist, so it is born here, for C12 to read |
| wired into `make test` in the house pattern | DONE (TEST_SECTIONS + trailer marker) |
| sabotage (a) unlisted form, (b) stale row, (c) below floor; run and transcribed; next S-ids; reach checked | DONE (S478-S480) |
| `tests/memfn/CLAUDE.md`, touched CLAUDE.md files, lanes index | DONE |
| `make`, `make strict`, C17 target, witnesses | DONE |
| no `memfn/` edits, minimal Makefile hook, zero movers | DONE |

## 8. For the kit session (decisions to confirm at review)

- The **vocabulary-in-tests** placement (`tests/memfn/search_vocab.tsv`) as
  C12's future source.
- **N6's `walk-back` line** and the `loop` budget for N6, VMSTRIDE and N7.
- **The extra `companions`/`ref` columns.**
- **Floor maintenance.** Any row-adding change raises `C17_ROW_FLOOR` in
  the same commit (written in the TSV header and the script).
- **Merge with memfnskel.** Both lanes may append to TEST_SECTIONS and the
  phony list, and the only expected conflict is that line.
