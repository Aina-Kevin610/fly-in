GREEN  := \033[0;32m
NC     := \033[0m
RED    := \033[0;31m
SRCS	=	parsing.py \
			fly_in.py \
			utils.py

install: venv/bin/python3
	@echo "$(GREEN)installing all dependencies...$(NC)"
	@venv/bin/pip install -r requirements.txt > /dev/null 2>&1

venv/bin/python3:
	@echo "$(GREEN)creating a virtual environement...$(NC)"
	@python3 -m venv venv > /dev/null 2>&1

run: install
	venv/bin/python3 fly_in.py

lint:
	@echo "$(GREEN)checking lint...$(NC)"
	@venv/bin/flake8 $(SRCS) > /dev/null 2>&1
	@venv/bin/mypy --warn-return-any \
--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
--check-untyped-defs $(SRCS) > /dev/null 2>&1
	

clean:
	@echo "$(RED)Cleanning...$(NC)"
	@m -rf __pycache__ .vscode .mypy_cache > /dev/null 2>&1

.PHONY: install run clean