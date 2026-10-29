#!/usr/bin/env python3
"""vmopt.py -- lane vmbc's HAND-TWIN GENERATOR (scratch, not a product).

Reads an emitted VM artifact (gcc-dialect C from pcrec, D183 base) and rewrites
its matcher body with the B/C rules of docs/dev/lanes/vmbc_report.md:

  C-move   the linked call's restore moves from the shared region exit to each
           call site's return label (it reads the call frame through a local
           set at the exit), so each site can keep its own restore set;
  DSE      a slot write is dead if no path reads the slot before the next write
           (a PUSH reads live-in(resume label); accept reads the capture slots;
           a region exit reads live-in of its callers' return labels);
           a dead restore at a return label also drops the site's snapshot
           entry (renumbered), the snapshot being the restore's storage;
  COPY     a write of a value the slot provably already holds is removed
           (available copies: SET(a, slot_values[b]) makes a == b);
  TRAIL    a write needs no trail entry when its slot is already trailed in
           the current segment (must-analysis; a push starts a segment, a
           resume continues the pushing segment, a cut only merges).

Modes: -m B (DSE+COPY+TRAIL, no C-move), -m C (C-move + DSE of restores and
snapshots only), -m BC (all), -m none (parse only; stats).
Usage: vmopt.py -m MODE IN.c OUT.c   (stats on stderr, one line)
Anything it does not recognise makes it BAIL for that function (no rewrite):
the twin is conservative by refusal, not by guess.
"""
import re
import sys


DEBUG = False


class Bail(Exception):
    pass


def parse_defines(text, up):
    slots = {}
    for m in re.finditer(r"^#define %s_SLOT_(\w+)\s+(\d+)\s*$" % up, text, re.M):
        slots["%s_SLOT_%s" % (up, m.group(1))] = int(m.group(2))
    nslots = int(re.search(r"^#define %s_NSLOTS (\d+)" % up, text, re.M).group(1))
    m = re.search(r"^#define %s_NCAPS (\d+)" % up, text, re.M)
    if m:
        ncaps = int(m.group(1))
    else:
        gs = [int(x) for x in re.findall(r"^#define %s_SLOT_GROUP(\d+)_START" % up, text, re.M)]
        if not gs and "%s_SLOT_WHOLE_START" % up not in text:
            raise Bail("no capture layout")
        ncaps = max(gs, default=0) + 1
    return slots, nslots, ncaps


def slot_of(tok, slots):
    tok = tok.strip()
    if tok in slots:
        return slots[tok]
    if re.fullmatch(r"\d+", tok):
        return int(tok)
    raise Bail("unresolved slot %r" % tok)


def split_set(s):
    # "RX_SET(A, EXPR);" -> (A, EXPR)
    inner = s[s.index("(") + 1: s.rindex(")")]
    a, e = inner.split(",", 1)
    return a.strip(), e.strip()


def reads_of(expr, slots, allmask):
    m = 0
    for x in re.findall(r"slot_values\[([^\]]+)\]", expr):
        x = x.strip()
        if x.startswith("(") and x.endswith(")"):
            x = x[1:-1]
        try:
            m |= 1 << slot_of(x, slots)
        except Bail:
            return allmask
    return m


class Fn:
    pass


def analyse(text, p, up, mode, stats):
    useU = mode.endswith("U")
    if useU:
        mode = mode[:-1]
    slots, nslots, ncaps = parse_defines(text, up)
    ALL = (1 << nslots) - 1
    CAP = (1 << (2 * ncaps)) - 1
    lines = text.split("\n")
    # the matcher: the function holding `<p>_match_anchored(` definition
    start = None
    for i, ln in enumerate(lines):
        if re.match(r"^static .*\bptrdiff_t %s_match_anchored\(const" % p, ln):
            start = i
            break
    if start is None:
        raise Bail("no matcher")
    j = start
    while lines[j] != "{":
        j += 1
    k = j + 1
    while lines[k] != "}":
        k += 1
    b0, b1 = j + 1, k          # body = lines[b0:b1]
    fail_at = None
    for i in range(b0, b1):
        if re.match(r"^%s_fail:" % p, lines[i]):
            fail_at = i
            break
    if fail_at is None:
        raise Bail("no fail label")
    for i in range(fail_at, b1):
        if re.match(r"^%s_L\d+:" % p, lines[i]):
            raise Bail("label after fail")
    body = list(range(b0, fail_at))
    lab = {}
    for i in body:
        m = re.match(r"^%s_(L\d+|accept):" % p, lines[i])
        if m:
            lab[m.group(1)] = i
    # ---- classify every line
    N = len(lines)
    kind = {}
    info = {}
    depth_loop = 0
    for i in body:
        s = lines[i].strip()
        if re.match(r"^%s_(L\d+|accept):" % p, lines[i]):
            kind[i] = "label"
            continue
        if re.match(r"^(for|while)\b", s):
            depth_loop += 1
        if depth_loop and "_SET(" in s:
            raise Bail("SET in a C loop")
        if depth_loop and s == "}":
            depth_loop -= 1
        if re.fullmatch(r"%s_SET\(.*\);" % up, s) and s.count("%s_SET(" % up) == 1:
            a, e = split_set(s)
            info[i] = (slot_of(a, slots), e)
            kind[i] = "set"
            continue
        if "_SET(" in s:
            raise Bail("SET in an unusual line: %s" % s)
        if re.search(r"slot_values\[[^\]]*\]\s*=[^=]", s):
            raise Bail("direct slot write: %s" % s)
        if re.fullmatch(r"%s_PUSH\(&&%s_(L\d+), .*\);" % (up, p), s):
            kind[i] = "push"
            info[i] = re.match(r"%s_PUSH\(&&%s_(L\d+)" % (up, p), s).group(1)
            continue
        if re.fullmatch(r"%s_CALL\(&&%s_(L\d+), .*\);" % (up, p), s):
            kind[i] = "call"
            info[i] = re.match(r"%s_CALL\(&&%s_(L\d+)" % (up, p), s).group(1)
            continue
        if "_PUSH(" in s or "_CALL(" in s:
            raise Bail("unusual push/call: %s" % s)
        if re.search(r"goto \*run->resume_stack\[\w+\]\.call_ret", s):
            kind[i] = "exit"
            continue
        if "goto *" in s:
            raise Bail("other indirect goto: %s" % s)
        kind[i] = "other"
    # ---- successors (line graph)
    succ = {i: [] for i in body}
    pushs = {}      # line -> resume label line
    for idx, i in enumerate(body):
        s = lines[i].strip()
        nxt = body[idx + 1] if idx + 1 < len(body) else None
        if kind[i] == "exit":
            continue        # filled after regions are known
        for x in re.findall(r"goto %s_(L\d+|accept)\b" % p, s):
            succ[i].append(lab[x])
        if kind[i] == "push":
            pushs[i] = lab[info[i]]
        uncond = s.startswith("goto ") or s.startswith("return ") or s.startswith("return;")
        if not uncond and nxt is not None:
            succ[i].append(nxt)
    # ---- calls and regions
    calls = []   # (call line, ret label line, snapshot lines, entry label line)
    for i in body:
        if kind[i] != "call":
            continue
        idx = body.index(i)
        snap = []
        q = idx + 1
        while kind[body[q]] == "set":
            snap.append(body[q])
            q += 1
        while re.fullmatch(r"%s_TRAIL_CHECK\(\);" % up, lines[body[q]].strip()):
            q += 1
        m = re.fullmatch(r"goto %s_(L\d+);" % p, lines[body[q]].strip())
        if not m:
            raise Bail("call without goto entry")
        for sl in snap:
            a, e = split_set(lines[sl].strip())
            if e != "slot_values[%s]" % a:
                raise Bail("snapshot not a self-write")
        calls.append((i, lab[info[i]], snap, lab[m.group(1)]))
    entries = sorted(set(c[3] for c in calls))
    exits = [i for i in body if kind[i] == "exit"]
    ret_lines = set(c[1] for c in calls)
    region_of_exit = {}
    call_after = {c[0]: c[1] for c in calls}
    for e in entries:
        seen = set()
        st = [e]
        while st:
            v = st.pop()
            if v in seen:
                continue
            seen.add(v)
            if kind.get(v) == "exit":
                if v in region_of_exit and region_of_exit[v] != e:
                    raise Bail("exit reached from two regions")
                region_of_exit[v] = e
                continue
            if kind.get(v) == "call":
                st.append(call_after[v])
                continue
            st.extend(succ[v])
            if v in pushs:
                st.append(pushs[v])
    for x in exits:
        if x not in region_of_exit:
            raise Bail("exit with no region")
        succ[x] = [c[1] for c in calls if c[3] == region_of_exit[x]]
    # the restore lines at each exit: the run of SETs reading trail_mark + j
    restores = {}   # exit line -> list of (line, slot, j)
    for x in exits:
        idx = body.index(x)
        q = idx - 1
        rs = []
        while q >= 0 and (kind[body[q]] != "label"):
            ln = lines[body[q]].strip()
            if kind[body[q]] == "set":
                m = re.search(r"run->trail\[run->resume_stack\[run->call_top\]\.trail_mark \+ (\d+)\]\.saved_value", ln)
                if m:
                    rs.append((body[q], info[body[q]][0], int(m.group(1))))
            q -= 1
        rs.reverse()
        restores[x] = rs
    # W per region must agree with every call site's snapshot
    W = {}
    for x in exits:
        w = [s for (_, s, _) in sorted(restores[x], key=lambda t: t[2])]
        e = region_of_exit[x]
        if e in W and W[e] != w:
            raise Bail("two exits disagree on W")
        W[e] = w
    for (ci, r, snap, e) in calls:
        if [info[s][0] for s in snap] != W.get(e, []):
            raise Bail("snapshot != W")
    stats["calls"] = len(calls)
    stats["W"] = sum(len(W[e]) for e in W)
    stats["sets"] = sum(1 for i in body if kind[i] == "set")

    # ================= the transform state =================
    removed = set()          # set lines deleted
    untrailed = set()        # set lines written without a trail entry
    pinned = set()           # snapshot sets (trail storage)
    for c in calls:
        pinned.update(c[2])
    # C-move: per call site restore list at its return label (virtual lines)
    site_keep = {c[0]: list(range(len(W.get(c[3], [])))) for c in calls}
    cmove = mode in ("C", "BC", "BCd") and calls
    exit_restore_lines = set(ln for x in exits for (ln, _, _) in restores[x])
    moved = set()
    if cmove:
        moved = set(exit_restore_lines)
        removed.update(moved)
    elif mode in ("B", "Bd", "Bt"):
        pinned.update(exit_restore_lines)   # B alone leaves the linkage as it is
    doB = mode in ("B", "BC", "Bd", "BCd")
    # virtual restore nodes: for the analyses, a return label R of call c gets
    # restores of W[j] for j in site_keep[c] (writes, reading no slot)
    def ret_writes(ci):
        e = [c for c in calls if c[0] == ci][0][3]
        return [W[e][j] for j in site_keep[ci]]
    ret_of = {c[1]: c[0] for c in calls}
    snaplines = set(sl for c in calls for sl in c[2])
    call_ret = {c[0]: c[1] for c in calls}
    entry_of = {c[0]: c[3] for c in calls}
    ret_entry = {c[1]: c[3] for c in calls}
    Wmask = {e: sum(1 << s for s in W[e]) for e in W}
    after_ret = {}
    for c in calls:
        q = body.index(c[1]) + 1
        after_ret[c[0]] = body[q]

    def live_analysis():
        live_in = {i: 0 for i in body}
        changed = True
        order = list(reversed(body))
        while changed:
            changed = False
            for i in order:
                if (i in removed and i not in snaplines) or (cmove and i in snaplines):
                    out = 0
                    for u in succ[i]:
                        out |= live_in[u]
                    v = out
                else:
                    out = 0
                    for u in succ[i]:
                        out |= live_in[u]
                    k_ = kind[i]
                    s = lines[i].strip()
                    if k_ == "set":
                        a, e = info[i]
                        v = (out & ~(1 << a)) | reads_of(e, slots, ALL)
                        if i in pinned:
                            v |= (1 << a)
                    elif k_ == "push":
                        v = out | live_in[pushs[i]] | reads_of(s, slots, ALL)
                    elif k_ == "label" and i in ret_of and cmove:
                        # THE MODEL: every return restores ALL of W (the stock
                        # semantics), and a value of W live after the return
                        # flows AROUND the callee (through the trail) to the
                        # call site; see the report's C soundness argument
                        v = out & ~Wmask[ret_entry[i]]
                    elif k_ == "call" and cmove:
                        v = out | (live_in[after_ret[i]] & Wmask[entry_of[i]])
                    elif s.startswith("return (ptrdiff_t)(scan_position"):
                        v = CAP
                    elif s.startswith("return"):
                        v = 0
                    else:
                        v = out | reads_of(s, slots, ALL)
                        m = re.search(r"%s_CUT\((\d+)\)" % up, s)
                        if m:
                            v |= 1 << int(m.group(1))
                        if re.search(r"%s_\w+\(" % up, s) and not re.search(
                                r"%s_(CUT|CHARGE_WORK|PRUNE_TOO_SHORT|PRUNE_CLAMP_SPAN|TRAIL_CHECK)\(" % up, s):
                            if not re.search(r"%s_(CALL|PUSH)\(" % up, s):
                                v |= ALL   # unknown macro: assume it reads everything
                if v != live_in[i]:
                    live_in[i] = v
                    changed = True
        return live_in

    def live_out_of(i, live_in):
        out = 0
        for u in succ[i]:
            out |= live_in[u]
        return out

    def dse(live_in):
        n = 0
        for i in body:
            if not doB:
                break
            if kind[i] != "set" or i in removed or i in pinned:
                continue
            a, e = info[i]
            if not (live_out_of(i, live_in) >> a) & 1:
                removed.add(i)
                n += 1
        return n

    def c_set(li):
        ch = False
        for (ci, r, snap, e) in calls:
            keep = [j for j in range(len(W[e])) if (li[after_ret[ci]] >> W[e][j]) & 1]
            if keep != site_keep[ci]:
                ch = True
                site_keep[ci] = keep
            for j, sl in enumerate(snap):
                if j in keep:
                    removed.discard(sl)
                    drop_snap.discard(sl)
                else:
                    removed.add(sl)
                    drop_snap.add(sl)
        return ch

    def c_fix():
        # LEAST fixpoint: a site keeps restore j only if W[j] is live after its
        # return label in the program whose snapshots are exactly the kept ones
        # (a snapshot reads its slot, so a greatest fixpoint keeps itself alive)
        for (ci, r, snap, e) in calls:
            site_keep[ci] = []
            for sl in snap:
                removed.add(sl)
                drop_snap.add(sl)
        while True:
            li = live_analysis()
            ch = False
            for (ci, r, snap, e) in calls:
                out = live_out_of(r, li)
                keep = [j for j in range(len(W[e])) if (out >> W[e][j]) & 1]
                if keep != site_keep[ci]:
                    ch = True
                    site_keep[ci] = keep
                    for j, sl in enumerate(snap):
                        if j in keep:
                            removed.discard(sl)
                            drop_snap.discard(sl)
            if not ch:
                return

    def copies():
        # forward must-analysis of equalities; returns removable identity sets
        UNIV = None
        st_in = {i: UNIV for i in body}
        first = body[0]
        st_in[first] = frozenset()
        for c in calls:
            st_in[c[1]] = frozenset()
        changed = True
        def meet(a, b):
            if a is UNIV:
                return b
            if b is UNIV:
                return a
            return a & b
        while changed:
            changed = False
            for i in body:
                cur = st_in[i]
                if cur is UNIV:
                    continue
                f = set(cur)
                if kind[i] == "label" and i in ret_of:
                    f = set()
                if kind[i] == "set" and i not in removed:
                    a, e = info[i]
                    m = re.fullmatch(r"slot_values\[(\w+)\]", e)
                    if m and slot_of(m.group(1), slots) == a:
                        pass
                    else:
                        f = {pr for pr in f if a not in pr}
                        if m:
                            bslot = slot_of(m.group(1), slots)
                            f.add(frozenset((a, bslot)))
                outs = list(succ[i])
                if i in pushs:
                    outs.append(pushs[i])
                ff = frozenset(f)
                for u in outs:
                    if u in ret_lines and kind.get(u) == "label":
                        continue  # return labels start empty
                    nv = meet(st_in[u], ff)
                    if nv != st_in[u]:
                        st_in[u] = nv
                        changed = True
        rem = []
        for i in body:
            if kind[i] != "set" or i in removed or i in pinned:
                continue
            a, e = info[i]
            m = re.fullmatch(r"slot_values\[(\w+)\]", e)
            if not m:
                continue
            bslot = slot_of(m.group(1), slots)
            f = st_in[i]
            if f is None:
                continue
            if bslot == a or frozenset((a, bslot)) in f:
                rem.append(i)
        return rem

    drop_snap = set()
    if mode != "none":
        it = 0
        while True:
            it += 1
            before = {k: list(v) for k, v in site_keep.items()}
            li = live_analysis()
            if cmove:
                c_set(li)
            n = dse(li)
            if site_keep != before:
                n += 1
            if mode in ("B", "BC", "Bd", "BCd"):
                rem = copies()
                for i in rem:
                    removed.add(i)
                n += len(rem)
            if n == 0 or it > 50:
                break
        # TRAIL must-analysis (B only)
        if mode in ("B", "BC", "Bt"):
            UNIV = None
            st_in = {i: UNIV for i in body}
            st_in[body[0]] = 0
            for c in calls:
                st_in[c[1]] = 0
            changed = True
            while changed:
                changed = False
                for i in body:
                    cur = st_in[i]
                    if cur is UNIV:
                        continue
                    f = cur
                    if kind[i] == "label" and i in ret_of:
                        f = 0
                        if cmove:
                            for sl in ret_writes(ret_of[i]):
                                f |= 1 << sl   # the moved restores: trailed
                    if kind[i] == "set" and i not in removed and i not in drop_snap:
                        a, e = info[i]
                        f |= 1 << a
                    if kind[i] in ("push", "call"):
                        after = 0
                    else:
                        after = f
                    for u in succ[i]:
                        if u in ret_lines and kind.get(u) == "label":
                            continue
                        nv = after if st_in[u] is UNIV else (st_in[u] & after)
                        if nv != st_in[u]:
                            st_in[u] = nv
                            changed = True
                    if i in pushs:
                        u = pushs[i]
                        nv = f if st_in[u] is UNIV else (st_in[u] & f)
                        if nv != st_in[u]:
                            st_in[u] = nv
                            changed = True
            for i in body:
                if kind[i] != "set" or i in removed or i in pinned or i in drop_snap:
                    continue
                a, e = info[i]
                cur = st_in[i] or 0
                if (cur >> a) & 1:
                    untrailed.add(i)
            # the moved restores themselves stay trailed (return label = new segment)
        # ===== lane trailgen: UNDO-DEAD (a write's trail entry is needed only if
        # the OLD value is live where an unwind can deliver it: the resume label
        # of a frame that may be live at the write, or the next attempt's entry)
        if useU:
            li = live_analysis()
            mayf = {i: None for i in body}
            mayf[body[0]] = frozenset()
            changed = True
            while changed:
                changed = False
                for i in body:
                    cur = mayf[i]
                    if cur is None:
                        continue
                    outs = [(u, cur) for u in succ[i]]
                    if kind[i] == "push":
                        outs = [(u, cur | {pushs[i]}) for u in succ[i]] + [(pushs[i], cur)]
                    for u, val in outs:
                        nv = val if mayf[u] is None else (mayf[u] | val)
                        if nv != mayf[u]:
                            mayf[u] = nv
                            changed = True
            nU = 0
            for i in body:
                if kind[i] != "set" or i in removed or i in pinned or i in drop_snap or i in untrailed:
                    continue
                a, e = info[i]
                fr = mayf[i]
                if fr is None:
                    continue           # unreachable line: leave it alone
                need = (li[body[0]] >> a) & 1
                for L in fr:
                    if (li[L] >> a) & 1:
                        need = 1
                        break
                if not need:
                    untrailed.add(i)
                    nU += 1
            stats["undo_dead"] = nU
        # ================= rewrite =================
        out = list(lines)
        nsetdel = 0
        for i in removed:
            if i in moved or i in drop_snap:
                continue
            out[i] = "    /* vmbc: dead */"
            nsetdel += 1
        for i in drop_snap:
            out[i] = "    /* vmbc: snapshot not needed */"
        for i in untrailed:
            a, e = info[i]
            out[i] = lines[i].replace("%s_SET(" % up, "%s_SETU(" % up, 1)
        if cmove:
            for (ci, r, snap, e) in calls:
                keep = site_keep[ci]
                # renumber the kept snapshot: they stay in order, so position = rank
                rs = []
                for rank, j in enumerate(keep):
                    s = W[e][j]
                    rs.append("    %s_SET(%d, run->trail[run->resume_stack[%s_ret_frame].trail_mark + %d].saved_value);"
                              % (up, s, p, rank))
                out[r] = lines[r] + ("\n" + "\n".join(rs) if rs else "")
            for x in exits:
                for (ln, s, j) in restores[x]:
                    out[ln] = "    /* vmbc: restore moved to the return label */"
                out[x] = lines[x].replace("goto *", "%s_ret_frame = %s_call_frame; goto *" % (p, p))
            # declare the local
            for i in range(b0, b1):
                if "size_t %s_trail_gc_at" % p in lines[i] or "size_t scan_position" in lines[i]:
                    out[i] = lines[i] + "\n    size_t %s_ret_frame = 0; (void)%s_ret_frame;" % (p, p)
                    break
        stats["dead"] = nsetdel
        stats["untrailed"] = len(untrailed)
        stats["snap_dropped"] = len(drop_snap)
        if cmove and DEBUG:
            def why(start, a):
                from collections import deque
                prev = {start: None}
                dq = deque([start])
                while dq:
                    v = dq.popleft()
                    s = lines[v].strip()
                    rd = reads_of(s, slots, ALL) if kind[v] != "set" else reads_of(info[v][1], slots, ALL)
                    m = re.search(r"%s_CUT\((\d+)\)" % up, s)
                    if m: rd |= 1 << int(m.group(1))
                    if v != start and v not in removed and (rd >> a) & 1:
                        path = []
                        while v is not None:
                            path.append(v + 1)
                            v = prev[v]
                        return list(reversed(path))
                    if v != start and kind[v] == "set" and v not in removed and info[v][0] == a:
                        continue
                    nx = list(succ[v]) + ([pushs[v]] if v in pushs else [])
                    if v in ret_of and v != start:
                        if a in ret_writes(ret_of[v]):
                            continue
                    for u in nx:
                        if u not in prev:
                            prev[u] = v
                            dq.append(u)
                return None
            for (ci, r, snap, e) in calls:
                for j in site_keep[ci]:
                    sys.stderr.write("   why %d slot %d: %s\n" % (ci + 1, W[e][j], (why(r, W[e][j]) or [])[-8:]))
            inv = {v: k for k, v in slots.items()}
            for (ci, r, snap, e) in calls:
                sys.stderr.write("  site line %d keeps %s\n" % (ci + 1, [inv.get(W[e][j], W[e][j]) for j in site_keep[ci]]))
        stats["restores_kept"] = sum(len(site_keep[c[0]]) for c in calls) if cmove else stats["W"]
        txt = "\n".join(out)
        # the untrailed write macro, beside RX_SET
        txt = txt.replace("#define %s_PUSH(" % up,
                          "#define %s_SETU(slot_, v_) do { slot_values[(slot_)] = (v_); } while (0)\n#define %s_PUSH(" % (up, up), 1)
        return txt
    return text


def main(argv):
    global DEBUG
    mode = "BC"
    if argv[:1] == ["-d"]:
        DEBUG = True
        argv = argv[1:]
    if argv[:1] == ["-m"]:
        mode = argv[1]
        argv = argv[2:]
    src, dst = argv
    text = open(src, encoding="latin-1").read()
    m = re.search(r"^static .*\bptrdiff_t (\w+)_match_anchored\(const", text, re.M)
    p = m.group(1)
    up = p.upper()
    stats = {}
    try:
        out = analyse(text, p, up, mode, stats)
        stats["status"] = "ok"
    except Bail as e:
        out = text
        stats["status"] = "bail: %s" % e
    open(dst, "w", encoding="latin-1").write(out)
    sys.stderr.write("vmopt %s %s %s\n" % (mode, src, " ".join("%s=%s" % kv for kv in stats.items())))


if __name__ == "__main__":
    main(sys.argv[1:])
