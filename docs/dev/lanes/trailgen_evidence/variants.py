#!/usr/bin/env python3
"""variants.py MODE IN.c OUT.c -- lane trailgen's trail-structure TWINS (scratch, not a product).

Text rewrites of an emitted VM artifact (prefix rx/RX, lane/trailgc D183 base):

  cnt      counters: trail entries written, frames pushed, entries restored by
           the unwind (destructor prints `tg trail=.. push=.. undo=..`)
  notrail  RX_SET writes the slot and no trail entry (an UPPER BOUND on the
           trail's cost; not a correct matcher in general)
  R        REGISTER-RESIDENT RUN CURSORS: trail/resume depth, their bases and
           caps, call_top, steps_left, work_left become matcher locals, loaded
           at entry and written back at every return and around the cold
           compaction call. Answer-identical by construction (same values,
           same order of every observable store).
  P        PACKED 8-byte trail entry: (value << 16) | slot in one uint64
           (slot < 65536, |value| < 2^47); the compaction compares slots by
           the low 16 bits.
  RP       R and P together.
Combine with cnt by MODE+cnt (e.g. R+cnt). Bails (exit 3) on anything unexpected.
"""
import re
import sys


class Bail(Exception):
    pass


def matcher_span(t):
    m = re.search(r"^static [^\n]*\bptrdiff_t rx_match_anchored\(", t, re.M)
    if not m:
        raise Bail("no matcher")
    end = t.index("\n}\n", m.start()) + 3
    return m.start(), end


def macro_span(t, name):
    m = re.search(r"^#define %s" % re.escape(name), t, re.M)
    if not m:
        return None
    e = m.start()
    while True:
        nl = t.index("\n", e)
        if t[nl - 1] != "\\":
            return m.start(), nl + 1
        e = nl + 1


# (field, local, declaration type, written back at exits)
ALLF = [("trail_depth", "tg_td", "size_t", True), ("resume_depth", "tg_rd", "size_t", True),
        ("call_top", "tg_ct", "size_t", True), ("steps_left", "tg_sl", "long long", True),
        ("work_left", "tg_wl", "long long", True), ("trail_cap", "tg_tcap", "const size_t", False),
        ("resume_cap", "tg_rcap", "const size_t", False),
        ("resume_stack", "tg_fb", "rx_frame *const", False), ("trail", "tg_tb", "rx_trail_entry *const", False)]


def run_fields(t):
    m = re.search(r"typedef struct \{(.*?)\} rx_run_state;", t, re.S)
    if not m:
        raise Bail("no rx_run_state")
    body = m.group(1)
    return [f for f in ALLF if re.search(r"\b%s\b" % f[0], body)]


def subst_fields(s, fl):
    sync = " ".join("run->%s = %s;" % (f, l) for f, l, _, w in fl if w)
    for f, l, _, _ in fl:
        s = re.sub(r"run->%s\b(?!\s*=[^=])" % f if False else r"run->%s\b" % f, l, s)
    s = re.sub(r"\breturn ([^;\n]+);", r"{ " + sync + r" return \1; }", s)
    return s


def mode_R(t):
    fl = run_fields(t)
    a, b = matcher_span(t)
    body = t[a:b]
    if re.search(r"[(,]\s*run\s*[,)]", re.sub(r"rx_trail_compact\(run\)", "", body)):
        raise Bail("matcher passes run to a call")
    head = t[:a]
    names = ["RX_TRAIL", "RX_SET", "RX_PUSH", "RX_CUT", "RX_CALL", "RX_CHARGE_WORK", "RX_TRAIL_CHECK"]
    spans = []
    for nm in names:
        sp = macro_span(head, nm + "(")
        if sp:
            spans.append(sp)
    out = head
    hasrd = any(f == "resume_depth" for f, *_ in fl)
    for s, e in sorted(spans, reverse=True):
        seg = out[s:e]
        if seg.startswith("#define RX_TRAIL_CHECK("):
            seg = ("#define RX_TRAIL_CHECK() do {                              \\\n"
                   "        if (tg_td > rx_trail_gc_at) {                       \\\n"
                   "            run->trail_depth = tg_td; %s \\\n"
                   "            rx_trail_gc_at = rx_trail_compact(run);             \\\n"
                   "            tg_td = run->trail_depth; }                         \\\n"
                   "    } while (0)\n") % ("run->resume_depth = tg_rd;" if hasrd else "")
        else:
            seg = subst_fields(seg, fl)
        out = out[:s] + seg + out[e:]
    anchor = "    ptrdiff_t *const slot_values = run->slot_values;\n"
    if anchor not in body:
        raise Bail("no slot_values anchor")
    pre, post = body.split(anchor, 1)
    post = subst_fields(post, fl)
    loc = anchor + "".join("    %s %s = run->%s; (void)%s;\n" % (ty, l, f, l) for f, l, ty, _ in fl)
    left = set(re.findall(r"run->\w+", post)) - {"run->%s" % f for f, _, _, w in fl if w} - {"run->slot_values"}
    if left:
        raise Bail("unhandled run field in matcher: %s" % sorted(left))
    return out + pre + loc + post + t[b:]


def accessor(t, field, mac):
    out = []
    i = 0
    while True:
        j = t.find(field, i)
        if j < 0:
            out.append(t[i:]); break
        # walk back over the postfix expression ending at j
        k = j
        while True:
            if t[k - 1] == "]":
                depth = 0; k -= 1
                while True:
                    if t[k] == "]": depth += 1
                    elif t[k] == "[":
                        depth -= 1
                        if depth == 0: break
                    k -= 1
            elif re.match(r"\w", t[k - 1]):
                while re.match(r"\w", t[k - 1]): k -= 1
            elif t[k - 2:k] == "->":
                k -= 2; continue
            else:
                break
            if t[k - 2:k] == "->" or t[k - 1] == "]" :
                continue
            if re.match(r"\w", t[k - 1]):
                continue
            break
        if k < i:
            raise Bail("overlapping accessor")
        out.append(t[i:k]); out.append("%s(%s)" % (mac, t[k:j])); i = j + len(field)
    return "".join(out)


def mode_P(t):
    # entry type
    t2 = t.replace("typedef struct { unsigned slot_index; ptrdiff_t saved_value; } rx_trail_entry;",
                   "typedef struct { unsigned long long w; } rx_trail_entry;")
    if t2 == t:
        raise Bail("no trail entry typedef")
    t = t2
    t = re.sub(r"#define RX_TRAIL_FRAME_SIZE \d+", "#define RX_TRAIL_FRAME_SIZE 8", t)
    hdr_fix = True
    # writes: X.slot_index = (unsigned)(slot_); X.saved_value = slot_values[(slot_)];
    t = re.sub(r"(\S+)\.slot_index = \(unsigned\)\(slot_\);(\s*\\\n\s*)\1\.saved_value = slot_values\[\(slot_\)\];",
               r"\1.w = ((unsigned long long)slot_values[(slot_)] << 16) | (unsigned)(slot_);\2(void)0;", t)
    t = accessor(t, ".saved_value", "TG_VAL")
    t = accessor(t, ".slot_index", "TG_SLOT")
    m = re.search(r"^typedef struct \{ unsigned long long w; \} rx_trail_entry;\n", t, re.M)
    t = t[:m.end()] + ("#define TG_VAL(e) ((ptrdiff_t)((long long)(e).w >> 16))\n"
                       "#define TG_SLOT(e) ((unsigned)((e).w & 0xffffu))\n") + t[m.end():]
    if "slot_index" in t or "saved_value" in t:
        left = sorted(set(l.strip()[:120] for l in t.split("\n") if "slot_index" in l or "saved_value" in l))
        raise Bail("unhandled trail field use: %s" % left[:4])
    return t


def mode_cnt(t):
    a, _ = matcher_span(t)
    decl = ("static unsigned long long tg_nt, tg_np, tg_nu;\n#include <stdio.h>\n"
            "__attribute__((destructor)) static void tg_rep(void){ fprintf(stderr, \"tg trail=%llu push=%llu undo=%llu\\n\", tg_nt, tg_np, tg_nu); }\n")
    t = t[:a] + t[a:]
    m = re.search(r"^#define RX_TRAIL\(", t, re.M)
    if not m:
        raise Bail("no RX_TRAIL")
    t = t[:m.start()] + decl + t[m.start():]
    t = re.sub(r"((?:run->trail_depth|tg_td)\+\+;)", r"\1 tg_nt++;", t, count=1)
    t = re.sub(r"((?:run->resume_depth|tg_rd)\+\+;)", r"\1 tg_np++;", t)
    # the unwind at fail: the while loop's decrement inside the matcher
    a, b = matcher_span(t)
    body = t[a:b]
    body2 = re.sub(r"(while \((?:run->trail_depth|tg_td) > [^)]*\) \{\n\s*(?:run->trail_depth|tg_td)--;)", r"\1 tg_nu++;", body)
    return t[:a] + body2 + t[b:]


def mode_notrail(t):
    sp = macro_span(t, "RX_SET(")
    if not sp:
        raise Bail("no RX_SET")
    s, e = sp
    return t[:s] + "#define RX_SET(slot_, v_) do { slot_values[(slot_)] = (v_); } while (0)\n" + t[e:]


def main():
    mode, src, dst = sys.argv[1:4]
    t = open(src).read()
    try:
        for m in mode.split("+"):
            if m == "R":
                t = mode_R(t)
            elif m == "P":
                t = mode_P(t)
            elif m == "RP":
                t = mode_P(mode_R(t))
            elif m == "cnt":
                t = mode_cnt(t)
            elif m == "notrail":
                t = mode_notrail(t)
            elif m == "stock":
                pass
            else:
                raise Bail("unknown mode " + m)
    except Bail as e:
        sys.stderr.write("variants %s %s BAIL %s\n" % (mode, src, e))
        sys.exit(3)
    open(dst, "w").write(t)


main()
