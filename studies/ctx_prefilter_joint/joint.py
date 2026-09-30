#!/usr/bin/env python3
"""joint.py -- [CTX-PREFILTER] JOINT-POSITION measurement (lane ctxjoint).

STEP 0 (docs/dev/ctx_prefilter_census.md) estimated the prefilter
tightening with an INDEPENDENCE MODEL. This script measures the JOINT
quantity on real subjects: of the positions the lookaround-free prefilter
admits as candidate match starts, how many would the proposed NECESSARY
ONE-CHARACTER CONTEXT CONDITION actually reject?

Derivation (documented equivalence, no compiler involved):

  B0  the "prefilter pattern": the pattern text with every lookaround
      construct ERASED, except the single-character ones (shape a), which
      [UCP] U2's A_CTX already hosts EXACTLY in the DFA and which stay as
      real lookarounds.  Its candidate set is
          C0 = { p : B0 matches (anchored) at p }
      -- the positions a sound lookaround-free superset admits as a match
      start, which is what the hybrid prefilter's forward+reverse DFA pair
      hands the VM.  (S0 = the same with EVERY lookaround erased, kept as a
      sensitivity column.)
  E1  B0 with each POSITIVE multi-character lookaround (shape b/c/d whose
      necessary set is computable, not quantified) REPLACED IN PLACE by its
      one-character condition:  (?=abc) -> (?=[a]),  (?<=xy) -> (?<=[y]).
          C1 = { p : E1 matches at p }        C1 is a subset of C0.
  T   the ORIGINAL pattern: T = { p : P matches at p }.
          T must be a subset of C1  (SOUNDNESS CONTROL: the condition is
          NECESSARY, so it may never reject a true match start).

  rejection      = (|C0| - |C1|) / |C0|
  false-cand rem = (|C0| - |C1|) / (|C0| - |T|)   (share of the FALSE
                   candidates the condition removes; the ceiling is 1.0)

Anchored-at-p membership is computed by libpcre2 itself (exact PCRE
semantics, unlike python `re`) by wrapping the pattern as (?=(?:P)) and
jumping between hits with one unanchored search per hit.

Reads: studies/ctx_prefilter_joint/population.tsv (the 354 still-VM rows
of U2's route manifest, df93ecf5), docs/dev/lookaround_census/{lac_engine,
shape_classify}.py (the step-0 parsers, imported unchanged).

usage: joint.py PCREC OUTDIR SUBJECT[,SUBJECT...] [--controls-only]
"""
import ctypes
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CENSUS = os.path.join(HERE, "..", "..", "docs", "dev", "lookaround_census")
sys.path.insert(0, CENSUS)
import lac_engine as L      # noqa: E402
import shape_classify as sc  # noqa: E402

PCRE2_UTF = 0x00080000
LIBPATH = os.environ.get("PCREC_PCRE2_PATH", "/opt/homebrew/lib/libpcre2-8.dylib")
lib = ctypes.CDLL(LIBPATH)
lib.pcre2_compile_8.restype = ctypes.c_void_p
lib.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32,
                                ctypes.POINTER(ctypes.c_int),
                                ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
lib.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
lib.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
lib.pcre2_match_8.restype = ctypes.c_int
lib.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t,
                              ctypes.c_size_t, ctypes.c_uint32, ctypes.c_void_p,
                              ctypes.c_void_p]
lib.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
lib.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
lib.pcre2_code_free_8.argtypes = [ctypes.c_void_p]
lib.pcre2_match_data_free_8.argtypes = [ctypes.c_void_p]
lib.pcre2_get_error_message_8.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_size_t]


class Refused(Exception):
    pass


def positions(pattern, subject, utf):
    """Sorted list of p in [0, len(subject)] where `pattern` matches at p."""
    wrapped = b"(?=(?:" + pattern + b"))"
    err = ctypes.c_int()
    eoff = ctypes.c_size_t()
    code = lib.pcre2_compile_8(wrapped, len(wrapped), PCRE2_UTF if utf else 0,
                               ctypes.byref(err), ctypes.byref(eoff), None)
    if not code:
        buf = ctypes.create_string_buffer(256)
        lib.pcre2_get_error_message_8(err.value, buf, 256)
        raise Refused("compile: %s" % buf.value.decode())
    md = lib.pcre2_match_data_create_from_pattern_8(code, None)
    ov = lib.pcre2_get_ovector_pointer_8(md)
    n = len(subject)
    out = []
    off = 0
    try:
        while off <= n:
            rc = lib.pcre2_match_8(code, subject, n, off, 0, md, None)
            if rc == -1:
                break
            if rc < 0:
                raise Refused("match rc=%d" % rc)
            p = ov[0]
            out.append(p)
            off = p + 1
    finally:
        lib.pcre2_match_data_free_8(md)
        lib.pcre2_code_free_8(code)
    return out


def cls(byteset):
    """A bytes character class for a set of byte values."""
    bs = sorted(byteset)
    if len(bs) > 128:
        comp = sorted(set(range(256)) - set(bs))
        return b"[^" + b"".join(b"\\x%02x" % b for b in comp) + b"]"
    return b"[" + b"".join(b"\\x%02x" % b for b in bs) + b"]"


def top_level(occs, pat):
    """Occurrences with spans not contained in an earlier (outer) span."""
    spans = sorted(((L.construct_span(pat, o["offset"]), o) for o in occs),
                   key=lambda t: (t[0][0], -t[0][1]))
    out, hi = [], -1
    for (s, e), o in spans:
        if s >= hi:
            out.append((s, e, o))
            hi = e
    return out


def plan(pat):
    """Returns (b0, s0, e1, conds, notes): the B0/S0/E1 pattern texts, the
    list of applied conditions [(kind, size, body)], and skip notes."""
    occs = sc.classify_pattern(pat)
    if occs is None:
        raise Refused("classify: unparsed")
    tl = top_level(occs, pat)
    b0, s0, e1 = bytearray(), bytearray(), bytearray()
    conds, notes = [], []
    last = 0
    for s, e, o in tl:
        seg = pat[last:s]
        for buf in (b0, s0, e1):
            buf += seg
        last = e
        text = pat[s:e]
        keep_a = (o["shape"] == "a")
        s0 += b""                                   # S0 erases every construct
        b0 += text if keep_a else b""
        rep = None
        quantified = not text.endswith(b")")
        if o["polarity"] == "+" and o["shape"] in ("b", "c", "d"):
            branches, resolved = L.try_parse_body_loose(o["body"])
            if not resolved:
                notes.append("unresolved-body")
            elif quantified:
                notes.append("quantified-construct")
            else:
                nec = (L.body_first_set(branches) if o["kind"] == "lookahead"
                       else L.body_last_set(branches))
                if nec is None:
                    notes.append("zero-width-possible")
                else:
                    rep = (b"(?=" if o["kind"] == "lookahead" else b"(?<=") + cls(nec) + b")"
                    conds.append((o["kind"], len(nec), o["body"].decode("latin-1")))
        e1 += rep if rep is not None else (text if keep_a else b"")
    tail = pat[last:]
    for buf in (b0, s0, e1):
        buf += tail
    return bytes(b0), bytes(s0), bytes(e1), conds, notes


def load_narrow():
    """(id, kind, body) -> step-0 narrow verdict, from the committed census."""
    d = {}
    p = os.path.join(CENSUS, "ctx_prefilter_61cbc894.tsv")
    for line in open(p, encoding="utf-8").read().splitlines()[1:]:
        f = line.split("\t")
        if len(f) > 5 and f[4].isdigit():
            d[(f[0], f[1], f[3])] = (f[5] == "True")
    return d


NARROW = load_narrow()


def selectivity(subject, byteset):
    tbl = bytearray(256)
    for b in byteset:
        tbl[b] = 1
    return sum(tbl[b] for b in subject) / len(subject)


def stamps(pcrec, pat, enc):
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "o.c")
        r = subprocess.run(["timeout", "20", pcrec, "--features", "all", "-e", enc,
                            "-o", out, "--pattern-esc" if False else "--pattern",
                            pat.decode("utf-8", "surrogateescape")],
                           capture_output=True)
        if r.returncode != 0:
            return "refused", "refused"
        src = open(out, errors="replace").read()
    g = lambda k: (re.search(r'#define %s "([^"]*)"' % k, src) or [None, "?"])[1]
    return g("RX_VM_PREFILTER"), g("RX_REQ_BYTE")


def measure(name, pat, subject, utf):
    b0, s0, e1, conds, notes = plan(pat)
    c0 = positions(b0, subject, utf)
    row = dict(id=name, n_conds=len(conds), notes=",".join(sorted(set(notes))) or "-",
               conds=";".join("%s/%d/%s" % c for c in conds), c0=len(c0))
    if not conds:
        return row
    c1 = positions(e1, subject, utf)
    t = positions(pat, subject, utf)
    sc0, sc1, st = set(c0), set(c1), set(t)
    row.update(c1=len(c1), t=len(t), sound=int(st <= sc1), nested=int(sc1 <= sc0),
               rej=(len(c0) - len(c1)) / len(c0) if c0 else None,
               false_rem=((len(c0) - len(c1)) / (len(c0) - len(t))
                          if len(c0) > len(t) else None))
    cs0 = set(positions(s0, subject, utf))
    row["s0"] = len(cs0)
    return row


def model_pass(pat, subject):
    """The step-0 independence model's survival fraction: the product of the
    necessary sets' own selectivities on the same subject."""
    _, _, _, conds_sets = None, None, None, None
    occs = sc.classify_pattern(pat) or []
    prod, k = 1.0, 0
    for s, e, o in top_level(occs, pat):
        if o["polarity"] != "+" or o["shape"] not in ("b", "c", "d") or not pat[s:e].endswith(b")"):
            continue
        br, ok = L.try_parse_body_loose(o["body"])
        if not ok:
            continue
        nec = L.body_first_set(br) if o["kind"] == "lookahead" else L.body_last_set(br)
        if nec is None:
            continue
        prod *= selectivity(subject, nec)
        k += 1
    return prod if k else None


CONTROLS = [
    # (name, pattern, subject, expected_c0, expected_c1, expected_rejection)
    ("ctl-ahead-75", rb"x(?=ab)", (b"xa" * 1000) + (b"xb" * 3000), 4000, 1000, 0.75),
    ("ctl-behind-75", rb"(?<=xy)w", (b"yw" * 1000) + (b"zw" * 3000), 4000, 1000, 0.75),
    ("ctl-zero", rb"x(?=ab)", b"xa" * 500, 500, 500, 0.0),
    ("ctl-all", rb"x(?=ab)", b"xb" * 500, 500, 0, 1.0),
]


def run_controls(out):
    ok = True
    for name, pat, subj, e0, e1, er in CONTROLS:
        r = measure(name, pat, subj, False)
        good = (r["c0"] == e0 and r["c1"] == e1 and abs(r["rej"] - er) < 1e-12 and r["sound"] == 1)
        ok &= good
        out.write("%-16s c0=%d c1=%d t=%d rej=%.4f expected %.4f  %s\n"
                  % (name, r["c0"], r["c1"], r["t"], r["rej"], er, "PASS" if good else "FAIL"))
    return ok


def main():
    pcrec, outdir, subjects = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "controls.txt"), "w") as f:
        ok = run_controls(f)
        f.write("controls: %s\n" % ("ALL PASS" if ok else "FAILED"))
    print("controls:", "ALL PASS" if ok else "FAILED", file=sys.stderr)
    if not ok or "--controls-only" in sys.argv:
        return
    pop = []
    for line in open(os.path.join(HERE, "population.tsv"), encoding="utf-8"):
        rid, enc, pat = line.rstrip("\n").split("\t")
        pop.append((rid, enc, pat.encode("utf-8", "surrogateescape")))
    cols = ["subject", "id", "enc", "prefilter", "req_byte", "narrow", "n_conds", "conds", "notes",
            "c0", "s0", "c1", "t", "rej", "false_rem", "sound", "nested",
            "model_pass", "meas_pass", "n_bytes"]
    stamp_cache = {}
    with open(os.path.join(outdir, "joint.tsv"), "w") as f:
        f.write("\t".join(cols) + "\n")
        for sj in subjects:
            subject = open(sj, "rb").read()
            for rid, enc, pat in pop:
                try:
                    occs = plan(pat)
                except Refused:
                    continue
                if not occs[3]:
                    continue          # no applicable condition: outside the 143
                # The conditions are BYTE sets, and libpcre2's UTF mode would read
                # a \\xA9 in a class as U+00A9, so the utf8 rows are measured in
                # byte mode (pattern text is the raw UTF-8 bytes); their `enc`
                # column keeps them separable from the byte rows.
                utf = False
                key = (pat, enc)
                if key not in stamp_cache:
                    stamp_cache[key] = stamps(pcrec, pat, enc)
                try:
                    r = measure(rid, pat, subject, utf)
                except Refused as e:
                    r = dict(id=rid, notes="refused:%s" % e)
                nar = [NARROW.get((rid, c.split("/")[0], c.split("/", 2)[2])) for c in r["conds"].split(";")] if r.get("conds") else []
                r.update(n_bytes=len(subject), narrow=("y" if nar and all(nar) else "n"),
                         subject=os.path.basename(sj), enc=enc,
                         prefilter=stamp_cache[key][0], req_byte=stamp_cache[key][1])
                if r.get("c0"):
                    r["model_pass"] = model_pass(pat, subject)
                    r["meas_pass"] = r["c1"] / r["c0"] if "c1" in r else None
                f.write("\t".join("" if r.get(c) is None else
                                  ("%.6g" % r[c] if isinstance(r[c], float) else str(r[c]))
                                  for c in cols) + "\n")
                f.flush()


if __name__ == "__main__":
    main()
