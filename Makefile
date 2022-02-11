all: \
	install \
	run

run:
	venv/bin/python wordle.py

clean:
	rm -rf ./venv

install:
	@./install.sh
	venv/bin/pre-commit install
