# span_cards/slot/est.py — THE SLOT'S ESTIMATOR: span_cards.md §3.4-§3.5 (docs/spec/measures.md §3.4-§3.5) over
# the window's cells, the gates, the NULL rule, the bimodal test, drift, the floor and the first-match outcome
# table; and the DRAFT SET writer (§3.8 step 1). Its arithmetic is drill.py's (the same text implemented
# literally; drill.py stays the design's evidence). The recompute (S2e, tests/knowledge/) is written from the
# spec and shares nothing with this file.
#   python3 -I est.py rows     RUNDIR           the rows and verdicts, one line each, and the outcome
#   python3 -I est.py draft    RUNDIR OUT.tsv   the draft set (format 2), digest by tests/knowledge/ks_ref.py;
#                                               a REFUSED outcome writes NO draft (exit 3, r9 G5/CONTRACT-6)
#   python3 -I est.py selftest SCRATCH          the input cross-checks over synthetic run directories (r9 G3)
# RUNDIR holds the FINALIZED run_record.tsv (record.py), cells.J<j>.tsv per ran timing job (format 2's cell
# columns under a `#run_id` line) and <job>/cell_text.tsv (link.py). THE RECORD IS THE INPUT (r9 G3): the plan,
# the floor and which jobs ran are its sections, never a live plan.py rebuild and never "a cells file exists";
# and so are the CARD AND POLICY VALUES ([rev1.3 r9fc-FIX-1]): the estimators, lengths, launches, rounds, units
# and gates come from the record's pinned `cards` and `policy` rows (plan.parse_cards over them), never from
# memfn/data's live tables, so a table edited after the run never moves its verdict.
# Refused inputs exit 2: a cells file of a never-ran job, a ran job missing a planned cell, a cells file of
# another run, an id whose fields disagree with its columns, a delta cell naming another base than the family
# rule's (plan.base_of), a ran job with no cell texts; [rev1.5 R15-1] a verify row's timed code whose two readings
# of the FUSED-COMPARE fact disagree, or whose fact differs between its launches, arm and twin; [rev1.5 r11-REV15-1]
# a launch executable that is not its job's manifest's, a manifest the record's pin disagrees with, a slot table
# whose stems are not the pinned plan's; [r11-REV15-10] a null base whose own code is fused.
# [rev1.5 R15-2] The draft names THIS estimator's commit (`# note est_commit`): a recompute applies that commit's
# rules. It is written only when every input of those rules is the commit's blob ([r11-REV15-6] est_inputs), and
# only when no TIMED path moved between the record's code_commit and it ([r11-REV15-7] NON_TIMED, an exclusion
# list), so scoring frozen cells with a later est never re-reads them under other code.
import hashlib, math, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import plan  # noqa: E402

TREE = plan.TREE
K_TRIM_E6, K_MED_E6 = 1723000, 210300      # measures.md §3.4¶16, §3.5¶6
# [rev1.4 R14-3, R14-4] the NOTE thresholds: they gate nothing (a note line in the record and the draft only)
NOTE_SPLIT_E6 = 5000       # a job's control: a gap over 0.5 % between two clusters of >= 2 launches: UNMEASURED DEFAULT (D149)
NOTE_BIMODAL_E6 = 100000   # a priced delta row: a gap over 10 % of its value, likewise: UNMEASURED DEFAULT (D149)
# [rev1.5 R15-1] THE FUSED-COMPARE BOUND: the tag a bound row carries in the draft, and the evidence its source names
FUSED_TAG = "fused-load-op"
FUSED_EVIDENCE = ("evidence: windows s2d-20261106 and s2d-20261107a, two null bases, both negative; the arms-only "
                  "fused/unfused step +0.14 wb (span_cards s2d2/analysis.md)")
# [rev1.5 R15-2, r11-REV15-7] WHICH TRACKED PATHS ARE TIMED, first match (a path ending `/` names a directory, one
# starting `*` a suffix): every tracked path is TIMED (its text may reach a timed binary or its subjects: libpcrec,
# the kit, build/pcrec's text pasted into the arm TUs, shared/, the vendored tables, the Makefile) unless a row
# below declares it not, with the reason
SLOT = "docs/design/memfn/span_cards/slot/"
NON_TIMED = (
    ("*.md",                       False, "prose: no build step reads a .md file"),
    (SLOT + "est.py",              False, "this estimator: it reads the run directory after the timing"),
    (SLOT + "record.py",           False, "the run record's writer: after each job, never inside one"),
    (SLOT + "sabotage.sh",         False, "plants into scratch copies of slot/ only"),
    (SLOT + "movers.py",           False, "S2e's census over the sets"),
    (SLOT + "j1_rule.py",          False, "J1's verdict from its cells (the record pins the verdict)"),
    (SLOT + "vcls.py",             False, "regenerates vcls.out, which is timed (the next row)"),
    (SLOT,                         True,  "the harness that renders, links, gates and times the cells (drv.c, gen.c, "
                                          "slot.h, link.py, art.py, plan.py, run.py, vcls.out, enter/, j1/, jobs/)"),
    ("docs/design/memfn/span_pick/census0.out", True, "plan.py's census: the keys and their sites"),
    ("docs/",                      False, "design, spec and process text"),
    ("tests/memfn/arm_fixtures.c", True,  "the fixture binary that renders every arm's site parts (link.py)"),
    ("tests/",                     False, "the suites: arm_fixtures.c (the row above) is the one tests/ file the slot builds"),
    ("memfn/data/policy.tsv",      False, "est's r_max_e6 and a `-` card's gate: the record pins both, no TU reads it"),
    ("memfn/docs/",                False, "the kit's ledger and journal"),
    ("scripts/",                   False, "box tooling (queue, lock, watchers): runs the jobs, reaches no binary"),
    ("tools/",                     False, "review tooling over the tree"),
    ("studies/",                   False, "adopted studies, never built by make"),
    ("examples/",                  False, "examples, built only by their own test"),
    ("analyze/",                   False, "pcrec-analyze, a separate binary linking nothing from libpcrec"),
    (".github/",                   False, "CI configuration"),
)

def timed(path):
    """[r11-REV15-7] is a tracked path TIMED (NON_TIMED's first matching row; no row: timed)"""
    for pat, t, _why in NON_TIMED:
        if pat.startswith("*") and path.endswith(pat[1:]) or pat.endswith("/") and path.startswith(pat) or path == pat:
            return t
    return True


class InputError(Exception):
    """a refused input (exit 2)"""

def rhafz(n, d):
    s = -1 if (n < 0) != (d < 0) else 1
    n, d = abs(n), abs(d)
    return s * ((n + d // 2) // d)

def isqrt_rn(N):
    r = math.isqrt(N)
    return r + 1 if N - r * r > r else r

def med(v):
    s = sorted(v)
    return s[(len(s) - 1) // 2]

def trim(x):
    m = med(x)
    k = max(range(len(x)), key=lambda i: (abs(x[i] - m), i))
    return [x[i] for i in range(len(x)) if i != k]

def sp2(x):
    w = trim(x)
    n = len(w)
    return rhafz(K_TRIM_E6 * (n * sum(t * t for t in w) - sum(w) ** 2), 10**6 * n * (n - 1))

def resolution(x):
    """[rev1.4 R14-2] a delta row's RESOLUTION r (measures.md §3.5¶3a): three standard errors of the median of its
    L anchored launch values, 3 x isqrt_rn(K_MED x sp2(x)) (§3.5¶6's scale for one median), in the row's unit"""
    return 3 * isqrt_rn(rhafz(K_MED_E6 * sp2(x), 10**6))

def r_max(rec):
    """[rev1.4 r10-REV14-2] (the cap on r, its source): the record's pinned policy row r_max_e6; a record planned
    before the row existed (windows s2d-20261106 and the second, both frozen at rev 1.4) pins none, and est then
    reads the LIVE table's row and says so in a `policy` line (rows) and a `# note` line (draft), never silently"""
    pol = plan.parse_policy(rec["policy"])
    if "r_max_e6" in pol:
        return pol["r_max_e6"], "pinned by the run record"
    live = plan.parse_policy(plan.table_rows(plan.POLICY))
    if "r_max_e6" not in live:
        raise InputError("neither the record's pinned policy nor the live %s holds r_max_e6" % plan.POLICY)
    return live["r_max_e6"], "NOT pinned by the run record (planned before the row): the live %s's, sha256 %s" % (
        os.path.relpath(plan.POLICY, TREE), plan.sha256(plan.POLICY))

# ---- [rev1.5 R15-1; r11] the FUSED-COMPARE fact, read off the TIMED code ------------------------------------------
# A verify class's compiled compare is FUSED when its timed function (`<stem>_time` in each launch executable,
# decoded over the symbol's own range, [r11-REV15-4]) holds EXACTLY ONE instruction that reads the subject
# ([r11-REV15-2]) and that instruction is a compare of the subject's memory (against an immediate or a register,
# [r11-REV15-3]): the load IS the compare, it writes FLAGS only, no register receives the loaded value and so no
# separate ALU op can act on it. READING THE SUBJECT ([r11-REV15-3]): a memory operand whose base or index register
# holds the subject pointer or a value made from it, register to register (the pointer arrives in %rdi, SysV's first
# argument; a register loaded FROM memory holds data, never the pointer); a call reads it too (the callee may), and
# so does a string instruction through %rsi/%rdi. Two readings, which must agree: fused_text() over objdump's
# mnemonics and operands (the derivation), fused_bytes() over the instruction BYTES with its own
# prefix/REX/VEX/EVEX/opcode/ModRM/SIB decode (the check); they share only objdump's instruction boundaries and the
# rule fact_of(). RESIDUAL ([r11-REV15-4], ACCEPTED): both read every instruction inside the symbol, dead code
# included (gcc emits none in these loops, and the manifest's sha closes the planting path).
SUBJ_REG = 7                        # %rdi: the subject pointer, the timed function's first argument

def fact_of(reads):
    """the rule, over one reading's subject reads (one bool per read: is it a fused compare form): fused iff exactly
    one read and it is the compare"""
    return len(reads) == 1 and reads[0]

GPR = {}
for _n, _names in enumerate((("rax", "eax", "ax", "al", "ah"), ("rcx", "ecx", "cx", "cl", "ch"), ("rdx", "edx", "dx", "dl", "dh"),
                             ("rbx", "ebx", "bx", "bl", "bh"), ("rsp", "esp", "sp", "spl"), ("rbp", "ebp", "bp", "bpl"),
                             ("rsi", "esi", "si", "sil"), ("rdi", "edi", "di", "dil"))):
    GPR.update((x, _n) for x in _names)
GPR.update(("r%d%s" % (_n, s), _n) for _n in range(8, 16) for s in ("", "d", "w", "b"))
TEXT_PREFIX = {"data16", "data32", "addr32", "cs", "ds", "es", "ss", "fs", "gs", "lock", "rep", "repz", "repe", "repnz",
               "repne", "notrack", "bnd"}

def _text_insn(t):
    """(mnemonic, register operands, memory operands' registers [one set per memory operand], first operand)"""
    w = t.split(None, 1)
    while w and (w[0] in TEXT_PREFIX or w[0].startswith("rex")):
        w = w[1].split(None, 1) if len(w) > 1 else []
    if not w:
        return "", set(), [], ""
    ops, depth, cur = [], 0, ""
    for ch in (w[1] if len(w) > 1 else ""):
        if ch == "," and depth == 0:
            ops.append(cur.strip()); cur = ""
            continue
        depth += {"(": 1, ")": -1}.get(ch, 0)
        cur += ch
    if cur.strip():
        ops.append(cur.strip())
    regs, mems = set(), []
    for o in ops:
        if "(" in o:
            mems.append({GPR[r] for r in re.findall(r"%(\w+)", o[o.index("("):]) if r in GPR})
        elif ":" not in o and o.lstrip("*").startswith("%") and o.lstrip("*")[1:] in GPR:
            regs.add(GPR[o.lstrip("*")[1:]])
    if re.fullmatch(r"(sh[lr]|sa[lr]|ro[lr]|rc[lr])[bwlq]?", w[0]) and ops and ops[0] == "%cl":
        regs.discard(1)             # a shift's count register is a source of the count only (the bytes' encoding)
    return w[0], regs, mems, (ops[0] if ops else "")

def fused_text(ins):
    """the derivation, over objdump's text: fact_of() of the function's subject reads"""
    dec = [_text_insn(t) for _b, t in ins]
    if any(m == "(bad)" for m, _r, _s, _f in dec):
        raise InputError("FUSED-FACT UNDECODED: objdump read (bad) inside a timed function")
    der = {SUBJ_REG}
    while True:                     # the subject-derived registers, to a fixed point (flow-insensitive)
        n = len(der)
        for m, regs, mems, _f in dec:
            if m.startswith(("nop", "prefetch")):
                continue
            if m.startswith("lea"):
                if mems and mems[0] & der:
                    der |= regs
            elif m.startswith("pop"):
                der |= regs
            elif not mems and not re.fullmatch(r"(cmp|test|bt)[bwlq]?", m) and regs & der:
                der |= regs
        if len(der) == n:
            break
    reads = []
    for m, regs, mems, first in dec:
        if m.startswith(("nop", "prefetch", "lea")):
            continue
        if m.startswith("call") or any(s & der for s in mems):
            reads.append(len(mems) == 1 and (bool(re.fullmatch(r"cmp[bwlq]?", m))
                                             or bool(re.fullmatch(r"test[bwlq]?", m)) and first.startswith("$")))
    return fact_of(reads)

PREFIXES = {0x26, 0x2E, 0x36, 0x3E, 0x64, 0x65, 0x66, 0x67, 0xF0, 0xF2, 0xF3}
NO_MODRM = (set(range(0x50, 0x60)) | set(range(0x70, 0x80)) | set(range(0x90, 0x9A)) | set(range(0xA0, 0xB0))
            | set(range(0xB0, 0xC0)) | {0x04, 0x05, 0x0C, 0x0D, 0x14, 0x15, 0x1C, 0x1D, 0x24, 0x25, 0x2C, 0x2D, 0x34,
                                        0x35, 0x3C, 0x3D, 0x68, 0x6A, 0xC2, 0xC3, 0xC9, 0xCC, 0xE8, 0xE9, 0xEB, 0x98, 0x99})
NO_MODRM_0F = set(range(0x80, 0x90)) | {0x05, 0x0B, 0x31, 0x77, 0xA2}
GROUP = {0x80, 0x81, 0x83, 0x8F, 0xC0, 0xC1, 0xC6, 0xC7, 0xD0, 0xD1, 0xD2, 0xD3, 0xF6, 0xF7, 0xFE, 0xFF}  # reg = opcode ext.
GROUP_0F = {0x00, 0x01, 0xAE, 0xBA, 0xC7} | set(range(0x18, 0x20)) | set(range(0x90, 0xA0))
BYTE_OPS = {0x00, 0x02, 0x08, 0x0A, 0x10, 0x12, 0x18, 0x1A, 0x20, 0x22, 0x28, 0x2A, 0x30, 0x32, 0x38, 0x3A, 0x84, 0x86,
            0x88, 0x8A, 0x80, 0xC0, 0xC6, 0xD0, 0xD2, 0xF6, 0xFE}       # 8-bit reg and r/m: ah..bh without a REX
STRING_REGS = {0xA4: {6, 7}, 0xA5: {6, 7}, 0xA6: {6, 7}, 0xA7: {6, 7}, 0xAA: {7}, 0xAB: {7}, 0xAC: {6}, 0xAD: {6},
               0xAE: {7}, 0xAF: {7}}

def _byte_insn(b, t):
    """one instruction's decode: (op, vex, reg field, r/m register or None, memory registers or None, call?)"""
    def need(k):
        if k >= len(b):
            raise InputError("FUSED-FACT UNDECODED: %r (%s)" % (t, " ".join("%02x" % x for x in b)))
    i = 0
    while i < len(b) and b[i] in PREFIXES:
        i += 1
    need(i)
    rex = b[i] if 0x40 <= b[i] <= 0x4F else 0
    i += 1 if rex else 0
    need(i)
    vex = b[i] in (0xC4, 0xC5, 0x62)          # 64-bit mode: always VEX (C4/C5) or EVEX (62)
    if vex:
        need(i + 1)
        p = b[i + 1]
        R, X, B = (~p >> 7) & 1, (~p >> 6) & 1 if b[i] != 0xC5 else 0, (~p >> 5) & 1 if b[i] != 0xC5 else 0
        mm, i = (1, i + 2) if b[i] == 0xC5 else ((p & 0x1F), i + 3) if b[i] == 0xC4 else ((p & 7), i + 4)
        if mm not in (1, 2, 3):
            raise InputError("FUSED-FACT UNDECODED: %r (VEX/EVEX map %d)" % (t, mm))
        rex = 0x40 | R << 2 | X << 1 | B
        need(i)
        op = ((0x0F,), (0x0F, 0x38), (0x0F, 0x3A))[mm - 1] + (b[i],)
        j, has = i + 1, not (mm == 1 and b[i] in NO_MODRM_0F)
    elif b[i] == 0x0F:
        need(i + 1)
        if b[i + 1] in (0x38, 0x3A):
            need(i + 2)
            op, j, has = (0x0F, b[i + 1], b[i + 2]), i + 3, True
        else:
            op, j, has = (0x0F, b[i + 1]), i + 2, b[i + 1] not in NO_MODRM_0F
    else:
        op, j, has = (b[i],), i + 1, b[i] not in NO_MODRM
    call = op == (0xE8,)
    if not has:
        if len(op) == 1 and op[0] in STRING_REGS:
            return op, vex, None, None, STRING_REGS[op[0]], call
        r = ((op[0] & 7) | (8 if rex & 1 else 0) if len(op) == 1 and (0x50 <= op[0] <= 0x5F or 0x90 <= op[0] <= 0x97
                                                                       or 0xB0 <= op[0] <= 0xBF) else None)
        return op, vex, r, None, None, call
    need(j)
    mod, reg, rm = b[j] >> 6, (b[j] >> 3) & 7, b[j] & 7
    byte_op = not rex and not vex and (len(op) == 1 and op[0] in BYTE_OPS)
    byte_rm = byte_op or (not rex and not vex and len(op) == 2 and (op[1] in (0xB6, 0xBE) or 0x90 <= op[1] <= 0x9F))
    regn = (reg & 3 if byte_op and reg >= 4 else reg) | (8 if rex & 4 else 0)
    if len(op) == 1 and op[0] in GROUP or len(op) == 2 and op[1] in GROUP_0F and not vex:
        regn = None
    call = call or (op == (0xFF,) and reg in (2, 3))
    if mod == 3:
        return op, vex, (reg, regn), (rm & 3 if byte_rm and rm >= 4 else rm) | (8 if rex & 1 else 0), None, call
    if rm == 4:
        need(j + 1)
        sib = b[j + 1]
        idx = ((sib >> 3) & 7) | (8 if rex & 2 else 0)
        base = None if (sib & 7) == 5 and mod == 0 else (sib & 7) | (8 if rex & 1 else 0)
        mem = {x for x in (base, None if idx == 4 else idx) if x is not None}
    elif rm == 5 and mod == 0:
        mem = set()                           # RIP-relative
    else:
        mem = {rm | (8 if rex & 1 else 0)}
    return op, vex, (reg, regn), None, mem, call

def fused_bytes(ins):
    """the check, from the bytes: fact_of() of the function's subject reads, each a fused compare form iff it is
    CMP r/m,r or r,r/m (38-3B), CMP r/m,imm (80/81/83 /7) or TEST r/m,imm (F6/F7 /0) and not VEX/EVEX"""
    dec = [_byte_insn(b, t) for b, t in ins]
    nop = lambda op: len(op) == 2 and op[0] == 0x0F and 0x18 <= op[1] <= 0x1F
    def nowrite(op, reg):
        return (op in ((0x38,), (0x39,), (0x3A,), (0x3B,), (0x84,), (0x85,), (0x0F, 0xA3))
                or op in ((0x80,), (0x81,), (0x83,)) and reg == 7 or op in ((0xF6,), (0xF7,)) and reg in (0, 1)
                or op == (0x0F, 0xBA) and reg == 4)
    der = {SUBJ_REG}
    while True:                     # the subject-derived registers, to a fixed point (flow-insensitive)
        n = len(der)
        for op, vex, rg, rmr, mem, _call in dec:
            if vex or nop(op):
                continue
            if mem is None and rmr is None:          # no ModRM: push/pop/xchg/mov imm by the opcode's register
                if rg is not None and 0x58 <= op[0] <= 0x5F:
                    der.add(rg)
                elif rg is not None and (0x90 <= op[0] <= 0x97) and ({0, rg} & der):
                    der |= {0, rg}
                continue
            if op == (0x8D,):
                if mem & der:
                    der.add(rg[1])
            elif mem is None and not nowrite(op, rg[0]):
                regs = {x for x in (rg[1], rmr) if x is not None}
                if regs & der:
                    der |= regs
        if len(der) == n:
            break
    reads = []
    for op, vex, rg, _rmr, mem, call in dec:
        if nop(op) or op == (0x8D,):
            continue
        if call or (mem is not None and mem & der):
            reads.append(not vex and rg is not None and (op in ((0x38,), (0x39,), (0x3A,), (0x3B,))
                                                       or op in ((0x80,), (0x81,), (0x83,)) and rg[0] == 7
                                                       or op in ((0xF6,), (0xF7,)) and rg[0] == 0))
    return fact_of(reads)

FUSED_DERIVE = fused_text           # the derivation the fact is taken from (est's self-test swaps it to plant one)

def disasm(exe):
    """{symbol stem: [(bytes, mnemonic text)]} for every `<stem>_time` function of exe (objdump -d, one line per
    instruction at --insn-width=16), [r11-REV15-4] the instructions inside the symbol's own range only (nm -S: its
    address and size; the alignment padding after it is never read)"""
    r = subprocess.run(["nm", "-S", "--defined-only", exe], capture_output=True, text=True)
    if r.returncode:
        raise InputError("nm %s: rc %d %s" % (exe, r.returncode, r.stderr[-300:]))
    rng = {}
    for ln in r.stdout.splitlines():
        f = ln.split()
        if len(f) == 4 and f[3].endswith("_time"):
            rng[f[3][:-5]] = (int(f[0], 16), int(f[0], 16) + int(f[1], 16))
    r = subprocess.run(["objdump", "-d", "--insn-width=16", exe], capture_output=True, text=True)
    if r.returncode:
        raise InputError("objdump %s: rc %d %s" % (exe, r.returncode, r.stderr[-300:]))
    out, cur, lim = {}, None, None
    for ln in r.stdout.splitlines():
        m = re.match(r"[0-9a-f]+ <(\w+)_time>:$", ln)
        if m:
            if m.group(1) not in rng:
                raise InputError("%s: %s_time has no symbol size (nm -S): its range is unknown" % (exe, m.group(1)))
            cur, lim = out.setdefault(m.group(1), []), rng[m.group(1)]
            continue
        if re.match(r"[0-9a-f]+ <", ln):
            cur = None
            continue
        m = re.match(r"\s*([0-9a-f]+):\t([0-9a-f ]+?)\s*\t(.*)$", ln)
        if m and cur is not None and lim[0] <= int(m.group(1), 16) < lim[1]:
            cur.append(([int(x, 16) for x in m.group(2).split()], re.sub(r"\s*#.*$", "", m.group(3)).strip()))
    return out

def manifest_check(rundir, rec, j, L):
    """[r11-REV15-1] job j's MANIFEST (run.py dry's: the run id and the sha-256 of the frozen plan and of every launch
    executable) against the run directory, and against the record's pin of it (`manifest_sha256_<job>`, from the
    window after the second) when the record has one: (the manifest's sha-256, pinned?)"""
    p = os.path.join(rundir, j, "manifest.tsv")
    if not os.path.exists(p):
        raise InputError("job %s ran but %s is absent (the fused-compare fact is read from the code it pins)" % (j, p))
    m = dict(ln.rstrip("\n").split("\t", 1) for ln in open(p) if ln.strip() and not ln.startswith("#"))
    msha, pin = plan.sha256(p), rec["run"].get("manifest_sha256_" + j)
    if pin is not None and pin != msha:
        raise InputError("MANIFEST MISMATCH job %s: %s's sha-256 is %s, the record pins %s" % (j, p, msha, pin))
    if m.get("run_id") != rec["run"]["run_id"]:
        raise InputError("MANIFEST MISMATCH job %s: the manifest's run id %s, the record's %s" % (j, m.get("run_id"), rec["run"]["run_id"]))
    if m.get("plan") != plan.sha256(os.path.join(rundir, "plan.tsv")):
        raise InputError("MANIFEST MISMATCH job %s: plan.tsv is not the plan the manifest pins" % j)
    for l in range(1, L + 1):
        exe = os.path.join(rundir, j, "L%d" % l, "%s.L%d" % (j, l))
        if not os.path.exists(exe):
            raise InputError("job %s ran but its launch executable %s is absent (the fused-compare fact is read "
                             "from the timed code)" % (j, exe))
        if plan.sha256(exe) != m.get("L%d" % l):
            raise InputError("MANIFEST MISMATCH job %s: launch %d's executable is not the one the manifest pins (the "
                             "code the cells timed)" % (j, l))
    return msha, pin is not None

def plan_stems(rundir, j):
    """[r11-REV15-1] {arm name: its symbol stem} for verify job j from the PINNED plan (RUNDIR/plan.tsv, the manifest
    pins its sha): link.py numbers a job's arms a0, a1, .. in plan.build's order with the control left out, and a
    verify job's order is its null bases by class, then each row and its twin in row order. The slot table
    obj/tab.c, which no manifest pins, must agree when it is present (STEM MISMATCH)"""
    fr = plan.read_frozen(os.path.join(rundir, "plan.tsv"))
    rows = [f for f in fr.get("rows", []) if f[2] == j]
    if not rows or not all(f[0].startswith("kit.verify_cmp.") and f[4].startswith("base.null.") for f in rows):
        raise InputError("job %s's pinned plan rows are not all verify rows on a null base: no stem order for it" % j)
    arms = sorted({f[4] for f in rows}) + [a for f in rows for a in (f[0], f[0] + "#b")]
    n = {f[0]: f[1] for f in fr.get("jobs", [])}.get(j)
    if n != str(len(arms) + 1):
        raise InputError("job %s: the pinned plan states %s arms, its verify order %d and the control" % (j, n, len(arms)))
    stems = {a: "a%d" % k for k, a in enumerate(arms)}
    p = os.path.join(rundir, j, "obj", "tab.c")
    if os.path.exists(p):
        tab = dict(re.findall(r'\{ "([^"]+)", K_\w+, (a\d+)_time', open(p).read()))
        if tab != stems:
            bad = sorted(a for a in set(tab) | set(stems) if tab.get(a) != stems.get(a))
            raise InputError("STEM MISMATCH job %s: obj/tab.c's stems differ from the pinned plan's arm order (%s)"
                             % (j, ", ".join(bad[:4])))
    return stems

def fused_facts(rundir, rec, keys, L):
    """[rev1.5 R15-1] ({verify row key: the FUSED-COMPARE fact}, {job: manifest_check's answer}), read from every
    launch executable of the row's job (each the one its manifest pins, r11-REV15-1) for the arm and its twin; the
    two readings must agree on every function, the fact must be one per row, and [r11-REV15-10] each row's null
    base must NOT be fused (§3.5¶3b's bound assumes an un-fused base)"""
    out, pins = {}, {}
    for j in sorted({j for _k, j in keys}):
        pins[j] = manifest_check(rundir, rec, j, L)
        syms = plan_stems(rundir, j)
        code = [disasm(os.path.join(rundir, j, "L%d" % l, "%s.L%d" % (j, l))) for l in range(1, L + 1)]
        def fact(arms, name):
            got = set()
            for arm in arms:
                for l, d in enumerate(code, 1):
                    ins = d.get(syms[arm])
                    if not ins:
                        raise InputError("launch %d of job %s holds no %s_time (%s)" % (l, j, syms[arm], arm))
                    f = bool(FUSED_DERIVE(ins))
                    if fused_bytes(ins) != f:
                        raise InputError("FUSED-FACT MISMATCH %s launch %d: the mnemonics say %s, the instruction "
                                         "bytes say %s" % (arm, l, "fused" if f else "not fused",
                                                           "not fused" if f else "fused"))
                    got.add(f)
            if len(got) != 1:
                raise InputError("FUSED-FACT UNSTABLE %s: fused in some launches or arm/twin, not in others" % name)
            return got.pop()
        mine = sorted(k for k, jj in keys if jj == j)
        for key in mine:
            out[key] = fact((key, key + "#b"), key)
        for b in sorted({plan.base_of(k) for k in mine}):
            if fact((b,), b):
                raise InputError("FUSED-FACT BASE %s: the null base's own compiled code is fused (one subject read, a "
                                 "compare): the bound of measures.md §3.5¶3b assumes an un-fused base" % b)
    return out, pins

def est_inputs():
    """[r11-REV15-6] the files whose text is the estimator's rules: est.py, every module it imported from outside the
    standard library, the digest's ks_ref.py, and the live policy table"""
    std = os.path.realpath(os.path.dirname(os.__file__)) + os.sep
    mods = {os.path.realpath(m.__file__) for m in list(sys.modules.values()) if getattr(m, "__file__", None)}
    return ([os.path.realpath(__file__)] + sorted(p for p in mods if not p.startswith(std) and p != os.path.realpath(__file__))
            + [os.path.join(TREE, "tests", "knowledge", "ks_ref.py"), plan.POLICY])

def est_commit(paths=None):
    """[rev1.5 R15-2, r11-REV15-6] (the commit of this estimator, None) or (None, why): HEAD of the tree est.py is
    in, refused unless EVERY input of its rules (est_inputs; paths[0] the estimator) is tracked at HEAD with a blob
    identical to the file (git hash-object vs ls-tree): an uncommitted edit, an untracked or ignored copy, or a file
    outside the tree has no commit that reproduces the draft"""
    paths = paths or est_inputs()
    def git(*a):
        return subprocess.run(["git", "-C", os.path.dirname(os.path.realpath(paths[0]))] + list(a), capture_output=True, text=True)
    h, top = git("rev-parse", "HEAD"), git("rev-parse", "--show-toplevel")
    if h.returncode or top.returncode or not re.fullmatch(r"[0-9a-f]{40}", h.stdout.strip()):
        return None, "est.py is not in a git tree"
    head, top = h.stdout.strip(), os.path.realpath(top.stdout.strip())
    for p in paths:
        rel = os.path.relpath(os.path.realpath(p), top)
        if rel.startswith(".."):
            return None, "%s is outside the tree %s" % (p, top)
        t = git("-C", top, "ls-tree", "HEAD", "--", rel)
        m = re.match(r"\d+ blob ([0-9a-f]{40})\t", t.stdout)
        if not m:
            return None, "%s is not tracked at HEAD %s (an untracked or ignored copy)" % (rel, head[:12])
        if git("-C", top, "hash-object", "--", os.path.realpath(p)).stdout.strip() != m.group(1):
            return None, "%s differs from its blob at HEAD %s (uncommitted)" % (rel, head[:12])
    return head, None

def timed_moved(code_commit, commit, where=HERE):
    """[rev1.5 R15-2, r11-REV15-7] the TIMED paths (timed()) whose text differs between the record's code_commit and
    the est commit, in the tree `where` is in"""
    r = subprocess.run(["git", "-C", where, "diff", "--name-only", code_commit, commit], capture_output=True, text=True)
    if r.returncode:
        raise InputError("git diff %s %s: %s" % (code_commit[:12], commit[:12], r.stderr.strip()[-200:]))
    return [p for p in r.stdout.split() if timed(p)]

def draft_gate(code_commit, paths=None):
    """[rev1.5 R15-2] the est commit a draft may name, or a refusal: no commit reproduces this estimator, or the
    timed code moved between the record's code_commit and it"""
    paths = paths or est_inputs()
    commit, why = est_commit(paths)
    if not commit:
        raise InputError("no draft from an uncommitted estimator (%s): a draft names the est commit that scored it" % why)
    moved = timed_moved(code_commit, commit, os.path.dirname(os.path.realpath(paths[0])))
    if moved:
        raise InputError("the timed code moved between the record's code_commit %s and the est commit %s (%s): a "
                         "later est scores frozen cells only over unchanged timed code" % (
                             code_commit[:12], commit[:12], ", ".join(moved[:8])))
    return commit

def split_gap(v):
    """the largest gap between two clusters of >= 2 launches in v sorted (k in 2 .. L-2, §3.5¶4's clusters)"""
    s = sorted(v)
    return max(s[k] - s[k - 1] for k in range(2, len(s) - 1))

def slope(pts):
    n = len(pts)
    sx = sum(x for x, _ in pts); sy = sum(y for _, y in pts)
    S = n * sum(x * y for x, y in pts) - sx * sy
    D = n * sum(x * x for x, _ in pts) - sx * sx
    return rhafz(S, D)

CELL_COLS = ["cell", "group", "arm", "length", "launch", "round", "events", "ns_e6"]

def cell_row(a, length, l, ns_e6):
    """one cell line for arm a (a plan.Arm) at (length, launch l): the id's fifth field is a delta arm's base
    (§3.4¶5), events the arm's (`-` on a slope arm and on ctl)"""
    base = a.base if a.base and not a.name.startswith("base.") else None
    cid = "%s/%s/%d/%d" % (a.group, a.name, length, l) + ("/" + base if base else "")
    ev = "-" if a.events is None else str(a.events)
    return "\t".join([cid, a.group, a.name, str(length), str(l), "med", ev, str(ns_e6)])

def cells_text(run_id, rows):
    return "#run_id\t%s\n#%s\n%s\n" % (run_id, "\t".join(CELL_COLS), "\n".join(rows))

def read_cells(rundir, rec):
    """the cells of every RAN timing job, cross-checked against the record (r9 G3)"""
    ran = {j for j, (s, _c) in rec["jobs"].items() if s == "ran"}
    cells = []
    for f in sorted(os.listdir(rundir)):
        m = re.fullmatch(r"cells\.(J\w+)\.tsv", f)
        if not m:
            continue
        j = m.group(1)
        if j not in ran:
            raise InputError("%s holds cells of job %s, which the record says %s" % (f, j, rec["jobs"].get(j, ("unplanned",))[0]))
        lines = open(os.path.join(rundir, f)).read().splitlines()
        if not lines or lines[0] != "#run_id\t%s" % rec["run"]["run_id"]:
            raise InputError("%s's first line %r is not `#run_id<TAB>%s`: a cells file of another run" % (f, lines[:1], rec["run"]["run_id"]))
        for ln in lines[1:]:
            if ln.startswith("#") or not ln.strip():
                continue
            c = dict(zip(CELL_COLS, ln.split("\t")))
            try:
                c["length"], c["launch"], c["ns_e6"] = int(c["length"]), int(c["launch"]), int(c["ns_e6"])
            except (KeyError, ValueError):
                raise InputError("%s: a malformed cell line %r" % (f, ln))
            idf = c["cell"].split("/")
            if idf[:4] != [c["group"], c["arm"], str(c["length"]), str(c["launch"])] or c["group"].split(".")[0] != j:
                raise InputError("%s: cell id %s disagrees with its columns (%s %s %d %d) or its job" % (f, c["cell"], c["group"], c["arm"], c["length"], c["launch"]))
            key = c["arm"][:-2] if c["arm"].endswith("#b") else c["arm"]
            want = plan.base_of(key) if key.startswith("kit.") else None
            if (idf[4] if len(idf) == 5 else None) != want or len(idf) > 5:
                raise InputError("%s: cell %s names base %s, the family rule's is %s" % (f, c["cell"], idf[4:] or "none", want))
            c["job"] = j
            cells.append(c)
    return cells

def read_record(rundir):
    """the finalized run record: run (dict), jobs {job: (state, cause)}, plan [(key, group, job)], floor, the
    pinned card and policy rows, and from them `card` ({quantity: card}) and `facts` (plan.card_facts)"""
    rec, sec = {"run": {}, "jobs": {}, "plan": [], "floor": [], "cards": [], "policy": []}, None
    p = os.path.join(rundir, "run_record.tsv")
    if not os.path.exists(p):
        raise InputError("%s is absent (record.py finalize writes it)" % p)
    for ln in open(p):
        ln = ln.rstrip("\n")
        if ln.startswith("#section "):
            sec = ln.split()[1]
            continue
        if ln.startswith("#") or not ln:
            continue
        f = ln.split("\t")
        if sec == "run":
            rec["run"][f[0]] = f[1]
        elif sec == "jobs":
            rec["jobs"][f[0]] = (f[1], f[2])
        elif sec in ("plan", "floor"):
            rec[sec].append(tuple(f))
        elif sec in ("cards", "policy"):
            rec[sec].append(f)
    if not rec["run"].get("run_id") or not rec["jobs"] or not rec["plan"] or not rec["floor"]:
        raise InputError("%s is not finalized (run_id, jobs, plan and floor are all required)" % p)
    for k in ("cards", "policy"):
        if not rec[k] or not re.fullmatch(r"[0-9a-f]{64}", rec["run"].get(k + "_sha256", "")):
            raise InputError("%s pins no %s values or no %s_sha256 (r9fc FIX-1: the verdict reads the values the "
                             "run was planned under, never the live tables)" % (p, k, k))
    try:
        rec["card"] = plan.parse_cards(rec["cards"], plan.parse_policy(rec["policy"]))
        rec["facts"] = plan.card_facts(rec["card"])
    except (SystemExit, KeyError, ValueError) as e:
        raise InputError("%s's pinned cards or policy do not parse: %s" % (p, e))
    if len(rec["card"]) != len(rec["cards"]):
        raise InputError("%s pins %d card rows, %d of them ver-%s cards" % (p, len(rec["cards"]), len(rec["card"]), plan.METHOD_VER))
    if rec["run"].get("rules") != "kit-grid@" + plan.METHOD_VER:
        raise InputError("the record's rules owner %r is not this producer's kit-grid@%s (measures.md §3.5¶8a)"
                         % (rec["run"].get("rules"), plan.METHOD_VER))
    return rec

def compute(rundir):
    rec = read_record(rundir)
    cells = read_cells(rundir, rec)
    floor = rec["floor"]
    R_MAX = r_max(rec)[0]
    card = rec["card"]                         # the PINNED cards (r9fc FIX-1), never plan.CARD
    LENGTHS, _LEN, L, _R, GU = rec["facts"]
    if any(k.split(".")[1] not in card for k, _g, _j in rec["plan"]):
        raise InputError("a planned key's quantity has no pinned card (%s)" % sorted({k.split(".")[1] for k, _g, _j in rec["plan"]} - set(card)))
    rows = [(k, g, j, card[k.split(".")[1]]["est"], plan.base_of(k)) for k, g, j in rec["plan"]]
    c = {}
    for x in cells:
        c[(x["job"], x["arm"], x["length"], x["launch"])] = x
    ran = {j for j, (s, _c) in rec["jobs"].items() if s == "ran" and j != "J1"}
    def need(j, arm, length, l):
        if (j, arm, length, l) not in c:
            raise InputError("job %s ran, but its cell (%s, %d, launch %d) is absent" % (j, arm, length, l))
        return c[(j, arm, length, l)]
    def cell(j, arm, length, l):
        return need(j, arm, length, l)["ns_e6"]
    u = {}
    for j in sorted(ran):
        if not any(r[2] == j for r in rows):
            continue
        u[j] = [slope([(x, cell(j, "ctl", x, l)) for x in LENGTHS]) for l in range(1, L + 1)]
        if min(u[j]) <= 0:
            raise InputError("job %s's control slopes %s: every u_l must be positive (measures.md §3.4¶14a)" % (j, u[j]))
    out = {}
    W = None
    # [rev1.5 R15-1] every ran verify row's FUSED-COMPARE fact, from its timed code
    fused, pins = fused_facts(rundir, rec, [(k, j) for k, _g, j, _e, b in rows if j in ran and b and k.startswith("kit.verify_cmp.")], L)
    for key, group, j, est, base in rows:
        if j not in ran:
            out[key] = {"absent": "never-ran:%s" % j}
            continue
        kind, xs = plan._est_parse(est)
        def per_launch(arm):
            if kind == "slope":
                return [slope([(x, cell(j, arm, x, l)) for x in xs]) for l in range(1, L + 1)], None
            ev = {need(j, a2, xs[0], l)["events"] for a2 in (key, key + "#b") for l in range(1, L + 1)}
            if len(ev) != 1 or not next(iter(ev)).isdigit() or int(next(iter(ev))) <= 0:
                raise InputError("%s's cells state events %s: one positive E is required (§3.4¶11)" % (key, sorted(ev)))
            E = int(ev.pop())
            D = [cell(j, arm, xs[0], l) - cell(j, base, xs[0], l) for l in range(1, L + 1)]
            return [rhafz(d, E) for d in D], D
        a, D = per_launch(key)
        ab, Db = per_launch(key + "#b")
        v = [rhafz(a[i] * 10**6, u[j][i]) for i in range(L)]
        vb = [rhafz(ab[i] * 10**6, u[j][i]) for i in range(L)]
        out[key] = {"group": group, "job": j, "est": est, "v": v, "vb": vb, "abs": med(a), "D": D, "Db": Db}
        if key == plan.UNIT_KEY:
            W = med(v)
    for key, r in out.items():
        if "absent" in r:
            continue
        if W is None or W <= 0:
            break
        x = [rhafz(t * 10**6, W) for t in r["v"]]
        xb = [rhafz(t * 10**6, W) for t in r["vb"]]
        aa = med([abs(xb[i] - x[i]) for i in range(L)])
        r.update(x=x, value=med(x), aa=aa, noise=isqrt_rn(aa * aa + sp2(x)))
        if r["D"] is not None and fused.get(key):
            # [rev1.5 R15-1] THE FUSED-COMPARE BOUND, scoped by the class fact (never by the sign): the compare is the
            # candidate load itself, so no base made by removing it can be null; a MEASURED row bounded by
            # max(r_max, |med(x_l)|). [r11-REV15-5] Its value is max(0, med(x_l)): the fused D is biased negative (the
            # base pays the un-fused load), so a positive median is a lower bound and 0 is known wrong there; the
            # fact decides the scope, the sign picks the value inside it
            r.update(null=False, fused=True, value=max(r["value"], 0), noise=max(R_MAX, abs(r["value"])),
                     why="fused-compare bound: value %d, noise max(r_max %d, |med| %d)" % (
                         max(r["value"], 0), R_MAX, abs(r["value"])))
        elif r["D"] is not None:
            aaD = med([abs(r["Db"][i] - r["D"][i]) for i in range(L)])
            r["null"] = not (all(d > 0 for d in trim(r["D"])) and med(r["D"]) > aaD)
            # [rev1.4 r10-REV14-2] r is the row's resolution capped at the policy's r_max_e6
            res = min(resolution(x), R_MAX)
            if r["null"] and all(d < 0 for d in trim(r["D"])):
                # [rev1.4 r10-REV14-1] negative on all six trimmed launches: a DEFECT, whatever r is
                r["why"] = "null: negative per-event cost on all six trimmed launches (a fixture defect, whatever r)"
            elif r["null"] and abs(r["value"]) <= res and r["aa"] <= res:
                # [rev1.4 R14-2] SUB-RESOLUTION: signs mixed, consistent with zero within r, its paired A/A within
                # r too: a MEASURED row, the clamped estimate, its noise r or the measured noise if larger
                # (measures.md §3.5¶3a)
                r.update(null=False, sub=res, value=max(0, r["value"]), noise=max(res, r["noise"]),
                         why="sub-resolution: consistent with zero within r %d" % res)
            elif r["null"] and abs(r["value"]) <= res:
                r["why"] = "null: within its resolution r %d but its paired A/A %d is above r" % (res, r["aa"])
            elif r["null"]:
                r["why"] = "null: below its paired A/A or signs mixed, at a size above its resolution r %d" % res
        else:
            # §3.5¶2: the card's gate; the unit's is HALF, compared doubled (exact for an odd gate, r9 G7)
            G = card[key.split(".")[1]]["gate"]
            half = 2 if key == plan.UNIT_KEY else 1
            r["gate"] = r["value"] > 0 and half * r["noise"] * 10**6 <= G * r["value"]
    unit = out.get(plan.UNIT_KEY, {})
    unit_bad = None
    if "absent" in unit or not unit or W is None or W <= 0:
        unit_bad = "unit absent"                  # measures.md §3.5¶12 row 1: no unit, no set (r9 CONTRACT-4)
    else:
        s = sorted(unit["x"])
        if not unit["gate"]:
            unit_bad = "unit over its half gate"
        elif any(2 * (s[k] - s[k - 1]) > GU for k in range(2, L - 1)):
            unit_bad = "unit bimodal"
    drift = {}
    uj = next((j for k, _g, j, _e, _b in rows if k == plan.UNIT_KEY), None)
    if uj in u:
        CU = med(u[uj])
        rel = lambda v: [rhafz(t * 10**6, med(v)) for t in v]
        for j in sorted(u):
            d = rhafz(abs(med(u[j]) - CU) * 10**6, CU)
            T3 = 3 * isqrt_rn(rhafz(K_MED_E6 * (sp2(rel(u[uj])) + sp2(rel(u[j]))), 10**6))
            drift[j] = (d, T3, 2 * d > GU and d > T3)    # §3.5¶6: both the size floor G/2 and 3 SE
    def unpriced(key):
        r = out[key]
        if "absent" in r:
            return r["absent"]
        if drift.get(r["job"], (0, 0, False))[2]:
            return "drift:%s" % r["job"]
        if r.get("null") or r.get("gate") is False:
            return "text"
        return None
    j1b = rec["run"].get("j1_verdict") == "b"
    clauses = {}
    for cl, key, when in floor:
        if when not in ("always", "unless-j1-b"):
            raise InputError("floor clause %s: unknown condition token %r" % (cl, when))
        if j1b and when == "unless-j1-b":
            continue
        clauses.setdefault(cl, []).append(key)
    failed = [cl for cl, ks in sorted(clauses.items()) if all(unpriced(k) for k in ks)]
    absent = [k for k in out if "absent" in out[k] or drift.get(out[k]["job"], (0, 0, False))[2]
              or out[k].get("gate") is False]
    if unit_bad:
        outcome = ("REFUSED", 3, ["unit"])
    elif failed:
        outcome = ("REFUSED", 3, ["floor:%s (%s)" % (cl, ",".join(sorted({unpriced(k) for k in clauses[cl]})))
                                  for cl in failed])
    elif absent:
        outcome = ("PARTIAL", 4, sorted(absent))
    else:
        outcome = ("FULL", 0, [])
    return out, drift, unit_bad, outcome, W, pins

def notes(rundir, out=None):
    """[rev1.4 R14-3, R14-4] the run's NOTE lines (the record's `run` keys note_box_state and note_bimodal, the
    draft's `# note` lines): a launch-level fast/slow split in a job's control (NOTE_SPLIT_E6), and the priced
    delta rows whose launches fall in two clusters (NOTE_BIMODAL_E6). They gate nothing."""
    if out is None:
        out = compute(rundir)[0]
    rec = read_record(rundir)
    LENGTHS, L = rec["facts"][0], rec["facts"][2]
    c = {(x["job"], x["arm"], x["length"], x["launch"]): x["ns_e6"] for x in read_cells(rundir, rec)}
    split = []
    for j in sorted({j for j, _a, _x, _l in c}):
        if (j, "ctl", LENGTHS[0], 1) not in c:
            continue
        u = [slope([(x, c[(j, "ctl", x, l)]) for x in LENGTHS]) for l in range(1, L + 1)]
        g = split_gap([rhafz(t * 10**6, med(u)) for t in u])
        if g > NOTE_SPLIT_E6:
            split.append("%s %d.%02d %%" % (j, g // 10000, g % 10000 // 100))
    bim = sorted(k for k, r in out.items() if "absent" not in r and r.get("D") is not None and not r.get("null")
                 and not r.get("sub") and not r.get("fused") and split_gap(r["x"]) * 10**6 > NOTE_BIMODAL_E6 * r["value"])
    return [("note_box_state", "a launch-level fast/slow split in the control of %s (a gap over %d ppm between two "
             "clusters of >= 2 launches): the box changed state within those jobs" % (", ".join(split), NOTE_SPLIT_E6)
             if split else "no launch-level fast/slow split in any job's control"),
            ("note_bimodal", "bimodal delta rows (a gap over %d ppm of the value between two clusters of >= 2 "
             "launches; priced with their spread as noise): %s" % (NOTE_BIMODAL_E6, ", ".join(bim) or "none"))]

def cell_texts(rundir, rec):
    """{row key: (form, fold hash, tags)} from every ran job's cell_text.tsv (link.py's, the texts it TIMED and
    checked, r9 G5); a form whose fold differs between jobs REFUSES (the kit moved inside the window)"""
    out, fold = {}, {}
    for j, (s, _c) in sorted(rec["jobs"].items()):
        if s != "ran" or j == "J1":
            continue
        p = os.path.join(rundir, j, "cell_text.tsv")
        if not os.path.exists(p):
            raise InputError("job %s ran but %s is absent" % (j, p))
        for ln in open(p):
            if ln.startswith("#") or not ln.strip():
                continue
            arm, form, _cls, _inst, fh, tags = ln.rstrip("\n").split("\t")
            if fold.setdefault(form, fh) != fh:
                raise InputError("form %s's fold hash is %s in one job and %s in %s" % (form, fold[form], fh, j))
            if not arm.endswith("#b") and arm.startswith("kit."):
                out[arm] = (form, fh, tags)
    return out

def main():
    cmd, rundir = sys.argv[1], sys.argv[2]
    if cmd == "selftest":
        return selftest(rundir)
    try:
        out, drift, unit_bad, outcome, W, pins = compute(rundir)
    except InputError as e:
        print("est: REFUSED input: %s" % e)
        return 2
    if cmd == "rows":
        print("policy\tr_max_e6\t%d\t%s" % r_max(read_record(rundir)))
        c, why = est_commit()
        print("est\tcommit\t%s" % (c or "none: " + why))
        for j, (msha, pinned) in sorted(pins.items()):     # [r11-REV15-1]
            print("manifest\t%s\t%s\t%s" % (j, msha, "pinned by the run record" if pinned else
                                             "NOT pinned by the run record (finalized before the pin): checked as it stands"))
        for k in sorted(out):
            r = out[k]
            if "absent" in r:
                print("row\t%s\tABSENT\t%s" % (k, r["absent"]))
            else:
                # [rev1.4 R14-4] a delta row has no gate (measures.md §3.5¶3): `ungated`, never a gate verdict
                print("row\t%s\tvalue %s\tnoise %s\t%s" % (k, "-" if r.get("null") else r["value"],
                      "-" if r.get("null") else r["noise"],
                      r.get("why") or ("ungated" if r["D"] is not None else
                                       "gate %s" % ("pass" if r.get("gate", True) else "FAIL"))))
        for j, (d, T, bad) in sorted(drift.items()):
            print("drift\t%s\t%d\t%d\t%s" % (j, d, T, "REFUSED" if bad else "kept"))
        for k, v in notes(rundir, out):
            print("note\t%s\t%s" % (k, v))
        print("== s2 OUTCOME %s exit %d %s" % (outcome[0], outcome[1], "; ".join(outcome[2])))
        return outcome[1]
    if cmd == "draft":
        if outcome[0] == "REFUSED":
            print("== s2 OUTCOME REFUSED: no draft written (%s)" % "; ".join(outcome[2]))
            return outcome[1]
        try:
            return write_draft(rundir, sys.argv[3], out, drift, outcome)
        except InputError as e:
            print("est: REFUSED input: %s" % e)
            return 2

def write_draft(rundir, path, out, drift, outcome):
    rec = read_record(rundir)
    for k in ("box", "isa", "libc", "gcc", "code_commit"):
        if not rec["run"].get(k):
            raise InputError("the record's run section has no %s (record.py window writes it)" % k)
    texts = cell_texts(rundir, rec)
    commit = draft_gate(rec["run"]["code_commit"])       # [rev1.5 R15-2, r11-REV15-6, r11-REV15-7]
    rsha = hashlib.sha256(open(os.path.join(rundir, "run_record.tsv"), "rb").read()).hexdigest()
    # the ver-3 cards as the record pins them, VERBATIM: each states its declared gate_e6 (`-`), so check C's
    # set-vs-card-table equality holds; the value a `-` took is the record's pinned policy ([rev1.3 r9fc-FIX-8])
    cards = ["\t".join(f) for f in rec["cards"]]
    n = str(rec["facts"][2] * rec["facts"][3])
    rows = []
    rec_rmax = r_max(rec)[0]
    for k in sorted(out):
        r = out[k]
        if "absent" in r or r.get("gate") is False or drift.get(r["job"], (0, 0, False))[2]:
            continue
        q = k.split(".")
        unit = rec["card"][q[1]]["unit"]
        deps, tags = "-", "-"
        if q[1] != "enter":
            if k not in texts:
                raise InputError("row %s has no cell text in its job's cell_text.tsv" % k)
            form, fh, tags = texts[k]
            if form != q[2]:
                raise InputError("row %s's cell text is form %s's" % (k, form))
            deps = "kit:form.%s=%s" % (form, fh)
        if r.get("null"):
            rows.append([k, unit, "", str(r["abs"]), "-", n, "null", "-", "-",
                         deps, tags, r["why"]])
        elif r.get("fused"):              # [rev1.5 R15-1, r11-REV15-5]
            rows.append([k, unit, str(r["value"]), str(r["abs"]), str(r["noise"]), n, "measured", "-", "-", deps,
                         FUSED_TAG if tags == "-" else tags + ";" + FUSED_TAG,
                         "slot %s fused-compare bound r_max %d; %s" % (r["job"], rec_rmax, FUSED_EVIDENCE)])
        else:
            rows.append([k, unit, str(r["value"]), str(r["abs"]), str(r["noise"]), n, "measured", "-", "-", deps,
                         tags, "slot %s%s" % (r["job"], " sub-resolution r %d" % r["sub"] if r.get("sub") else "")])
    hdr = [("format", "2"), ("id", "zen4-grid3"), ("rev", "1"), ("class", "x86_64/zen4"),
           ("isa", rec["run"]["isa"]), ("tier", "scratch"), ("composite", "0"), ("members", ""),
           ("unit_key", plan.UNIT_KEY), ("method", "kit-grid@%s" % plan.METHOD_VER),
           ("run", "%s record:%s" % (rec["run"]["run_id"], rsha)),
           ("box", rec["run"]["box"]), ("compiler", "gcc %s -O2 -march=x86-64 -mtune=generic" % rec["run"]["gcc"]),
           ("libc", rec["run"]["libc"]), ("code_commit", rec["run"]["code_commit"]),
           ("counters", "skipped:not-taken"), ("partial", "1" if outcome[0] == "PARTIAL" else "0"),
           ("rows", str(len(rows))), ("values_digest", "0000000000000000")]
    cells = ["\t".join([c[k] if isinstance(c[k], str) else str(c[k]) for k in CELL_COLS]) for c in read_cells(rundir, rec)]
    def text(h):
        t = ["# pcrec measurement set (spec: docs/spec/measures.md)"]
        t += ["# note %s: %s" % kv for kv in notes(rundir, out)]       # [rev1.4 R14-3, R14-4]
        t += ["# note r_max_e6: %d, %s" % r_max(rec)]                   # [rev1.4 r10-REV14-2]
        t += ["# note est_commit: %s, the estimator that scored the record (code_commit %s; the timed code unchanged "
              "between them)" % (commit, rec["run"]["code_commit"])]      # [rev1.5 R15-2]
        t += ["#section header", "#key\tvalue"]
        t += ["%s\t%s" % kv for kv in h]
        t += ["#section cards", "#" + "\t".join(["owner", "quantity", "ver", "dims", "unit", "subject", "lengths",
              "launches", "rounds", "aa_rule", "gate_e6", "env", "deps"])] + cards
        t += ["#section rows", "#" + "\t".join(["key", "unit", "value_e6", "abs_ns_e6", "noise_e6", "n", "status",
              "derivation", "inputs", "deps", "tags", "source"])] + ["\t".join(r) for r in rows]
        t += ["#section members", "#member\tunit_key\tunit_abs_ns_e6\tbox"]
        t += ["#section cells", "#" + "\t".join(CELL_COLS)] + cells
        return "\n".join(t) + "\n"
    open(path, "w").write(text(hdr))
    d = subprocess.run([sys.executable, "-I", os.path.join(TREE, "tests", "knowledge", "ks_ref.py"), "digest", path],
                       capture_output=True, text=True, check=True).stdout.strip()
    hdr[-1] = ("values_digest", d)
    open(path, "w").write(text(hdr))
    print("draft %s: %d rows, %d cells, digest %s, outcome %s" % (path, len(rows), len(cells), d, outcome[0]))
    return outcome[1]

# ---- the self-test (r9 G3): the cross-checks above, each case a refusal or an outcome ---------------------------
SYNTH_FUSED = ("l1", "c1")      # [rev1.5 R15-1] the classes the synthetic timed code compiles fused, as gcc does today
# [r11] the bodies a synthetic class or base may be compiled with (`variant` below): gcc -O2's lowering of each
SYNTH_BODY = {
    "fused":  "s[*p] == 0x2f",                                     # cmpb $imm,(s,i): ONE subject read, the compare
    "masked": "(s[*p] & 0xdf) == 0x58",                            # a load, then an ALU op
    "load":   "({ int one = 1; __asm__ volatile(\"\" : \"+r\"(one) : \"r\"(s[*p])); one; })",   # a null base's load
    "two":    "s[*p] == 0x2f && s[*p + 1] == 0x75",                # [r11-REV15-2] two fused compares
    "l8":     "memcmp(s + *p, \"/usr/bin\", 8) == 0",              # [r11-REV15-3] cmp %reg,(s,i) (opcode 39)
    "ptr":    "({ const unsigned char *q = s + *p; __asm__(\"\" : \"+r\"(q)); q[0] == 0x2f; })",  # [r11-REV15-3] cmpb $imm,(q)
}

def _synth_code(scratch, arms, fused, variant=None):
    """[rev1.5 R15-1] REAL timed code for a synthetic job: one `aK_time` per arm (link.py's symbol stems, its
    pointer-bump candidate loop), a class in `fused` comparing the candidate byte against an immediate (gcc fuses
    the load into the compare), any other class masking it first (a separate load and ALU op), a null base loading it
    into a register; [r11] `variant` {class or base name: SYNTH_BODY kind} overrides one; compiled once per text by
    gcc -O2 (identical-code folding off, so every stem stays)"""
    variant = variant or {}
    src = ["#include <stddef.h>", "#include <stdint.h>", "#include <string.h>"]
    for k, a in enumerate(arms):
        cls = a.name.split(".")[3] if a.name.startswith("kit.verify_cmp.") else None
        kind = (variant.get(a.name, "load") if a.name.startswith("base.")
                else variant.get(cls, "fused" if cls in fused else "masked"))
        src.append("__attribute__((noinline)) uint64_t a%d_time(const unsigned char *s, size_t n, const uint32_t *c, "
                   "size_t nc)\n{\n    (void)n;\n    uint64_t k = 0;\n    for (const uint32_t *p = c, *e = c + nc; p < e; "
                   "p++) k += (%s) != 0;\n    return k;\n}" % (k, SYNTH_BODY[kind]))
    text = "\n".join(src) + "\n"
    o = os.path.join(scratch, "synth_code.%s.o" % hashlib.sha256(text.encode()).hexdigest()[:16])
    if not os.path.exists(o):
        open(o[:-2] + ".c", "w").write(text)
        subprocess.run(["gcc", "-std=gnu11", "-O2", "-march=x86-64", "-mtune=generic", "-fno-ipa-icf", "-c",
                        o[:-2] + ".c", "-o", o], check=True)
    return o

def _synth_manifest(d, j):
    """[r11-REV15-1] job j's manifest as run.py dry writes it (the run id, the plan's and every launch's sha-256)"""
    run_id = read_record(d)["run"]["run_id"] if os.path.exists(os.path.join(d, "run_record.tsv")) else "selftest"
    m = {"run_id": run_id, "plan": plan.sha256(os.path.join(d, "plan.tsv"))}
    for l in range(1, plan.L_LAUNCHES + 1):
        m["L%d" % l] = plan.sha256(os.path.join(d, j, "L%d" % l, "%s.L%d" % (j, l)))
    open(os.path.join(d, j, "manifest.tsv"), "w").write("#name\tvalue\n" + "".join("%s\t%s\n" % kv for kv in sorted(m.items())))

def _synth_pin(d, j="J4", drop=False):
    """[r11-REV15-1] the record's pin of job j's manifest (record.py finalize's `manifest_sha256_<job>`), or none"""
    import record
    p = os.path.join(d, "run_record.tsv")
    rec = record.read(p)
    rec["run"] = [r for r in rec["run"] if r[0] != "manifest_sha256_" + j]
    if not drop:
        record.setrun(rec, "manifest_sha256_" + j, plan.sha256(os.path.join(d, j, "manifest.tsv")))
    record.write(p, rec)

def _synth_launches(d, j, arms, fused, launches=None, variant=None, manifest=True):
    """job j's slot table and launch executables (the synthetic code object, copied per launch; `launches`: only
    those launches rewritten), [r11-REV15-1] and its manifest unless `manifest` is False (the record's pin is the
    caller's, _synth_pin)"""
    os.makedirs(os.path.join(d, j, "obj"), exist_ok=True)
    open(os.path.join(d, j, "obj", "tab.c"), "w").write("".join(
        '    { "%s", K_%s, a%d_time, a%d_gate, ... },\n' % (a.name, "NULL" if a.name.startswith("base.") else "CMP", k, k)
        for k, a in enumerate(arms)))
    o = _synth_code(os.path.dirname(d), arms, fused, variant)
    for l in launches or range(1, plan.L_LAUNCHES + 1):
        os.makedirs(os.path.join(d, j, "L%d" % l), exist_ok=True)
        shutil.copyfile(o, os.path.join(d, j, "L%d" % l, "%s.L%d" % (j, l)))
    if manifest:
        _synth_manifest(d, j)

def _synth(d, run_id="selftest"):
    """a synthetic finalized run directory: the live plan frozen, every timing job ran, linear cells (a slope
    arm's per-byte cost and a delta arm's per-event cost by its key's hash, so rows differ), no clock;
    [rev1.5 R15-1] each verify job's timed code compiled (_synth_code), [r11-REV15-1] its manifest written and
    pinned by the record"""
    import record
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    open(os.path.join(d, "plan.tsv"), "w").write(plan.frozen_text())
    fr = plan.read_frozen(os.path.join(d, "plan.tsv"))
    jobs, _rows, _f, _u = plan.build()
    rec = {name: [] for name, _ in record.SECTIONS}
    rec["run"] = [["set", record.SET], ["rules", record.RULES], ["run_id", run_id], ["code_commit", "0000000"],
                  ["j1_verdict", "a"]]
    rec["jobs"] = [[j, "ran", "-"] for j in record.JOBS]
    record.pin(rec, fr)
    record.write(os.path.join(d, "run_record.tsv"), rec)
    for j, arms in jobs.items():
        if j == "J1":
            continue
        lines = []
        for a in arms:
            h = int(hashlib.sha256(a.name.rstrip("#b").encode()).hexdigest()[:4], 16)
            for l in range(1, plan.L_LAUNCHES + 1):
                for x in a.lengths:
                    jit = (l * 7919 + (a.name.endswith("#b")) * 13) % 97
                    if a.kind == "ctl" or plan._est_parse(plan.CARD.get(a.name.split(".")[1], {"est": "slope 1,2,3"})["est"])[0] == "slope" and not a.name.startswith("base."):
                        ns = x * (1000 + h % 500) + 5000 + jit
                    else:
                        ns = 9000000 + (a.events or 0) * (2000 + h % 900) + jit
                    lines.append(cell_row(a, x, l, ns * 1000))
        open(os.path.join(d, "cells.%s.tsv" % j), "w").write(cells_text(run_id, lines))
        if any(a.name.startswith("kit.verify_cmp.") for a in arms):
            _synth_launches(d, j, [a for a in arms if a.kind != "ctl"], SYNTH_FUSED)
            _synth_pin(d, j)
    return d

# [r11-REV15-2..4] the READING cases: hand-written timed functions (assembled, .size set), each with the fact both
# readings must give; a disagreement or another answer is WRONG
READING_CASES = (
    ("a fused compare beside a VEX load of the subject: not fused (both read the VEX operand)",
     "cmpb $0x2f,(%rdi,%rcx,1)\n vmovdqu (%rdi,%rcx,1),%ymm0\n ret", False),
    ("an EVEX load of the subject alone: not fused", "vmovdqu64 (%rdi,%rcx,1),%zmm0\n ret", False),
    ("the subject as a base-less SIB index beside a fused compare: two reads, not fused",
     "cmpb $0x2f,(%rdi,%rcx,1)\n movzbl 0x40(,%rdi,1),%eax\n ret", False),
    ("a table read through a base-less SIB beside a fused compare: one subject read, fused",
     "cmpb $0x2f,(%rdi,%rcx,1)\n movzbl 0x40(,%rcx,1),%eax\n ret", True),
    ("cmp %reg,mem (39): fused", "mov (%rdx),%ecx\n cmp %r8,(%rdi,%rcx,1)\n ret", True),
    ("cmp mem,%reg (3B): fused", "mov (%rdx),%ecx\n cmp (%rdi,%rcx,1),%r8d\n ret", True),
    ("cmp through a computed pointer, no index: fused",
     "mov (%rdx),%eax\n add %rdi,%rax\n cmpl $0x7273752f,(%rax)\n ret", True),
    ("two fused compares: not fused", "cmpb $0x2f,(%rdi,%rcx,1)\n cmpb $0x75,1(%rdi,%rcx,1)\n ret", False),
    ("a call beside a fused compare: not fused", "cmpb $0x2f,(%rdi,%rcx,1)\n call a0_time\n ret", False),
    ("a load past the symbol's size (padding) beside a fused compare: fused",
     "cmpb $0x2f,(%rdi,%rcx,1)\n ret\n .size {f}, .-{f}\n movzbl (%rdi,%rcx,1),%eax\n ret", True),
)

def _reading_cases(scratch):
    """[r11] READING_CASES: (name, got, want) per case, over one assembled object"""
    src = [" .text"]
    for k, (_n, body, _w) in enumerate(READING_CASES):
        f = "a%d_time" % k
        src += [" .globl %s" % f, " .type %s,@function" % f, "%s:" % f, " " + body.replace("{f}", f)]
        if ".size" not in body:
            src.append(" .size %s, .-%s" % (f, f))
        src.append(" .p2align 4")
    p = os.path.join(scratch, "reading_cases.s")
    open(p, "w").write("\n".join(src) + "\n")
    subprocess.run(["gcc", "-c", p, "-o", p[:-2] + ".o"], check=True)
    d = disasm(p[:-2] + ".o")
    out = []
    for k, (name, _b, want) in enumerate(READING_CASES):
        ins = d.get("a%d" % k, [])
        out.append((name, (bool(FUSED_DERIVE(ins)), fused_bytes(ins)), (want, want)))
    return out

def _gate_repo(scratch, case):
    """[rev1.5 R15-2, r11-REV15-6/7] a scratch git tree for one draft-gate case: slot/est.py, slot/plan.py and
    memfn/data/policy.tsv committed (code_commit), worktrees/ ignored; `case` then edits it. (code_commit, paths)"""
    g = os.path.join(scratch, "gate_repo")
    if os.path.exists(g):
        shutil.rmtree(g)
    def git(*a):
        return subprocess.run(["git", "-C", g, "-c", "user.name=selftest", "-c", "user.email=selftest@invalid", "-c",
                               "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null"] + list(a),
                              capture_output=True, text=True, check=True).stdout.strip()
    files = {"slot/est.py": "rules\n", "slot/plan.py": "plan\n", "memfn/data/policy.tsv": "r_max_e6\t1\n",
             "src/x.c": "int x;\n", "docs/n.md": "text\n", ".gitignore": "worktrees/\n"}
    for f, s in files.items():
        os.makedirs(os.path.dirname(os.path.join(g, f)), exist_ok=True)
        open(os.path.join(g, f), "w").write(s)
    git("init", "-q")
    git("add", "-A")
    git("commit", "-q", "-m", "code")
    c0 = git("rev-parse", "HEAD")
    paths = [os.path.join(g, f) for f in ("slot/est.py", "slot/plan.py", "memfn/data/policy.tsv")]
    def commit(f, s):
        open(os.path.join(g, f), "a").write(s)
        git("commit", "-q", "-am", "edit " + f)
    if case == "prose":
        commit("docs/n.md", "more\n")
    elif case == "timed":
        commit("src/x.c", "int y;\n")
    elif case == "dirty":
        open(paths[0], "a").write("edited\n")
    elif case == "policy":
        open(paths[2], "a").write("edited\n")
    elif case == "ignored":
        os.makedirs(os.path.join(g, "worktrees", "evil", "slot"))
        paths[0] = os.path.join(g, "worktrees", "evil", "slot", "est.py")
        open(paths[0], "w").write("other rules\n")
    return c0, paths

GATE_CASES = (
    ("clean, the timed code unchanged", "clean", "ok"),
    ("only prose (docs/) moved since code_commit", "prose", "ok"),
    ("timed code (src/) moved since code_commit", "timed", "refused:the timed code moved"),
    ("est.py edited, uncommitted", "dirty", "refused:uncommitted"),
    ("policy.tsv edited, uncommitted", "policy", "refused:uncommitted"),
    ("an est.py copy under an ignored path", "ignored", "refused:not tracked"),
)

def selftest(scratch):
    """each case: (name, the plant on a fresh synthetic directory, the expected result: 'ok' or 'refused')"""
    def edit(p, f):
        new = f(open(p).read())
        open(p, "w").write(new)
    def drop_line(t):
        ls = t.split("\n")
        k = next(i for i, ln in enumerate(ls) if "/kit.find_hit." in ln and "/4/" in ln)
        return "\n".join(ls[:k] + ls[k + 1:])
    def set_never(d):
        edit(os.path.join(d, "run_record.tsv"), lambda t: t.replace("J3\tran\t-", "J3\tnever-ran\tfailed"))
    def base_swap(t):
        return re.sub(r"(/kit\.find_hit\.libc\.[^\t]*/)base\.libc\t", r"\1base.walk\t", t, count=1)
    def unpin(d):
        edit(os.path.join(d, "run_record.tsv"), lambda t: re.sub(r"(#section policy\n#[^\n]*\n)[^#]*", r"\1", t))
    def unit_twin_skew(d):     # 4 of the unit twin's 7 launches x1.004 at every length (fixcheck FIX-1's repro)
        def f(t):
            out = []
            for ln in t.split("\n"):
                c = ln.split("\t")
                if len(c) == 8 and c[2] == plan.UNIT_KEY + "#b" and int(c[4]) <= 4:
                    c[7] = str(int(c[7]) * 1004 // 1000)
                out.append("\t".join(c))
            return "\n".join(out)
        edit(os.path.join(d, "cells.J2.tsv"), f)
    def live_edit(d):          # the live tables move after the run: est must not read them (r9fc FIX-1)
        unit_twin_skew(d)
        for c in plan.CARD.values():
            c["gate"] = 300
        plan.CARD["find_byte"]["est"] = "slope 1,2,3"
    def set_delta(d, key, ds, twin=3):
        """[rev1.4 R14-2] KEY's (and its twin's) cells in J4 = its base's cell + ds[l-1] x E per launch l (the twin
        `twin` x E above, or twin[l-1] x E for a list): a per-event cost of ds[l-1] in the cells' own units"""
        p = os.path.join(d, "cells.J4.tsv")
        ls = open(p).read().split("\n")
        base = {}
        for ln in ls:
            c = ln.split("\t")
            if len(c) == 8 and c[2].startswith("base.null."):
                base[(c[2], c[3], c[4])] = int(c[7])
        out = []
        for ln in ls:
            c = ln.split("\t")
            if len(c) == 8 and c[2] in (key, key + "#b"):
                E, l = int(c[6]), int(c[4])
                tw = twin[l - 1] if isinstance(twin, list) else twin
                c[7] = str(base[(c[0].split("/")[4], c[3], c[4])] + (ds[l - 1] + (tw if c[2] != key else 0)) * E)
            out.append("\t".join(c))
        open(p, "w").write("\n".join(out))
    VK = "kit.verify_cmp.settest.c2.p0"     # [rev1.5 R15-1] a class compiled NOT fused (c1's is, SYNTH_FUSED)
    FK = "kit.verify_cmp.rc-memcmp.l1.p0"   # [rev1.5 R15-1] a class compiled fused
    def row(pred, key=VK):
        return lambda out: pred(out[key])
    sub = row(lambda r: bool(r.get("sub")) and not r["null"] and r["value"] >= 0 and r["noise"] >= r["sub"])
    # [rev1.4 r10-REV14-2] the cap's cases are scaled by the live r_max_e6, the value _synth's record pins (a
    # per-event ds of 1 is about 1 in x here, the synthetic unit)
    RM = plan.parse_policy(plan.table_rows(plan.POLICY))["r_max_e6"]
    live_policy = plan.POLICY
    def policy_moved(d):       # the live policy's r_max moves to 1 after the run: the pinned copy must still rule
        p = os.path.join(scratch, "policy_moved.tsv")
        open(p, "w").write("".join("%s\n" % "\t".join(f if f[0] != "r_max_e6" else [f[0], "1", f[2]])
                                   for f in plan.table_rows(live_policy)))
        set_delta(d, VK, [40, -30, 10, -50, 20, -10, 30])
        plan.POLICY = p
    def unpin_rmax(d):         # a record planned before the row (windows 1 and 2): the live row, named
        edit(os.path.join(d, "run_record.tsv"), lambda t: re.sub(r"\nr_max_e6\t[^\n]*", "", t, count=1))
        set_delta(d, VK, [40, -30, 10, -50, 20, -10, 30])
    j4 = [a for a in plan.build()[0]["J4"] if a.kind != "ctl"]
    ALLNEG = [-20, -60, -10, -40, -30, -90, -25]
    CK = "kit.verify_cmp.settest.c1.p0"     # [r11] the other class compiled fused
    def bound_at(key, positive=False):
        """[rev1.5 R15-1, r11-REV15-5] KEY bound: measured, value max(0, med(x)), noise max(r_max, |med|), no bimodal note"""
        def pred(out):
            r, m = out[key], med(out[key]["x"])
            return (r.get("fused") and not r["null"] and r["value"] == max(0, m) and (m > 0) == positive
                    and r["noise"] == max(RM, abs(m)) and key not in dict(notes(d_now[0], out))["note_bimodal"])
        return pred
    fused_bound = bound_at(FK)
    def unfused_code(d):       # the l1/c1 code compiled un-fused: the fact follows the timed code, nothing declared
        _synth_launches(d, "J4", j4, ())
        _synth_pin(d)
        set_delta(d, FK, ALLNEG)
    def unstable(d):           # launch 3 alone compiled un-fused (its manifest and the record's pin follow it)
        _synth_launches(d, "J4", j4, (), launches=[3])
        _synth_pin(d)
    def recompiled(variant, key=None):   # [r11] J4 recompiled with `variant`, manifest and pin following; KEY all-negative
        def plant(d):
            _synth_launches(d, "J4", j4, SYNTH_FUSED, variant=variant)
            _synth_pin(d)
            if key:
                set_delta(d, key, ALLNEG)
        return plant
    def exe_swapped(d):        # [r11-REV15-1] P3: launch 3's executable un-fused, its manifest NOT rewritten
        _synth_launches(d, "J4", j4, (), launches=[3], manifest=False)
    def manifest_rewritten(d): # [r11-REV15-1] the manifest rewritten to match, the record's pin not
        _synth_launches(d, "J4", j4, (), launches=[3])
    def unpinned(d):           # [r11-REV15-1] a record finalized before the pin (windows 1 and 2): checked as it stands
        _synth_pin(d, drop=True)
    def stems_swapped(d):      # [r11-REV15-1] P6: obj/tab.c's stems of l1.p0 and w1.p0 swapped
        p = os.path.join(d, "J4", "obj", "tab.c")
        t = open(p).read()
        a, b = (re.search(r'"%s", K_CMP, (a\d+)_time' % re.escape(k), t).group(1) for k in (FK, "kit.verify_cmp.rc-words.w1.p0"))
        open(p, "w").write(t.replace(" %s_time" % a, " TMP_time").replace(" %s_time" % b, " %s_time" % a).replace(" TMP_time", " %s_time" % b))
    def wear(d):               # the derivation hands every class the fact: the bytes' reading must refuse it
        global FUSED_DERIVE
        FUSED_DERIVE = lambda ins: True
    cases = [
        ("complete", lambda d: None, "ok"),
        ("[R15-1] a fused class negative on all six: measured 0, noise max(r_max, |med|), no bimodal note",
         lambda d: set_delta(d, FK, ALLNEG), fused_bound),
        ("[R15-1, r11-REV15-5] a fused class priced positive: bound, value its median (a lower bound), noise max(r_max, |med|)",
         lambda d: set_delta(d, FK, [1000, 1010, 990, 1005, 995, 1020, 1000]), bound_at(FK, positive=True)),
        ("[R15-1] a class NOT fused negative on all six: null (REV14-1 holds)",
         lambda d: set_delta(d, VK, ALLNEG),
         row(lambda r: r["null"] and not r.get("fused") and "all six trimmed" in r["why"])),
        ("[R15-1] the fused class compiled un-fused: null (the fact is read from the code)", unfused_code,
         row(lambda r: r["null"] and not r.get("fused") and "all six trimmed" in r["why"], FK)),
        ("[R15-1] the fact differing between launches", unstable, "refused:FUSED-FACT UNSTABLE"),
        ("[R15-1] a non-fused class wearing the fact", wear, "refused:FUSED-FACT MISMATCH"),
        ("[r11-REV15-1] a launch executable not the manifest's (P3)", exe_swapped, "refused:MANIFEST MISMATCH job J4: launch 3"),
        ("[r11-REV15-1] the manifest rewritten to match, the record's pin not", manifest_rewritten, "refused:the record pins"),
        ("[r11-REV15-1] a record pinning no manifest: checked as it stands, named",
         unpinned, lambda out: compute(d_now[0])[5]["J4"][1] is False),
        ("[r11-REV15-1] obj/tab.c's stems swapped (P6)", stems_swapped, "refused:STEM MISMATCH"),
        ("[r11-REV15-2] c1 compiled as two fused compares: not fused, null",
         recompiled({"c1": "two"}, CK), row(lambda r: r["null"] and not r.get("fused") and "all six trimmed" in r["why"], CK)),
        ("[r11-REV15-3] l1 compiled as cmp %reg,(s,i) (L 8): bound", recompiled({"l1": "l8"}, FK), fused_bound),
        ("[r11-REV15-3] c1 compiled through a computed pointer, no index: bound", recompiled({"c1": "ptr"}, CK), bound_at(CK)),
        ("[r11-REV15-10] a null base compiled fused", recompiled({"base.null.l1": "fused"}), "refused:FUSED-FACT BASE"),
        ("[R14-2] a verify row at zero, signs mixed: sub-resolution, measured",
         lambda d: set_delta(d, VK, [40, -30, 10, -50, 20, -10, 30]), sub),
        ("[r10-REV14-1] negative on all six trimmed launches within r: null (a defect, whatever r)",
         lambda d: set_delta(d, VK, [-20, -60, -10, -40, -30, -90, -25]),
         row(lambda r: r["null"] and not r.get("sub") and "all six trimmed" in r["why"])),
        ("[r10-REV14-1] signs mixed, a negative median within r: measured, its value clamped to 0",
         lambda d: set_delta(d, VK, [-20, 30, -10, -40, 25, -90, -25]), row(lambda r: bool(r.get("sub")) and r["value"] == 0)),
        ("[R14-2] consistently negative above r: null (a fixture artifact)",
         lambda d: set_delta(d, VK, [-1000, -1010, -990, -1005, -995, -1020, -1000]),
         row(lambda r: r["null"] and not r.get("sub") and "negative" in r["why"])),
        ("[r10-REV14-2] signs mixed, |med| within its own r but above r_max: null",
         lambda d: set_delta(d, VK, [3 * RM // 2, -3 * RM, 4 * RM, 3 * RM // 2, -2 * RM, 5 * RM, 7 * RM // 5]),
         row(lambda r: r["null"] and not r.get("sub") and abs(r["value"]) <= resolution(r["x"]) and abs(r["value"]) > RM)),
        ("[r10-REV14-2] signs mixed, |med| within r_max below its own r: sub-resolution, r capped",
         lambda d: set_delta(d, VK, [RM // 2, -3 * RM, 4 * RM, RM // 2, -2 * RM, 5 * RM, 2 * RM // 5]),
         row(lambda r: bool(r.get("sub")) and r["sub"] == RM and resolution(r["x"]) > RM)),
        ("[r10-REV14-2] within r, its paired A/A above r: null",
         lambda d: set_delta(d, VK, [40, -30, 10, -50, 20, -10, 30], twin=[0, 200, -200, 200, -200, 200, -200]),
         row(lambda r: r["null"] and not r.get("sub") and "paired A/A" in r["why"] and r["aa"] > resolution(r["x"]))),
        ("[r10-REV14-2] within r, its paired A/A at r: sub-resolution",
         lambda d: set_delta(d, VK, [40, -30, 10, -50, 20, -10, 30], twin=[0, 30, -30, 30, -30, 30, -30]),
         row(lambda r: bool(r.get("sub")) and 0 < r["aa"] <= r["sub"])),
        ("[r10-REV14-2] the live r_max moved after the run: the pinned r_max rules", policy_moved, sub),
        ("[r10-REV14-2] a record pinning no r_max: the live row, named",
         unpin_rmax, lambda out: sub(out) and r_max(read_record(d_now[0]))[1].startswith("NOT pinned")),
        ("[R14-2] signs mixed at a size above r: null",
         lambda d: set_delta(d, VK, [1000, 1000, 1000, 1000, -50, -600, 1000]),
         row(lambda r: r["null"] and not r.get("sub") and "signs mixed" in r["why"])),
        ("[R14-2] a priced verify row keeps the NULL rule's value (no clamp, no r)",
         lambda d: set_delta(d, VK, [1000, 1010, 990, 1005, 995, 1020, 1000]),
         row(lambda r: not r["null"] and not r.get("sub") and r["value"] > 0)),
        ("[R14-4] a delta row in two clusters is named by the bimodal note",
         lambda d: set_delta(d, VK, [1000, 1000, 1000, 1500, 1500, 1500, 1000]),
         lambda out: VK in dict(notes(d_now[0], out))["note_bimodal"]),
        ("leftover cells of a never-ran job", set_never, "refused"),
        ("a planned cell missing", lambda d: edit(os.path.join(d, "cells.J3.tsv"), drop_line), "refused"),
        ("a cells file of another run", lambda d: edit(os.path.join(d, "cells.J4.tsv"),
                                                       lambda t: t.replace("#run_id\tselftest", "#run_id\tother", 1)), "refused"),
        ("a delta cell naming another base", lambda d: edit(os.path.join(d, "cells.J3.tsv"), base_swap), "refused"),
        ("an id disagreeing with its launch column", lambda d: edit(os.path.join(d, "cells.J2.tsv"),
            lambda t: re.sub(r"(J2\.unit/kit\.find_byte\.walk/65536/)4(\t)", r"\g<1>5\2", t, count=1)), "refused"),
        ("a record pinning no policy values", unpin, "refused"),
        ("a unit twin skewed (the baseline of the next case)", unit_twin_skew, "ok"),
        ("live card/policy edit after the run", live_edit, "same"),
    ]
    # `same`: the record and cells equal the previous case's byte for byte, only the LIVE tables differ (the
    # plant edits plan.CARD in memory, restored after), and the outcome must be the previous case's
    bad, prev = 0, None
    live = {q: dict(c) for q, c in plan.CARD.items()}
    d_now = [None]
    for name, plant, want in cases:
        d = d_now[0] = _synth(os.path.join(scratch, "est_selftest"))
        def state():           # the record, the cells and [rev1.5 R15-1] the timed code
            return open(os.path.join(d, "run_record.tsv")).read() + "".join(
                open(os.path.join(d, f)).read() for f in sorted(os.listdir(d)) if f.startswith("cells.")) + "".join(
                hashlib.sha256(open(os.path.join(d, "J4", "L%d" % l, "J4.L%d" % l), "rb").read()).hexdigest()
                for l in range(1, plan.L_LAUNCHES + 1)) + "".join(
                open(os.path.join(d, "J4", f)).read() for f in ("manifest.tsv", os.path.join("obj", "tab.c")))
        before = state()
        plant(d)
        after = state()
        if not isinstance(want, str):       # a row predicate over compute()'s rows (rev 1.4)
            try:
                ok = bool(want(compute(d)[0]))
            except (InputError, KeyError) as e:
                ok = False
                print("selftest\t%s\t(%s)" % (name, e))
            finally:
                plan.POLICY = live_policy
            bad += not ok
            print("selftest\t%s\t%s" % (name, "ok" if ok else "WRONG"))
            continue
        if want != "ok" and before == after and plan.CARD == live and FUSED_DERIVE is fused_text:
            print("selftest\t%s\tPLANT DID NOT APPLY" % name)
            bad += 1
            continue
        try:
            outcome = compute(d)[3]
            got = "ok"
            why = "%s exit %d" % outcome[:2]
        except InputError as e:
            outcome, got, why = None, "refused", str(e)
        finally:
            for q, c in live.items():
                plan.CARD[q].clear()
                plan.CARD[q].update(c)
            globals()["FUSED_DERIVE"] = fused_text
        if want == "same":
            got = "same" if outcome is not None and prev is not None and outcome[:2] == prev[:2] and after == prev_after else "moved"
            why += " (the previous case's: %s)" % ("%s exit %d" % prev[:2] if prev else "none")
        prev, prev_after = outcome, after
        # `refused:TEXT`: refused, and its refusal names TEXT (the check that was meant, not an earlier one)
        ok = got == want.split(":")[0] and (":" not in want or want.split(":", 1)[1] in why)
        bad += not ok
        print("selftest\t%s\t%s\t%s (%s)" % (name, "ok" if ok else "WRONG", got, why[:150]))
    for name, got, want in _reading_cases(scratch):          # [r11-REV15-2..4]
        ok = got == want
        bad += not ok
        print("selftest\t[r11 reading] %s\t%s\t(text, bytes) %s" % (name, "ok" if ok else "WRONG", got))
    for name, case, want in GATE_CASES:                     # [rev1.5 R15-2, r11-REV15-6/7]
        c0, paths = _gate_repo(scratch, case)
        try:
            draft_gate(c0, paths)
            got, why = "ok", "a draft"
        except InputError as e:
            got, why = "refused", str(e)
        ok = got == want.split(":")[0] and (":" not in want or want.split(":", 1)[1] in why)
        bad += not ok
        print("selftest\t[r11 gate] %s\t%s\t%s (%s)" % (name, "ok" if ok else "WRONG", got, why[:150]))
    n = len(cases) + len(READING_CASES) + len(GATE_CASES)
    print("== est SELFTEST %s: %d cases, %d wrong" % ("ok" if not bad else "FAILED", n, bad))
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
