"""[DD-14] §3.5 / §2.4 / §4.4b -- THE R34 C1 FINDINGS, re-run by this lane.

Four axes, all raised by R34's C1 panel and all re-measured here from scratch
rather than transcribed:

  W  THE MISSING CONSTRUCT FAMILY -- a call whose TARGET GROUP is lexically
     inside a LOOKAROUND or an ATOMIC GROUP. The design had calls INSIDE a
     lookaround (§3.4(e)) and never had calls TO a group inside one. The
     callee runs as its OWN region: forward, consuming, cut-free,
     back-step-free, whatever its lexical home does. An emitter that reached
     the callee by jumping INTO its lexical position would inherit the
     wrapper -- the lookbehind's back-step, the negative lookahead's cut, the
     atomic group's cut -- and miscompile all three.

  M  §4.4b's FIXPOINT, with the witness C1 built: an indirect recursion in
     which the called group has NO non-recursive branch, yet the pattern
     MATCHES. The first version's gloss ("minimum over the non-recursive
     branches") gives infinity, the MRL prune reads that as "no position can
     match", and the answer is a LOST MATCH.

  Z  A FOURTH MISSING SPELLING FAMILY -- LEADING-ZERO absolute calls. The
     rule is "parse the whole digit run as DECIMAL; the value 0 is the ROOT",
     and it is uniform across the `(?` and `\\g` doorways. pcrec's registry
     has a `(?0)` row described as a `(?R)` synonym, so wiring the doorway on
     the CHARACTER `0` makes `(?01)` compile as the root -- a MISCOMPILE.

  G  `\\G`, a non-zero startpos, and `\\A`/`\\z` inside a callee.

REACHABILITY. Axis W's rows are worthless without CONTROLS that isolate the
wrapper: for each wrapped-target cell there is a cell where the callee's FIRST
alternative already suffices (so the retry is not being exercised) and a cell
with the same language written INLINE. Axis Z's rows are worthless unless the
subject can tell "group 1" from "the root", which needs the ANCHORED form --
this probe's first draft used the unanchored `(a\\g<00>?b)`, where both answers
are (0,4), and it would have reported that `\\g<00>` is group 1.
"""
import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "sr_oracle", os.path.join(_HERE, "sr_oracle.py"))
sr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sr)

print("libpcre2:", sr.version())
print("python3 :", sys.version.split()[0])
print("sr_oracle.SELFCHECK:", sr.SELFCHECK or "none")
print()

_out = set()


def cell(pat, subj, note="", opts=0, start=0):
    r = sr.match_limits(pat, subj, start=start, options=opts)
    if isinstance(r, tuple) and r and r[0] == "ERR":
        _out.add("refuse")
        txt = "ERR %d %s" % (r[1][0], r[1][2])
    elif isinstance(r, tuple) and r and r[0] == "rc":
        _out.add("giveup")
        txt = "rc=%d %s" % (r[1], sr.pcre2._errmsg(r[1]))
    else:
        _out.add("nomatch" if r is None else "match")
        txt = repr(r)
    print("  %-38s %-10r %-30s%s"
          % (pat, subj, txt, ("  # " + note) if note else ""))
    return txt


print("=== AXIS W: the call's TARGET is inside a LOOKAROUND / ATOMIC group ===")
print("# Each group of rows is: the WRAPPED-TARGET cell, a control where the")
print("# callee's FIRST alternative suffices, and where possible the same")
print("# language written INLINE.")
print()
print("# W1 -- target inside a LOOKBEHIND. The callee runs FORWARD and")
print("#       CONSUMES, though its lexical home steps BACKWARD first.")
cell(r"^ab(?<=(ab))(?1)$", "abab", "the call consumes 'ab' at offset 2")
cell(r"^ab(?<=(ab))(?1)$", "ab", "control: the call must consume something")
cell(r"^ab(?<=(ab))ab$", "abab", "control: the same language, inline")
print()
print("# W2 -- target inside a NEGATIVE LOOKAHEAD. The callee must RETRY into")
print("#       its second alternative, inside a region whose lexical home is")
print("#       cut on the assertion's own success.")
cell(r"^(?!(z|zy))x(?1)c$", "xzyc", "the callee retried into 'zy'")
cell(r"^(?!(z|zy))x(?1)c$", "xzc", "control: the first alternative suffices")
cell(r"^(?!(z|zy))x(?:z|zy)c$", "xzyc", "control: inline")
print()
print("# W3 -- target inside an ATOMIC group. The callee must GIVE BACK.")
cell(r"^(?>(a|ab))z(?1)c$", "azabc", "the callee gave back 'a' and took 'ab'")
cell(r"^(?>(a|ab))z(?1)c$", "azac", "control: the first alternative suffices")
cell(r"^(?>(a|ab))z(?:a|ab)c$", "azabc", "control: inline, atomic kept")
cell(r"^(?:a|ab)z(?:a|ab)c$", "azabc", "control: no wrapper at all")
print()
print("# W4 -- the atomic target is never RUN lexically (an optional group")
print("#       the subject skips), so the only execution is the call's.")
cell(r"^q(?>(a|ab))?z(?1)c$", "qzabc", "the wrapper never ran")
print()
print("# W5 -- target inside a POSITIVE LOOKAHEAD, and inside a lookahead")
print("#       nested in a quantified group.")
cell(r"^(?=(a|ab))..(?1)$", "abab")
cell(r"^((?=(b))|a)+(?2)$", "ab")
print()
print("# THE READING. Every W row matches. A callee reached by JUMPING INTO")
print("# its lexical position would inherit the wrapper's machinery -- the")
print("# back-step in W1, the assertion's cut in W2, the atomic cut in W3 --")
print("# and answer nomatch on each. The design's §5.4 must therefore say")
print("# that a callee body is emitted as its OWN region.")
print()

print("=== AXIS M: §4.4b's fixpoint, and the gloss that loses a match ======")
print("# g's ONLY branch is `(?&h)b`; h's branches are `x` and `(?&g)`.")
print("# So g has NO non-recursive branch -- and the pattern matches.")
_m = r"^(?(DEFINE)(?<g>(?&h)b)(?<h>x|(?&g)))(?&g)$"
for subj in ["xb", "xbb", "xbbb", "xbbbb", "b", "x", "", "yb"]:
    cell(_m, subj)
print("# the least fixpoint: minw(h) = 1 (the `x` branch), minw(g) = 2.")
print("# the WITHDRAWN gloss 'minimum over the non-recursive branches' has")
print("# no branch to minimise over in g, gives INFINITY, and the MRL prune")
print("# turns every row above into nomatch.")
print()
print("# CONTROL -- a recursion that genuinely IS the empty language, where")
print("# infinity is the RIGHT answer (§12 P-12):")
for subj in ["ab", "aabb", "", "aaabbb"]:
    cell(r"^(?(DEFINE)(?<g>a(?&g)b))(?&g)$", subj)
print()

print("=== AXIS Z: LEADING-ZERO absolute calls, both doorways =============")
print("# The discriminator is the ANCHORED form: `(?R)` re-runs the anchors")
print("# (§2.4) so it answers nomatch on 'aabb', while a call to GROUP 1")
print("# answers (0,4). The UNANCHORED form cannot tell them apart and this")
print("# probe's first draft used it.")
for pat in [r"^(a(?1)?b)$", r"^(a(?01)?b)$", r"^(a(?001)?b)$",
            r"^(a(?0001)?b)$", r"^(a(?R)?b)$", r"^(a(?0)?b)$",
            r"^(a(?00)?b)$", r"^(a\g<1>?b)$", r"^(a\g<01>?b)$",
            r"^(a\g<0>?b)$", r"^(a\g<00>?b)$", r"^(a\g'01'?b)$",
            r"^(a\g'00'?b)$"]:
    cell(pat, "aabb", "GROUP 1 if (0,4); the ROOT if nomatch")
print()
print("# and the RELATIVE forms take a leading zero too, while a relative")
print("# value of ZERO stays error 126 in every spelling:")
cell(r"^(a)(b)\g<-01>$", "abb")
cell(r"^(a)(b)(?-01)$", "abb")
cell(r"^(a)(b)\g<-02>$", "aba")
for pat in [r"(a)(?-00)", r"(a)(?+00)", r"(a)(?-0)", r"(a)\g<-0>"]:
    cell(pat, "aa", "relative zero")
print()
print("# THE RULE: parse the whole digit run as DECIMAL; the value 0 is the")
print("# ROOT; a RELATIVE value of 0 is error 126. Uniform across (? and \\g.")
print()

print("=== AXIS G: \\G, a non-zero startpos, and \\A / \\z inside a callee ===")
_g = r"(?(DEFINE)(?<g>\Ga))(?&g)"
for st in (0, 1):
    cell(_g, "xa", "\\G is an absolute test against startpos", start=st)
cell(r"(?(DEFINE)(?<g>\Aa))x?(?&g)", "xa", "\\A means the SUBJECT's start")
cell(r"(?(DEFINE)(?<g>\Aa))(?&g)", "a", "control")
cell(r"(?(DEFINE)(?<g>a\z))x(?&g)", "xa", "\\z means the SUBJECT's end")
cell(r"(?(DEFINE)(?<g>a\z))x(?&g)b", "xab", "control")
print("# All four compose with no rule of this module's own: a call changes")
print("# neither the subject nor startpos, so the absolute assertions mean")
print("# inside a callee exactly what they mean outside one.")
print()

print("=== AXIS J: is the (?J) call rule uniform across ALL FOUR spellings? =")
print("# §3.4(c) measured it for (?&name) only. The other three:")
for pat in [r"^(?:(?<a>x)|q)(?<a>y)(?&a)$", r"^(?:(?<a>x)|q)(?<a>y)(?P>a)$",
            r"^(?:(?<a>x)|q)(?<a>y)\g<a>$", r"^(?:(?<a>x)|q)(?<a>y)\g'a'$"]:
    cell(pat, "qyx", "FIRST DECLARATION if it matches", sr.PCRE2_DUPNAMES)
    cell(pat, "qyy", "first SET member if it matches", sr.PCRE2_DUPNAMES)
print()

print("=== REACHABILITY GUARDS =============================================")
print("outcomes populated:", sorted(_out))
need = {"match", "nomatch", "refuse", "giveup"}
missing = need - _out
if missing:
    print("!! VACUOUS: %s never occurred" % sorted(missing))
else:
    print("matches, no-matches, compile refusals and match-time give-ups all "
          "occur: these axes separate four answers, not one")
