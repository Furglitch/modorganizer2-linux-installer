#!/usr/bin/env bash

log_info "installing nxm link broker in '$shared'"
cp "$handlers/modorganizer2-nxm-broker.sh" "$shared"
chmod +x "$shared/modorganizer2-nxm-broker.sh"
cp "$utils/find-heroic-game-installation.sh" "$shared"
chmod +x "$shared/find-heroic-game-installation.sh"

app_dir="$HOME/.local/share/applications"
log_info "installing nxm link handler in '$app_dir/'"
mkdir -p "$app_dir"
cp "$handlers/modorganizer2-nxm-handler.desktop" "$app_dir/"

truncate --size=0 "$install_dir/variables.sh"
echo "${game_launcher@A}" >>"$install_dir/variables.sh"
echo "${game_appid@A}" >>"$install_dir/variables.sh"
echo "${game_epic_productid@A}" >>"$install_dir/variables.sh"
echo "${game_gog_productid@A}" >>"$install_dir/variables.sh"

if [ -n "$(command -v xdg-mime)" ]; then
	xdg-mime default modorganizer2-nxm-handler.desktop x-scheme-handler/nxm
else
	log_warn "xdg-mime not found, cannot register mimetype"
fi
