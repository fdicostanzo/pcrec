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
#
# [REVW.1 wave 1, 2026-09-18] RE-AIMED, FILE ONLY. The escape itself moved
# from `rxt_source.c`'s `put_escaped` to `src/core/sb.c`'s `pcrec_sb_field`, so the
# `.rxt` subject vocabulary and `--explain`'s frame-only one share their
# `\xNN` tail rather than spelling it twice. The move is VERBATIM — same
# bytes, same column — so `SAB_BEFORE` is UNCHANGED and only `SAB_FILE`
# moves; `replace.py` matches whole-file and line-agnostic, so a relocation
# that keeps its column costs a re-aim of one field.
# INTENT RE-VERIFIED (the house rule for any re-anchor, and it needed asking
# because the function now has FOUR callers' worth of columns rather than
# rxt_source.c's three): `pcrec_sb_field` is called at exactly the 11 `--list-source`
# sites `put_escaped` was, and NOWHERE else in the tree — the registry dumps
# use `pcrec_sb_text`, the OTHER vocabulary, which does not carry this case at all.
# So the plant still un-escapes exactly the columns this row names and
# nothing more, and its detector (tests/rxtsource's field-count survey) is
# unmoved. Verified by grep at the re-aim and by the solo run below.
SAB_ID="S200-rxt-pattern-unescaped"
SAB_FILE="src/core/sb.c"
SAB_SUITES="rxtsource"
SAB_DESC="--list-source emits a raw tab in the pattern column, so the three corpus blocks whose pattern contains a literal tab produce rows with 20 fields where the header declares 19, and every column after the pattern column shifts on exactly those rows"
# [DD-13b.W23.4] STALE-COUNT RE-STATEMENT, w23_impl.md §6.4 item 6/r59-A-M2:
# this row's own detector (R5, tests/rxtsource/run_rxtsource_tests.sh) is
# now SECTION-AWARE and its plain-English failure message no longer quotes
# a field count at all, but SAB_DESC above is re-derived from a live count
# regardless — 19 main-table columns (`kind`..`esc`) is this pin's real
# number, not the "15"/"16" this row has carried at earlier pins.
# [mechreach fix, 2026-09-09] `grep -cP` needs libpcre-backed grep; the real
# `/usr/bin/grep` this driver actually runs under on this box is BSD grep
# 2.6.0-FreeBSD, which has no -P at all ("invalid option -- P", exit 2 --
# exactly the exit code the battery's mech.log recorded for this row). Note
# this is NOT the interactive shell's own `grep` (a Claude-Code function
# shimming ugrep) -- a plain `bash -c` child process never inherits that
# function, so it always sees the real binary. The driver's OWN internal
# row-filter grep hit this identical trap and was fixed the same way
# ([MACPORT], see this script's "was `grep -P` ... ERE + bash ANSI-C
# quoting" comment near its results-table extraction): ERE (-E) instead of
# PCRE (-P), and a portable way to get a literal tab into the pattern that
# does not require nesting a single quote inside this already-single-quoted
# field (this directory's own documented trap -- "Nested single quotes in
# SAB_REACH break the assignment quietly"). `$(printf "\t")` reaches the
# nested `bash -c "$SAB_REACH"` untouched and expands to a real tab there,
# using only double quotes throughout.
SAB_REACH='grep -cE "^pattern .*$(printf "\t")" "$TREE/tests/base/bounded_repeats.rxt"'
SAB_REACH_EXPECT="2"
SAB_REACH_POP="tests/modifiers/xxmode.rxt|^pattern .*	|1"
SAB_COUNT=1
SAB_BEFORE="        case '\\t': sb_puts(sb, \"\\\\t\");  break;"
SAB_AFTER="        case '\\t': sb_putc(sb, '\\t');  break;   /* SABOTAGE S200 */"
