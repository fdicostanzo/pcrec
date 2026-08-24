# The RFC 5322 email specimen — original vs subroutine-factored (2026-08-24)

Frank's specimen (`orig.rx`, 426 bytes, the widely copied "RFC 5322"
email pattern; validity unimportant): the first REAL member of the
population subroutines_design.md §8.4 found empty — calls as FACTORING,
not recursion. `factored.rx` names the four textually repeated
sub-languages (`atom`, `qchar`, `label`, `octet`) with the `{0}`-callee
idiom and `(?&name)` calls; `factored_x.rx` is the same under `(?x)`.
Measured by the srEmail lane (sonnet) on MAIN = post-A2 main and BC =
lane/srBC (wave B+C, calls compile and match), oracle libpcre2 10.46
through the project's ctypes chain, 85 subjects (`manifest.tsv`,
regenerable by `gen_subjects.py`) + three 1 MB throughput subjects.

## Results

- Oracle self-check: orig and factored AGREE under libpcre2 on 85/85.
- MAIN/orig and BC/orig: 0 disagreements with libpcre2 on 85/85; the
  two compilers agree on all 85 (B+C changed nothing for a call-free
  pattern).
- BC/factored: 0 answer disagreements, but FIVE `PCREC_ERR_FRAMES`
  give-ups on deep-repetition subjects (2000-deep `a.a.a…`, 5 KB quoted
  strings, 500-label domain): every `(?&x)` iteration is a CALL and a
  call is a resume frame that survives its return (§5.1/§5.3, S-SR3),
  so a 2048-frame default artifact gives up ~2 K iterations in.
- Artifacts: MAIN/orig and BC/orig are the DFA engine with the
  byte-class skip prefilter (51 KB); BC/factored is the VM engine
  (the `{0}` definitions' named groups are CAPTURES, so engine
  selection forces VM), NO prefilter, 5 `goto *` sites, 53 KB.
- Throughput (1 MB, median of 5): (a) valid addresses — 13.4 / 14.9 /
  53.8 ms (MAIN/orig, BC/orig, BC/factored) vs libpcre2 30.4 ms;
  (b) no `@` at all — 6.5 / 6.9 / **155.0** ms vs 0.025 ms (the
  prefilter loss, ~23×: wave G's number); (c) 1 MB of `a` — 4.0 / 7.4
  ms / **PCREC_ERR_STEPS after ~6 s** vs 0.018 ms: the VM without its
  rungs (rung admission declines call-bearing bodies, D71.6) exposes
  the pattern's classic `atom+(\.atom+)*` backtracking shape, which
  the DFA structurally cannot.

## The conclusion (manager, same day)

Factoring with calls is today STRICTLY WORSE than the hand-inlined
pattern on every axis except readability — and every one of the three
losses has one cause: the callee is emitted as a CALL, which forces
the VM, drops the prefilter, declines the rungs and keeps a frame per
iteration. For an ACYCLIC callee wave G's SPLICE removes all of them
at once — and one more step makes factoring FREE: a definition group
that is reached ONLY through calls (its `{0}` occurrence never
matches lexically) can never leave a VISIBLE capture, because the
return RESTORES every slot the callee wrote (§3.1) — so its capture
slots are dead, engine selection may treat the pattern as
capture-free, and the DFA engine applies. The checkable bar for wave
G: `factored.rx`'s artifact is BYTE-IDENTICAL (modulo the pattern
stamp) to `orig.rx`'s. Recorded on plan row [DD-14.G].
