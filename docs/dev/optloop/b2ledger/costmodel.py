#!/usr/bin/env python3
"""Exact, clock-free accounting of the emitted pre-check's work under the
bench's find-all throughput regime, for the BEFORE (b1885a83's predecessor
8d716693, one-byte check) and AFTER (b1885a83, run scan loop) shapes.

The emitted run loop is, verbatim from the artifact:
    rp_pos = search_from;
    for (;;) {
        rp_q = memchr(subject + rp_pos, SCAN, subject_length - rp_pos);
        if (!rp_q) return 0;
        rp_c = rp_q - subject;
        if (rp_c + L <= subject_length && !memcmp(subject + rp_c, RUN, L)) break;
        rp_pos = rp_c + 1;
    }
so it makes ONE memchr CALL per occurrence of SCAN until the RUN is found.
The batch-1 one-byte check made exactly ONE memchr call per invocation.
"""
import os, re, sys
SCR = os.environ["SCR"]
subs = [open(f"{SCR}/subj/{k}.bin","rb").read() for k in ("t-64k","t-256k","t-1m")]

def findall_starts(sub, pat_re):
    """find-all call positions, the bench's own formula pos = max(end, pos+1)."""
    out, pos = [], 0
    n = len(sub)
    while pos <= n:
        m = pat_re.search(sub, pos)
        out.append(pos)
        if not m: break
        pos = max(m.end(), pos + 1)
    return out, sum(1 for _ in [])

def account(name, pat_re, before_byte, after_scan, after_run, run_at):
    tot_calls_b = tot_scan_b = 0
    tot_calls_a = tot_scan_a = tot_memcmp = 0
    nmatch = 0
    for sub in subs:
        n = len(sub); pos = 0
        while pos <= n:
            # --- BEFORE: one memchr for before_byte over [pos, n)
            if before_byte is not None:
                q = sub.find(bytes([before_byte]), pos)
                tot_calls_b += 1
                tot_scan_b += (n - pos) if q < 0 else (q - pos + 1)
            # --- AFTER: the run scan loop
            if after_run is not None:
                rp = pos
                while True:
                    q = sub.find(bytes([after_scan]), rp)
                    tot_calls_a += 1
                    if q < 0:
                        tot_scan_a += n - rp; break
                    tot_scan_a += q - rp + 1
                    start = q - run_at
                    tot_memcmp += 1
                    if start >= 0 and start + len(after_run) <= n and \
                       sub[start:start+len(after_run)] == after_run:
                        break
                    rp = q + 1
                    if rp >= n: break
            else:
                q = sub.find(bytes([after_scan]), pos)
                tot_calls_a += 1
                tot_scan_a += (n - pos) if q < 0 else (q - pos + 1)
            m = pat_re.search(sub, pos)
            if not m: break
            nmatch += 1
            pos = max(m.end(), pos + 1)
    return dict(name=name, matches=nmatch,
                before_calls=tot_calls_b, before_scan=tot_scan_b,
                after_calls=tot_calls_a, after_scan=tot_scan_a, memcmp=tot_memcmp)

CASES = [
  # name, python regex (find-all semantics), BEFORE byte, AFTER scan byte, run, run_at
  ("router-prefix-order", rb"/user|/users", 114, 47, b"/user", 0),
  ("keyword-prefix-order", rb"in|instanceof", 110, 110, b"in", 1),
  ("logparse-atomic", rb"(?s)^(?:(?:kern|user|mail|daemon|auth|syslog|cron)\.(?:emerg|alert|crit|err|warning|notice|info|debug)): (.*)$", 32, 58, b": ", 0),
  ("wild-validator-email-owasp", rb"(?s)^[a-zA-Z0-9_+&*-]+(?:\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", 46, 64, None, 0),
  ("tag-pair-match", rb"<([a-zA-Z][\w:-]*)(?:\s[^>]*)?>.*?</\1\s*>", 62, 60, b"</", 0),
  ("wild-secrets-github-pat", rb"\b(github_pat_[0-9a-zA-Z_]{82})\b", 95, 95, b"hub_pat_", 3),
]
FLOOR = 23113.3/1376256.0   # ns per byte, cycle1 §0's measured floor rate
print(f"{'pattern':30s} {'match':>6s} {'B:calls':>8s} {'B:scan':>9s} {'A:calls':>8s} {'A:scan':>9s} {'call amp':>9s}")
rows=[]
for name, rx, bb, sc, run, at in CASES:
    r = account(name, re.compile(rx), bb, sc, run, at)
    amp = r['after_calls']/max(r['before_calls'],1)
    rows.append((r,amp))
    print(f"{name:30s} {r['matches']:6d} {r['before_calls']:8d} {r['before_scan']:9d} "
          f"{r['after_calls']:8d} {r['after_scan']:9d} {amp:8.1f}x")
print()
print("PREDICTED added cost = (A:calls - B:calls) * c_call + (A:scan - B:scan) * floor_rate")
print(f"floor rate = {FLOOR:.6f} ns/byte")
for r,amp in rows:
    dcalls = r['after_calls']-r['before_calls']; dscan = r['after_scan']-r['before_scan']
    for c in (8.3,):
        print(f"  {r['name']:30s} dcalls={dcalls:8d} dscan={dscan:9d} "
              f"-> predicted {dcalls*c + dscan*FLOOR:12.1f} ns  (c_call={c} ns)")
