#!/usr/bin/env bash
# Monthly GSN reverify dispatcher — the freshness promise as a timer.
#
# Dispatches the farm wave (vendor credits, not Anthropic) re-verifying the 60
# oldest-verified nodes, then registers an sq open-thread so Claude's next
# session picks up the harvest for the guarded merge. The MERGE IS NEVER
# AUTOMATED: workers draft, Claude reviews and lands (worker hard rules).
#
# Scheduled by ~/.config/systemd/user/gsn-reverify.{service,timer}
# (monthly, 13:07 America/New_York = 17:07 UTC — inside MiMo's 16-24 UTC
# off-peak discount window; lane default xiaomi, see reverify_wave.py).
set -euo pipefail
GSN=/home/ollan/claude/gsn
STOP=/home/ollan/.local/share/socrates/farm.stop
OUT=/home/ollan/.local/share/socrates/gsn-reverify
export PATH="/home/ollan/bin:$PATH"

if [ -e "$STOP" ]; then
  echo "farm.stop present — skipping monthly reverify dispatch"
  exit 0
fi

cd "$GSN"
git pull --rebase --quiet || echo "WARN: git pull failed, waving against local tree"
mkdir -p "$OUT"
TSV="$OUT/wave-$(date +%Y%m%d).tsv"
python3 scripts/reverify_wave.py 60 xiaomi 2>/dev/null \
  | sed "s/today=TODAY/today=$(date +%F)/g" > "$TSV"
[ -s "$TSV" ] || { echo "empty wave TSV — abort"; exit 1; }

echo "dispatching $(wc -l < "$TSV") reverify lanes"
farm-wave "$TSV" 2

WAVEDIR=$(ls -dt /home/ollan/.local/share/socrates/waves/* | head -1)
sq open "GSN monthly reverify wave dispatched $(date +%F) — HARVEST AWAITS GUARDED MERGE: $WAVEDIR/artifacts (apply via the guarded-merge pattern from 2026-09-10: observations verbatim, coords/url frozen, failed checks never bump last_verified)" \
  -r "gsn scripts/reverify-monthly.sh, muninn 01M25XRYK3K94Y0W3RD4EM455J" || true
echo "done: $WAVEDIR"
