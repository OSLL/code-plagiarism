FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt-get install -y clang libncurses5
RUN apt-get install -y man
RUN pip3 install --upgrade setuptools
RUN pip3 install 'argparse-manpage==2.1'

ARG UTIL_NAME
ADD . /usr/src/${UTIL_NAME}
WORKDIR /usr/src/${UTIL_NAME}

RUN make
