UTIL_VERSION            := 0.2.2
UTIL_NAME               := codeplag

BASE_DOCKER_TAG         := $(shell echo $(UTIL_NAME)-base-ubuntu20.04:$(UTIL_VERSION) | tr A-Z a-z)
TEST_DOCKER_TAG         := $(shell echo $(UTIL_NAME)-test-ubuntu20.04:$(UTIL_VERSION) | tr A-Z a-z)
DOCKER_TAG              ?= $(shell echo $(UTIL_NAME)-ubuntu20.04:$(UTIL_VERSION) | tr A-Z a-z)

PWD                     := $(shell pwd)
PYTHONPATH              = $(PWD)/src/
LOGS_PATH               := /var/log/codeplag
CODEPLAG_LOG_PATH       := $(LOGS_PATH)/$(UTIL_NAME).log
WEBPARSERS_LOG_PATH     := $(LOGS_PATH)/webparsers.log
SOURCE_SUB_FILES        := src/codeplag/consts.py \
                           src/webparsers/consts.py
DEBIAN_SUB_FILES        := debian/changelog \
                           debian/control \
                           debian/preinst \
                           debian/postinst \
                           debian/copyright
DOCKER_SUB_FILES        := docker/base_ubuntu2004.dockerfile \
                           docker/test_ubuntu2004.dockerfile \
                           docker/ubuntu2004.dockerfile
PYTHON_REQUIRED_LIBS    := $(shell python3 setup.py --install-requirements)


all: substitute_sources man install

# $< - %.in file, $@ desired file %
%: %.in
	sed \
		-e "s|@UTIL_NAME@|${UTIL_NAME}|g" \
		-e "s|@UTIL_VERSION@|${UTIL_VERSION}|g" \
		-e "s|@WEBPARSERS_LOG_PATH@|${WEBPARSERS_LOG_PATH}|g" \
		-e "s|@CODEPLAG_LOG_PATH@|${CODEPLAG_LOG_PATH}|g" \
		-e "s|@PYTHON_REQUIRED_LIBS@|${PYTHON_REQUIRED_LIBS}|g" \
		-e "s|@LOGS_PATH@|${LOGS_PATH}|g" \
		$< > $@

substitute_sources: $(SOURCE_SUB_FILES)
	@echo "Substituting of information about the utility in the source files"

substitute_debian: $(DEBIAN_SUB_FILES)
	@echo "Substituting of information about the utility in the debian files"

substitute_docker: $(DOCKER_SUB_FILES)
	@echo "Substituting of information about the utility in the docker files"

man: substitute_sources
	mkdir -p man
	argparse-manpage --pyfile src/codeplag/codeplagcli.py \
					 --function CodeplagCLI \
					 --author "Codeplag Development Team" \
					 --project-name "$(UTIL_NAME) $(UTIL_VERSION)" \
					 --url "https://github.com/OSLL/code-plagiarism" \
					 --output man/$(UTIL_NAME).1

install: substitute_sources man
	python3 -m pip install --root=/$(DESTDIR) .

	mkdir -p $(DESTDIR)/$(LOGS_PATH)
	chmod 0777 $(DESTDIR)/$(LOGS_PATH)

	install -D -m 0644 man/$(UTIL_NAME).1 $(DESTDIR)/usr/share/man/man1/$(UTIL_NAME).1

package: substitute_debian
	find debian/deb/$(UTIL_NAME)* > /dev/null 2>&1 || ( \
		dpkg-buildpackage -jauto -b \
			--buildinfo-option="-u$(CURDIR)/debian/deb" \
			--changes-option="-u$(CURDIR)/debian/deb" \
			--no-sign \
	)

test: substitute_sources
	pytest test/unit -q
	make clean-cache

autotest:
	pytest test/auto -q
	make clean-cache

clean-cache:
	find . -maxdepth 1 -type d | grep -E "pytest_cache" | (xargs rm -r 2> /dev/null || exit 0)
	find . -type d | grep -E "__pycache__" | (xargs rm -r 2> /dev/null || exit 0)

clean: clean-cache
	rm --force --recursive man/
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive debian/deb/*
	rm --force --recursive debian/.debhelper/
	rm --force --recursive debian/codeplag-util/
	rm --force debian/debhelper-build-stamp
	rm --force debian/files
	rm --force debian/codeplag-util.debhelper.log
	rm --force debian/codeplag-util.substvars
	rm --force --recursive src/codeplag.egg-info

clean-all: clean
	rm --force src/codeplag/consts.py
	rm --force src/webparsers/consts.py

	rm --force docker/base_ubuntu2004.dockerfile
	rm --force docker/test_ubuntu2004.dockerfile
	rm --force docker/ubuntu2004.dockerfile

	rm --force debian/changelog
	rm --force debian/control
	rm --force debian/preinst
	rm --force debian/postinst
	rm --force debian/copyright

uninstall:
	rm --force /usr/share/man/man1/$(UTIL_NAME).1
	pip3 uninstall $(UTIL_NAME) -y

docker-base-image: substitute_sources substitute_docker
	docker image inspect $(BASE_DOCKER_TAG) > /dev/null 2>&1 || ( \
		export DOCKER_BUILDKIT=1 && \
		docker image build \
			--tag "$(BASE_DOCKER_TAG)" \
			--file docker/base_ubuntu2004.dockerfile \
			. \
	)

docker-test-image: docker-base-image substitute_debian
	docker image inspect $(TEST_DOCKER_TAG) > /dev/null 2>&1 || \
	docker image build \
		--tag  "$(TEST_DOCKER_TAG)" \
		--file docker/test_ubuntu2004.dockerfile \
		.

docker-test: docker-test-image
	docker run --rm \
		--volume $(PWD)/test:/usr/src/$(UTIL_NAME)/test \
		"$(TEST_DOCKER_TAG)"

docker-autotest: docker-test-image
	docker run --rm \
		--volume $(PWD)/test:/usr/src/$(UTIL_NAME)/test \
		--env-file .env \
		"$(TEST_DOCKER_TAG)" bash -c \
		"make && make autotest"

docker-build-package: docker-test-image
	docker run --rm \
		--volume $(PWD)/debian/deb:/usr/src/$(UTIL_NAME)/debian/deb \
		"$(TEST_DOCKER_TAG)" bash -c \
		"make package"

docker-image: docker-base-image docker-test-image
	docker image inspect $(DOCKER_TAG) > /dev/null 2>&1 || ( \
		make docker-test && \
		make docker-build-package && \
		docker image build \
			--tag  "$(DOCKER_TAG)" \
			--file docker/ubuntu2004.dockerfile \
			. \
	)

docker-run: docker-image
	docker run --rm --tty --interactive \
		"$(DOCKER_TAG)"

docker-rmi:
	@docker rmi $(DOCKER_TAG) --force 2> /dev/null || \
	echo "Image $(DOCKER_TAG) is not exists"

	@docker rmi $(TEST_DOCKER_TAG) --force 2> /dev/null || \
	echo "Image $(TEST_DOCKER_TAG) is not exists"

	@docker rmi $(BASE_DOCKER_TAG) --force 2> /dev/null || \
	echo "Image $(BASE_DOCKER_TAG) is not exists"

help:
	@echo "Usage:"
	@echo "  make [command]"
	@echo
	@echo "Commands:"
	@echo "  install                Install on the local computer without using package manager;"
	@echo "  uninstall              Remove installed util from system;"
	@echo "  man                    Create man file."
	@echo "                         Require argparse-manpage python library;"
	@echo "  test                   Runs unit tests with pytest framework;"
	@echo "  autotest               Runs auto tests."
	@echo "                         Required installed codeplag util and provided ACCESS_TOKEN;"
	@echo "  package                Build the debian package;"
	@echo "  clean-cache            Delete __pycache__ folders created by pytest framework;"
	@echo "  clean                  Remove generated while installing and testing files in the source directory (contains clean-cache);"
	@echo "  clean-all              Remove all generated files such as created docker files, debian and sources (contains clean);"
	@echo "  help                   Display this message and exit."
	@echo
	@echo "Docker:"
	@echo "  docker-run             Runs docker container with installed util;"
	@echo "  docker-image           Build docker image;"
	@echo "  docker-test            Runs unit tests with pytest framework in the docker container;"
	@echo "  docker-autotest        Runs autotests in docker container;"
	@echo "  docker-build-package   Build the debian package in special docker image;"
	@echo "  docker-rmi             Delete created docker images."
	@echo


.EXPORT_ALL_VARIABLES:
.PHONY: all test man
