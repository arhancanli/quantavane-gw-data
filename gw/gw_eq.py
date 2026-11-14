# Colourings of [1,n] with ANY number of colours, as equivalence relations: e(i,j) = "i and j share a colour".
# No rainbow k-AP (k = 3): some pair of its 3 terms shares a colour. No monochromatic l-AP: not all consecutive pairs equal.
# Also: max number of colours in a good colouring (classes = points i with no j < i of the same colour).
import sys, itertools
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
def build(n, l, min_colours=0):
    pool = IDPool(); e = lambda i, j: pool.id(('e', min(i, j), max(i, j)))
    cl = []
    for i, j, k in itertools.combinations(range(n), 3):      # transitivity
        cl += [[-e(i, j), -e(j, k), e(i, k)], [-e(i, j), -e(i, k), e(j, k)], [-e(i, k), -e(j, k), e(i, j)]]
    for a in range(n):
        for d in range(1, n):
            if a + 2 * d < n:
                p = [a, a + d, a + 2 * d]
                cl.append([e(p[0], p[1]), e(p[1], p[2]), e(p[0], p[2])])
            if a + (l - 1) * d < n:
                cl.append([-e(a + j * d, a + (j + 1) * d) for j in range(l - 1)])
    if min_colours:
        rep = []
        for i in range(n):
            r = pool.id(('rep', i)); rep.append(r)
            for j in range(i): cl.append([-r, -e(j, i)])      # rep -> no earlier point of its colour
            cl.append([r] + [e(j, i) for j in range(i)])        # not rep -> some earlier point of its colour
        enc = CardEnc.atleast(lits=rep, bound=min_colours, vpool=pool, encoding=EncType.seqcounter)
        cl += enc.clauses
    return cl, pool
if __name__ == '__main__':
    n, l, mc = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    cl, pool = build(n, l, mc)
    f = CNF(from_clauses=cl)
    out = sys.argv[4] if len(sys.argv) > 4 else None
    if out: f.to_file(out); print('wrote', out, 'vars', f.nv, 'clauses', len(f.clauses))
    else:
        from pysat.solvers import Solver
        with Solver(name='cadical195', bootstrap_with=cl) as s: print(f'n={n} l={l} min_colours={mc}:', 'SAT' if s.solve() else 'UNSAT')
