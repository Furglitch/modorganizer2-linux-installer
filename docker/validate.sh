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

header "Runtime Tests"

if [[ -f "$STATE_FILE" ]]; then
    WINE_USER=$(whoami)

    while IFS='|' read -r game ipath gpath launcher wine_prefix; do
        [[ -z "$game" ]] && continue

        echo
        echo "  Testing redirector execution for [$game / $launcher]..."

        game_dir="$gpath"
        [[ ! -d "$gpath" ]] && game_dir=$(dirname "$gpath")
        redirector=$(find "$game_dir" -maxdepth 2 -name "mo2-redirector.exe" 2>/dev/null | head -1)

        MO2_EXE="$ipath/ModOrganizer.exe"
        WINE_PREFIX="$wine_prefix"
        GAME_DIR=$(dirname "$redirector")

        echo "    → Instance:    $ipath"
        echo "    → Redirector:  ${redirector:-<not found>}"
        echo "    → MO2 Exe:     $MO2_EXE"
        echo "    → Wine Prefix: $WINE_PREFIX"

        if [[ -z "$redirector" ]]; then
            fail "[$game] Redirector not found near: $game_dir"
            continue
        fi
        if [[ ! -f "$MO2_EXE" ]]; then
            fail "[$game] ModOrganizer.exe not found: $MO2_EXE"
            continue
        fi
        if [[ -z "$WINE_PREFIX" ]]; then
            fail "[$game] Wine prefix could not be determined"
            continue
        fi

        proc=$(ls -lh "$redirector" | awk '{print $1, $3, $4, $5, $6, $7, $8}')
        echo "    → Permissions: $proc"

        mkdir -p "$WINE_PREFIX/drive_c/users/$WINE_USER/Temp" \
                 "$WINE_PREFIX/drive_c/users/$WINE_USER/AppData/Local/Temp" \
                 "$HOME/.cache/mo2-lint/logs"
        rm -f "$HOME/.cache/mo2-lint/logs/redirector."*.log 2>/dev/null || true

        echo "    → Running redirector (15s timeout)..."
        (
            cd "$GAME_DIR" || exit 1
            timeout 15s env \
            WINEPREFIX="$WINE_PREFIX" \
            USER="$WINE_USER" \
            WINEDEBUG=-all \
            xvfb-run -a wine "./$(basename "$redirector")" >/dev/null 2>&1
        ) || true

        REDIR_LOGFILE=$(ls -t "$HOME/.cache/mo2-lint/logs/redirector."*.log 2>/dev/null | head -1)
        if [[ -f "$REDIR_LOGFILE" ]]; then
            echo "    → Redirector log: $REDIR_LOGFILE"
            sed 's/^/      /' "$REDIR_LOGFILE"
        else
            warn "Redirector log not found"
            REDIR_ERRLOG="$HOME/.cache/mo2-lint/logs/redirector.error.log"
            [[ -f "$REDIR_ERRLOG" ]] && sed 's/^/      /' "$REDIR_ERRLOG"
        fi

        if [[ -f "$REDIR_LOGFILE" ]] && grep -q "Launching:.*ModOrganizer" "$REDIR_LOGFILE" 2>/dev/null; then
            pass "[$game] Redirector launched ModOrganizer.exe"
        else
            fail "[$game] Redirector did not start ModOrganizer.exe"
        fi

        # Verify redirector found the correct MO2 instance
        expected_mo2_wine="Z:$(echo "$ipath/ModOrganizer.exe" | sed 's|/|\\|g')"
        found_mo2=$(grep "Found MO2 instance:" "$REDIR_LOGFILE" 2>/dev/null | sed 's/.*Found MO2 instance: //' | tr -d '\r')
        if [[ -n "$found_mo2" ]]; then
            if [[ "$found_mo2" == "$expected_mo2_wine" ]]; then
                pass "[$game] Correct MO2 instance: $found_mo2"
            else
                fail "[$game] Wrong MO2 instance: expected '$expected_mo2_wine', got '$found_mo2'"
            fi
        else
            warn "[$game] Could not extract MO2 instance path from log"
        fi

        # Verify redirector resolved the correct game executable
        expected_exe=$(python3 - "$STATE_FILE" "$game" "$launcher" <<'PYEOF'
import json, sys
with open(sys.argv[1]) as f:
    data = json.load(f)
for inst in data.get("instances", []):
    if inst.get("game") == sys.argv[2] and inst.get("launcher") == sys.argv[3]:
        gpath = inst.get("game_path", "")
        exe   = inst.get("game_executable", "")
        print(str(gpath) + "/" + exe if exe else "")
        break
PYEOF
)
        found_exe=$(grep "Game executable:" "$REDIR_LOGFILE" 2>/dev/null | sed 's/.*Game executable: //' | tr -d '\r')
        if [[ -n "$found_exe" && -n "$expected_exe" ]]; then
            # Convert Wine Z:\ path to POSIX for comparison
            found_exe_posix=$(echo "$found_exe" | sed 's|^Z:\\||;s|^Z:/||;s|\\|/|g')
            found_exe_posix="/${found_exe_posix#/}"
            if [[ "$found_exe_posix" == "$expected_exe" ]]; then
                pass "[$game] Correct game executable: $found_exe_posix"
            else
                fail "[$game] Wrong game executable: expected '$expected_exe', got '$found_exe_posix'"
            fi
        else
            warn "[$game] Could not verify game executable (found='$found_exe' expected='$expected_exe')"
        fi

    done < <(python3 - "$STATE_FILE" <<'PYEOF'
import json, sys, os

HEROIC_CFG = os.path.expanduser("~/.config/heroic/GamesConfig")
STEAM_PFX  = os.path.expanduser("~/.local/share/Steam/steamapps/compatdata/22330/pfx")

with open(sys.argv[1]) as f:
    data = json.load(f)

for inst in data.get("instances", []):
    launcher = inst.get("launcher", "")
    wine_prefix = ""
    if launcher == "steam":
        wine_prefix = STEAM_PFX
    elif launcher in ("epic", "gog"):
        ids = inst.get("launcher_ids", {})
        game_id = str(ids.get(launcher, ""))
        if game_id:
            cfg = os.path.join(HEROIC_CFG, f"{game_id}.json")
            try:
                with open(cfg) as cf:
                    cdata = json.load(cf)
                wine_prefix = cdata.get(game_id, {}).get("winePrefix", "")
            except Exception:
                pass
    print("{}|{}|{}|{}|{}".format(
        inst.get("game", "unknown"),
        inst.get("instance_path", ""),
        inst.get("game_path", ""),
        launcher,
        wine_prefix,
    ))
PYEOF
)
else
    warn "Skipping runtime tests (state.json missing)"
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
