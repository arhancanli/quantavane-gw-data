/* Exhaustive DFS over colourings of [1,n] in first-occurrence (RGS) form with no rainbow k-AP and no monochromatic
   l-AP (k5 agent, 12 Nov 2026; generalises k4/dfs_k4l3.c, shares no code with the SAT encoders).
   Usage: dfs_k5l3 k l N cap cmin [report]
     N     largest length explored (the search stops at length N);
     cap   at most cap colours (cap >= k makes the rainbow test active);
     cmin  prune a branch when r + (N - t) < cmin, i.e. it can no longer reach cmin colours by length N
           (cmin = 1: no pruning; then every good colouring of length <= N with <= cap colours is visited).
   For every r: the largest t <= N with a good exact r-colouring of [1,t] that was visited; counts cnt[t][r].
   With cmin > 1 the counts and maxima are only for colourings that can still reach cmin colours by N
   (a colouring of [1,t] with r colours is visited iff r + N - t >= cmin). */
#include <stdio.h>
#include <stdlib.h>
#define MAXN 128
static int K, L, N, CAP, CMIN;
static int c[MAXN + 2];
static long long cnt[MAXN + 1][MAXN + 1];
static long long nodes = 0;
static int best[MAXN + 1];
static char bestcol[MAXN + 1][MAXN + 2];
static int ok_last(int t) {        /* APs ending at t */
  for (int d = 1; t - (L - 1) * d >= 1 || t - (K - 1) * d >= 1; d++) {
    if (t - (L - 1) * d >= 1) {
      int j; for (j = 1; j < L; j++) if (c[t - j * d] != c[t]) break;
      if (j == L) return 0;
    }
    if (CAP >= K && t - (K - 1) * d >= 1) {
      int distinct = 1;
      for (int a = 0; a < K && distinct; a++)
        for (int b = a + 1; b < K; b++) if (c[t - a * d] == c[t - b * d]) { distinct = 0; break; }
      if (distinct) return 0;
    }
  }
  return 1;
}
static void dfs(int t, int r) {    /* c[1..t] good, r colours used */
  nodes++;
  cnt[t][r]++;
  if (t > best[r]) { best[r] = t; for (int i = 1; i <= t; i++) bestcol[r][i - 1] = "0123456789abcdefghijklmnopqrstuvwxyz"[c[i] % 36]; bestcol[r][t] = 0; }
  if (t == N) return;
  for (int col = 0; col <= r && col < CAP; col++) {
    int r2 = col == r ? r + 1 : r;
    if (r2 + (N - t - 1) < CMIN) continue;
    c[t + 1] = col;
    if (ok_last(t + 1)) dfs(t + 1, r2);
  }
}
int main(int argc, char **argv) {
  if (argc < 6) { fprintf(stderr, "usage: dfs_k5l3 k l N cap cmin [report]\n"); return 2; }
  K = atoi(argv[1]); L = atoi(argv[2]); N = atoi(argv[3]); CAP = atoi(argv[4]); CMIN = atoi(argv[5]);
  int report = argc > 6 ? atoi(argv[6]) : 1;
  if (N > MAXN) N = MAXN;
  c[1] = 0; if (1 + (N - 1) >= CMIN) dfs(1, 1);
  printf("k=%d l=%d N=%d cap=%d cmin=%d nodes %lld\n", K, L, N, CAP, CMIN, nodes);
  for (int r = 1; r <= MAXN; r++) if (best[r]) printf("r=%d largest t with a visited good exact r-colouring: %d %s\n", r, best[r], bestcol[r]);
  if (report) for (int t = 1; t <= N; t++) { int any = 0; for (int r = 1; r <= MAXN; r++) if (cnt[t][r]) any = 1; if (!any) continue;
    printf("t=%d:", t); for (int r = 1; r <= MAXN; r++) if (cnt[t][r]) printf(" r%d=%lld", r, cnt[t][r]); printf("\n"); }
  return 0;
}
