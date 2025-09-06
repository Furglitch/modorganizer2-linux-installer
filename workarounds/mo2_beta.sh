xdg-open "$mo2_url" & disown
xdg-open "$downloads_cache" & disown

"$dialog" infobox "Due to issues with direct downloads, the installer will now open a web page where you can download the latest MO2 beta release.\n\nPlease download the file and save it to:\n/tmp/mo2-linux-installer-downloads-cache/\n\nOnce the download is complete, click Continue to proceed with the installation."
