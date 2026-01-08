venv/bin/activate: requirements.txt
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

run: venv/bin/activate
	./venv/bin/python3 src/mo2-lint/__init__.py

_build: venv/bin/activate
	make clean
	make redirector
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

redirector:
    rm -f src/steam-redirector/redirector.exe || true
	(cd src/steam-redirector && \
	x86_64-w64-mingw32-gcc -v -municode -static -static-libgcc -Bstatic -lpthread -mwindows -o redirector.exe main.c win32_utils.c)
	mkdir -p dist
	cp src/steam-redirector/redirector.exe dist/redirector.exe
	chmod +x dist/redirector.exe || true

clean:
	rm -rf .ruff_cache
	rm -rf build/mo2_lint
	rm -rf build/nxm_handler
	rm -rf build/find_heroic_install
	rm -rf dist
	rm -f dist/redirector.exe
	rm -f mo2_lint.spec
	rm -f nxm_handler.spec
	rm -f find_heroic_install.spec
	find . -type d -name '__pycache__' -exec rm -r {} +

revenv:
	make clean
	rm -rf venv
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt
