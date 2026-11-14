# DIMACS encoder for the GW rows with any number of colours (k4 agent, 12 Nov 2026).
#
# Question: is there an n with nmin <= n <= N and a colouring of [1,n] with no rainbow k-AP and no monochromatic l-AP
# that uses at least cmin and at most cmax colours?  UNSAT means: for no such n.
#
# Colours are numbered in order of first appearance (restricted growth string, RGS): point 1 has colour 0, a point
# carries colour c >= 1 only if colour c-1 occurs at an earlier point, and point i (1-based) has a colour below i.
# Every colouring can be renamed into this form, so nothing is lost. Then "at least C colours on [1,n]" is the same as
# "colour C-1 occurs in [1,n]", and "at most R colours" means colours 0..R-1 only.
#
# Prefix activation (only when nmin < N): act(n) = "the colouring is required to be good on [1,n]"; act(n) -> act(n-1),
# act(nmin) holds, and every AP clause is guarded by act(last point of the AP). Points after n are left free (any real
# colouring of [1,n] extends by colour 0), so every clause holds for a real good colouring of some [1,n], n in range.
#
# Rainbow k-APs: --rainbow perm writes one clause per injective colour assignment (only sensible for few colours);
# --rainbow aux (default) uses same-colour variables s(i,j) with s(i,j) -> (x(i,c) <-> x(j,c)) and one clause
# "s(p,q) for some pair of the AP" per k-AP. Monochromatic l-APs: one clause per AP and colour.
#
# Usage: gw_rgs.py N k l nmin cmin cmax out.cnf [--rainbow perm|aux] [--map out.map]
# The map file lists the variable of every (point, colour) pair, so a model can be decoded (decode_rgs.py).
import sys, itertools

def main():
    a = sys.argv[1:]
    N, k, l, nmin, cmin, cmax = map(int, a[:6]); out = a[6]
    rainbow = 'aux'; mapf = None
    if '--rainbow' in a: rainbow = a[a.index('--rainbow') + 1]
    if '--map' in a: mapf = a[a.index('--map') + 1]
    assert 1 <= nmin <= N and 1 <= cmin <= cmax
    top = [0]
    def new():
        top[0] += 1
        return top[0]
    cols = lambda i: range(min(i + 1, cmax))          # 0-based point i may carry colours 0..min(i, cmax-1)
    x = {(i, c): new() for i in range(N) for c in cols(i)}
    prefix = nmin < N
    act = {n: new() for n in range(nmin, N + 1)} if prefix else {}
    cl = []
    if prefix:
        cl.append([act[nmin]])
        for n in range(nmin + 1, N + 1): cl.append([-act[n], act[n - 1]])
    def guard(last):                                  # literal list guarding an AP whose last 0-based point is `last`
        n = last + 1
        if not prefix or n <= nmin: return []
        return [-act[n]]
    # exactly one colour per point
    for i in range(N):
        cl.append([x[i, c] for c in cols(i)])
        for c1, c2 in itertools.combinations(cols(i), 2): cl.append([-x[i, c1], -x[i, c2]])
    # restricted growth: colour c >= 1 at i needs colour c-1 before i
    cl.append([x[0, 0]])
    for i in range(1, N):
        for c in cols(i):
            if c >= 1: cl.append([-x[i, c]] + [x[j, c - 1] for j in range(c - 1, i)])
    # monochromatic l-APs
    for s0 in range(N):
        for d in range(1, N):
            last = s0 + (l - 1) * d
            if last >= N: break
            pts = [s0 + j * d for j in range(l)]
            for c in cols(pts[0]):
                cl.append(guard(last) + [-x[p, c] for p in pts])
    # rainbow k-APs
    same = {}
    def s(i, j):
        if (i, j) not in same:
            v = new(); same[i, j] = v
            for c in cols(j):                          # i < j, so cols(i) is a prefix of cols(j)
                if c < min(i + 1, cmax):
                    cl.append([-v, -x[i, c], x[j, c]]); cl.append([-v, -x[j, c], x[i, c]])
                else:
                    cl.append([-v, -x[j, c]])
        return same[i, j]
    if k <= cmax:
        for s0 in range(N):
            for d in range(1, N):
                last = s0 + (k - 1) * d
                if last >= N: break
                pts = [s0 + j * d for j in range(k)]
                if rainbow == 'aux':
                    cl.append(guard(last) + [s(p, q) for p, q in itertools.combinations(pts, 2)])
                else:
                    for cs in itertools.permutations(range(cmax), k):
                        if all(c in cols(p) for p, c in zip(pts, cs)):
                            cl.append(guard(last) + [-x[p, c] for p, c in zip(pts, cs)])
    # at least cmin colours inside the active prefix: colour cmin-1 occurs at some point i with act(i+1)
    if cmin >= 2:
        ys = []
        for i in range(cmin - 1, N):
            y = new(); ys.append(y)
            cl.append([-y, x[i, cmin - 1]])
            if prefix and i + 1 > nmin: cl.append([-y, act[i + 1]])
        cl.append(ys)
    with open(out, 'w') as f:
        f.write(f'c gw_rgs.py N={N} k={k} l={l} nmin={nmin} cmin={cmin} cmax={cmax} rainbow={rainbow}\n')
        f.write(f'p cnf {top[0]} {len(cl)}\n')
        for c in cl: f.write(' '.join(map(str, c)) + ' 0\n')
    if mapf:
        with open(mapf, 'w') as f:
            for (i, c), v in sorted(x.items()): f.write(f'{i} {c} {v}\n')
            for n, v in sorted(act.items()): f.write(f'act {n} {v}\n')
    print(f'wrote {out}: {top[0]} vars, {len(cl)} clauses', file=sys.stderr)

main()
