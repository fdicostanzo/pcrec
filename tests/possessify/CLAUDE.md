# tests/possessify — the [ENG-BREP] possessification rung's validation

`docs/design/eng_brep_design.md` §2 is the design; `src/opt/possessify.c` is
the analysis; `src/gen/emit_vm.c` is what acts on it. This directory is the
evidence that it changes no answer.

**Not a module directory.** Possessification is an OPTIMISATION over the base
tier, not a regex feature, so it has no module gate of its own (the only
`features` directives are possessify.rxt's `(?m)` blocks, which need module
`assertions` to spell `(?m)` at all). It gets its own directory for the reason
`tests/vm/` has one: what it needs to assert is not expressible as `.rxt`
expectations.

## Files

- **`possessify.rxt`** — oracle-verified cases over the §2.2 rule's own families: both arms (exact-count and disjointness) in both preferences, one block per DECLINING ...
- **`patterns.txt`** — the differential's population, built as §2.4's family (prefix × body × count × follow) with every count spelled BOTH ways.
- **`calls.txt`** — K93's differential population (lane k93fix, 2026-10-07): a group with a call whose follow overlaps the group's FIRST where its lexical follow does not, ...
- **`possdiff_driver.c`** — links the possessified and denied artifacts under two prefixes into one TU. (`-DDIFF_EXACT_SUBJECT`, [OPT-LITSCAN] S2a: each subject is handed ...
- **The [ART-POSS-ARMS] section of `run_possdiff.sh`** (poss_arms.md 8.1; lane possbuild-pd).
- **`run_possdiff.sh`**, **`run_possessify_tests.sh`** — the two suites, wired into `make test` as `make test-possessify` and into the `make ubsan`/`make asan` both-axes ...
- **`run_possdiff.sh` + `possdiff_driver.c`** — the row's PRIMARY instrument (§5.1).
- **`run_possessify_tests.sh`** — that the rewrite HAPPENED where the stamp says it did, NOWHERE when denied (D47.3's do-or-die, asserted against the artifact and never ...
- `composition_d27.rxt` (+ `composition_d27_notes.md`) — D27-BLINDED composition corpus (lane posscomp, 2026-10-07, [ART-POSS-ARMS] review R-3a). 676 blocks / 7,412 cases ...
- `ctx_admits_check.c` -- exhaustive model check of `pcrec_poss_ctx_admits` (16 truth tables x 3 non-empty P masks x 53 C sets, plus the named A-F3 cell); built through ...
- `.h` — section "[DD-14.FB] the frames-rung check reads the capacity macro from the `.h` (2026-08-25)" (history file)

## Two lessons this directory paid for, recorded so they are not re-paid

**The subject generator can silently measure nothing.** D47.6: the design
lane's archived sweep reported 20 "false declines" that were 20 GENUINE
divergences, because its random-subject alphabet was `"abcd "` and every
`z`-prefixed pattern in its family was therefore swept essentially without its
prefix. `run_possdiff.sh` derives each pattern's subject alphabet from the
PATTERN'S OWN TEXT for this reason, and the discriminating family is prefix +
repeated body. *A generator whose alphabet omits a pattern character measures
the generator.*

**A green sabotage row is a finding about the POPULATION, not a clean bill.**
Sabotage S48 (the enclosing-loop FOLLOW term dropped) came back UNDETECTED
against the first version of `patterns.txt`, and the reason was that every
nested cell in it put a NON-NULLABLE item after the inner quantifier — a shape
where the term is merely conservative. A generated search over an
18,480-pattern nested family found 7,553 patterns whose verdict changes
without the term and 44 wrong spans in a 1,259 sample; the shape that
discriminates puts the inner quantifier at the END of the enclosing body.
Twelve witnesses were added and S48 is now DETECTED. The term is load-bearing;
the first population simply could not see it.

- Also (one-line entries for these are in the history file): `arms_core.txt`, `arms_i.txt`, `arms_manifest.tsv`, `arms_mline.txt`, `arms_reach.tsv`, `arms_routeflip.txt`, `arms_ucp.txt`, `arms_utf8.txt`, `arms_utf8i.txt`, `subjects_exh.py`.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__possessify.md`.
