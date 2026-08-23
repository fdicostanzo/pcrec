#!/usr/bin/env python3
"""[M6.6.1] §5/§6 -- THE DFA-ELIGIBLE SUBSET and the D66 HAND-OFF.

Three questions, all answered against the SHIPPED compiler and libpcre2
rather than against a design document:

  S1  THE POSITIVE CONTROL for the identity gate. No lookaround exists today,
      so "this module changes nothing for the existing population" is
      TRIVIALLY true and therefore worth nothing. The gate needs a control
      that can FAIL. The one this design proposes: a ONE-CHARACTER lookaround
      whose body is a single class IS an assertions-module context assertion,
      and where the assertions module already ships an equivalent spelling
      the two artifacts must be BYTE-IDENTICAL past their embedded pattern
      text. `\\b` decomposes as `(?<!\\w)(?=\\w)|(?<=\\w)(?!\\w)` -- measured
      here for EQUIVALENCE against libpcre2 first, because a control built on
      a false equivalence proves the wrong thing.

  S2  THE (?m)^ SELF-ORACLE the D66 hand-off needs: is today's folded (?m)^
      equivalent to the expansion `\\A|(?<=\\n)(?!\\z)`? Measured cell by cell
      on libpcre2, including the cells where the two could differ (a trailing
      newline, an empty subject, consecutive newlines, \\r\\n) -- and against
      the SHIPPED pcrec's own (?m)^ on the same subjects, which is what makes
      it a differential rather than a claim.

  S3  CAN THE H3 HAZARD COEXIST WITH A LIVE PRUNE CEILING? probe_prefilter_
      hazard.py found H3-sharp violated only inside an alternation whose
      erased branch 1 succeeds to the end of the pattern -- which needs an
      all-optional tail -- while `RX_VM_PRUNE_CEILING` reads
      "prefilter-window" only when the emitter has a CLAMP site. Those two
      requirements may be incompatible, in which case the H3 fix costs
      nothing and the design should say so. SWEPT rather than argued.
"""
import importlib.util
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", "..", ".."))
_spec = importlib.util.spec_from_file_location(
    "la_oracle", os.path.join(_HERE, "la_oracle.py"))
la = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(la)

PCREC = os.path.join(_ROOT, "build", "pcrec")


def show(v):
    if v == "ERR":
        return "ERR"
    if v is None:
        return "nomatch"
    return "(%d,%d)" % (v[0][0], v[0][1])


def pcrec_stamps(pat, names):
    """The named #define stamps of pcrec's artifact for `pat`, or None if it
    refuses (with the diagnostic)."""
    r = subprocess.run(["/usr/bin/gnutimeout", "20", PCREC, "-p", "rx",
                        "--features", "all", "-o", "-", pat],
                       capture_output=True, text=True, cwd=_ROOT)
    if r.returncode != 0:
        return None, r.stderr.strip()
    out = {}
    for line in r.stdout.splitlines():
        for nm in names:
            if line.startswith("#define " + nm + " "):
                out[nm] = line.split(nm, 1)[1].strip()
    return out, r.stdout


def hdr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


print("libpcre2:", la.version())
print("python3  :", sys.version.split()[0])
print("la_oracle SELFCHECK:", la.SELFCHECK or "none")
print("pcrec    :", "present" if os.path.exists(PCREC) else "ABSENT -- pcrec arms SKIP")

# --------------------------------------------------------------------------
hdr("S1 -- IS A ONE-CHARACTER LOOKAROUND REALLY THE ASSERTION IT CLAIMS TO BE?")
print("The identity gate's POSITIVE CONTROL rests on these equivalences. If any")
print("row disagrees, the control is testing the wrong thing.")
print()
SUBJECTS = ["", "a", " a ", "ab cd", "a-b", "\n", "a\n", "\na", "a\nb",
            "  ", "_x_", "1a", "a1", "\r\n", "a\r\nb", "aa\n\nbb"]
EQUIV = [
    (r"\b",   r"(?:(?<!\w)(?=\w)|(?<=\w)(?!\w))", "word boundary, decomposed"),
    (r"\B",   r"(?:(?<!\w)(?!\w)|(?<=\w)(?=\w))", "non-boundary, decomposed"),
    (r"\A",   r"(?<!\C)",                          "start-of-subject (\\C control)"),
    (r"\z",   r"(?!\C)",                           "end-of-subject"),
    (r"(?m)^", r"(?:\A|(?<=\n)(?!\z))",            "D66's own expansion"),
    (r"(?m)$", r"(?:(?=\n)|\z)",                   "multiline $"),
]
print("%-10s %-36s | cells | disagreements" % ("construct", "expansion"))
for a, b, note in EQUIV:
    dis = []
    n = 0
    for s in SUBJECTS:
        # THE TAIL SET IS `(?m)`-SCOPED. An earlier version used ("", "x",
        # "\\w") and reported ZERO disagreements for the (?m)^ row while S2
        # below -- whose tail set includes `$` -- found three. The tails are
        # not neutral: `$` MEANS something different under `(?m)`, so an
        # expansion arm without the option compares two different `$`s. Every
        # arm below is wrapped so both sides carry the same option state.
        for tail in ("", "x", "\\w", "$", "\\b"):
            pa, pb = "(?m:" + a + tail + ")", "(?m:" + b + tail + ")"
            ra, rb = la.search(pa, s), la.search(pb, s)
            n += 1
            if show(ra) != show(rb):
                dis.append((pa, pb, s, show(ra), show(rb)))
    print("%-10s %-36s | %5d | %d" % (a, b, n, len(dis)))
    for pa, pb, s, ra, rb in dis[:6]:
        print("        DISAGREE  %-14s %-30s subj=%-10s %s vs %s"
              % (pa, pb, repr(s), ra, rb))
    if len(dis) > 6:
        print("        ... and %d more" % (len(dis) - 6))
print()
print("# NOTE the \\A/\\z rows use \\C (any code unit), which is NOT the pcrec")
print("# spelling of anything -- they are here only to show the shape, and a")
print("# disagreement there is about \\C, not about the anchor.")

# --------------------------------------------------------------------------
hdr("S1b -- THE ARTIFACT-LEVEL POSITIVE CONTROL, on the SHIPPED compiler")
print("What the identity gate's positive control would compare, TODAY, with")
print("the lookaround half refused. This measures what the control can and")
print("cannot see before [M6.6.2] lands.")
if os.path.exists(PCREC):
    NAMES = ["RX_ENGINE", "RX_ENGINE_WHY", "RX_VM_PREFILTER", "RX_NCAPS",
             "RX_NSLOTS", "RX_VM_PRUNE_CEILING"]
    print("  (every pcrec call below passes `--features all`; the DEFAULT is")
    print("   `std1`, which does NOT enable module `assertions` -- measured:")
    print("   `\\bfoo` under the default refuses with \"requires module")
    print("   'assertions'\". That gating is a fact §10 and §9 both consume.)")
    for pat in [r"\bfoo", r"(?<!\w)(?=\w)foo", r"(?m)^foo",
                r"(?:\A|(?<=\n)(?!\z))foo", r"\Bfoo", r"foo"]:
        st, extra = pcrec_stamps(pat, NAMES)
        if st is None:
            print("  %-28s REFUSED: %s" % (pat, extra))
        else:
            print("  %-28s %s" % (pat, " ".join("%s=%s" % (k, v)
                                                for k, v in st.items())))
    print()
    print("  # and the artifact SIZE + a content digest past the embedded")
    print("  # pattern text, which is what a byte-identity gate compares:")
    for pat in [r"\bfoo", r"foo"]:
        r = subprocess.run(["/usr/bin/gnutimeout", "20", PCREC, "-p", "rx",
                            "--features", "all", "-o", "-", pat],
                           capture_output=True, text=True, cwd=_ROOT)
        import hashlib
        print("    %-12s bytes=%-6d sha1(full)=%s"
              % (pat, len(r.stdout), hashlib.sha1(
                  r.stdout.encode()).hexdigest()[:16]))
else:
    print("  SKIPPED -- no build/pcrec")

# --------------------------------------------------------------------------
hdr("S2 -- (?m)^ AS A SELF-ORACLE: folded implementation vs the expansion")
print("D66 needs the core lookbehind-anchor form. The check that would catch a")
print("wrong lowering is a differential between today's FOLDED (?m)^ and the")
print("expansion `\\A|(?<=\\n)(?!\\z)`. Both arms measured: libpcre2 against")
print("itself (is the expansion even correct?) and pcrec's shipped (?m)^")
print("against libpcre2's (does pcrec already agree?).")
print()
MSUBJ = ["", "a", "\n", "a\n", "\na", "a\nb", "a\n\nb", "\n\n",
         "abc\ndef\n", "\r\n", "a\r\nb\r\n", "x\ny\nz"]
print("%-10s | %-26s | %-14s | %-14s | %s" %
      ("subject", "(?m)^X vs expansion", "pcre2 folded", "pcre2 expanded", "same?"))
bad_expansion = 0
bad_nooption = [0]
for s in MSUBJ:
    for tail in (r"\w", r"a", r"$"):
        # BOTH ARMS CARRY `(?m)`. The first version put `(?m)` only on the
        # folded arm and reported THREE disagreements -- every one of them on
        # a `$` tail, i.e. a `(?m)$` compared against a plain `$`. That is a
        # defect in the probe, not a property of the expansion, and it is
        # exactly the shape backrefs_measurements catalogues: a filter or a
        # population that does not hold the thing being measured constant.
        # The uncorrected arm is kept below as `folded_bad` so the number is
        # reproducible rather than merely described.
        folded = r"(?m)^" + tail
        expanded = r"(?m)(?:\A|(?<=\n)(?!\z))" + tail
        expanded_nom = r"(?:\A|(?<=\n)(?!\z))" + tail
        ra, rb = la.search(folded, s), la.search(expanded, s)
        rc_ = la.search(expanded_nom, s)
        same = show(ra) == show(rb)
        if not same:
            bad_expansion += 1
        if show(ra) != show(rc_):
            bad_nooption[0] += 1
        if not same or tail == r"\w":
            print("%-10s | %-26s | %-14s | %-14s | %s" %
                  (repr(s), folded + " / expansion", show(ra), show(rb),
                   "yes" if same else "NO"))
print()
print("EXPANSION DISAGREEMENTS with the folded form (libpcre2 vs itself): %d"
      % bad_expansion)
print("  ... and with the OPTION-LESS expansion arm (the probe defect): %d"
      % bad_nooption[0])
print("  Both numbers are reported because the second one is what an")
print("  uncorrected probe would have published as a finding about (?m)^.")
print()
print("# the (?!\\z) conjunct is load-bearing. Same sweep WITHOUT it:")
bad_nozed = 0
for s in MSUBJ:
    for tail in (r"\w", r"a", r"$"):
        ra = la.search(r"(?m)^" + tail, s)
        rb = la.search(r"(?m)(?:\A|(?<=\n))" + tail, s)
        if show(ra) != show(rb):
            bad_nozed += 1
print("  `\\A|(?<=\\n)` (no (?!\\z)) disagrees with (?m)^ on %d of %d cells"
      % (bad_nozed, len(MSUBJ) * 3))
if bad_nozed == 0:
    print("  !! ZERO -- then this population cannot tell the two apart and the")
    print("  !! (?!\\z) conjunct's necessity is NOT established by it")
print()
if os.path.exists(PCREC):
    print("# pcrec's own shipped (?m)^ against libpcre2, same subjects:")
    import tempfile
    tmp = os.path.join(_HERE, "..", "..", "..", "..", "worktrees")
    scratch = os.environ.get("LA_SCRATCH", "/tmp")
    ndis = 0
    ncell = 0
    for tail in (r"\w", r"a"):
        pat = r"(?m)^" + tail
        src = os.path.join(scratch, "la_m_%s.c" % ("w" if tail == r"\w" else "a"))
        exe = src[:-2]
        r = subprocess.run(["/usr/bin/gnutimeout", "20", PCREC, "-p", "rx",
                            "--features", "all", "--emit-main", "-o", src, pat],
                           capture_output=True, text=True, cwd=_ROOT)
        if r.returncode != 0:
            print("  pcrec refused %r: %s" % (pat, r.stderr.strip()))
            continue
        c = subprocess.run(["/usr/bin/gnutimeout", "120", "nice", "-n", "19",
                            "gcc", "-O1", "-o", exe, src],
                           capture_output=True, text=True)
        if c.returncode != 0:
            print("  gcc failed: %s" % c.stderr.strip()[:120])
            continue
        for s in MSUBJ:
            got = subprocess.run(["/usr/bin/gnutimeout", "10", exe, s],
                                 capture_output=True, text=True)
            mine = got.stdout.strip()
            want = la.search(pat, s)
            wants = ("nomatch" if want is None
                     else "match %d %d" % (want[0][0], want[0][1]))
            ncell += 1
            if mine != wants:
                ndis += 1
                print("  DISAGREE %-8s subj=%-12s pcrec=%-14s pcre2=%s"
                      % (pat, repr(s), mine, wants))
    print("  pcrec (?m)^ vs libpcre2: %d disagreements over %d cells"
          % (ndis, ncell))

# --------------------------------------------------------------------------
hdr("S3 -- CAN AN H3 VIOLATION COEXIST WITH A LIVE PREFILTER-WINDOW CEILING?")
print("Swept over a small shape space rather than argued. A shape QUALIFIES")
print("when BOTH hold: (a) pcrec's artifact for the ERASURE stamps")
print("RX_VM_PRUNE_CEILING = \"prefilter-window\", and (b) libpcre2 says the")
print("erasure anchored at the true match's start ends BEFORE the true end.")
print()
if not os.path.exists(PCREC):
    print("  SKIPPED -- no build/pcrec")
else:
    PCRE2_ANCHORED = 0x80000000
    # THE FIRST POPULATION HERE COULD NOT CONTAIN A QUALIFYING SHAPE, and the
    # guard below is what made that visible instead of publishable. Every tail
    # it used was NULLABLE, and the emitter raises no CLAMP site for a
    # nullable-follow bounded repeat -- so condition (a) read "none" on all 36
    # shapes and the sweep reported "0 qualifying" over a space in which 0 was
    # the only possible answer. That is the shape of unfalsifiable zero this
    # project keeps cataloguing (R32, against its own instruments). The tails
    # below end in a MANDATORY unit, and CEILING_CONTROL asserts that at least
    # one erasure really does stamp "prefilter-window".
    HEADS = [(r"(?:a(?!q)|aq)",   r"(?:a|aq)"),
             (r"(?:a(?=z)|aq)",   r"(?:a|aq)"),
             (r"(?:a(?<=xa)|aq)", r"(?:a|aq)"),
             (r"(?:a(?!q)|ab)",   r"(?:a|ab)"),
             (r"(?:ab(?!q)|abq)", r"(?:ab|abq)")]
    TAILS = [r"(?:xy){0,4}q", r"[xy]{0,4}q", r"(?:xy){0,3}q",
             r"(?:ab){0,4}q", r"q", r"(?:xy){0,4}"]
    SUBJ = ["aqq", "aq", "aqxyq", "aaqq", "xaqq", "abq", "abqq", "azq",
            "aqxyxyq", "xaq", "abxyq", "aqb"]
    qualifying = []
    tried = 0
    ceiling_live = 0
    for h, eh in HEADS:
        for tl in TAILS:
            pat = "(" + h + tl + ")"
            er = "(" + eh + tl + ")"
            tried += 1
            st, _ = pcrec_stamps(er, ["RX_VM_PRUNE_CEILING"])
            ceil = "-" if st is None else st.get("RX_VM_PRUNE_CEILING", "?")
            live = ceil == '"prefilter-window"'
            if live:
                ceiling_live += 1
            hits = []
            for s in SUBJ:
                tr = la.search(pat, s)
                if tr is None or tr == "ERR":
                    continue
                a = la.search(er, s, tr[0][0], PCRE2_ANCHORED)
                if a is None or a == "ERR":
                    hits.append((s, tr[0], None))
                elif a[0][1] < tr[0][1]:
                    hits.append((s, tr[0], a[0]))
            if live and hits:
                qualifying.append((pat, er, hits))
            print("  %-36s ceiling=%-20s H3-sharp hits=%-3d%s"
                  % (pat, ceil, len(hits),
                     "  <== QUALIFIES" if (live and hits) else ""))
    print()
    print("VACUITY GUARD (condition (a) must be REACHABLE in this population):")
    if ceiling_live == 0:
        print("  !! FAILED: no erasure in the population stamps")
        print("  !! \"prefilter-window\", so condition (a) is unsatisfiable here")
        print("  !! and a count of 0 qualifying shapes measures NOTHING.")
    else:
        print("  ok: %d of %d erasures carry a LIVE prefilter-window ceiling,"
              % (ceiling_live, tried))
        print("      so a zero below would have been a real result")
    print()
    print("SHAPES TRIED: %d.  QUALIFYING (both conditions): %d"
          % (tried, len(qualifying)))
    for pat, er, hits in qualifying[:6]:
        print("  %s   erasure %s" % (pat, er))
        for s, tr, a in hits[:3]:
            print("      subj=%-10s true=%s  erased-anchored-there=%s" %
                  (repr(s), tr, a))
    if len(qualifying) > 6:
        print("  ... and %d more qualifying shapes" % (len(qualifying) - 6))
    if not qualifying:
        print("  NONE FOUND on this space.")
