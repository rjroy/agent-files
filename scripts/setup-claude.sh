#!/usr/bin/env bash
# Bootstrap this repo as the source of the user's global Claude config:
#   1. Symlink ~/.claude/CLAUDE.md -> COMMON.md
#   2. Register this repo as a local plugin marketplace
#   3. Install every plugin the marketplace declares
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
claude_md="$HOME/.claude/CLAUDE.md"
agents_md="$repo_dir/COMMON.md"
marketplace_json="$repo_dir/.claude-plugin/marketplace.json"

echo "==> Linking $claude_md -> $agents_md"
if [ -e "$claude_md" ] || [ -L "$claude_md" ]; then
	if [ -L "$claude_md" ] && [ "$(readlink "$claude_md")" = "$agents_md" ]; then
		echo "    already linked, skipping"
	else
		backup="$claude_md.bak.$(date +%Y%m%d%H%M%S)"
		echo "    existing file found, backing up to $backup"
		mv "$claude_md" "$backup"
		ln -s "$agents_md" "$claude_md"
	fi
else
	mkdir -p "$(dirname "$claude_md")"
	ln -s "$agents_md" "$claude_md"
fi

echo "==> Registering marketplace: $repo_dir"
claude plugin marketplace add "$repo_dir"

echo "==> Installing plugins"
marketplace_name="$(claude plugin marketplace list --json 2>/dev/null \
	| python3 -c "
import json, sys
marketplaces = json.load(sys.stdin)
for m in marketplaces:
    if m.get('path') == '$repo_dir':
        print(m['name'])
        break
" 2>/dev/null || true)"

if [ -z "$marketplace_name" ]; then
	marketplace_name="$(python3 -c "import json; print(json.load(open('$marketplace_json'))['name'])")"
fi

plugins="$(python3 -c "
import json
data = json.load(open('$marketplace_json'))
for p in data['plugins']:
    print(p['name'])
")"

while IFS= read -r plugin; do
	[ -z "$plugin" ] && continue
	echo "    installing $plugin@$marketplace_name"
	claude plugin install "$plugin@$marketplace_name"
done <<<"$plugins"

echo "==> Done"
