.PHONY: run _build nxm_handler mo2_lint clean

run: uv run src/mo2-lint/__init__.py

_build: clean nxm_handler mo2_lint

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

clean:
	rm -rf .ruff_cache
	rm -rf build/mo2_lint
	rm -rf build/nxm_handler
	rm -rf build/find_heroic_install
	rm -rf dist
	rm -f mo2_lint.spec
	rm -f nxm_handler.spec
	rm -f find_heroic_install.spec
	find . -type d -name '__pycache__' -exec rm -r {} +
