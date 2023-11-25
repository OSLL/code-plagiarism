UTIL_VERSION            := 0.4.0
UTIL_NAME               := codeplag
PWD                     := $(shell pwd)

USER_UID                ?= $(shell id --user)
USER_GID                ?= $(shell id --group)

BASE_DOCKER_VERSION     := 1.3
BASE_DOCKER_TAG         := $(shell echo $(UTIL_NAME)-base-ubuntu20.04:$(BASE_DOCKER_VERSION) | tr A-Z a-z)
TEST_DOCKER_TAG         := $(shell echo $(UTIL_NAME)-test-ubuntu20.04:$(UTIL_VERSION) | tr A-Z a-z)
DOCKER_TAG              ?= $(shell echo $(UTIL_NAME)-ubuntu20.04:$(UTIL_VERSION) | tr A-Z a-z)

PYTHONDONTWRITEBYTECODE := "1"
PYTHONPATH              := $(PWD)/src/:$(PWD)/test/auto

LOGS_PATH               := /var/log/$(UTIL_NAME)
CODEPLAG_LOG_PATH       := $(LOGS_PATH)/$(UTIL_NAME).log
CONFIG_PATH             := /etc/$(UTIL_NAME)/settings.conf
LIB_PATH                := /var/lib/$(UTIL_NAME)
DEBIAN_PACKAGES_PATH    := debian/deb

SOURCE_SUB_FILES        := src/$(UTIL_NAME)/consts.py
IS_DEVELOPED            ?= 1
ALL                     ?= 0
DEBIAN_SUB_FILES        := debian/changelog \
                           debian/control \
                           debian/preinst \
                           debian/copyright
DOCKER_SUB_FILES        := docker/base_ubuntu2004.dockerfile \
                           docker/test_ubuntu2004.dockerfile \
                           docker/ubuntu2004.dockerfile

PYTHON_REQUIRED_LIBS    := $(shell python3 setup.py --install-requirements)


ifeq ($(IS_DEVELOPED), 1)
DEVEL_SUFFIX            := .devel
endif


substitute = @sed \
		-e "s|@UTIL_NAME@|${UTIL_NAME}|g" \
		-e "s|@UTIL_VERSION@|${UTIL_VERSION}|g" \
		-e "s|@CODEPLAG_LOG_PATH@|${CODEPLAG_LOG_PATH}|g" \
		-e "s|@DEVEL_SUFFIX@|${DEVEL_SUFFIX}|g" \
		-e "s|@PYTHON_REQUIRED_LIBS@|${PYTHON_REQUIRED_LIBS}|g" \
		-e "s|@LOGS_PATH@|${LOGS_PATH}|g" \
		-e "s|@LIB_PATH@|${LIB_PATH}|g" \
		-e "s|@CONFIG_PATH@|${CONFIG_PATH}|g" \
		-e "s|@BASE_DOCKER_TAG@|${BASE_DOCKER_TAG}|g" \
		-e "s|@DEBIAN_PACKAGES_PATH@|${DEBIAN_PACKAGES_PATH}|g" \
		$(1) > $(2) \
		&& echo "Substituted from '$(1)' to '$(2)'."

all: install

# $< - %.in file, $@ desired file %
%: %.in
	$(call substitute,$<,$@)

%.py: %.tmp.py
	$(call substitute,$<,$@)

substitute-sources: $(SOURCE_SUB_FILES)
	@echo "Substituted information about the utility in the source files."

substitute-debian: $(DEBIAN_SUB_FILES)
	@echo "Substituted information about the utility in the debian files."

substitute-docker: $(DOCKER_SUB_FILES)
	@echo "Substituted information about the utility in the docker files."

man: substitute-sources
	mkdir -p man
	argparse-manpage --pyfile src/$(UTIL_NAME)/$(UTIL_NAME)cli.py \
					 --function CodeplagCLI \
					 --author "Codeplag Development Team" \
					 --project-name "$(UTIL_NAME) $(UTIL_VERSION)" \
					 --url "https://github.com/OSLL/code-plagiarism" \
					 --output man/$(UTIL_NAME).1

install: substitute-sources man
	python3 -m pip install --root=/$(DESTDIR) .

	install -D -d -m 0755 $(DESTDIR)/$(LOGS_PATH)
	install -D -m 0666 /dev/null $(DESTDIR)/$(CODEPLAG_LOG_PATH)
	install -D -d -m 0755 $(DESTDIR)/$(LIB_PATH)

	install -D -m 0666 src/templates/report_ru.templ $(DESTDIR)/$(LIB_PATH)/report_ru.templ
	install -D -m 0666 src/templates/report_en.templ $(DESTDIR)/$(LIB_PATH)/report_en.templ

	if [ ! -f $(DESTDIR)/$(CONFIG_PATH) ]; then \
		install -D -d -m 0755 $(DESTDIR)/etc/$(UTIL_NAME); \
		install -D -m 0666 /dev/null $(DESTDIR)/$(CONFIG_PATH); \
		echo "{}" > $(DESTDIR)/$(CONFIG_PATH); \
	fi

	install -D -m 0644 man/$(UTIL_NAME).1 $(DESTDIR)/usr/share/man/man1/$(UTIL_NAME).1

package: substitute-debian
	find $(DEBIAN_PACKAGES_PATH)/$(UTIL_NAME)* > /dev/null 2>&1 || ( \
		dpkg-buildpackage -jauto -b \
			--buildinfo-option="-u$(CURDIR)/$(DEBIAN_PACKAGES_PATH)" \
			--changes-option="-u$(CURDIR)/$(DEBIAN_PACKAGES_PATH)" \
			--no-sign && \
		cp $(DEBIAN_PACKAGES_PATH)/usr/share/man/man1/$(UTIL_NAME).1 $(DEBIAN_PACKAGES_PATH)/$(UTIL_NAME).1 && \
		chown --recursive ${USER_UID}:${USER_GID} $(DEBIAN_PACKAGES_PATH) \
	)

test: substitute-sources
	pytest test/unit -vv
	make clean-cache

autotest:
	pytest test/auto -vv
	make clean-cache

pre-commit:
	pre-commit run --all-files

clean-cache:
	find . -maxdepth 1 -type d | grep -E "pytest_cache" | (xargs rm -r 2> /dev/null || exit 0)
	rm --recursive --force $(shell find -type d -iname "__pycache__")

clean: clean-cache
	rm --force --recursive man/
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive $(DEBIAN_PACKAGES_PATH)/*
	rm --force --recursive debian/.debhelper/
	rm --force --recursive debian/$(UTIL_NAME)-util/
	rm --force debian/debhelper-build-stamp
	rm --force debian/files
	rm --force debian/$(UTIL_NAME)-util.debhelper.log
	rm --force debian/$(UTIL_NAME)-util.substvars
	rm --force --recursive src/$(UTIL_NAME).egg-info

clean-all: clean
	rm --force src/$(UTIL_NAME)/consts.py

	rm --force docker/base_ubuntu2004.dockerfile
	rm --force docker/test_ubuntu2004.dockerfile
	rm --force docker/ubuntu2004.dockerfile

	rm --force --recursive $(DEBIAN_PACKAGES_PATH)
	rm --force debian/changelog
	rm --force debian/control
	rm --force debian/preinst
	rm --force debian/postinst
	rm --force debian/copyright

uninstall:
	rm --force /usr/share/man/man1/$(UTIL_NAME).1
	pip3 uninstall $(UTIL_NAME) -y

reinstall: uninstall install

todo-list: clean-all
	@grep --color=auto -r -n 'TODO' ./* --exclude=Makefile --exclude-dir=docs

help:
	@echo "Usage:"
	@echo "  make [targets] [arguments]"
	@echo
	@echo "Commands:"
	@echo "  install                Install on the local computer without using package manager;"
	@echo "  uninstall              Remove installed util from system;"
	@echo "  man                    Create man file."
	@echo "                         Require argparse-manpage python library;"
	@echo "  test                   Runs unit tests with pytest framework;"
	@echo "  autotest               Runs auto tests."
	@echo "                         Required installed '$(UTIL_NAME)' util and provided ACCESS_TOKEN;"
	@echo "  package                Build the debian package;"
	@echo "  clean-cache            Delete __pycache__ folders created by pytest framework;"
	@echo "  clean                  Remove generated while installing and testing files in the source directory (contains clean-cache);"
	@echo "  clean-all              Remove all generated files such as created docker files, debian and sources (contains clean);"
	@echo "  help                   Display this message and exit."
	@echo
	@echo "Docker:"
	@echo "  docker-run             Runs docker container with installed util;"
	@echo "  docker-image           Build docker image;"
	@echo "      ALL=[1|0] REBUILD=[1|0]"
	@echo "  docker-test            Runs unit tests with pytest framework in the docker container;"
	@echo "  docker-autotest        Runs autotests in docker container;"
	@echo "  docker-build-package   Build the debian package in special docker image;"
	@echo "  docker-rmi ALL=[1|0]   Delete created docker images."
	@echo


.EXPORT_ALL_VARIABLES:
.PHONY: all test man

include docker.mk
