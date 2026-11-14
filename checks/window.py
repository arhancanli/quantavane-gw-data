# Window search for Lemma 5.3 of the paper (written for papers/gw-2026, 12 Nov 2026).
# For k = 3: if a good colouring uses at least R colours, a minimal window [a, a+L] has L odd and its interior
# x -> c(a+x), 1 <= x <= L-1, is a good colouring with exactly R-2 colours that is constant on the orbits of
# x -> 2x mod L. This program decides, for each odd L in [3, Lmax], whether such an interior colouring exists
# (exhaustive backtracking over colourings of the doubling orbits, colours in order of first appearance).
# Usage: python3 -I window.py l R Lmax     (k = 3; prints every odd L with a solution, then a summary line)
import sys
sys.setrecursionlimit(10000)
l, R, Lmax = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
C = R - 2
def orbits(L):
    seen, out = set(), []
    for x in range(1, L):
        if x in seen: continue
        o, y = [], x
        while y not in o:
            o.append(y); y = (2 * y) % L
        seen.update(o); out.append(sorted(o))
    return out
def search(L):
    orbs = orbits(L)
    orbs.sort(key=lambda o: o[0])            # orbit of the smallest point first
    n = L - 1
    col = [-1] * (n + 1)
    # progressions through each point, inside [1, n]
    aps3 = {x: [] for x in range(1, n + 1)}
    apsl = {x: [] for x in range(1, n + 1)}
    for a in range(1, n + 1):
        for d in range(1, n):
            if a + 2 * d <= n:
                t = (a, a + d, a + 2 * d)
                for x in t: aps3[x].append(t)
            if a + (l - 1) * d <= n:
                t = tuple(a + j * d for j in range(l))
                for x in t: apsl[x].append(t)
            if a + 2 * d > n and a + (l - 1) * d > n: break
    found = []
    def ok(orb):
        for x in orb:
            for t in aps3[x]:
                cs = [col[y] for y in t]
                if -1 not in cs and len(set(cs)) == 3: return False
            for t in apsl[x]:
                c0 = col[t[0]]
                if c0 != -1 and all(col[y] == c0 for y in t): return False
        return True
    def rec(i, used):
        if found: return
        if used + (len(orbs) - i) < C: return
        if i == len(orbs):
            if used == C: found.append(list(col[1:]))
            return
        for c in range(min(used + 1, C)):
            for x in orbs[i]: col[x] = c
            if ok(orbs[i]): rec(i + 1, max(used, c + 1))
            for x in orbs[i]: col[x] = -1
    rec(0, 0)
    return found[0] if found else None, len(orbs)
hits = []
for L in range(3, Lmax + 1, 2):
    sol, no = search(L)
    if sol is not None:
        hits.append(L)
        print(f'L={L} orbits={no} interior colouring with exactly {C} colours: {"".join(map(str, sol))}', flush=True)
print(f'k=3 l={l} R={R} odd L in [3,{Lmax}]: windows found at L = {hits if hits else "none"}')
