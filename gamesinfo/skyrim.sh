game_steam_subdirectory="Skyrim"
game_nexusid="skyrim"
game_appid=72850
game_gog_productid=""
game_epic_productid=""
game_executable="SkyrimLauncher.exe"
game_protontricks=("d3dcompiler_43" "d3dx9")
declare -A game_scriptextender_urls=(
	["steam"]="https://skse.silverlock.org/beta/skse_1_07_03.7z"
	["gog"]=""
	["epic"]=""
)
game_scriptextender_files=(
	"skse_1_07_03/Data"
	"skse_1_07_03/skse_1_9_32.dll"
	"skse_1_07_03/skse_loader.exe"
	"skse_1_07_03/skse_steam_loader.dll"
)
