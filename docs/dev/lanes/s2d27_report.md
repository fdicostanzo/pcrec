# s2d27 report: Part D spec-first decline and R-by-role witnesses (D27 author, opus)

## FINDINGS (top, as briefed)

1. **No answer disagreement between pcrec and the oracle.** The compiled matchers (this cell's
   `build/pcrec --emit-main`, gcc -O2) agree with python3 `re` on every case: 143 m/n cases in
   26 blocks, run under 4 to 5 arms each = 619 case-runs, 0 disagreements
   (`/var/tmp/pcrec-pcrec/scratch/s2d27/run_final.tsv`, last line `TOTAL-DISAGREEMENTS 0`). A
   random-subject fuzz over the same 26 patterns and arms, with random startpos (rx_search through
   my own driver, so `max(startpos, c - K)` is exercised), found none either: 110,000 comparisons
   (subjects up to 48 bytes, 16,112 of them matches) plus 54,400 (subjects up to 300 bytes, the
   `-fmemfn-simd` arm added, 9,304 matches), 0 disagreements.
2. **The design's F1/F2 witness no longer reaches the decline at this build (route moved, not an
   answer error).** part_d.md §2.4's table gives `(a|bc)[a-z]{8}.q` as the declined run. Here
   pcrec states the run `[6163][61-7a]x8`: the prefix's last position `{a,c}` joins it, and `{a,c}`
   (0x61, 0x63) is a two-member cube, so the run has a findable position. The compile shows
   `_REQ_RUN "...@0"`, `_REQ_HANDOFF "1"` (the run's position 0): a TESTED run, not a decline.
   Under the brief's caveat it is inert for F1/F2, so I re-shaped it: `(a|bc|de)[a-z]{8}.q`
   (position 0 `{a,c,e}`, three members) and `(a|bd)[a-z]{8}.q` (position 0 `{a,d}`, two members,
   not a cube). Both show the decline's contract signature: no `@` (match_api.md §6.3.7¶7 row 3),
   `_REQ_WHY "emitted"` and `_REQ_HANDOFF "11"`, q's own K (§6.3.7¶11: the landmark is the
   leading member where the kit declined the run). The old shape is kept as a CONTROL block (a
   tested run whose scan is a cube between wide positions, part_d.md §2.1 item 2).
3. **The F7 cube witness's route is now known.** part_d.md §2.4 recorded `(a|bc)\d[aA]\d` as
   `_REQ_WHY "none"` before stage 3 and left its stage-3 route INFERRED. At this build it is
   `_REQ_WHY "emitted"`, `_REQ_HANDOFF "1"`, `_REQ_RUN "[6163][30-39][4161][30-39]@2"`, so it reaches
   the pre-check. Under `--memfn=no-run-verify-wide` its pre-check tests only the `[aA]` stretch.
   I read that from the emitted text of the sibling `(a|bc)\d{3}-\d{4}`, which under the deny
   becomes `!memcmp(subject + cand + 4, "-", 1)` alone: the one-position stretch.

## STATE AT HANDOFF

DONE. The five witness files are written in the cell's `witnesses/`, every expectation
oracle-verified, and every block's route is recorded in a comment above its `pattern` line.
Commit: no (cell, per the deliver file). Rulings file `docs/dev/lanes/s2d27_rulings.md`: empty at
every checkpoint, so no ruling applied. Nothing is OWED from this lane. When the witnesses land
with the joint merge, they still need the harness checks I could not run (GAPS 3).

## WITNESSES

Files (each header cites the contract text it was derived from and lists its arms):
- `/home/pcrec/projects/pcrec/worktrees/s2d27-cell/witnesses/partd_decline.rxt`: F1 (handoff
  route, K = the member's), F2 (member head), §9 item 3 (nothing to render: `untestable`), and the
  cube-scan control.
- `/home/pcrec/projects/pcrec/worktrees/s2d27-cell/witnesses/partd_dominated.rxt`: F3, the
  dominated no-scan run (`x.(?:cat|dog)`, `q(a|bc|de)[a-z]{8}`). It also holds the JOINT
  SUPERSET cases (`x-cog`, `x-dat`, `x-cag` hold every position's set and must not match,
  §6.3.7¶7a).
- `/home/pcrec/projects/pcrec/worktrees/s2d27-cell/witnesses/partd_required.rxt`: F4 and P2/P9
  (the scan-less REQUIRED run on a no-match and a matching subject), plus five more scan-less
  REQUIRED runs covering each handoff K state: finite 1 and 0, `unbounded`, and `none` (a
  pre-check part that is not a slice of the run).
- `/home/pcrec/projects/pcrec/worktrees/s2d27-cell/witnesses/partd_deny_stretch.rxt`: F7, the
  deny arm's one-position stretch: a one-member `-` and a cube `[aA]`, each with a findable
  (`{a,c}`) and a wide (`{a,c,e}`) position 0.
- `/home/pcrec/projects/pcrec/worktrees/s2d27-cell/witnesses/partd_r_by_role.rxt`: the wide R that
  keeps `run-pinned` (`xy/users\d+`, offsets `0*,1,..,7`, `_REQ_RUN "78792f7573657273[30-39]@0"`),
  six more wide-R shapes whose exact stretch sits at the start, the end or the middle, the control
  R with no one-member position (`[a-z]{4}\d+`: `byte-class`, `untestable`), and a caseless form.

Reaching rule (the [r2pd P5] caveat): every F1, F2 and F7 witness compiles to `_REQ_WHY "emitted"`
on the default arm. No witness was counted while inert.

## RECORDS

Default arm, this cell's `build/pcrec`. The full per-arm records are in `run_final.tsv`
(ROUTE rows).

| finding | pattern | _REQ_WHY | _REQ_HANDOFF | _REQ_RUN (shape) | route |
|---|---|---|---|---|---|
| F1, F2 | `(a\|bc\|de)[a-z]{8}.q` | emitted | 11 | `[616365][61-7a]x8`, no `@` | VM hybrid, prefilter `handoff` |
| F1, F2 | `(a\|bd)[a-z]{8}.q` | emitted | 11 | `[6164][61-7a]x8`, no `@` | VM hybrid, `handoff` |
| §9 item 3 | `(a\|bc\|de)[a-z]{8}` | untestable | none | no `@` | VM hybrid, `byte-class` |
| control | `(a\|bc)[a-z]{8}.q` | emitted | 1 | `[6163][61-7a]x8@0` | VM hybrid, `handoff` |
| F3 | `x.(?:cat\|dog)` | dominated | none | `[6364][616f][6774]`, no `@` | DFA, `memchr` |
| F3 | `q(a\|bc\|de)[a-z]{8}` | dominated | none | no `@` | VM hybrid, `memchr` |
| F4, P2/P9 | `(x?)([a-z]+)+eeeeeeee~#~#~#~#.[0-7]{32}\1` | emitted | none | `[0-7]{32}` as `30../f8..`, no `@` | VM, `_VM_PREFILTER "none"` |
| F4 | `(x?)[a-z]{6}\1` | emitted | 1 | no `@` | VM attempt loop |
| F4 | `([a-z])\1\d{6}` | emitted | unbounded | no `@` | VM attempt loop |
| F4 | `(\w)\1[a-z]{6}` | emitted | unbounded | no `@` | VM attempt loop |
| F4 | `(\d)[a-f]{6}\1` | emitted | 0 | no `@` | VM attempt loop |
| F4 | `(a)\1?[0-7]{4}` | emitted | none | `30303030/f8f8f8f8`, no `@` | VM attempt loop |
| F7 | `(a\|bc)\d{3}-\d{4}` | emitted | 1 | `...@4` | VM hybrid, `handoff` (both arms) |
| F7 | `(a\|bc)\d[aA]\d` | emitted | 1 | `...@2` | VM hybrid, `handoff` (both arms) |
| F7 | `(a\|bc\|de)\d{3}-\d{4}` | emitted | 1 | `...@4` | VM hybrid |
| F7 | `(a\|bc\|de)\d[aA]\d` | emitted | 1 | `...@2` | VM hybrid |
| wide R | `xy/users\d+` | dominated | none | `78792f7573657273[30-39]@0` | DFA `run-pinned` `0*,1,2,3,4,5,6,7` |
| wide R | `xy/users\d+z` | dominated | none | `...@0` | `run-pinned` `0*,1,..,7` |
| wide R | `id=\d{3}[a-z]+` | emitted | 0 | `...@2` | `run-pinned` `0,1,2*` |
| wide R | `xy[a-z]users\d+` | emitted | 0 | `...@0` | `run-pinned` `0*,1` |
| wide R | `a\dbcdefg\d+` | emitted | 0 | `...@2` | `run-pinned` `0,2*,3,4,5,6,7` |
| wide R | `\d{2}abcdefg\d+` | emitted | 0 | `...@3` | `run-pinned` `0,2,3*,4,5,6,7,8` |
| wide R | `ab[0-9a-f]cdefgh[xy]+` | emitted | 0 | `...@1` | `run-pinned` `0,1*` |
| R control | `[a-z]{4}\d+` | untestable | none | no `@` | DFA `byte-class` |
| caseless | `(?i)xy/users\d+` | emitted | 0 | `...@0` | DFA `offset-set` `0,2*` (GAPS 5) |

Cross-arm movements, all consistent with the spec as I read it:
- `--memfn=no-run-verify-wide` turns the wide-R sites from `emitted` to `dominated`. This matches
  tuning.md §2.30¶1: on the default arm the reply verifies wide positions past the pinned exact
  stretch, so the pre-check stays emitted. Under the deny the reply is clipped to the findable
  stretch, and the pinned compare then covers it.
- On `(a|bc)[a-z]{8}.q` the same deny moves `_DFA_PREFILTER` from `handoff` to `byte-class`. The
  verified extent shrinks to the common pair `{a,c}`, and §2.41¶8a's `1/h - max(K,0) > 1/m` test
  then fails.
- `--memfn=no-fd-pres-g1` turns both F3 witnesses into `emitted` with handoff 0: P2 is denied.
- The decline's emitted text confirms it. The pre-check of `(a|bc|de)[a-z]{8}.q` is a
  `memchr(.., 113, ..)` with `landmark_position - 11`, with no run test. The scan-less
  REQUIRED part of `(x?)[a-z]{6}\1` is a byte loop that verifies all six positions at every
  candidate (`for (; pos + 5 < n; pos++)`).

## ORACLE

- python3 `re`, bytes mode (`\d`/`\w` ASCII). `flags i` maps to `re.I | re.ASCII` (rxt_format.md
  §3¶2). `features` is a no-op for the oracle. Every m/n line of every block was checked, except
  the one below.
- **The one construct python cannot judge** is performance, not semantics. On F4's 36-letter
  no-match subject, `([a-z]+)+` backtracks exponentially in python: 0.42 s at 22 letters, doubling
  per letter, so roughly 2^14 times that at 36. That block carries `oracle none <reason>`
  (rxt_format.md §3.1¶2) and a DERIVED answer: every match contains `[0-7]{32}`, and the subject
  holds no byte 0-7 (checked mechanically with `re.search(rb'[0-7]', s)`), so there is no match.
  The python-verifiable 20-letter version of the same subject sits in the block above it.
  pcrec's own `-fno-req-run` arm gives up (`steps`) at 36 letters and not at 24 or fewer, which is
  why the 36-letter subject is kept.
- libpcre2 was not used: it is not in the cell, and every construct here is python-judgeable
  (backreferences included).
- Tools, in scratch (not in the cell), all reading the cell's `build/pcrec` and the witness files:
  `/var/tmp/pcrec-pcrec/scratch/s2d27/tools/runwit.py` (oracle + per-arm compile and run, prints
  ROUTE and CASE rows), `fuzz.py` / `fuzz_long.py` + `fdrv.c` (the random-subject and startpos
  differential), and `probe.sh` (one compile's stamps).

## GAPS

1. **Disclosure.** At spawn the harness injected the user-global CLAUDE.md, the session-root
   CLAUDE.md and the manager's memory index. No text from `src/`, `tests/`, `memfn/src/` or
   `memfn/tests/` reached me. The cell contains a `.git` directory: I did not read or query it.
2. **No per-block `--memfn=` line exists in the .rxt format**, so the deny arm is not written into
   the files. It reaches them through `make test-axes`' memfn arm (docs/testing.md, "The
   `--memfn=` arm"), which runs every `--list-axes` memfn row, `run-verify-wide` included, over
   the corpus. Each file's `# arms:` comment names the arms I ran, and is a plain comment to every
   other reader.
3. **I did not run the harness's own readers on these files** (`tests/harness/run.sh`,
   `verify_rxt.py`: I am denied `tests/`). My runner implements the subset of the format the files
   use. `pcrec --list-source` parses all five files (rc 0) and records the `oracle none` line in
   its oracle column. **Two things to check at landing:**
   - Confirm that `verify_rxt.py` SKIPS the `oracle none` block. If it does not, python hangs on
     it (FINDINGS' exponential case). The fallback is to drop that block and keep only the
     20-letter one.
   - Moving the files into a `tests/<module>/` directory moves corpus population pins (startset
     manifests, the rxtsource census, axes allowances), per BOILERPLATE's delivery bar.
4. **The kit-internal facts are observed only through stamps and emitted text**: `pres_row` = PD,
   `proven_by`, `has_scan`, the extent. As far as I found, no CLI listing exposes the kit's links,
   so a witness asserts each finding through its observable consequence: `@` presence, the
   handoff K, `_REQ_WHY`, and the answer. "REQUIRED route" is inferred as the VM attempt loop
   (`_VM_PREFILTER "none"`) from part_d.md §2.4's P2/P9 row. The contract text names the need
   (`N_REQUIRED`) but no stamp exposes it.
5. **Ambiguity, not counted as a finding.** tuning.md §2.30¶4 says the pin is "the maximal stretch
   of exact positions around the rarest exact byte". It does not say whether a ONE-position exact
   stretch pins. `(?i)xy/users\d+` has one exact position (`/`) and takes `offset-set` `0,2*`, not
   `run-pinned`, while memfn.h `run_stated` reads as 1 there (R has a one-member position). If a
   pin needs two or more exact positions, the spec sentence should say so. The block asserts
   answers only, not the prefilter value.
6. The witnesses assert answers. Each route is RECORDED in a comment, not asserted (the .rxt
   format has no stamp assertion). A route moving under a later change shows only when someone
   re-reads the comments, so the landing may want a stamp check that reads them.
