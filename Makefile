PWD 				:= $(shell pwd)
IMAGE_NAME			:= $(shell basename $(PWD))
DOCKER_TAG			?= $(IMAGE_NAME)-ubuntu:0.0.2
UTIL_NAME			:= codeplag

all: install install-man test

install:
	python3 setup.py install
	install -D -m 0755 src/sbin/$(UTIL_NAME) /usr/sbin/$(UTIL_NAME)

install-man:
	mkdir -p Man
	argparse-manpage --pyfile src/codeplag/codeplagcli.py \
					 --function get_parser \
					 --author "Codeplag Development Team" \
					 --author-email "inbox@moevm.info" \
					 --project-name "$(UTIL_NAME) 0.0.2" \
					 --url "https://github.com/OSLL/code-plagiarism" \
					 --output man/codeplag.1

	install -D -m 0644 man/codeplag.1 /usr/share/man/man1/codeplag.1

test:
	python3 -m unittest discover ./src
	make clear-cache

test-pytest:
	python3 -m pytest
	make clear-cache

clear-cache:
	find . -type d | grep -E "__pycache__" | xargs rm -r

rm:
	pip3 uninstall $(UTIL_NAME) -y

docker:
	docker image build \
		--tag  "$(DOCKER_TAG)" \
		--file Dockerfile \
		--build-arg UTIL_NAME="$(UTIL_NAME)" \
		.

docker-test:
	docker run --rm \
		"$(DOCKER_TAG)" bash -c \
		'make test'

docker-run:
	docker run --rm --tty --interactive \
		"$(DOCKER_TAG)" /bin/bash

docker-rmi:
	docker rmi $(DOCKER_TAG)

help:
	@echo "Usage:"
	@echo "  make [command]"
	@echo
	@echo "Commands:"
	@echo "  install                          Install on the local computer"
	@echo "  install-man                      Create and install man file."
	@echo "                                   Required argparse-manpage and sudo privilege"
	@echo "  test                             Run unittest"
	@echo "  test-pytest                      Run pytest"
	@echo "  clear-cache                      Delete __pycache__ folders"
	@echo "  rm                               Remove installed package"
	@echo "  help                             Display this message and exit"
	@echo
	@echo "Docker:"
	@echo "  docker                           Build docker image"
	@echo "  docker-test                      Test code in docker container"
	@echo "  docker-run                       Run docker container"
	@echo "  docker-rmi                       Delete docker image"
	@echo
