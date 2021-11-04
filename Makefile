IMAGE_NAME			:= $(shell basename $(PWD))
DOCKER_TAG			?= $(IMAGE_NAME)-ubuntu:0.0.1

all: install test

install:
	eval "sudo apt update"

	echo "Starting installing requirements..."
	for PACKAGE in clang libncurses5 python3 python3-pip ; do \
		if ! dpkg -l $$PACKAGE >/dev/null 2>/dev/null; then \
			eval "sudo apt install $$PACKAGE" ; \
		fi \
	done

	python3 setup.py install --user

test:
	python3 -m unittest discover -v ./src

test-pytest:
	python3 -m pytest -v

docker:
	docker image build \
		--tag  "$(DOCKER_TAG)" \
		--file Dockerfile \
		.

docker-test:
	docker run --rm \
		"$(DOCKER_TAG)" bash -c \
		'make test'

docker-run:
	docker run --rm --tty --interactive \
		"$(DOCKER_TAG)" /bin/bash
