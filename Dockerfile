FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt-get install -y clang libncurses5 groff
RUN pip3 install --upgrade setuptools
RUN pip3 install argparse-manpage

ADD . /usr/src/code-plagiarism
WORKDIR /usr/src/code-plagiarism

RUN make all
