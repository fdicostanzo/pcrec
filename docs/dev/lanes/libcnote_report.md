# libcnote report — kit F2: delegated sites' libc calls reach MEMFN_LIBC

Branch `lane/libcnote` (cut from `lane/memfn-rowcon` @ ccf0ca33). Every
validation below that ran, ran with `gnutimeout`, inside the box rules
(`make -j4`, `make strict`, 16 single compiles, one 17-fixture driver run).

## 1. Every libc emission site in memfn/src

| site (file:line) | name | noted where | rationale |
|---|---|---|---|
| ofsskip.c:219, :223 (pair leapfrog, in `ofs_fn_define`) | memchr | ofsskip.c:247, `ofs_fn_define`, beside its `MF_INC_STRING_H` bit, before either body is written | both bodies of the one function write `memchr(`; an error after the note is sticky (the compile fails, no text is kept) |
| ofsskip.c:260, :262 (single stream, `ofs_fn_define`) | memchr | same note | same |
| precheck.c:168 (`gate`, the one-byte gate) | memchr | precheck.c:234, in `precheck_use`, right after `gate()` writes | only when the gate is actually written (a part list that is all FUNC parts writes no memchr, while `includes` is set unconditionally) |
| precheck.c:187 (`set_rest`, the table loop) | memchr | precheck.c:237, right after `set_rest()` | same |
| precheck.c FUNC parts (`run_line`, `ofs_fn_call`) | none directly | the FUNC part's definition goes through `ofs_fn_define` (row 1) | a call to the generated function is not a libc call |
| runcmp.c:291 (`run_cmp_render`, `RC_F_MEMCMP`) | memcmp | runcmp.c:297, after the compare text is written | reached from `runcmp` arm, `ofsskip` verify chain (ofsskip.c:184) and `precheck` run parts alike, all through this one render function |
| runcmp.c:338 (`mf_flush_helpers`, `<p>_w<W>`) | memcpy | NOT noted | constant length 2/4/8 = the record's one exclusion (§R4.3.3), the same one `memcpy_is_idiom` in src/gen/memfn_stamps.c applies (literal 1-8). A comment at the site says so |
| runcmp.c `RC_F_WORDS` render, `RC_F_BYTES` | none | n/a | calls to the helpers / byte compares, no libc |
| generic.c, compose.c (render paths), k1_ref.c | none | n/a | grep for every name in pcrec's `libc_names` (mem*/str*/b*, popcount is a builtin and not a libc call) found no emission; the `strlen`/`strcmp`/`memset`/`memcpy` there are the kit's own C, not rendered text |

Exclusion match: the kit notes only `memchr` and `memcmp`; pcrec's scan
records both (its only exclusion is a `memcpy` of literal 1-8, which the kit
never notes). So the kit can never note a name pcrec's scan skips. No such
case was found; no STOP.

Discard analysis. The only way a rendered call fails to reach the artifact
inside the kit is a refusal, and the art's error is sticky (`mf_art_note_libc`
itself returns -1 once `err` is set), so a refused compile keeps no stamps.
In pcrec every kit sink is a Job buffer written into the artifact (checked
`vm_run_compare`, `ofs_site_define`, `pcrec_memfn_use/call/emit`); the art is
per attempt (`job->mf`, ended by `pcrec_memfn_stamps_render`). A host that
renders into a sink and then throws the text away must also throw the art
away; stated in the `mf_art_note_libc` comment in memfn.h. The note precedes
the text by a few statements only in `ofs_fn_define` (the note sits beside
the `includes` bit, the text follows in the same function); the two can
disagree only through the sticky error.

## 2. Changes (commit 37067844)

- memfn/src/ofsskip.c, precheck.c, runcmp.c: the notes above (error return
  propagated as `return -1`, the kit's idiom).
- memfn/include/memfn.h: the `mf_art_note_libc` comment (comment only; no
  signature or struct change; kept to those lines for the missn merge).
- memfn/src/CLAUDE.md, tests/memfn/CLAUDE.md: wording.
- tests/memfn/arm_fixtures.c + run_arm_pins.sh (the kit's stand-alone
  `mf_art` rendering every arm, already wired to `make test-memfn-arms`,
  seconds): the driver prints each fixture's `MEMFN_LIBC` from `mf_stamps`
  (no pcrec scan), the script compares it with its own scan of the rendered
  text, with floors (at least one memchr and one memcmp fixture). This was
  chosen over G2 (run_g2.sh/g2/ is a D27-blinded author's, needs a full
  run, and is forbidden here). Detected the defect: against the unfixed kit
  it fails 8 fixtures (`MEMFN_LIBC is "none", the text calls "memchr"`...);
  against the fix it passes (`arm pins: 34 rows over 17 fixtures`, checks
  passed 74, failed 0). No pin moved (rendered text is unchanged, 34 rows
  green). Observed per fixture: ofsskip -> memchr; pre-lead-handoff ->
  memchr,memcmp; pre-* others -> memchr; run-memcmp8 and run-exact-deny ->
  memcmp; run-overlap/words/bytes and the two generic declines -> none.
- No abi bump: no emitted byte moves (kit text unchanged; only the record).

## 3. make strict

`make strict -j4`: rc 0 ("whole tree compiles clean with -Werror -Wshadow").

## 4. Sample compiles (16 of 20: 8 patterns x before/after)

Before = build of the base kit (stash of memfn/src), after = this branch.
`pcrec -p t --pattern P -o X.c`, MEMFN_LIBC stamp, then `.c` and `.h`
compared (the include line's file name normalised).

| pattern | before | after | .c / .h |
|---|---|---|---|
| `abcdefgh[0-9]+xyz` | memchr,memcmp | memchr,memcmp | identical |
| `user=[a-z]+` | memchr | memchr | identical |
| `a(b|c)+d` | memchr | memchr | identical |
| `foo.*bar.*baz` | memchr | memchr | identical |
| `(?i)hello world` | memchr | memchr | identical |
| `/user/[0-9]+/profile` | memchr,memcmp | memchr,memcmp | identical |
| `xyz[a-c]{2}q` | memchr | memchr | identical |
| `(?:cat|dog|bird)s` | memchr | memchr | identical |

## 5. VALIDATION OWED (manager's slot; not run here)

Zero-mover identity gate (reference = the base sha ccf0ca33; build the
reference as the sweep's own `--ref` flow does; completion judged by the
gate script over the log, plus make's own `*** [...test-` lines for any
suite):

    cd /home/pcrec/projects/pcrec/worktrees/libcnote && make -j4 && \
    python3 scripts/emit_sweep.py --ref ccf0ca33 > $SCRATCH/libcnote_sweep.log 2>&1; \
    python3 docs/design/memfn/probes/lxrun/memfn_r4c_gate.py --zero-dumps $SCRATCH/libcnote_sweep.log

Completion line: `R4C-GATE PASS (--zero-dumps): 0 movers on every stream (...)`
(exit 0); `R4C-GATE FAIL:` lines otherwise. (`--zero-dumps` because the ref
already carries the memfn-simd rows.) Run it detached (`nohup ... & disown`)
and judge the gate script's exit code, not "sections ran".

G2 (the nm -u / stamp check that caught F2; full run, the manager's call on
quick vs full):

    cd /home/pcrec/projects/pcrec/worktrees/libcnote && make -j4 && \
    TMPDIR=$SCRATCH gnutimeout 3600 bash memfn/tests/run_g2.sh > $SCRATCH/libcnote_g2.log 2>&1; echo rc=$?

Completion: final `checks passed: N` / `checks failed: 0`, floors held,
witnesses fired, rc 0. Expect the 37 nm -u batches that reported
`MEMFN_LIBC "none"` to now name memchr/memcmp.

Also cheap, worth including in the same slot: `make test-memfn-arms
test-memfn-stamps` (the stamps/C11 census, which compares pcrec's scan with
the object's undefined symbols).

## 6. Charter vs committed

- [x] every kit libc render notes via `mf_art_note_libc` (memchr x3 sites,
      memcmp x1; memcpy excluded and commented)
- [x] §R4.3.3 exclusion matched to pcrec's `memcpy_is_idiom`; kit never
      notes a name pcrec's scan skips (no STOP case)
- [x] notes happen only on the render path; discard analysed (sticky error;
      host rule stated in memfn.h)
- [x] error return propagated (`return -1`)
- [x] coding_guide read before the C edit (4 two-line additions)
- [x] zero pcrec movers: samples identical; the full gate is OWED
- [x] kit-level direct check: arm-pins gains a stand-alone MEMFN_LIBC check
      with floors; red before, green after. Not in G2 (blinded, forbidden run)
- [x] memfn.h comment and CLAUDE.md entries updated
- [x] `make strict` rc 0
- [ ] zero-mover gate, G2 (owed, section 5)
