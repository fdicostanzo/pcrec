# S185 (S-OPTK1) — [OPT-K] THE OFFSET-k SKIP RESUMES PAST A REAL CANDIDATE.
#
# `docs/design/offset_k_skip.md` §5.2. After a candidate fails its verify
# chain, the emitted helper resumes the scan at `cand + 1` — one position
# later, so the next `memchr` starts at `hit + 1` and no position is either
# examined twice or skipped. The obvious wrong version resumes at
# `cand + 1 + k*`, which reads naturally ("start after the byte we just
# looked at") and SKIPS EVERY REAL MATCH CLOSER THAN k* TO A FAILED
# CANDIDATE.
#
# IT IS A LOST MATCH, NOT A SLOWDOWN, and that is why it is a sabotage row
# rather than a bench floor. On `\d{4}-\d{2}-\d{2}` the scan is `memchr('-')`
# at offset 4, so `"1234-2026-08-28"` has a failing candidate at 0 (its
# offset-4 `-`) one byte before the real match at 5 — and the wrong resume
# jumps from 1 to 5+4, past it.
#
# WHY tests/offsetskip CANNOT BE THE ONLY DETECTOR. Every `n` row in that
# file passes under this sabotage (a skip that refuses too much still refuses
# everything it should), so only its §4 OVERLAPPING-CANDIDATE `m` rows fire —
# rows that exist for this defect and would be the first thing an editor
# trimmed as redundant. `tests/codegen/run_offset_skip.sh` §2 reads the
# resume line itself on all four witnesses, so the row is detected by a check
# that names the LINE as well as by cells that name the ANSWER.
SAB_ID="S185-ofsskip-resume-off-by-one"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness offsetskip"
SAB_HARNESS_TARGET="tests/offsetskip/offset_skip.rxt"
SAB_DESC="the emitted offset-k skip resumes its scan at cand + 1 + k* instead of cand + 1 after a failed candidate, so any real match closer than k* to a failed one is skipped entirely — a LOST MATCH, invisible to every no-match cell"
SAB_DOC_FIGURE="PRE-VALIDATED (2026-08-28, lane optk): DETECTED against a clean 19pass/0fail + 80pass/0fail baseline -- offsetskip:4fail/19pass, corpus:1fail/79pass. The corpus arm is ONE case and had to be BUILT: this plant first measured 0 corpus failures, because a pattern can only turn the off-by-one into a lost match if it ALLOWS its own scan byte before the offset it is scanned at, which none of the four witnesses does. tests/offsetskip gained [-a]{3}-b for exactly this row."
SAB_COUNT=1
SAB_BEFORE='    sb_puts(c,   "        pos = cand + 1;\n"'
SAB_AFTER='    sb_printf(c, "        pos = cand + 1 + %d;\n", ofsk_scan(f)->k);   /* SABOTAGE S185 */
    sb_puts(c,   ""'
