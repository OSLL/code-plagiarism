FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt-get install -y clang libncurses5
RUN pip3 install --upgrade setuptools

ADD . /usr/src/code-plagiarism
WORKDIR /usr/src/code-plagiarism

RUN python3 setup.py install
