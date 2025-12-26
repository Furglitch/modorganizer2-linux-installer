venv/bin/activate: requirements.txt
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

run: venv/bin/activate
	./venv/bin/python3 src/mo2-lint/__init__.py

pyinstaller: venv/bin/activate
	rm -rf build/mo2_lint
	rm -rf build/nxm_handler
	rm -rf build/find_heroic_install
	rm -rf dist
	./venv/bin/pyinstaller --onefile --name nxm_handler \
		--paths src \
		--hidden-import find_heroic_install \
		--hidden-import pydantic_core \
		--add-data "src/nxm-handler:src" \
		--runtime-hook "build/runtime_hooks.py" \
		src/nxm-handler/__init__.py
	./venv/bin/pyinstaller --onefile --name mo2_lint \
		--paths src \
		--hidden-import patoolib \
		--hidden-import requests \
		--add-data "src/mo2-lint:src" \
		--add-data "configs:cfg" \
		--add-data "dist:dist" \
		--runtime-hook "build/runtime_hooks.py" \
		src/mo2-lint/__init__.py

clean:
	rm -rf venv
	rm -rf .ruff_cache
	rm -rf build/mo2_lint
	rm -rf build/nxm_handler
	rm -rf build/find_heroic_install
	rm -rf dist
	rm -rf mo2_lint.spec
	rm -rf nxm_handler.spec
	rm -rf find_heroic_install.spec
	find . -type d -name '__pycache__' -exec rm -r {} +

revenv:
	rm -rf venv
	rm -rf .ruff_cache
	rm -rf build/mo2_lint
	rm -rf build/nxm_handler
	rm -rf build/find_heroic_install
	rm -rf dist
	rm -rf mo2_lint.spec
	rm -rf nxm_handler.spec
	rm -rf find_heroic_install.spec
	find . -type d -name '__pycache__' -exec rm -r {} +
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt
