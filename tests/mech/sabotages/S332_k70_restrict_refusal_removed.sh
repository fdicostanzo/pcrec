# S332 — K70's (?r) refusal REVERTED under -e utf8: `mod_modifiers.c`'s
# `case 'r':` stops consulting `PcrecEnc.restrict_ok` and goes back to a
# bare `break` (the pre-fix "measured no-op at options=0" text) — `(?r)`
# silently accepts again under `utf8`, restoring the tier-1 miscompile K70
# fixed (docs/dev/known_issues.md K70: `(?i)(?r)k` matches U+212A on pcrec
# where libpcre2 10.46 answers nomatch).
SAB_ID="S332-k70-restrict-refusal-removed"
SAB_FILE="src/parse/mod_modifiers.c"
SAB_SUITES="harness cli"
SAB_HARNESS_TARGET="tests/utf8/restrict.rxt"
SAB_DESC="case 'r': stop consulting PcrecEnc.restrict_ok and always break (the pre-K70 no-op) — (?r) silently accepts under -e utf8 again"
SAB_DOC_FIGURE="harness: tests/utf8/restrict.rxt's five utf8 perr blocks ACCEPT instead of refusing (red); cli: run_cli_tests.sh's K70 block's refusal cell reads ACCEPTED (red). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S332."
# [MECH-REACH] the plant is reached on a real byte encoding compile too
# (case 'r' still runs there) — the byte control in tests/utf8/restrict.rxt
# section 1 stays green under the plant, which is what makes this row's
# harness detection specific to the utf8 arm rather than a population
# artifact.
SAB_REACH='"$PCREC" --features all -e utf8 --pattern "(?i)(?r)k" >/dev/null 2>&1; echo $?'
SAB_REACH_EXPECT="1"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (!hyphen) {
                const PcrecEnc *e = pcrec_enc_by_id(cx->opt->encoding);
                if (!e->restrict_ok) {
                    char buf[112];
                    snprintf(buf, sizeof buf,
                             "inline option '"'"'r'"'"' (caseless-restrict) is not "
                             "implemented under encoding '"'"'%s'"'"'", e->name);
                    return modport_refuse(want, i, buf);
                }
            }
            break;'
SAB_AFTER='            break;                        /* SABOTAGE S332: pre-K70 no-op */'
