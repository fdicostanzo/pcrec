# S200 (S-C9) — [DD-13b.W1.1] `--list-source` emits a literal TAB in the
# `pattern` column instead of escaping it, so the row splits and every
# later column shifts.
#
# THREE ROWS OUT OF 3,265, WHICH IS EXACTLY THE SIZE OF FINDING A SUMMARY
# SWALLOWS. The corpus carries a literal tab in three patterns —
# tests/base/bounded_repeats.rxt's `a{\tab1}` and `a{ 1\tab,\tab2 }`, and
# tests/modifiers/xxmode.rxt's `(?xx)[a\tabb]` — and in EVERY ONE the tab is
# the thing under test (a tab inside a brace quantifier makes it a literal
# brace run; a tab inside a class under `(?xx)` is stripped). They are the
# hardest three rows in the corpus to notice going wrong and the three most
# load-bearing, which is the combination a check has to be built for
# deliberately.
#
# THE DETECTOR IS THE FIELD MANIFEST'S PER-ROW FIELD COUNT — the table
# contract's HEADER TRUTHFULNESS rule — and not the diff, because a diff
# reports three changed lines out of 3,265 and a reader skims it. The
# check's failure message names the three blocks by file.
SAB_ID="S200-rxt-pattern-unescaped"
SAB_FILE="src/parse/rxt_source.c"
SAB_SUITES="rxtsource"
SAB_DESC="--list-source emits a raw tab in the pattern column, so the three corpus blocks whose pattern contains a literal tab produce rows with 16 fields where the header declares 15, and every column after the pattern column shifts on exactly those rows"
SAB_REACH='grep -cP "^pattern .*\\t" "$TREE/tests/base/bounded_repeats.rxt"' 
SAB_REACH_EXPECT="2"
SAB_REACH_POP="tests/modifiers/xxmode.rxt|^pattern .*	|1"
SAB_COUNT=1
SAB_BEFORE="        case '\\t': sb_puts(sb, \"\\\\t\");  break;"
SAB_AFTER="        case '\\t': sb_putc(sb, '\\t');  break;   /* SABOTAGE S200 */"
