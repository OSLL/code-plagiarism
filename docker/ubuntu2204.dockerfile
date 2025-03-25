ARG BASE_DOCKER_TAG
FROM $BASE_DOCKER_TAG

ARG UTIL_NAME
ARG DEBIAN_PACKAGES_PATH
ARG DEB_PKG_NAME

ADD LICENSE /usr/src/$UTIL_NAME/LICENSE
ADD $DEBIAN_PACKAGES_PATH /usr/src/$UTIL_NAME/$DEBIAN_PACKAGES_PATH

RUN apt-get install -y /usr/src/$UTIL_NAME/$DEBIAN_PACKAGES_PATH/$DEB_PKG_NAME.deb
# TODO: Fix this hook. apt-get don't install manpage into image.
RUN install -D -m 0644 $DEBIAN_PACKAGES_PATH/$UTIL_NAME.1 /usr/share/man/man1/
RUN rm --recursive /usr/src/$UTIL_NAME/debian

RUN register-python-argcomplete $UTIL_NAME >> ~/.bashrc

CMD ["/bin/bash"]
