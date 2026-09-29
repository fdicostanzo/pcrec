# ucpu1b — [UCP] test-cpset-structure triage + abi 44 -> 45 + K72

Lane `ucpu1b` (sonnet), continuing `lane/ucpu1` in the same worktree from
HEAD `98e94f1d` (the previous lane had ended). Four tasks per the manager's
brief.

## 1. Triage: test-cpset-structure CHECK 3 manifest drift

**Verdict: every moved row is explained by mechanism. Re-recorded.**

The full `make test CC=gcc-16` chain the previous lane launched
(`/tmp/ucpu1s/final_chain.log`) had already finished by the time this lane
started: `sections ran: 45/45`, rc=2 from `test-codegen` (which includes
`test-cpset-structure`). `make_test_full.log:4885` read:

```
FAIL: [3] the recorded manifest has drifted from this run. Under r49 that is
a DIFF TO REVIEW, not a number to bump: read it, decide whether each moved
stamp is a ruling or a regression, and re-record deliberately.
```

The diff: all 12 sample rows, `EMITTED_BYTES` only, each **exactly +4**.

| pattern | before | after | delta |
|---|---|---|---|
| `a` | 22800 | 22804 | +4 |
| `abc` | 23469 | 23473 | +4 |
| `a(b\|c)+d` | 31482 | 31486 | +4 |
| `(a)(b)(c)` | 31006 | 31010 | +4 |
| `[a-z]+@[a-z]+` | 26756 | 26760 | +4 |
| `^foo$` | 18057 | 18061 | +4 |
| `\bword\b` | 27669 | 27673 | +4 |
| `(?i)HeLLo` | 29500 | 29504 | +4 |
| `cat\|dog\|cow\|calf\|camel` | 27603 | 27607 | +4 |
| `(\w+)\s+\1` | 26497 | 26501 | +4 |
| `(?<=foo)bar` | 31080 | 31084 | +4 |
| `(a(?1)?b)` | 29937 | 29941 | +4 |

**Mechanism, confirmed by diffing the artifact rather than inferred from
size**: CHECK 3's census compiles every sample with `--features all`
(`tests/codegen/run_cpset_structure.sh:497`), and U0 (`42a85627`) added
module `ucp` to the registry — under `--features all` its name joins
`PCREC_FEATURE_MODULES`. `,ucp` is exactly 4 bytes. Diffed the `abc`
artifact at the same `-o` basename against a scratch build of main
`7a756066`:

```
< #define PCREC_FEATURE_MODULES "...,extended-classes,modifiers,verbs,vars"
> #define PCREC_FEATURE_MODULES "...,extended-classes,modifiers,ucp,verbs,vars"
```

No other line differs. This is the identical shape the file's own §8.1.1
CHECK 3 history already documents for module `vars`'s `,vars` addition
(+5 bytes, one bump before this one) — a `--features all` fact, not a
per-artifact one.

**Main confirmed green independently**: `git worktree add --detach` at main
`7a756066`, built (`make -j4 CC=gcc-16`), `bash tests/codegen/
run_cpset_structure.sh` → 28/0, CHECK 3 reading "matches this run exactly".
Scratch worktree removed after.

Since every move is explained, the manifest was re-recorded (`tests/codegen/
manifests/m5_stage1_stamps.tsv`) with a fifteenth "RE-RECORDED" comment block
in `run_cpset_structure.sh` naming the mechanism. `bash tests/codegen/
run_cpset_structure.sh` → **28/0** after re-recording (commit `06934ef4`).

## 2. abi 44 -> 45: module ucp's PCREC_FEATURE_MODULES stamp

**Ruling applied, overriding U1's own Q-A default** ("no bump"). D76/D94
plus the `vars` precedent (`d755a9445`, abi 31 -> 32, the same landing that
added `,vars` to the identical stamp) make a `--features all`
scaffolding-only module-name addition an `abi` event on its own, independent
of any per-artifact behaviour change.

### The constant

`src/gen/emit_dfa.c:51`, `#define PCREC_ARTIFACT_ABI 44` -> `45`. Committed
alone as `a6e367a7` so the FILEPIN self-pin below could reference it (the
k64fix/k66fix/findtie convention: "this lane's own last src commit").

### Every reader found by grep

`grep -rln "PCREC_ARTIFACT_ABI\b"` across `*.c`/`*.h`/`*.sh`/`*.py`/`*.md`
returned 33 files. Of these:

- **`src/gen/emit_dfa.c`** — the constant itself (bumped).
- **`docs/spec/match_api.md`** §6 — the ONE change-log home (D76 addendum,
  [REVW.A1]); the "is `44` on every artifact today" bullet converted to
  "was `44`", a new "is `45`" bullet added stating the mechanism, the
  verification (`abc` artifact diff against main), and the reach
  (`run_cpset_structure.sh` CHECK 3's +4 census).
- **`tests/codegen/run_codegen_tests.sh`** — `ABI_EXPECT=44` -> `45`
  (line 2884), and the `[DD-14.FB]` failure message's own copied §6
  narrative (line 2886, D76's "this string is updated FROM §6, never
  authored here" rule) gained the matching transition clause. Verified
  with `bash -n` after editing (the message is a single long bash
  double-quoted string with no backtick/dollar hazards to escape).
- **`tests/codegen/run_recursion_identity.sh`** — comparison (B)'s FILEPIN
  re-pinned `ed51481b` (abi 43->44) -> `a6e367a7` (this lane's own last
  src commit, abi 44->45), same-line comment updated with the mechanism
  and the D76/2026-09-29 dating.
- **`tests/registry/limits_check.sh`** — names `PCREC_ARTIFACT_ABI` only
  as a SCHEMA-VERSION-kind constant in an allowlist of constant NAMES
  (never the value); no edit needed.
- **`lib/pcrec.h`**, **`lib/CLAUDE.md`** — state `PCREC_VERSION` is
  INDEPENDENT of `abi`/`PCREC_ARTIFACT_ABI`, citing the macro by name only;
  no value cited, no edit needed.
- **`src/gen/CLAUDE.md`**, **`docs/dev/coding_guide.md`**,
  **`docs/design/cls_tree_design.md`** — each states "the current value is
  `PCREC_ARTIFACT_ABI` (`src/gen/emit_dfa.c:51`)" deliberately WITHOUT
  quoting the number (the coding guide's own stated policy: a writer needs
  to know what to grep for, not a number that drifts on every bump); no
  edit needed.
- **`docs/design/reqpos_2b.md`** — ALREADY DESCRIBES the wrong citation
  (`src/core/limits.def`) as a FINDING against itself, not a repetition;
  left as-is (`admin3_report.md`'s prior disposition).
- **`docs/design/CLAUDE.md`** — states the same finding about the two wrong
  citations; no edit needed.
- **`docs/dev/known_issues.md`** — cites `PCREC_ARTIFACT_ABI 38 -> 39` as
  a dated historical fact inside K68's own entry; no edit needed (dated
  narrative, not a current-value claim).
- **`docs/dev/plan.md`**, every **`docs/dev/lanes/*_report.md`** — dated
  historical narrative citing past bump events by NUMBER (`abi 40 -> 41`
  etc.); none states "the current value is 44"; no edit needed.

No other file in the grep names a bare "44" tied to `abi`
(`grep -rn "abi.*44\|44.*abi\|\.abi = 44\|is \`44\`" docs/spec/*.md` — one
hit, the match_api.md bullet already converted above).

### Verified

- `tests/codegen/run_cpset_structure.sh` CHECK 3: **28/0**, unaffected —
  `44` -> `45` is a same-length digit substitution, 0 net bytes.
- `make strict CC=gcc-16`: clean.
- `make test-codegen CC=gcc-16`: **11/12 scripts, see §5** — the sole
  failure is the standing darwin `run_inline_capability.sh` red, verified
  pre-existing (A/B against a fresh main `7a756066` scratch build, same
  failure, same message).

## 3. K72 filed — `\h`/`\v` under `-e utf8` are the byte sets

`docs/dev/known_issues.md`, new top entry (highest prior: K71). Confirmed
live both directions:

- **pcrec** (`build/pcrec -e utf8 --emit-main --pattern '^\h$'`, compiled,
  run): matches U+00A0, ASCII space, ASCII tab; answers `nomatch` on
  U+3000 IDEOGRAPHIC SPACE.
- **libpcre2 10.46** (`PCRE2_UTF`, no UCP; light ssh probe,
  `docs/dev/lanes/ucpu1_evidence/probe_hv.py` ->
  `probe_hv_10.46.txt`, `ssh duxevents@100.69.121.107`): `^\h$` matches
  U+3000, U+00A0, space, tab; `^\v$` matches U+2028 LINE SEPARATOR and LF.

Mechanism traced to `h_def`/`v_def` in `src/parse/registry.c` (fixed
`DEF_ALWAYS` string literals, `[\t \xa0]` / `[\n\x0b\f\r\x85]`), never
widened by the encoding lowering or by [UCP] — independent of UCP, since
neither `\h` nor `\v` is one of `DEF_UCP_{D,S,W,P,T}`. UCP's own POSIX
`[:blank:]` is built from the Unicode `\h` list directly (`mod_ucp.c`'s
`t_blank`), not from this escape's `h_def` row, so it is unaffected and
correct. Status: deferred, no fix scheduled, no `tests/known_fail/` repro
(scoping question for whichever milestone widens `\h`/`\v`, out of this
lane's charter).

## 4. `make strict`

Clean (`-Werror -Wshadow`, whole tree) — see §2.

## 5. Suite results (the verdict is make's own `*** [test-X] Error` lines)

- **`make test-codegen CC=gcc-16`**: `run_group: 11/12 scripts passed`,
  `make: *** [test-codegen] Error 1`. The ONE failure:
  `run_inline_capability.sh`'s `FAIL: nm could not read arm_a.o (no
  rx_search symbol)` — the STANDING pre-existing darwin red (documented
  in dozens of prior lane reports, e.g. `mtriage_report.md`,
  `evtriage3_report.md`, `axtriage_report.md`, `w5_report.md`),
  independent of this abi bump. `run_codegen_tests.sh` itself: **111/0**,
  reading `rx_info.abi is 45 (VM) / 45 (DFA), expected 45 on both` —
  the `[DD-14.FB]` abi assertion PASSES at the new value.
- **`make test-registry CC=gcc-16`**: **RC=0, clean** — `bash tests/
  registry/run_registry_tests.sh` end to end, no `FAIL:`/`Error` line
  anywhere; PC-3's own summary `checks passed: 213 / checks failed: 0`,
  the definitions-oracle differential `354 cells, 101244 A==B
  comparisons, 101244 A==C comparisons, 0 disagreements`.
- **`make test-rxtsource`**: **RC=0, clean** — `checks passed: 269 /
  checks recorded: 1 / checks failed: 0`, `rxtsource: INV-COMPAT holds
  over 252 files / 4181 blocks / 30967 expectation lines` (the 1
  `recorded` is the pre-existing darwin C3 non-native-pin note the
  U1 report already carries, unrelated to this bump).
- **`make test-cpset-structure`**: covered under test-codegen above
  (28/0, §1/§2).
- **`make test-ucp`**: **RC=0, clean** — `ucp: all checks passed`;
  `verify_ucp`: 1540 cells agree with libpcre2 10.46, 0 disagree;
  `ucp_compare`: 42 passed / 0 failed (23 sets compared exactly, 9 wide
  utf8 refusals, both directions verified against the committed 10.46
  store); the byte-tier Latin-1 fold relation: 112/112 rows agree. None
  of this moves with an abi digit substitution, and none did.

All four suites named in the brief (`test-registry`, `test-codegen`,
`test-rxtsource`, `test-cpset-structure`) plus `test-ucp` are clean at
abi 45, modulo the one standing pre-existing darwin `nm arm_a.o` red in
`run_inline_capability.sh` inside `test-codegen` — reproduced identically
against a scratch build of main `7a756066` (see §1's methodology; the
same darwin toolchain quirk, documented across dozens of prior lane
reports, applies to `--engine=vm --vm-entry-shape=4` object reading and
has nothing to do with this lane).

## Files touched

`src/gen/emit_dfa.c` (abi bump), `docs/spec/match_api.md` (§6 change log),
`tests/codegen/run_codegen_tests.sh` (ABI_EXPECT + message),
`tests/codegen/run_recursion_identity.sh` (FILEPIN self-pin),
`tests/codegen/run_cpset_structure.sh` + `tests/codegen/manifests/
m5_stage1_stamps.tsv` (CHECK 3 re-record), `docs/dev/known_issues.md`
(K72), `docs/dev/lanes/ucpu1_report.md` (§6 Q-A ruled outcome, side finding
-> K72 pointer), `docs/dev/lanes/ucpu1_evidence/probe_hv.py` +
`probe_hv_10.46.txt` (K72's evidence).
