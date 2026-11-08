#!/usr/bin/env python3
"""u3tgt_movers.py -- [XARCH-DEV] U2+U3's DECLARED-MOVERS proof (lane u3tgt).

Compiles every distinct corpus pattern (emit_sweep's own population:
enumerate_corpus over the tree's .rxt files) with a REF pcrec (the merge base,
abi 97) and the LANE pcrec (abi 98), at byte and utf8, default engine and
--engine=vm, in two modes, and holds every difference to the prediction the
brief declared:

  default   (no SIMD flag) the abi digits and one `<PREFIX>_TARGETS` line
            ("none:generic"), nothing else: the ref's text with the abi
            digits renumbered and that line added must EQUAL the lane's.
  simd      (`-fmemfn-simd=TARGET` on both sides, the same token) the lane
            ADDS only the TARGETS line, the guarded-bytes and forms stamps
            and the target's fixed text (the kit's guard and region, measured
            on a control pattern no kit row serves, never spelled here); it
            REMOVES only CPU `#if`/`#elif`/`#else`/`#endif` lines, the levels
            the target does not admit (each such `#if` block whole), the
            selector's other arms and blank lines. Its MEMFN_FORMS is the
            ref's with the unadmitted levels dropped (`vrun@w32+w16` ->
            `vrun@w16` at the baseline target).

A refusal on one side only is a failure. CONTROL: every compiled cell is
judged a second time with one line planted in the lane's text, which must be
rejected (a judge that accepts everything fails the run). Prints one line per (mode, enc,
engine) cell (patterns, movers, failures) and up to 5 failure samples per
cell; exit 0 iff no failure.

Usage: u3tgt_movers.py REF_BIN LANE_BIN TREE TARGET [--jobs N] [--limit N]
"""
import concurrent.futures
import difflib
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../scripts"))
import emit_sweep as es  # noqa: E402

ABI_RE = [(re.compile(rb"\(abi 97\)"), b"(abi 98)"),
          (re.compile(rb"\(PCREC_(\w+)_ABI_H \+ 0\) != 97"), rb"(PCREC_\1_ABI_H + 0) != 98"),
          (re.compile(rb"#define PCREC_(\w+)_ABI_H 97\b"), rb"#define PCREC_\1_ABI_H 98"),
          (re.compile(rb"\.abi = 97,"), b".abi = 98,")]
STAMP_RE = re.compile(rb"^#define \w+_(TARGETS|SIMD_GUARDED_BYTES|MEMFN_FORMS) ")
FORMS_RE = re.compile(rb'^#define \w+_MEMFN_FORMS "([^"]*)"', re.M)
CPU_PP = re.compile(rb"^#\s*(if|elif)\b.*\b(__x86_64__|__aarch64__|__SSE2__|__AVX2__|__ARM_NEON)")
PP_ELSE_END = re.compile(rb"^#\s*(else|endif)\b")


def renumber(text):
    for rx, rep in ABI_RE:
        text = rx.sub(rep, text)
    return text


def lines(b):
    return b.splitlines(keepends=True)


def fixed_lines(ref, lane, extra):
    """The lines the lane's target adds to a control pattern no kit row serves."""
    ok_r, r = es.compile_stream_c(ref, b"a", 30, extra=extra)[:2]
    ok_l, l = es.compile_stream_c(lane, b"a", 30, extra=extra)[:2]
    if not (ok_r and ok_l):
        sys.exit("control pattern refused")
    rl, ll = lines(renumber(r)), lines(l)
    out = set()
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, rl, ll, autojunk=False).get_opcodes():
        if tag in ("insert", "replace"):
            out.update(x for x in ll[j1:j2] if not STAMP_RE.match(x))
    return out


def unadmitted_spans(rl, kept_levels):
    """Indices of ref lines inside a CPU `#if` block that defines a level
    helper the lane does not render (`__wNN(` not in kept_levels)."""
    drop = set()
    i = 0
    while i < len(rl):
        if CPU_PP.match(rl[i]) and rl[i].lstrip().startswith(b"#if"):
            depth, j = 1, i + 1
            while j < len(rl) and depth:
                if rl[j].lstrip().startswith(b"#if"):
                    depth += 1
                elif rl[j].lstrip().startswith(b"#endif"):
                    depth -= 1
                j += 1
            body = b"".join(rl[i:j])
            # the block's level is the helper it DEFINES (its body also calls
            # the next level down, its fall-through)
            levels = set(re.findall(rb"^static[^\n(]*__(w\d+)\(", body, re.M))
            if levels and not (levels & kept_levels):
                drop.update(range(i, j))
            i = j
        else:
            i += 1
    return drop


def judge(mode, r, l, fixed):
    """None if the difference is the declared one, else the reason."""
    r = renumber(r)
    if mode == "default":
        rl, ll = lines(r), lines(l)
        add = [x for x in ll if x not in rl]
        if any(not re.match(rb'^#define \w+_TARGETS "none:generic"\n$', x) for x in add) or len(add) != 1:
            return "default: unpredicted added lines %r" % add[:3]
        if [x for x in ll if not re.match(rb"^#define \w+_TARGETS ", x)] != rl:
            return "default: the texts differ beyond the TARGETS line"
        return None
    fr, fl = FORMS_RE.search(r), FORMS_RE.search(l)
    if not (fr and fl):
        return "simd: a side has no MEMFN_FORMS"
    rforms, lforms = fr.group(1), fl.group(1)
    kept = set(re.findall(rb"(w\d+)", lforms))
    want = []
    for tok in rforms.split(b","):
        if b"@" in tok:
            f, lv = tok.split(b"@", 1)
            keep = [x for x in lv.split(b"+") if x in kept]
            want.append(f + b"@" + b"+".join(keep) if keep else None)
        else:
            want.append(tok)
    want = b",".join(x for x in want if x) or b"none"
    if lforms != want:
        return "simd: MEMFN_FORMS %r, predicted %r from the ref's %r" % (lforms, want, rforms)
    rl, ll = lines(r), lines(l)
    drop_ok = unadmitted_spans(rl, kept)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, rl, ll, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        for j in range(j1, j2):
            x = ll[j]
            if not (STAMP_RE.match(x) or x in fixed):
                return "simd: unpredicted lane line %r" % x[:120]
        for i in range(i1, i2):
            x = rl[i]
            if (i in drop_ok or STAMP_RE.match(x) or CPU_PP.match(x) or PP_ELSE_END.match(x)
                    or not x.strip() or re.match(rb"^\s*return \w+__body\(", x)):
                continue
            arm = re.match(rb"^\s*return \w+__(w\d+)\(", x)   # a selector arm of an unadmitted level
            if arm and arm.group(1) not in kept:
                continue
            return "simd: unpredicted ref line removed %r" % x[:120]
    return None


def main():
    a = sys.argv[1:]
    jobs, limit = 8, 0
    if "--jobs" in a:
        k = a.index("--jobs"); jobs = int(a[k + 1]); del a[k:k + 2]
    if "--limit" in a:
        k = a.index("--limit"); limit = int(a[k + 1]); del a[k:k + 2]
    ref, lane, tree, target = a
    pats = sorted({p for _, _, p in es.enumerate_corpus(lane, tree, 30)})
    if limit:
        pats = pats[:limit]
    print("u3tgt movers: %d distinct patterns, target %s" % (len(pats), target))
    cells = [(m, enc, eng) for m in ("default", "simd") for enc in ("byte", "utf8") for eng in (None, "vm")]
    fixed = {}
    for enc in ("byte", "utf8"):
        base = ["-e", "utf8"] if enc == "utf8" else []
        fixed[enc] = fixed_lines(ref, lane, base + ["-fmemfn-simd=" + target])
    stats = {c: [0, 0, []] for c in cells}

    def job(p):
        out = []
        for c in cells:
            m, enc, eng = c
            extra = (["-e", "utf8"] if enc == "utf8" else []) + (["-fmemfn-simd=" + target] if m == "simd" else [])
            okr, r = es.compile_stream_c(ref, p, 30, engine=eng, extra=extra)[:2]
            okl, l = es.compile_stream_c(lane, p, 30, engine=eng, extra=extra)[:2]
            if okr != okl:
                out.append((c, True, "refused on one side (ref %s, lane %s)" % (okr, okl)))
            elif not okr:
                out.append((c, False, None))
            else:
                fr = FORMS_RE.search(r)
                served = bool(fr) and fr.group(1) != b"none"
                why = judge(m, r, l, fixed[enc])
                # THE CONTROL, per compiled cell: the same judge must REJECT
                # the lane text with one planted line, so it cannot pass blind
                planted = l.replace(b"\n", b"\nint u3tgt_plant;\n", 1)
                if not why and judge(m, r, planted, fixed[enc]) is None:
                    why = "CONTROL: the judge accepted a planted line"
                out.append((c, served, why))
        return p, out

    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        for p, out in ex.map(job, pats):
            for c, moved, why in out:
                s = stats[c]
                s[0] += 1
                if why:
                    s[2].append((p, why))
                s[1] += moved
    bad = 0
    for c in cells:
        n, mv, fails = stats[c]
        print("cell %-7s %-4s %-7s patterns %d kit-SIMD-served %d unpredicted %d"
              % (c[0], c[1], c[2] or "default", n, mv, len(fails)))
        for p, why in fails[:5]:
            print("  UNPREDICTED %r: %s" % (p, why))
        bad += len(fails)
    print("== u3tgt movers COMPLETE: unpredicted %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
