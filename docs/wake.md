# Wake-up brief — read this first

You are continuing **pcrec**, an ahead-of-time PCRE→C regex compiler.
This file is a hand-off from the previous session. It is deliberately
**not committed** — scratch orientation, not project record. The committed
docs are authoritative; if this file disagrees with them, they win.
(Do not `git add -A -- docs`; it stages this file. Use explicit paths.)

Repo: `/home/duxevents/pcrec` → `github.com/fdicostanzo/pcrec` (public, MIT).
Last session ended with everything committed AND PUSHED (through `cc125b6`);
working tree clean apart from this file. Nothing is in `STATE:started`, so
there is no half-finished work to reconstruct.

---

## 1. Orient (do this before touching anything)

```sh
tail -160 docs/dev_journal.md        # narrative, most recent last
sed -n '1,25p' docs/plan.md          # how the STATE tags work
grep -n "STATE:not-started" docs/plan.md
```

Then, as needed: `APPROACH.md` (architecture), `docs/decisions.md` (**D1–D24**;
**D18–D22** set the strategic frame, **D23** case-insensitivity, **D24 governs
the current work — read it, including its "SR-1 AS BUILT" addendum and its two
same-day corrections**), `docs/pcre2_compliance.md`, `docs/reviews/` (**R1–R4;
R4 is SR-1's and its NOTED items are live**), `docs/known_issues.md` (K2 is
open), `docs/upstream_issues.md`.

**Do not re-derive status from the code.** The docs are kept current on purpose.

## 2. Verify the baseline (~5 minutes)

```sh
make && make test    # 805 corpus, 49 CLI, 112 reject, 127 registry,
                     # 29 codegen, 7 trie-identity, ratchet clean
python3 tests/harness/verify_rxt.py     # expect 100% (796 python-verified cases)
python3 tests/fuzz/fuzz.py --seed 1     # expect 0 divergences
make bench                              # expect 0 budget failures
```
If any of that is red before you have changed anything, stop — the environment
differs (e.g. a different `libpcre2-8`; the fuzz summary prints the oracle
version for exactly this reason).

`make test` takes >2 minutes. Do not run it inside a 2-minute tool timeout.
`bash tests/bench/compare/gate.sh` is the slow one (tens of minutes) and its
floors are machine-specific; run it before and after performance work.

## 3. Where the project is

**M0, M1, all of M2, R3's follow-ups, OS-0b, OS-1, TS-1, PC-1, and now SR-1 are
complete.** Two engines still matter (`ENG_UNANCH` table-driven O(n);
`ENG_ATTEMPT` per-start computed goto for `^` patterns — D18/OS-4 still calls
that split an unearned axis, and it is still unmeasured).

**SR-1 shipped `src/parse/registry.c`**: 67 rows, one declarative home per
non-base construct, guarded by `tests/registry/` (127 checks, 8 sabotage
validations). **`parse.c` does not read it yet.** That is SR-2's job and it is
the whole point — until SR-2 lands, the registry is a sixth copy of knowledge
that already lived in five places, and R4's F11 says so.

## 4. THE NEXT TASKS: SR-2, then SR-3, then SR-4

Frank's instruction at session end: *begin the next few pieces.* That is SR-2
first, then SR-3 and SR-4, which together turn the table from data into the
mechanism D24 designed.

### SR-2 — four dispatch points (the one that pays SR-1's debt)

`pcrec_ext_escape(cx, c, in_class)`, `pcrec_ext_group(cx, c2)`,
`pcrec_ext_verb(cx)`, `pcrec_ext_class_bracket(cx, c2, cls)`. parse.c keeps ONLY
the base grammar and stops growing.

- **The acceptance bar is BYTE-IDENTICAL emitted output across the corpus**,
  proved the way OS-0b proved it: 167 patterns × 3 prefixes × 4 emission modes
  = 1980 hashed outputs. The script pattern is in OS-0b's journal entry.
- The base switch must run FIRST and return before the registry is reachable —
  that is what keeps the common path free, and SR-5 later guards it.
- `tests/registry/`'s 127 checks already pin every diagnostic string SR-2 must
  reproduce. Use them; they were built to be this step's safety net.
- The handler field lands here (SR-1 deliberately deferred it: its four
  signatures are determined by these functions, not by the table).

### SR-3 — `pcrec --list-syntax [--flavour F]`, `--explain '\v'`

The anti-drift mechanism, not a convenience: SR-4 consumes the dump.

### SR-4 — make the dump load-bearing

`tests/reject/` iterates it instead of 93 hand-written entries;
`docs/pcre2_compliance.md` is rendered from it.

- **Keep the accept-controls hand-written.** A control must not share a source
  with the thing it controls (the trie-identity lesson).
- **WARNING from R4:** `\x{...}` and the possessive `+` have NO registry row, so
  iterating the dump silently drops their existing coverage unless SR-4
  special-cases them. Same for anything rejected with fixed text rather than a
  "requires module" diagnostic.

Do NOT build flavours (SR-7) or move the engine check (SR-8); both are deferred
with their forcing functions named.

## 5. Live items R4 left open (read before SR-2)

- **`pcrec_registry_find` takes no flavour argument** and returns the first row
  matching a byte, so SR-1's "short chain for the rare flavour-varying byte" is
  not expressible in the shipped shape. SR-7 must change that signature. Not a
  live bug — duplicates fail loudly today.
- **SR-6 carries an unwritten schema change**: no status value means
  "implemented by module X"; `RS_MODULE` unconditionally implies rejection.
- **The verb doorway's sweep is byte-keyed and the doorway is name-keyed** — a
  name-conditional branch in parse.c would escape it. Needs per-verb rows
  (SR-6). Do not read "all four doorways swept" as "all four equally guarded".
- **Residual circularity**: a NEW construct given the same wrong module in both
  parse.c and registry.c, with no `tests/reject/` row added, is caught by
  nothing. The two tables can drift in row count without either noticing.
- **K2** (docs/known_issues.md): pcrec prints "(backreference/octal)" for
  `\1`..`\9`, describing PCRE2 behaviour that does not exist. Cosmetic today;
  deliberately NOT fixed because SR-2's bar is byte-identical output. Fix with
  module 'backrefs'.
- **Three known second homes**: `\x{...}`, possessive `+`, `\N{U+hhhh}`.

## 6. Other open work, if the SR arc is not the right call that day

- **OS-4** — measure the ENG_UNANCH/ENG_ATTEMPT split, the axis D18 condemns.
- **OPT-A memchr2/memchr3** — two measured customers now. Frank's steer stands:
  **do not optimize yet — get things working first.**
- **MECH-1** — generate the sabotage tables. Still the highest-value process
  item; the battery grew to eight hand-written entries this session.
- **R3.6–R3.10** — floors provenance, the 0.90 ceiling, loose bench budgets.
- **M3.0** — the streaming design gate. *Do not write streaming code first.*
- **DD-9** (dense patterns, ~6x loss) and **DD-10/TS-4** (unbounded
  `compile_ast` recursion). **TS-2/TS-3** — TSan concurrency tests.

## 7. House rules that are easy to get wrong

- **Scope mandate**: touch only this repo. Temp files in the session scratchpad.
  Restate it in every subagent brief.
- **After any significant work**: append to `docs/dev_journal.md`, update
  `STATE:` tags in `docs/plan.md`, update touched `CLAUDE.md` files, commit.
- **Subagents MUST write findings to a scratchpad file AS THEY CONFIRM THEM.**
  All three critics did this session and all three delivered.
- **Run a critic panel at every checkpoint (D6).** SR-1 nearly shipped without
  one; Frank had to ask. Give critics different LENSES, and brief them to attack
  the DEFENCE, not just the target — the most useful thing any of them did was
  run the whole suite against its own sabotage.
- **Critics contaminate benchmarks.** Check `uptime` before AND after any
  measurement; do not measure while a subagent runs.
- **Behaviour-preserving changes need a structural test**, sabotage-validated,
  and **record the exact sabotage EDIT, not just the count**.
- **Check the artifact a stranger gets**: `git clone && make && make test`.

## 8. Hard-won lessons worth not relearning

- **PCRE2 is the authority; the corpus's oracle is python `re`, and they
  disagree.** Four constructs so far where python CERTIFIED a divergence rather
  than catching it. Verify anything new against libpcre2 directly — there is a
  working `dlopen` probe pattern in the R4 scratchpad work, and
  `tests/fuzz/pcre2_oracle.c` in the repo.
- **Do not write a semantic note from memory.** SR-1 shipped nine rows saying
  `\1`..`\9` fall back to octal (Perl/PCRE1 behaviour that PCRE2 does not have).
  Found by a critic in hours, in the very file built to stop that class of error.
- **A test's documentation drifts toward what it was MEANT to do.** SR-1's sweep
  covered two of four doorways while three documents claimed four.
- **"True by construction" is not a test.** Twice in one session I argued a
  structural guarantee instead of testing it, and both were holes.
- **A check that iterates what EXISTS cannot see what is MISSING.** Deleting two
  rows was invisible to 116 checks. A coverage floor answers "did someone delete
  a lot", never "did someone delete the right ones" — use a hand-written
  manifest.
- **The compiler is not where the bugs are — the SPEC-TO-CODE GAP is.** Five
  checkpoints and ~54M oracle-checked comparisons: zero compiler defects.
  Afternoons of reading PCRE2's syntax reference: three real errors.
- **A wrong citation propagates fast.** D24's TS-1 miscitation was copied into
  two source files within hours. The cost scales with how quotable it is.
- **Over-rejection is as wrong as under-rejection**, and a positive control must
  fire INSIDE the corpus's own range.
- **Measure before describing.** It keeps producing smaller, better answers than
  the one about to be written from memory.
