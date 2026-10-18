#!/usr/bin/env python3
"""tests/memfn/pr11_front.py -- PR-11's CONTROL, the shared core (R17-b' B3a,
lane b3a; docs/design/memfn/r17b_prime.md rev 3 §3.1 row B3a, §4.6's HYB_PF
row, memfn/docs/requests.md R-21 PR-11).

THE CLAIM UNDER TEST. A VM hybrid whose DFA prefilter is COUNT-COLLAPSED
(`RX_VM_PREFILTER_LANG "count-collapsed"`: `X{m,n}` built as
`X{min(m,1),}`, src/ir/nfa.c) still enforces the pattern's whole necessary
set and its necessary run, because the collapse keeps every `rmin >= 1`
copy. That is why presence on HYB_PF is OPTIONAL (§4.6): an absent
necessary byte gives the front no candidate, so the budgeted VM never runs.

THE EVIDENCE SHARES NO SOURCE WITH THE REQ WALK. The walk's own output
(`--emit-facts`' `req_set` and `req_whole_run`) is only the list of CLAIMS;
each claim is judged by RUNNING THE EMITTED FRONT: the artifact is included
into a driver that calls its static `<prefix>_prefilter` directly, over a
subject the pattern MATCHES with the claimed byte (or every occurrence of
the claimed run) deleted. The front must find no candidate there. The
undeleted subject must yield one (the driver's positive control: a front
that rejected a matching subject would make every negative verdict vacuous).

Used by tests/memfn/run_pr11.sh (the witness table) and by
docs/design/memfn/r17b_prime/b3a/pr11_census.py (the census over the
collapsed hybrids of the corpus, bench and rwquest populations).
"""
import os
import re
import subprocess

PREFIX = "pr11"
DRIVER = r'''
#include "a.c"
#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv)
{
    FILE *f = fopen(argv[1], "rb");
    unsigned char hdr[4];
    if (!f) return 2;
    while (fread(hdr, 1, 4, f) == 4) {
        size_t n = (size_t)hdr[0] | (size_t)hdr[1] << 8 | (size_t)hdr[2] << 16 |
                   (size_t)hdr[3] << 24;
        unsigned char *s = malloc(n ? n : 1);
        if (n && fread(s, 1, n, f) != n) return 3;
        ptrdiff_t window[1][2];
        printf("%d\n", pr11_prefilter(s, n, 0, window) == 1);
        free(s);
    }
    return 0;
}
'''


HARVEST = r'''
#include "a.c"
#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv)
{
    int want = atoi(argv[1]);
    for (int a = 2; a < argc && want > 0; a++) {
        FILE *f = fopen(argv[a], "rb");
        if (!f) continue;
        size_t cap = 4u << 20;
        unsigned char *s = malloc(cap);
        size_t n = fread(s, 1, cap, f);
        fclose(f);
        size_t from = 0;
        while (want > 0 && from <= n) {
            ptrdiff_t caps[PR11_NCAPS][2];
            if (pr11_search(s, n, from, caps) != 1) break;
            printf("%d %td %td\n", a, caps[0][0], caps[0][1]);
            want--;
            from = (size_t)caps[0][1] > from ? (size_t)caps[0][1] : from + 1;
        }
        free(s);
    }
    return 0;
}
'''


def harvest(c, texts, work, cc="gcc", want=8, ctx=64, timeout=300):
    """MATCHING subjects for a pattern with none of its own: the artifact's
    own full matcher (`<prefix>_search`, whose answers the corpus holds to
    its oracles elsewhere) finds up to `want` matches in the subject TEXTS,
    and each match with `ctx` bytes of its real context on either side is a
    subject the pattern matches."""
    d = os.path.join(work, "harv.c")
    with open(d, "w") as fh:
        fh.write(HARVEST)
    exe = os.path.join(work, "harv")
    r = subprocess.run([cc, "-O1", "-w", "-std=gnu11", "-I", work, "-o", exe, d],
                       capture_output=True, timeout=timeout)
    if r.returncode != 0:
        return []
    r = subprocess.run([exe, str(want)] + list(texts), capture_output=True, timeout=timeout)
    out = []
    for ln in r.stdout.decode().splitlines():
        a, st, en = (int(x) for x in ln.split())
        with open(texts[a - 2], "rb") as fh:
            fh.seek(max(0, st - ctx))
            out.append(fh.read(en + ctx - max(0, st - ctx)))
    return out


def compile_front(pcrec, flags, pat, work, timeout=120):
    """Compile `pat`; return the artifact's path when its prefilter is
    count-collapsed, None when it is not (or the compile refused)."""
    os.makedirs(work, exist_ok=True)
    c = os.path.join(work, "a.c")
    argv = [pcrec, "-p", PREFIX, "--features", "all"] + flags + ["-o", c, "--pattern", pat]
    try:
        r = subprocess.run(argv, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None
    with open(c, "rb") as fh:
        text = fh.read()
    if b'_VM_PREFILTER_LANG "count-collapsed"' not in text:
        return None
    if b"static int %s_prefilter(" % PREFIX.encode() not in text:
        return None
    return c


def claims(pcrec, flags, pat, timeout=120):
    """The req walk's claims: the necessary set's members (bytes) and the
    whole run (bytes, mask or None), read from `--emit-facts`."""
    r = subprocess.run([pcrec, "--features", "all"] + flags + ["--emit-facts", "--pattern", pat],
                       capture_output=True, timeout=timeout)
    members, run = [], None
    for ln in r.stdout.decode("utf-8", "replace").splitlines():
        c = ln.split("\t")
        if len(c) < 7 or c[0].startswith("#"):
            continue
        if c[1] == "req_set" and c[4] == "derived" and c[6] not in ("", "none"):
            members = [int(x) for x in c[6].split(",") if x]
        if c[1] == "req_whole_run" and c[4] == "derived" and c[6] not in ("", "none"):
            v = c[6]
            m = None
            if "/" in v:
                v, mk = v.split("/", 1)
                m = bytes.fromhex(mk)
            if "@" in v:
                v = v.split("@", 1)[0]
            run = (bytes.fromhex(v), m)
    return members, run


def _run_hits(s, run):
    """Start offsets where the (possibly masked) run occurs in s."""
    bts, mask = run
    L = len(bts)
    out = []
    for i in range(len(s) - L + 1):
        ok = True
        for j in range(L):
            k = mask[j] if mask else 0xFF
            if (s[i + j] & k) != bts[j]:
                ok = False
                break
        if ok:
            out.append(i)
    return out


def derive(subject, members, run):
    """(label, derived subject) pairs, each lacking one claim entirely."""
    out = []
    for b in members:
        if b in subject:
            out.append(("member:%d" % b, bytes(x for x in subject if x != b)))
    if run:
        s = bytearray(subject)
        if _run_hits(bytes(s), run):
            for _ in range(len(s) + 1):
                hits = _run_hits(bytes(s), run)
                if not hits:
                    break
                del s[hits[0]]
            out.append(("run", bytes(s)))
    return out


def run_front(c, subjects, work, cc="gcc", timeout=120):
    """Prefilter verdicts (1 = a candidate) for each subject, or None when
    the driver does not build or run."""
    d = os.path.join(work, "drv.c")
    with open(d, "w") as fh:
        fh.write(DRIVER)
    exe = os.path.join(work, "drv")
    r = subprocess.run([cc, "-O0", "-w", "-std=gnu11", "-I", work, "-o", exe, d],
                       capture_output=True, timeout=timeout)
    if r.returncode != 0:
        return None
    blob = os.path.join(work, "subj.bin")
    with open(blob, "wb") as fh:
        for s in subjects:
            fh.write(len(s).to_bytes(4, "little"))
            fh.write(s)
    r = subprocess.run([exe, blob], capture_output=True, timeout=timeout)
    if r.returncode != 0:
        return None
    v = [int(x) for x in r.stdout.decode().split()]
    return v if len(v) == len(subjects) else None


def check(pcrec, flags, pat, matching, work, cc="gcc"):
    """One collapsed hybrid over its matching subjects. Returns (status,
    detail): status 'not-collapsed', 'no-claims', 'no-subject', 'driver',
    'vacuous' (the front rejected a matching subject), 'ok' (every derived
    subject rejected) or 'enforcement' (a derived subject lacking a claim
    got a candidate: the claim is FALSE for this front). detail counts."""
    c = compile_front(pcrec, flags, pat, work)
    if not c:
        return "not-collapsed", {}
    members, run = claims(pcrec, flags, pat)
    if not members and not run:
        return "no-claims", {}
    subs = [s for s in matching if s is not None]
    derived = []
    for s in subs:
        derived += [(lab, d) for lab, d in derive(s, members, run)]
    if not subs or not derived:
        return "no-subject", {"subjects": len(subs)}
    v = run_front(c, subs + [d for _, d in derived], work, cc)
    if v is None:
        return "driver", {}
    if not all(v[:len(subs)]):
        return "vacuous", {"subjects": len(subs)}
    bad = [lab for (lab, _), got in zip(derived, v[len(subs):]) if got]
    det = {"subjects": len(subs), "derived": len(derived), "accepted": bad[:5]}
    return ("enforcement" if bad else "ok"), det
