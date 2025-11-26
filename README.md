<img src="./.github/README/logo.svg" alt="Mod Organizer 2 Linux Installer Logo" width="96" align="left" />
# Mod Organizer 2 Linux Installer (MO2-LINT)
<br clear="left"/>

Currently, MO2-LINT is almost written entirely in Bash. (As stated by the original developer)[https://github.com/Furglitch/modorganizer2-linux-installer/issues/182#issuecomment-740300503], this was due to it's ease of access and integration.

But, as the functionality and userbase of this project has grown, the cracks in approach have started to show. The codebase is becoming increasingly difficult to manage and expand upon.

As such, the project will be rewritten in it's entirety, switching over to Python.

---

Our goals with this rewrite are as follows:
* **Preserve the Functionality of the Original Script** - Set-up of the MO2 instances, related game's Proton prefix, NXM protocol integration and Steam Redirector (The "simply click play in Steam" part).
* **Improve User Experience** - Give users a clearer and more streamlined installer. Visually pleasing is a plus.
  * **Troubleshooting** - Provide clearer logging so that less adept users might be more able to resolve issues on their own.
  * **Instance Management** - Allow users to modify or uninstall existing instances of MO2.
* **Improve Contributor Experience** - Improve script readability and expansion capability.
  * **Linting** - Enforce code styles with pre-commit hooks and linters.
* **Improve Distribution** - Package MO2-LINT as an AppImage, rather than multiple scripts in a .tar file.
* **Improve Downloads** - Decrease the resource-intensiveness of downloads for the MO2 instance
  * **Caching** - The script will cache external resources locally for future use, for the benefit of file providers and those will less capable hardware/ISPs.
  * **Cache Purging** - Cache purging will no longer occur whenever the script fails, as it did originally.

This is not a firm or all-inclusive list. For more detailed information, see the discussion thread [here](https://github.com/Furglitch/modorganizer2-linux-installer/discussions/873).