#!/usr/bin/env python3
"""[START-SET] edge lane (ssedge): compile one block, read its sets, decide
which hat (if any) the D148/addendum-1 predicates admit, and build the twins.

Shared by `classify.py`, `mut.py`.  Reads the EMITTED artifact (the same way
`../rev2/estar.py` does, extended to keep the per-seed escape sets so the
"E* omitting one seed state" mutants can be built) and the AST start set from
`fsp` (`fsp.c`, `../fs_probe.c` with the compile's options read).

Env: PCREC (the compiler), FSP (the built fsp probe), W (scratch dir).
"""
import os, re, subprocess

PCREC = os.environ.get("PCREC", "build/pcrec")
FSP = os.environ.get("FSP")


def pflags(b):
    """pcrec argv for a block dict (flags i/u, enc, engine, xflags)."""
    a = ["--features", "all"]
    if b.get("enc", "byte") == "utf8": a += ["-e", "utf8"]
    if "i" in b.get("flags", ""): a += ["-i"]
    if "u" in b.get("flags", ""): a += ["--ucp"]
    if b.get("engine") == "vm": a += ["--engine=vm"]
    if b.get("frames"): a += ["--backtrack-frames=%d" % b["frames"]]
    a += b.get("xflags", [])
    return a


def compile_block(b, d, prefix):
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, prefix + ".c")
    r = subprocess.run([PCREC, *pflags(b), "-p", prefix, "-o", out, "--pattern", b["pat"].encode()],
                       capture_output=True)
    if r.returncode: return None, r.stderr.decode(errors="replace").strip().splitlines()[0]
    return out, None


def stamps(src):
    return dict(re.findall(r'#define RX_(\w+) "?([^"\n]*)"?', src)) if src else {}


def table(src, name):
    m = re.search(r"static const (?:unsigned |signed )?(?:char|short|int) %s\[(\d+)\] = \{(.*?)\};" % re.escape(name), src, re.S)
    if not m: return None
    v = [int(x) for x in re.findall(r"-?\d+", m.group(2))]
    assert len(v) == int(m.group(1)), name
    return v


def fsp_set(b):
    a = []
    if b.get("enc", "byte") == "utf8": a += ["-e", "utf8"]
    if "i" in b.get("flags", ""): a += ["-i"]
    if "u" in b.get("flags", ""): a += ["--ucp"]
    line = "x\t%s\n" % b["pat"].encode().hex()
    out = subprocess.run([FSP, *a], input=line, capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1].split("\t")
    if out[1] != "ok": return None, None
    h = bytes.fromhex(out[4])
    return {i for i in range(256) if h[i >> 3] >> (i & 7) & 1}, out[2] == "1"


def machine(src, p):
    """The forward machine the skip lives in: E, per-seed escape sets, Tdfa."""
    cls = table(src, p + "_forward_byte_class"); nxt = table(src, p + "_forward_next_state")
    seed = table(src, p + "_forward_seed_state"); cbm = table(src, p + "_can_begin_match")
    if cls is None or nxt is None: return None
    im = re.search(r"%s_forward_state forward_state = (?:\w+ \? %s_forward_seed_state\[.*?\] : )?(\d+);" % (re.escape(p), re.escape(p)), src)
    if not im: return None
    s0 = int(im.group(1))
    step = re.search(r"%s_forward_step\(.*?\)\s*\{\s*return transitions\[(.*?)\];" % re.escape(p), src, re.S)
    sm = re.fullmatch(r"s(?: \* (\d+))? \+ cl", step.group(1).strip())
    stride = int(sm.group(1) or 1)
    dm = re.search(r"%s_forward_is_dead\(%s_forward_state s\) \{ return s (==|<) (\d+);" % (re.escape(p), re.escape(p)), src)
    isdead = (lambda s, v=int(dm.group(2)): s == v) if dm.group(1) == "==" else (lambda s: s < 0)
    d = lambda s, c: nxt[s * stride + cls[c]]
    seeds = sorted(set(seed or []) | {s0})
    esc = {s: {c for c in range(256) if d(s, c) != s} for s in seeds}
    td = {c for s in seeds for c in range(256) if d(s, c) not in seeds and not isdead(d(s, c))}
    return {"s0": s0, "seeds": seeds, "seeded": seed is not None, "esc": esc, "E": esc[s0],
            "Estar": set().union(*esc.values()), "Tdfa": td,
            "cbm": None if cbm is None else {c for c in range(256) if cbm[c]}}


SKIP_RE = (r"( *)while \(scan_position( \+ 1)? < subject_length && !%s_can_begin_match\[subject\[scan_position\]\]\) scan_position\+\+;\n"
           r"((?: *)if \(scan_position >= subject_length\) return 0;\n)?")


def classify(b, d):
    """Compile; return a dict with the route, the sets and the hat verdict."""
    path, err = compile_block(b, d, "rx")
    if not path: return {"status": "refused", "err": err}
    src = open(path).read(); st = stamps(src)
    S, nullable = fsp_set(b)
    o = {"status": "ok", "path": path, "engine": st.get("ENGINE"), "vmpf": st.get("VM_PREFILTER", ""),
         "dfapf": st.get("DFA_PREFILTER", ""), "scan": st.get("DFA_SCAN", ""), "vmstart": st.get("VM_START", ""),
         "handoff": st.get("REQ_HANDOFF", ""), "utfcheck": st.get("UTF_CHECK", ""), "S": S, "nullable": nullable}
    m = machine(src, "rx")
    o["m"] = m
    hat = "none"
    if (m and m["seeded"] and o["scan"] == "unanchored" and o["dfapf"] in ("byte-class", "byte-class-bounded")
            and len(re.findall(SKIP_RE % "rx", src)) == 1):
        o["skip_bounded"] = o["dfapf"].endswith("bounded")
        if S is not None and not nullable and len(S) < 256:
            T = S & m["Estar"]
            if T and T < m["E"]: hat = "dfa"
    elif o["engine"] == "vm" and o["vmpf"] == "none" and o["vmstart"] == "unanchored":
        if S is not None and not nullable and len(S) < 256: hat = "vm"
        elif S is not None and nullable and len(S) < 256: hat = "vm-nullable"   # V's non-nullable conjunct declines
    o["hat"] = hat
    return o


# ---- DFA-hat twin: write T, add the re-seed (none / conditional / unconditional) ----
def dfa_twin(src, p, T, reseed="cond"):
    m = re.search(r"(static const unsigned char %s_can_begin_match\[256\] = \{)(.*?)(\};)" % p, src, re.S)
    assert m, "no can_begin_match"
    src = src[:m.start()] + m.group(1) + "\n        " + ", ".join("1" if i in T else "0" for i in range(256)) + "\n    " + m.group(3) + src[m.end():]
    ms = list(re.finditer(SKIP_RE % p, src)); assert len(ms) == 1, "skip count %d" % len(ms)
    k = ms[0]; ind = k.group(1)
    seed = "%s_forward_seed_state[%s_forward_byte_class[subject[scan_position - 1]]]" % (p, p)
    s0m = re.search(r"%s_forward_state forward_state = (?:\w+ \? %s_forward_seed_state\[.*?\] : )?(\d+);" % (p, p), src)
    if reseed == "cond":
        rs = "%sif (scan_position > entry_position) forward_state = %s;\n" % (ind, seed)
    elif reseed == "uncond":   # pf_emit_ofs_reseed's form (emit_dfa.c:6373)
        rs = "%sforward_state = scan_position ? %s : %s;\n" % (ind, seed, s0m.group(1))
    else:
        rs = ""
    new = "%ssize_t entry_position = scan_position; (void)entry_position;\n" % ind + k.group(0) + rs
    return src[:k.start()] + new + src[k.end():]


def dfa_pre_seek_before_validation(src, p, T):
    """The 'seek placed before UTF validation' mutant, DFA-hat form: a first-memchr
    style early `return 0` (no byte of T in [search_from, n)) hoisted above the
    -futf-check refusal in <p>_search."""
    tbl = ", ".join("1" if i in T else "0" for i in range(256))
    pat = r"(    if \(%s_valid_upto\(subject, subject_length, search_from\) != subject_length\) return PCREC_ERR_UTF;\n)" % p
    m = re.search(pat, src)
    if not m: return None
    pre = ("    { static const unsigned char %s_pre_T[256] = { %s };\n"
           "      size_t q = search_from; while (q < subject_length && !%s_pre_T[subject[q]]) q++;\n"
           "      if (q >= subject_length) return 0; }\n") % (p, tbl, p)
    return src[:m.start()] + pre + src[m.start():]


# ---- VM-hat twin: the entry seek and the retry seek (../twin/vmtwin.py's shape) ----
def vm_twin(src, p, S, variant="ok"):
    """variant: ok | late (seek starts one byte late: q+1) | retry-skip (the retry
    seek skips the next valid start) | before-valid (entry seek above the -futf-check
    refusal) | nullable (the seek applied though the pattern is nullable: same code,
    the caller passes the nullable pattern's S)."""
    vals = ", ".join("1" if i in S else "0" for i in range(256))
    def seek(ind, start):
        return ("%s{\n%s    static const unsigned char %s_start_set[256] = { %s };\n"
                "%s    %s\n"
                "%s    while (attempt_position < subject_length && !%s_start_set[subject[attempt_position]]) attempt_position++;\n"
                "%s    if (attempt_position >= subject_length) return 0;\n%s}\n") % (
            ind, ind, p, vals, ind, start, ind, p, ind, ind)
    assert "_prefilter(" not in src, "hybrid: VM hat applies to prefilter-less VM only"
    old_e = "    attempt_position = search_from;\n"
    assert src.count(old_e) == 1, "entry count %d" % src.count(old_e)
    late = "if (attempt_position < subject_length) attempt_position++;" if variant == "late" else ""
    if variant == "before-valid":
        vm = re.search(r"    if \(%s_valid_upto\(subject, subject_length, search_from\) != subject_length\) return PCREC_ERR_UTF;\n" % p, src)
        if not vm: return None
        pre = ("    { static const unsigned char %s_pre_S[256] = { %s };\n"
               "      size_t q = search_from; while (q < subject_length && !%s_pre_S[subject[q]]) q++;\n"
               "      if (q >= subject_length) return 0; }\n") % (p, vals, p)
        src = src[:vm.start()] + pre + src[vm.start():]
    src = src.replace(old_e, old_e + seek("    ", late), 1)
    old_r = "\n    }\n    if (capture_spans)"
    assert src.count(old_r) == 1, "loop-end count %d" % src.count(old_r)
    rlate = late if variant == "late" else ("if (attempt_position < subject_length) attempt_position++;" if variant == "retry-skip" else "")
    src = src.replace(old_r, "\n" + seek("        ", rlate).rstrip("\n") + "\n    }\n    if (capture_spans)", 1)
    return src


