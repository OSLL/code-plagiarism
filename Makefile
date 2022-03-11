PWD 				:= $(shell pwd)
IMAGE_NAME			:= $(shell basename $(PWD))
UTIL_VERSION		:= $(shell /usr/bin/env python3 src/codeplag/brand_consts.py --version)
UTIL_NAME			:= $(shell /usr/bin/env python3 src/codeplag/brand_consts.py --util_name)
DOCKER_TAG			?= $(shell echo $(IMAGE_NAME)-ubuntu18.04:$(UTIL_VERSION) | tr A-Z a-z)
CODEPLAG_LOG_PATH	:= $(shell /usr/bin/env python3 src/codeplag/consts.py --get_log_path)
WEBPARSERS_LOG_PATH	:= $(shell /usr/bin/env python3 src/webparsers/consts.py --get_log_path)


all: install install-man

install:
	python3 setup.py install
	install -D -m 0755 src/sbin/$(UTIL_NAME) /usr/sbin/$(UTIL_NAME)
	install -D -m 0744 profile.d/$(UTIL_NAME) /etc/profile.d/$(UTIL_NAME).sh

	touch $(CODEPLAG_LOG_PATH)
	chmod 0666 $(CODEPLAG_LOG_PATH)

	touch $(WEBPARSERS_LOG_PATH)
	chmod 0666 $(WEBPARSERS_LOG_PATH)

install-man:
	mkdir -p Man
	argparse-manpage --pyfile src/codeplag/codeplagcli.py \
					 --function get_parser \
					 --author "Codeplag Development Team" \
					 --author-email "inbox@moevm.info" \
					 --project-name "$(UTIL_NAME) $(UTIL_VERSION)" \
					 --url "https://github.com/OSLL/code-plagiarism" \
					 --output man/codeplag.1

	install -D -m 0644 man/codeplag.1 /usr/share/man/man1/$(UTIL_NAME).1

test:
	python3 -m unittest discover ./src
	make clear-cache

test-pytest:
	python3 -m pytest
	make clear-cache

run:
	bash -login

clear-cache:
	find . -type d | grep -E "__pycache__" | xargs rm -r

rm:
	rm -f /etc/profile.d/$(UTIL_NAME).sh
	rm -f /usr/sbin/$(UTIL_NAME)
	rm -f /usr/share/man/man1/$(UTIL_NAME).1
	rm -f man/$(UTIL_NAME).1
	rm -f $(CODEPLAG_LOG_PATH)
	rm -f $(WEBPARSERS_LOG_PATH)
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
		"$(DOCKER_TAG)" /bin/bash -login

docker-rmi:
	docker rmi $(DOCKER_TAG)

help:
	@echo "Usage:"
	@echo "  make [command]"
	@echo
	@echo "Commands:"
	@echo "  install                          Install on the local computer;"
	@echo "  install-man                      Create and install man file."
	@echo "                                   Required argparse-manpage and sudo privilege;"
	@echo "  run                              Run bash with root privileges and in an interactive mode."
	@echo "                                   This is required for correct work of the autocomlete;"
	@echo "  test                             Run unittest;"
	@echo "  test-pytest                      Run pytest;"
	@echo "  clear-cache                      Delete __pycache__ folders;"
	@echo "  rm                               Remove installed package;"
	@echo "  help                             Display this message and exit."
	@echo
	@echo "Docker:"
	@echo "  docker                           Build docker image;"
	@echo "  docker-test                      Test code in docker container;"
	@echo "  docker-run                       Run docker container;"
	@echo "  docker-rmi                       Delete docker image."
	@echo
