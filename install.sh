#!/bin/bash

INSTALL=""
for package in clang libncurses5 python3 python3-pip; do
	if ! dpkg -l $package >/dev/null 2>/dev/null; then
		INSTALL="$INSTALL $package"	
	fi
done

if [ -n "$INSTALL" ]; then
	echo "Starting install requirements..."
	eval "sudo apt update"
	eval "sudo apt install $INSTALL"
fi

python3 setup.py install --user
python3 -m unittest discover -v ./src
