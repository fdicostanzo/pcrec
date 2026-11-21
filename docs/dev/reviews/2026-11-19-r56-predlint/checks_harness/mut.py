import os, shutil, subprocess, sys, json
L="/var/tmp/pcrec-pcrec/scratch/crit-predlint/checks"
BASE=L+"/base"
env=dict(os.environ, PCREC_TMPDIR=L)
src=open(BASE+"/scripts/pred_doc_lint.py").read()
M=[]
def m(name, old, new, count=1): M.append((name, old, new, count))
# L1
m("L1 dup tag off", "if tag in seen_tags:", "if False:")
m("L1 dup section off", "if sec in seen_secs:", "if False:")
# L2
m("L2 malformed piece fail off", 'rep.fail("L2", where, p["malformed"])', "pass")
m("L2 TAG_RE off", "if not TAG_RE.match(tag):", "if False:")
m("L2 tag-file-word mismatch off", 'if tag.split("/")[0] != word:', "if False:")
m("L2 tag-in-section off", 'elif p["section"] is None or "/".join(tag.split("/")[:2]) != p["section"][0]:', "elif False:")
m("L2 section tag grammar/word off", 'if not SECTION_RE.match(sec) or sec.split("/")[0] != word:', "if False:")
m("L2 malformed section heading fail off", 'rep.fail("L2", "%s:%d" % (b, ln), msg)', "pass")
m("L2 was: always excuses", 'elif p["was"] is None:', "elif False:")
m("L2 sub-tag 4th level not allowed (grammar)", '(?:/%s)?$" % (SEG, SEG, SEG))', '$" % (SEG, SEG))')
# L3
m("L3 base w/o entry off", "if t not in sd:", "if False:")
m("L3 entry w/o base off", 'if e["tag"] not in sb:', "if False:")
m("L3 order off", "if sb == sd and bt != dt and len(bt) == len(dt):", "if False:")
m("L3 details absent off", 'rep.fail("L3", d, "details file absent for existing base %s" % P["base"])', "pass")
m("L3 malformed entry heading off", 'rep.fail("L3", "%s:%d" % (d, ln), msg)', "pass")
# L4
m("L4 no date off", "rep.fail(\"L4\", where, \"no status date (want '<status> YYYY-MM-DD')\")", "pass")
m("L4 bad date off", 'rep.fail("L4", where, "bad status date %s" % date)', "pass")
m("L4 open slug off", 'if not st.startswith("open ") or not SLUG_RE.match(sl):', "if False:")
m("L4 open: drop SLUG_RE half", 'if not st.startswith("open ") or not SLUG_RE.match(sl):', 'if not st.startswith("open "):')
m("L4 open: drop 'open ' half", 'if not st.startswith("open ") or not SLUG_RE.match(sl):', 'if not SLUG_RE.match(sl):')
m("L4 status set off", "elif st not in STATUSES:", "elif False:")
m("L4 parked only in parked off", 'elif st == "parked" and word != "parked":', "elif False:")
m("L4 ruled no rulings off", "if not items:", "if False:")
m("L4 item w/o record off", 'rulings item without (record: "<entry title>")', "XX")  # placeholder replaced below
m("L4 record absent file off", 'rep.fail("L4", d, "record %s absent: cannot check titles" % RECORD)', "pass")
m("L4 title not found off", 'if " ".join(m.group(1).split()) not in titles:', "if False:")
m("L4 title whitespace-normalise off", 'if " ".join(m.group(1).split()) not in titles:', "if m.group(1) not in titles:")
m("L4 non-ruled pieces also need rulings", 'if p["status"] != "ruled" or e is None:', 'if e is None:')
# L5
m("L5 names-no-piece off", 'rep.fail("L5", where, "%s: %s names no piece" % (kind, t))', "pass")
m("L5 by not principle off", 'if kind == "by" and not t.startswith("core/principles/"):', "if False:")
m("L5 later file off", "if RANK[tw] > RANK[word]:", "if False:")
m("L5 later in file off", "elif tw == word and own and tn >= own[1]:", "elif False:")
m("L5 self-needs allowed (>= to >)", "tn >= own[1]", "tn > own[1]")
m("L5 skipped-pair excuse removed", "continue  # its pair was skipped: unresolvable, not a fault", "pass")
m("L5 skipped-pair excuse always", "if tw in RANK and tw not in pairs and not require_all:", "if tw in RANK and tw not in pairs:")
m("L5 by: tag missing => treated ok when in index but non-principle later", 'for kind in ("needs", "by"):', 'for kind in ("needs",)')
# L6
for w in ["WITHDRAWN","REVERSED","SUPERSEDED"]:
    m("L6 word %s removed"%w, "|%s"%w, "")
m("L6 [REV removed", r"\[REV|", "")
m("L6 review rN removed", "|(?i:review r\\d+|rev \\d+)", "|(?i:rev \\d+)")
m("L6 rev N removed", "|(?i:review r\\d+|rev \\d+)", "|(?i:review r\\d+)")
m("L6 case-insensitivity off", "(?i:review r\\d+|rev \\d+)", "(?:review r\\d+|rev \\d+)")
m("L6 fence exempt off", 'if infence:\n                continue\n            rep.ok("L6")', 'rep.ok("L6")')
m("L6 whole check off", 'rep.fail("L6", "%s:%d" % (b, i + 1)', 'print("", ')
# L7
m("L7 piece cap 40->41", "PIECE_MAX = 200, 40", "PIECE_MAX = 200, 41") if False else None
m("L7 PIECE_MAX 40->41", "STATEMENT_MAX, PIECE_MAX = 200, 40", "STATEMENT_MAX, PIECE_MAX = 200, 41")
m("L7 PIECE_MAX 40->39", "STATEMENT_MAX, PIECE_MAX = 200, 40", "STATEMENT_MAX, PIECE_MAX = 200, 39")
m("L7 STATEMENT_MAX 200->201", "STATEMENT_MAX, PIECE_MAX = 200, 40", "STATEMENT_MAX, PIECE_MAX = 201, 40")
m("L7 STATEMENT_MAX 200->199", "STATEMENT_MAX, PIECE_MAX = 200, 40", "STATEMENT_MAX, PIECE_MAX = 199, 40")
m("L7 piece lines off-by-one (+1 miscount)", 'nlines = p["end"] - p["line"] + 1', 'nlines = p["end"] - p["line"]')
m("L7 no-statement fail off", 'rep.fail("L7", where, "no statement line (only a \'?\' piece may lack one)")', "pass")
m("L7 '?' exempt widened (all may lack)", "if not is_q:\n                    rep.fail", "if False:\n                    rep.fail")
m("L7 soft cap warn off", 'if P["size"] > caps[word]:', "if False:")
m("L7 CAPS core 64K->1K", '"core": 64 * 1024', '"core": 1024')
m("L7 CAPS lib 24K->1K", '"lib": 24 * 1024', '"lib": 1024')
m("L7 CAPS parked 16K->1K", '"parked": 16 * 1024', '"parked": 1024')
m("L7 soft cap becomes hard", 'rep.warns.append("L7 %s: base file', 'rep.fail("L7", b, "x"); rep.warns.append("L7 %s: base file')
# L8
m("L8 fail off", 'rep.fail("L8", where,', 'print("", ')
m("L8 exempt '?' removed", "if not is_q and st not in", "if st not in")
m("L8 exempt parked removed", 'st not in ("parked", "under-construction")', 'st not in ("under-construction",)')
m("L8 exempt under-construction removed", 'st not in ("parked", "under-construction")', 'st not in ("parked",)')
m("L8 exempt principles removed", ' and not tag.startswith("core/principles/")', "")
m("L8 principles exemption widened to all core", 'not tag.startswith("core/principles/")', 'not tag.startswith("core/")')
m("L8 all->any modes", 'all(w in t for w in ("WHOLE", "SEARCHED", "FIND-ALL"))', 'any(w in t for w in ("WHOLE", "SEARCHED", "FIND-ALL"))')
m("L8 drop FIND-ALL requirement", '("WHOLE", "SEARCHED", "FIND-ALL"))', '("WHOLE", "SEARCHED"))')
m("L8 drop SEARCHED requirement", '("WHOLE", "SEARCHED", "FIND-ALL"))', '("WHOLE", "FIND-ALL"))')
m("L8 modes: n/a without why accepted/no startswith", 't.startswith("modes: n/a")', 'False')
m("L8 example searched in heading line too", "body = p[\"text\"][1:]", "body = p[\"text\"]")
# L9
m("L9 kebab slug check off", 'rep.fail("L9", "%s:%d" % (P["details"], ln), "slug \'%s\' is not lower-case kebab" % s)', "pass")
m("L9 shared exemption always", "if len(tags) > 1 and s not in shared:", "if False:")
m("L9 shared exemption never", "if len(tags) > 1 and s not in shared:", "if len(tags) > 1:")
m("L9 shared only from same file (cross-file)", 'shared.update(P["dp"]["shared"])', "pass")
m("L9 none/- skip removed", 's in ("none", "-")', "False")
m("L9 tags>1 -> >2", "if len(tags) > 1 and", "if len(tags) > 2 and")
m("L9 cross-file collisions not seen (owners per file)", "owners.setdefault(s, [])", "owners.setdefault((s, P['details']), [])") if False else None
# L10
m("L10 ratchet fail off", 'rep.fail("L10", P["base"],', 'print("", ')
m("L10 > to >= (equality fails)", 'P["qcount"] > rat[word]', 'P["qcount"] >= rat[word]')
m("L10 > to >+1 slack", 'P["qcount"] > rat[word]', 'P["qcount"] > rat[word] + 1')
m("L10 qcount counts nothing", 'qn = sum(1 for p in bp["pieces"] if p["status"] == "?")', "qn = 0")
m("L10 absent ratchet is fatal->silent (note removed)", 'rep.notes.append("L10: %s absent: ratchet not checked" % RATCHET)', "pass")
m("L10 ratchet per-word lookup (only core)", "if word in rat:", 'if word in rat and word == "core":')
m("L10 write_ratchet raises (min -> max)", "new[word] = min(old.get(word, P[\"qcount\"]), P[\"qcount\"])", "new[word] = max(old.get(word, P[\"qcount\"]), P[\"qcount\"])")
m("L10 write_ratchet ignores old", "new[word] = min(old.get(word, P[\"qcount\"]), P[\"qcount\"])", "new[word] = P[\"qcount\"]")
# L11
m("L11 no pieces off", 'rep.fail("L11", b, "no pieces (a base file with none is vacuous)")', "pass")
m("L11 no entries off", 'rep.fail("L11", P["details"], "no entries (a details file with none is vacuous)")', "pass")
m("L11 require-all absent off", 'rep.fail("L11", b, "base file absent (--require-all)")', "pass")
m("L11 whole-run nothing present silent", 'rep.notes.append("no pair present: nothing linted")', "pass")
m("L11 count of 'checked' not incremented", 'rep.ok("L11")', "pass")
# selftest machinery
m("ST plant exact-rule -> 'rule in got'", "if got == {rule}:", "if rule in got:")
m("ST plant: any failure counts", "if got == {rule}:", "if got:")
m("ST clean control off", 'expect(not rep.fails, "clean sample fails: %r" % rep.fails)', "pass")
m("ST floors off", "expect(rep.checked[r] >= f,", "expect(True or rep.checked[r] >= f,")
m("ST covered-all check off", 'expect(r in covered, "rule %s has no detected plant" % r)', "pass")
m("ST plant text sub no count check", 'raise SystemExit("selftest: plant text', 'pass #')
m("ST was: control off", 'expect(not rep.fails, "was: line did not excuse', 'expect(True, "was: line did not excuse')
m("ST fence control off", 'expect(not rep.fails, "a fenced history word was not exempt', 'expect(True, "a fenced')
m("ST L8 exemptions control off", 'expect(not rep.fails, "L8 exemption for a', 'expect(True, "L8 exemption for a')
m("ST skip control off", 'expect(not rep.fails and any("skip parked" in x for x in rep.notes), "an absent pair was not skipped")', "pass")
m("ST require-all control off", 'expect(rep.rules_failed() == {"L11"}', 'expect(True or rep.rules_failed() == {"L11"}')
m("ST noratchet control off", 'expect(not rep.fails and any(x.startswith("L10") for x in rep.notes), "an absent', 'expect(True, "an absent')
m("ST soft control off", 'expect(not rep.fails and any(w.startswith("L7") for w in rep.warns), "soft cap', 'expect(True, "soft cap')
m("ST write-ratchet controls off", 'expect(read_ratchet(os.path.join(d, RATCHET)).get("core") == 1', 'expect(True or read_ratchet(os.path.join(d, RATCHET)).get("core") == 1')
m("ST write-ratchet raise control off", 'expect(read_ratchet(os.path.join(d, RATCHET)).get("core") == 0', 'expect(True or read_ratchet(os.path.join(d, RATCHET)).get("core") == 0')
m("ST committed sample control off", 'expect(not rep.fails, "committed sample is not clean', 'expect(True, "committed')
M=[x for x in M if x]
only=sys.argv[1:]
res=[]
for i,(name,old,new,cnt) in enumerate(M):
    if only and str(i) not in only: continue
    if old not in src and old!="":
        print("%3d NOMATCH %s"%(i,name)); continue
    s=src.replace(old,new) if old.count else src
    d=L+"/mut/m%d"%i
    shutil.rmtree(d,ignore_errors=True); shutil.copytree(BASE,d)
    open(d+"/scripts/pred_doc_lint.py","w").write(s)
    def run(args):
        try:
            r=subprocess.run(["python3","-I",d+"/scripts/pred_doc_lint.py"]+args,env=env,capture_output=True,text=True,timeout=60)
            return r.returncode, r.stdout+r.stderr
        except Exception as e: return -9,str(e)
    a,ao=run(["--selftest"])
    b,bo=run(["--root",d+"/scripts/tests/pred_doc/root","--require-all"])
    n=src.count(old)
    print("%3d st=%s sample=%s %s%s"%(i,"GREEN" if a==0 else "red%d"%a,"GREEN" if b==0 else "red%d"%b,name,"" if n==1 else " (matches %d)"%n))
    shutil.rmtree(d,ignore_errors=True)
