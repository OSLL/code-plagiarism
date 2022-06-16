PWD 					:= $(shell pwd)
IMAGE_NAME				:= $(shell basename $(PWD))
UTIL_VERSION			:= 0.1.5
UTIL_NAME				:= codeplag
DOCKER_TAG				?= $(shell echo $(IMAGE_NAME)-ubuntu18.04:$(UTIL_VERSION) | tr A-Z a-z)
LOGS_PATH				:= /var/log
CODEPLAG_LOG_PATH		:= $(LOGS_PATH)/$(UTIL_NAME).log
WEBPARSERS_LOG_PATH		:= $(LOGS_PATH)/webparsers.log


CONVERTED_FILES 		:= src/codeplag/consts.py \
						   src/webparsers/consts.py


all: substitute install install-man

# $< - %.in file, $@ desired file %
%: %.in
	sed \
		-e "s|@UTIL_NAME@|${UTIL_NAME}|g" \
		-e "s|@UTIL_VERSION@|${UTIL_VERSION}|g" \
		-e "s|@WEBPARSERS_LOG_PATH@|${WEBPARSERS_LOG_PATH}|g" \
		-e "s|@CODEPLAG_LOG_PATH@|${CODEPLAG_LOG_PATH}|g" \
		$< > $@

substitute: $(CONVERTED_FILES)
	@echo "Substituting of information about the utility in files"

install: substitute
	python3 -m pip install .
	install -D -m 0755 src/sbin/$(UTIL_NAME) /usr/sbin/$(UTIL_NAME)
	install -D -m 0744 profile.d/$(UTIL_NAME) /etc/profile.d/$(UTIL_NAME).sh

	touch $(CODEPLAG_LOG_PATH)
	chmod 0666 $(CODEPLAG_LOG_PATH)

	touch $(WEBPARSERS_LOG_PATH)
	chmod 0666 $(WEBPARSERS_LOG_PATH)

install-man: substitute
	mkdir -p Man
	argparse-manpage --pyfile src/codeplag/codeplagcli.py \
					 --function get_parser \
					 --author "Codeplag Development Team" \
					 --author-email "inbox@moevm.info" \
					 --project-name "$(UTIL_NAME) $(UTIL_VERSION)" \
					 --url "https://github.com/OSLL/code-plagiarism" \
					 --output man/codeplag.1

	install -D -m 0644 man/codeplag.1 /usr/share/man/man1/$(UTIL_NAME).1


test: substitute
	python3 -m pytest -q
	make clear-cache

autotest: substitute
	codeplag --version || \
	exit $?
	@echo "\n\n"

	codeplag --extension cpp \
			 --files test/codeplag/cplag/data/sample1.cpp test/codeplag/cplag/data/sample2.cpp || \
	exit $?
	@echo "\n\n"

	codeplag --extension cpp \
			 --directories test/codeplag/cplag/data || \
	exit $?
	@echo "\n\n"

	codeplag --extension cpp \
			 --github-files https://github.com/OSLL/code-plagiarism/blob/main/test/codeplag/cplag/data/sample3.cpp \
			 				https://github.com/OSLL/code-plagiarism/blob/main/test/codeplag/cplag/data/sample4.cpp || \
	exit $?
	@echo "\n\n"

	codeplag --extension cpp \
			--github-project-folders https://github.com/OSLL/code-plagiarism/tree/main/test || \
	exit $?
	@echo "\n\n"

	codeplag --extension cpp \
			 --github-user OSLL \
			 --regexp "code-plag" || \
	exit $?
	@echo "\n\n"

	codeplag --extension py \
			 --directories test/codeplag/cplag \
			 --files src/codeplag/pyplag/astwalkers.py || \
	exit $?
	@echo "\n\n"

	codeplag --extension py \
			 --github-files https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag/utils.py \
							https://github.com/OSLL/code-plagiarism/blob/main/setup.py || \
	exit $?
	@echo "\n\n"

	codeplag --extension py \
			 --github-user OSLL \
			 --regexp "code-plag" || \
	exit $?
	@echo "\n\n"

	codeplag --extension py \
			 --github-project-folders https://github.com/OSLL/code-plagiarism/blob/main/src/codeplag/pyplag || \
	exit $?

run:
	bash -login

clear-cache:
	find . -maxdepth 1 -type d | grep -E "pytest_cache" | (xargs rm -r 2> /dev/null || exit 0)
	find . -type d | grep -E "__pycache__" | (xargs rm -r 2> /dev/null || exit 0)

uninstall:
	rm --force /etc/profile.d/$(UTIL_NAME).sh
	rm --force /usr/sbin/$(UTIL_NAME)
	rm --force /usr/share/man/man1/$(UTIL_NAME).1
	rm --force man/$(UTIL_NAME).1
	rm --force $(WEBPARSERS_LOG_PATH)
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force src/codeplag/consts.py
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
		"make test"

docker-autotest:
	docker run --rm \
		"$(DOCKER_TAG)" bash -c \
		"make autotest"

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
	@echo "  test                             Run pytest;"
	@echo "  clear-cache                      Delete __pycache__ folders;"
	@echo "  uninstall                        Remove installed package;"
	@echo "  help                             Display this message and exit."
	@echo
	@echo "Docker:"
	@echo "  docker                           Build docker image;"
	@echo "  docker-test                      Test code in docker container;"
	@echo "  docker-run                       Run docker container;"
	@echo "  docker-rmi                       Delete docker image."
	@echo
