# lflaxtri — triage of lane/lfl0's test-axes red (2026-10-10)

Scope: report plus proposed fix; nothing applied to lane/lfl0 or to this
branch's tests. Sides measured per case with `RXTFLAGS` + `RXTDUMP` through
`tests/harness/run.sh` (the sweep's own mechanism) on main's tip 33b47662
(own worktree build) and on `worktrees/lfl0/build/pcrec` (f59672aa, executed
read-only). The three corpus cells were extracted into small `.rxt` files
(patterns and subjects verbatim); libpcre2 10.46 called through ctypes.

## Verdict

All three cases are class (b)+(c): the behaviour is BYTE-IDENTICAL on main and
lfl0 (lfl0 is a true no-mover here), and the cases are legitimate
default-answers / denied-axis-budget transitions of an already-allowed shape
that nobody had enumerated, because their corpus cells entered the tree after
main's last whole-corpus test-axes. Fix: five `GIVEUP1_ALLOWANCE` rows
(Group H). No code finding.

## Per-case table

Cell format: `trc/out`. "def" = no axis flag.

| case | axes | main def / axis | lfl0 def / axis | class | mechanism |
|---|---|---|---|---|---|
| nullable_anch.rxt line 48, `^(([a-z]+)*)+$` on 17 letters + `!` | `-fno-prefilter`; `--engine=vm`; `--engine=vm -fno-start-set` | 0/nomatch / 3/steps | 0/nomatch / 3/steps | (b)+(c) | default artifact has `RX_VM_PREFILTER "hybrid"` (exact prefilter, nomatch in linear time); `-fno-prefilter` gives `"none"`; `--engine=vm` disables the DFA prefilter (tuning.md section 2.11) so `"none"` too. The catastrophic VM then exhausts its step budget. Same as allowance Groups B and G1. |
| nullable_anch.rxt line 67, `^(\s+)*$` on 32 blanks + `x` | same three | 0/nomatch / 3/steps | 0/nomatch / 3/steps | (b)+(c) | identical mechanism, second pattern of the file's two "give-up cells" |
| composition_d27.rxt line 8336, `a*(?R)?b` (features all) on `1- ` | `-fno-req-byte` | 0/nomatch / 3/frames | 0/nomatch / 3/frames | (b)+(c) | default artifact has `RX_REQ_BYTE "98"`, `RX_REQ_WHY "emitted"`: one memchr for `b` proves nomatch. `-fno-req-byte` gives `"none"`; the left-recursive walk exhausts the frame budget. Same as allowance Group E4 (recursion, frames). |

Not lfl0-caused (a): every cell above is identical across the two builds, and
the emitted `RX_*` stamps compared (`RX_VM_PREFILTER`, `RX_REQ_BYTE`,
`RX_REQ_WHY`, `RX_ENGINE_SEL`) are the same on both for default and each axis.

Why main never flagged them: the last whole-corpus test-axes on main ran at
041e450a (2026-10-06; journal "overnight, 10-07"). `git merge-base
--is-ancestor` shows composition_d27.rxt (27455a1d, 2026-10-07) and
nullable_anch.rxt (321ea68f, 2026-10-08) are both AFTER it. The cells were
never swept on main; lfl0's landing run is the first whole-corpus sweep to
reach them. Same pattern as axtri's Group E5 (cells landed after the last
sweep). The nullable_anch file's own comment says line 48 and 67 cells were
"the default VM gave up" before the NULLABLE-ANCH decline lift; the axes
reproduce exactly that old behaviour, which is what a deny axis is for.

Answer correctness (libpcre2 10.46, interpreter, no JIT, default limits):
case 3 returns -1 (no match), agreeing with pcrec default. Cases 1 and 2
return -47 (match limit) in the interpreter here; the corpus rows are marked
`pcre2-only` and record nomatch, so their oracle answer came from a different
configuration than my ctypes probe. Not investigated further (it does not
affect the class: pcrec default and lfl0 default agree with each other and
with the corpus). Worth one line to whoever owns those cells if the oracle
configuration is not recorded.

The composite axis `--engine=vm -fno-start-set` needs no key of its own: the
allowance lookup (tests/axes/run_axes.sh, the `for _c in $flags` fallback)
tries each whitespace-separated part, so a `--engine=vm|...` row covers it
(the same way Group F's fno-start-set rows are consulted).

## Allowance rules honoured

Keyed by exact `<flags>|<file:line>` (a manifest, never a count); each row's
text names the mechanism and direction; the group header records the live
measurement; and the mechanisms are existing documented ones (prefilter loss,
necessary-byte pre-check loss), not a blanket excuse. Total new rows: 5
(4 + 1). Neither lfl0 nor main changes answers; the expected post-fix lfl0
log reading is `giveup1-allowed` +2 on each of the three nullable_anch axes and +1
on `-fno-req-byte`, with `giveup1-unallowed=0`.

## Proposed fix

An exact diff against `tests/axes/run_axes.sh` at main 33b47662 is in
`docs/dev/lanes/lflaxtri_allowance.diff` (applies with `patch -p0` from the
repo root; `bash -n` clean). It inserts a "GROUP H" comment block and five
rows after the last Group G row. It is kept as a separate file because the
rows follow the neighbouring rows' spelling, which cites tuning.md sections
with the section sign; the spec-history check rejects that form in reports.
It was NOT applied to the tests tree: modifying the allowance is the
manager's call. Not re-run end to end (a per-file `run_axes.sh` run needs the
rows in the tree); the manager can verify with
`AXES="-fno-prefilter" bash tests/axes/run_axes.sh tests/base/nullable_anch.rxt`
after applying.

Late finding check: the lfl0 axes log was still running at report time; the
list of AXIS FAIL lines I saw reduced to these three cases only. Re-grep it
at the end: `grep 'AXIS FAIL' worktrees/lfl0/build/land/axes.log | grep -v
'nullable_anch.rxt:\(48\|67\)\|composition_d27.rxt:8336\|mismatch(es)'`.
