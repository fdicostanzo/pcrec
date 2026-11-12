# or49disp report: disposition of the make-test reds against PCRE2 10.49 ([ORACLE-UPGRADE])

Lane or49disp (sonnet), 2026-11-12. Source run: queue job 300 (`300-main-oracle49-maketest`), log
`/var/tmp/pcrec-pcrec/scratch/oracle49/test.make.log` (premise test: 5 red sections, confirmed). No `src/` or `memfn/` edit.
Probes: `$PCREC_TMPDIR/scratch/or49disp/probe.c` built against the box's 10.46 (Unicode 16.0.0) and the tarball build 10.49
(Unicode 17.0.0); a small ctypes-free C driver (`probe46`/`probe49`), not pcre2test (no 10.46 pcre2test exists on this box).
Release ChangeLog: `.../pcre2-10.49/src/pcre2-10.49/ChangeLog` (documentation). Official UCD 17.0.0 files fetched as DATA only into scratch.

## STATE AT HANDOFF
- Branch `lane/or49disp`, one mechanical edit applied: `tests/registry/pcre2_check.c` gains a 10.49 PC-3 floor (class d, below).
  Verified standalone: the PC-3 binary built from the edited file against 10.49 (box link: oracle49 worktree's libpcrec.a, read-only)
  prints `checks passed: 217, failed: 0`; before the edit 216/1.
- Everything else is listed as a ruling, none applied. No wrong pcrec answer found for any case that matches the STOP RULE; one
  edge (R3, `\K` reached by recursion from a lookaround) is a pcrec/10.49 divergence, class (a), reported prominently.
- Last rulings entry applied: none (`or49disp_rulings.md` empty at each read).
- Evening hold (20:00-01:00) respected: work was done before 20:00, single compiles and single-case probes only.

## FINDINGS

### test-registry (1 red) - class (d), APPLIED
- `FAIL: POSIX class names: no probe-count floor for libpcre2 10.49`. Measured on this box (gcc, tarball-built 10.49): **155338**
  probes (10.46 floors: 149804/154210/155742; 10.48 Homebrew 187872). Floor + RECORD added beside the others; D98's list of
  measured floors should gain the line when the pin moves. No other PC-3 check differs on 10.49 (216 other checks pass).

### test-uprops (1 red: `d27 corpus disagrees with libpcre2`) - class (b)
- 2 cells, `tests/uprops/d27/emoji.rxt:582` (`\p{Extended_Pictographic}`) and `:622` (`\P{...}`) on U+1F000.
  10.46/Unicode 16: Extended_Pictographic; 10.49/Unicode 17: not. The official Unicode 17.0.0 `emoji-data.txt` lists
  Extended_Pictographic as `1F004`, `1F02C..1F02F`, ... with no `1F000..1F003` (mahjong tiles dropped). So 10.49 is right and pcrec's
  UCD 16 is right for 16; not a PCRE2 bug. The d27 pcre2 arm has no drift budget (the main uprops differential does, and passed).
- Fix: a Unicode 16 -> 17 data move (ruling R1), or a drift exception for the two cells keyed to the pinned UCD version.

### test-ucp (1 red: `verify_ucp` + `gen_island_rxt.py --verify`, the same 36 cells counted by each) - class (b)
- 18 code points x 2 positions (`(*UCP)x\b`, `(*UCP)\bx`): U+088F, 0C5C, 0CDC, 1ACF, A7CE, A7CF, A7D2, A7D4, A7F1, 10EC5, 10EFB, 187F8,
  187FF, 18D09, 2B73A, 2B73F, 2CEA2, 323B0. All are Cn in pcrec's UCD 16.0.0 (so the island generator emitted them as non-word,
  file says `(0, 1)`), all assigned in 17.0.0 (UnicodeData.txt 17.0.0: Lo/Lu/Lm/Mn/CJK Ext J), so `\b` has no boundary after
  `x` in 10.49. Probe: 10.46 `match 0 1`, 10.49 `nomatch`, 18/18. Same drift the u3twin and orwire lanes saw on the Mac's 10.48.
- Everything keyed to the committed 10.46 store (section 2, 49 checks) and the Latin-1 fold passes on 10.49: no data in the stores moved.
- Fix: ruling R1 (UCD 17), or a drift tolerance in `verify_ucp`/`gen_island_rxt.py --verify` that excuses a disagreement only when the
  code point is Cn in the pinned UCD (the uprops drift budget's shape).

### test-subst (18 checks red, 5 distinct causes) and test-subst-d27 (4 sections red) - classes (a) and (c)
1. **`\K` via recursion from a lookaround: -60 -> -75 (class a).** Cells `backward`, `backward2`, `overlap` (+ d27 `bsk-057..071`,
   9 `FAIL` cells). `PCRE2_ERROR_BAD_BACKSLASH_K` (-75, "disallowed use of \K in lookaround") is new in the 10.49 header (absent in
   10.46's `pcre2.h`; 10.46 reports end-before-start and substitute gives -60). Probe: `x(?=(?1))|(b\K)` on `xb`, global substitute:
   10.46 `rc=-60`, 10.49 `rc=-75`; plain `pcre2_match`: 10.46 match (2,1), 10.49 `rc=-75`. The ChangeLog and docs do NOT list the
   change (10.43 item 6 locked `\K` in direct lookarounds; this extends the lock to recursion at run time, so it is undocumented upstream
   behaviour, cited by header and probe). pcrec's own answer (spec subst_api.md 4 para 20: reports [2,1), BADSPAN) is unchanged.
2. **`corner` and d27 `bsk-063/065/069` "FIXED?" (class a)**: `^|(?<=(?1))y|(?!)(\Kz)` on `zy`: 10.46 -60, 10.49 `rc=2 out=[][zy]`,
   equal to pcrec. The documented divergence (subst_api.md 9 row 9, "pcre2 tests the SEARCH start") has disappeared on 10.49.
3. **`illformed` and d27 `utf-003/009/063/069/079/083/126` "FIXED?" (class a)**: `x*` global on `a\xffb` under UTF|MATCH_INVALID_UTF:
   10.46 `[]a\xff[]b[]` (3 matches), 10.49 `[]a[]\xff[]b[]` (4), equal to pcrec; subst_api.md 9 row 11 (C1, "anchored retry
   reports a match past the ill-formed byte") no longer diverges. Closest ChangeLog: 10.48 item 27 (#945, advance by one unit over invalid
   characters); the entry is JIT-worded but the interpreter changed too.
4. **`\G` global-empty cells, d27 `empty-185..188,190,191` (class a, Perl-confirmed)**: `\G` on `ab` global: 10.46 `[]a[]b[]`, 10.49
   `[]ab`; `\Ga?` on `ab`: 10.46 `[a][]b[]`, 10.49 `[a][]b`. Perl 5 gives `[]ab` and `[a][]b`, i.e. 10.49 now follows Perl and pcrec
   follows 10.46. No ChangeLog entry found.
5. **`$+` replacement, d27 `tpl-049` (class a, feature)**: 10.47 item 18 (#817) added `$+` to `pcre2_substitute`. 10.46 returns -35,
   10.49 substitutes the last group (`xax`). pcrec refuses `$+` (template offset 0). A feature gap, not a wrong answer.
6. **Trailing ill-formed sequence loses the final empty match, d27 `utf-004..008, 064..068` (class c, candidate PCRE2 bug)**:
   UTF|MATCH_INVALID_UTF, `x*` global: subject `\xc3`: 10.46 `[]\xc3[]`, 10.49 `[]\xc3`; `a\xff`: `[]a[]\xff[]` vs `[]a[]\xff`;
   `\xff\xff`: 3 matches vs 1. Subjects with the ill-formed unit mid-subject keep the trailing empty match, and valid subjects
   (`a`, `ab`) still get it, so it is specific to ending in an ill-formed unit. Perl has no equivalent. Repro in the scratch driver:
   `probe49 subst 'x*' 'a\xff' '[$0]' 4080000 100`. I could not find it in the ChangeLog; likely a side effect of the #945 advance
   change. pcrec keeps the 10.46 answer (and the old Perl-for-valid-input shape).
7. **Reach tokens (`S1346`, `S1347`, `illformed`, `badspancorner`; "carried by no passing cell")**: derived from 1-3, not separate.
- U24/U23 and the other substitute cells passed. Fix and CI-pin: see R2-R6.

### Other 10.49 differences recorded
- PC-3 probe counts, version stamps and `[ORACLE-LINK]` lines all resolve to 10.49; no section other than the five turned red.
- U25's tolerance (5-7 cells of `(?<*(.{1,3}))b`, `tests/lookaround/vlb_one.sh`) was not exercised: test-lookaround section 5 passed with
  0 tolerated on 10.49 (fixed upstream 10.48, ChangeLog 10.48 item 37). It can be retired in the pin change (R7).
- U26 (DEFLB) was already filed (#1072) and is untouched.

### Rulings wanted (recommendation each)
- **R1 Unicode 16 -> 17 (classes b: 38 cells: 2 in uprops d27, 36 in ucp)**: file a plan row [UCD-17] (third_party UCD move, measure_store, the
  oracle store, `uprop_more.md` "version pin" rule, regenerated tables) and move all files together; until then add drift exceptions
  restricted to code points that are Cn in the pinned UCD (ucp) and to the two named emoji cells (d27). Recommend: the plan row, plus
  the narrow exceptions only if the CI pin moves before the data does.
- **R2 version-aware expectations in tests/subst**: cells.tsv and the d27 corpus carry one libpcre2 answer per cell; 10.46 and 10.49
  now differ on 18 cells. Recommend: a per-version column (`rc:-60|rc:-75`, `known:` rows retired for >= 10.47) in the same change as
  the CI pin move, not before, so the box's 10.46 stays green meanwhile.
- **R3 `\K` via recursion in a lookaround**: pcrec reports a span, PCRE2 10.49 errors. Recommend: follow (D26: Perl locked it out,
  compatible-unless-bug); file a plan row [BSK-LOOKAROUND] (compile or match refusal with the PCRE2 text); pcrec bug id not needed
  yet. Not a wrong answer on a pattern anyone writes, hence not stopped.
- **R4 `\G` under global substitute**: recommend follow 10.49/Perl (plan row [SUBST-G]); an engine-behaviour change in the `\G` handling
  of the substitute loop, owned by the substitute module; hold until R2's version split exists.
- **R5 `$+` template**: recommend a plan row [SUBST-PLUS] to add `$+` (spec subst_api.md template list + tests); until then keep the refusal
  and exclude tpl-049 on >= 10.47.
- **R6 trailing ill-formed final empty match (class c)**: recommend an upstream report U27 (repro above, 10.49 only) AFTER a
  maintainer-style minimization the manager approves (outward-facing; I did not file). Keep pcrec's answer; tolerance row in
  upstream_issues for the 11 d27 cells on 10.49.
- **R7 CI pin move (D98 10.46 -> 10.49)**: can happen with the packet R1-R6 + the version split (R2) in ONE change; the PC-3 floor is already in this lane's tip; also retire
  U25's tolerance in `tests/lookaround/vlb_one.sh` in the same change. It must NOT move alone: the CI run would be red on test-uprops,
  test-ucp, test-subst and test-subst-d27 today.

## OWED
- After 01:00, via the box queue (RUNS.md), re-run against 10.49 at this lane's tip (PKG_CONFIG_PATH/LD_LIBRARY_PATH as in
  `docs/dev/lanes/oracle49/300-main-oracle49-maketest.job.sh`): `test-registry` (expected green now), and the four others only after the
  rulings land (they stay red by design until R1/R2). Job key: none queued by this lane (no queue call was made; the registry floor
  was verified standalone). The manager queues the registry re-run; the other four are not worth re-running before R1/R2.
- The standalone PC-3 verification used the oracle49 worktree's `libpcrec.a` (built from main 0c56b73cf); a full `make test-registry`
  at this tip is the clean confirmation.
