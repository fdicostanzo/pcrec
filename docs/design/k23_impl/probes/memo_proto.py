#!/usr/bin/env python3
"""K23 prototype: LOOP-ENTRY FAILURE MEMOIZATION, as a patch on emitted C.

The competitor to MRL pruning (k23_design.md section 5). Throwaway, same
status as prune_proto.py: it exists to price the mechanism against the real
emitted code, not to be the implementation.

WHAT IT DOES
------------
At each span-loop scan site -- the entry to outer replica k, at subject
position `pos` -- it inserts

    if (rx_memo[k][pos]) goto rx_fail;
    rx_memo[k][pos] = 1;

Soundness, STRUCTURAL, and it is worth stating because it is the whole
mechanism: the VM is a pure depth-first backtracker, so a SECOND arrival at
the same (program point, position) can only happen after the first arrival's
entire subtree was explored and failed -- had it succeeded, the matcher
would have returned. "Visited" therefore implies "failed", and no separate
success/failure bookkeeping is needed.

Two conditions on that, both real and both named rather than smoothed over:
  * the future must be a function of (program point, position) ALONE. It is
    here because captures are write-only with respect to control flow. A
    BACKREFERENCE would break it (the future then depends on a captured
    substring), and so would anything else that reads mutable state.
  * the memo must survive across the search's start-position attempts, and
    it soundly does, for the same reason: failure from (k, pos) does not
    depend on where the match was started.

THE COST, which is the point of the measurement: the table is
(replica count) x (subject length + 1) BYTES here, and even packed to bits
it is Theta(program points x subject length). That is a per-match allocation
whose size is not known at compile time -- the constraint this prototype is
built to price, not to satisfy. `--bits` packs it, `--cap N` caps the
subject length the table covers (positions past the cap are simply not
memoized, which stays sound -- it loses pruning, never adds any).

Usage:
  memo_proto.py IN.c OUT.c [--slot-base B] [--bits] [--cap N]
"""
import argparse
import re
import sys

SCAN = re.compile(
    r'''    RX_SET\((?P<slot>\d+),\ \(ptrdiff_t\)pos\);\n
        \ {4}\{\n
        \ {8}unsigned\ long\ it_\ =\ 0;\n
        \ {8}rx_cur\ =\ pos;\n
        (?P<loop>\ {8}while\ \(.*?\)\ \{\ rx_cur\ \+=\ \d+;\ it_\+\+;\ \}\n)
        \ {4}\}\n''',
    re.VERBOSE)

# Inserted just before the impl function, so the table is visible to it.
# A file-scope array is NOT what a shipped design could do (TS-1 forbids
# mutable globals in generated code); it is the cheapest way to measure the
# mechanism's search-space effect without also building an allocator.
TABLE_BITS = '''
/* K23 memo prototype -- file-scope on purpose, see memo_proto.py's header:
 * a shipped version could not be a global (TS-1), and that is the finding,
 * not an oversight. */
#define RX_MEMO_K %d
#define RX_MEMO_N %d
static unsigned char rx_memo[RX_MEMO_K][(RX_MEMO_N + 8) / 8];
static unsigned long rx_memo_bytes = sizeof rx_memo;
#define RX_MEMO_TEST(k_, p_) ((p_) < RX_MEMO_N && (rx_memo[k_][(p_) >> 3] & (1u << ((p_) & 7))))
#define RX_MEMO_SET(k_, p_)  do { if ((p_) < RX_MEMO_N) rx_memo[k_][(p_) >> 3] |= (unsigned char)(1u << ((p_) & 7)); } while (0)
'''

TABLE_BYTES = '''
#define RX_MEMO_K %d
#define RX_MEMO_N %d
static unsigned char rx_memo[RX_MEMO_K][RX_MEMO_N];
static unsigned long rx_memo_bytes = sizeof rx_memo;
#define RX_MEMO_TEST(k_, p_) ((p_) < RX_MEMO_N && rx_memo[k_][p_])
#define RX_MEMO_SET(k_, p_)  do { if ((p_) < RX_MEMO_N) rx_memo[k_][p_] = 1; } while (0)
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--slot-base', type=int, default=None)
    ap.add_argument('--bits', action='store_true')
    ap.add_argument('--cap', type=int, default=4096)
    a = ap.parse_args()

    text = open(a.src).read()
    hits = list(SCAN.finditer(text))
    if not hits:
        print('memo_proto: no span-loop scan sites found', file=sys.stderr)
        sys.exit(1)
    base = a.slot_base if a.slot_base is not None else min(
        int(h.group('slot')) for h in hits)
    nk = max(int(h.group('slot')) for h in hits) - base + 1

    out, last, n_patched = [], 0, 0
    for h in hits:
        k = int(h.group('slot')) - base
        if k < 0:
            continue
        out.append(text[last:h.start()])
        last = h.start()
        out.append(
            '    /* K23 memo prototype: replica %d */\n'
            '    if (RX_MEMO_TEST(%d, pos)) goto rx_fail;\n'
            '    RX_MEMO_SET(%d, pos);\n' % (k, k, k))
        n_patched += 1
    out.append(text[last:])
    text = ''.join(out)

    table = (TABLE_BITS if a.bits else TABLE_BYTES) % (nk, a.cap)
    anchor = 'static ptrdiff_t rx_match_impl'
    if anchor not in text:
        print('memo_proto: impl anchor not found', file=sys.stderr)
        sys.exit(1)
    text = text.replace(anchor, table + '\n' + anchor, 1)
    # make the table size observable from the run
    text = text.replace(
        '    atexit(rx_probe_report);',
        '    atexit(rx_probe_report);\n'
        '    fprintf(stderr, "MEMOBYTES %lu\\n", rx_memo_bytes);', 1)
    open(a.dst, 'w').write(text)
    print('memo_proto: %d scan sites, %d memo points, table %s %dx%d'
          % (len(hits), n_patched, 'bits' if a.bits else 'bytes', nk, a.cap),
          file=sys.stderr)
    if n_patched == 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
