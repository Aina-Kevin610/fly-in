SRCS = parsing.py fly_in.py

install: venv/bin/python3
	venv/bin/pip install -r requirements.txt

venv/bin/python3:
	python3 -m venv venv

run: install
	venv/bin/python3 fly_in.py

lint:
	venv/bin/flake8 $(SRCS)
	venv/bin/mypy --warn-return-any \
--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
--check-untyped-defs $(SRCS)

clean:
	rm -rf __pycache__ .vscode .mypy_cache

.PHONY: install run clean