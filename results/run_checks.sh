#!/bin/sh
# Quick checks of this repository, well under a minute on one core. Run from the repository root:
#   sh results/run_checks.sh         (PYTHON=/path/to/python3 to choose the interpreter)
# Needs a C compiler, Python 3, tar (with xz support), gzip and shasum. Writes results/results.txt and removes its work folder.
# Exit 0 only if every step gave the expected result.
#  1. SHA-256 digests: the files of the three archives and the l = 5 files against the stored lists; the three l = 5
#     formulas and the two cube files against the digests printed below.
#  2. The strict LRAT checker (gw/lratcheck.c) on every stored proof with its formula.
#  3. The colouring checkers on the stored witnesses.
#  4. The paper's colouring checker (checks/gwcheck.c) on the stored colourings, compared with the stored outputs.
set -u
PY=${PYTHON:-python3}; CC=${CC:-cc}; W=work/checks; rm -rf $W; mkdir -p $W/main $W/k4 $W/k5
bad=0
{
echo "run_checks.sh $(date -u +%Y-%m-%dT%H:%M:%SZ); $($PY --version 2>&1); $($CC --version 2>&1 | head -1)"
tar -xJf gw/certificates.tar.xz -C $W/main && tar -xJf gw/k4/certificates_k4l3.tar.xz -C $W/k4 && tar -xJf gw/k5/certificates_k5.tar.xz -C $W/k5 || bad=1

echo "=== 1. digests"
( cd $W/main && shasum -a 256 -c SHA256SUMS 2>&1 | grep -v ': OK$' ; echo "gw/certificates.tar.xz: $(shasum -a 256 -c SHA256SUMS 2>/dev/null | grep -c ': OK$') files match its SHA256SUMS, $(shasum -a 256 -c SHA256SUMS 2>/dev/null | grep -vc ': OK$') do not" )
cmp -s $W/main/SHA256SUMS gw/SHA256SUMS && echo "gw/SHA256SUMS is the list inside the archive" || { bad=1; echo "gw/SHA256SUMS DIFFERS from the list inside the archive"; }
[ "$(cd $W/main && shasum -a 256 -c SHA256SUMS 2>/dev/null | grep -vc ': OK$')" = 0 ] || bad=1
for pair in "k4 SHA256SUMS_k4l3" "k5 SHA256SUMS_k5"; do
  set -- $pair; cmp -s $W/$1/$2 gw/$1/$2 || { bad=1; echo "gw/$1/$2 DIFFERS from the list inside the archive"; }
  for f in gw/$1/lrat/*.lrat.gz; do b=$(basename $f .lrat.gz); cp $f $W/$1/lrat/ 2>/dev/null || { mkdir -p $W/$1/lrat; cp $f $W/$1/lrat/; }; gzip -dc $f > $W/$1/lrat/$b.lrat; done
  n=0; m=0
  while read h name rest; do
    case "$h" in \#*|"") continue;; esac
    [ -f $W/$1/$name ] || { m=$((m+1)); continue; }
    [ "$(shasum -a 256 $W/$1/$name | cut -d' ' -f1)" = "$h" ] && n=$((n+1)) || { bad=1; echo "DIGEST MISMATCH gw/$1 $name"; }
  done < gw/$1/$2
  echo "gw/$1/$2: $n files match (formulas, proofs and gzip files); $m listed files are not in this repository"
done
n=0; m=0
while read h name; do
  [ -f gw/l5cert/$name ] || { m=$((m+1)); continue; }
  [ "$name" = SHA256SUMS ] && continue
  [ "$(shasum -a 256 gw/l5cert/$name | cut -d' ' -f1)" = "$h" ] && n=$((n+1)) || { bad=1; echo "DIGEST MISMATCH gw/l5cert/$name"; }
done < gw/l5cert/SHA256SUMS
echo "gw/l5cert/SHA256SUMS: $n files match; $m listed files are not in this repository"
# the first 16 hexadecimal digits of these three are printed in Appendix C of the paper
for x in "A3_293 29c61bd98844f5cd" "A5_294 c84186bf1825de17" "P294 829addc0c4a9b441"; do
  set -- $x; h=$($PY -I -c "import lzma, hashlib, sys; print(hashlib.sha256(lzma.open(sys.argv[1]).read()).hexdigest())" gw/l5cert/$1.cnf.xz)
  case "$h" in $2*) echo "$h  gw/l5cert/$1.cnf (uncompressed): begins with $2 as expected";; *) bad=1; echo "$h  gw/l5cert/$1.cnf (uncompressed): DOES NOT begin with $2";; esac
done
shasum -a 256 gw/k4l4_exact/R1.txt gw/k4l4_exact/R2.txt

echo "=== 2. strict LRAT checker"
$CC -O2 -w -o $W/lratcheck gw/lratcheck.c || bad=1
ok=0; no=0
for c in $W/main/cnf/*.cnf; do
  b=$(basename $c .cnf); [ -f $W/main/lrat/$b.lrat ] || continue
  if $W/lratcheck $c $W/main/lrat/$b.lrat 2>/dev/null | grep -q '^s VERIFIED UNSAT'; then ok=$((ok+1)); else no=$((no+1)); echo "NOT VERIFIED $b"; fi
done
echo "gw/certificates.tar.xz: $ok proofs VERIFIED UNSAT, $no not"; [ $no = 0 ] && [ $ok -gt 0 ] || bad=1
for x in "k4 A4_57" "k4 P10" "k4 U56" "k5 V2_9" "k5 V3_27"; do
  set -- $x; out=$($W/lratcheck $W/$1/cnf/$2.cnf $W/$1/lrat/$2.lrat 2>&1 | tail -2 | tr '\n' ' '); echo "gw/$1 $2: $out"
  case "$out" in *"s VERIFIED UNSAT"*) ;; *) bad=1;; esac
done

echo "=== 3. witnesses"
$CC -O2 -o $W/check_k5 gw/k5/check_k5.c || bad=1
for x in "4 3 gw/k4/witnesses_k4l3.txt" "4 3 gw/k4/extremal56_rgs.txt" "5 3 gw/k5/witnesses_k5l3.txt" "4 4 gw/colouring_1_328.txt"; do
  set -- $x; $W/check_k5 $1 $2 < $3 > $W/out.txt 2>&1
  echo "$3 (k = $1, l = $2): $(grep -c 'GOOD$' $W/out.txt) GOOD, $(grep -c 'BAD' $W/out.txt) BAD; longest: $(sort -t= -k2 -n $W/out.txt | tail -1)"
  [ "$(grep -c 'BAD' $W/out.txt)" = 0 ] && [ "$(grep -c 'GOOD$' $W/out.txt)" -gt 0 ] || bad=1
done
for s in $(sed -n 's/^r = [0-9]*: //p' gw/witnesses_52.txt); do echo "gw/witnesses_52.txt (l = 4): $($PY -I gw/check_rm.py 4 $s)"; done
for f in g3_292 g5_293; do echo "gw/l5cert/$f.col (l = 5): $($PY -I gw/check_rm.py 5 $(cat gw/l5cert/$f.col))"; done

echo "=== 4. the paper's colouring checker"
$CC -O2 -o $W/gwcheck checks/gwcheck.c || bad=1
for f in residue aligned aligned_m table table_extra table_extra2 z4zq; do
  $W/gwcheck < checks/out/${f}_colourings.txt > $W/out.txt 2>&1
  cmp -s $W/out.txt checks/out/${f}_check.txt && echo "checks/out/${f}_colourings.txt: $(grep -c '' $W/out.txt) lines, same as checks/out/${f}_check.txt" || { bad=1; echo "checks/out/${f}_colourings.txt: output DIFFERS from checks/out/${f}_check.txt"; }
done
[ $bad = 0 ] && echo "ALL PASS" || echo "SOMETHING FAILED"
} > results/results.txt 2>&1
rm -rf work
tail -1 results/results.txt
[ $bad = 0 ]
