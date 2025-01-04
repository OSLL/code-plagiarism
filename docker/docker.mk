docker-base-image: substitute-sources substitute-docker
	@docker image inspect $(BASE_DOCKER_TAG) > /dev/null 2>&1 || ( \
		echo "Building base docker image." && \
		export DOCKER_BUILDKIT=1 && \
		docker image build \
			--tag "$(BASE_DOCKER_TAG)" \
			--file docker/base_ubuntu2204.dockerfile \
			. \
	)

docker-test-image: docker-base-image
	@docker image inspect $(TEST_DOCKER_TAG) > /dev/null 2>&1 || \
	docker image build \
		--tag  "$(TEST_DOCKER_TAG)" \
		--file docker/test_ubuntu2204.dockerfile \
		.

docker-test: docker-test-image
	docker run --rm \
		--volume $(PWD)/test:/usr/src/$(UTIL_NAME)/test \
		"$(TEST_DOCKER_TAG)"

docker-autotest: docker-test-image docker-build-package
	@if [ $(shell find . -maxdepth 1 -type f -name .env | wc --lines) != 1 ]; then \
		echo "Requires '.env' file with provided GitHub token for running autotests."; \
		exit 200; \
	else \
		docker run --rm \
			--volume $(PWD)/$(DEBIAN_PACKAGES_PATH):/usr/src/$(UTIL_NAME)/$(DEBIAN_PACKAGES_PATH) \
			--volume $(PWD)/test:/usr/src/$(UTIL_NAME)/test \
			--env-file .env \
			"$(TEST_DOCKER_TAG)" bash -c \
			"apt-get install -y /usr/src/${UTIL_NAME}/${DEBIAN_PACKAGES_PATH}/${DEB_PKG_NAME}.deb && make autotest"; \
	fi

docker-build-package: docker-test-image
	docker run --rm \
		--volume $(PWD)/$(DEBIAN_PACKAGES_PATH):/usr/src/$(UTIL_NAME)/$(DEBIAN_PACKAGES_PATH) \
		--env IS_DEVELOPED=$(IS_DEVELOPED) \
		--env USER_UID=$(USER_UID) \
		--env USER_GID=$(USER_GID) \
		"$(TEST_DOCKER_TAG)" bash -c \
		"make package"

docker-image: docker-base-image docker-test-image
	@if [ "$(REBUILD)" = "1" ]; then \
		make clean-all docker-rmi ALL="$(ALL)"; \
	fi

	@(docker image inspect $(DOCKER_TAG) > /dev/null 2>&1 && \
	echo "The image already exists. For rebuilding image provide REBUILD=1 argument.") || ( \
		make docker-test && \
		make docker-build-package && \
		docker image build \
			--tag  "$(DOCKER_TAG)" \
			--file docker/ubuntu2204.dockerfile \
			. \
	)

docker-run: docker-image
	@touch .env
	docker run --rm --tty --interactive \
		--env-file .env \
		"$(DOCKER_TAG)"

docker-rmi:
	@docker rmi $(DOCKER_TAG) --force
	@docker rmi $(TEST_DOCKER_TAG) --force
	@if [ "$(ALL)" = "1" ]; then \
		docker rmi $(BASE_DOCKER_TAG) --force; \
	fi
