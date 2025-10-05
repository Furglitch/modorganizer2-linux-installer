#!/usr/bin/env bash

client_id="mo2linux-test"
redirect_port="8425"
#redirect_uri=$(printf 'http://localhost:%s' "$redirect_port" | sed -e 's/:/%3A/g' -e 's/\//%2F/g')
token="${NEXUS_TOKEN:-}"

function code_challenge() { # https://modding.wiki/en/api/oauth2-guide#create-the-code-challenge-public-apps
	verifier="$(openssl rand -hex 43)"

	challenge="$(printf '%s' "$verifier" | openssl dgst -sha256 -binary | openssl base64 -A | tr '+/' '-_' | tr -d '=')"

	echo "$challenge"
}

function auth_url() { # https://modding.wiki/en/api/oauth2-guide#generate-an-authorize-url

	response_type='code'
	scope=''
	state=$(uuidgen)
	method='S256'
	challenge=$(code_challenge)

	url="https://users.nexusmods.com/oauth/authorize?client_id=${client_id}&response_type=${response_type}&scope=${scope}&redirect_uri=${redirect_uri}&state=${state}&code_challenge_method=${method}&code_challenge=${challenge}"

	echo "$url"
	
}

function get_token() {
	
	url=$(auth_url)

	printf "Please visit the following URL to authorize the application: \n\n"
	printf "%s" "$url"
	xdg-open "$url" 2>/dev/null || true

}

echo $(get_token)