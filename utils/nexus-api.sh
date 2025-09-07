token="${NEXUS_TOKEN:-}"
user_token="${NEXUS_USER_TOKEN:-}"
application="mod-organizer-2-linux-installer"
version="indev"

function sso() {
	echo "Placeholder"
}

function request_headers() {
	echo "apikey: $user_token"
	echo "Application-Name: $application"
	echo "Application-Version: $version"
}

function curl_nexus() {
	local url="$1"
	shift
	local attempt_max=3
	local attempt=1
	local response=""

	local headers=()
	while IFS= read -r line; do
		headers+=("-H" "$line")
	done < <(request_headers)

	log_info "Requesting URL: $url"

	while [ $attempt -lt $attempt_max ]; do
		response=$(curl -s -v "${headers[@]}" "$@" "$url")
		if [[ -z "$response" || "$response" == *"Please provide an authentication method"* ]]; then
			log_info "Attempt $attempt failed: No response or authentication required. Retrying..."
			((attempt++))
			sleep 2
		else
			echo "$response"
			return 0
		fi
	done

	log_error "Failed after $attempt_max attempts."
	exit 1
}

function fetch_download_link() {
	local game_id="$1"
	local mod_id="$2"
	local file_id="$3"

	response=$(curl_nexus "https://api.nexusmods.com/v1/games/$game_id/mods/$mod_id/files/$file_id/download_link.json")
	parsed=$(echo "$response" | grep -o '{[^}]*"short_name":"Nexus CDN"[^}]*}' | sed -n 's/.*"URI":"\([^"]*\)".*/\1/p')
	parsed=$(echo "$parsed" | sed 's/\\u0026/\&/g')

	log_info "Raw response: $response"
	log_info "Parsed download link: $parsed"

	if [ -z "$parsed" ]; then
		log_error "Failed to parse download link from response."
		exit 1
	fi

	echo "${parsed}"
}

function url_download() {
	url="$1"
	out="-L --fail -o '$2'"

	url_encoded="${url// /%20}"
	#curl_nexus "$url_encoded" $out
	curl -L --fail -o "$2" "$url_encoded"
}