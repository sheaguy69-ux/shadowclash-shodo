#!/bin/bash
# Refresh the ShadowClash code snapshot in the second brain from the working repo.
# Run:  cd .../GAME-CODE-PRIVATE-DEV && ./refresh.sh
set -euo pipefail

SRC=/Users/anthonyguy/shadowclash-preview
DST="$(cd "$(dirname "$0")" && pwd)"

[ -f "$SRC/web/index.html" ] || { echo "ERROR: source repo not found at $SRC"; exit 1; }

echo "Refreshing snapshot from $SRC"

cp "$SRC/web/index.html" "$DST/web/index.html"
rsync -a --delete "$SRC/web/assets/sprites/" "$DST/web/assets/sprites/"
rsync -a --delete "$SRC/web/assets/ninjas/"  "$DST/web/assets/ninjas/"
[ -d "$SRC/web/assets/stages" ] && rsync -a --delete "$SRC/web/assets/stages/" "$DST/web/assets/stages/"

rsync -a --delete --include='*/' --include='*.py' --include='*.mjs' --include='*.md' \
      --exclude='*' "$SRC/tools/" "$DST/tools/"

cp "$SRC"/*.md "$DST/" 2>/dev/null || true
mkdir -p "$DST/docs"; cp "$SRC"/docs/*.md "$DST/docs/" 2>/dev/null || true

SV=$(grep -o 'const SHEET_V = [0-9]*' "$DST/web/index.html" | head -1 | grep -o '[0-9]*')
COMMIT=$(cd "$SRC" && git log --oneline -1 2>/dev/null || echo "n/a")
STAMP=$(date +%Y-%m-%d)

# keep the header table in _SNAPSHOT-INFO.md honest
python3 - "$DST/_SNAPSHOT-INFO.md" "$STAMP" "$SV" "$COMMIT" <<'PY'
import re,sys
p,stamp,sv,commit=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
s=open(p).read()
s=re.sub(r'(\|\s*\*\*Snapshot taken\*\*\s*\|\s*)[^|]*(\|)', r'\g<1>'+stamp+r' \g<2>', s)
s=re.sub(r'(\|\s*\*\*SHEET_V at snapshot\*\*\s*\|\s*)[^|]*(\|)', r'\g<1>'+sv+r' \g<2>', s)
if '**HEAD commit**' not in s:
    s=s.replace('| **Source of truth**', '| **HEAD commit** | `'+commit+'` |\n| **Source of truth**',1)
else:
    s=re.sub(r'(\|\s*\*\*HEAD commit\*\*\s*\|\s*)[^|]*(\|)', r'\g<1>`'+commit+r'` \g<2>', s)
open(p,'w').write(s)
PY

echo "Snapshot refreshed: SHEET_V $SV | $COMMIT | $(du -sh "$DST" | cut -f1)"
