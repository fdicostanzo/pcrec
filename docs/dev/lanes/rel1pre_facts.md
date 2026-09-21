# [REL-1] pre-flight fact sheet (lane rel1pre, 2026-09-21, read-only)

Facts only, each with a file:line citation or an explicit GAP. No `make`, no
build, no compile was run (quiet-box timing measurement was in flight
elsewhere). Branch `lane/rel1pre` from `30099e67`.

## 1. [REL-META]'s row — obligations and where each is satisfied

`docs/dev/plan.md:578` (the row itself, quoted for exact wording).

| obligation | where satisfied | status |
|---|---|---|
| Recursion frame/trail defaults (2,048/3,072) in user docs | `docs/spec/limits.md:78` ("Resume-stack default: 2,048 frames. Trail default: 3,072 entries."), `docs/spec/limits.md:404`; source constants `src/core/limits.def:183-186` | DONE (spec tier) |
| The subject-size implication for recursive patterns (`^(a(?1)?b)$` gives up at 684 bytes) | not found by grep for "684" in `docs/spec/limits.md` or `docs/spec/match_api.md` | GAP — the specific worked example from D73 isn't in the spec; the general mechanism (frame/trail counts, `_in` override) is |
| musl/small-thread-stack caveat (K33) | `docs/spec/limits.md:413-523` (whole "§5. K33: the default entries and the C stack" section — musl's 128 KB default named at `:451`) | DONE (spec tier) |
| Caller-provided buffer (`_in` entries) as the remedy | `docs/spec/limits.md:125`, `:484-523`; `docs/spec/match_api.md` §10 (cited at `limits.md:484`) | DONE (spec tier) |
| The GUIDE-1 use-case paragraph pointing at the above | `docs/guide/` does not exist | GAP — full row not started |
| README pass referencing the guide | README.md has no guide reference (guide doesn't exist) | GAP |
| Release-mechanics item: "abi resets to 1 at the 1.0 release" | D81 addendum (`docs/dev/decisions.md`), reaffirmed at D113/D114 (`docs/dev/decisions.md:7692-7693`): **the reset does NOT fire at 0.1** — abi keeps counting past 27. Nothing to build for 0.1 beyond stating this. | NOT APPLICABLE to 0.1 (by design) |
| CONTRIBUTING.md + PR template + RUN-STAMP (item a) | none exist | GAP |
| CI on GitHub Actions (item b) | `.github/` does not exist | GAP |
| README release-adequacy pass + quickstart (item c) | quickstart exists (README.md:7-12) but the Status section is stale (§2 below) | PARTIAL |
| Versioning + changelog + release mechanics (item d) | no version constant, no CHANGELOG, no tag; `gh` CLI present (§4, §8) | GAP |
| "whatever the survey finds" (item e) | this document | in progress |

REL-META itself is still `STATE:not-started` (`docs/dev/plan.md:578`) — its
own "propose the concrete rows" charter has not been executed; [REL-1]'s
2026-09-21 note (`docs/dev/plan.md:574`) says this rel1pre survey substitutes
for it directly rather than waiting for a separate REL-META lane.

## 2. README.md staleness

Full file read (`README.md`, 48 lines).

| claim | current truth | citation |
|---|---|---|
| "Milestones M1 ... and M2 ... are complete" | true but a severe understatement — M4 (captures/VM hybrid), M5 (UTF-8), M6 (all five modules: named-groups, assertions, atomic-groups, backrefs, lookaround) are ALSO complete | `docs/dev/plan.md:110-251` (M4.x archived), `docs/dev/plan_completed.md:3907` (M5.0 completed 2026-09-12), `docs/dev/plan.md:233-240` (M6.0-M6.6 archived) |
| "Roadmap: streaming input (M3), captures via a backtracking VM engine (DFA-prefilter hybrid, M4), UTF-8 (M5), then the wider PCRE feature set as drop-in modules" | M4 and M5 are DONE, not roadmap; M3 (streaming) is genuinely still `STATE:not-started`; "the wider PCRE feature set as drop-in modules" is also mostly done (M6 complete) | M3: `docs/dev/plan.md:254-255` (`STATE:not-started`); M4/M5/M6 completion citations above |
| "read counts from a run, not from this file — two hand-copied counts have gone stale here already" | still true in spirit, but no counts appear in the current file at all (they were apparently removed already) | README.md:20-31 |
| No mention of: abi versioning, `--tune`, `--engine=`, encodings (`-e byte|utf8`), `--features`, the registry dump surfaces (`--list-syntax` etc.), the recursion module, the whole [REVW.1]-[REVW.5] code-review/layering wave | — | not in README.md at all |
| Requirements section says "gcc (or clang)" | clang cannot build the sanitizer/lint axes (Apple clang lacks `-fsanitize=leak`/`-fanalyzer`, `docs/dev/lanes/santriage_report.md`) but CAN build the default `make`/`make test` target; the claim is accurate for the base build, silent on the caveat | README.md:43; `docs/dev/lanes/santriage_report.md` |
| "a portable fallback emitter is on the roadmap" | no corresponding plan row found by grep for "fallback emitter" or "portable" milestone in plan.md/plan_completed.md | GAP or the claim is itself stale — could not confirm a live row |

**What a stranger cannot find in README today**: how to run `make test`
(only `make` and a one-off `gcc` compile are shown), where the spec lives
(`docs/spec/` is never mentioned — only `docs/testing.md`, `docs/dev/`), what
constructs/modules are actually supported (`docs/pcre2_compliance.md` is
never linked), that the repo has 40+ non-corpus test suites and a code-review
process, or that there is a companion benchmark project. No CONTRIBUTING
link, no license badge/CI badge (none exist to link).

## 3. docs/guide/ and docs/spec/ pointers

`docs/guide/` — **does not exist** (`ls docs/guide/` → No such file or
directory). [GUIDE-1]'s full charter (`docs/dev/plan.md:561-571`): a
simplified, human-facing, use-case-organized guide (compile→search/match/
captures/named results; anchored/whole-subject idiom `(?:P)\z`; choosing
engine/options; give-up behavior and the `_in` remedy — D73's obligation at
guide depth, one paragraph pointing at spec; embedding the generated file;
CLI vs library). Explicitly "LOWER PRIORITY, basically maintained, NO
edge-case details." Its stated precondition ("starts after [SPEC-1] has the
limits section it would point at") is **met** — `docs/spec/limits.md`
already has that section (§1 above) — even though [SPEC-1] itself is still
`STATE:started`, not completed (`docs/dev/plan.md:519`).

`docs/spec/` — 8 content files + its own CLAUDE.md, each with a one-line
purpose from its own header:

| file | purpose (from its own header) |
|---|---|
| `cli.md` | the CLI spec — every flag checked against `cli/main.c` and a live binary run; delegates axis/limit NUMBERS to `tuning.md`/`limits.md` |
| `ir_listing.md` | the `--emit-ir` VM-program-listing contract (control structure exact, operands lossy by design) |
| `limits.md` | the resource-bound contract — every give-up/budget number, each traced to its constant/artifact/test |
| `match_api.md` | the generated-artifact and library contract (`lib/pcrec.h` + every emitted matcher's promises) |
| `registry.md` | the TSV column contract for `--list-syntax`/`--list-verbs`/`--list-families` |
| `rxt_format.md` | the `.rxt` test format and driver protocol (three-reader contract) |
| `table_contract.md` | the generic tabular-output wire format every `pcrec` listing surface shares |
| `tuning.md` | the `-f`/`-fno-` optimization-axis family, `--unroll=`, `--engine=` |

A guide chapter's likely spec pointers: "compile a pattern" → `cli.md` §1;
"give-ups and the `_in` remedy" → `limits.md`; "choosing engine/options" →
`tuning.md` + `cli.md`; "embedding the generated file / abi stamp" →
`match_api.md`; "what's supported" → `docs/pcre2_compliance.md` (spec-tier
by ruling, not physically in `docs/spec/` — `docs/dev/plan.md:519`).

## 4. Version plumbing

**None exists.** Greps run: `--version` in `cli/main.c` (0 hits — only
`-h`/`--help` exist, `cli/main.c:726`); `PCREC_VERSION`/`_VERSION_MAJOR`/
`_VERSION_MINOR` across `src/`, `cli/`, `lib/`, `Makefile` (0 hits anywhere
in the tree); pkg-config / `.pc` file (0 hits); `install:` Makefile target
(0 hits — `Makefile` has no install rule at all, `grep -n "^install:"
Makefile` empty). `git tag -l` returns nothing — no tags exist yet.

The `abi` number (unrelated to a product version — it versions emitted
scaffolding, not the tool) is emitted per-artifact and is currently 27
(`[EMIT-VERB]`, `docs/dev/lanes/emitverb_report.md`). It is documented at
`docs/spec/match_api.md` §6 (the single home for the abi change log per
`docs/dev/lanes/w5_report.md`'s D76 addendum) and governed by D76/D94 (grep-
by-number re-pin ritual, `CLAUDE.md`'s situation-index row). **The 0.1 beta
must NOT reset this number** — D113/D114 rule that explicitly (§1 above).
There is currently no separate "product version" concept anywhere in the
tree for a release tag to attach to; `v0.1` would be a bare git tag with no
corresponding in-source constant unless one is built.

## 5. Compliance page freshness

`docs/pcre2_compliance.md` (2,310 lines). Header self-reports (lines 10-11):
**"Last surveyed: 2026-08-09"**, **"Last refreshed: 2026-08-22"**.

This header is ITSELF STALE: the file was substantively edited twice since
without the header being bumped —
- `81817971` (2026-09-12, `docs/dev/lanes/m5close_report.md`): the
  `[M5.0]` close-out compliance-refresh, which patched the unicode-
  properties section's prose in place for the K53 fix (`git show
  81817971 -- docs/pcre2_compliance.md` — a 15-line insertion, no header
  touch).
- `a4ea61e0` (2026-09-19, `[REVW.3]` item 1): a further touch (dump-tier
  move), not inspected in detail here — out of this survey's read budget,
  but confirmed to exist in `git log -- docs/pcre2_compliance.md`.

So the true last-touch is 2026-09-19, six weeks after what the page tells a
reader. The mechanism (`compliance-refresh` skill, `.claude/skills/
compliance-refresh/SKILL.md`) exists and was used correctly on 2026-09-12 —
the header line is simply not one of the fields the skill's own process
re-stamps, per the observed diff.

**Public-reader-shaped assessment (one paragraph, as invited by the
brief):** the page is dense and process-heavy for an outside reader — three
components "held in checked tension," construct-KEYED annotation stores,
`[DOC-DRV]`/`[D65]` citations to internal decision IDs, and a generated
"Registry construct index" that assumes familiarity with pcrec's own
`built`/`unbuilt` vocabulary. It is an excellent internal audit instrument
and a rough "what is supported" page for a stranger; REL-1's charter to use
it as "the public support page" implies at minimum a header-freshness fix
and probably a short front-matter TL;DR a newcomer can read before the
three-component explanation.

## 6. Stranger's build — prerequisites and where stated

From `Makefile` and `docs/testing.md`:

| prerequisite | where stated | notes |
|---|---|---|
| GNU make | `CLAUDE.md` ("Plain GNU make on purpose, D2"); not in README | README's Requirements section (line 43) doesn't say "GNU" specifically, just "make" |
| gcc (or clang) for the base build | README.md:43; `Makefile:13` (`CC := gcc`, no version pin) | Apple clang builds `make`/`make test` on darwin but not `make ubsan`/`make asan`/`make lint` (§2 above, `santriage_report.md`) — this caveat is NOT in README |
| Real GNU gcc version per box, for the FULL suite (san/lint) | `docs/testing.md:4013-4056` "The boxes" — ubuntubudu: gcc 15.2; Mac dev box: Homebrew `gcc-16` (bare `gcc` is Apple clang, resolved via `tests/lib/cc_resolve.sh`) | box-specific, not a hard requirement of the base build |
| python3 | used in 40+ test scripts (grep count, tests/**/*.sh) — no explicit version pinned in docs/testing.md or Makefile | e.g. box's python3 was 3.9.6 in one cited lane report (`hdr2_report.md`'s ecosystem, informally) |
| libpcre2-8-0 (optional) | `docs/testing.md:100-129` — build does not need it; `make test`'s PC-3/PC-4 registry stages SKIP loudly without it; **without headers/lib installed the differential-only stages skip, the base build still links/runs** | README.md does not mention this at all |
| GNU `timeout`/`sed` binaries specifically | `docs/testing.md:4058-4082` ("The `sed` binary itself") and the `timeout` sections cited in `CLAUDE.md`'s situation index — **box-dependent test-harness detail, not a base-build requirement** | irrelevant to `make`/`make test` itself passing, only to some suite scripts' correctness |

**The two boxes** (`docs/testing.md:4013-4056`, quoted in full for a
future reader):
- **ubuntubudu**: Ryzen 5 1600, 12 threads, x86_64 Ubuntu, gcc 15.2, GNU
  userland, libpcre2-8-0 10.46 (the reference oracle), GNU `timeout` at
  `/usr/bin/gnutimeout`. The bench's machine + pcrec's full-suite venue.
- **The Mac dev box**: Apple M1 Max, 10 cores, arm64, macOS. Real GNU gcc
  is Homebrew `gcc-16` (bare `gcc` is Apple clang); bare `timeout` is GNU
  coreutils 9.11; `bash` on PATH is Homebrew 5.3.15 (a box dependency);
  libpcre2 is Homebrew 10.48, NOT the reference (PC-3 reads 119 expected
  reds here, `upstream_issues.md` U13); `ulimit -v` does not bind so
  `tests/resource` Section 2 skips loudly; LSan hangs at exit under
  `detect_leaks=1` (K54) — `SAN_DETECT_LEAKS` derivation disables it on
  Darwin only.

**What a stranger's `make`/`make test` would actually need**: gcc+GNU make
(the two hard requirements), python3 (soft — many suites use it), libpcre2-
8-0 optional (graceful skip). None of this is in README today.

## 7. Contribution posture

- **LICENSE**: exists, MIT, root (`LICENSE`, 1,073 bytes, copyright Frank
  DiCostanzo 2026). README links it correctly (README.md:48).
- **CONTRIBUTING.md**: does not exist.
- **Issue/PR templates, `.github/`**: does not exist at all (no
  `.github` directory, no CI workflow).
- **CLAUDE.md is committed and public-facing**: the repo is confirmed
  PUBLIC on GitHub (`gh repo view fdicostanzo/pcrec` → `"visibility":
  "PUBLIC"`, description "pcre compiler"). The root `CLAUDE.md` — the
  entire lane/manager/subagent workflow, the situation index, the D-number
  decision citations — is visible to any visitor and to any AI agent that
  clones the repo. It is candid internal process documentation (WIP
  commits, "the manager," "lanes," box-concurrency rules) that a stranger
  evaluating the project for contribution will read literally, since it is
  the first file many tools look for. Nothing in the tree currently
  distinguishes "this is our internal process" from "this is how you
  should contribute" for an external reader — that gap is exactly what
  CONTRIBUTING.md (REL-META item a) would need to resolve.
- No `SECURITY.md`, `CODE_OF_CONDUCT.md`, or `FUNDING.yml` found.

## 8. Release-mechanics candidates

- **git tag `v0.1`**: no tags exist (`git tag -l` empty). Nothing blocks
  creating one once a version is otherwise ready.
- **`gh` CLI**: present and current — `gh --version` → `gh version 2.100.0
  (2026-09-03)`.
- **Remote**: `git remote -v` → `origin
  https://github.com/fdicostanzo/pcrec.git` (fetch+push) — matches the
  mandate's named remote exactly. A second remote, `ubuntubudu` (ssh to the
  Linux reference box), is also configured but is not a release target.
- **GitHub release via `gh release create`**: not attempted (this lane is
  read-only and a release is an outward-facing, hard-to-reverse action
  outside its charter) — the tool exists and is authenticated enough to
  answer `gh repo view`, so the mechanical path is open once content is
  ready.

## 9. Size-estimate list

| candidate substep | size | depends on |
|---|---|---|
| Bump `docs/pcre2_compliance.md`'s freshness header + re-run compliance-refresh for real (confirm no drift since 2026-09-19) | S | `.claude/skills/compliance-refresh` |
| README rewrite (Status section, requirements caveats, spec/guide links, test instructions) | S-M | nothing blocking; can start immediately |
| [GUIDE-1] — the user guide itself | M | `docs/spec/limits.md`/`match_api.md`/`tuning.md`/`cli.md` (all exist); D73's guide-depth paragraph |
| A version constant (+ `--version` flag) and deciding what it versions (independent of `abi`) | S | none — pure new surface; must NOT collide with abi's own D76/D94 machinery |
| CONTRIBUTING.md + PR template + RUN-STAMP | M | distilling `CLAUDE.md`/`docs/dev/coding_guide.md`/`docs/dev/learnings.md` into contributor-sized form; deciding what of the internal process (lanes, manager) stays internal-only |
| GitHub Actions CI (test+strict per-PR tier only, per REL-META item b's own ruling that the full gate never runs in CI) | M | none technical; a policy decision on what tier runs on forks |
| git tag `v0.1` + GitHub release | S | everything else above being ready; `gh` already works |
| Stranger's-build verification (fresh clone, both boxes) | S | a scratch clone + the two boxes' existing calibration (§6) |
| Contribution-posture docs (LICENSE already done; add SECURITY.md/CODE_OF_CONDUCT.md if wanted) | S | policy decision, not blocked |
| REL-META's own row (formal disposition, since this survey substitutes for its content but the row itself is still `not-started`) | S | Frank's ruling on whether to formally close/fold it now that this survey exists |
