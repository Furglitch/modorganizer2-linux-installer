#!/usr/bin/env bash
# Validate that mo2-lint installed correctly.
# Exits 0 if all checks pass, 1 if any fail.

set -uo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

PASS=0
FAIL=0

pass()   { echo -e "  ${GREEN}✓${NC} $1"; ((++PASS)); }
fail()   { echo -e "  ${RED}✗${NC} $1"; ((++FAIL)); }
warn()   { echo -e "  ${YELLOW}!${NC} $1"; }
header() { echo; echo -e "${BOLD}── $1 ──${NC}"; }

STATE_FILE="$HOME/.config/mo2-lint/state.json"
INSTANCES_DIR="$HOME/.config/mo2-lint/instances"
MO2_DIR="$HOME/Games/mo2-lint_oblivion-steam"
LOGS_DIR="$HOME/.cache/mo2-lint/logs"
NXM_HANDLER="$HOME/.local/share/mo2-lint/nxm-handler"
DESKTOP_FILE="$HOME/.local/share/applications/mo2lint_nxm-handler.desktop"

echo -e "${BOLD}mo2-lint Installation Validator${NC}"
echo "================================"

# --- #

header "Configuration"

if [[ -f "$STATE_FILE" ]]; then
    pass "state.json found: $STATE_FILE"
else
    fail "state.json not found: $STATE_FILE"
fi

# --- #

header "Instance Symlinks"

if [[ -d "$INSTANCES_DIR" ]]; then
    link_count=0
    while IFS= read -r -d '' link; do
        name=$(basename "$link")
        target=$(readlink "$link")
        if [[ -e "$link" ]]; then
            pass "[$name] → $target"
        else
            fail "[$name] broken symlink → $target (target missing)"
        fi
        ((++link_count))
    done < <(find "$INSTANCES_DIR" -maxdepth 1 -type l -print0 2>/dev/null)

    if [[ $link_count -eq 0 ]]; then
        warn "No instance symlinks found in $INSTANCES_DIR"
    fi
else
    fail "Instances directory not found: $INSTANCES_DIR"
fi

# --- #

header "MO2 Instances"

if [[ -f "$STATE_FILE" ]]; then
    instance_count=0

    # Parse state.json with python; emit "game|instance_path|game_path" per instance.
    while IFS='|' read -r game ipath gpath; do
        [[ -z "$game" ]] && continue
        ((++instance_count))

        # MO2 instance directory contains ModOrganizer.exe
        if [[ -f "$ipath/ModOrganizer.exe" ]]; then
            pass "[$game] MO2 instance: $ipath"
        else
            fail "[$game] MO2 instance not found at: $ipath"
        fi

        # Redirector sits in the game folder; search up to 2 levels from game_path
        game_dir="$gpath"
        [[ ! -d "$gpath" ]] && game_dir=$(dirname "$gpath")
        redirector=$(find "$game_dir" -maxdepth 2 -name "mo2-redirector.exe" 2>/dev/null | head -1)
        if [[ -n "$redirector" ]]; then
            pass "[$game] Redirector: $redirector"
        else
            fail "[$game] Redirector (mo2-redirector.exe) not found near: $game_dir"
        fi

    done < <(python3 - "$STATE_FILE" <<'PYEOF'
import json, sys
with open(sys.argv[1]) as f:
    data = json.load(f)
for inst in data.get("instances", []):
    print("{}|{}|{}".format(
        inst.get("game", "unknown"),
        inst.get("instance_path", ""),
        inst.get("game_path", ""),
    ))
PYEOF
)

    if [[ $instance_count -eq 0 ]]; then
        warn "No instances found in state.json"
    fi
else
    warn "Skipping instance checks (state.json missing)"
fi

# --- #

header "Logs"

if [[ -d "$LOGS_DIR" ]]; then
    pass "Logs directory: $LOGS_DIR"
else
    fail "Logs directory not found: $LOGS_DIR"
fi

# --- #

header "NXM Handler"

if [[ -x "$NXM_HANDLER" ]]; then
    pass "NXM Handler executable: $NXM_HANDLER"
elif [[ -f "$NXM_HANDLER" ]]; then
    fail "NXM Handler exists but is not executable: $NXM_HANDLER"
else
    fail "NXM Handler not found: $NXM_HANDLER"
fi

if [[ -f "$DESKTOP_FILE" ]]; then
    pass "Desktop entry: $DESKTOP_FILE"
else
    fail "Desktop entry not found: $DESKTOP_FILE"
fi

# --- #

echo
echo "================================"
if [[ $FAIL -gt 0 ]]; then
    echo -e "${RED}${BOLD}$FAIL check(s) failed${NC}, ${GREEN}$PASS passed${NC}"
    echo -e "${RED}Installation has issues — review the failures above.${NC}"
    exit 1
else
    echo -e "${GREEN}${BOLD}All $PASS checks passed.${NC}"
    echo -e "${GREEN}Installation looks good!${NC}"
    exit 0
fi
