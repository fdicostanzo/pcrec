#!/usr/bin/env python3
"""docs/dev/lanes/k382_evidence/census.py -- lane k382's MOVER CENSUS for [MEMFN] R-38 K38-2 (pcrec abi
100 -> 101 since lane k382m merged main e889ba64c; 99 -> 100 over d81ebd294 before it; was 98 -> 99, "the seam event"), in r30b_evidence/census.py's shape (emit_sweep has no abi normalization):
which corpus artifacts move, does each move lie in a DECLARED population
(docs/design/memfn/span_runs_sheet.md rev 1.3 §5.1, the abi changelog's top entry), and did every
artifact that SHOULD move (read off BASE, never off the tip) actually move?

    python3 -I census.py --base BIN --new BIN --tree DIR --out FILE [--jobs N] [--shard I/N]
                         [--sample N] [--patterns-file F]... [--control NAME]

BASE is main e889ba64c's pcrec ([PFFIX] + the D27 \\p corpus + cloud mech/recid, abi 100), NEW the K38-2 tip's (abi 101). The corpus is every distinct
pattern scripts/emit_sweep.py enumerates (its `enumerate_corpus`, one implementation), each compiled
`--features all` like emit_sweep's argv streams. NEW's output has the abi digits mapped back (101 -> 100, --abi)
in the five places they occur and nothing else is normalized; rc and stderr are compared too.

ARMS (.c, `-p rx -o -`): c-default, c-utf8 (-e utf8), c-vm, c-vm-utf8, c-comments (-fcomments),
c-simd (-fmemfn-simd); LISTINGS: ir (--engine=vm --emit-ir, may NOT move at all) and facts
(--emit-facts=byte,utf8, rows classified like the .c stamps). XARMS (`x:*`): every arm of the identity
gate (emit_sweep.ident_arms against --base-rev): each `--extra` arm's c-default/c-vm/emit-ir streams, the
`start` arm table (emit_sweep.arm_table, 42 rows) at c-default/c-vm, and `witness` (--witness-bins).
COMPOSITION: every .rxt/.rxtin build (emit_sweep's stream 4).

THE PREDICTION is read from BASE ALONE: BASE's own facts listing (per encoding: `req_whole_run`, the
cut window `req_run` = hex@idx, its offset `at` in the whole run) and BASE's artifact on the arm.
  CUT     the whole run is longer than BASE's cut window (a run over 8 positions).
  WHOLE   BASE's artifact calls `rx_reqrun_whole(` (the K66 two-part pre-check).
  FLIP    BASE's REQ_WHY is "dominated" and the tip's is "emitted" (§4.2's clip flip; only on CUT).
THE POPULATIONS (a moved line is classified by its region -- a `#define` stamp's name, matched by
suffix so a sub-artifact's `RX__Q_*` stamps count, or the enclosing function -- first match):
  P1  K: a `*REQ_HANDOFF` stamp; `handoff_position`/`landmark` lines of a search entry. Allowed on CUT
      with an offset > 0 among `ats`, or inside a FLIP. MUST: CUT, an `at` > 0, BASE's handoff stamp
      equal to the cut window's K (`req_landmark_maxoff`) -> the tip's is K - at.
  P2  a `*REQ_RUN` stamp. Allowed on CUT (2a: the tip renders a `rx_reqrun(` pre-check run part;
      2b: not). MUST: CUT and BASE's stamp is the cut window -> the tip's hex is the whole run.
      P2s (counted APART, a possible open question): the hex unchanged, BASE's `@` lost (no `@` on the
      tip), mask unchanged; examples listed (`== P2s-example`). Kit manager ruling 2 (2026-11-11): only
      where the tip renders NO search that reads a run position (no reqrun block, no `cover` DFA scan, no
      `run-pinned` prefilter: the @ table's row 3); a P2s member with any of those is UNEXPLAINED.
  P3  the reqrun blocks (`*reqrun*` functions and lines naming them), `*MEMFN_LIBC`, `*RUN_WORDS`.
      Allowed on CUT, WHOLE or FLIP. MUST: WHOLE -> the tip names no `_reqrun_whole` and calls
      `rx_reqrun(`. P3v (c-simd only, with a P3 move): the one run part takes a kit SIMD form
      (`*MEMFN_FORMS`, `*SIMD_GUARDED_BYTES`, an intrinsics `#include`, the target guard/region).
  P4  the run pin: `*ofsskip*`/`*prefilter*` blocks, `*DFA_PREFILTER*`, `*REQ_WHY`, a `scan_position`
      or `*_prefilter(` call line of a search entry (a FLIP starts it at the handoff). Allowed on CUT only. P4f counts the FLIPs.
  ADJ the `rx_w8` helper, blank and brace lines: allowed beside a P1, P3 or P4 move, never alone.
  P5  comment text: only on c-comments, beside a P1-P4 or P5k move. P5k: [K82]'s "before its run
      window" becomes "before its whole run" -- on EVERY artifact that carried it (MUST, two-sided),
      uncut runs included (the window WAS the run); the census rewrites BASE's spelling and diffs the rest.
  facts: rows `req_run` (P2), `req_run_maxoff`/`req_landmark_maxoff` (P1), `run_pin` (P4), the
      decisions stamps as above, part-layout rows naming a reqrun/ofsskip function; `used`: a `req_*`
      row whose ONLY move is its `used` column, allowed where that encoding's REQ_WHY moved (a FLIP)
      or, for `req_whole_run` no -> yes, where BASE's `req_run` was used (the reader moved, §4.3).
      Fret (k382fix, review 2026-11-11 r1 k382 F5): the `req_run` and `req_run_maxoff` rows RETIRED
      (present at BASE, absent on the tip); a retired row that moves but stays is still P2/P1.
Anything else that moved is UNEXPLAINED. The verdict is red on any UNEXPLAINED artifact, any MUST
artifact that did not move as declared, an empty task list, or (K35, a full run only, not --sample /
--patterns-file / --shard) an empty P1, P2a, P2b or P3 summed over c-default + c-vm.
--control NAME (a NEGATIVE control, never for a gate): `no-p3` stops classifying P3 lines (they become
UNEXPLAINED); `no-norm` maps no abi digit back. Either must turn the verdict red.
"""
import argparse
import concurrent.futures
import difflib
import shlex
import os
import re
import subprocess
import sys

def abi_pairs(old, new):
    """The four places the abi digits occur, NEW's spelling -> BASE's (nothing else is normalized)."""
    return [(b"(abi %d)" % new, b"(abi %d)" % old),
            (b"(PCREC_RX_ABI_H + 0) != %d" % new, b"(PCREC_RX_ABI_H + 0) != %d" % old),
            (b"#define PCREC_RX_ABI_H %d" % new, b"#define PCREC_RX_ABI_H %d" % old),
            (b"    .abi = %d," % new, b"    .abi = %d," % old)]


ABI = abi_pairs(100, 101)       # --abi OLD:NEW sets it (the lane's event: 100 -> 101 over BASE e889ba64c)
BASE_REV = "e889ba64c"          # --base-rev: the identity gate's arm list is read against it
WITNESS = None                  # --witness-bins BASE_W NEW_W: the -DPCREC_SIMD_WITNESS builds
C = ["-p", "rx", "--features", "all", "-o", "-"]
# (arm, extra argv, facts encoding)
ARMS = [
    ("c-default", [], "byte"),
    ("c-utf8", ["-e", "utf8"], "utf8"),
    ("c-vm", ["--engine=vm"], "byte"),
    ("c-vm-utf8", ["--engine=vm", "-e", "utf8"], "utf8"),
    ("c-comments", ["-fcomments"], "byte"),
    ("c-simd", ["-fmemfn-simd"], "byte"),
]
IR = ["--features", "all", "--engine=vm", "--emit-ir"]
FACTS = ["--features", "all", "--emit-facts=byte,utf8"]
POPS = ["P1", "P2", "P2a", "P2b", "P2s", "P2se", "P2sd", "P2so", "Aa_K", "Aa_noK", "P3", "P3v", "P4", "P4f", "P5", "P5k", "used",
        "Fret"]   # P2 (unsplit): the facts listing
FLOOR_ARMS = ("c-default", "c-vm")
FLOOR_POPS = ("P1", "P2a", "P2b", "P3")
WITNESSES = [  # tests/codegen/run_prechecks.sh, reqcube_check.py, the sheet's §4.2/§5.1 examples
    "(?:ab|cd)xabcdefghijkq", "xabcdefghijkq", "hello world", r"(x?)([a-z]+)+eeeeeeee~#~#~#~#\1",
    "github_pat_[A-Za-z0-9]{4}", "(a)(b)", "abc", "(?i)hello", r"\s?xabcdefghijkq", r"x\wabcdefghijklmn\w+",
    "a.*xabcdefghijkq", r"[a-z]abcdefghijkl\d+", r"\w\wabcdefghijklmnop[0-9]+x", r"(?:a|b)abcdefghijklmn\d*z",
    "error: segmentation fault at", "[a-z]abcdefghijklmnopqrstuvwx[0-9]", r"(x?)([a-z]+)+Q.abcdefghij\1",
    r"(x?)([a-z]+)+abcdefgh\1", "(x?)([a-z]+)+eeeeeeee~#~#~#~#", r"(x?)(?i:abcdefghijkl)\1", "ab.*xyzw",
]
CONTROL = ""
XARMS = []


def norm(out):
    if CONTROL == "no-norm":
        return out
    for a, b in ABI:
        out = out.replace(a, b)
    return out


SIZE_ERR = re.compile(rb"(large artifact: |pattern too large: )(\d+)( bytes of emitted (?:C source \(|code))(\d+)?")


def norm_err(err):
    """Either side's stderr with the NUMBERS of pcrec's size diagnostics masked (the `large artifact: N
    bytes of emitted C source (M of code)` warning, the `pattern too large: N bytes` refusal): they count the
    artifact's bytes, so they move with the abi digits (+4 at 99 -> 100) AND with every real mover, and a
    listing's sub-compiles print several (measured: one moved 4, one did not). The artifact's own text is
    judged on its own arm; the diagnostic's wording, its presence and the exit status still must match.
    Nothing else is masked."""
    if CONTROL == "no-norm":
        return err
    return SIZE_ERR.sub(lambda m: m.group(1) + b"N" + m.group(3) + (b"N" if m.group(4) else b""), err)


def run(argv, timeout=120):
    try:
        r = subprocess.run(argv, capture_output=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -9, b"", b"TIMEOUT"


def stamp(text, name):
    m = re.search(rb'^#define RX_' + name + rb' "([^"]*)"', text, re.M)
    return m.group(1).decode() if m else None


def facts_of(listing, enc):
    """{fact: value} of one encoding's `#section facts` rows."""
    out = {}
    for ln in listing.decode("utf-8", "replace").split("\n"):
        c = ln.split("\t")
        if len(c) >= 7 and c[0] == enc and not ln.startswith("#"):
            out.setdefault(c[1], c[6])
    return out


def run_of(f):
    """(whole hex, cut hex, ats, K) from BASE's facts, or None (no run). `ats`: every offset the cut
    window's bytes occur at in the whole run (a repeated byte makes the window's own `at` ambiguous)."""
    whole, cut = f.get("req_whole_run", "").split("/")[0], f.get("req_run", "")
    if not re.fullmatch(r"[0-9a-f]{4,}", whole) or not cut or cut == "none":
        return None
    ch = cut.split("@")[0].split("/")[0]
    ats = [i // 2 for i in range(0, len(whole) - len(ch) + 1, 2) if whole[i:i + len(ch)] == ch]
    k = f.get("req_landmark_maxoff", "")
    return whole, ch, ats, int(k) if k.isdigit() else None


def stamps_all(text):
    return {m.group(1).decode(): m.group(2).decode("utf-8", "replace")
            for m in re.finditer(rb'^#define (\w+) "([^"]*)"', text, re.M)}


def hexof(v):
    return (v or "").split("@")[0].split("/")[0]


def regions(lines):
    """Per line: (function or `#define` name or 'top', is_comment)."""
    out, fn, incom = [], "top", False
    for ln in lines:
        s = ln.strip()
        com = incom or s.startswith(b"/*") or s.startswith(b"//") or (s.startswith(b"*") and not s.startswith(b"*)"))
        if s.startswith(b"/*") or incom:
            incom = b"*/" not in s[2 if s.startswith(b"/*") and not incom else 0:]
        m = re.match(rb"#define (\w+)", ln)
        if m:
            out.append((m.group(1).decode(), com))
            continue
        h = (re.match(rb"[A-Za-z_][^;=]*?\b([A-Za-z_]\w*)\s*\(", re.sub(rb"__attribute__\(\(\w*\)\)\s*", b"", ln))
             if not com and ln[:1] not in b" \t#}" and not ln.startswith(b"__attribute__") else None)
        if h and not s.endswith(b";"):
            fn = h.group(1).decode()
            out.append((fn, False))
            if s.endswith(b"}"):
                fn = "top"
            continue
        out.append((fn, com))
        if ln == b"}":
            fn = "top"
    return out


K82_OLD = re.compile(rb"(\[K82\] every match begins at most \d+ bytes? before its) run\n(\s*\*) window,")
K82_NEW = rb"\1 whole\n\2 run,"
SIMD_SCAFFOLD = re.compile(rb"#include <\w*intrin\.h>|#pragma GCC (push_options|pop_options|target)|"
                           rb"#if !?defined\(__|#error|#endif|#else|#elif")


def classify(name, com, line, comments_arm, simd_arm):
    """The population of ONE moved line, from its region alone; None = unexplained."""
    if com:
        return "P5" if comments_arm else None
    if simd_arm and (name in ("RX_MEMFN_FORMS", "RX_SIMD_GUARDED_BYTES") or SIMD_SCAFFOLD.match(line.strip())):
        return "P3v"                 # the one run part takes a kit SIMD form (its scaffolding)
    if name.endswith("_REQ_HANDOFF"):
        return "P1"
    if name.endswith("_REQ_RUN"):
        return "P2"
    if name.endswith("MEMFN_LIBC") or name.endswith("RUN_WORDS") or "reqrun" in name or b"reqrun" in line:
        return "P3" if CONTROL != "no-p3" else None
    if name == "rx_w8" or line.strip() in (b"", b"{", b"}", b"} else", b"else"):
        return "ADJ"                 # the rx_w8 helper, a blank or brace line beside a moved block
    if "DFA_PREFILTER" in name or name.endswith("REQ_WHY") or "ofsskip" in name or "prefilter" in name:
        return "P4"
    if re.search(r"_search|_match|_find|__", name):
        if re.search(rb"handoff_position|landmark", line):
            return "P1"
        if re.search(rb"scan_position|_prefilter\(", line):
            return "P4"
    return None


COVER_FIND = re.compile(rb"memchr\(rx_mf\d+_s \+ rx_mf\d+_c \+ (\d+), (\d+),")


def scan_search(text):
    """What in an artifact reads a run position with a scan find (the REQ_RUN @ table's rows 1-2), or ''
    (row 3): a reqrun pre-check block, a `cover` DFA scan, a `run-pinned` prefilter."""
    if re.search(rb"\w_reqrun(__\w+)?\(", text):
        return "a reqrun block"
    if re.search(rb'^#define \w+_SCAN "cover"', text, re.M):
        return "a cover window search"
    if re.search(rb'^#define \w+_PREFILTER "run-pinned"', text, re.M):
        return "a run-pinned prefilter"
    return ""


def moved_lines(b, n):
    a, c = b.split(b"\n"), n.split(b"\n")
    ra, rc = regions(a), regions(c)
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, c, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        out += [(ra[i][0], ra[i][1], a[i]) for i in range(i1, i2)]
        out += [(rc[j][0], rc[j][1], c[j]) for j in range(j1, j2)]
    return out


def judge_c(arm, rb, rn, f, comments_arm, simd_arm):
    """(pops moved set, problem or '', must list, flags) for one .c arm of one pattern."""
    moved = rb[0] != rn[0] or norm_err(rb[2]) != norm_err(rn[2]) or rb[1] != norm(rn[1])
    b, n = rb[1], norm(rn[1])
    ri = run_of(f)
    cut = bool(ri) and len(ri[0]) > len(ri[1])
    ats = ri[2] if ri else []
    atpos = any(x > 0 for x in ats)
    whole = re.search(rb"\w_reqrun_whole\(", b) is not None
    flip = cut and stamp(b, b"REQ_WHY") == "dominated" and stamp(n, b"REQ_WHY") == "emitted"
    must = []
    sb, sn = stamp(b, b"REQ_RUN"), stamp(n, b"REQ_RUN")
    if cut and sb is not None and sb.split("@")[0].split("/")[0] == ri[1]:
        must.append(("P2", (sn or "").split("@")[0].split("/")[0] == ri[0]))
    hb, hn = stamp(b, b"REQ_HANDOFF"), stamp(n, b"REQ_HANDOFF")
    if cut and atpos and hb is not None and hb.isdigit() and ri[3] is not None and int(hb) == ri[3]:
        must.append(("P1", hn in {str(int(hb) - x) for x in ats if x > 0}))
    if whole:
        must.append(("P3", b"_reqrun_whole" not in n and re.search(rb"\w_reqrun\(", n) is not None))
    if comments_arm and K82_OLD.search(b):
        # P5k: [K82]'s "run window" spelling becomes "whole run" (on uncut runs too: the window WAS the run)
        must.append(("P5k", not K82_OLD.search(n)))
        b = K82_OLD.sub(K82_NEW, b)
        if b == n:
            return {"P5k"}, "", must, (cut, whole, flip)
    if rb[0] != rn[0] or norm_err(rb[2]) != norm_err(rn[2]):
        return set(), "rc/stderr moved", must, (cut, whole, flip)
    if not moved:
        bad = "a MUST artifact did not move (%s)" % ",".join(p for p, _ in must) if must else ""
        return set(), bad, must, (cut, whole, flip)
    pops, unexp = set(), []
    stb, stn = stamps_all(b), stamps_all(n)
    if comments_arm and any(p == "P5k" for p, _ in must):
        pops.add("P5k")
    for name, com, line in moved_lines(b, n):
        p = classify(name, com, line, comments_arm, simd_arm)
        if p == "P2":
            vb, vn = stb.get(name, ""), stn.get(name, "")
            if hexof(vb) == hexof(vn) and "@" in vb and "@" not in vn and vb.split("/")[1:] == vn.split("/")[1:]:
                why = scan_search(n)
                wm = re.search(rb'^#define \w+_REQ_WHY "(\w+)"', n, re.M)
                p = "P2se" if wm and wm.group(1) == b"emitted" else "P2sd"   # emitted-no-scan / dominated or other WHY
                if why == "a cover window search":
                    # k382 2026-11-11 (match_api §6.3.7 para 7 row 3): a cover find that reads a position
                    # OUTSIDE the run is P2so. The find is the tip's `memchr(rx_mfK_s + rx_mfK_c + N, B, ..)`;
                    # the artifact does not name the run's offset in the find's frame, so "outside" is read
                    # CONSERVATIVELY: no find byte B is any byte of the run (masked runs: B folded by the
                    # mask too). A find byte that occurs in the run, or no readable find, is UNEXPLAINED.
                    hx = bytes.fromhex(hexof(vb).decode() if isinstance(hexof(vb), bytes) else hexof(vb))
                    mk = vb.split("/")[1] if "/" in vb else ""
                    mb = bytes.fromhex(mk) if mk else b"\xff" * len(hx)
                    runb = {c & m for c, m in zip(hx, mb)}
                    finds = [(int(o), int(c)) for o, c in COVER_FIND.findall(n)]
                    hit = [(o, c) for o, c in finds if any((c & m) in runb for m in set(mb))]
                    if finds and not hit:
                        p, why = "P2so", ""
                    else:
                        why = ("a cover find whose byte is in the run (+offset, byte: %s)" % hit
                               if finds else "a cover window search with no readable memchr find")
                if why:      # ruling 2: no @ only where NO search reads a run position (table row 3)
                    unexp.append("P2s refused: %s lost its @ but the tip renders %s" % (name, why))
                    continue
            elif not cut:
                p = None
            else:
                p = "P2a" if re.search(rb"\w_reqrun\(", n) else "P2b"
        elif p == "P1" and not ((cut and atpos) or flip):
            p = None
        elif p == "P3" and not (cut or whole or flip):
            p = None
        elif p == "P4" and not cut:
            p = None
        if p is None:
            unexp.append("%s%s: %s" % (name, " (comment)" if com else "", line[:100].decode("utf-8", "replace")))
        else:
            pops.add(p)
    if "ADJ" in pops:
        pops.discard("ADJ")
        if not pops & {"P1", "P3", "P4"}:
            unexp.append("the rx_w8 helper / a blank or brace line moved alone")
    if "P3v" in pops and "P3" not in pops:
        unexp.append("SIMD scaffolding moved without a run-part (P3) move")
    if "P5" in pops and not pops & {"P1", "P2a", "P2b", "P3", "P4", "P5k"}:
        unexp.append("comment text moved alone")
    bad = ""
    if unexp:
        bad = "UNEXPLAINED: " + " | ".join(unexp[:4])
    elif any(not ok for _, ok in must):
        bad = "a MUST move is not the declared one (%s)" % ",".join(p for p, ok in must if not ok)
    if flip:
        pops.add("P4f")
    # ADMISSION/PICK (k382 2026-11-11, COUNT-ONLY, never a verdict): a landmark admission or NEXT pick moved,
    # i.e. a REQ_HANDOFF none<->number, DFA_PREFILTER, VM_START_SCAN or REQ_WHY stamp changed; split by
    # whether K moved too (P1 in the artifact) or not (Aa_K / Aa_noK).
    if any(stb.get(k) != stn.get(k) for k in set(stb) | set(stn) if ADM_STAMP.search(k)):
        pops.add("Aa_K" if "P1" in pops else "Aa_noK")
    return pops, bad, must, (cut, whole, flip)


ADM_STAMP = re.compile(r"_(REQ_HANDOFF|DFA_PREFILTER|VM_START_SCAN|REQ_WHY)$")
FACT_POP = {"req_run": "P2", "req_run_maxoff": "P1", "req_landmark_maxoff": "P1", "run_pin": "P4",
            "RX_REQ_RUN": "P2", "RX_REQ_HANDOFF": "P1", "RX_REQ_WHY": "P4", "RX_MEMFN_LIBC": "P3",
            "RX_RUN_WORDS": "P3"}


def facts_rows(text):
    """{(section, encoding, name): row} of a facts listing, plus the other lines as a sorted list."""
    rows, other, sec = {}, [], ""
    for ln in text.split(b"\n"):
        if ln.startswith(b"#section "):
            sec = ln[9:].decode()
        c = ln.decode("utf-8", "replace").split("\t")
        if not ln.startswith(b"#") and len(c) >= 3:
            rows[(sec, c[0], c[1])] = c
        else:
            other.append(ln)
    return rows, sorted(other)


def judge_facts(rb, rn):
    """The facts listing, row by row (keyed by section, encoding and fact/stamp/function name): a moved
    row's name must be a declared one (FACT_POP, an RX_DFA_PREFILTER* stamp, a part-layout row naming a
    reqrun or ofsskip function); a `req_*` fact row whose ONLY move is its `used` column is `used`,
    allowed where the same encoding's RX_REQ_WHY moved (a FLIP's new pre-check asks the fact)."""
    if rb[0] != rn[0] or norm_err(rb[2]) != norm_err(rn[2]):
        return set(), "rc/stderr moved"
    (ra, oa), (rc, oc) = facts_rows(rb[1]), facts_rows(norm(rn[1]))
    pops, unexp, used = set(), [], []
    if oa != oc:
        unexp.append("a non-row line moved")
    why = {k[1] for k in set(ra) | set(rc) if k[2] == "RX_REQ_WHY" and ra.get(k) != rc.get(k)}
    for k in sorted(set(ra) | set(rc)):
        x, y = ra.get(k), rc.get(k)
        if x == y:
            continue
        sec, enc, key = k
        if sec == "facts" and x and y and len(x) == len(y) and len(x) > 5 and key.startswith("req_") \
                and [v for i, v in enumerate(x) if i != 5] == [v for i, v in enumerate(y) if i != 5]:
            used.append(k)
            continue
        if sec == "facts" and y is None and key in ("req_run", "req_run_maxoff"):
            pops.add("Fret")    # k382fix (review r1 k382 F5): the two rows RETIRED, gone from every listing
            continue
        if sec.startswith("part-layout"):
            p = "P3" if "reqrun" in key else "P4" if "ofsskip" in key or "prefilter" in key else None
        else:
            p = FACT_POP.get(re.sub(r"^RX_\w*?(REQ_\w+|MEMFN_LIBC|RUN_WORDS)$", r"RX_\1", key)) \
                or ("P4" if key.startswith("RX_") and "DFA_PREFILTER" in key else None)
        if p == "P3" and CONTROL == "no-p3":
            p = None
        if p:
            pops.add(p)
        else:
            unexp.append("%s %s %s" % k)
    for k in used:
        rr = ra.get(("facts", k[1], "req_run"))
        if k[2] == "req_whole_run" and rr and len(rr) > 5 and rr[5] == "yes" and rc[k][5] == "yes":
            pops.add("used")         # the cut window's reader now reads the whole run (§4.3)
        elif k[1] in why:
            pops.add("used")
        else:
            unexp.append("%s %s %s (used only, no REQ_WHY move)" % k)
    return pops, ("UNEXPLAINED: " + " | ".join(unexp[:4]) if unexp else "")


def one(task):
    base, new, pat = task
    res = []
    fb = run([base] + FACTS + ["--pattern", pat])
    fn = run([new] + FACTS + ["--pattern", pat])
    for arm, extra, enc in ARMS:
        rb = run([base] + C + extra + ["--pattern", pat])
        rn = run([new] + C + extra + ["--pattern", pat])
        pops, bad, must, flags = judge_c(arm, rb, rn, facts_of(fb[1], enc), arm == "c-comments", arm == "c-simd")
        moved = rb[0] != rn[0] or rb[1] != norm(rn[1]) or norm_err(rb[2]) != norm_err(rn[2])
        res.append((arm, moved, pops, bad, must, flags))
    ib, inn = run([base] + IR + ["--pattern", pat]), run([new] + IR + ["--pattern", pat])
    im = ib[0] != inn[0] or ib[1] != norm(inn[1]) or norm_err(ib[2]) != norm_err(inn[2])
    res.append(("ir", im, set(), "the ir listing moved" if im else "", [], (False, False, False)))
    fm = fb[0] != fn[0] or fb[1] != norm(fn[1]) or norm_err(fb[2]) != norm_err(fn[2])
    fp, fbad = judge_facts(fb, fn) if fm else (set(), "")
    res.append(("facts", fm, fp, fbad, [], (False, False, False)))
    # BASE's facts UNDER THE ARM'S OWN FLAGS (lane k382m, 2026-11-12): the prediction is the run the arm's
    # BASE artifact was compiled from, so `-fno-req-run-fold`'s unfolded run, `-i`'s folded one, etc. Was:
    # the default listing for every arm but `-i`, which predicted the FOLDED whole run under
    # utf8+-fno-req-run-fold and read `^(a)(b)(c)(d)(e)(f)(g)(h)(i)(j|k)(?-10)$` red. One listing per distinct
    # flag list AND engine (`-fprefilter` is a VM-only flag); a listing BASE refuses under the arm while it
    # compiles the arm's artifact is a problem on the arm, never a silent fall back to the default.
    fxs = {(): fb}
    for arm, extra, stream in XARMS:
        if stream.startswith("w-"):          # the witness arm: the -DPCREC_SIMD_WITNESS builds
            eng = ["--engine=vm"] if stream == "w-c-vm" else []
            rb = run([WITNESS[0]] + C + eng + ["--pattern", pat])
            rn = run([WITNESS[1]] + C + eng + ["--pattern", pat])
            pops, bad, must, flags = judge_c(arm, rb, rn, facts_of(fb[1], "byte"), False, False)
            moved = rb[0] != rn[0] or rb[1] != norm(rn[1]) or norm_err(rb[2]) != norm_err(rn[2])
            res.append((arm, moved, pops, bad, must, flags))
            continue
        if stream == "ir":
            ib = run([base] + IR[:-1] + extra + ["--emit-ir", "--pattern", pat])
            inn = run([new] + IR[:-1] + extra + ["--emit-ir", "--pattern", pat])
            im = ib[0] != inn[0] or ib[1] != norm(inn[1]) or norm_err(ib[2]) != norm_err(inn[2])
            res.append((arm, im, set(), "the ir listing moved" if im else "", [], (False, False, False)))
            continue
        eng = ["--engine=vm"] if stream == "c-vm" else []
        rb = run([base] + C + eng + extra + ["--pattern", pat])
        rn = run([new] + C + eng + extra + ["--pattern", pat])
        enc = "utf8" if "utf8" in extra else "byte"
        key = tuple(eng + [x for x in extra if x != "--engine=vm"])
        if key not in fxs:
            fxs[key] = run([base] + FACTS + list(key) + ["--pattern", pat])
        fx = fxs[key]
        if fx[0] != 0 and rb[0] == 0:
            res.append((arm, True, set(), "BASE compiles the arm but refuses --emit-facts under %s" % " ".join(key),
                        [], (False, False, False)))
            continue
        pops, bad, must, flags = judge_c(arm, rb, rn, facts_of(fx[1], enc), "-fcomments" in extra,
                                         any(x.startswith("-fmemfn-simd") for x in extra))
        moved = rb[0] != rn[0] or rb[1] != norm(rn[1]) or norm_err(rb[2]) != norm_err(rn[2])
        res.append((arm, moved, pops, bad, must, flags))
    return pat, res


def xarms_of(emit_sweep, new_bin):
    """The identity gate's declared arms (emit_sweep.ident_arms, one implementation), each as its
    c-default / c-vm / emit-ir streams: (name, extra argv, stream). `base` is this census's own arms.
    `start` is emit_sweep's arm table (`arm_table()`, (base, flag) rows: ARM_BASES[base] + the flag) at
    c-default and c-vm, as `x:start:<flag>`. `witness` is BASE's and NEW's -DPCREC_SIMD_WITNESS builds
    (--witness-bins) at c-default and c-vm, as `x:witness:*`; without --witness-bins it is NOT covered
    and is named in the output (skipped)."""
    out, skipped = [], []
    for b, flag in emit_sweep.arm_table():
        extra = list(emit_sweep.ARM_BASES[b]) + shlex.split(flag)
        for stream in ("c-default", "c-vm"):
            out.append(("x:start:%s%s:%s" % ("utf8+" if b == "utf8" else "", flag or "null", stream), extra, stream))
    if WITNESS:
        out += [("x:witness:c-default", [], "w-c-default"), ("x:witness:c-vm", [], "w-c-vm")]
    for name, args in emit_sweep.ident_arms(new_bin, BASE_REV):
        argv = shlex.split(args)
        ex = [x[len("--extra="):] for x in argv if x.startswith("--extra=")]
        st = next((x[len("--streams="):] if x.startswith("--streams=") else argv[i + 1]
                   for i, x in enumerate(argv) if x == "--streams" or x.startswith("--streams=")), "")
        if name in ("base", "start") or (name == "witness" and WITNESS):
            continue
        if not ex:
            skipped.append(name)
            continue
        extra = [w for e in ex for w in shlex.split(e)]
        for stream in ("c-default", "c-vm", "emit-ir"):
            if stream in st.split(","):
                out.append(("x:%s:%s" % (name, "ir" if stream == "emit-ir" else stream), extra,
                            "ir" if stream == "emit-ir" else stream))
    return out, skipped


def composition(base, new, tree, scratch, shard):
    """The composition stream (emit_sweep's stream 4): every .rxt/.rxtin under tests/ built by both sides
    into fresh dirs; each artifact file compared after abi normalization. No facts exist per file, so the
    judgment is region-only and the CUT is read from the two stamps' VALUES (the tip's REQ_RUN hex holds
    BASE's, longer): rows (file:artifact, moved, pops, bad)."""
    import emit_sweep
    files = emit_sweep.find_files(tree, (".rxt", ".rxtin"))
    if shard:
        i, n = (int(x) for x in shard.split("/"))
        files = [p for k, p in enumerate(files) if k % n == i - 1]
    out, producing = [], 0
    for k, fpath in enumerate(files):
        sides = []
        for tag, binp in (("b", base), ("n", new)):
            d = os.path.join(scratch, "comp", "%d%s" % (k, tag))
            subprocess.run(["rm", "-rf", d])
            os.makedirs(d)
            r = run([binp, "--features", "all", fpath, "-o", d])
            arts = {fn: open(os.path.join(d, fn), "rb").read() for fn in sorted(os.listdir(d))}
            subprocess.run(["rm", "-rf", d])
            sides.append((r, arts))
        (rb, ab), (rn, an) = sides
        producing += bool(ab)
        rel = os.path.relpath(fpath, tree)
        if rb[0] != rn[0] or set(ab) != set(an):
            out.append((rel, True, set(), "rc or artifact set moved"))
            continue
        for fn in ab:
            b, n = ab[fn], norm(an[fn])
            if b == n:
                continue
            stb, stn = stamps_all(b), stamps_all(n)
            cut = any(nm.endswith("REQ_RUN") and len(hexof(stn.get(nm))) > len(hexof(v)) and hexof(v) in hexof(stn.get(nm))
                      for nm, v in stb.items())
            f = {"req_whole_run": "ffff", "req_run": "ff"} if cut else {}   # cut, offset unknown: P1 allowed, no MUST
            pops, bad, _, _ = judge_c("composition", (0, b, b""), (0, an[fn], b""), f, False, False)
            out.append(("%s:%s" % (rel, fn), True, pops, bad))
    return out, len(files), producing


def sample_of(pats, n, seed=0):
    """A deterministic sample: the witnesses, then half of the rest from corpus patterns holding a 9+
    literal stretch (the run populations), the other half evenly spaced over the corpus."""
    out = list(WITNESSES)
    longrun = [p for p in pats if re.search(r"[A-Za-z0-9 _:~#-]{9,}", p) and p not in out]
    want = max(0, n - len(out))
    step = max(1, len(longrun) // max(1, want // 2))
    out += longrun[seed % step::step][:want // 2]
    rest = [p for p in pats if p not in out]
    step = max(1, len(rest) // max(1, n - len(out)))
    out += rest[seed % step::step][:n - len(out)]
    return out[:n]


def main():
    global CONTROL
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--shard", default="", help="I/N: the corpus patterns i with i %% N == I-1")
    ap.add_argument("--sample", type=int, default=0, help="a SAMPLE run of N patterns (no K35 floor)")
    ap.add_argument("--sample-seed", type=int, default=0, help="the sample's offset (a different slice)")
    ap.add_argument("--patterns-file", action="append", default=[], help="raw patterns, one per line (added)")
    ap.add_argument("--control", default="", choices=["", "no-p3", "no-norm"])
    ap.add_argument("--no-xarms", action="store_true", help="skip the identity gate's --extra arms")
    ap.add_argument("--no-composition", action="store_true", help="skip the composition stream")
    ap.add_argument("--abi", default="100:101", help="OLD:NEW, the abi event (NEW's digits mapped back)")
    ap.add_argument("--base-rev", default="e889ba64c", help="BASE's revision (the identity arm list)")
    ap.add_argument("--witness-bins", nargs=2, metavar=("BASE_W", "NEW_W"),
                    help="the -DPCREC_SIMD_WITNESS builds of BASE and NEW (the identity arm `witness`)")
    a = ap.parse_args()
    CONTROL = a.control
    global XARMS, ABI, BASE_REV, WITNESS
    o, nw = (int(x) for x in a.abi.split(":"))
    ABI, BASE_REV, WITNESS = abi_pairs(o, nw), a.base_rev, a.witness_bins
    sys.path.insert(0, os.path.join(a.tree, "scripts"))
    import emit_sweep  # noqa: E402  (the corpus enumeration, one implementation)
    corpus = sorted({os.fsdecode(p) for _, _, p in emit_sweep.enumerate_corpus(a.new, a.tree, 60)})
    if len(corpus) < 4000:
        print("census: corpus enumerated %d patterns (< 4000): a blind enumeration" % len(corpus))
        return 1
    pats = sample_of(corpus, a.sample, a.sample_seed) if a.sample else list(corpus)
    for f in a.patterns_file:
        pats += [ln.rstrip("\n") for ln in open(f, encoding="utf-8", errors="surrogateescape") if ln.strip()]
    pats = list(dict.fromkeys(pats))
    if a.shard:
        i, n = (int(x) for x in a.shard.split("/"))
        pats = [p for k, p in enumerate(pats) if k % n == i - 1]
    full = not (a.sample or a.patterns_file)
    skipped = []
    if not a.no_xarms:
        XARMS, skipped = xarms_of(emit_sweep, a.new)
        if len(XARMS) < 150:
            print("census: %d identity --extra arm streams (< 150): a blind arm list" % len(XARMS))
            return 1
    names = [x[0] for x in ARMS] + ["ir", "facts"] + [x[0] for x in XARMS] + ["composition"]
    tally = {k: {"moved": 0, "bad": 0, "must": 0, **{p: 0 for p in POPS}} for k in names}
    overlap, lines, p2s = {}, [], []
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        for pat, res in ex.map(one, [(a.base, a.new, p) for p in pats]):
            ptxt = os.fsencode(pat).decode("utf-8", "backslashreplace").replace("\n", "\\n").replace("\t", "\\t")
            for arm, moved, pops, bad, must, flags in res:
                t = tally[arm]
                t["moved"] += moved
                t["bad"] += bool(bad)
                t["must"] += bool(must)
                for p in pops:
                    t[p] += 1
                if pops:
                    key = (arm, "+".join(sorted(pops)))
                    overlap[key] = overlap.get(key, 0) + 1
                if pops & {"P2se", "P2sd", "P2so"} and arm in FLOOR_ARMS:
                    p2s.append("%s\t%s" % (arm, ptxt))
                if moved or bad:
                    lines.append("%s\t%s\t%s\t%s\t%s" % ("UNEXPECTED" if bad else "MOVED", arm,
                                 "+".join(sorted(pops)) or "-", ptxt, bad))
    ncomp = nprod = 0
    if not a.no_composition:
        crow, ncomp, nprod = composition(a.base, a.new, a.tree, os.environ.get("TMPDIR", "/var/tmp"), a.shard)
        for rel, moved, pops, bad in crow:
            t = tally["composition"]
            t["moved"] += moved
            t["bad"] += bool(bad)
            for p in pops:
                t[p] += 1
            lines.append("%s\tcomposition\t%s\t%s\t%s" % ("UNEXPECTED" if bad else "MOVED", "+".join(sorted(pops)) or "-", rel, bad))
        if full and not a.shard and nprod < 30:
            lines.append("UNEXPECTED\tcomposition\t-\t-\tonly %d producing files (< 30): a blind stream" % nprod)
            tally["composition"]["bad"] += 1
    floor_bad = []
    if full:
        for p in FLOOR_POPS:
            if sum(tally[k][p] for k in FLOOR_ARMS) < 1:
                floor_bad.append(p)
    unexpected = sum(t["bad"] for t in tally.values())
    with open(a.out, "w") as f:
        f.write("# k382 census: %d corpus patterns, %d tasks%s%s%s\n" % (
            len(corpus), len(pats), " SAMPLE" if a.sample else "", " shard " + a.shard if a.shard else "",
            " CONTROL " + CONTROL if CONTROL else ""))
        for ln in sorted(lines):
            f.write(ln + "\n")
        for (arm, combo), c in sorted(overlap.items()):
            f.write("== overlap %-10s %-20s %d\n" % (arm, combo, c))
        for ln in sorted(p2s):
            f.write("== P2s-example\t%s\n" % ln)
        for k in names:
            t = tally[k]
            f.write("== arm %-10s patterns=%d movers=%d must=%d %s unexplained=%d\n" % (
                k, ncomp if k == "composition" else len(pats), t["moved"], t["must"],
                " ".join("%s=%d" % (p, t[p]) for p in POPS if t[p]), t["bad"]))
        f.write("== composition: %d files, %d producing\n" % (ncomp, nprod))
        f.write("== NOT COVERED here (identity arms without --extra): %s\n" % (" ".join(skipped) or "-"))
        f.write("== floor (K35, c-default+c-vm, P1 P2a P2b P3 >= 1): %s\n" % (
            ("EMPTY " + ",".join(floor_bad)) if floor_bad else ("held" if full else "not applied (sample run)")))
        rc = 1 if unexpected or floor_bad or not pats else 0
        f.write("== census COMPLETE: %d unexplained, verdict %s rc=%d\n" % (unexpected, "GREEN" if rc == 0 else "RED", rc))
    os.system("grep -E '^(UNEXPECTED|== arm c-|== arm (ir|facts|composition) |== floor|== census|== NOT|== comp)' "
              + a.out + " | head -40; grep -c '^== arm x:' " + a.out + " | sed 's/^/== x-arms: /'; "
              "grep '^== arm x:' " + a.out + " | grep -v 'unexplained=0$' | head")
    return rc


if __name__ == "__main__":
    sys.exit(main())
