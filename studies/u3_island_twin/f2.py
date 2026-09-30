"""f2.py -- the HAND-DERIVED island machines for patterns whose context set
is NOT byte-expressible (ucp_design.md s2.3): no all-byte form exists, so
there is no artifact to compute the machine from.  Each machine below is
written out by hand from the pattern's semantics, in both directions, and
checked (check.py) against libpcre2 and against the VM pcrec emits today.

  x1  (?<=[\\x{100}-\\x{2000}])x       a lookbehind whose one-character
                                      context is a wide class -- forward
                                      seed from the char before `from`; the
                                      reverse pass tests the char before the
                                      match, past `from` if it must.
  x2  (?<!W)W+(?!W), W = \\w plus Latin/Greek/Cyrillic ranges
                                      a \\b-shaped pattern with a WIDE
                                      context set spelled as lookarounds, so a
                                      VM baseline exists.
  x3  \\b\\w+\\b under UCP              the real thing: W = \\p{Xwd}.  pcrec
                                      REFUSES it today (U1), so there is no
                                      baseline; libpcre2 is the only oracle.

Common shape of x2/x3 (H7, the accept column): a run state accepts only if
the NEXT character is not in W, so accept is answered per next character --
by the class-indexed accept table for ASCII and by acc_isl[q][v] inside the
island for non-ASCII.
"""
import os
import sys

from cm import CM

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cls_tree_study"))

W2_NONASCII = [(0xC0, 0x24F), (0x370, 0x52F)]
X1_W = [(0x100, 0x2000)]


def _cls256(is_first_class):
    return [0 if is_first_class(b) else 1 for b in range(128)] + [2] * 128


def x1():
    cls = _cls256(lambda b: b == ord("x"))          # 0 = 'x', 1 = other ASCII, 2 = NA
    # states: 0 = A (prev not in W), 1 = B (prev in W), 2 = ACC
    fwd = CM("fwd", 3, cls, 2,
             nxt=[[0, 0, 'I'], [2, 0, 'I'], [-1, -1, 'I']],
             tgt=[[0, 1, 0], [0, 1, 0], [-1, -1, -1]],
             acc=[0, 0, 1],
             seed=dict(abs=0, asc=[0, 0], isl=[0, 1, 0]), req_byte=ord("x"))
    # reverse: R0 (at match end) --x--> R1; R1 accepts iff the char BEFORE is in W
    rev = CM("rev", 2, cls, 2,
             nxt=[[1, -1, 'I'], [-1, -1, 'I']],
             tgt=[[-1, -1, -1], [-1, -1, -1]],
             accn=[[0, 0], [0, 0]], aend=[0, 0],
             acc_isl=[[0, 0, 0], [0, 1, 0]], byclass=True)
    return fwd, rev, X1_W


def runmachine(ascii_word):
    """x2/x3's machine: ASCII class 0 = word, 1 = non-word, 2 = NA."""
    cls = _cls256(ascii_word)
    N, WIN, WPRE = 0, 1, 2
    fwd = CM("fwd", 3, cls, 2,
             nxt=[[WIN, N, 'I'], [WIN, -1, 'I'], [WPRE, N, 'I']],
             tgt=[[N, WIN, N], [-1, WIN, -1], [N, WPRE, N]],
             accn=[[0, 0], [0, 1], [0, 0]], aend=[0, 1, 0],
             acc_isl=[[0, 0, 0], [1, 0, 1], [0, 0, 0]], byclass=True,
             seed=dict(abs=N, asc=[WPRE, N], isl=[N, WPRE, N]))
    rev = CM("rev", 2, cls, 2,
             nxt=[[1, -1, 'I'], [1, -1, 'I']],
             tgt=[[-1, 1, -1], [-1, 1, -1]],
             accn=[[0, 0], [0, 1]], aend=[0, 1],
             acc_isl=[[0, 0, 0], [1, 0, 1]], byclass=True)
    return fwd, rev


def _ascii_word(b):
    return chr(b).isalnum() or b == ord("_")


def x2():
    fwd, rev = runmachine(_ascii_word)
    return fwd, rev, W2_NONASCII


def x3():
    import clsets
    d = dict(clsets.uprops())
    iv = [(lo, hi) for (lo, hi) in d["XWD"] if hi >= 0x80]
    iv = [(max(lo, 0x80), hi) for (lo, hi) in iv]
    fwd, rev = runmachine(_ascii_word)
    return fwd, rev, iv


BUILD = {"x1": x1, "x2": x2, "x3": x3}


def build(case, write_case):
    fwd, rev, iv = BUILD[case]()
    write_case(case, fwd, rev, iv, dict(hand="f2", set_intervals=len(iv)))
    print(case, "hand-derived; non-ASCII set: %d intervals" % len(iv))
