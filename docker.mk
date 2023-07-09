docker-base-image: substitute-sources substitute-docker
	@docker image inspect $(BASE_DOCKER_TAG) > /dev/null 2>&1 || ( \
		echo "Building base docker image." && \
		export DOCKER_BUILDKIT=1 && \
		docker image build \
			--tag "$(BASE_DOCKER_TAG)" \
			--file docker/base_ubuntu2004.dockerfile \
			. \
	)

docker-test-image: docker-base-image
	@docker image inspect $(TEST_DOCKER_TAG) > /dev/null 2>&1 || \
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
		--env IS_DEVELOPED=$(IS_DEVELOPED) \
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
			--file docker/ubuntu2004.dockerfile \
			. \
	)

docker-run: docker-image
	docker run --rm --tty --interactive \
		"$(DOCKER_TAG)"

docker-rmi:
	@docker rmi $(DOCKER_TAG) --force
	@docker rmi $(TEST_DOCKER_TAG) --force
	@if [ "$(ALL)" = "1" ]; then \
		docker rmi $(BASE_DOCKER_TAG) --force; \
	fi
