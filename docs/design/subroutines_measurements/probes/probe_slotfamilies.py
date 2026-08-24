"""[DD-14] §5.3 -- THE RESTORE SET W, and why CAPTURE-SLOTS-ONLY is a
MISCOMPILE CLASS rather than one bug.

R34's C2 panel refuted §5.3's first version. This probe is the lane's OWN
re-run of the refutation: it rebuilds both critic prototypes from source
(`../prototype/slotproto_pending.c`, `../prototype/slotproto_cutmark.c`,
adopted unchanged -- see their headers) and compares three columns against
libpcre2 10.46.

THE CLAIM UNDER TEST. §5.3's first version defined W over CAPTURE slots only,
on the reasoning inherited from `lookaround_design.md` §6.4(2) that every
other slot family is "re-initialised at its own entry label on every entry".
That is true of SEQUENTIAL re-entry -- the case that design had -- and FALSE
of RECURSIVE re-entry: an INNER activation's write to a LEXICALLY-OUTER
construct's slot is still live when the outer activation reads it, because
there is only one slot per lexical construct and the activations are nested
rather than sequential.

pcrec has SEVEN slot families (`vm_slot_name`, emit_vm.c:645-697) and only
ONE of them is captures:

    SLOT_GROUP<n>_START/END    captures            <- the only family §5.3 had
    SLOT_GROUP<n>_PENDING      publish-at-close, [M6.5.2]
    SLOT_EMPTY_GUARD<n>        the empty-iteration guard
    SLOT_SPAN_LOW<n>           the cursor low-water mark
    SLOT_CUT_MARK<n>           the atomic/possessive cut mark
    SLOT_REVDET<n>_{ENTRY,LOW,HI}  the revdet rung
    SLOT_COUNTER<n>            the counter-K rung

TWO of them are MEASURED here. The others are the same shape and the design
says so rather than claiming a measurement it does not have.

  AXIS P -- SLOT_GROUP<n>_PENDING.  `^(a(?1)?b)\\1$`.  A group a backreference
     names is MARKED, and a marked group lowers publish-at-close: the opening
     position goes to a non-capture PENDING slot and the pair is published at
     the close. The inner activation overwrites the outer's pending value, so
     the outer publishes the WRONG START.  Failure direction: LOST MATCH.

  AXIS C -- SLOT_CUT_MARK<n>.  `^((?>a(?1)?))a$`.  A mark slot per atomic
     group PER EMITTED COPY (R34 V-2 corrected the design's "per lexical
     group"; here the group is unquantified, so it is one instance), written
     at entry and read by `RX_CUT`. The inner activation's
     mark overwrites the outer's, so the outer's cut becomes a NO-OP and the
     atomic group stops being atomic.  Failure direction: FALSE MATCH -- and
     the false-match set is EXACTLY the non-atomic control's language, which
     is what makes the diagnosis precise rather than merely "it differs".

REACHABILITY GUARDS, and this probe needs three:
  (a) the two builds must DISAGREE on at least one cell per axis, or the
      capture-only rule was never exercised;
  (b) the FIXED build must agree with libpcre2 on EVERY cell, or the fix is
      not the fix;
  (c) axis C additionally prints the NON-ATOMIC control language, so a reader
      can see that the broken build does not merely differ -- it computes a
      different, nameable language.
"""
import importlib.util
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "sr_oracle", os.path.join(_HERE, "sr_oracle.py"))
sr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sr)

PROTO = os.path.normpath(os.path.join(_HERE, "..", "prototype"))
TMP = os.environ.get("TMPDIR", "/tmp")

AXES = [
    dict(name="P", slot="SLOT_GROUP<n>_PENDING", src="slotproto_pending.c",
         define="W_INCLUDES_PENDING", pat=r"^(a(?1)?b)\1$", ctrl=None,
         subj=["abab", "aabbaabb", "aaabbbaaabbb", "ab", "aabb", "abba",
               "aabbab", "abaabb", "", "a", "b", "aabbaabbaabb", "ababab"],
         direction="LOST MATCH"),
    dict(name="C", slot="SLOT_CUT_MARK<n>", src="slotproto_cutmark.c",
         define="W_INCLUDES_MARK", pat=r"^((?>a(?1)?))a$",
         ctrl=r"^((?:a(?1)?))a$",
         subj=["a", "aa", "aaa", "aaaa", "aaaaa", "b", "ab", "",
               "aaaaaaaa", "aaaaaa"],
         direction="FALSE MATCH"),
]


def build(src, define, out):
    cmd = ["gcc", "-O2", "-std=gnu11", "-Wall", "-Wextra"]
    if define:
        cmd.append("-D" + define)
    cmd += ["-o", out, os.path.join(PROTO, src)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("BUILD FAILED:", " ".join(cmd)); print(r.stderr); sys.exit(3)
    if r.stderr.strip():
        print("  build warnings:", r.stderr.strip()[:400])


def pcre(pat, subj):
    r = sr.match_limits(pat, subj)
    if r is None:
        return "nomatch"
    if isinstance(r, tuple) and r and r[0] == "rc":
        return "giveup(rc=%d)" % r[1]
    if isinstance(r, tuple) and r and r[0] == "ERR":
        return "COMPILE-ERR %d" % r[1][0]
    span, g = r
    g1 = g[0] if g and g[0] else (-1, -1)
    return "match %d %d %d %d" % (span[0], span[1], g1[0], g1[1])


def run(binary, subj):
    return subprocess.run([binary, subj], capture_output=True, text=True,
                          timeout=60).stdout.strip()


print("libpcre2:", sr.version())
print("python3 :", sys.version.split()[0])
print("sr_oracle.SELFCHECK:", sr.SELFCHECK or "none")
print("prototypes:", PROTO, "(adopted from the R34 C2 panel unchanged)")
print()

ok = True
for ax in AXES:
    d = os.path.join(TMP, "dd14_slot_%s_designed" % ax["name"])
    f = os.path.join(TMP, "dd14_slot_%s_fixed" % ax["name"])
    build(ax["src"], None, d)
    build(ax["src"], ax["define"], f)
    print("=== AXIS %s -- %s ===================================="
          % (ax["name"], ax["slot"]))
    print("  pattern: %s      failure direction: %s"
          % (ax["pat"], ax["direction"]))
    if ax["ctrl"]:
        print("  non-atomic control: %s" % ax["ctrl"])
    print()
    da = db = fa = fb = 0
    equals_ctrl = 0
    for subj in ax["subj"]:
        vd, vf, vp = run(d, subj), run(f, subj), pcre(ax["pat"], subj)
        vc = pcre(ax["ctrl"], subj) if ax["ctrl"] else None
        da += (vd == vp); db += (vd != vp)
        fa += (vf == vp); fb += (vf != vp)
        note = ""
        if vd != vp:
            note = "   <-- CAPTURES-ONLY W DISAGREES"
            if vc is not None and vd == vc:
                note += " (and EQUALS the non-atomic language)"
                equals_ctrl += 1
        if vf != vp:
            note += "   <-- THE FIX ALSO DISAGREES"
        print("  %-16s capturesW=%-22s +%s=%-22s pcre2=%-22s%s"
              % (repr(subj), vd, ax["define"].split("_")[-1].lower(), vf,
                 vp, note))
    print()
    print("  W as §5.3 FIRST WROTE it : %d agree, %d DISAGREE" % (da, db))
    print("  W + the %s slot : %d agree, %d DISAGREE" % (ax["slot"], fa, fb))
    if db == 0:
        print("  !! VACUOUS: the captures-only build agrees on every cell -- "
              "this axis never exercised the rule it is about")
        ok = False
    if fb != 0:
        print("  !! THE FIX IS NOT THE FIX: it still disagrees on %d cell(s)"
              % fb)
        ok = False
    if ax["ctrl"] and equals_ctrl == 0:
        print("  (note: no broken cell equalled the control's language, so "
              "the diagnosis is 'differs' rather than 'computes THIS other "
              "language')")
    print()

print("=== REACHABILITY GUARDS =============================================")
print("  (a) each axis's two builds disagree somewhere:", "OK" if ok else "SEE ABOVE")
print("  (b) each fixed build agrees with libpcre2 everywhere:",
      "OK" if ok else "SEE ABOVE")
print()
print("WHY THE LANE'S OWN CORPUS COULD NOT SEE THIS. Both axes need a")
print("SECOND lexical construct whose slot is live across a call:")
print("  axis P needs a group that a BACKREFERENCE names (otherwise the")
print("     group is not marked and publish-at-close never fires);")
print("  axis C needs an ATOMIC GROUP live at two recursion depths.")
print("`probe_callproto.py`'s four patterns have neither -- P1..P4 are plain")
print("capturing groups and alternations -- so every cell agreed and the")
print("rule went unexercised. The lesson is the project's own: a control")
print("that shares its alphabet with the thing it controls does not control")
print("it, and this corpus shared the DESIGN's alphabet.")
