# One instance for every n <= N at once: is there a good colouring of [1,n] (no rainbow 3-AP, no monochromatic
# l-AP) using at least C colours, for SOME n in [C, N]? act_i = "point i is inside [1,n]" (act_{i+1} -> act_i).
# Every clause is valid for a real colouring of [1,n] with its prefix indicator, so UNSAT proves: for no n <= N.
# Transitivity is added lazily (CEGAR); UNSAT of the subset used is a valid proof. Usage: gw_prefix.py N l C out.cnf
import sys, time, itertools
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
N, l, C, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
pool = IDPool()
e = lambda i, j: pool.id(('e', min(i, j), max(i, j)))
act = lambda i: pool.id(('a', i))
rep = lambda i: pool.id(('r', i))
for i, j in itertools.combinations(range(N), 2): e(i, j)
for i in range(N): act(i); rep(i)
base = []
for i in range(N - 1): base.append([-act(i + 1), act(i)])
base.append([act(C - 1)])
for a in range(N):
    for d in range(1, N):
        if a + 2 * d < N: base.append([-act(a + 2 * d), e(a, a + d), e(a + d, a + 2 * d), e(a, a + 2 * d)])
        if a + (l - 1) * d < N: base.append([-act(a + (l - 1) * d)] + [-e(a + j * d, a + (j + 1) * d) for j in range(l - 1)])
for i in range(N):
    base.append([-rep(i), act(i)])
    for j in range(i): base.append([-rep(i), -e(j, i)])
    base.append([rep(i), -act(i)] + [e(j, i) for j in range(i)])
base += CardEnc.atleast(lits=[rep(i) for i in range(N)], bound=C, vpool=pool, encoding=EncType.seqcounter).clauses
used = list(base); t0 = time.time(); it = 0
with Solver(name='cadical195', bootstrap_with=base) as s:
    while True:
        it += 1
        if not s.solve():
            print(f'iter {it}: UNSAT, {len(used) - len(base)} transitivity clauses ({time.time()-t0:.0f}s)', flush=True); res = 'UNSAT'; break
        m = set(x for x in s.get_model() if x > 0)
        val = lambda i, j: e(i, j) in m
        n = sum(1 for i in range(N) if act(i) in m)
        adj = [[j for j in range(N) if j != i and val(i, j)] for i in range(N)]
        new = []
        for k in range(N):
            nb = adj[k]
            for x in range(len(nb)):
                for y in range(x + 1, len(nb)):
                    if not val(nb[x], nb[y]): new.append([-e(nb[x], k), -e(k, nb[y]), e(nb[x], nb[y])])
        if not new:
            print(f'iter {it}: SAT: a good colouring of [1,{n}] with >= {C} colours exists', flush=True); res = 'SAT'; break
        for c in new: s.add_clause(c)
        used += new
        print(f'iter {it}: +{len(new)} (total {len(used) - len(base)}, {time.time()-t0:.0f}s)', flush=True)
if res == 'UNSAT':
    with open(out, 'w') as f:
        f.write(f'p cnf {pool.top} {len(used)}\n')
        for c in used: f.write(' '.join(map(str, c)) + ' 0\n')
    print('wrote', out, pool.top, 'vars', len(used), 'clauses')
