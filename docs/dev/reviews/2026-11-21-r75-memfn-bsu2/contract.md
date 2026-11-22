# CRITIC contract: memfn-bsu2 (r75)

## Findings

### CONTRACT-1 CONFIRMED (doc; effort: one sentence in two spec rows, or a decision; blast radius: width-4095 window sites within ~330 bytes of the code cap)
The wrapper's SIMD-off bytes push a pattern that compiles at BASE over `PCREC_MAX_VM_EMIT_CODE_BYTES` (500000), and no spec sentence says the default (rather than only span-loop's deny) can now be refused.
Repro (pattern in contract/cap_witness.txt): P='[0-9a-f]{1000}(?:[g-mA-FQUW][n-zG-KRTV]){940}', `--window-search-width=4095`:
- BASE `R/base/build/pcrec`: rc=0, 499743 bytes of code.
- SUBJECT default: rc=1, "pattern too large: 500060 bytes of emitted code (limit 500000) ... lower a count, try --unroll=1, or raise --max-emit-code-bytes".
- SUBJECT `--memfn=no-span-vector`: rc=0, 499743 (= BASE). The same holds at `-fmemfn-simd=x86-64-v3` (500063, refused).
- At N=941 both refuse, so the band is about 317-332 bytes wide (the wrapper's two heads and its call). Trace: wfS at=0 k=1000 T-vwin.
Expected per the contract: registry.md §6¶8a `span-vector` says only "Answer-identical". tuning.md §2.43¶3d says the cap refusal applies to "the deny (and a lever head that high) ... where the default compiles". Both are now false in this band, because the default refuses where the deny compiles (the reverse direction). The refusal message names levers (--unroll=1, which does not help here) but not `--memfn=no-span-vector`, the one that does.
Fix: either a sentence in the span-vector row and ¶3d ("its function heads add a few hundred bytes; near the emitted-code cap the default can be refused where the deny compiles"), or have the V rows decline when the site's text would cross the cap. Contrived (non-default width, about 2,900 positions), so doc severity.

### CONTRACT-2 CONFIRMED (doc: a caller-visible U3 sentence landed at U2; effort: rewording one string, or noting it as U3-forward; blast radius: `--list-axes` text and every reader of it)
`memfn/src/options.def` (the `span-vector` row's help string, from design §7's proposal verbatim) is printed by `W/build/pcrec --list-axes` (line 229) as: "long window spans of one byte set are tested by a function that, under -fmemfn-simd at a target with 32-byte vectors, tests 32 (or 16) bytes per step". At U2 no layer does this. `-fmemfn-simd=x86-64-v3` on `[0-9a-f]{32}` emits `rxa_mf1_vs0` calling `rxa_mf1_vs0__body` (the scalar text), `RXA_MEMFN_FORMS "none"`, and the default-vs-deny diff is the same 10 lines as at -fno-memfn-simd. The abi changelog says the opposite ("The vector helper itself (unit U3) renders no byte yet").
A related gap: registry §6¶8a's row and tuning §2.43¶3d say that "with SIMD off (and at a target without 32-byte vectors)" the body is the former inline text. They say nothing about a w32 target, so a reader infers a different text there. At U2 it is the same at every target.
Expected (D80, COMMON "a U3 sentence landed early"): at U2 the help and the spec say "at every setting, a call of a function whose body is the former inline text (a SIMD body is a later unit)", or the help omits the w32 clause until U3 lands. Also "(or 16)": design §3.3 says a w16-only target gets `__body` (no w16 form), so even at U3 "16 bytes per step" holds only for the w32 helper's cascade (§4.4), not for a 16-byte target. Worth checking the words then.

### CONFIRMED CONTRACT-3 (doc, minor; effort: two words; blast radius: callers using a finder deny)
registry §6¶8a's `span-vector` row and tuning §2.43¶3d say "24 to 64 where it [the window search] walks to the stop". Finder row D1w is also a walk to the stop (finder.c:280 "the table walk", FF_WALK), and the code excludes it on purpose (design §3.3, keyed on R7w alone). Repro: `ab[0-9]{26} --memfn=no-fd-d1` (trace: fd D1w, wfS at=2 k=26 T-head, no `_vs0`). That site walks to its stop, k is 26 (in 24..64), and it is not wrapped. A caller reading the spec would expect a call. Fix: "walks to the stop with the default set walk" or "(not under a finder deny)". It answers nothing and it is not a byte bug, so doc severity.

## PROBED-AND-HELD

(a) Spec and abi:
- D94 reader grep, unfiltered (`git -C W grep -n -w 109|111 -- src tests docs/spec docs/testing.md memfn`, 211 and 103 hits, read by file): every abi reader moved. That is emit_dfa.c PCREC_ARTIFACT_ABI, match_api §1's three guard lines, §6's row, §6¶17, run_codegen_tests ABI_EXPECT, S693 BEFORE/AFTER (111/109), and recursion identity FILEPIN. ABASEPIN is unchanged, as the commit states. The provenance line reads "abi 111". The subst `_v%d` suffix is generated from the constant (emit_subst.c:529), and no tree text spells v109/v111. The remaining 109 hits are PCRE2 error 109, line numbers and counts. The abi_changelog paragraph matches behaviour (no MEMFN_FORMS token, "none" at v3; no rx_info change).
- registry floor 15 = `--list-axes` memfn rows (BASE 14). The row order matches options.def. trace_format's `at=I k=K` after `phase=` matches the trace's ROW/SEL/END lines.
- Default vs deny at -fno-memfn-simd and at -fmemfn-simd=x86-64-v3 (`[0-9a-f]{32}`): exactly the two file-scope functions plus the one replaced call. The abi number is the same in both.
(b) Edges (trace-subj, wfS END):
- T-vwin k15 no / k16 V (`[0-9a-f]{16}`/`{17}`); k1000 V / k1001 no (`{1001}`/`{1002}` at 4095).
- T-vscan k23 no / k24 V (`[0-9]{24}`/`{25}`); k63, k64 V / k65 no (`[0-9]{64,65,66}` at 4095).
- D1w excluded: `ab[0-9]{26} --memfn=no-fd-d1`, k26, T-head.
- First eligible stretch only: `[0-9a-f]{20}[g-z]{20}` at 4095 gives k20 V, then k19 T-head. When an ineligible stretch comes first (`[0-9a-f]{5}[g-z]{20}`), the later one gets V.
- Order: span-loop force and deny win over V, and so do no-span-vector,span-loop. The admitted R7w shapes (`--memfn=no-window-skip`, `[0-9a-f]{31}[0-9]`) take V. utf8 routes the bench texts to T-vscan. --engine=vm takes none.
- `own` (a C-table stretch): no reaching pattern found (fused, PAIR, D1, literal-prefix shapes all T-head, gcc-clean).
- Answers vs libpcre2-8 on 18 V instances x 60 boundary subjects (match at end, one short, truncated, mutated position, non-ASCII byte), byte/utf8, widths 32/4095, off/v3: 0 mismatches / 1080.
- A 60-char prefix compiles. gcc and clang -Wall -Wextra -Werror are clean on 3 artifacts.
- Caps: only PCREC_MAX_VM_EMIT_CODE_BYTES is reachable by the wrapper's bytes (CONTRACT-1). PCREC_MAX_EMIT_BYTES (1M, the whole artifact) binds only after the code cap here, since a window site's tables are small. That is inferred, not run. No state or node cap reads kit text.
LARGEST witness: `[0-9a-f]{1000}(?:[gikmoqsuwyGIKMOQSUWY][hjlnprtvxzHJLNPRTVXZ]){1547}` at width 4095 (4094 positions, 2.2 MB code, refused at both trees). LONGEST V stretch: k=1000. About 110 compiles used.

CRITIC COMPLETE
