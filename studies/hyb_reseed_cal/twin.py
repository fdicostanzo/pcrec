"""studies/hyb_reseed_cal/twin.py — the HAND-TWIN transformer.

usage: twin.py BASE_ARTIFACT.c TWIN.c

Reads an artifact emitted by the BRANCH-POINT compiler (abi 46, whose
clamp-free retry steps) and writes a twin whose retry tail is chosen at
build time by -DTW_MODE: 0 step (the abi-46 retry), 1 always re-seed,
2 one-short-gap step block, 3 two-short-gap step block, 4/5 variants that
also read the entry gap, 6 the doubling block (the shipped shape, with
TW_N gap, TW_K block, TW_CAP cap, TW_INIT first budget, TW_SHORT0 initial
short count). Every TW_* macro has a default below, so each script passes
only what it varies. The twin's answers are checked against the base's by
drv.c's span hash in every script that uses it.
"""
import sys, re
src = open(sys.argv[1]).read()
lines = src.split("\n")
out = []
i = 0
# decl before the for(;;) of rx_search_run: insert after "ctx.caps = NULL; ctx.user = NULL;"
done_decl = False
for idx, l in enumerate(lines):
    if l.strip() == "size_t attempt_position;":
        out.append(l); out.append("    size_t tw_entry_gap = 0; (void)tw_entry_gap;"); continue
    if not done_decl and l.strip() == "ctx.caps = NULL; ctx.user = NULL;":
        out.append(l)
        out.append("    unsigned tw_steps = TW_INIT, tw_short = TW_SHORT0, tw_block = TW_K; (void)tw_steps; (void)tw_short; (void)tw_block;\n#if TW_MODE >= 4\n    tw_short = tw_entry_gap < TW_N; if (TW_MODE == 5 && tw_short) tw_steps = TW_K;\n#endif")
        done_decl = True
        continue
    if l.strip() == "attempt_position = (size_t)window[0][0];" and not done_decl and 'entry_done' not in globals():
        globals()['entry_done']=True
        out.append(l)
        out.append("#if TW_MODE >= 4\n        tw_entry_gap = attempt_position - search_from;\n#endif")
        continue
    if l.startswith("    if (capture_spans) rx_report_captures") and out[-1] == "    }":
        closing = out.pop()
        out.append("""#if TW_MODE == 1
        { ptrdiff_t window[1][2]; if (rx_prefilter(subject, subject_length, attempt_position, window) != 1) return 0; attempt_position = (size_t)window[0][0]; }
#elif TW_MODE == 2
        if (tw_steps) tw_steps--;
        else { ptrdiff_t window[1][2]; const size_t tw_from = attempt_position; if (rx_prefilter(subject, subject_length, attempt_position, window) != 1) return 0; attempt_position = (size_t)window[0][0]; if (attempt_position - tw_from < TW_N) tw_steps = TW_K; }
#elif TW_MODE == 3
        if (tw_steps) tw_steps--;
        else { ptrdiff_t window[1][2]; const size_t tw_from = attempt_position; if (rx_prefilter(subject, subject_length, attempt_position, window) != 1) return 0; attempt_position = (size_t)window[0][0]; tw_short = attempt_position - tw_from < TW_N ? (tw_short < 2 ? tw_short + 1 : 2) : 0; if (tw_short >= 2) tw_steps = TW_K; }
#elif TW_MODE == 6
        if (tw_steps) tw_steps--;
        else { ptrdiff_t window[1][2]; const size_t tw_from = attempt_position; if (rx_prefilter(subject, subject_length, attempt_position, window) != 1) return 0; attempt_position = (size_t)window[0][0];
          if (attempt_position - tw_from < TW_N) { if (tw_short < 2) tw_short++; if (tw_short == 2) { tw_steps = tw_block; if (tw_block < TW_CAP) tw_block *= 2; } }
          else { tw_short = 0; tw_block = TW_K; } }
#elif TW_MODE == 4 || TW_MODE == 5
        if (tw_steps) tw_steps--;
        else { ptrdiff_t window[1][2]; const size_t tw_from = attempt_position; if (rx_prefilter(subject, subject_length, attempt_position, window) != 1) return 0; attempt_position = (size_t)window[0][0]; tw_short = attempt_position - tw_from < TW_N ? (tw_short < 2 ? tw_short + 1 : 2) : 0; if (tw_short >= (TW_MODE == 4 ? 2 : 1)) tw_steps = TW_K; }
#endif""")
        out.append(closing)
    out.append(l)
assert done_decl
prelude = "".join(f"#ifndef {m}\n#define {m} {d}\n#endif\n" for m, d in
                  (("TW_MODE", 0), ("TW_INIT", 0), ("TW_SHORT0", 0), ("TW_N", 1), ("TW_K", 1), ("TW_CAP", 1)))
open(sys.argv[2], "w").write(prelude + "\n".join(out))
