venv/bin/activate: requirements.txt
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

run: venv/bin/activate
	./venv/bin/python3 src/mo2-lint/__init__.py

pyinstaller: venv/bin/activate
	./venv/bin/pyinstaller --onefile --name mo2-lint \
		--paths src \
		--add-data "src/mo2-lint:src" \
		--add-data "configs:cfg" \
		--runtime-hook "build/runtime_hooks.py" \
		src/mo2-lint/__init__.py

clean:
	rm -rf venv
	rm -rf .ruff_cache
	find . -type d -name '__pycache__' -exec rm -r {} +
