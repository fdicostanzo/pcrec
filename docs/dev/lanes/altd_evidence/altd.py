#!/usr/bin/env python3
"""altd.py -- lane altd's HAND-TWIN GENERATOR for candidate D (scratch, not a product).

Reads an emitted VM artifact (gcc-dialect C from pcrec; stock D183 or a vmbc
B+C twin) plus the same pattern's --emit-ir listing (for the ROLE of each push
site), and rewrites every selected CHOICE POINT -- a block ending in
`RX_PUSH(&&R, scan_position); goto B;` -- into a FIRST-BYTE DISPATCH:

  continuations  an alternation chain is flattened to its arms [B0, B1, .., Bk]
                 (resume labels that are themselves `PUSH(&&R'); goto B'` and
                 referenced once); a 2-way choice point is [B, R].
  FIRST+(c)      a superset of the bytes the first consumed byte can be when
                 continuation c succeeds, plus EOS (c may succeed with no byte
                 left / without consuming), read off the emitted TEXT by a
                 flow walk (pushes fork, non-consuming conditional gotos fork,
                 a consuming test contributes its class and the walk continues
                 on its fail path, a span loop contributes its class and is
                 skipped as if it ran zero times, anything unrecognised = ALL).
  dispatch       bytes are partitioned by the candidate tuple (the ordered
                 subsequence of continuations whose FIRST+ holds the byte);
                 each class gets its own chain: PUSH only between candidates,
                 in the ORIGINAL order; one candidate = no push; none = fail.

Modes: -m A (alternation chains only), -m AL (also the 2-way loop / optional
choice points), -m none (parse + stats only).
Usage: altd.py -m MODE IN.c IN.ir OUT.c      (stats on stderr)
Needs: gcc, and -I paths for rx.h's includes in $ALTD_CFLAGS (mask evaluation
compiles a copy of IN.c with an appended main, so class helpers are in scope).
"""
import os
import re
import subprocess
import sys
import tempfile

LABEL = re.compile(r"^(rx_\w+): __attribute__\(\(unused\)\);\s*$")
ALLB = (1 << 256) - 1

BRANCH_ROLES = ("branch ",)
LOOP_ROLES = ("the loop's ONLY frame", "another iteration preferred", "body preferred")


def strip_chars(s):
    return re.sub(r"'(\\.|[^'\\])'", "0", s)


def group_statements(lines):
    """Group raw lines into statements: a statement ends when parens and braces
    balance and the text ends with ';' or '}' (or is a comment line)."""
    out, cur, depth_b, depth_p = [], [], 0, 0
    for ln in lines:
        st = ln.strip()
        if not cur and (st == "" or (st.startswith("/*") and st.endswith("*/"))):
            if st:
                out.append(st)
            continue
        cur.append(ln)
        t = strip_chars(re.sub(r"/\*.*?\*/", "", ln))
        depth_b += t.count("{") - t.count("}")
        depth_p += t.count("(") - t.count(")")
        if depth_b == 0 and depth_p == 0 and (st.endswith(";") or st.endswith("}")):
            out.append("\n".join(cur))
            cur = []
    if cur:
        out.append("\n".join(cur))
    return out


def parse(text):
    lines = text.split("\n")
    labels = []  # (name, line index)
    for i, ln in enumerate(lines):
        m = LABEL.match(ln)
        if m:
            labels.append((m.group(1), i))
    names = [n for n, _ in labels]
    if len(set(names)) != len(names):
        raise SystemExit("refused: repeated label names (more than one matcher body in the file)")
    blocks = {}
    for j, (name, i) in enumerate(labels):
        end = labels[j + 1][1] if j + 1 < len(labels) else len(lines)
        if name == "rx_fail":
            end = i + 1
        blocks[name] = (i, end, group_statements(lines[i + 1:end]))
    return lines, labels, blocks


def split_and(expr):
    """Top-level && conjuncts of expr."""
    parts, depth, cur, i = [], 0, "", 0
    while i < len(expr):
        c = expr[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        if depth == 0 and expr.startswith("&&", i):
            parts.append(cur.strip())
            cur = ""
            i += 2
            continue
        cur += c
        i += 1
    parts.append(cur.strip())
    return parts


def first_byte_expr(conds, var):
    """AND of the conjuncts that read only subject[var] / subject[var + 0]
    (normalised to subject[scan_position]); others dropped (a superset)."""
    keep = []
    for c in conds:
        subs = re.findall(r"subject\[([^\]]+)\]", c)
        if not subs:
            continue
        if all(re.fullmatch(r"\s*%s(\s*\+\s*0)?\s*" % var, s) for s in subs):
            keep.append(re.sub(r"subject\[\s*%s(\s*\+\s*0)?\s*\]" % var, "subject[scan_position]", c))
    if not keep:
        return None
    return " && ".join("(%s)" % k for k in keep)


class Walker:
    def __init__(self, blocks, rets=None):
        self.blocks = blocks
        self.rets = rets
        self.exprs = {}       # expr text -> id
        self.unknown = {}

    def eid(self, e):
        if e not in self.exprs:
            self.exprs[e] = len(self.exprs)
        return self.exprs[e]

    def first(self, label):
        """-> (set of expr ids, set of literal bytes, all_flag, eos_flag)"""
        ex, lits = set(), set()
        allf = eos = False
        work, seen = [(label, 0)], set()
        while work:
            lab, k = work.pop()
            if (lab, k) in seen:
                continue
            seen.add((lab, k))
            if lab == "rx_fail":
                continue
            if lab == "rx_accept" or lab not in self.blocks:
                allf = eos = True
                continue
            stmts = self.blocks[lab][2]
            while k < len(stmts):
                s = stmts[k].strip()
                k += 1
                one = " ".join(x.strip() for x in s.split("\n"))
                if s.startswith("/*"):
                    continue
                if re.match(r"RX_CUT\(", s):
                    # COMMIT-OPACITY: a cut discards frames (perhaps the very frame this
                    # dispatch would push for the next candidate), so a continuation that
                    # can reach a cut before its first consumed byte is never dropped
                    self.unknown["RX_CUT (commit-opaque)"] = self.unknown.get("RX_CUT (commit-opaque)", 0) + 1
                    allf = eos = True
                    break
                if re.match(r"(RX_SET|RX_SETU|RX_CHARGE_WORK|RX_TRAIL_CHECK|RX_TIER_NOTE|RX_CALL)\(", s):
                    continue
                if one in ("rx_span_cursor = scan_position;", "scan_position = rx_span_cursor;") or \
                        re.fullmatch(r"rx_span_cursor -= \d+;", one):
                    continue
                m = re.fullmatch(r"RX_PUSH\(&&(rx_\w+), [^;]*\);", one)
                if m:
                    work.append((m.group(1), 0))
                    continue
                m = re.fullmatch(r"if \(scan_position < subject_length && (.*)\) \{ scan_position\+\+; goto (rx_\w+); \}", one)
                if m:
                    e = first_byte_expr(split_and(m.group(1)), "scan_position")
                    if e is None:
                        allf = True
                    else:
                        ex.add(self.eid(e))
                    continue
                m = re.fullmatch(r"if \(scan_position \+ 0 < subject_length && subject\[scan_position \+ 0\] == (\d+)\) goto (rx_\w+);", one)
                if m:
                    lits.add(int(m.group(1)))
                    continue
                m = re.fullmatch(r"if \(\(ptrdiff_t\)rx_span_cursor < (.*) \+ (\d+)\) goto rx_fail;", one)
                if m and int(m.group(2)) >= 1:
                    break         # zero-iteration model: a span with a minimum >= 1 fails here
                m = re.fullmatch(r"if \((.*)\) goto (rx_\w+);", one)
                if m and "subject[" not in m.group(1) and "=" not in m.group(1).replace("==", "").replace("<=", "").replace(">=", "").replace("!=", ""):
                    work.append((m.group(2), 0))
                    continue
                if one.startswith("if (scan_position + 0 < subject_length) switch (subject[scan_position + 0]) {"):
                    for b in re.findall(r"case (\d+): goto rx_\w+;", one):
                        lits.add(int(b))
                    continue
                if one.startswith("{") and "while (" in one and "goto" not in one and "return" not in one:
                    w = re.search(r"while \((.*)\) \{", one)
                    e = first_byte_expr(split_and(w.group(1)), "rx_span_cursor") if w else None
                    if e is None:
                        allf = True
                    else:
                        ex.add(self.eid(e))
                    continue      # zero iterations: fall through (superset)
                m = re.fullmatch(r"goto (rx_\w+);", one)
                if m:
                    work.append((m.group(1), 0))
                    break
                if self.rets is not None and "goto *run->resume_stack[rx_call_frame].call_ret;" in one:
                    for r in self.rets:      # FOLLOW: any return lands on some call's return label (superset)
                        work.append((r, 0))
                    break
                # region exit, return, anything else: refuse to reason
                self.unknown[one[:60]] = self.unknown.get(one[:60], 0) + 1
                allf = eos = True
                break
            else:
                # fell off a block end (fallthrough into the next label): not expected
                allf = eos = True
        return ex, lits, allf, eos


def eval_masks(src_c, exprs, cflags):
    if not exprs:
        return {}
    d = tempfile.mkdtemp(prefix="altd_", dir=os.environ.get("ALTD_TMP", "/var/tmp/pcrec-pcrec/scratch/altd/tmp"))
    body = ["\n#include <stdio.h>\nint main(void){ unsigned char buf[4]={0,0,0,0}; const unsigned char *subject=buf; size_t scan_position=0; (void)subject; (void)scan_position;"]
    for e, i in exprs.items():
        body.append(' printf("%d ", %d); for (int c=0;c<256;c++){ buf[0]=(unsigned char)c; putchar((%s) ? \'1\' : \'0\'); } putchar(\'\\n\');' % (i, i, e))
    body.append(" return 0; }\n")
    open(os.path.join(d, "ev.c"), "w").write(src_c + "".join(body))
    r = subprocess.run(["gcc", "-O0", "-w", "-std=gnu11"] + cflags + ["-o", os.path.join(d, "ev"), os.path.join(d, "ev.c")],
                       capture_output=True, text=True)
    if r.returncode:
        sys.stderr.write(r.stderr[:2000])
        raise SystemExit("mask evaluation failed to compile")
    out = subprocess.run([os.path.join(d, "ev")], capture_output=True, text=True, check=True).stdout
    masks = {}
    for ln in out.split("\n"):
        if not ln.strip():
            continue
        i, bits = ln.split()
        masks[int(i)] = sum(1 << c for c in range(256) if bits[c] == "1")
    return masks


def ranges(bs):
    bs = sorted(bs)
    out, s = [], None
    for b in bs:
        if s is None:
            s = p = b
        elif b == p + 1:
            p = b
        else:
            out.append((s, p))
            s = p = b
    if s is not None:
        out.append((s, p))
    return out


def main(argv):
    mode = argv[argv.index("-m") + 1]
    rest = [a for a in argv[1:] if a not in ("-m", mode)]
    inc, inir, outc = rest
    text = open(inc).read()
    cflags = os.environ.get("ALTD_CFLAGS", "").split()
    lines, labels, blocks = parse(text)

    # push sites in program order, zipped with the listing's roles
    csites = [(m.group(1), m.group(2)) for m in re.finditer(r"RX_PUSH\(&&(rx_\w+), ([^)]*)\);", text)]
    noir = inir == "-"
    roles = ["branch (structural)"] * len(csites) if noir else \
        [ln.split("\t")[4] if len(ln.split("\t")) > 4 else "" for ln in open(inir) if ln.split("\t")[1:2] == ["push"]]
    if len(csites) != len(roles):
        raise SystemExit("push sites %d != listing pushes %d" % (len(csites), len(roles)))
    role_of = {}
    for (tgt, pos), role in zip(csites, roles):
        role_of[tgt] = role

    def refs(lab):
        return len(re.findall(r"\b%s\b" % lab, text)) - 1

    want = BRANCH_ROLES + (LOOP_ROLES if mode == "AL" else ())
    rets = sorted(set(re.findall(r"RX_CALL\(&&(rx_\w+), ", text))) if os.environ.get("ALTD_FOLLOW") == "1" else None
    W = Walker(blocks, rets)
    sites = []
    interior = set()
    for name, li in labels:
        st = [s for s in blocks[name][2] if not s.strip().startswith("/*")]
        if len(st) < 2:
            continue
        m1 = re.fullmatch(r"RX_PUSH\(&&(rx_\w+), scan_position\);", st[-2].strip())
        m2 = re.fullmatch(r"goto (rx_\w+);", st[-1].strip())
        if not (m1 and m2):
            continue
        r = m1.group(1)
        if not role_of.get(r, "").startswith(want):
            continue
        if name in interior:
            continue
        conts = [m2.group(1)]
        chainlabs = []
        while True:
            rs = [s for s in blocks.get(r, (0, 0, []))[2] if not s.strip().startswith("/*")]
            mm1 = len(rs) == 2 and re.fullmatch(r"RX_PUSH\(&&(rx_\w+), scan_position\);", rs[0].strip())
            mm2 = len(rs) == 2 and re.fullmatch(r"goto (rx_\w+);", rs[1].strip())
            if role_of.get(r, "").startswith("branch ") and mm1 and mm2 and refs(r) == 1:
                interior.add(r)
                chainlabs.append(r)
                conts.append(mm2.group(1))
                r = mm1.group(1)
                continue
            if role_of.get(r, "").startswith("branch ") and len(rs) == 1 and re.fullmatch(r"goto (rx_\w+);", rs[0].strip()) and refs(r) == 1:
                interior.add(r)
                conts.append(re.fullmatch(r"goto (rx_\w+);", rs[0].strip()).group(1))
            else:
                conts.append(r)
            break
        sites.append((name, role_of.get(m1.group(1)), conts))

    firsts = {}
    for _, _, conts in sites:
        for c in conts:
            if c not in firsts:
                firsts[c] = W.first(c)
    masks = eval_masks(text, W.exprs, cflags)

    def mask_of(c):
        ex, lits, allf, eos = firsts[c]
        if allf:
            return ALLB, True
        m = 0
        for e in ex:
            m |= masks[e]
        for b in lits:
            m |= 1 << b
        return m, eos

    # emit
    insert = {}   # label -> replacement block text (statements after the label line)
    stats = dict(sites=0, rewritten=0, pushes_static_before=0, pushes_static_after=0, classes=0)
    report = []
    n = 0
    for name, role, conts in sites:
        stats["sites"] += 1
        ms = [mask_of(c) for c in conts]
        classes = {}
        for b in range(256):
            tup = tuple(j for j, (m, _) in enumerate(ms) if (m >> b) & 1)
            classes.setdefault(tup, []).append(b)
        eos_t = tuple(j for j, (_, e) in enumerate(ms) if e)
        full = tuple(range(len(conts)))
        if list(classes.keys()) == [full] and eos_t == full:
            report.append("%s keep (%d conts, no byte drops one)" % (name, len(conts)))
            continue
        rule = os.environ.get("ALTD_RULE")
        is_loop = (role or "").startswith(("the loop's ONLY frame", "another iteration preferred"))
        if (rule == "pref" or (rule == "kind" and is_loop)) and not any(
                t and t[0] == 0 and t != full for t in classes):
            # PREFERRED-PATH rule: some byte the preferred continuation can start
            # with must lose a candidate, else every entry pays the switch for nothing
            report.append("%s decline (%d conts, preferred path unchanged) classes[%s]" % (
                name, len(conts), ", ".join("%s:%d" % (",".join(str(j + 1) for j in t) or "-", len(bs)) for t, bs in classes.items())))
            continue
        n += 1
        stats["rewritten"] += 1
        stats["classes"] += len(classes)
        p = "rx_D%d" % n
        st = blocks[name][2]
        nonc = [i for i, s in enumerate(st) if not s.strip().startswith("/*")]
        keep = st[:nonc[-2]]
        out = list(keep)
        out.append("    if (scan_position >= subject_length) goto %s_eos;" % p)
        out.append("    switch (subject[scan_position]) {")
        cls = sorted(classes.items(), key=lambda kv: -len(kv[1]))
        dflt = cls[0][0]
        idx = {t: i for i, (t, _) in enumerate(cls)}
        for t, bs in cls[1:]:
            for lo, hi in ranges(bs):
                out.append("    case %d%s: goto %s_c%d;" % (lo, "" if lo == hi else " ... %d" % hi, p, idx[t]))
        out.append("    default: goto %s_c%d;" % (p, idx[dflt]))
        out.append("    }")
        chains = [(t, "%s_c%d" % (p, idx[t])) for t, _ in cls] + [(eos_t, "%s_eos" % p)]
        # numeric labels (rx_L<n>), so line-graph checkers that know only that shape read the twin
        lab_no = {}

        def L(sym):
            if sym not in lab_no:
                lab_no[sym] = "rx_L%d" % (900000 + 1000 * n + len(lab_no))
            return lab_no[sym]
        for t, lab in chains:
            out.append("%s: __attribute__((unused));" % L(lab))
            if not t:
                out.append("    goto rx_fail;")
                continue
            for j, a in enumerate(t):
                if j:
                    out.append("%s: __attribute__((unused));" % L("%s_%d" % (lab, j)))
                if j + 1 < len(t):
                    out.append("    RX_PUSH(&&%s, scan_position);" % L("%s_%d" % (lab, j + 1)))
                out.append("    goto %s;" % conts[a])
        out = [ln if not ln.startswith("    if (scan_position >= subject_length) goto ") else
               "    if (scan_position >= subject_length) goto %s;" % L("%s_eos" % p) for ln in out]
        out = [re.sub(r"goto (rx_D\d+_c\d+);", lambda m: "goto %s;" % L(m.group(1)), ln) for ln in out]
        insert[name] = out
        desc = ", ".join("%s:%s" % (",".join(str(j + 1) for j in t) or "-", len(bs)) for t, bs in cls)
        report.append("%s %s (%d conts) classes[%s] eos:%s" % (name, (role or "")[:24], len(conts), desc, ",".join(str(j + 1) for j in eos_t) or "-"))

    res = []
    i = 0
    starts = {li: name for name, li in labels}
    while i < len(lines):
        if i in starts and starts[i] in insert:
            name = starts[i]
            res.append(lines[i])
            res.extend(insert[name])
            i = blocks[name][1]
            continue
        res.append(lines[i])
        i += 1
    open(outc, "w").write("\n".join(res))
    for r in report:
        sys.stderr.write("  " + r + "\n")
    if W.unknown:
        sys.stderr.write("  ALL-by-refusal statements: %s\n" % "; ".join("%s x%d" % kv for kv in sorted(W.unknown.items(), key=lambda kv: -kv[1])[:6]))
    sys.stderr.write("altd: mode=%s sites=%d rewritten=%d classes=%d\n" % (mode, stats["sites"], stats["rewritten"], stats["classes"]))


if __name__ == "__main__":
    main(sys.argv)
