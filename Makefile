VIRTUALENV=.env
BIN=$(VIRTUALENV)/bin

default: setup
	$(BIN)/python build.py

upload: setup
	echo TODO

watch: setup
	while inotifywait -e close_write dist static build.py articles; do $(BIN)/python build.py; done

setup:
	if [ -f "$(VIRTUALENV)" ]; then echo "Virtualenv exists"; else virtualenv -p `which python3` $(VIRTUALENV); fi
	$(BIN)/pip install -r requirements.txt
