ARG BASE_DOCKER_TAG
FROM $BASE_DOCKER_TAG

ARG PYTHON_TEST_LIBS
ARG PYTHON_BUILD_LIBS
ARG LOGS_PATH
ARG UTIL_NAME

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y --no-install-recommends debhelper python3-dev build-essential
RUN pip3 install --break-system-packages $PYTHON_TEST_LIBS $PYTHON_BUILD_LIBS
RUN mkdir -p $LOGS_PATH

# TODO: Move to middle docker file or make another solution
ADD setup.py /usr/src/$UTIL_NAME/setup.py
ADD pyproject.toml /usr/src/$UTIL_NAME/pyproject.toml
ADD src/ /usr/src/$UTIL_NAME/src
ADD README.md /usr/src/$UTIL_NAME/README.md
ADD LICENSE /usr/src/$UTIL_NAME/LICENSE
ADD Makefile /usr/src/$UTIL_NAME/Makefile
ADD locales/ /usr/src/$UTIL_NAME/locales
ADD docker/docker.mk /usr/src/$UTIL_NAME/docker/docker.mk
ADD debian/ /usr/src/$UTIL_NAME/debian

RUN apt-get clean
RUN rm --recursive --force /tmp/* /var/tmp/*

CMD make test
