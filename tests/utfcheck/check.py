#!/usr/bin/env python3
"""tests/utfcheck/check.py -- [UTF-VALID]'s differential and its guards
(docs/design/utf_valid_design.md §7; docs/spec/match_api.md §9.4 and §3.1.2).

Usage: check.py PCREC WORKDIR   (run_utfcheck.sh passes both; the C compiler
is $CC, resolved by tests/lib/cc_resolve.sh; every compile it runs is
bounded by a subprocess timeout)

THE ORACLE is cases_10.46.tsv: libpcre2 10.46 under PCRE2_UTF with checking
ON, the contract `-futf-check` reproduces, answering gen_cases.py's
questions (probe_pcre2.c; ubuntubudu, light). THE SECOND, INDEPENDENT
ORACLE is python's strict `bytes.decode('utf-8')` over the range the
design's §1.3 walk defines, transcribed here from the design's rule and
NOT from pcrec's C; it must agree with libpcre2 on every row before any
pcrec answer is scored, so a transcript error or a moved PCRE2 fails here
rather than becoming the expectation.

WHAT IS CHECKED, per pattern pcrec compiles (the population is counted and
floored, never assumed):

  LB      the artifact's `rx_VALID_LB` equals PCRE2_INFO_MAXLOOKBEHIND
  K       -e utf8 -futf-check (auto engine): every row's answer, the
          refusal (-9 vs PCRE2's UTF errors, -7 vs its BADUTFOFFSET, i.e.
          the K50 guard FIRST) and valid_upto's offset vs startchar
  KV      the same under --engine=vm (the VM without the prefilter)
  KW      the same on the capture-wrapped (P) (the VM hybrid)
  KA      -futf-check -fstartpos-guard=align, align rows: the answer is
          PCRE2's at the ALIGNED position, checked there with no carve-out
  A       -fstartpos-guard=align alone, well-formed align rows
  D       the DEFAULT -e utf8 artifact: never -9, valid_upto still exact,
          and on a well-formed checked range the same answer as K
  B       -e byte: -futf-check and -fstartpos-guard=align are INERT (the
          artifact is byte-identical to the default one)
"""
import os, subprocess, sys, collections

PCREC, WORK = sys.argv[1], sys.argv[2]
CC = os.environ.get("CC") or "cc"
HERE = os.path.dirname(os.path.abspath(__file__))
TIMEOUT = 120

fails = []
passes = 0
def bad(msg):
    fails.append(msg)
    if len(fails) <= 40:
        print("FAIL: " + msg)
def ok(msg):
    global passes
    passes += 1
    print("PASS: " + msg)

# ---- the oracle --------------------------------------------------------
Row = collections.namedtuple("Row", "set pat subj sp mode qp rc ov0 ov1 sc mlb")
rows = []
with open(os.path.join(HERE, "cases_10.46.tsv")) as f:
    head = f.readline()
    if "libpcre2 10.46" not in head:
        bad("cases_10.46.tsv's header does not name libpcre2 10.46: " + head.strip())
    for line in f:
        c = line.rstrip("\n").split("\t")
        subj = bytes.fromhex(c[2]) if c[2] != "-" else b""
        rows.append(Row(c[0], c[1], subj, int(c[3]), c[4], int(c[5]),
                        c[6], c[7], c[8], c[9], c[10]))
if len(rows) < 6000:
    bad(f"the oracle transcript holds {len(rows)} rows, floor 6000 -- it was truncated or regenerated smaller")

def utf_err(rc):
    return rc.lstrip("-").isdigit() and -23 <= int(rc) <= -3

# ---- the second oracle: python's strict decoder, the design's §1.3 walk --
def stepback(s, pos, lb):
    """Per character: one byte back, then back over EVERY continuation
    byte; clamped at 0; unvalidated (utf_valid_design.md §1.3)."""
    for _ in range(lb):
        if pos == 0: break
        pos -= 1
        while pos > 0 and (s[pos] & 0xC0) == 0x80:
            pos -= 1
    return pos

def py_offset(s, pos, lb):
    f = stepback(s, pos, lb)
    try:
        s[f:].decode("utf-8")
        return len(s)
    except UnicodeDecodeError as e:
        return f + e.start

nx = 0
for r in rows:
    if r.rc == "compile" or int(r.rc) in (-33, -36):
        continue
    want = int(r.sc) if utf_err(r.rc) else len(r.subj)
    got = py_offset(r.subj, r.qp, int(r.mlb))
    nx += 1
    if got != want:
        bad(f"ORACLES DISAGREE [{r.pat}] {r.subj!r}@{r.qp}: libpcre2 {r.rc} "
            f"startchar {r.sc}, python offset {got} (LB {r.mlb})")
if nx < 5000:
    bad(f"only {nx} rows were cross-checked between the two oracles, floor 5000")
else:
    ok(f"the two oracles agree on {nx} rows (libpcre2 10.46's refusal and offset vs python's strict decode over the §1.3 range)")

# ---- the design's §1 tables, reproduced exactly --------------------------
# (pattern, subject, start) -> (rc, startchar) or ("match", ov0, ov1); the
# values are utf_valid_design.md §1.1-§1.3's, typed from the note.
DESIGN = {
    ("a", b"a\xff", 0): ("-23", "1"), ("a", b"xa\xffz", 0): ("-23", "2"),
    ("b", b"\xffab", 2): ("match", "2", "3"),
    ("(?<=a)b", b"\xffab", 2): ("match", "2", "3"),
    ("(?<=..)b", b"\xffab", 2): ("-23", "0"),
    ("(?<=a|bc)d", b"\xffbcd", 3): ("match", "3", "4"),
    ("a", b"ab\xe3\x80", 0): ("-3", "2"), ("a", b"ab\xc0\x80", 0): ("-17", "2"),
    ("a", b"ab\xed\xa0\x80", 0): ("-16", "2"),
    ("a", b"ab\xf4\x90\x80\x80", 0): ("-15", "2"), ("a", b"ab\x80", 0): ("-22", "2"),
    ("a", b"\xc3\xa9a", 1): ("-36", None),
    ("a", b"\xc3\xa9\xffa", 1): ("-36", None), ("a", b"\x80\xa9a", 1): ("-36", None),
    ("(?<=a)b", b"\xc3\xa9\xffb", 1): ("-36", None),
    ("a", b"\xa9a\xff", 1): ("-23", "2"), ("(?<=a)b", b"\x80b", 1): ("-22", "0"),
    ("(?<=a)b", b"\x80\x80\x80b", 3): ("-22", "0"),
    ("(?<=a)b", b"a\x80\x80b", 3): ("-22", "1"),
    ("(?<=a)b", b"\xff\xc3\xa9\xa9b", 4): ("-22", "3"),
    ("b", b"\x80b", 0): ("-22", "0"), (r"\Ab", b"\xffab", 1): ("-23", "0"),
    ("a", b"\xa9a\xff", 5): ("-33", None),
}
seen = set()
for r in rows:
    if r.set != "pinned" or r.mode != "S":
        continue
    k = (r.pat, r.subj, r.sp)
    if k not in DESIGN or k in seen:
        continue
    seen.add(k)
    w = DESIGN[k]
    if w[0] == "match":
        good = int(r.rc) > 0 and (r.ov0, r.ov1) == (w[1], w[2])
    else:
        good = r.rc == w[0] and (w[1] is None or r.sc == w[1])
    if not good:
        bad(f"the transcript does not reproduce the design's §1 row [{r.pat}] {r.subj!r}@{r.sp}: want {w}, have rc {r.rc} sc {r.sc} ov ({r.ov0},{r.ov1})")
if len(seen) != len(DESIGN):
    bad(f"{len(seen)} of the design's {len(DESIGN)} §1 rows were found in the transcript")
else:
    ok(f"the 10.46 transcript reproduces the design's §1 tables exactly ({len(seen)} rows)")

# ---- the CLIP class: PCRE2_UTF's lookbehind reads stop at f ---------------
# MEASURED (this lane, 10.46 and 10.48): with UTF checking ON, libpcre2
# treats f -- startpos stepped back LB characters -- as the START OF THE
# SUBJECT for every backwards read: a `\b` at f sees no previous character,
# and a nested lookbehind that would step before f fails. So wherever a
# pattern's true read-behind (its REACH) exceeds LB -- the design's §1.4
# "no accumulation" residual -- PCRE2_UTF's ANSWER on an accepted subject can
# depend on startpos even on well-formed text: `(?<=\ba)b` on "xab" from 2
# is (2,3) under PCRE2_UTF and nomatch from 0 and without UTF. pcrec reads
# the real bytes there, with or without -futf-check (the design §1.4 said
# PCRE2 "reads them unvalidated"; it does not read them at all). The
# refusal set and the offset are exact for these patterns too; only the
# accepted ANSWER may differ, and it must then equal the default artifact's.
# The table names each pattern with its reach > LB, from the pattern text.
CLIP = {r"(?<=\ba)b": (2, 1), r"(?<=\b..)b": (3, 2), "(?<=(?<=..)a)b": (3, 2)}

# ---- pcrec -------------------------------------------------------------
by_pat = collections.OrderedDict()
for r in rows:
    by_pat.setdefault(r.pat, []).append(r)

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, timeout=TIMEOUT, **kw)

def build(pat, flags, tag):
    d = os.path.join(WORK, tag)
    os.makedirs(d, exist_ok=True)
    art = os.path.join(d, "gen.c")
    p = run([PCREC, "-p", "rx", "--features", "all"] + flags +
            ["-o", art, "--pattern", pat])
    if p.returncode != 0:
        return None, p.stderr.decode(errors="replace").strip()
    exe = os.path.join(d, "drv")
    c = run([CC, "-O1", "-std=gnu11", "-Wall", "-Wextra", "-Werror",
             "-I", d, "-o", exe, os.path.join(HERE, "driver.c"), art])
    if c.returncode != 0:
        return None, "driver build failed: " + c.stderr.decode(errors="replace")[:400]
    return (exe, art), None

def drive(exe, rs):
    inp = "".join(f"{r.subj.hex() or '-'} {r.sp} {r.qp} {r.mode}\n" for r in rs)
    p = run([exe], input=inp.encode())
    out = p.stdout.decode().splitlines()
    if p.returncode != 0 or len(out) != len(rs):
        return None
    return out

def expect_k(r, at_q):
    """The -futf-check answer, from the oracle's answer at the queried
    position. `at_q` False: the row's startpos is mid-character and the
    artifact refuses (K50 first) -- -36's mapping."""
    rc = int(r.rc) if at_q else -36
    if r.mode == "S":
        if utf_err(r.rc) and at_q: return ("S", "-9")
        if rc == -36: return ("S", "-7")
        if rc in (-33, -1): return ("S", "0")
        return ("S", "1", r.ov0, r.ov1)
    if utf_err(r.rc) and at_q: return ("A", "-9")
    if rc == -36: return ("A", "-7")
    if rc in (-33, -1): return ("A", "-1")
    # anchored: the entries return the CONSUMED length (\K cannot move it),
    # and match_caps reports PCRE2's own span
    return ("A", str(int(r.ov1) - r.qp), r.ov0, r.ov1)

def shape(line):
    f = line.split()
    if f[0] == "S":
        return (("S", f[1]) if f[1] != "1" else ("S", "1", f[2], f[3])), f[4], f[5]
    if f[0] == "A":
        return (("A", f[1]) if int(f[1]) < 0 else ("A", f[1], f[3], f[4])), f[5], f[6]
    return (tuple(f),), None, None

npat = 0
counts = collections.Counter()
for pat, rs in by_pat.items():
    if rs[0].rc == "compile":
        continue
    # --- K / KV / KW -------------------------------------------------------
    arts = {}
    for tag, pp, flags in (("K", pat, ["-e", "utf8", "-futf-check"]),
                           ("KV", pat, ["-e", "utf8", "-futf-check", "--engine=vm"]),
                           ("KW", "(" + pat + ")", ["-e", "utf8", "-futf-check"]),
                           ("KA", pat, ["-e", "utf8", "-futf-check", "-fstartpos-guard=align"]),
                           ("A", pat, ["-e", "utf8", "-fstartpos-guard=align"]),
                           ("D", pat, ["-e", "utf8"])):
        built, err = build(pp, flags, f"p{npat}_{tag}")
        if built is None:
            if tag == "K":
                break          # pcrec does not compile this pattern at all
            bad(f"[{pat}] compiles under -futf-check but not as config {tag}: {err}")
            continue
        arts[tag] = built
    if "K" not in arts:
        counts["refused"] += 1
        continue
    npat += 1
    # --- LB --------------------------------------------------------------
    lbline = [l for l in open(arts["K"][1]) if l.startswith("#define rx_VALID_LB ")]
    lb = lbline[0].split()[2] if lbline else "?"
    if lb != rs[0].mlb:
        bad(f"[{pat}] rx_VALID_LB is {lb}, libpcre2 10.46's MAXLOOKBEHIND is {rs[0].mlb}")
    else:
        counts["lb"] += 1
    # --- K-family rows (qpos == startpos) ----------------------------------
    plain = [r for r in rs if r.qp == r.sp]
    clipped = {}
    for tag in ("K", "KV", "KW"):
        if tag not in arts: continue
        out = drive(arts[tag][0], plain)
        if out is None:
            bad(f"[{pat}] config {tag}: the driver crashed or printed the wrong number of lines")
            continue
        for i, (r, line) in enumerate(zip(plain, out)):
            got, v1, v2 = shape(line)
            want = expect_k(r, True)
            if got != want and pat in CLIP and len(got) > 1 and want[1] not in ("-9", "-7") \
               and got[1] not in ("-9", "-7"):
                # the clip class: the refusal matched (neither side refused);
                # the accepted answer is pcrec's own, checked against D below
                clipped.setdefault(tag, {})[i] = got
                counts["clip-" + tag] += 1
                continue
            if got != want:
                bad(f"[{pat}] {tag} {r.mode} {r.subj!r}@{r.sp}: want {want}, got {line}")
                continue
            if utf_err(r.rc) and v1 != r.sc:
                bad(f"[{pat}] {tag} valid_upto {r.subj!r}@{r.sp} = {v1}, libpcre2 startchar {r.sc}")
                continue
            if not utf_err(r.rc) and int(r.rc) != -36 and v1 != str(len(r.subj)):
                bad(f"[{pat}] {tag} valid_upto {r.subj!r}@{r.sp} = {v1} on a range libpcre2 accepts (want {len(r.subj)})")
                continue
            counts[tag] += 1
            if want[1] == "-9": counts[tag + "-refused"] += 1
    # --- KA / A: align rows, answered at the aligned position -------------
    al = [r for r in rs if r.set == "align"]
    for tag in ("KA", "A"):
        if tag not in arts or not al: continue
        sel = al if tag == "KA" else [r for r in al if py_offset(r.subj, 0, 0) == len(r.subj)]
        out = drive(arts[tag][0], sel)
        if out is None:
            bad(f"[{pat}] config {tag}: the driver crashed or printed the wrong number of lines")
            continue
        for r, line in zip(sel, out):
            got, v1, v2 = shape(line)
            want = expect_k(r, True)
            if tag == "A" and want[1] == "-9":
                bad(f"[{pat}] A: a well-formed align row reads a UTF error in the oracle ({r})")
                continue
            if r.mode == "A" and r.qp != r.sp and want[1] != "-9":
                want = ("A", "-1")        # no match begins inside a character
            if got != want:
                bad(f"[{pat}] {tag} {r.mode} {r.subj!r}@{r.sp} (aligned {r.qp}): want {want}, got {line}")
                continue
            if utf_err(r.rc) and v2 != r.sc:
                bad(f"[{pat}] {tag} valid_upto at the aligned {r.qp} = {v2}, libpcre2 startchar {r.sc}")
                continue
            counts[tag] += 1
            if r.qp != r.sp: counts[tag + "-moved"] += 1
            if want[1] == "-9": counts[tag + "-refused"] += 1
    # --- D: the default artifact ------------------------------------------
    if "D" in arts:
        out = drive(arts["D"][0], plain)
        if out is None:
            bad(f"[{pat}] config D: the driver crashed")
        else:
            for i, (r, line) in enumerate(zip(plain, out)):
                got, v1, v2 = shape(line)
                if len(got) < 2:
                    bad(f"[{pat}] D: {line}")
                    continue
                if got[1] == "-9":
                    bad(f"[{pat}] the DEFAULT artifact returned PCREC_ERR_UTF ({r})")
                    continue
                if utf_err(r.rc):
                    if v1 != r.sc:
                        bad(f"[{pat}] D valid_upto {r.subj!r}@{r.sp} = {v1}, want {r.sc} (the entry is the check's, flag or not)")
                        continue
                    counts["D-tolerant"] += 1
                    continue
                want = expect_k(r, True)
                if pat in CLIP and any(i in c for c in clipped.values()):
                    # the checked artifacts' own answer is the expectation
                    for tag, c in clipped.items():
                        if i in c and c[i] != got:
                            bad(f"[{pat}] clip row {r.subj!r}@{r.sp}: {tag} answered {c[i]}, the default artifact {got} -- -futf-check must not move an accepted answer")
                    counts["D-clip"] += 1
                    continue
                if got != want:
                    bad(f"[{pat}] D {r.mode} {r.subj!r}@{r.sp}: on a range libpcre2 accepts the default answer must equal the checked one: want {want}, got {line}")
                    continue
                counts["D"] += 1
        text = open(arts["D"][1]).read()
        if "return PCREC_ERR_UTF;" in text or '_UTF_CHECK "off"' not in text:
            bad(f"[{pat}] the default -e utf8 artifact emits a check or does not stamp UTF_CHECK \"off\"")
    ktext = open(arts["K"][1]).read()
    if '_UTF_CHECK "whole"' not in ktext:
        bad(f"[{pat}] the -futf-check artifact does not stamp UTF_CHECK \"whole\"")
    if "KA" in arts and '_STARTPOS_GUARD "align"' not in open(arts["KA"][1]).read():
        bad(f"[{pat}] the -fstartpos-guard=align artifact does not stamp STARTPOS_GUARD \"align\"")
    # --- B: byte-inert ----------------------------------------------------
    b0 = os.path.join(WORK, f"p{npat}_B0"); b1 = os.path.join(WORK, f"p{npat}_B1")
    os.makedirs(b0, exist_ok=True); os.makedirs(b1, exist_ok=True)
    p0 = run([PCREC, "-p", "rx", "--features", "all", "-o", os.path.join(b0, "gen.c"), "--pattern", pat])
    p1 = run([PCREC, "-p", "rx", "--features", "all", "-futf-check", "-fstartpos-guard=align",
              "-o", os.path.join(b1, "gen.c"), "--pattern", pat])
    if p0.returncode != p1.returncode:
        bad(f"[{pat}] -e byte: the inert flags changed whether the pattern compiles")
    elif p0.returncode == 0:
        same = all(open(os.path.join(b0, x), "rb").read() == open(os.path.join(b1, x), "rb").read()
                   for x in ("gen.c", "gen.h"))
        if not same:
            bad(f"[{pat}] -e byte: -futf-check -fstartpos-guard=align MOVED the artifact; both must be inert under byte")
        else:
            txt = open(os.path.join(b1, "gen.c")).read()
            if '_UTF_CHECK "inert"' not in txt:
                bad(f"[{pat}] -e byte artifact does not stamp UTF_CHECK \"inert\"")
            else:
                counts["B"] += 1

# ---- populations, floored (K35: an empty population is a red result) ----
# MEASURED on the first green run (2026-09-30, lane uvbuild) and rounded
# DOWN; a population below its floor means an arm stopped reaching what it
# exists to check (K35), never "fewer problems".
FLOORS = {
    "lb": 40, "K": 6000, "K-refused": 2600, "KV": 6000, "KV-refused": 2600,
    "KW": 6000, "KW-refused": 2600, "KA": 1250, "KA-moved": 350,
    "KA-refused": 220, "A": 800, "A-moved": 270, "D": 3300,
    "D-tolerant": 2600, "B": 40,
}
# The CLIP class is a DOCUMENTED DIVERGENCE, so it is pinned EXACT in both
# directions: more rows means pcrec's answer moved away from PCRE2's on a
# new cell, fewer means the class is no longer exercised.
CLIP_EXACT = {"clip-K": 4, "clip-KV": 4, "clip-KW": 4, "D-clip": 4}
for k, want in CLIP_EXACT.items():
    if counts[k] != want:
        bad(f"population {k} is {counts[k]}, pinned EXACTLY {want} -- the PCRE2_UTF lookbehind-clip divergence (the CLIP table above) moved")
print("populations: " + ", ".join(f"{k}={counts[k]}" for k in sorted(counts)))
for k, fl in FLOORS.items():
    if counts[k] < fl:
        bad(f"population {k} is {counts[k]}, floor {fl} -- the arm no longer reaches what it exists to check")
if npat < 30:
    bad(f"only {npat} patterns compiled, floor 30")
else:
    ok(f"{npat} patterns compiled under every config; {counts['refused']} the oracle knows pcrec refuses")
if not fails:
    ok("every config agrees with libpcre2 10.46 (and python) on every row")
print(f"checks passed: {passes}")
print(f"checks failed: {len(fails)}")
sys.exit(1 if fails else 0)
