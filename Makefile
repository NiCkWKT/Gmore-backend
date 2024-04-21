.PHONY: default setup

default: setup

setup:
	git config core.hooksPath .githooks
	test -d .venv || pdm venv create
	pdm sync
