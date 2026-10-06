# studies/artrev -- run recipe

One artifact lives in `build-artrev/<name>/` (`ARTREV_ROOT` overrides):
`artifact.c/.h/.s` (the pin), `meta.json`, `GENERATION.txt` (pin, abi, gcc,
generation line, asm line, compile line), `arms/<arm>/artifact.c`,
`twins/<arm>.rN.patch`, `identity/`, `timing/NNN/`, `iterations.tsv`.

    export ARTREV_CC=gcc-16            # Mac: Homebrew gcc; bare `gcc` there is clang and is REFUSED
    A="python3 studies/artrev/artrev.py"

    # 1. generate at the pin (a pcrec binary built at the pin sha; --pin records it)
    $A gen NAME --pcrec BIN --pattern 'a(b|c)+d' [--flags=--no-captures] [--prefix rx] --pin SHA
    studies/artrev/gen_selection.py --pcrec BIN --pin SHA --pilot|--all|--ids A01,A07

    # 2. twin: the standing arms, then each lead (a lead id = the arm name, e.g. L1)
    $A twin NAME null --null                     # the noise control, rides every timing run
    $A twin NAME L1 --new                        # copies the original; edit arms/L1/artifact.c
    $A twin NAME L1 --seal                       # diff -> twins/L1.rN.patch, checked + logged
    $A twin NAME L1 --patch FILE                 # or apply a patch against the pinned artifact
    #    REJECTED (exit 4): intrinsics headers, __builtin_ia32_/neon, vector_size,
    #    #pragma GCC optimize/target, __attribute__((optimize/target)), _mm*, NEON types,
    #    any artifact.h change.  Controls (self-test) use --control and are not counted.

    # 3. identity -- zero differences is the bar before ANY timing (time refuses without it)
    $A identity NAME L1 [--subject FILE]... --corpus --battery 3000 --block 16 [--san]
    #    transcripts of orig and twin must be byte-identical over S/SI/M/MI/C/CI/N/V and the
    #    find-all walk; libpcre2 sample (10.48 Homebrew on the Mac: noted, not the 10.46 oracle)

    # 4. time: orig, orig2 (recompiled original), null, then leads; interleaved rounds
    $A time NAME --arms orig,null,L1 --subject cell=FILE [--subject dense=FILE ...] --rounds 11
    $A time NAME ... --remote ubuntubudu         # 08:00-19:00 local only; --dry-run prints the commands

Hardened identity (charter S1-S3, 2026-10-06) -- all part of the plain `identity` call:
- the compile line carries `-DARTREV_HAVE_IN=1` when the artifact has `_in` entries (before this fix
  no `_in` shape was ever driven; the summary now prints how many `_in` search lines were);
- SHRUNKEN RESOURCES: both arms rebuilt with RX_STEP_BUDGET/RX_WORK_BUDGET shrunk (`--shrunk-budgets
  8:64,64:1024,2000:40000`) and every `_in` shape driven with {0,1} frames x {0,1} trail; transcripts
  compared under THE GIVE-UP RULE (identity.py docstring): original gives up + twin answers = a REPAIR,
  legal only if equal to libpcre2's answer (checked, counted, printed); twin gives up where the original
  answers, or answers differently = FAIL.  `--strict-giveup` also fails every repair;
- WINDOW START: an artifact with an internal `<p>_prefilter` gets orig-vs-twin window differential at
  every search_from (driver_pf.c); a start that moves early fails here, not by a 900 s timeout;
- LIVELOCK BOUND: the twin's driver runs under max(30 s, 25 x the original's wall)
  (`ARTREV_LIVELOCK_FLOOR` lowers the floor, self-test only in practice);
- `--skip-shrunk` / `--skip-window` log PASS-PARTIAL, which `time` refuses.

Layout control and cell (timing, charter S4):

    $A time NAME --arms orig,orig2,null,L1,L2 --subject a=F1 --subject b=F2 --subject c=F3 --cell a,b,c \
         --pads 16,32,48,64 --pad-arms orig,L1 --rounds 11 [--remote ubuntubudu]
    $A variants NAME --subject CELLFILE --out-dense D.bin --out-sparse S.bin

`--pads` (>=4 multiples of 16) rebuilds `orig` and the `--pad-arms` at those code offsets and times them
in the same interleaved rounds; the verdict then also needs the win to exceed both arms' spread across
pads and to agree at every paired pad (timing.py docstring).  `--cell` adds the CELL row (per round,
per arm, the median over the named subjects = the bench's cell number).  `confirm_prep.sh` rebuilds
the pilot's artifact roots from the pin and imports the reviewers' twins (docs/dev/optloop/artrev/
confirm_plan.md uses it).

Bounds (charter 3.1, enforced from `iterations.tsv`; exit 3 = refused): at most 6
leads per artifact, 4 revisions per lead, 3 timing runs per revision. Every twin
revision (rejected ones included) and every timing run (failed ones included) is a
ledger row. A load-gate refusal (exit 7) starts nothing and is not logged.

`time` refuses (exit 5) while `worktrees/.mac-suite.lock` exists (file OR directory),
while another timing run holds `build-artrev/.timing.lock`, or when load1 stays above
the gate (default 2.0 on darwin, 0.5 elsewhere; `--load-max`). Every run is under
`scripts/watchdog` (wall 10 min, RSS 2 GB; `--wall`, `--rss-kb`).

Verdict (charter S4): an arm WINS if its median beats the original's by more than BOTH
the null twin's deviation from the original AND the IQR (the larger of the arm's and
the original's); LOSS by the same rule reversed; else NOISE. Mac numbers are SCRATCH
(they steer iteration and are never reported); reportable timing is ubuntubudu by day.
The remote wrapper bundles the arms, takes `~/scratch_lx/artrev/.timing.lock`, runs
`gnutimeout ... scripts/watchdog ... _rawtime` with `ARTREV_REMOTE_CC` (default `gcc`)
and copies `raw.tsv` back; it cannot see a declared bench window, only the hour.

The ONE compile line: `$CC -O2 -fPIC -I<arm> -DARTREV_PFX=p -DARTREV_PFXU=P
[-DARTREV_HAVE_IN=1] shim.c <driver>.c` (the bench's `$CC -O2 -fPIC -shared shim.c`
with the artifact #included; pcrec-bench `testees/pcrec/adapter.py` "COMPILE COST",
`shim.c` header). `-S` asm is the same TU. `--san` only ADDS
`-fsanitize=address,undefined -fno-sanitize-recover=all -g` and is never timed.

Self-test: `bash studies/artrev/selftest.sh 2>&1 | tee studies/artrev/selftest.log`.

Reviewer cell and leads (charter 3.2): the D27 cell allowlist for a reviewer is
`docs/spec/`, `studies/artrev/`, its artifact directory AND
`docs/dev/optloop/artrev/notebook/`. The harness does not define or validate
`leads.tsv`; its schema is the charter's, with the added `origin` column
(`fresh` or `notebook:<entry>`).

## Inside a D27 cell: set ARTREV_HOST_ROOT

A cell's own tree is not where the shared locks live. Every reviewer
running in a cell exports `ARTREV_HOST_ROOT=/Users/fdicostanzo/pcrec` (the
main checkout) so that `time` takes the ONE shared
`build-artrev/.timing.lock` and checks the real
`worktrees/.mac-suite.lock`. Without it, each cell would hold a private
timing lock and two reviewers could time at once (lane artprep's finding,
2026-10-06). Self-test note: `orig2` reading LOSS once under a
gate-overridden, heavily loaded Mac (load1 ~20) is load noise, and a re-run
on a lighter box was 101/101; the real gate exists to refuse those runs.
