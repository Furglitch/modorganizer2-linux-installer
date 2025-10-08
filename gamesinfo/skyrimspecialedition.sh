game_steam_subdirectory="Skyrim Special Edition"
game_nexusid="skyrimspecialedition"
game_appid=489830
game_gog_productid=1711230643
game_epic_productid=""
game_executable="SkyrimSELauncher.exe"
game_protontricks=("xaudio2_7=native" "xact" "d3dcompiler_43" "vcrun2022")
declare -A game_scriptextender_urls=(
	["steam"]="https://skse.silverlock.org/beta/skse64_2_02_06.7z"
	["gog"]=""
	["epic"]=""
)
game_scriptextender_files=(
	"skse64_2_02_06/Data"
	"skse64_2_02_06/skse64_1_6_1170.dll"
	"skse64_2_02_06/skse64_loader.exe"
)
