.PHONY: run _build redirector nxm_handler mo2_lint clean

run: uv run src/mo2-lint/__init__.py

_build: clean redirector nxm_handler mo2_lint

mo2_lint:
	uv run pyinstaller --onefile --name mo2_lint \
		--paths src \
		--hidden-import InquirerPy \
		--hidden-import patoolib \
		--hidden-import protontricks \
		--hidden-import pydantic_core \
		--hidden-import requests \
		--hidden-import send2trash \
		--hidden-import websockets \
		--hidden-import yaml \
		--add-data "src/mo2-lint:src" \
		--add-data "configs:cfg" \
		--add-data "dist:dist" \
		--runtime-hook "build/runtime_hooks.py" \
		--additional-hooks-dir "build/hooks" \
		src/mo2-lint/__init__.py

nxm_handler:
	uv run pyinstaller --onefile --name nxm_handler \
		--paths src \
		--hidden-import find_heroic_install \
		--hidden-import protontricks \
		--hidden-import pydantic_core \
		--add-data "src/nxm-handler:src" \
		--runtime-hook "build/runtime_hooks.py" \
		--additional-hooks-dir "build/hooks" \
		src/nxm-handler/__init__.py

redirector: setup-wine-python
	@WINEPREFIX=$${WINEPREFIX:-$$HOME/.wine-py}; \
	if [ ! -f "$$WINEPREFIX/drive_c/Program Files/Python311/python.exe" ]; then \
		echo "ERROR: Run 'make setup-wine-python' first."; exit 1; \
	fi; \
	echo "Building redirector..."; \
	WINEPREFIX="$$WINEPREFIX" wine "C:\\Program Files\\Python311\\python.exe" -m pip install -q --upgrade pip pyinstaller loguru pyyaml 2>&1 | grep -v '^[0-9a-f]*:' || true; \
	WINEPREFIX="$$WINEPREFIX" wine "C:\\Program Files\\Python311\\python.exe" -m PyInstaller --onefile --noconsole --name mo2-redirector.exe \
		--paths src --hidden-import loguru --hidden-import yaml --hidden-import configparser \
		--add-data "configs;cfg" --icon .github/README/logo.ico src/redirector/__init__.py 2>&1 | grep -E '(Building|WARNING|ERROR|completed)' || true
	@chmod +x dist/mo2-redirector.exe 2>/dev/null || true
	@echo "Done. Verify: file dist/mo2-redirector.exe"

setup-wine-python:
	@command -v wine >/dev/null 2>&1 || { echo "ERROR: wine not found"; exit 1; }
	@command -v wget >/dev/null 2>&1 || command -v curl >/dev/null 2>&1 || { echo "ERROR: wget or curl not found"; exit 1; }
	@WINEPREFIX=$${WINEPREFIX:-$$HOME/.wine-py}; \
	if [ ! -d "$$WINEPREFIX/drive_c/Program Files/Python311" ]; then \
		echo "Installing Python (Windows) to $$WINEPREFIX..."; \
		mkdir -p /tmp/wine-python-setup && cd /tmp/wine-python-setup; \
		wget -q --show-progress https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe -O py.exe 2>/dev/null || \
		curl -# -L https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe -o py.exe || { echo "ERROR: Failed to download Python installer"; exit 1; }; \
		WINEPREFIX="$$WINEPREFIX" wine py.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 2>&1 | grep -v '^[0-9a-f]*:' || true; \
		sleep 3; cd - >/dev/null; rm -rf /tmp/wine-python-setup; \
		echo "Done. Run: make redirector"; \
	else \
		echo "Python already installed."; \
	fi

clean:
	rm -rf .ruff_cache
	find build -maxdepth 1 -mindepth 1 ! -name 'hooks' ! -name 'runtime_hooks.py' -exec rm -rf {} +
	rm -rf dist
	rm -f *.spec
	find . -type d -name '__pycache__' -exec rm -r {} +
