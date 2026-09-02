#!/usr/bin/env python3
"""TWIN C -- SINGLE-INDUCTION-VARIABLE SCAN EDGE.

[OPT-5]'s scan edge is emitted as a two-induction-variable loop: it advances
the cursor AND a separate `scan_run_length` counter, and tests three things
per byte (cursor < end, counter < bound, class).  Clang defeats this by fully
unrolling when the bound is small; gcc does not, and pays the counter.

The general spelling folds the count bound into a CURSOR LIMIT computed once
before the loop, leaving one induction variable and two tests per byte.  It
needs no unroll threshold and is correct for any bound, so it is the same
code for `{0,4}` and `{0,65535}`.  The run length after the loop is recovered
by subtraction, exactly as before.
"""
import re, sys
src = open(sys.argv[1]).read()
n = 0

# ---- forward / anchored: cursor moves UP, bounded above by subject_length
fwd = re.compile(
    r'( *)unsigned long scan_run_length = 1;\n'
    r'( *)(\w+)\+\+;\n'
    r'( *)while \((\w+) < (\w+) && scan_run_length < (\d+)UL\n'
    r' *&& (.*?)\) \{ \5\+\+; scan_run_length\+\+; \}')
def fsub(m):
    global n; n += 1
    i, cur, end, bound, test = m.group(1), m.group(5), m.group(6), m.group(7), m.group(8)
    return (f'{i}const size_t rx_edge_start = {cur};   /* [twinC] single-IV edge */\n'
            f'{i}const size_t rx_edge_limit = ({end} - rx_edge_start > {bound}UL)\n'
            f'{i}                             ? rx_edge_start + {bound}UL : {end};\n'
            f'{i}{cur}++;\n'
            f'{i}while ({cur} < rx_edge_limit && {test}) {{ {cur}++; }}\n'
            f'{i}unsigned long scan_run_length = (unsigned long)({cur} - rx_edge_start);')
src, k = fwd.subn(fsub, src)

# ---- reverse: cursor moves DOWN, bounded below by search_from
rev = re.compile(
    r'( *)unsigned long scan_run_length = 1;\n'
    r'( *)(\w+)--;\n'
    r'( *)while \((\w+) > (\w+) && scan_run_length < (\d+)UL\n'
    r' *&& (.*?)\) \{ \5--; scan_run_length\+\+; \}')
def rsub(m):
    global n; n += 1
    i, cur, floor, bound, test = m.group(1), m.group(5), m.group(6), m.group(7), m.group(8)
    return (f'{i}const size_t rx_edge_start = {cur};   /* [twinC] single-IV edge */\n'
            f'{i}const size_t rx_edge_limit = (rx_edge_start - {floor} > {bound}UL)\n'
            f'{i}                             ? rx_edge_start - {bound}UL : {floor};\n'
            f'{i}{cur}--;\n'
            f'{i}while ({cur} > rx_edge_limit && {test}) {{ {cur}--; }}\n'
            f'{i}unsigned long scan_run_length = (unsigned long)(rx_edge_start - {cur});')
src, j = rev.subn(rsub, src)
open(sys.argv[2], 'w').write(src)
print('edges rewritten: forward/anchored %d, reverse %d' % (k, j))
