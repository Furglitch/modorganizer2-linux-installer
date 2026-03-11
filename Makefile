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
	export WINEARCH=win64; \
	echo "Checking for Windows Python at $$WINEPREFIX/drive_c/python313/python.exe"; \
	if [ ! -f "$$WINEPREFIX/drive_c/python313/python.exe" ]; then \
		echo "ERROR: Windows Python not found. WINEPREFIX=$$WINEPREFIX"; \
		ls -la "$$WINEPREFIX/drive_c/" 2>/dev/null || echo "drive_c directory not found"; \
		exit 1; \
	fi; \
	echo "Building redirector..."; \
	WINEPREFIX="$$WINEPREFIX" WINEARCH=win64 wine "C:\\python313\\python.exe" -m pip install -q --upgrade pip pyinstaller loguru pyyaml 2>&1 | grep -v '^[0-9a-f]*:' || true; \
	WINEPREFIX="$$WINEPREFIX" WINEARCH=win64 wine "C:\\python313\\python.exe" -m PyInstaller --onefile --noconsole --name mo2-redirector.exe \
		--paths src --hidden-import loguru --hidden-import yaml --hidden-import configparser \
		--add-data "configs;cfg" --icon .github/README/logo.ico src/redirector/__init__.py 2>&1 | grep -E '(Building|WARNING|ERROR|completed)' || true
	@chmod +x dist/mo2-redirector.exe 2>/dev/null || true
	@echo "Done. Verify: file dist/mo2-redirector.exe"

setup-wine-python:
	@command -v wine >/dev/null 2>&1 || { echo "ERROR: wine not found"; exit 1; }
	@command -v wget >/dev/null 2>&1 || command -v curl >/dev/null 2>&1 || { echo "ERROR: wget or curl not found"; exit 1; }
	@command -v unzip >/dev/null 2>&1 || { echo "ERROR: unzip not found"; exit 1; }
	@WINEPREFIX=$${WINEPREFIX:-$$HOME/.wine-py}; \
	export WINEARCH=win64; \
	if [ ! -f "$$WINEPREFIX/drive_c/python313/python.exe" ]; then \
		echo "Installing Python 3.13 embeddable (Windows) to $$WINEPREFIX..."; \
		mkdir -p "$$WINEPREFIX/drive_c/python313"; \
		cd "$$WINEPREFIX/drive_c/python313"; \
		wget -q --show-progress https://www.python.org/ftp/python/3.13.0/python-3.13.0-embed-amd64.zip 2>/dev/null || \
		curl -# -L https://www.python.org/ftp/python/3.13.0/python-3.13.0-embed-amd64.zip -o python-3.13.0-embed-amd64.zip || { echo "ERROR: Failed to download Python"; exit 1; }; \
		unzip -q python-3.13.0-embed-amd64.zip && rm -f python-3.13.0-embed-amd64.zip; \
		echo "Installing pip..."; \
		wget -q https://bootstrap.pypa.io/get-pip.py 2>/dev/null || curl -# -L https://bootstrap.pypa.io/get-pip.py -o get-pip.py; \
		WINEPREFIX="$$WINEPREFIX" wine python.exe get-pip.py --no-warn-script-location 2>&1 | grep -v '^[0-9a-f]*:' || true; \
		rm -f get-pip.py; \
		echo "Python 3.13 installed at $$WINEPREFIX/drive_c/python313/python.exe"; \
	else \
		echo "Python already installed at $$WINEPREFIX/drive_c/python313/python.exe"; \
	fi

clean:
	rm -rf .ruff_cache
	find build -maxdepth 1 -mindepth 1 ! -name 'hooks' ! -name 'runtime_hooks.py' -exec rm -rf {} +
	rm -rf dist
	rm -f *.spec
	find . -type d -name '__pycache__' -exec rm -r {} +
