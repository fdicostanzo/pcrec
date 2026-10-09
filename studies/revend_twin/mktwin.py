#!/usr/bin/env python3
"""[OPT-REVEND] hand-twin generator (STUDY, not a build path).

    mktwin.py IN.c OUT.c PREFIX EOL

Takes an UNMODIFIED pcrec artifact (a DFA artifact, `RX_DFA_SCAN
"unanchored"`, `RX_DFA_START "reverse-pass"`, emitted with `-p PREFIX`) and
writes its twin: the forward pass of `<PREFIX>_search` is DELETED and the
artifact's OWN reverse block (copied verbatim, not re-written) is run from
the subject end instead -- seeded at `n`, and at `n-1` when EOL is 1 and
`s[n-1] == '\\n'` -- keeping the smallest accepting position `s*` over the
seeds. The match end then comes from the artifact's OWN anchored entry
`<PREFIX>_match` run once at `s*`, never from the walk (form A, "exact";
TWIN_FORM=lower selects form B: s* becomes the unchanged body's
search_from, the forward and reverse passes then run over [s*, n)).

EOL is 1 for a `$`/`\\Z` pattern (the end_window fact's eps), 0 for `\\z`.

Every marker is asserted: an artifact whose text does not have the shape
this script was written against is refused, never half-transformed.
"""
import re, sys

src, dst, p, eol = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
# CONTROLS (the sweep must be able to fail): TWIN_SABOTAGE=noeol drops the
# n-1 seed (a `$` match before a final newline is lost); =firstseed keeps
# the first seed that accepts instead of the minimum over the seeds (the
# leftmost start is lost where the n-1 walk reaches further, `a*$` on
# "aa\n").
sab = __import__("os").environ.get("TWIN_SABOTAGE", "")
if sab == "noeol": eol = 0
# FORM (TWIN_FORM): "exact" (default) hands s* to the anchored entry for the
# end; "lower" hands s* to the artifact's unchanged forward+reverse body as
# its search_from (design note §3, forms A and B).
form = __import__("os").environ.get("TWIN_FORM", "exact")
t = open(src).read()

def need(cond, what):
    if not cond:
        sys.exit(f"mktwin: {src}: {what}")

for stamp, val in (("DFA_SCAN", "unanchored"), ("DFA_START", "reverse-pass")):
    need(f'#define {p.upper()}_{stamp} "{val}"' in t, f"not a {stamp}={val} artifact")

# the search function's body
m = re.search(r"^int %s_search\(.*?^\}\n" % re.escape(p), t, re.S | re.M)
need(m, "no <p>_search definition")
body = m.group(0)

# (1) the forward pass: from its first declaration to its no-match return
# an artifact with a REQ pre-check/handoff starts its scan at the handoff
# position (read from search_from at the top of the body, before the tables)
ho_txt = ("    size_t handoff_position = %s_reqrun(subject, subject_length, search_from);\n"
          "    if (handoff_position >= subject_length) return 0;\n") % p
handoff = ho_txt in body
if handoff:
    # the req-use handoff's "c - K" back-off block, when emitted, follows it
    ho_adj = re.search(r"    if \(handoff_position - search_from > \d+\) \{\n        handoff_position -= \d+;\n    \} else\n        handoff_position = search_from;\n", body)
    if ho_adj and body.find(ho_txt) + len(ho_txt) == ho_adj.start():
        ho_txt += ho_adj.group(0)
fwd_a = body.find("    size_t scan_position = %s;\n" % ("handoff_position" if handoff else "search_from"))
fwd_z_txt = "    if (last_accept_position == (size_t)-1) return 0;\n"
fwd_z = body.find(fwd_z_txt)
need(fwd_a >= 0 and fwd_z > fwd_a, "forward-pass markers")
need(body.count(fwd_z_txt) == 1, "forward no-match return not unique")
need("if (search_from > subject_length) return 0;\n" in body[fwd_a:fwd_z],
     "forward pass lost its search_from guard")
need(not handoff or form == "lower", "REQ-handoff artifacts are twinned in form B only")

# (2) the reverse block, verbatim: from its start declaration to the
#     no-match return that follows it
rev_head = ("    {\n        size_t match_end_position = last_accept_position;\n")
need(body[fwd_z + len(fwd_z_txt):].startswith(rev_head), "reverse block head")
r_a = fwd_z + len(fwd_z_txt) + len(rev_head)
r_z_txt = "        if (match_start_position == (size_t)-1) return 0;\n"
r_z = body.find(r_z_txt, r_a)
need(r_z > r_a, "reverse block tail")
rev = body[r_a:r_z]
need(rev.startswith("        size_t match_start_position = (size_t)-1;\n"),
     "reverse block does not open with its start variable")
need("size_t rewind_position = match_end_position;" in rev, "reverse seed line")
need("return" not in rev, "the reverse block returns from inside (the seed loop would be bypassed)")
tail = body[r_z + len(r_z_txt):]
need(tail.startswith("        if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)match_start_position; capture_spans[0][1] = (ptrdiff_t)match_end_position; }\n        return 1;\n    }\n}\n"),
     "unexpected success tail (captures beyond group 0?)")

# the reverse block, indented one level deeper inside the seed loop
rev_in = "".join("    " + l if l.strip() else l for l in rev.splitlines(True))
# the walk is a COPY of the block; form B keeps the original too, so the
# copy's label is renamed (the emitted label is `<p>_reverse_scan_views`)
rev_in = rev_in.replace("%s_reverse_scan_views" % p, "%s_revend_scan_views" % p)

new = (
    "    if (search_from > subject_length) return 0;\n"
    "    /* [OPT-REVEND] HAND-TWIN: no forward pass. The artifact's own reverse\n"
    "     * block runs from each possible match END (n; n-1 under $/\\Z when the\n"
    "     * last byte is the newline) and the smallest accepting position over\n"
    "     * the seeds is the leftmost-first START. */\n"
    "    size_t revend_start = (size_t)-1;\n"
    "    for (int revend_seed = 0; revend_seed < %d; revend_seed++) {\n"
    "        size_t match_end_position = subject_length;\n"
    "        if (revend_seed == 1) {\n"
    "            if (subject_length == 0 || subject[subject_length - 1] != '\\n') break;\n"
    "            match_end_position = subject_length - 1;\n"
    "        }\n"
    "        if (match_end_position < search_from) break;\n"
    "%s"
    + ("            if (match_start_position != (size_t)-1 && revend_start == (size_t)-1) revend_start = match_start_position;\n"
       if sab == "firstseed" else
       "            if (match_start_position < revend_start) revend_start = match_start_position;\n")
    +
    "    }\n"
    "    if (revend_start == (size_t)-1) return 0;\n"
    "    {\n"
    "        rx_ctx revend_ctx = { subject, subject_length, revend_start, 0, NULL, NULL, NULL, 0 };\n"
    "        ptrdiff_t revend_len = %s_match(&revend_ctx);\n"
    "        if (revend_len < 0) return PCREC_ERR_INTERNAL;   /* the proof says unreachable */\n"
    "        if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)revend_start; capture_spans[0][1] = (ptrdiff_t)revend_start + revend_len; }\n"
    "        return 1;\n"
    "    }\n"
    "}\n") % (1 + eol, rev_in, p)

if form == "lower":
    # FORM B: the walk's s* is handed to the UNCHANGED body as its lower
    # bound (a WINDOW row handing LOWER, W1's own type); nothing after it
    # is touched, so the forward pass runs over [s*, n) and the reverse
    # pass recovers s* again.
    head = new[:new.index("    if (revend_start == (size_t)-1) return 0;\n")]
    # with a REQ handoff, the pre-check MOVES to after the walk (design 4.1,
    # PRESENCE: it scans [s*, n), never [search_from, n))
    pre = body[:fwd_a]
    ho = ""
    if handoff:
        pre = pre.replace(ho_txt, "")
        ho = ho_txt
    body2 = (pre + head +
             "    if (revend_start == (size_t)-1) return 0;\n"
             "    search_from = revend_start;\n" + ho + body[fwd_a:])
else:
    body2 = body[:fwd_a] + new
# the anchored entry must be its own machine, never a call back into _search
mm = re.search(r"^ptrdiff_t %s_match\(const rx_ctx \*ctx\)\n\{.*?^\}\n" % p, t, re.S | re.M)
need(mm, "no <p>_match definition")
need("%s_search(" % p not in mm.group(0), "<p>_match calls <p>_search (not its own machine)")

out = t[:m.start()] + body2 + t[m.end():]
# a prototype for the anchored entry ahead of the search's attribute block
proto = "ptrdiff_t %s_match(const rx_ctx *ctx);\n" % p
k = out.find("#ifndef __has_attribute\n")
need(0 <= k < out.find("int %s_search(" % p), "no attribute block ahead of _search")
out = out[:k] + proto + out[k:]
open(dst, "w").write(out)
