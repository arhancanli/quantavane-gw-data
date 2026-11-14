#!/bin/zsh
# GW(4;4,4) lane certificates (12 Nov 2026).  Everything UNSAT is CaDiCaL 3.0.1 (--lrat=true --binary=false
# --vivifyinst=false) with the LRAT proof streamed into our strict checker lratcheck (--skip-satisfied-hints), via
# run44.py; cube CNFs are streamed through named pipes (--fifo-cnf), so nothing large is written.  Logs: logs/.
# Stop: touch $D/STOP (the residue-block runs stop between cubes).  Resumable: rerun; finished cubes are skipped.
setopt NO_BG_NICE
K=${0:A:h}                                       # this folder
D=${GW44_WORK:-$K/work}                          # work folder (base formulas and cube files)
P=/usr/bin/python3
CAD=${CADICAL:-cadical}                          # CaDiCaL 3.0.1
OC=${LRATCHECK:-${K:h}/lratcheck}                # lratcheck.c of the folder above, compiled
L=$K/logs/cert44.log
mkdir -p $D $K/logs; cd $D
log() { echo "$(date '+%F %T %z') $*" | tee -a $L; }
log "START cert44.sh pid $$"
# --- base CNFs (hashes logged) ---
$P -I $K/gw44_cnf.py 329 4 4 4 P329.cnf --exact --mirror 2>/dev/null
$P -I $K/gw44_cnf.py 329 4 4 4 P329_plain.cnf --exact --no-rgs 2>/dev/null
$P -I $K/gw44_cnf.py 53 4 3 4 V53.cnf --exact --mirror 2>/dev/null
$P -I $K/gw44_cnf.py 57 4 4 3 V57.cnf --exact --mirror 2>/dev/null
$P -I $K/w24_cnf.py 35 W24_35.cnf; $P -I $K/w24_cnf.py 34 W24_34.cnf
for f in P329 P329_plain V53 V57 W24_35; do log "CNF $f $(grep '^p cnf' $f.cnf) sha256 $(shasum -a 256 $f.cnf | cut -c1-64)"; done
# --- small certificates: whole formulas (one empty cube) ---
echo "all" > all.txt
run() { $P -I $K/run44.py --base $1 --cubes $2 --log $3 --work $D/w --n $4 --k $5 --l $6 --jobs ${7:-1} --fifo-cnf ${@:8}; }
run W24_35.cnf all.txt $K/logs/W24_35.log 35 4 4
run V53.cnf all.txt $K/logs/V53.log 53 3 4
run V57.cnf all.txt $K/logs/V57.log 57 4 3
$P -I $K/cubes44.py 329 4 B183.txt --b3 183-329 2>/dev/null
run P329.cnf B183.txt $K/logs/B183.log 329 4 4
for x in W24_35 V53 V57 B183; do log "RESULT $x: $(grep FINISH $K/logs/$x.log | tail -1 | cut -d' ' -f2-4)"; done
# green controls (SAT expected; decoded colourings checked by two separate programs)
s34=$(nice -n 10 $CAD -q W24_34.cnf | $P -I -c "import sys; m={int(t) for l in sys.stdin if l.startswith('v') for t in l.split()[1:] if int(t)>0}; print(''.join('0' if 2*i+1 in m else '1' for i in range(34)))")
log "GREEN w(2;4): 2-colouring of [1,34] $s34 -> $($P -I $K/../k4/check_k4.py 5 4 $s34)"
for spec in "52 4 3 4" "56 4 4 3"; do set -- ${=spec}
  $P -I $K/gw44_cnf.py $1 $2 $3 $4 G.cnf --exact --mirror 2>/dev/null; nice -n 10 $CAD -q G.cnf > G.out
  col=$($P -I $K/decode44.py G.out $1 $2); log "GREEN n=$1 k=$3 l=$4: $col -> $($P -I $K/../k4/check_k4.py $3 $4 $col) / $(echo $col | $K/check_k5 $3 $4)"
done
# --- red controls ---
log "RED eval (unsound strict mirror on the 328 colouring): $($P -I $K/eval44.py $K/../colouring_1_328.txt 328 4 4 4 --exact --mirror --mirror-strict-RED)"
log "SOUND eval: $($P -I $K/eval44.py $K/../colouring_1_328.txt 328 4 4 4 --exact --mirror)"
$P -I - $K/../colouring_1_328.txt > red_block.txt <<'PY'
import sys
col = [int(ch) for ch in open(sys.argv[1]).read() if ch.isdigit()]
names = {}; [names.setdefault(x, len(names)) for x in col]; cc = [names[x] for x in col]
print(' '.join(['red'] + [str(i * 4 + cc[i] + 1) for i in range(123, 204)]))
PY
for fl in "" "--mirror-strict-RED"; do
  $P -I $K/gw44_cnf.py 328 4 4 4 R328.cnf --exact --mirror $fl 2>/dev/null
  rm -f $K/logs/RED328$fl.log; run R328.cnf red_block.txt $K/logs/RED328$fl.log 328 4 4
  log "RED328 mirror $fl + central 81 points of the 328 colouring: $(grep FINISH $K/logs/RED328$fl.log | cut -d' ' -f3)"
done
# checker red control: a stored small proof (V57) with the last hint of the empty-clause step removed must be rejected
nice -n 10 $CAD -q --lrat=true --binary=false --vivifyinst=false V57.cnf V57.lrat > /dev/null
$P -I - V57.lrat V57_red.lrat <<'PY'
import sys
L = [l for l in open(sys.argv[1]).read().split('\n') if l.strip()]
for i in range(len(L) - 1, -1, -1):
    t = L[i].split()
    if len(t) > 3 and t[1] == '0': L[i] = ' '.join(t[:2] + t[2:-2] + ['0']); break
open(sys.argv[2], 'w').write('\n'.join(L) + '\n')
PY
log "CHECKER green V57: $($OC V57.cnf V57.lrat 2>&1 | tail -1)  red (one hint removed): $($OC V57.cnf V57_red.lrat 2>&1 | tr '\n' ' ' | cut -c1-160)"
rm -f V57.lrat V57_red.lrat
# --- R1: central 31-point residue blocks mod 109 (109 cubes) ---
$P -I $K/rigid44.py 329 109 15 R1.txt 2>/dev/null
log "R1 cubes sha256 $(shasum -a 256 R1.txt | cut -c1-64)"
run P329_plain.cnf R1.txt $K/logs/R1.log 329 4 4 2 --stop-file $D/STOP
log "R1: $(grep -c 'status=UNSAT_CHECKED' $K/logs/R1.log) of 109 UNSAT_CHECKED, other: $(grep FINISH $K/logs/R1.log | grep -vc UNSAT_CHECKED)"
# --- R2: 41-point residue blocks mod 109 at every start a = 1..145 (by reflection a <= 145 suffices) ---
rm -f R2.txt; for a in {1..145}; do $P -I $K/rigid44.py 329 109 0 r.tmp --start $a --len 41 2>/dev/null; cat r.tmp >> R2.txt; done
log "R2 cubes $(wc -l < R2.txt) sha256 $(shasum -a 256 R2.txt | cut -c1-64)"
run P329_plain.cnf R2.txt $K/logs/R2.log 329 4 4 2 --stop-file $D/STOP
log "R2: $(grep -c 'status=UNSAT_CHECKED' $K/logs/R2.log) of $(wc -l < R2.txt) UNSAT_CHECKED, other: $(grep FINISH $K/logs/R2.log | grep -vc UNSAT_CHECKED)"
log "END cert44.sh"
