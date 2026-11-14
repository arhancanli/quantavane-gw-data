/* Exhaustive DFS over colourings of [1,n] in first-occurrence (RGS) form with no rainbow 4-AP and no monochromatic
   3-AP. For every r records the largest n with a good colouring using exactly r colours, and counts the good
   colourings of every length. Independent of the SAT encoders. */
#include <stdio.h>
#include <stdlib.h>
#define MAXN 64
static int c[MAXN + 1];           /* c[1..t] */
static long long cnt[MAXN + 1][MAXN + 1];   /* cnt[t][r] good colourings of [1,t] with r colours */
static long long nodes = 0;
static int best[MAXN + 1];
static int ok_last(int t) {        /* APs ending at t */
  for (int d = 1; t - 2 * d >= 1; d++) {
    if (c[t] == c[t - d] && c[t] == c[t - 2 * d]) return 0;
    if (t - 3 * d >= 1) {
      int a = c[t - 3 * d], b = c[t - 2 * d], e = c[t - d], f = c[t];
      if (a != b && a != e && a != f && b != e && b != f && e != f) return 0;
    }
  }
  return 1;
}
static void dfs(int t, int r) {    /* c[1..t] good, r colours used */
  nodes++;
  cnt[t][r]++;
  if (t > best[r]) best[r] = t;
  if (t == MAXN) return;
  for (int col = 0; col <= r; col++) {
    c[t + 1] = col;
    if (ok_last(t + 1)) dfs(t + 1, col == r ? r + 1 : r);
  }
}
int main(void) {
  c[1] = 0; dfs(1, 1);
  printf("nodes %lld\n", nodes);
  for (int r = 1; r <= MAXN; r++) if (best[r]) printf("r=%d largest n with an exact good r-colouring: %d\n", r, best[r]);
  int maxt = 0; for (int t = 1; t <= MAXN; t++) for (int r = 1; r <= MAXN; r++) if (cnt[t][r]) maxt = t;
  printf("longest good colouring (any number of colours): %d\n", maxt);
  for (int t = 1; t <= maxt; t++) { printf("t=%d:", t); for (int r = 1; r <= MAXN; r++) if (cnt[t][r]) printf(" r%d=%lld", r, cnt[t][r]); printf("\n"); }
  return 0;
}
