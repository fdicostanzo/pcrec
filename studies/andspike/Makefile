# studies/andspike -- never built or run by pcrec's make. Niced, single process.
# PCRE2: ANDSPIKE_PCRE2=/path/libpcre2-8.so overrides the 10.49 oracle build.
PY = nice -n 10 python3 -B

all: cases predicates cost sweeps

cases:
	$(PY) cases.py > results/cases.txt
predicates:
	$(PY) predicates.py demo > results/predicates.txt
	$(PY) predicates.py sweep 200 4 1 >> results/predicates.txt
	ANDSPIKE_SABOTAGE=pred $(PY) predicates.py sweep 50 4 1 >> results/predicates.txt
cost:
	$(PY) cost.py 20 > results/cost.txt
sweeps:
	$(PY) sweep.py cross 200 5 1 > results/cross.txt
	for s in order drop; do echo "## control ANDSPIKE_SABOTAGE=$$s"; \
	  ANDSPIKE_SABOTAGE=$$s $(PY) sweep.py cross 50 5 1 | head -7; done >> results/cross.txt
	$(PY) sweep.py laws 200 4 1 > results/laws.txt

.PHONY: all cases predicates cost sweeps
