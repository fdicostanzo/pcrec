import re,sys
R='/var/tmp/pcrec-pcrec/scratch/crit-predspec22/subject/'
rec=open(R+'COND-FAMILY.md').read()
norm=lambda s:re.sub(r'\s+',' ',s.replace('\\"','"'))
recn=norm(rec)
pref=("match-context","zero-pass","mark-in-none","not-is-complement","P & (k","Would it","I agree","I think I see","In my reading","Isn't that","This makes sense","spelling-phrasing","mark-domain","anywhere","This does need","two patterns that","If nothing","It's not the","Logic aside","I'm assuming","one value set","the semantic","If there","You could","The issue","It's obscure","sorry","labels that go","such logic","absent-rule","optional-as-loop")
for fn in sys.argv[1:]:
  tn=norm(open(R+fn).read())
  for m in re.finditer(r'"((?:[^"\\]|\\.){6,400}?)"',tn):
    q=m.group(1).replace('\\"','"')
    if any(q.startswith(p) for p in pref):
      if norm(q) in recn: print(fn,'OK',repr(q[:60]))
      else:
        parts=[p.strip() for p in re.split(r'\.\.\.|…',q) if p.strip()]
        print(fn,'ELLIPSIS-OK' if all(norm(p) in recn for p in parts) else 'MISS',repr(q[:220]))
