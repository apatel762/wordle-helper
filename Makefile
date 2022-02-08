all: \
	install

clean:
	rm -rf ./venv

install:
	@./install.sh
	venv/bin/pre-commit install
