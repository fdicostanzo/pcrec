"""[DD-14.K34] PCRE2 10.46's RECURSION-LOOP RULE, measured from ITS OWN
SOURCE rather than inferred by black-box sweep alone.

`../subroutines_design.md` §3.3 (`out/leftrec.txt` L5b) already found the
OBVIOUS reading of rc -52's message ("refuse a recursion re-entered at a
position an ancestor already occupies") FALSE -- 199 same-position nested
recursions can MATCH -- and said explicitly: "THIS LANE DID NOT PIN 10.46's
EXACT PREDICATE BY BLACK-BOX PROBING". K34 is that open predicate. This probe
closes it by READING `pcre2_match.c` (10.46, fetched from
https://github.com/PCRE2Project/pcre2/releases/download/pcre2-10.46/pcre2-10.46.tar.gz
into the scratch dir per the scope mandate -- never into this tree) and then
testing the read rule to falsification, rather than re-running the earlier
black-box sweep with more cells.

THE RULE (cited: pcre2-10.46/src/pcre2_match.c, `case OP_RECURSE`, the block
immediately after the case label -- line numbers as shipped in the 10.46
release tarball):

  Every heapframe F carries three fields the check reads:
    F->current_recurse    -- the group NUMBER of the nearest enclosing
                              RECURSE frame among F's ancestors, or the
                              sentinel RECURSE_UNSET (0xffffffff) if F is not
                              executing inside ANY recursion at all. Set once,
                              at NEW_FRAME time, only when the new frame's own
                              group_frame_type IDs it as GF_RECURSE (line
                              ~792: `Fcurrent_recurse =
                              GF_DATAMASK(group_frame_type)`); inherited
                              unchanged by every other frame kind via the
                              plain field copy at MATCH_RECURSE.
    F->last_group_offset  -- chains to the NEAREST ENCLOSING "special group"
                              frame (capture, non-capture, cond-assert OR
                              recurse) -- a linked list through every group
                              boundary on the call stack, not just recursions.
    F->recurse_last_used  -- set (line ~5602, `F->recurse_last_used =
                              mb->last_used_ptr`) at the INSTANT a frame is
                              about to issue ITS OWN first branch attempt into
                              a recursion target, i.e. the match-so-far
                              high-water mark AT THE MOMENT this frame made
                              its call.
  `mb->last_used_ptr` is PCRE2's OWN running high-water mark of the furthest
  subject byte any opcode has examined so far in the WHOLE match attempt --
  not the cursor, not "matched", "looked at" (a failed literal compare against
  a byte still advances it to that byte).

  At `case OP_RECURSE`, target group `number` resolved (0 for whole-pattern
  recursion via `(?R)`/`(?0)`):

    if (Fcurrent_recurse != RECURSE_UNSET)        // (G) only check while
                                                    //     ALREADY inside SOME
                                                    //     active recursion
      walk F->last_group_offset outward, frame by frame, until either the
      chain ends or a frame N is found with N->group_frame_type ==
      (GF_RECURSE | number)                        // (A) NEAREST ancestor
                                                    //     recursion of the
                                                    //     SAME group -- not
                                                    //     every ancestor,
                                                    //     the first one found
      if found:
        let P = the frame that issued N's own recursive call (N's immediate
                caller, i.e. (heapframe*)((char*)N - frame_size))
        if Feptr == P->eptr                         // (P) zero forward
                                                      //     progress in the
                                                      //     MATCH CURSOR
                                                      //     since P's call
           && mb->last_used_ptr == P->recurse_last_used   // (U) zero growth
                                                      //     in the "how far
                                                      //     right has
                                                      //     anything looked"
                                                      //     mark either
           && (mb->moptions & PCRE2_DISABLE_RECURSELOOP_CHECK) == 0   // (D)
          return PCRE2_ERROR_RECURSELOOP;      // -52, a bare `return`, NOT
                                                 // `RRETURN` -- see R4: this
                                                 // aborts the ENTIRE match,
                                                 // not just the current
                                                 // branch, so a sibling
                                                 // top-level alternative that
                                                 // does not touch the
                                                 // recursion at all is never
                                                 // reached either.
        // else: fall through, recurse normally (no error)
      // if no such N in the chain: fall through, recurse normally

  So the plain-English rule a corpus author can apply: **a recursive call is
  flagged as a loop only on the SECOND-OR-LATER time the SAME group is
  re-entered while already inside recursion, and only if, between the
  previous entry and this one, NEITHER the match cursor NOR PCRE2's own
  "furthest byte examined" mark has moved at all.** Any construct that forces
  at least one of the two to advance between successive entries -- a
  mandatory literal before the call, or (more subtly) a base-case alternative
  whose FAILED attempt peeks even one byte further right than the ancestor's
  own attempt did -- defers or defeats the guard, however deep the recursion
  goes; PCRE2's own resource limits (match/depth/heap) are the only backstop
  left once that happens, exactly what (D) exposes as a match-time knob
  (`PCRE2_DISABLE_RECURSELOOP_CHECK`, 0x00040000, `pcre2.h.in:200`) and R5
  exploits directly to confirm the code path rather than just its effects.

CELLS discriminate each of (G)/(A)/(P)/(U)/(D) and the whole-match-abort
consequence separately, then the K34 case-study patterns are re-measured and
EXPLAINED by the rule rather than re-discovered by more sweeping. Every claim
is MEASURED against libpcre2 10.46 here; nothing is read from documentation.
REACHABILITY: every family that claims "always/never -52" is checked for a
population of at least 3 subjects per shape, and the footer refuses to
conclude if any outcome class the design needs never appeared.
"""
import ctypes
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

PCRE2_DISABLE_RECURSELOOP_CHECK = 0x00040000

_seen_classes = set()
_agree, _disagree = 0, 0


def classify(r):
    if r is None:
        return "NOMATCH"
    if isinstance(r, tuple) and r and r[0] == "ERR":
        return "ERR:%d" % r[1][0]
    if isinstance(r, tuple) and r and r[0] == "rc":
        return "RC:%d" % r[1]
    return "MATCH:%r" % (r,)


def cell(pat, subj, predict, note=""):
    """`predict` is either an exact classify() string, or a callable
    got -> bool. Records agreement and prints one row."""
    global _agree, _disagree
    r = sr.match_limits(pat, subj)
    got = classify(r)
    _seen_classes.add(got.split(":")[0])
    ok = predict(got) if callable(predict) else (got == predict)
    if ok:
        _agree += 1
    else:
        _disagree += 1
    plabel = predict.__doc__ if callable(predict) else predict
    print("  %-42s %-14r predict=%-22s got=%-18s %s%s"
          % (pat, subj, plabel, got, "OK" if ok else "**MISMATCH**",
             ("  # " + note) if note else ""))
    return r


def is52(got):
    """RC:-52"""
    return got == "RC:-52"


def not52(got):
    """not RC:-52"""
    return got != "RC:-52"


# ==========================================================================
print("=== R1: FIRST-ITEM recursion -- (G)+(A)+(P)+(U) on the simplest =====")
print("# no consumption and no peek precede the call: predicate (P) and (U)")
print("# are BOTH trivially satisfied the instant recursion re-enters, so")
print("# the rule predicts -52 fires at the SECOND same-group entry -- i.e.")
print("# immediately -- for EVERY subject, whether or not a base case exists")
print("# to consume characters, because the base case is never even reached")
print("# before the guard trips on the SECOND recursive attempt.")
print()

print("-- 1a: no base case at all (cannot match anything, ever) --")
for subj in ("a", "aaaaa", "b"):
    cell(r'^((?1)a)$', subj, is52, "no base case: recursion is unconditional")
cell(r'^((?1)a)$', "", "NOMATCH",
     "EMPTY subject: NOT -52 -- see R1.5 below. PCRE2's START-OPTIMIZE "
     "pass (a compile-time minlength/required-byte prescreen) rejects "
     "before the recursive matcher -- confirmed by "
     "sr._lib.pcre2_match_8 depth=1 already returning NOMATCH here, and "
     "by PCRE2_NO_START_OPTIMIZE flipping it to RC:-52 (R1.5) -- so this "
     "is a DIFFERENT PCRE2 mechanism intercepting the cell, not evidence "
     "against the loop rule")

print("-- 1b: base case present, subject has NO trailing junk (matching) --")
for n in (1, 5, 50, 199):
    cell(r'^(a|(?1)a)$', "a" * n, "MATCH:((0, %d), [(0, %d)])" % (n, n),
         "base case defers the guard indefinitely -- reproduces design "
         "§3.3's 199-deep cell as a PREDICTION, not a re-discovery")

print("-- 1b: base case present, subject is a's then one non-'a' byte "
      "(non-matching; the descent runs out of ways to advance) --")
for n in (1, 3, 10, 40):
    cell(r'^(a|(?1)a)$', "a" * n + "b", is52,
         "once no 'a' remains to try, the failed base-case attempt no "
         "longer peeks past where the ancestor's did -- guard fires")

print("-- 1b on EMPTY subject --")
cell(r'^(a|(?1)a)$', "", "NOMATCH",
     "EMPTY subject: also START-OPTIMIZE (minlen 1, 'a' required), not "
     "the loop rule -- same mechanism as 1a's empty cell, see R1.5")

print("-- 1a/1b UNANCHORED: does the guard's whole-match abort even reach "
      "past start position 0? --")
cell(r'(a|(?1)a)', "b" * 5, "NOMATCH",
     "'bbbbb' contains NO 'a' anywhere -- START-OPTIMIZE's required-byte "
     "prescreen rejects the whole subject before pcre2_match ever runs, "
     "same confound as above, not a start-position question at all; R4 "
     "below is the real test of the whole-match-abort claim")


# ==========================================================================
print()
print("=== R1.5: THE CONFOUND -- START-OPTIMIZE can turn a would-be -52 ====")
print("=== into an early NOMATCH, for a reason that has NOTHING to do ======")
print("=== with the recursion-loop rule ======================================")
print("# Found DURING this probe's own first run: five R1/R3 cells the rule")
print("# predicted RC:-52 for instead measured NOMATCH, all and only the")
print("# ones whose subject is EMPTY or is missing a byte the pattern")
print("# structurally requires SOMEWHERE ('a' for the 1a/1b families, 'b'")
print("# for the x* family). `sr.match_limits(..., depth=1)` already shows")
print("# NOMATCH for these -- the recursive matcher never ran even ONE")
print("# level -- which is the signature of PCRE2's COMPILE-TIME")
print("# start-optimize pass (minlength / required-byte prescan), not the")
print("# match-time loop guard. `PCRE2_NO_START_OPTIMIZE` (0x00010000,")
print("# compile-time) is the falsification: if these cells are really the")
print("# prescreen and not some corner of the loop rule, forcing it off")
print("# must flip every one of them to RC:-52. A CORPUS AUTHOR CONSEQUENCE:")
print("# testing a runaway-recursion cell on a subject that happens to be")
print("# too short, or missing a required literal, measures the WRONG")
print("# mechanism and will read as 'sometimes NOMATCH, sometimes -52' with")
print("# no visible pattern unless this confound is known.")
print()


def nsocell(pat, subj, predict, note=""):
    global _agree, _disagree
    got = classify(_ns_search(pat, subj))
    _seen_classes.add(got.split(":")[0])
    ok = predict(got) if callable(predict) else (got == predict)
    if ok:
        _agree += 1
    else:
        _disagree += 1
    plabel = predict.__doc__ if callable(predict) else predict
    print("  %-42s %-14r NO_START_OPTIMIZE predict=%-10s got=%-18s %s%s"
          % (pat, subj, plabel, got, "OK" if ok else "**MISMATCH**",
             ("  # " + note) if note else ""))


PCRE2_NO_START_OPTIMIZE = 0x00010000


def _ns_search(pat, subj):
    patb = pat.encode("latin-1")
    subjb = subj.encode("latin-1")
    errcode = ctypes.c_int(0)
    erroff = ctypes.c_size_t(0)
    code = sr._lib.pcre2_compile_8(patb, len(patb),
                                   PCRE2_NO_START_OPTIMIZE,
                                   ctypes.byref(errcode), ctypes.byref(erroff),
                                   None)
    if not code:
        return ("ERR", (errcode.value, erroff.value,
                        sr.pcre2._errmsg(errcode.value)))
    md = sr._lib.pcre2_match_data_create_from_pattern_8(code, None)
    try:
        rc = sr._lib.pcre2_match_8(code, subjb, len(subjb), 0, 0, md, None)
        if rc == sr.PCRE2_ERROR_NOMATCH:
            return None
        if rc < 0:
            return ("rc", rc)
        ov = sr._lib.pcre2_get_ovector_pointer_8(md)
        npairs = rc if rc > 0 else 1
        pairs = [(ov[2 * i], ov[2 * i + 1]) for i in range(npairs)]
        groups = [None if s == sr.PCRE2_UNSET else (s, e)
                  for s, e in pairs[1:]]
        return (pairs[0][0], pairs[0][1]), groups
    finally:
        sr._lib.pcre2_match_data_free_8(md)
        sr._lib.pcre2_code_free_8(code)


for pat, subj in ((r'^((?1)a)$', ""), (r'^(a|(?1)a)$', ""),
                  (r'(a|(?1)a)', "b" * 5), (r'^(x*(?1)b)$', ""),
                  (r'^(x*(?1)b)$', "xx")):
    nsocell(pat, subj, is52,
            "same pattern+subject as the NOMATCH cell above, compiled "
            "with PCRE2_NO_START_OPTIMIZE: the prescreen is off, so the "
            "recursive matcher actually runs and the loop rule's own "
            "prediction (RC:-52) holds")


# ==========================================================================
print()
print("=== R2: CONSUMING PREFIX -- predicate (P) can NEVER be satisfied =====")
print("# a MANDATORY >=1-byte literal before the call means Feptr strictly")
print("# advances at every successive same-group entry, so P->eptr < Feptr")
print("# always -- the rule predicts -52 NEVER fires, for ANY subject,")
print("# matching or not, with or without a base case. This is a clean")
print("# universally-quantified prediction: 0 of N cells is RC:-52.")
print()

print("-- 2a: no base case (genuinely CANNOT match: no floor to the "
      "descent, but the failure must be a clean NOMATCH, never -52) --")
for subj in ("", "x", "xxxxx", "xxxaaa", "a" * 5):
    cell(r'^(x(?1)a)$', subj, not52,
         "consuming prefix -- position always advances between calls")

print("-- 2b: base case present, balanced (matching) subjects --")
for n in (1, 3, 8, 30):
    subj = "x" * n + "a" * (n + 1)
    cell(r'^(a|x(?1)a)$', subj, not52,
         "matching balanced x^n a^(n+1) -- never -52 regardless of depth")

print("-- 2b: non-matching (x's run out before a floor, or wrong tail) --")
for subj in ("xxxbbb", "xxx", "xxxaa", ""):
    cell(r'^(a|x(?1)a)$', subj, not52,
         "consuming prefix still forces P even on a losing subject")

print("-- 2 UNANCHORED --")
cell(r'(a|x(?1)a)', "xxxbbb", not52, "unanchored consuming-prefix control")


# ==========================================================================
print()
print("=== R3: NULLABLE PREFIX -- (P) depends on whether the prefix has ====")
print("=== anything LEFT to eat, not on whether it ever ate anything ========")
print("# x* is greedy: at the FIRST call it eats every available x in one")
print("# bite, landing the recursion at a position beyond where any second")
print("# same-group entry can ever reach (nothing left for x* to eat at the")
print("# next level down) -- so predicate (P) is satisfied from the SECOND")
print("# within-recursion attempt onward exactly as in R1, REGARDLESS of how")
print("# many x's were actually present. This refines design §3.3's L3/L5")
print("# findings (all measured -52) by explaining WHY: it is never about")
print("# 'did the prefix advance the position at all', only about 'is there")
print("# anything left for it to eat on the NEXT attempt'.")
print()

print("-- 3a: no base case, no x's available --")
cell(r'^(x*(?1)b)$', "", "NOMATCH",
     "EMPTY subject: START-OPTIMIZE prescreen again (no 'b' at all), "
     "not the loop rule -- see R1.5")
for subj in ("b", "bb"):
    cell(r'^(x*(?1)b)$', subj, is52, "x* eats 0, nothing to differ next time")

print("-- 3a: no base case, x's present (greedy x* eats them all up front) --")
cell(r'^(x*(?1)b)$', "xx", "NOMATCH",
     "'xx' contains NO 'b' anywhere -- SAME required-byte prescreen as "
     "the empty-subject cell above intercepts it before the recursive "
     "matcher runs at all (confirmed: depth=1 already gives NOMATCH here, "
     "and PCRE2_NO_START_OPTIMIZE flips it to RC:-52, R1.5) -- the "
     "'greedy x* exhausts its supply' mechanism this family is meant to "
     "demonstrate is real (see 'xxb'/'xxxxxb' below) but this particular "
     "cell never reaches it")
for subj in ("xxb", "xxxxxb"):
    cell(r'^(x*(?1)b)$', subj, is52,
         "x* eats every x on the FIRST attempt; the SECOND attempt (one "
         "level down) has none left, so (P) still trips one level in")

print("-- 3b: WITH a base case (?1)? made optional -- does a real base case "
      "change anything once x* has already exhausted its supply? --")
cell(r'^(?(DEFINE)(?<g>x*(?&g)?b))(?&g)$', "xxb", is52,
     "reproduces design out/leftrec.txt L5's own cell -- greedy x* still "
     "exhausts on the first bite, guard trips one level in regardless of "
     "the optional-call base case")


# ==========================================================================
print()
print("=== R4: THE WHOLE-MATCH ABORT -- `return`, not `RRETURN` ============")
print("# -52 is returned directly from match(), not routed through the")
print("# ordinary backtrack-and-try-the-next-alternative machinery. So a")
print("# TOP-LEVEL sibling alternative that never goes near the recursion at")
print("# all should be UNREACHABLE once -52 fires on an earlier alternative")
print("# -- decisive because a naive reader would expect PCRE2 to fall")
print("# through to '|^Y$' the way an ordinary failed branch would.")
print()

cell(r'^Y$', "Y", "MATCH:((0, 1), [])", "control: bare alternative target "
     "matches on its own (sanity baseline, no recursion involved)")
cell(r'^Z$|^Y$', "Y", "MATCH:((0, 1), [])",
     "control: an ORDINARY failed first alternative DOES fall through")
cell(r'^(a|(?1)a)$|^Y$', "Y", is52,
     "the runaway first alternative's -52 ABORTS the whole match before "
     "the second top-level alternative is ever tried -- 'Y' matches "
     "'^Y$' on its own (previous cell) but the compound pattern still -52s")
cell(r'^Y$|^(a|(?1)a)$', "Y", "MATCH:((0, 1), [None])",
     "order matters: recursion as the SECOND alternative is never reached "
     "at all when the first already matches -- confirms this is really "
     "about the FIRST alternative's own abort, not some pattern-wide veto")


# ==========================================================================
print()
print("=== R5: PCRE2_DISABLE_RECURSELOOP_CHECK -- confirms the CODE PATH, ===")
print("=== not just its effects ==============================================")
print("# (D) is a single `&&` term gating the `return -52` in the source.")
print("# Setting the match-time option bit should make an otherwise-52 cell")
print("# fall through to ordinary (bounded) resource exhaustion instead --")
print("# under an explicit small depth_limit, that means RC:-53")
print("# (PCRE2_ERROR_DEPTHLIMIT), a DIFFERENT negative code, not a match")
print("# and not silence. This is the most direct falsification available:")
print("# if the option bit does nothing, the read of (D) is wrong.")
print()


def search_mo(pat, subj, start=0, moptions=0, depth=None, heap=None,
              match=None):
    patb = pat.encode("latin-1") if isinstance(pat, str) else pat
    subjb = subj.encode("latin-1") if isinstance(subj, str) else subj
    errcode = ctypes.c_int(0)
    erroff = ctypes.c_size_t(0)
    code = sr._lib.pcre2_compile_8(patb, len(patb), 0, ctypes.byref(errcode),
                                    ctypes.byref(erroff), None)
    if not code:
        return ("ERR", (errcode.value, erroff.value,
                        sr.pcre2._errmsg(errcode.value)))
    mc = sr._mk_context(depth, match, heap)
    md = sr._lib.pcre2_match_data_create_from_pattern_8(code, None)
    try:
        rc = sr._lib.pcre2_match_8(code, subjb, len(subjb), start, moptions,
                                   md, mc)
        if rc == sr.PCRE2_ERROR_NOMATCH:
            return None
        if rc < 0:
            return ("rc", rc)
        ov = sr._lib.pcre2_get_ovector_pointer_8(md)
        npairs = rc if rc > 0 else 1
        pairs = [(ov[2 * i], ov[2 * i + 1]) for i in range(npairs)]
        groups = [None if s == sr.PCRE2_UNSET else (s, e)
                  for s, e in pairs[1:]]
        return (pairs[0][0], pairs[0][1]), groups
    finally:
        sr._lib.pcre2_match_data_free_8(md)
        sr._lib.pcre2_match_context_free_8(mc)
        sr._lib.pcre2_code_free_8(code)


def mocell(pat, subj, moptions, predict, depth=None, note=""):
    global _agree, _disagree
    r = search_mo(pat, subj, moptions=moptions, depth=depth)
    got = classify(r)
    _seen_classes.add(got.split(":")[0])
    ok = predict(got) if callable(predict) else (got == predict)
    if ok:
        _agree += 1
    else:
        _disagree += 1
    plabel = predict.__doc__ if callable(predict) else predict
    print("  %-42s %-14r mo=0x%-8x predict=%-14s got=%-18s %s%s"
          % (pat, subj, moptions, plabel, got, "OK" if ok else "**MISMATCH**",
             ("  # " + note) if note else ""))


mocell(r'^(a|(?1)a)$', "a" * 10 + "b", 0, is52,
       note="baseline: default options, this cell is -52 (R1 above)")
mocell(r'^(a|(?1)a)$', "a" * 10 + "b", PCRE2_DISABLE_RECURSELOOP_CHECK,
       "RC:-53", depth=500,
       note="SAME pattern+subject, check disabled + a small explicit depth "
       "limit: predicts it now runs past where -52 used to fire and hits "
       "DEPTHLIMIT instead -- a DIFFERENT code, not a match, not silence")
mocell(r'^((?1)a)$', "a", 0, is52,
       note="baseline: the R1 1a family, no base case, default options")
mocell(r'^((?1)a)$', "a", PCRE2_DISABLE_RECURSELOOP_CHECK, "RC:-53",
       depth=200,
       note="same construct with the guard off: the underlying descent is "
       "genuinely unconditional (no base case at all), so this should hit "
       "the depth limit almost immediately once the guard is not there to "
       "catch it first")


# ==========================================================================
print()
print("=== R6: (A) NEAREST-ANCESTOR-OF-THE-SAME-GROUP, not 'any ancestor' ===")
print("# a chain that cycles through THREE distinct groups (p->q->r->p) only")
print("# re-enters group p every THIRD hop; the search walks the WHOLE")
print("# last_group_offset chain (not just the immediate parent) to find it")
print("# there, so the rule predicts the guard still fires -- but only once")
print("# the SAME group truly recurs, never on a hop to a DIFFERENT group.")
print()

cell(r'^(?(DEFINE)(?<p>(?&q)a)(?<q>(?&r)a)(?<r>(?&p)a))(?&p)$', "a",
     is52, "3-node same-position cycle p->q->r->p: (A) must walk 3 frames "
     "up the chain (past q and r) to find the nearest 'p' ancestor")
cell(r'^(?(DEFINE)(?<p>x(?&q)a)(?<q>x(?&r)a)(?<r>x(?&p)a))(?&p)$',
     "xxxxxxaaaaaa", not52,
     "same 3-node cycle, each edge now consumes: predicate (P) can never "
     "hold between two 'p' entries either, exactly like R2's 2-node case")


# ==========================================================================
print()
print("=== R7: SPELLING INVARIANCE -- (?1) / (?R) / (?&name) / \\g<1> / ====")
print("=== \\g'name' all read the SAME group_frame_type, so the SAME rule ===")
print()

cell(r'^((?1)a)$', "a", is52, "(?1), numeric relative-to-1")
cell(r'^((?R)a)$', "a", is52, "(?R), whole-pattern spelling of the same "
     "group-1-wraps-everything shape")
cell(r'^(?(DEFINE)(?<g>(?&g)a))(?&g)$', "a", is52, "(?&name)")
cell(r'^(?(DEFINE)(?<g>\g<g>a))\g<g>$', "a", is52, "\\g<name>")
cell(r"^(?(DEFINE)(?<g>\g'g'a))\g'g'$", "a", is52, "\\g'name'")
cell(r'^(?(DEFINE)(?<g>(?P>g)a))(?P>g)$', "a", is52, "(?P>name)")
cell(r'^(a|(?1)a)$', "a" * 30, "MATCH:((0, 30), [(0, 30)])",
     "(?1) numeric base-case family for contrast")


# ==========================================================================
print()
print("=== R8: THE K34 CASE-STUDY PATTERNS THEMSELVES, EXPLAINED ===========")
print("# K34's own cells, unanchored, re-measured here and walked through")
print("# the rule rather than re-discovered: `known_issues.md` K34 reports")
print("# these RESULTS already; this section is the EXPLANATION.")
print()

cell(r'(a|(?1)a)b', "a", "NOMATCH",
     "K34's headline cell. Unanchored start=0: branch1 'a' matches "
     "position 0->1, then needs 'b' but subject is exhausted -> backtrack; "
     "branch2 '(?1)a' recurses (FIRST recursion, (G) not yet armed, no "
     "check) at position 0 again; that level's OWN branch1 'a' matches "
     "0->1 and needs a trailing 'a' (from branch2's own text) which is "
     "ALSO exhausted -> backtrack to branch2 AGAIN: THIS is the second "
     "same-group entry, (G) is now armed -- but Feptr is back at 0 for "
     "the recursive attempt while last_used_ptr has already been pushed "
     "to 1 (both failed trailing-character checks looked at position 1, "
     "past the ancestor's own baseline of 0) -- so (U) is FALSE and the "
     "guard does not fire; the whole tree exhausts through ordinary "
     "backtracking instead, and start=1 is then tried and also fails -- "
     "a clean NOMATCH, no -52 anywhere in the search")
cell(r'(a|(?1)a)b', "aaa", "NOMATCH",
     "same mechanism, more 'a's to exhaust before the clean NOMATCH")
cell(r'(a|(?1)a)b', "", "NOMATCH",
     "same family, empty subject: branch1 fails immediately with nothing "
     "to peek past, branch2 recurses once (unchecked), inner branch1 also "
     "fails immediately -- ordinary NOMATCH, again no -52")
cell(r'(a|(?1)a)b', "ab", "MATCH:((0, 2), [(0, 1)])",
     "K34's matching cell: branch2 recurses, inner branch1 matches 'a', "
     "outer 'b' then matches -- ordinary success, no recursion depth "
     "beyond 1 is ever needed")
cell(r'^((?1)a)$', "a", is52,
     "K34's `((?1)a)` cell: this IS the R1 1a family (no base case, no "
     "consuming prefix) -- guard fires at the second entry unconditionally")
cell(r'^(a?(?1)b)$', "ab", is52,
     "K34's `(a?(?1)b)` cell: a? is a NULLABLE prefix exactly like R3 -- "
     "greedy a? eats the one available 'a' on the FIRST attempt, leaving "
     "nothing for the second within-recursion attempt to differ on")
cell(r'((?1)?a)', "a", is52,
     "K34's inverse-direction cell (pcrec matches, PCRE2 -52): (?1)? is "
     "the FIRST-ITEM-no-consuming-prefix shape (R1's 1a family) with an "
     "optional wrapper that changes nothing about (P)/(U) -- guard fires "
     "at the second entry exactly as 1a predicts, REGARDLESS of the "
     "optionality, because the guard trips before the '?' ever gets a "
     "chance to try the WITHOUT branch")
cell(r'((?1)*a)', "a", is52,
     "K34's other inverse cell, same reasoning as (?1)? above, quantifier "
     "kind (* vs ?) does not matter -- greedy always tries WITH first")


# ==========================================================================
print()
print("=== R9: pcrec's ACTUAL answer today, vs the §3.3-RULED DESIGN's ======")
print("=== PROJECTED answer -- two different things, kept separate ==========")
print("# Module `recursion` is ROADMAP_PLANNED (src/parse/registry.c), not")
print("# built -- pcrec refuses every one of R1-R8's patterns at COMPILE")
print("# time today ('requires module recursion'), which this section")
print("# confirms on a representative subset rather than assuming it. That")
print("# refusal is D26-honest (OK-LIMITED, not a wrong answer) and is NOT")
print("# the 'PCREC_ERR_FRAMES' behaviour docs/dev/known_issues.md K34")
print("# describes -- K34's 'pcrec answers ... FRAMES' describes the RULED,")
print("# UNBUILT design (subroutines_design.md §3.3: 'pcrec builds NO")
print("# same-position guard ... the DEPTH CAPACITY is the only guard'),")
print("# not a measurement of running code. This probe does not build a new")
print("# prototype to turn that projection into a measurement (out of the")
print("# 'docs/probes only' scope this lane was given) -- it only keeps the")
print("# two honestly labelled and distinct, which K34's own wording blurs.")
print()

import subprocess  # noqa: E402

PCREC = os.path.normpath(os.path.join(_HERE, "..", "..", "..", "..",
                                       "build", "pcrec"))
_refusals = 0
for pat in (r'^((?1)a)$', r'^(a|(?1)a)$', r'^(x(?1)a)$', r'^(x*(?1)b)$',
            r'(a|(?1)a)b', r'^((?R)a)$'):
    try:
        p = subprocess.run([PCREC, "-p", "rx", "--emit-main", "-o",
                            "/dev/null", pat],
                           capture_output=True, text=True, timeout=10)
        refused = "requires module 'recursion'" in (p.stderr + p.stdout)
        if refused:
            _refusals += 1
        print("  pcrec %-24r -> %s" % (
            pat, "REFUSED (requires module 'recursion')" if refused
            else "rc=%d stdout=%r stderr=%r"
                 % (p.returncode, p.stdout[:80], p.stderr[:80])))
    except FileNotFoundError:
        print("  pcrec binary not found at", PCREC,
              "-- build it first (make, in this worktree)")
        break

print()
print("  DIVERGENCE CLASSES (§3.3's RULED design vs PCRE2, PROJECTED -- not")
print("  measured on running code, since module `recursion` has no build):")
print("  class 1, 'pcrec gives up where PCRE2 concludes cleanly': every R1")
print("    cell PCRE2 answers -52 on IMMEDIATELY (depth 2) is NOT this class")
print("    -- a depth-capped VM would also conclude at depth 2, i.e. give up")
print("    LESS eagerly than PCRE2's O(1) same-position check, not more.")
print("    The real members are the R1 1b MATCHING family at large n (199+)")
print("    and any R2/R3 shape whose true recursion depth sits ABOVE pcrec's")
print("    stamped cap but BELOW where PCRE2 needs real resources (§3.3's")
print("    own L9: 10.46 still answers at 800 KB / 400,000 deep) -- the band")
print("    §3.3 already names and sizes as the residual (its own §12 P-3).")
print("  class 2, 'pcrec matches where PCRE2 -52s' (the INVERSE, K34's other")
print("    reported gap): R7/R8's `((?1)?a)`/`((?1)*a)` cells -- PCRE2 -52s")
print("    at depth 2 unconditionally (R1 1a's shape) while a depth-capped,")
print("    no-same-position-guard VM just tries the recursion and, since it")
print("    has a base case reachable via the '?'/'*' WITHOUT arm, matches.")
print("    Per K34's own text this is 'pcrec arguably better; no expectation")
print("    writable' -- not a corpus-blocking divergence.")


# ==========================================================================
print()
print("=== REACHABILITY GUARD ===============================================")
needed = {"NOMATCH", "MATCH", "RC"}
missing = needed - _seen_classes
print("outcome classes seen:", sorted(_seen_classes))
if missing:
    print("VACUOUS: never observed", sorted(missing),
          "-- a conclusion drawn from this sweep about that class would be "
          "invented, not measured")
else:
    print("all three outcome classes occurred: refusal, match and give-up "
          "are separated by measurement, not assumed")
print("agreement with the source-derived rule: %d / %d cells"
      % (_agree, _agree + _disagree))
if _disagree:
    print("** %d CELL(S) DISAGREED WITH THE PREDICTED RULE -- see the "
          "MISMATCH rows above; the rule as stated needs correction before "
          "it is trusted **" % _disagree)
print("=== END ===")
