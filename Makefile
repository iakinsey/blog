VIRTUALENV=.env
BIN=$(VIRTUALENV)/bin

default: setup
	$(BIN)/python build.py

upload: setup
	echo TODO

setup:
	if [ -f "$(VIRTUALENV)" ]; then echo "Virtualenv exists"; else virtualenv -p `which python3` $(VIRTUALENV); fi
	$(BIN)/pip install -r requirements.txt
