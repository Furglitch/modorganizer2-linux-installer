#!/usr/bin/env bash

download="$utils/download.sh"
extract="$utils/extract.sh"

jdk_url='https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u312-b07/OpenJDK8U-jre_x64_windows_hotspot_8u312b07.zip'

mo2_url='https://1drv.ms/u/c/371272c49a37cc4a/EdGmNLqk43hBl__pDggWoCcBRT8T1N_hd-o3HkdWADqPtA'
mo2_sha256='a9f36c8f622491fe7ce8e9feeb685b7c80a37eb0880bd81a23e139c7bdeb42a2'

winetricks_url='https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks'

downloaded_jdk="$downloads_cache/${jdk_url##*/}"
extracted_jdk="${downloaded_jdk%.*}"
downloaded_winetricks="$downloads_cache/winetricks"
executable_winetricks="$shared/winetricks"

downloaded_mo2="$downloads_cache/Mod.Organizer-2.5.3beta2.7z"
extracted_mo2="${downloaded_mo2%.*}"

downloaded_scriptextender=""
extracted_scriptextender=""

downloaded_plugins=()
extracted_plugins=()

function validate_sha256() {
	local file="$1"
	local expected="$2"
	if [ ! -f "$file" ]; then
		return 1
	fi
	local actual
	actual=$(sha256sum "$file" | awk '{print $1}')
	if [ "$actual" != "$expected" ]; then
		log_info "Checksum mismatch for $file: expected $expected, got $actual. Removing file."
		rm -f "$file"
		return 1
	fi
	return 0
}

if [ -n "$game_scriptextender_url" ]; then
	downloaded_scriptextender="$downloads_cache/${game_nexusid}_${game_scriptextender_url##*/}"
	extracted_scriptextender="${downloaded_scriptextender%.*}"
fi

if [ -n "$plugin_download_urls" ]; then
	IFS=' ' read -ra plugin_download_urls <<< "${plugin_download_urls[@]}"
	for url in "${plugin_download_urls[@]}"; do
		downloaded_plugin="$downloads_cache/${url##*/}"
		extracted_plugin="${downloaded_plugin%.*}"
		downloaded_plugins+=("$downloaded_plugin")
		extracted_plugins+=("$extracted_plugin")
	done
else 
	downloaded_plugins=("")
	extracted_plugins=("")
fi

function purge_downloads_cache() {
	if [ -f "$downloaded_scriptextender" ]; then
		log_info "removing '$downloaded_scriptextender'"
		rm "$downloaded_scriptextender"

		if [ -d "$extracted_scriptextender" ]; then
			log_info "removing '$extracted_scriptextender'"
			rm -rf "$extracted_scriptextender"
		fi
	fi

	if [ -f "$downloaded_mo2" ]; then
		log_info "removing '$downloaded_mo2'"
		rm "$downloaded_mo2"

		if [ -d "$extracted_mo2" ]; then
			log_info "removing '$extracted_mo2'"
			rm -rf "$extracted_mo2"
		fi
	fi

	if [ -f "$downloaded_jdk" ]; then
		log_info "removing '$downloaded_jdk'"
		rm "$downloaded_jdk"

		if [ -d "$extracted_jdk" ]; then
			log_info "removing '$extracted_jdk'"
			rm -rf "$extracted_jdk"
		fi
	fi

	if [ -f "$downloaded_winetricks" ]; then
		log_info "removing '$downloaded_winetricks'"
		rm "$downloaded_winetricks"
	fi

	for file in "${downloaded_plugins[@]}"; do
		if [ -f "$file" ]; then
			log_info "removing '$file'"
			rm "$file"
		fi
	done

	for dir in "${extracted_plugins[@]}"; do
		if [ -d "$dir" ]; then
			log_info "removing '$dir'"
			rm -rf "$dir"
		fi
	done
}

if [ "$cache_enabled" == "0" ]; then
	purge_downloads_cache
fi

started_download_step=1

if [ ! -f "$downloaded_jdk" ]; then
	"$download" "$jdk_url" "$downloaded_jdk"
	mkdir "$extracted_jdk"
	"$extract" "$downloaded_jdk" "$extracted_jdk"
fi

mo2_attempts=0
mo2_max_attempts=2
while ! validate_sha256 "$downloaded_mo2" "$mo2_sha256"; do
	mo2_attempts=$((mo2_attempts + 1))
	if [ "$mo2_attempts" -ge "$mo2_max_attempts" ]; then
		log_info "Failed to match checksum of downloaded MO2 after $mo2_max_attempts attempts. Aborting."
		exit 1
	fi
	log_info "Running MO2 beta download workaround"
	source "$workarounds/mo2_beta.sh"
	#log_info "Attempt $mo2_attempts: Downloading MO2 again due to checksum failure."
	#rm -f "$downloaded_mo2"
	#"$download" "$mo2_url" "$downloaded_mo2"
done
if [ ! -d "$extracted_mo2" ]; then
	mkdir "$extracted_mo2"
	"$extract" "$downloaded_mo2" "$extracted_mo2"
fi

if [ ! -f "$downloaded_winetricks" ]; then
	"$download" "$winetricks_url" "$downloaded_winetricks"
fi
cp "$downloaded_winetricks" "$executable_winetricks"
chmod u+x "$executable_winetricks"

if [ "$install_extras" == true ] && [ -n "$downloaded_scriptextender" ] && [ ! -f "$downloaded_scriptextender" ]; then
	"$download" "$game_scriptextender_url" "$downloaded_scriptextender"
	mkdir "$extracted_scriptextender"
	"$extract" "$downloaded_scriptextender" "$extracted_scriptextender"
fi

if [ -n "$downloaded_plugins" ]; then
	for i in "${!downloaded_plugins[@]}"; do
		if [ ! -f "${downloaded_plugins[$i]}" ]; then
			"$download" "${plugin_download_urls[$i]}" "${downloaded_plugins[$i]}"
			mkdir "${extracted_plugins[$i]}"
			"$extract" "${downloaded_plugins[$i]}" "${extracted_plugins[$i]}"
		fi
	done
fi