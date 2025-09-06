
# Installer version (update this as needed)
installer_version="5.2.8"

# GitHub repo info
repo="Furglitch/modorganizer2-linux-installer"
api_url="https://api.github.com/repos/$repo/releases/latest"

# Fetch latest release tag from GitHub
latest_version=$(curl -s "$api_url" | grep '"tag_name"' | head -1 | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$latest_version" ]; then
	log_error "Could not fetch latest release info from GitHub."
	exit 0
fi

if [ "$installer_version" != "$latest_version" ]; then
	log_warn "Your installer version ($installer_version) is not the latest release ($latest_version). Please update by visiting: https://github.com/$repo/releases/latest"
	else
	log_info "Installer is up to date ($installer_version)."
fi
