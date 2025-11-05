UTIL_VERSION            := $(shell grep -Po '^version\s*=\s*"\K[\d.]+' pyproject.toml)
UTIL_NAME               := $(shell grep -Po '^name\s*=\s*"\K\w+' pyproject.toml)
PWD                     := $(shell pwd)

USER_UID                ?= $(shell id --user)
USER_GID                ?= $(shell id --group)

BASE_DOCKER_VERSION     := 1.0
DIST                    := ubuntu24.04
BASE_DOCKER_TAG         := $(shell echo $(UTIL_NAME)-base-${DIST}:$(BASE_DOCKER_VERSION))
TEST_DOCKER_TAG         := $(shell echo $(UTIL_NAME)-test-${DIST}:$(UTIL_VERSION))
DOCKER_TAG              ?= $(shell echo $(UTIL_NAME)-${DIST}:$(UTIL_VERSION))

PYTHONDONTWRITEBYTECODE := "1"
PYTHONPATH              := $(PWD)/src/:$(PWD)/test/auto

LOGS_PATH               := /var/log/$(UTIL_NAME)
CODEPLAG_LOG_PATH       := $(LOGS_PATH)/$(UTIL_NAME).log
CONFIG_PATH             := /etc/$(UTIL_NAME)/settings.conf
LIB_PATH                := /var/lib/$(UTIL_NAME)
DEBIAN_PATH             := debian/
DEBIAN_PACKAGES_PATH    := ${DEBIAN_PATH}/deb
PY_INSTALL_PATH         := $(shell python3 -c "import site; print(site.getsitepackages()[0]);")

SOURCE_SUB_FILES        := src/$(UTIL_NAME)/consts.py
IS_DEVELOPED            ?= 1
ALL                     ?= 0
DEBIAN_SUB_FILES        := ${DEBIAN_PATH}/changelog \
                           ${DEBIAN_PATH}/control \
                           ${DEBIAN_PATH}/preinst \
                           ${DEBIAN_PATH}/copyright

PYTHON_REQUIRED_LIBS    := $(shell python3 setup.py --install-requirements)
PYTHON_BUILD_LIBS       := $(shell python3 setup.py --build-requirements)
PYTHON_TEST_LIBS        := $(shell python3 setup.py --test-requirements)


ifeq ($(IS_DEVELOPED), 1)
DEVEL_SUFFIX            := .devel
endif

DEB_PKG_NAME            := ${UTIL_NAME}-util_${UTIL_VERSION}-1${DEVEL_SUFFIX}.${DIST}_amd64


substitute = @sed \
		-e "s|@UTIL_NAME@|${UTIL_NAME}|g" \
		-e "s|@UTIL_VERSION@|${UTIL_VERSION}|g" \
		-e "s|@CODEPLAG_LOG_PATH@|${CODEPLAG_LOG_PATH}|g" \
		-e "s|@DEVEL_SUFFIX@|${DEVEL_SUFFIX}|g" \
		-e "s|@PYTHON_REQUIRED_LIBS@|${PYTHON_REQUIRED_LIBS}|g" \
		-e "s|@DIST@|${DIST}|g" \
		-e "s|@LOGS_PATH@|${LOGS_PATH}|g" \
		-e "s|@LIB_PATH@|${LIB_PATH}|g" \
		-e "s|@CONFIG_PATH@|${CONFIG_PATH}|g" \
		-e "s|@DEBIAN_PACKAGES_PATH@|${DEBIAN_PACKAGES_PATH}|g" \
		-e "s|@DEB_PKG_NAME@|${DEB_PKG_NAME}|g" \
		$(1) > $(2) \
		&& echo "Substituted from '$(1)' to '$(2)'."

.PHONY: all
all: install

# $< - %.in file, $@ desired file %
%: %.in
	$(call substitute,$<,$@)

%.py: %.tmp.py
	$(call substitute,$<,$@)

.PHONY: substitute-sources
substitute-sources: $(SOURCE_SUB_FILES)
	@echo "Substituted information about the utility in the source files."

.PHONY: substitute-debian
substitute-debian: $(DEBIAN_SUB_FILES)
	@echo "Substituted information about the utility in the debian files."

.PHONY: substitute-docker
substitute-docker: $(DOCKER_SUB_FILES)
	@echo "Substituted information about the utility in the docker files."

.PHONY: install
install: substitute-sources man translate-compile
	python3 -m pip install --root=$(DESTDIR)/ .

	@echo "Cleaning unnecessary files after Cython compilation in $(PY_INSTALL_PATH)"
	find "$(DESTDIR)/$(PY_INSTALL_PATH)/$(UTIL_NAME)/" -type f -name '*.py' -exec rm --force '{}' +
	find "$(DESTDIR)/$(PY_INSTALL_PATH)/$(UTIL_NAME)/" -type f -name '*.c' -exec rm --force '{}' +
	find "$(DESTDIR)/$(PY_INSTALL_PATH)/$(UTIL_NAME)" -type d -iname "__pycache__" -exec rm --recursive --force '{}' +
	find "$(DESTDIR)/$(PY_INSTALL_PATH)/webparsers" -type d -iname "__pycache__" -exec rm --recursive --force '{}' +

	@echo "Cleaning unnecessary temporary Python files after installation in $(PY_INSTALL_PATH)"
	find "$(DESTDIR)/$(PY_INSTALL_PATH)/$(UTIL_NAME)/" -type f -name '*.tmp.py' -exec rm --force '{}' +
	rm --recursive --force "$(DESTDIR)/$(PY_INSTALL_PATH)/$(UTIL_NAME)/consts"

	install -D -d -m 0755 $(DESTDIR)/$(LOGS_PATH)
	install -D -m 0666 /dev/null $(DESTDIR)/$(CODEPLAG_LOG_PATH)
	install -D -d -m 0755 $(DESTDIR)/$(LIB_PATH)

	install -D -m 0666 src/templates/general.templ $(DESTDIR)/$(LIB_PATH)/general.templ
	install -D -m 0666 src/templates/sources.templ $(DESTDIR)/$(LIB_PATH)/sources.templ

	cp --recursive locales/translations/ $(DESTDIR)/$(LIB_PATH)/
	find "$(DESTDIR)/$(LIB_PATH)/translations/" -type f -name '*.po' -exec rm --force '{}' +

	if [ ! -f $(DESTDIR)/$(CONFIG_PATH) ]; then \
		install -D -d -m 0755 $(DESTDIR)/etc/$(UTIL_NAME); \
		install -D -m 0666 /dev/null $(DESTDIR)/$(CONFIG_PATH); \
		echo "{}" > $(DESTDIR)/$(CONFIG_PATH); \
	fi

	install -D -m 0644 man/$(UTIL_NAME).1 $(DESTDIR)/usr/share/man/man1/$(UTIL_NAME).1

.PHONY: man
man: substitute-sources
	mkdir -p man
	if [ ! -f man/$(UTIL_NAME).1 ]; then \
		argparse-manpage --pyfile src/$(UTIL_NAME)/$(UTIL_NAME)cli.py \
						--function CodeplagCLI \
						--author "Codeplag Development Team" \
						--project-name "$(UTIL_NAME) $(UTIL_VERSION)" \
						--url "https://github.com/OSLL/code-plagiarism" \
						--output man/$(UTIL_NAME).1; \
	fi

.PHONY: package
package: substitute-debian
	find $(DEBIAN_PACKAGES_PATH)/$(UTIL_NAME)* > /dev/null 2>&1 || ( \
		dpkg-buildpackage -jauto -b \
			--buildinfo-option="-u$(CURDIR)/$(DEBIAN_PACKAGES_PATH)" \
			--buildinfo-file="$(CURDIR)/$(DEBIAN_PACKAGES_PATH)/$(DEB_PKG_NAME).buildinfo" \
			--changes-option="-u$(CURDIR)/$(DEBIAN_PACKAGES_PATH)" \
			--changes-file="$(CURDIR)/$(DEBIAN_PACKAGES_PATH)/$(DEB_PKG_NAME).changes" \
			--no-sign && \
		cp $(DEBIAN_PACKAGES_PATH)/usr/share/man/man1/$(UTIL_NAME).1 $(DEBIAN_PACKAGES_PATH)/$(UTIL_NAME).1 && \
		chown --recursive ${USER_UID}:${USER_GID} $(DEBIAN_PACKAGES_PATH) \
	)

.PHONY: test
test: substitute-sources
	pytest test/unit test/misc --cov=src/ --cov-report xml --cov-report term
	make clean-cache

.PHONY: autotest
autotest:
	pytest test/auto
	make clean-cache

.PHONY: pre-commit
pre-commit:
	python3 -m pre_commit run --all-files

.PHONY: clean-cache
clean-cache:
	find . -maxdepth 1 -type d | grep -E "pytest_cache" | (xargs rm -r 2> /dev/null || exit 0)
	find "src/$(UTIL_NAME)/" -type f -name '*.c' -exec rm --force '{}' +
	rm --recursive --force $(shell find -type d -iname "__pycache__")

.PHONY: clean
clean: clean-cache
	rm --force --recursive man/
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive $(DEBIAN_PACKAGES_PATH)/*
	rm --force --recursive ${DEBIAN_PATH}/.debhelper/
	rm --force --recursive ${DEBIAN_PATH}/$(UTIL_NAME)-util/
	rm --force ${DEBIAN_PATH}/debhelper-build-stamp
	rm --force ${DEBIAN_PATH}/files
	rm --force ${DEBIAN_PATH}/$(UTIL_NAME)-util.debhelper.log
	rm --force ${DEBIAN_PATH}/$(UTIL_NAME)-util.substvars
	rm --force --recursive src/$(UTIL_NAME).egg-info

.PHONY: clean-all
clean-all: clean
	rm --force src/$(UTIL_NAME)/consts.py

	rm --force --recursive $(DEBIAN_PACKAGES_PATH)
	rm --force ${DEBIAN_PATH}/changelog
	rm --force ${DEBIAN_PATH}/control
	rm --force ${DEBIAN_PATH}/preinst
	rm --force ${DEBIAN_PATH}/copyright

.PHONY: uninstall
uninstall:
	rm --force $(DESTDIR)/usr/share/man/man1/$(UTIL_NAME).1
	rm --force --recursive $(DESTDIR)/$(LIB_PATH)
	pip3 uninstall $(UTIL_NAME) -y

.PHONY: reinstall
reinstall: uninstall install

.PHONY: todo-list
todo-list: clean-all
	@grep --color=auto -r -n 'TODO' ./* --exclude=Makefile --exclude-dir=docs

.PHONY: help
help: general-help docker-help translate-help

.PHONY: general-help
general-help:
	@echo "Usage:"
	@echo "  make [targets] [arguments]"
	@echo
	@echo "Commands:"
	@echo "  all                    Install on the local computer without using package manager;"
	@echo "  install                Install on the local computer without using package manager;"
	@echo "  uninstall              Removes the installed utility from the system;"
	@echo "  reinstall              Removes the installed utility from the system and then installs it again;"
	@echo "  man                    Create man file. Require argparse-manpage python library;"
	@echo "  pre-commit             Runs all pre-commit hooks;"
	@echo "  test                   Runs unit tests with pytest framework;"
	@echo "  autotest               Runs auto tests."
	@echo "                         Required installed '$(UTIL_NAME)' util and provided ACCESS_TOKEN;"
	@echo "  substitute-sources     Substitutes dynamic variables into source code files and generates final files;"
	@echo "  substitute-debian      Substitutes dynamic variables into debian files and generates final files;"
	@echo "  substitute-docker      Substitutes dynamic variables into docker files and generates final files;"
	@echo "  package                Build the debian package;"
	@echo "  clean-cache            Delete __pycache__ folders created by pytest framework;"
	@echo "  clean                  Remove generated while installing and testing files in the source directory (contains clean-cache);"
	@echo "  clean-all              Remove all generated files such as created docker files, debian and sources (contains clean);"
	@echo "  todo-list              Displays what is good to do in the source code;"
	@echo "  general-help           Displays information about upper-level targets;"
	@echo "  help                   Displays information about all available targets."
	@echo


.EXPORT_ALL_VARIABLES:

include docker/docker.mk
include locales/i18n.mk
