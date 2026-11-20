#!/usr/bin/env sh
# Install every skill in this repo for Claude Code (macOS / Linux / Git Bash on Windows).
#   ./install.sh             -> your user skills folder (~/.claude/skills), available in every project
#   ./install.sh --project   -> ./.claude/skills of the folder you run it from (this game only)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
if [ "$1" = "--project" ]; then DEST="$(pwd)/.claude/skills"; else DEST="$HOME/.claude/skills"; fi
mkdir -p "$DEST"
for d in "$HERE"/skills/*/; do
  name="$(basename "$d")"
  rm -rf "$DEST/$name"
  cp -R "$d" "$DEST/$name"
  echo "installed $name"
done
echo ""
echo "Done: skills are in $DEST"
echo "Open Claude Code and say: \"I want to make a game. Where do I start?\""
