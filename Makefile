UTIL_VERSION			:= 0.2.1
UTIL_NAME				:= codeplag

BASE_DOCKER_TAG			:= $(shell echo $(UTIL_NAME)-base-ubuntu20.04:$(UTIL_VERSION) | tr A-Z a-z)
TEST_DOCKER_TAG			:= $(shell echo $(UTIL_NAME)-test-ubuntu20.04:$(UTIL_VERSION) | tr A-Z a-z)
DOCKER_TAG				?= $(shell echo $(UTIL_NAME)-ubuntu20.04:$(UTIL_VERSION) | tr A-Z a-z)

PWD 					:= $(shell pwd)
LOGS_PATH				:= /var/log
CODEPLAG_LOG_PATH		:= $(LOGS_PATH)/$(UTIL_NAME).log
WEBPARSERS_LOG_PATH		:= $(LOGS_PATH)/webparsers.log
CONVERTED_FILES 		:= src/codeplag/consts.py \
						   src/webparsers/consts.py \
						   docker/base_ubuntu2004.dockerfile \
						   docker/test_ubuntu2004.dockerfile \
						   docker/ubuntu2004.dockerfile


all: substitute man install

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

man:
	mkdir -p man
	export PYTHONPATH=src/ && \
	argparse-manpage --pyfile src/codeplag/codeplagcli.py \
					 --function CodeplagCLI \
					 --author "Codeplag Development Team" \
					 --author-email "inbox@moevm.info" \
					 --project-name "$(UTIL_NAME) $(UTIL_VERSION)" \
					 --url "https://github.com/OSLL/code-plagiarism" \
					 --output man/$(UTIL_NAME).1

install:
	python3 -m pip install .

	touch $(CODEPLAG_LOG_PATH)
	chmod 0666 $(CODEPLAG_LOG_PATH)

	touch $(WEBPARSERS_LOG_PATH)
	chmod 0666 $(WEBPARSERS_LOG_PATH)

	install -D -m 0644 man/$(UTIL_NAME).1 /usr/share/man/man1/$(UTIL_NAME).1

test:
	pytest test/unit -q
	make clean-cache

autotest:
	pytest test/auto -q
	make clean-cache

clean: clean-cache
	rm --force --recursive Man/
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive src/codeplag.egg-info
	rm --force src/codeplag/consts.py
	rm --force src/webparsers/consts.py
	rm --force docker/base_ubuntu2004.dockerfile
	rm --force docker/test_ubuntu2004.dockerfile
	rm --force docker/ubuntu2004.dockerfile

clean-cache:
	find . -maxdepth 1 -type d | grep -E "pytest_cache" | (xargs rm -r 2> /dev/null || exit 0)
	find . -type d | grep -E "__pycache__" | (xargs rm -r 2> /dev/null || exit 0)

uninstall:
	rm --force /usr/share/man/man1/$(UTIL_NAME).1
	pip3 uninstall $(UTIL_NAME) -y

docker-base-image: substitute
	docker image inspect $(BASE_DOCKER_TAG) > /dev/null 2>&1 || ( \
		export DOCKER_BUILDKIT=1 && \
		docker image build \
			--tag "$(BASE_DOCKER_TAG)" \
			--file docker/base_ubuntu2004.dockerfile \
			. \
	)

docker-test-image: docker-base-image
	docker image inspect $(TEST_DOCKER_TAG) > /dev/null 2>&1 || \
	docker image build \
		--tag  "$(TEST_DOCKER_TAG)" \
		--file docker/test_ubuntu2004.dockerfile \
		.

docker-test: docker-test-image
	docker run --rm \
		--volume $(PWD)/man:/usr/src/$(UTIL_NAME)/man \
		--volume $(PWD)/test:/usr/src/$(UTIL_NAME)/test \
		"$(TEST_DOCKER_TAG)"

docker-autotest: docker-test-image
	docker run --rm \
		--volume $(PWD)/test:/usr/src/$(UTIL_NAME)/test \
		--env-file .env \
		"$(TEST_DOCKER_TAG)" bash -c \
		"make autotest"

docker-image:
	docker image inspect $(DOCKER_TAG) > /dev/null 2>&1 || ( \
		make docker-test && \
		docker image build \
			--tag  "$(DOCKER_TAG)" \
			--file docker/ubuntu2004.dockerfile \
			. \
	)

docker-run: docker-image
	docker run --rm --tty --interactive \
		"$(DOCKER_TAG)"

docker-rmi:
	@docker rmi $(DOCKER_TAG) 2> /dev/null || \
	echo "Image $(DOCKER_TAG) is not exists"

	@docker rmi $(TEST_DOCKER_TAG) 2> /dev/null || \
	echo "Image $(TEST_DOCKER_TAG) is not exists"

	@docker rmi $(BASE_DOCKER_TAG) 2> /dev/null || \
	echo "Image $(BASE_DOCKER_TAG) is not exists"

help:
	@echo "Usage:"
	@echo "  make [command]"
	@echo
	@echo "Commands:"
	@echo "  install                          Install on the local computer;"
	@echo "  man                              Create man file."
	@echo "                                   Required argparse-manpage and sudo privilege;"
	@echo "  test                             Runs unit tests with pytest framework;"
	@echo "  autotest                         Runs autotests."
	@echo "                                   Required installed codeplag util and provided ACCESS_TOKEN;"
	@echo "  clean                            Remove generated while installing and testing files in the source directory;"
	@echo "  clean-cache                      Delete __pycache__ folders created by pytest framework;"
	@echo "  uninstall                        Remove installed util from system;"
	@echo "  help                             Display this message and exit."
	@echo
	@echo "Docker:"
	@echo "  docker-image                     Build docker image;"
	@echo "  docker-test                      Runs unit tests with pytest framework in docker container;"
	@echo "  docker-run                       Runs docker container with installed util;"
	@echo "  docker-autotest                  Runs autotests in docker container;"
	@echo "  docker-rmi                       Delete created docker images."
	@echo

.PHONY: all test man