FROM ubuntu:24.04

ARG PYTHON_REQUIRED_LIBS
ARG UTIL_NAME

# Remove diverted man binary to prevent man-pages being replaced with "minimized" message.
RUN if  [ "$(dpkg-divert --truename /usr/bin/man)" = "/usr/bin/man.REAL" ]; then \
        rm -f /usr/bin/man; \
        dpkg-divert --quiet --remove --rename /usr/bin/man; \
    fi
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    python3-pip \
    clang \
    libncurses6 \
    vim \
    nano \
    less
RUN apt-get clean

RUN pip3 install --break-system-packages $PYTHON_REQUIRED_LIBS

RUN rm --recursive --force /tmp/* /var/tmp/*

VOLUME /usr/src/works
WORKDIR /usr/src/$UTIL_NAME
