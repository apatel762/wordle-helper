all: \
	install

clean:
	@echo "no-op"

install:
	@./install.sh
	venv/bin/pre-commit install
