#!/usr/bin/env python3
"""p910 P10 twins: hand edits of pcrec's own auto artifacts (scratch only).

Input: DIR/rx.c, an auto artifact whose search route is ONE direct-threaded DFA
attempt (`DFA_SCAN "attempt"`, `REQ_WHY "one-attempt"`): either the DFA
engine's `rx_search` or a VM hybrid's `rx_prefilter`. Writes
  DIR-pre/    the presence check G2 declines, taken at the attempt's entry
              (what the forced VM does): memchr(req) over [start, n)
  DIR-paced/  the same check taken only at a CHECKPOINT: once the attempt has
              read D = max(D0, (n - start) / R) bytes and is still alive.
              Every state's existing end-of-subject test reads `lim` instead
              of `subject_length`; at lim < n the check runs once, lim
              becomes n, and the attempt resumes in the SAME state.
R and D0 are compile-time -D values (P10_R, P10_D0) so one source serves the
sweep. A failed check returns 0 (no match): every match contains the byte.
"""
import os, re, sys

src_dir = sys.argv[1]
src = open(os.path.join(src_dir, "rx.c")).read()
req = re.search(r'^#define RX_REQ_BYTE "(\d+)"', src, re.M).group(1)

# the one function holding the attempt
m = re.search(r'^(int rx_search|static int rx_prefilter)\(', src, re.M)
fs = m.start()
fe = src.index("\n}\n", fs) + 3
fn = src[fs:fe]
assert "goto *((start == 0)" in fn, "not a one-attempt direct-threaded route"
assert "const size_t start_max = 0" in fn

anchor = "        size_t last_accept_position = (size_t)-1;\n"
assert fn.count(anchor) == 1


def build(mode):
    f = fn
    if mode == "pre":
        f = f.replace(anchor, anchor +
                      f"        if (!memchr(subject + start, {req}, subject_length - start)) return 0;\n")
        return f
    f = f.replace(anchor, anchor +
                  "        size_t p10_d = (subject_length - start) >> P10_SHIFT;\n"
                  "        if (p10_d < P10_D0) p10_d = P10_D0;\n"
                  "        const size_t p10_n = subject_length;   /* the real end, read only on the cold path */\n"
                  "        if (subject_length - start > p10_d) subject_length = start + p10_d;   /* the hot bound IS the checkpoint */\n")
    out, pos, n = [], 0, 0
    for lm in re.finditer(r'^(rx_s\d+): __attribute__\(\(unused\)\);\n', f, re.M):
        lab = lm.group(1)
        # the state's own bound test, the first one after its label
        t = "if (scan_position >= subject_length) goto rx_done;"
        i = f.index(t, lm.end())
        nxt = re.compile(r'^rx_s\d+: ', re.M).search(f, lm.end())
        if nxt and i > nxt.start():
            continue
        out.append(f[pos:i])
        out.append("if (scan_position >= subject_length) { if (subject_length < p10_n) { "
                   "if (!p10_present(subject + start, p10_n - start)) return 0; "
                   f"subject_length = p10_n; goto {lab}; }} goto rx_done; }}")
        pos = i + len(t)
        n += 1
    out.append(f[pos:])
    print(src_dir, "paced: states patched", n, file=sys.stderr)
    body = "".join(out)
    # every OTHER read of the end (the EOL views inside states) keeps the real end
    ev = "scan_position == subject_length || (scan_position + 1 == subject_length"
    k = body.count(ev)
    body = body.replace(ev, "scan_position == p10_n || (scan_position + 1 == p10_n")
    print(src_dir, "paced: eol views kept on the real end", k, file=sys.stderr)
    return body


for mode in ("pre", "paced"):
    od = src_dir.rstrip("/") + "-" + mode
    os.makedirs(od, exist_ok=True)
    body = build(mode)
    pre = "#ifndef P10_SHIFT\n#define P10_SHIFT 6\n#endif\n#ifndef P10_D0\n#define P10_D0 16\n#endif\n#include <string.h>\n" + f"static __attribute__((noinline, cold)) int p10_present(const unsigned char *p, size_t k) {{ return memchr(p, {req}, k) != 0; }}\n"
    open(os.path.join(od, "rx.c"), "w").write(pre + src[:fs] + body + src[fe:])
    for h in os.listdir(src_dir):
        if h.endswith(".h"):
            open(os.path.join(od, h), "w").write(open(os.path.join(src_dir, h)).read())


# ---- paced2: the hot function holds NO call. At the checkpoint it RETURNS
# (code 2) with its state, position and last accept; the wrapper runs the
# presence check and RE-ENTERS the same function in that state with the real
# end. The resume entry is one indirect jump through a label table.
def build_paced2():
    f = fn
    m2 = re.match(r'(int rx_search|static int rx_prefilter)\((.*)\)[ \t]*(?=\n)', f)
    name = m2.group(1).split()[-1]
    params = m2.group(2)
    labels = re.findall(r'^(rx_s\d+): __attribute__\(\(unused\)\);\n', f, re.M)
    core_sig = (f"static __attribute__((noinline)) int {name}_p10core({params}, size_t p10_n, int p10_rs, "
                "size_t p10_rpos, size_t p10_racc, int *p10_st, size_t *p10_pos, size_t *p10_acc)")
    f = f[:m2.start()] + core_sig + f[m2.end():]
    lab_tab = "        static const void *const p10_labels[] = { " + ", ".join("&&" + l for l in labels) + " };\n"
    f = f.replace(anchor, anchor + lab_tab +
                  "        if (p10_rs >= 0) { scan_position = p10_rpos; last_accept_position = p10_racc; goto *p10_labels[p10_rs]; }\n")
    out, pos = [], 0
    t = "if (scan_position >= subject_length) goto rx_done;"
    for idx, lm in enumerate(re.finditer(r'^(rx_s\d+): __attribute__\(\(unused\)\);\n', f, re.M)):
        i = f.index(t, lm.end())
        nxt = re.compile(r'^rx_s\d+: ', re.M).search(f, lm.end())
        if nxt and i > nxt.start():
            continue
        k = labels.index(lm.group(1))
        out.append(f[pos:i])
        out.append("if (scan_position >= subject_length) { if (subject_length < p10_n) { "
                   f"*p10_st = {k}; *p10_pos = scan_position; *p10_acc = last_accept_position; return 2; }} "
                   "goto rx_done; }")
        pos = i + len(t)
    out.append(f[pos:])
    body = "".join(out)
    ev = "scan_position == subject_length || (scan_position + 1 == subject_length"
    body = body.replace(ev, "scan_position == p10_n || (scan_position + 1 == p10_n")
    pnames = [p.strip().split()[-1].lstrip("*").replace("(*", "").split(")")[0] for p in params.split(",")]
    # pnames: subject, subject_length, search_from, capture_spans
    s_, n_, sf_, cs_ = "subject", "subject_length", "search_from", "capture_spans"
    wrap = (f"{m2.group(1)}({params})\n{{\n"
            f"    int st; size_t pos, acc;\n"
            f"    if ({sf_} > {n_}) return 0;\n"
            f"    size_t d = ({n_} - {sf_}) >> P10_SHIFT;\n"
            f"    if (d < P10_D0) d = P10_D0;\n"
            f"    if ({n_} - {sf_} <= d)\n"
            f"        return {name}_p10core({s_}, {n_}, {sf_}, {cs_}, {n_}, -1, 0, 0, &st, &pos, &acc);\n"
            f"    int r = {name}_p10core({s_}, {sf_} + d, {sf_}, {cs_}, {n_}, -1, 0, 0, &st, &pos, &acc);\n"
            f"    if (r != 2) return r;\n"
            f"    if (!memchr({s_} + {sf_}, {req}, {n_} - {sf_})) return 0;\n"
            f"    return {name}_p10core({s_}, {n_}, {sf_}, {cs_}, {n_}, st, pos, acc, &st, &pos, &acc);\n}}\n")
    return body + "\n" + wrap


od = src_dir.rstrip("/") + "-paced2"
os.makedirs(od, exist_ok=True)
pre = "#ifndef P10_SHIFT\n#define P10_SHIFT 6\n#endif\n#ifndef P10_D0\n#define P10_D0 16\n#endif\n#include <string.h>\n"
open(os.path.join(od, "rx.c"), "w").write(pre + src[:fs] + build_paced2() + src[fe:])
for h in os.listdir(src_dir):
    if h.endswith(".h"):
        open(os.path.join(od, h), "w").write(open(os.path.join(src_dir, h)).read())
