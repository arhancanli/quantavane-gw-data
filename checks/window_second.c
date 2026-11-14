/* Second, separately written window search (written by an independent referee agent on 12 Nov 2026; searches
   colourings with AT LEAST R-2 colours, a superset of the exactly-(R-2) case of Lemma 5.3). Kept unchanged below. */
/* C version of window.py: for k=3, search odd L <= Lmax for colourings of
   [1,L-1] constant on orbits of x -> 2x mod L, (3,l)-good, with >= need colours.
   Such a colouring plus two unique colours at 0 and L is a good colouring of
   [0,L] with >= need+2 colours, and every good colouring with >= R colours
   contains such a window with need = R-2 (Lemma 2.4 + doubling).
   Usage: ./window l R Lmin Lmax */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXL 20000
static int L, ELL, NEED, n;
static int orb[MAXL], corb[MAXL], c[MAXL];
static long long nodes;
static int found;

static int ok(int x) {
    int cx = c[x];
    for (int d = 1; 2 * d < x; d++) {
        int a = c[x - 2 * d], b = c[x - d];
        if (a != b && a != cx && b != cx) return 0;
    }
    for (int d = 1; (ELL - 1) * d < x; d++) {
        int t;
        for (t = 1; t < ELL; t++) if (c[x - t * d] != cx) break;
        if (t == ELL) return 0;
    }
    return 1;
}

static void dfs(int x, int r) {
    if (found) return;
    nodes++;
    if (x > n) {
        if (r >= NEED) {
            found = 1;
            printf("  L=%d colours=%d inner=", L, r);
            for (int i = 1; i <= n; i++) printf("%d", c[i]);
            printf("\n");
        }
        return;
    }
    int o = orb[x];
    if (corb[o] >= 0) {
        c[x] = corb[o];
        if (ok(x)) dfs(x + 1, r);
        return;
    }
    for (int col = 0; col <= r && col < 16; col++) {
        corb[o] = col; c[x] = col;
        if (ok(x)) dfs(x + 1, col == r ? r + 1 : r);
        if (found) return;
    }
    corb[o] = -1;
}

int main(int argc, char **argv) {
    ELL = atoi(argv[1]); int R = atoi(argv[2]); NEED = R - 2;
    int Lmin = atoi(argv[3]), Lmax = atoi(argv[4]);
    int hits = 0;
    for (L = (Lmin | 1); L <= Lmax; L += 2) {
        n = L - 1;
        for (int i = 0; i <= n; i++) orb[i] = -1;
        int nor = 0;
        for (int x = 1; x <= n; x++) if (orb[x] < 0) {
            int y = x;
            while (orb[y] < 0) { orb[y] = nor; y = (2 * y) % L; }
            nor++;
        }
        if (nor < NEED) continue; /* cannot have NEED colours */
        for (int i = 0; i < nor; i++) corb[i] = -1;
        found = 0; nodes = 0;
        dfs(1, 0);
        if (found) hits++;
        fflush(stdout);
    }
    printf("l=%d R=%d L in [%d,%d]: windows found %d\n", ELL, R, Lmin, Lmax, hits);
    return 0;
}
